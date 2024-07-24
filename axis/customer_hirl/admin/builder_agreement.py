__author__ = "Artem Hruzd"
__date__ = "09/23/2021 5:37 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.contrib import admin, messages
from django.contrib.admin.decorators import register
from .admin import (
    HIRLBuilderInsuranceTabularInlineAdmin,
    HIRLBuilderAgreementStatusTabularInlineAdmin,
)
from axis.customer_hirl.models import BuilderAgreement
from axis.filehandling.admin import CustomerDocumentGenericTabularInline


def make_change_state_without_notification_action(state):
    def change_state_without_notification(modeladmin, request, queryset):
        updated_count = queryset.update(state=state)
        messages.info(request, f"{updated_count} Builder Agreement(s) has been updated")

    change_state_without_notification.short_description = (
        f"Change Builder Agreement state to {state}(Without notification)"
    )

    change_state_without_notification.__name__ = (
        f"change_builder_agreement_state_to_{state}_without_notification"
    )

    return change_state_without_notification


@register(BuilderAgreement)
class BuilderAgreementAdmin(admin.ModelAdmin):
    raw_id_fields = (
        "mailing_geocode",
        "mailing_geocode_response",
        "shipping_geocode",
        "shipping_geocode_response",
        "company",
        "owner",
        "signed_agreement",
        "certifying_document",
        "initiator",
        "extension_request_certifying_document",
        "extension_request_signed_agreement",
        "created_by",
    )
    inlines = (
        HIRLBuilderInsuranceTabularInlineAdmin,
        HIRLBuilderAgreementStatusTabularInlineAdmin,
        CustomerDocumentGenericTabularInline,
    )
    search_fields = ("id", "company__name", "data__envelope_id")
    list_filter = ("state",)
    list_display = (
        "company",
        "state",
    )

    def get_actions(self, request):
        actions = super(BuilderAgreementAdmin, self).get_actions(request)
        for choice in BuilderAgreement.STATE_CHOICES:
            action = make_change_state_without_notification_action(choice[0])
            actions[action.__name__] = (action, action.__name__, action.short_description)
        return actions
