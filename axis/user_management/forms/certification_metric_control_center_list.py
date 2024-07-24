"""certification_metric_control_center_list.py: """


from django import forms

from axis.company.models import Company
from axis.core.widgets import FilterSelect
from axis.eep_program.models import EEPProgram

__author__ = "Artem Hruzd"
__date__ = "10/30/2019 18:25"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class CertificationMetricControlCenterListFilterForm(forms.Form):
    company = forms.ModelChoiceField(
        queryset=Company.objects.none(), widget=FilterSelect, required=False
    )
    eep_program = forms.ModelChoiceField(
        label="Program", queryset=EEPProgram.objects.none(), widget=FilterSelect, required=False
    )
    date_start = forms.DateField(
        label="Certification date start", widget=forms.TextInput(attrs={"class": "form-control"})
    )
    date_end = forms.DateField(
        label="Certification date end", widget=forms.TextInput(attrs={"class": "form-control"})
    )

    def __init__(self, *args, **kwargs):
        _ = kwargs.pop("user")
        companies = kwargs.pop("companies")
        eep_programs = kwargs.pop("eep_programs")
        super(CertificationMetricControlCenterListFilterForm, self).__init__(*args, **kwargs)
        self.fields["company"].queryset = companies
        self.fields["eep_program"].queryset = eep_programs
