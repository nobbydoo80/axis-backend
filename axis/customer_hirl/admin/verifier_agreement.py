__author__ = "Artem Hruzd"
__date__ = "05/24/2021 6:56 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from axis.customer_hirl.models import VerifierAgreement, ProvidedService
from django.contrib import admin, messages
from django.contrib.admin.decorators import register

from axis.customer_hirl.verifier_agreements.states import VerifierAgreementStates
from axis.filehandling.admin import CustomerDocumentGenericTabularInline


def make_change_state_without_notification_action(state):
    def change_state_without_notification(modeladmin, request, queryset):
        updated_count = queryset.update(state=state)
        messages.info(request, f"{updated_count} Verifier Agreement(s) has been updated")

    change_state_without_notification.short_description = (
        f"Change Verifier Agreement state to {state}(Without notification)"
    )

    change_state_without_notification.__name__ = (
        f"change_verifier_agreement_state_to_{state}_without_notification"
    )

    return change_state_without_notification


@register(VerifierAgreement)
class VerifierAgreementAdmin(admin.ModelAdmin):
    raw_id_fields = (
        "mailing_geocode",
        "shipping_geocode",
        "verifier_signed_agreement",
        "verifier_certifying_document",
        "officer_signed_agreement",
        "officer_certifying_document",
        "hirl_signed_agreement",
        "hirl_certifying_document",
        "owner",
        "verifier",
    )
    filter_horizontal = ("provided_services",)
    list_display = ("verifier", "state")
    list_filter = ("state",)
    search_fields = (
        "verifier__first_name",
        "verifier__last_name",
        "verifier__email",
        "verifier_agreement_docusign_data__envelope_id",
        "officer_agreement_docusign_data__envelope_id",
        "hirl_agreement_docusign_data__envelope_id",
    )
    inlines = (CustomerDocumentGenericTabularInline,)

    def get_actions(self, request):
        actions = super(VerifierAgreementAdmin, self).get_actions(request)
        for state in VerifierAgreementStates.ordering:
            action = make_change_state_without_notification_action(state)
            actions[action.__name__] = (action, action.__name__, action.short_description)
        return actions


@register(ProvidedService)
class ProvidedServiceAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ("name", "slug", "order")
