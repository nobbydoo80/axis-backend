"""urls.py: Django builder_agreement"""


import logging

from django import forms
from axis.company.strings import COMPANY_TYPES
from axis.filehandling.models import AsynchronousProcessedDocument

from django_select2.forms import Select2Widget

from .models import BuilderAgreement
from axis.company.models import BuilderOrganization, Company
from axis.geographic.models import City
from axis.community.models import Community
from axis.subdivision.models import Subdivision
import axis

__author__ = "Steven Klass"
__date__ = "5/21/12 12:58 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class BuilderAgreementCreateForm(forms.ModelForm):
    subdivision = forms.ModelChoiceField(
        queryset=Subdivision.objects.all(), widget=Select2Widget, help_text=None, required=False
    )
    builder_org = forms.ModelChoiceField(
        queryset=Company.objects.filter(company_type=Company.BUILDER_COMPANY_TYPE),
        widget=Select2Widget,
        help_text=None,
        required=True,
        label="Builder",
    )

    def __init__(self, *args, **kwargs):
        super(BuilderAgreementCreateForm, self).__init__(*args, **kwargs)

        # We're modifying widget settings here instead of in Meta.widgets so that we don't have to
        # repetitively declare the specific widget class.
        self.fields["total_lots"].widget.attrs = {"class": "input-mini"}
        self.fields["start_date"].widget.attrs = {"class": "input-small datepicker"}
        self.fields["expire_date"].widget.attrs = {"class": "input-small datepicker"}
        self.fields["comment"].widget.attrs = {"class": "form-control", "attrs": {"rows": 3}}

    class Meta:
        model = BuilderAgreement
        exclude = ("lots_paid", "is_active", "is_legacy", "documents")
        labels = {
            "eep_programs": "Programs",
        }

    def clean(self):
        """Validates the Subdivision."""
        data = self.cleaned_data
        if "subdivision" not in data or "builder_org" not in data:
            return data  # Validation can't possibly work
        if data["subdivision"] and data["subdivision"].builder_org.id != data["builder_org"].id:
            err = (
                'The subdivision "{}" builder "{}" does not match the builder provided '
                'in the form "{}"'
            )
            err = err.format(
                data["subdivision"], data["subdivision"].builder_org, data["builder_org"]
            )
            log.warning(err)
            raise forms.ValidationError(err)
        if data["subdivision"]:
            if BuilderAgreement.objects.filter(
                builder_org=data["builder_org"],
                subdivision=data["subdivision"],
                company=data["company"],
            ).count():
                err = "A builder agreement for {} already exists".format(data["subdivision"])
                log.warning(err)
                raise forms.ValidationError(err)
        else:
            if BuilderAgreement.objects.filter(
                builder_org=data["builder_org"], subdivision__isnull=True, company=data["company"]
            ).count():
                err = "A builder agreement for {} already exists".format(data["builder_org"])
                log.warning(err)
                raise forms.ValidationError(err)
        return data


class BuilderAgreementUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(BuilderAgreementUpdateForm, self).__init__(*args, **kwargs)

        # We're modifying widget settings here instead of in Meta.widgets so that we don't have to
        # repetitively declare the specific widget class.
        self.fields["start_date"].widget.attrs = {"class": "datepicker"}
        self.fields["expire_date"].widget.attrs = {"class": "datepicker"}
        self.fields["comment"].widget.attrs = {"class": "form-control", "attrs": {"rows": 4}}

    class Meta:
        model = BuilderAgreement
        exclude = ("subdivision", "builder_org", "company", "lots_paid", "documents")
        labels = {"eep_programs": "Programs eligible for payment"}
        help_texts = {
            "eep_programs": "",
        }


class BuilderAgreementStatusForm(forms.Form):
    subdivision = forms.ModelChoiceField(
        queryset=Subdivision.objects.all(), help_text=None, required=False
    )
    community = forms.ModelChoiceField(
        queryset=Community.objects.all(), help_text=None, required=False
    )
    city = forms.ModelChoiceField(queryset=City.objects.all(), required=False)
    hers_min = forms.IntegerField(required=False)
    hers_max = forms.IntegerField(required=False)
    start = forms.DateField(required=False)
    end = forms.DateField(required=False)

    search_bar = forms.CharField(max_length=100, required=False, widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(BuilderAgreementStatusForm, self).__init__(*args, **kwargs)

        self.fields["hers_min"].label = "HERS min"
        self.fields["hers_max"].label = "HERS max"

        for co_type, label in dict(COMPANY_TYPES).items():
            self.fields[co_type] = forms.ModelChoiceField(
                queryset=Company.objects.none(), required=False, label=label
            )


class BuilderSubdivisionReportForm(forms.ModelForm):
    subdivision = forms.ModelChoiceField(
        queryset=Subdivision.objects.all(), help_text=None, required=False
    )
    community = forms.ModelChoiceField(
        queryset=Community.objects.all(), help_text=None, required=False
    )
    city = forms.ModelChoiceField(queryset=City.objects.all(), required=False)
    hers_min = forms.IntegerField(required=False)
    hers_max = forms.IntegerField(required=False)
    start = forms.DateField(required=False)
    end = forms.DateField(required=False)

    company = forms.ModelChoiceField(queryset=Company.objects.none(), required=False)
    search_bar = forms.CharField(max_length=100, required=False, widget=forms.HiddenInput())

    class Meta:
        model = AsynchronousProcessedDocument
        fields = ("task_name",)

    def __init__(self, *args, **kwargs):
        super(BuilderSubdivisionReportForm, self).__init__(*args, **kwargs)
        for co_type, label in dict(COMPANY_TYPES).items():
            self.fields[co_type] = forms.ModelChoiceField(
                queryset=Company.objects.none(), required=False, label=label
            )

    def clean_task_name(self):
        """This is the task name"""
        from .tasks import export_status_report

        return export_status_report

    def clean(self):
        """Validate the dates"""
        cleaned_data = super(BuilderSubdivisionReportForm, self).clean()
        cleaned_data["task_name"] = self.clean_task_name()
        return cleaned_data
