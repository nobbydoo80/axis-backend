"""task.py: """

__author__ = "Artem Hruzd"
__date__ = "01/13/2020 12:43"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


from django import forms
from django.contrib.auth import get_user_model

from axis.scheduling.models import TaskType, Task
from axis.home.models import Home

User = get_user_model()


class TaskForm(forms.ModelForm):
    date = forms.DateField(required=True)
    time = forms.TimeField(required=True)

    class Meta:
        model = Task
        # In Region Set type forms, we don't have a good way of knowing when a field is required
        # so for now, we're changing the labels to what we know are required.
        labels = {
            "task_type": "Task Type",
            "date": "Date",
            "assignees": "Who",
            "status": "Completion Status",
        }
        fields = ("task_type", "date", "assignees", "time", "status", "note", "is_public")

    def __init__(self, user, *args, **kwargs):
        home_id = kwargs.pop("home_id", None)
        super(TaskForm, self).__init__(*args, **kwargs)

        assigner = user
        if self.instance.pk:
            assigner = self.instance.assigner

        assigner_user_ids = assigner.company.users.values_list("id", flat=True)
        relationships_user_ids = []

        if home_id:
            home = Home.objects.get(id=home_id)
            relationships_user_ids = home.relationships.values_list(
                "company__users__id", flat=True
            ).distinct()

        self.fields["assignees"].queryset = User.objects.filter(
            id__in=list(relationships_user_ids) + list(assigner_user_ids), is_active=True
        ).distinct()
        self.fields["task_type"].queryset = TaskType.objects.filter_by_user(assigner)
        self.fields["assignees"].label_from_instance = self.assignees_label

    @staticmethod
    def assignees_label(user):
        return f"{user.first_name} {user.last_name} ({user.company.name})"


class UserTaskForm(forms.ModelForm):
    date = forms.DateField(required=True)
    time = forms.TimeField(required=True)

    class Meta:
        model = Task
        # In Region Set type forms, we don't have a good way of knowing when a field is required
        # so for now, we're changing the labels to what we know are required.
        labels = {
            "task_type": "Task Type",
            "date": "Date",
            "status": "Completion Status",
        }
        fields = ("task_type", "date", "time", "status", "note")

    def __init__(self, user, *args, **kwargs):
        super(UserTaskForm, self).__init__(*args, **kwargs)

        assigner = user
        if self.instance.pk:
            assigner = self.instance.assigner

        self.fields["task_type"].queryset = TaskType.objects.filter_by_user(assigner)
