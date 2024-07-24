"""task_type.py: """


from django import forms

from axis.scheduling.models import TaskType

__author__ = "Artem Hruzd"
__date__ = "01/13/2020 12:43"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class TaskTypeForm(forms.ModelForm):
    class Meta:
        model = TaskType
        fields = (
            "id",
            "name",
        )
