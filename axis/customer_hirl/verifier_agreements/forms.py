"""forms.py: """

from django import forms
from django.apps import apps
from django.db.models import BLANK_CHOICE_DASH

from axis.core.fields import ApiModelChoiceField
from axis.core.widgets import BigSelectMultiple
from axis.core.widgets import FilterSelect
from axis.examine.forms import AjaxBase64FileFormMixin
from axis.geographic.fields import UnrestrictedCityChoiceWidget
from . import (
    ENROLLMENT_FIELDS,
    ENROLLMENT_LABELS,
    MANAGEMENT_FIELDS,
    MANAGEMENT_LABELS,
    STATE_LABEL,
)
from axis.customer_hirl.models import VerifierAgreement, COIDocument
from .states import VerifierAgreementStates
from axis.company.models import RaterOrganization, Company

__author__ = "Artem Hruzd"
__date__ = "04/16/2020 17:07"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

customer_hirl_app = apps.get_app_config("customer_hirl")


class VerifierAgreementFilterForm(forms.Form):
    """Filter form that feeds into the datatables ajax filters."""

    state = forms.ChoiceField(
        label=STATE_LABEL,
        widget=FilterSelect,
        choices=(("", BLANK_CHOICE_DASH),) + VerifierAgreementStates.choices,
        required=False,
    )
    verifier__company = forms.ModelChoiceField(
        label="Company",
        widget=FilterSelect,
        queryset=Company.objects.none(),
        required=False,
    )
    expiration_date = forms.ChoiceField(
        label="Expiration Date",
        choices=(
            ("", "-----"),
            ("1", "30 days"),
            ("2", "60 days"),
            ("3", "90 days"),
            ("4", "More than 90 days"),
        ),
        widget=FilterSelect,
        required=False,
    )

    def __init__(self, user, *args, **kwargs):
        super(VerifierAgreementFilterForm, self).__init__(*args, **kwargs)

        if user and user.company:
            if user.is_superuser or user.company.slug == customer_hirl_app.CUSTOMER_SLUG:
                self.fields["verifier__company"].queryset = RaterOrganization.objects.filter(
                    users__customer_hirl_enrolled_verifier_agreements__isnull=False
                ).distinct()
            else:
                self.fields["verifier__company"].queryset = RaterOrganization.objects.filter(
                    users__customer_hirl_enrolled_verifier_agreements__verifier__company=user.company
                ).distinct()


class VerifierAgreementEnrollmentForm(forms.ModelForm):
    """Enrollee form for information required at signup."""

    mailing_geocode_street_line1 = forms.CharField(max_length=100, label="Address Line 1")
    mailing_geocode_street_line2 = forms.CharField(
        max_length=100, label="Address Line 2", required=False
    )
    mailing_geocode_zipcode = forms.CharField(max_length=15, label="ZIP Code")
    mailing_geocode_city = ApiModelChoiceField(
        widget=UnrestrictedCityChoiceWidget, required=True, label="City"
    )

    shipping_geocode_street_line1 = forms.CharField(
        max_length=100, label="Address Line 1", required=True
    )
    shipping_geocode_street_line2 = forms.CharField(
        max_length=100, label="Address Line 2", required=False
    )
    shipping_geocode_zipcode = forms.CharField(max_length=15, label="ZIP Code", required=True)
    shipping_geocode_city = ApiModelChoiceField(
        widget=UnrestrictedCityChoiceWidget, required=True, label="City"
    )

    applicant_first_name = forms.CharField(max_length=30, label="First Name", required=True)
    applicant_last_name = forms.CharField(max_length=30, label="Last Name", required=True)
    applicant_title = forms.CharField(max_length=100, label="Title", required=True)
    applicant_phone_number = forms.CharField(max_length=30, label="Phone Number", required=True)
    applicant_email = forms.CharField(max_length=30, label="Email", required=True)

    administrative_contact_first_name = forms.CharField(
        max_length=30, label="First Name", required=True
    )
    administrative_contact_last_name = forms.CharField(
        max_length=30, label="Last Name", required=True
    )
    administrative_contact_phone_number = forms.CharField(
        max_length=30, label="Phone Number", required=True
    )
    administrative_contact_email = forms.EmailField(
        max_length=100, label="Email Address", required=True
    )

    company_officer_first_name = forms.CharField(max_length=30, label="First Name", required=True)
    company_officer_last_name = forms.CharField(max_length=30, label="Last Name", required=True)
    company_officer_title = forms.CharField(max_length=30, label="Title", required=True)
    company_officer_phone_number = forms.CharField(
        max_length=30, label="Phone Number", required=True
    )
    company_officer_email = forms.EmailField(max_length=100, label="Email Address", required=True)

    class Meta:
        model = VerifierAgreement
        fields = ENROLLMENT_FIELDS
        labels = ENROLLMENT_LABELS
        widgets = {"provided_services": BigSelectMultiple(), "us_states": BigSelectMultiple()}

    def __init__(self, *args, **kwargs):
        super(VerifierAgreementEnrollmentForm, self).__init__(*args, **kwargs)


class VerifierAgreementManagementForm(forms.ModelForm):
    """Label fields with management names."""

    class Meta:
        model = VerifierAgreement
        fields = MANAGEMENT_FIELDS
        labels = MANAGEMENT_LABELS


class COIDocumentForm(AjaxBase64FileFormMixin.for_fields(["document"]), forms.ModelForm):
    """Standard `CustomerDocument` upload form.

    This form supports base64-encoded payloads on the `document_raw` field, which is preferred over
    `document` if it is present.
    """

    class Meta:
        model = COIDocument
        fields = ("document", "description", "policy_number", "start_date", "expiration_date")


class BasicCOIDocumentForm(AjaxBase64FileFormMixin.for_fields(["document"]), forms.ModelForm):
    class Meta:
        model = COIDocument
        fields = ("document", "description")
