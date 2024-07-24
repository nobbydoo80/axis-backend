"""Examine support for `customer_hirl.verifier_agreements`"""


import logging

import waffle
from django.urls import reverse_lazy

from .base import BaseVerifierAgreementMachinery
from ..api import VerifierAgreementEnrollmentViewSet
from ..forms import VerifierAgreementEnrollmentForm

__author__ = "Autumn Valenta"
__date__ = "2019-05-16 4:47 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = ["Autumn Valenta"]

log = logging.getLogger(__name__)


class VerifierAgreementEnrollmentMachinery(BaseVerifierAgreementMachinery):
    """Enrollee machinery.  This is used after enrollment is complete to manage their info.

    Note that the owner's `VerifierEnrollmentApprovalMachinery` subclasses this as a read-only
    machinery.
    """

    type_name = "hirl_verifier_agreement_enrollment"
    api_provider = VerifierAgreementEnrollmentViewSet
    detail_template = "examine/customer_hirl/verifier_agreement/enrollment_detail.html"
    form_template = "examine/customer_hirl/verifier_agreement/enrollment_form.html"
    object_list_url = reverse_lazy(
        "hirl:verifier_agreements:enroll"
    )  # no list, just loop back to clean /add process
    delete_success_url = reverse_lazy("hirl:verifier_agreements:enroll")

    save_name = "Update"  # See get_edit_actions() for custom 'Enroll'-type text
    form_class = VerifierAgreementEnrollmentForm

    @property
    def region_template(self):
        """Return normal or 'new' region variants depending on creation mode."""

        if self.create_new:
            return "examine/customer_hirl/verifier_agreement/agreement_region_new.html"
        return "examine/customer_hirl/verifier_agreement/agreement_region.html"

    def get_form(self, instance=None):
        """Return a modified form for the current `instance_certification` availability."""

        form = super(VerifierAgreementEnrollmentMachinery, self).get_form(instance=instance)

        user = self.context["request"].user
        if not instance or not instance.pk:
            form.initial["applicant_first_name"] = user.first_name
            form.initial["applicant_last_name"] = user.last_name
            form.initial["applicant_title"] = user.title
            form.initial["applicant_phone_number"] = user.work_phone
            form.initial["applicant_cell_number"] = user.cell_phone
            form.initial["applicant_email"] = user.email
            if user.company:
                form.initial["mailing_geocode_street_line1"] = user.company.street_line1
                form.initial["mailing_geocode_street_line2"] = user.company.street_line2
                form.initial["mailing_geocode_city"] = user.company.city
                form.initial["mailing_geocode_zipcode"] = user.company.zipcode

        return form

    def get_edit_actions(self, instance):
        """Return normal edit actions, or a modified save label for initial enrollment."""

        actions = super(VerifierAgreementEnrollmentMachinery, self).get_edit_actions(instance)
        if self.create_new:
            # NOTE: Replace ALL actions since 'cancel' is not applicable either
            actions = [
                self.Action(
                    "Submit for Review and Approval by NGBS",
                    instruction="save",
                    size="md",
                    disabled=waffle.switch_is_active("Disable NGBS Verifier Agreement"),
                    style="primary",
                ),
            ]

        return actions

    def get_helpers(self, instance):
        """Return support dict for client page to trigger custom actions on the server."""

        helpers = super(VerifierAgreementEnrollmentMachinery, self).get_helpers(instance)
        return helpers
