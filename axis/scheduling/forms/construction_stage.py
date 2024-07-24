"""construction_stage.py: """


from django import forms

from axis.scheduling.models import ConstructionStage

__author__ = "Artem Hruzd"
__date__ = "01/13/2020 12:43"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class ConstructionStageForm(forms.ModelForm):
    class Meta:
        exclude = ["is_public"]
        model = ConstructionStage

    def clean_order(self):
        if self.cleaned_data["order"] < 1:
            raise forms.ValidationError("The order must be between 0-100")
        if self.cleaned_data["order"] > 99:
            raise forms.ValidationError("The order must be between 0-100")
        return self.cleaned_data["order"]
