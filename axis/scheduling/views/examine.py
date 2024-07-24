from axis import examine
from ..api import TaskTypeViewSet, TaskViewSet
from ..forms import TaskTypeForm, TaskForm, UserTaskForm
from ..models import TaskType, Task

__author__ = "Michael Jeffrey"
__date__ = "9/13/16 11:33 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Michael Jeffrey",
]


class TaskTypeMachinery(examine.TableMachinery):
    model = TaskType
    api_provider = TaskTypeViewSet
    type_name = "task_type"
    form_class = TaskTypeForm

    def get_visible_fields(self, instance, form):
        return ["name"]

    def get_field_order(self, instance, form):
        # Modal templates use field_order rather than visible_fields
        return self.get_visible_fields(instance, form)


class TaskHomeMachinery(examine.PanelMachinery):
    model = Task
    api_provider = TaskViewSet
    type_name = "home_task"
    form_class = TaskForm

    regionset_template = "examine/scheduling/home_task_regionset_panel.html"
    region_template = "examine/scheduling/home_task_region_panel.html"
    form_template = "examine/scheduling/home_task_form_panel.html"
    detail_template = "examine/scheduling/home_task_detail_default.html"

    def get_visible_fields(self, instance, form):
        return ["task_type", "date", "time", "assignees", "status", "note", "is_public"]

    def get_field_order(self, instance, form):
        return self.get_visible_fields(instance, form)

    def get_form_kwargs(self, instance):
        home_id = self.context.get("home_id")
        return {"user": self.context["request"].user, "home_id": home_id}

    def get_region_dependencies(self):
        return {"home": [{"field_name": "id", "serialize_as": "home"}]}


class TaskUserMachinery(examine.PanelMachinery):
    model = Task
    api_provider = TaskViewSet
    type_name = "user_task"
    form_class = UserTaskForm

    regionset_template = "examine/scheduling/user_task_regionset_panel.html"
    region_template = "examine/scheduling/home_task_region_panel.html"
    form_template = "examine/scheduling/user_task_form_panel.html"
    detail_template = "examine/scheduling/home_task_detail_default.html"

    def get_visible_fields(self, instance, form):
        return [
            "task_type",
            "date",
            "time",
            "status",
            "note",
        ]

    def get_field_order(self, instance, form):
        return self.get_visible_fields(instance, form)

    def get_form_kwargs(self, instance):
        return {"user": self.context["request"].user}

    def get_region_dependencies(self):
        return {"user": [{"field_name": "id", "serialize_as": "region_assignee"}]}
