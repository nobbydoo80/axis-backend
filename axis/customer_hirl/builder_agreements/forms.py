"""Builder Agreement and related state machine."""

__author__ = "Autumn Valenta"
__date__ = "2019-05-16 4:47 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = ["Autumn Valenta"]

import logging

from django.apps import apps
from django import forms
from django.db.models import BLANK_CHOICE_DASH

from axis.core.fields import ApiModelChoiceField
from axis.core.widgets import FilterSelect
from axis.geographic.fields import UnrestrictedCityChoiceWidget
from axis.customer_hirl.models import BuilderAgreement
from . import ui

log = logging.getLogger(__name__)
app = apps.get_app_config("customer_hirl")


class FilterForm(forms.Form):
    """Filter form that feeds into the datatables ajax filters."""

    state = forms.ChoiceField(
        label=ui.STATE_LABEL,
        widget=FilterSelect,
        choices=(("", BLANK_CHOICE_DASH),) + BuilderAgreement.STATE_CHOICES,
        required=False,
    )
    company = forms.ModelChoiceField(
        label="Company", widget=FilterSelect, queryset=app.enrollee_queryset, required=False
    )
    agreement_expiration_date = forms.ChoiceField(
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

    agreement_insurance_expiration_date = forms.ChoiceField(
        choices=(
            ("", "-----"),
            ("1", "30 days"),
            ("2", "60 days"),
            ("3", "90 days"),
            ("4", "More than 90 days"),
        ),
        widget=FilterSelect,
        required=False,
        label="COI Expiration Date",
    )
