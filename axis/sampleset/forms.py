"""forms.py: Django sampleset"""


import logging

from django import forms
from django.db.models import Q

from django_select2.forms import Select2MultipleWidget, Select2Widget

from axis.company.models import Company, ProviderOrganization, BuilderOrganization
from axis.eep_program.models import EEPProgram
from axis.home.models import EEPProgramHomeStatus
from axis.subdivision.models import Subdivision
from .models import SampleSet

__author__ = "Autumn Valenta"
__date__ = "07/30/14 12:43 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class HomeQueryForm(forms.Form):
    """Form that powers table manipulations for the home adder."""

    has_sampleset = forms.ChoiceField(
        label="Sample Set",
        required=False,
        choices=(
            ("", "All"),
            ("0", "Unassigned"),
            ("1", "Assigned"),
        ),
    )
    has_answers = forms.ChoiceField(
        label="Sampled type",
        required=False,
        choices=(
            ("", "All"),
            ("1", "Test houses only"),
            ("0", "Non-test houses only"),
        ),
    )
    name = forms.ChoiceField(label="Sample set name", required=False, widget=Select2Widget)
    start_date = forms.ChoiceField(
        label="Sample set start date", required=False, widget=Select2Widget
    )
    eep_program = forms.ModelMultipleChoiceField(
        label="Program",
        required=False,
        queryset=EEPProgram.objects.all(),
        widget=Select2MultipleWidget,
    )
    builder = forms.ModelChoiceField(
        required=False,
        queryset=Company.objects.filter(company_type=Company.BUILDER_COMPANY_TYPE).all(),
        widget=Select2Widget,
    )
    subdivision = forms.ModelMultipleChoiceField(
        required=False, queryset=Subdivision.objects.all(), widget=Select2MultipleWidget
    )
    homestatus_state = forms.ChoiceField(
        label="Certification status",
        initial="uncertified",
        required=False,
        choices=[("", "All"), ("uncertified", "Not Certified")]
        + EEPProgramHomeStatus.Machine.get_state_choices(),
    )

    def __init__(self, user, *args, **kwargs):
        super(HomeQueryForm, self).__init__(*args, **kwargs)

        _eep_qs = EEPProgram.objects.filter_by_user(user).filter(
            Q(allow_sampling=True) | Q(allow_metro_sampling=True)
        )
        self.fields["eep_program"].choices = list(_eep_qs.values_list("id", "name"))

        _bldr_qs = (
            Company.objects.filter(company_type=Company.BUILDER_COMPANY_TYPE)
            .filter_by_user(user)
            .filter(sampling_approved__sampling_approved=True)
            .distinct()
        )
        self.fields["builder"].choices = [("", "")] + list(_bldr_qs.values_list("id", "name"))

        _sub_qs = Subdivision.objects.choice_items_from_instances(
            user, Q(use_sampling=True) | Q(use_metro_sampling=True)
        )
        self.fields["subdivision"].choices = _sub_qs

        names = (
            SampleSet.objects.filter_by_user(user)
            .order_by("alt_name", "uuid")
            .values("uuid", "alt_name")
        )
        self.fields["name"].choices = [("", "")] + [
            (
                data["uuid"],
                (
                    ("%s (%s)" % (data["alt_name"], data["uuid"][:8]))
                    if data["alt_name"]
                    else data["uuid"][:8]
                ),
            )
            for data in names
        ]

        dates = (
            SampleSet.objects.filter_by_user(user)
            .order_by("start_date")
            .values_list("start_date", flat=True)
            .distinct()
        )
        self.fields["start_date"].choices = [("", "")] + [(v, v) for v in dates]

        if user.is_superuser:
            _own_qs = Company.objects.filter_by_user(user).filter(
                Q(sampling_approved__sampling_approved=True, company_type="rater")
                | Q(company_type="provider")
            )
            self.fields["owner"] = forms.ModelMultipleChoiceField(
                required=False, queryset=Company.objects.all(), widget=Select2Widget
            )
            self.fields["owner"].choices = [("", "All")] + list(_own_qs.values_list("id", "name"))


class SamplingProviderApprovalFormSet(forms.models.BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super(SamplingProviderApprovalFormSet, self).__init__(*args, **kwargs)
        if user and not user.is_superuser:
            queryset = Company.objects.filter(
                id=user.company.id, company_type=Company.PROVIDER_COMPANY_TYPE
            )
            for form in self.forms:
                form.fields["provider"].initial = user.company.id
                form.fields["provider"].queryset = queryset
