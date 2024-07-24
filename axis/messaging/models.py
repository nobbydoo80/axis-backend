__author__ = "Autumn Valenta"
__date__ = "3/3/15 1:39 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

import logging
import os

from django.conf import settings
from django.db import models
from django.template import Template, Context
from django.utils import formats
from django.utils.html import strip_tags
from simple_history.models import HistoricalRecords

from .managers import MessageManager
from .messages import MESSAGE_REGISTRY, ModernMessage
from .utils import send_alert, send_email


log = logging.getLogger(__name__)


class Message(models.Model):
    """Representation of a persistent message sent to a User."""

    DEBUG_MESSAGE_LEVEL = "debug"
    INFO_MESSAGE_LEVEL = "info"
    SUCCESS_MESSAGE_LEVEL = "success"
    WARNING_MESSAGE_LEVEL = "warning"
    ERROR_MESSAGE_LEVEL = "error"
    SYSTEM_MESSAGE_LEVEL = "system"

    MESSAGE_LEVELS = (
        (DEBUG_MESSAGE_LEVEL, "DEBUG"),  # For admins, internals, etc
        (INFO_MESSAGE_LEVEL, "Info"),
        (SUCCESS_MESSAGE_LEVEL, "Success"),
        (WARNING_MESSAGE_LEVEL, "Warning"),
        (ERROR_MESSAGE_LEVEL, "Error"),
        (SYSTEM_MESSAGE_LEVEL, "System"),
    )

    objects = MessageManager()

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="received_messages"
    )
    company = models.ForeignKey("company.Company", on_delete=models.SET_NULL, null=True, blank=True)
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_messages",
        blank=True,
        null=True,
        help_text="If not set then it is System Message",
    )
    title = models.CharField("Subject", max_length=200)
    content = models.TextField("Body")
    email_content = models.TextField("Email Content", blank=True, null=True)
    email_subject = models.CharField("Email Subject", max_length=200, blank=True, null=True)

    level = models.CharField("Severity", max_length=10, choices=MESSAGE_LEVELS, default="info")
    category = models.CharField("Category", max_length=30, blank=True)
    date_created = models.DateTimeField("Date", auto_now_add=True)

    modern_message = models.CharField(
        max_length=255,
        blank=True,
        help_text="Populated automatically in case "
        "of message has been populated through Modern Message",
    )

    url = models.CharField("Message source", max_length=512, blank=True)
    sticky_alert = models.BooleanField(default=False, help_text="Stay visible until dismissed")

    date_alerted = models.DateTimeField("Alerted", blank=True, null=True)
    date_sent = models.DateTimeField("Emailed", blank=True, null=True)

    alert_read = models.BooleanField(default=False)
    email_read = models.BooleanField(null=True, default=None)

    class Meta:
        ordering = ("-date_created",)

    def __str__(self):
        created = formats.date_format(self.date_created, "SHORT_DATETIME_FORMAT")
        company = (
            f"[{self.user.company.company_type} (id={self.company.id})] "
            if hasattr(self.user, "company")
            else ""
        )
        return f"(id={self.pk:<2}) {created}: To: {self.user} {company}Subj: {self.title}"

    def copy(self):
        """
        Replicates the message to a new object so that it can be easily distributed again.  Note
        that the returned object is unsaved in the database unless it is asked to ``send()``.
        """

        # Date and read/unread flags are not copied because they represent stateful information
        # about the original message.

        # 'title' and 'content' are copied, but should be recalculated via ``render(**context)``
        # and a fresh template string.  ``utils().send()`` does this, for example, when
        # cloning a source message for distribution between multiple users.

        message = Message(
            **{
                "sender": self.sender,
                "title": self.title,
                "content": self.content,
                "email_content": self.email_content,
                "email_subject": self.email_subject,
                "level": self.level,
                "category": self.category,
                "url": self.url,
                "sticky_alert": self.sticky_alert,
                "modern_message": self.modern_message,
            }
        )

        try:
            self.user
        except AttributeError:
            pass
        else:
            message.user = self.user
        return message

    @property
    def duplicates(self):
        return Message.objects.exclude(pk=self.pk).filter(
            user=self.user,
            title=self.title,
            content=self.content,
            email_content=self.email_content,
            email_subject=self.email_subject,
        )

    def is_duplicate(self):
        """
        Returns True if there already exists a message to the target user with the same
        title/content, even if it is marked as read.
        """
        return self.duplicates.exists()

    def render_content(self, content_data, **context):
        """This will intelligently use Django Template syntax or default to
        basic python string formatting methods"""
        content = content_data
        if os.path.isfile(content_data):
            with open(content_data) as file_obj:
                content = file_obj.read()
        elif "/" in content_data:
            msg = f"content data {content_data} looks remarkably like a path that doesn't exist!"
            if content_data.endswith(".html") or content_data.endswith(".txt"):
                log.warning(msg)

        template_variable = "{{" in content and "}}" in content
        template_tag = "{%" in content and "%}" in content
        if template_variable or template_tag:
            # Ok this is a true django template
            template = Template(content)
            return template.render(Context(context))
        # Fallback to python string formating
        return content.format(**context)

    def render(self, **context):
        """
        Sends the ``title``, ``content`` and ``email_content`` through a formatter.
        save() is not called.
        """
        self.title = self.render_content(self.title, **context)
        if self.email_subject:
            self.email_subject = self.render_content(self.email_subject, **context)
        else:
            self.email_subject = self.title

        if self.content:
            self.content = self.render_content(self.content, **context)
        if self.email_content:
            self.email_content = self.render_content(self.email_content, **context)
            if self.content is None:
                self.content = strip_tags("%s" % self.email_content)

    def send(
        self,
        required=False,
        force_resend=False,
        config=None,
        request=None,
        session_key=None,
        unique=False,
    ):
        alert_sent = False
        email_sent = False

        if self.date_sent and not force_resend:
            log.info("Message pk=%d already sent; skipping.", self.pk)
            return (alert_sent, email_sent)

        if unique and self.is_duplicate():
            log.info("Message pk=%d is duplicate; dropping.", self.pk)
            # self.delete()
            return (alert_sent, email_sent)

        methods = []
        modern_message = self.get_modern_message_class()

        if (
            required
            or force_resend
            or (not config or config.receive_notification)
            and modern_message.can_send_notification()
        ):
            send_alert(
                self, required=required, config=config, request=request, session_key=session_key
            )
            alert_sent = True
            methods.append("Alert")
        if (
            required
            or force_resend
            or (config and config.receive_email)
            and modern_message.can_send_email()
        ):
            send_email(self, required=required, config=config)
            email_sent = True
            methods.append("Email")
        return (alert_sent, email_sent)

    def get_modern_message_class(self) -> ModernMessage:
        """
        Get ModernMessage class from MESSAGE_REGISTRY or use AxisDjangoMessage as fallback
        :return: ModernMessage
        """
        from axis.core.messages import AxisDjangoMessage

        return MESSAGE_REGISTRY.get(self.modern_message, AxisDjangoMessage)


class MessagingPreference(models.Model):
    """Provides user settings for how messages are to be delivered."""

    history = HistoricalRecords()

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.CharField(max_length=30)
    message_name = models.CharField(max_length=100)  # Classname of a declared ModernMessage
    receive_email = models.BooleanField(default=False)
    receive_notification = models.BooleanField(default=True)

    class Meta:
        pass

    def get_delivery_settings(self):
        return {
            "email": self.receive_email,
            "notification": self.receive_notification,
        }


class DigestPreference(models.Model):
    UNSUBSCRIBED_DIGEST_THRESHOLD = ""
    ALERTS_DIGEST_THRESHOLD = "alerts"
    EMAILS_DIGEST_THRESHOLD = "emails"
    ALL_DIGEST_THRESHOLD = "all"

    DIGEST_CHOICES = (
        (UNSUBSCRIBED_DIGEST_THRESHOLD, "Unsubscribed"),
        (ALERTS_DIGEST_THRESHOLD, "In-system-only alerts"),
        (EMAILS_DIGEST_THRESHOLD, "Email alerts"),
        (ALL_DIGEST_THRESHOLD, "Everything"),
    )
    history = HistoricalRecords()

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    threshold = models.CharField(choices=DIGEST_CHOICES, max_length=10)

    class Meta:
        pass


# Session footwork to make it easier to look up sessions for a given user
class UserSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    session = models.ForeignKey("sessions.Session", on_delete=models.CASCADE)
