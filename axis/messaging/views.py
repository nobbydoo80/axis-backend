""" Messaging system views """


import logging

from django.apps import apps
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.utils.http import urlsafe_base64_decode
from django.views import View
from django.views.generic import TemplateView, DetailView

from axis.core.messages import AxisSystemMessage
from axis.core.utils import has_beta_access
from .constants import constants
from .forms import MessagesFilterForm
from .messages import MESSAGE_REGISTRY
from .models import Message, MessagingPreference
from .tokens import unsubscribe_email_token
from .utils import get_digest_report

__author__ = "Autumn Valenta"
__date__ = "2015-03-04 2:01 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)
User = get_user_model()

frontend_app = apps.get_app_config("frontend")


class MessagingListView(LoginRequiredMixin, TemplateView):
    template_name = "messaging/message_list.html"

    def get_context_data(self, **kwargs):
        context = super(MessagingListView, self).get_context_data(**kwargs)
        context["filter_form"] = MessagesFilterForm(self.request.user)
        return context


class WebsocketIDListView(LoginRequiredMixin, TemplateView):
    model = User
    template_name = "messaging/websocket_id_list.html"

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, *args, **kwargs):
        return super(WebsocketIDListView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(WebsocketIDListView, self).get_context_data(**kwargs)
        websocket_data = self.request.session["websocket_ids"].items()
        context.update(
            {
                "data": [
                    (k, v) for k, v in sorted(websocket_data, key=lambda item: item[1]["date"])
                ],
            }
        )
        return context


class MessagingTestDigestView(LoginRequiredMixin, DetailView):
    model = User
    template_name = "messaging/digest_email.html"

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, *args, **kwargs):
        return super(MessagingTestDigestView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(MessagingTestDigestView, self).get_context_data(**kwargs)
        report, start, end = get_digest_report(user_id=self.kwargs["pk"])
        domain = get_current_site(self.request).domain
        context.update(
            {
                "start_date": start,
                "end_date": end,
                "user": self.object,
                "report": report,
                "domain": domain,
            }
        )
        return context


class MessagingTestEmailView(LoginRequiredMixin, DetailView):
    model = Message
    template_name = "messaging/notification_email.html"

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, *args, **kwargs):
        return super(MessagingTestEmailView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(MessagingTestEmailView, self).get_context_data(**kwargs)

        context.update(
            {
                "message": self.object,
                "domain": get_current_site(self.request).domain,
            }
        )
        return context


class MessagingTestGenerationView(TemplateView):
    template_name = "messaging/test.html"

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, *args, **kwargs):
        self.generate_notifications()
        return super(MessagingTestGenerationView, self).dispatch(*args, **kwargs)

    def generate_notifications(self):
        system_message = AxisSystemMessage()
        system_message.unique = False
        system_message.title = "Modern message"
        system_message.content = "Modern message content"
        system_message.send(user=self.request.user)

        messages.debug(
            self.request,
            {
                "content": "Company-wide message for {user.company}",
                "company": self.request.company,
                "sticky_alert": True,
            },
        )
        messages.debug(self.request, "Custom <strong>debug</strong> message")
        messages.info(
            self.request,
            {
                "title": "OMG a title",
                "content": "This is a <em>custom</em> message. Built via kwargs.",
            },
        )
        messages.warning(
            self.request,
            {
                "title": "{company} is amazing!",
                "content": "This is a {type} message. Built via string formatting!",
                "context": {
                    "company": self.request.user.company,
                    "type": "custom",
                },
            },
        )

        # Our 'system'-level extension doesn't exist in the django messages api, so
        # ``messages.system()`` is not possible.  Normally we wouldn't use ``add_message()``
        # directly for anything, but it keeps us consistent with using the django messages app as
        # the dispatch tool.
        messages.add_message(
            self.request,
            constants.SYSTEM,
            {
                "title": "NEEA V2 Program Suspension",
                "content": "Program is on hold, no more certifications until further notice.",
                "category": "system",
            },
        )


class UnsubscribeEmailView(View):
    def get(self, request, uidb64, token, mnameb64):
        try:
            uid = urlsafe_base64_decode(uidb64)
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is not None and unsubscribe_email_token.check_token(user, token):
            try:
                mname = urlsafe_base64_decode(mnameb64).decode()
                modern_message = MESSAGE_REGISTRY[mname]
            except (ValueError, KeyError):
                return render(request, "messaging/unsubscribe_email_invalid.html")

            instance, created = MessagingPreference.objects.update_or_create(
                message_name=modern_message.__name__, user=user, defaults={"receive_email": False}
            )
            return render(
                request,
                "messaging/unsubscribe_email.html",
                context={"modern_message": modern_message},
            )
        else:
            return render(request, "messaging/unsubscribe_email_invalid.html")


@staff_member_required
def modern_message_email_preview_admin_view(request, pk):
    message = Message.objects.get(pk=pk)
    context = {"message": message}
    return render(request, "messaging/admin/modern_message_email_preview.html", context)
