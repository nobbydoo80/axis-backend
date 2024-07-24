""" Messaging system views """

__author__ = "Autumn Valenta"
__date__ = "2015-03-04 2:01 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

import logging
from collections import defaultdict
from typing import Optional, List
from typing import TYPE_CHECKING

import waffle
from django.contrib.auth import get_user_model
from django.db.models import QuerySet, Q

if TYPE_CHECKING:
    from axis.company.models import Company
    from axis.messaging.models import Message

    User = get_user_model()

log = logging.getLogger(__name__)


MESSAGE_CATEGORIES = defaultdict(set)  # Category names mapped to message classes in that category
MESSAGE_REGISTRY = dict()  # Message class names mapped to the class reference


class MessageMetaclass(type):
    def __new__(cls, name, bases, attrs):
        """
        Register ModernMessage subclasses in their categories so that there is a simple dict
        breakdown for use in the frontend.

        Message classes sharing names with previously registered classes will trigger an assertion
        error, since MessagingPreference instances store the name of the class and category in order
        to track user settings.  Having more than one class with the same name would result in
        confusion that should be easily avoided.
        """
        new_cls = super(MessageMetaclass, cls).__new__(cls, name, bases, attrs)

        if name == "ModernMessage":
            return new_cls

        if new_cls.__name__ in MESSAGE_REGISTRY:
            log.warning(
                "Can't define more than one ModernMessage with the same class name! "
                "Can't add %r to list: %r" % (new_cls, MESSAGE_CATEGORIES)
            )
        else:
            MESSAGE_CATEGORIES[new_cls.category].add(new_cls)
            MESSAGE_REGISTRY[new_cls.__name__] = new_cls
        return new_cls


class ModernMessage(metaclass=MessageMetaclass):
    """
    Base class for registering messages for which the users can assign delivery preferences.

    NOTE: Simple messages that are on-site only (i.e., email component doesn't make sense) DO NOT
          need to subclass this, and can be sent to the user as a raw string.
    """

    # Content rendered for actual delivery of notification
    title = ""

    # Note:  You are allowed to pass a file location in both of these.
    # Note:  If we find '{{' and '}}' in these they will be handled like a django template
    # Note:  If content==None and email_content we will strip out the tags
    # for the text based version.
    content = None
    email_content = None
    email_subject = None

    # Static-only urls can be defined here.  If the url has an object id in it, then don't declare
    # it on the message class--it can be filled it at runtime during utils().send()
    url = ""

    # User-friendly strings for explaining what the notification is and where it comes from
    verbose_name = None
    description = None

    sticky_alert = False
    required = False
    level = "info"
    category = None

    # Won't be re-sent if the post-rendered message content and title match an existing message to
    # the user.
    unique = False

    # Axis-specific conditional for deciding if a company type can even configure/receive the
    # message.  This is a hint mechanism that helps us hide irrelevant settings for categories of
    # users.

    # When True - This will only send to a user if they are an admin.  This will only be displayed
    # for selection if they are an admin
    company_admins_only = False

    # When set only these company types will receive this.
    company_types = None

    # Axis-specific conditional for hiding configurations from all companies but the ones whose
    # object slugs appear in the list.
    company_slugs = None

    # Axis-specific conditional for revealing configurations to companies that have a business
    # relationship with the company slugs given in this list.
    companies_with_relationship = None
    companies_with_relationship_or_self = None

    # django-waffle extension allow to disable some group of notifications from database
    # set the list of switches to disable message completely or only email sending for example
    # Note that switch must be True to Activate, so to in database it must sound like "Disable XYZ"
    waffle_disable_message_switches: tuple[str] = ()
    waffle_disable_notification_switches: tuple[str] = ()
    waffle_disable_email_switches: tuple[str] = ()

    def __str__(self):
        return self.__class__.__name__

    def __init__(self, url: str = ""):
        self.url = url

    def send(
        self,
        company: Optional["Company"] = None,
        users: Optional[QuerySet["User"]] = None,
        user: Optional["User"] = None,
        from_user: Optional["User"] = None,
        context: Optional[dict] = None,
        force_resend: bool = False,
        # deprecated, use self.url instead
        url: Optional[str] = "",
    ) -> List["Message"]:
        from .utils import send_message_task
        from django.contrib.auth import get_user_model
        from axis.company.models import CompanyAccess
        from axis.messaging.models import Message

        User = get_user_model()

        if user and users:
            raise ValueError(f"You must specify either user or users. Not both")

        if company is None and user is None and users is None:
            raise ValueError(f"You must specify user or users or company")

        if user:
            recipients = User.objects.filter(id=user.id)
        elif users:
            recipients = users
        else:
            company_access_user_ids = CompanyAccess.objects.filter(company=company).values_list(
                "user", flat=True
            )
            recipients = User.objects.filter(id__in=company_access_user_ids)

        recipients = recipients.filter(is_active=True, is_approved=True)

        if self.company_admins_only:
            recipients = recipients.filter(Q(is_company_admin=True) | Q(is_superuser=True))

        if not context:
            context = {}

        message_url = self.url
        if url:
            log.warning("url param is Deprecated, use Message(url=url) instead")
            message_url = url

        created_messages = []

        if not self.can_send_message():
            return created_messages

        for recipient in recipients:
            message = Message(
                title=self.title,
                content=self.content,
                email_content=self.email_content,
                email_subject=self.email_subject,
                company=company,
                url=message_url,
                category=self.category,
                level=self.level,
                sticky_alert=self.sticky_alert,
                modern_message=self.__class__.__name__,
                sender=from_user,
                user=recipient,
            )

            render_kwargs = context.copy()
            render_kwargs["user"] = recipient
            render_kwargs["sender"] = from_user
            # It is better to move message.render method here, instead of magically set model attributes inside
            message.render(**render_kwargs)

            if self.unique and message.is_duplicate():
                continue
            elif message.duplicates.is_debouncing():
                continue

            # create message object
            message.save()

            send_message_task.delay(
                message_id=message.id,
                # sending conditions
                force_resend=force_resend,
                unique=self.unique,
                required=self.required,
            )

            created_messages.append(message)

        return created_messages

    @classmethod
    def can_send_message(cls) -> bool:
        builtin_switches = ("Disable Messaging",)
        switches = set(builtin_switches) | set(cls.waffle_disable_message_switches)
        return any(not waffle.switch_is_active(switch) for switch in switches)

    @classmethod
    def can_send_notification(cls) -> bool:
        builtin_switches = ("Disable Real-Time Notifications",)
        switches = set(builtin_switches) | set(cls.waffle_disable_notification_switches)
        return any(not waffle.switch_is_active(switch) for switch in switches)

    @classmethod
    def can_send_email(cls) -> bool:
        builtin_switches = ("Disable Email Sending",)
        switches = set(builtin_switches) | set(cls.waffle_disable_email_switches)
        return any(not waffle.switch_is_active(switch) for switch in switches)
