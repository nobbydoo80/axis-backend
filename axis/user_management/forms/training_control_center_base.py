"""control_center_base.py: """


from django import forms

from axis.company.models import Company
from axis.user_management.models import Training
from axis.core.widgets import FilterSelect

__author__ = "Artem Hruzd"
__date__ = "10/30/2019 18:25"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class TrainingControlCenterBaseFilterForm(forms.Form):
    company = forms.ModelChoiceField(
        queryset=Company.objects.none(), widget=FilterSelect, required=False
    )
    training_type = forms.ChoiceField(
        choices=(("", "-----"),) + Training.TRAINING_TYPE_CHOICES,
        widget=FilterSelect,
        required=False,
    )

    training_date_range = forms.ChoiceField(
        choices=(
            ("", "-----"),
            ("1", "Last Training > 90 Days Ago"),
            ("2", "Last Training < 90 Days Ago"),
        ),
        widget=FilterSelect,
        required=False,
    )
    training_date_start = forms.DateField(
        label="Training date start", widget=forms.TextInput(attrs={"class": "form-control"})
    )
    training_date_end = forms.DateField(
        label="Training date end", widget=forms.TextInput(attrs={"class": "form-control"})
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        companies = kwargs.pop("companies", Company.objects.none())
        super(TrainingControlCenterBaseFilterForm, self).__init__(*args, **kwargs)
        if user.is_superuser:
            self.fields["company"].queryset = companies
        else:
            del self.fields["company"]
