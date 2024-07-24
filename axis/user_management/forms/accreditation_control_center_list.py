"""accreditation_control_center_list.py: """


from django import forms

from axis.company.models import Company
from axis.user_management.models import Accreditation
from axis.core.widgets import FilterSelect

__author__ = "Artem Hruzd"
__date__ = "10/30/2019 18:25"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class AccreditationControlCenterListFilterForm(forms.Form):
    company = forms.ModelChoiceField(
        queryset=Company.objects.none(), widget=FilterSelect, required=False
    )
    state = forms.ChoiceField(
        choices=(("", "-----"),) + Accreditation.STATE_CHOICES,
        widget=FilterSelect,
        label="Accreditation status",
        required=False,
    )
    expiration_within = forms.ChoiceField(
        choices=(("", "-----"), ("90", "90 days")), widget=FilterSelect, required=False
    )
    expiration_date_start = forms.DateField(
        label="Start", widget=forms.TextInput(attrs={"class": "form-control"})
    )
    expiration_date_end = forms.DateField(
        label="End", widget=forms.TextInput(attrs={"class": "form-control"})
    )
    date_initial_start = forms.DateField(
        label="Start", widget=forms.TextInput(attrs={"class": "form-control"})
    )
    date_initial_end = forms.DateField(
        label="End", widget=forms.TextInput(attrs={"class": "form-control"})
    )
    date_last_start = forms.DateField(
        label="Start", widget=forms.TextInput(attrs={"class": "form-control"})
    )
    date_last_end = forms.DateField(
        label="End", widget=forms.TextInput(attrs={"class": "form-control"})
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        super(AccreditationControlCenterListFilterForm, self).__init__(*args, **kwargs)
        if user.is_superuser:
            self.fields["company"].queryset = Company.objects.filter(
                pk__in=Accreditation.objects.all().values_list("trainee__company__pk", flat=True)
            ).distinct()
        else:
            del self.fields["company"]
