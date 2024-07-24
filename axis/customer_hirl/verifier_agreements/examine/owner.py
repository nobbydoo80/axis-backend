"""Examine support for `customer_hirl.verifier_agreements`"""


import logging

from django.urls import reverse, reverse_lazy

from axis.examine import machinery
from .base import BaseVerifierAgreementMachinery
from .enrollee import VerifierAgreementEnrollmentMachinery
from ..forms import VerifierAgreementManagementForm
from ..api import VerifierAgreementManagementViewSet
from ..states import VerifierAgreementStates

__author__ = "Artem Hruzd"
__date__ = "04/16/2020 17:07"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

log = logging.getLogger(__name__)


class VerifierAgreementMachinery(BaseVerifierAgreementMachinery):
    """Power the owner's interaction with a VerifierAgreement."""

    type_name = "hirl_verifier_agreement"
    api_provider = VerifierAgreementManagementViewSet
    region_template = "examine/customer_hirl/verifier_agreement/agreement_region.html"
    detail_template = "examine/customer_hirl/verifier_agreement/agreement_detail.html"
    form_template = "examine/customer_hirl/verifier_agreement/agreement_form.html"
    object_list_url = reverse_lazy("hirl:verifier_agreements:list")
    delete_success_url = reverse_lazy("hirl:verifier_agreements:list")

    form_class = VerifierAgreementManagementForm

    def get_default_actions(self, instance):
        """Return default actions with contextual additions for the current state."""

        actions = super(VerifierAgreementMachinery, self).get_default_actions(instance)

        if instance.has_owner_powers(self.context["request"].user):
            # Contextual transition button
            if instance.state == VerifierAgreementStates.NEW:
                actions.insert(
                    0,
                    self.Action(
                        "Approve Verifier Enrollment", instruction="approve", style="primary"
                    ),
                )
            elif instance.state == VerifierAgreementStates.APPROVED and instance.can_countersign():
                actions.insert(
                    0,
                    self.Action(
                        "Route Agreement for Counter-Signing", instruction="verify", style="primary"
                    ),
                )

        return actions

    def get_static_actions(self, instance):
        """Return static actions with contextual additions for the current state."""
        # Extra actions
        actions = super(VerifierAgreementMachinery, self).get_static_actions(instance)

        self.admin_actions[:0] = [
            {
                "name": "Re-send email",
                "instruction": "resend_email",
                "icon": "envelope",
                "description": """Re-send email for current step recipient""",
            },
            {
                "name": "Re-issue legal agreement to verifier",
                "instruction": "ensure_blank_document",
                "icon": "refresh",
                "description": """
                 Repopulates or restores the verifiers's unsigned legal agreement. The verifier
                 will be notified, and the previous request for signing will no longer be
                 valid.
             """,
            },
            {
                "name": "Retire this agreement",
                "instruction": "ensure_blank_document",
                "icon": "calendar",
                "description": """
                 The verifier will be able to continue viewing and editing their enrollment
                 information for future agreements to be submitted.
             """,
            },
            {
                "name": "Delete this agreement",
                "instruction": "delete",
                "icon": "trash",
                "description": "Completely delete this Agreement "
                "and all related information about it",
            },
        ]

        signature_states = [
            VerifierAgreementStates.NEW,
            VerifierAgreementStates.APPROVED,
            VerifierAgreementStates.VERIFIED,
        ]
        if self.instance.state in signature_states:
            self.admin_actions[:0] = [
                {
                    "name": "Update DocuSign Status",
                    "instruction": "update_docusign_status",
                    "icon": "refresh",
                    "description": """
                     Updates the signing status from DocuSign.
                 """,
                }
            ]

        return actions

    def get_helpers(self, instance):
        """Return support dict for client page to trigger custom actions on the server."""

        helpers = super(VerifierAgreementMachinery, self).get_helpers(instance)
        helpers["api_urls"].update(
            {
                "ensure_blank_document": reverse(
                    "apiv2:hirl_verifier_agreement-ensure-blank-document", kwargs={"pk": "__ID__"}
                ),
                "update_docusign_status": reverse(
                    "apiv2:hirl_verifier_agreement-update-docusign-status", kwargs={"pk": "__ID__"}
                ),
                "resend_email": reverse(
                    "api_v3:verifier_agreements-resend-docusign-email", kwargs={"pk": "__ID__"}
                ),
            }
        )
        return helpers


class VerifierAgreementEnrollmentApprovalMachinery(VerifierAgreementEnrollmentMachinery):
    """Read-only enrollment view for owner to see details."""

    region_template = None

    def get_default_actions(self, instance):
        """Return default actions with contextual additions for the current state."""

        actions = super(BaseVerifierAgreementMachinery, self).get_default_actions(instance)

        return actions

    def get_static_actions(self, instance):
        return []

    def can_edit_object(self, instance, user=None):
        if user and user.is_superuser:
            return True
        return False

    def can_delete_object(self, instance, user=None):
        return False
