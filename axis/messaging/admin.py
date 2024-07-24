__author__ = "Artem Hruzd"
__date__ = "09/02/2021 12:14 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


from django.contrib import admin
from django.urls import path

from axis.messaging.models import Message
from django.urls import reverse
from django.utils.html import mark_safe
from axis.messaging.views import modern_message_email_preview_admin_view
from axis.core.pagination import NoCountPaginator


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    show_full_result_count = False
    raw_id_fields = ("user", "sender", "company")
    search_fields = (
        "email_subject",
        "title",
        "user__email",
        "user__first_name",
        "user__last_name",
    )
    list_display = ("id", "title", "user", "date_sent", "date_alerted", "content", "html_preview")
    list_filter = ("date_alerted", "date_sent", "alert_read", "email_read")

    paginator = NoCountPaginator

    def get_urls(self):
        urls = super(MessageAdmin, self).get_urls()
        my_urls = [
            path(
                "modern_message/email/preview/<int:pk>/",
                admin.site.admin_view(modern_message_email_preview_admin_view),
                name="modern_message_email_preview",
            ),
        ]
        return my_urls + urls

    def get_queryset(self, request):
        qs = super(MessageAdmin, self).get_queryset(request)
        return qs.select_related("user", "sender")

    @admin.display(
        description="HTML Preview",
    )
    def html_preview(self, obj):
        return mark_safe(
            f"<a href='{reverse('admin:modern_message_email_preview', kwargs={'pk': obj.pk})}' "
            f"target='_blank'>View</a>"
        )
