"""task.py: """
__author__ = "Artem Hruzd"
__date__ = "01/13/2020 12:46"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.apps import apps
from rest_framework import viewsets

from axis.examine.api import ExamineViewSetAPIMixin
from axis.scheduling.models import Task
from axis.scheduling.serializers import TaskHomeSerializer, TaskUserSerializer

frontend_app = apps.get_app_config("frontend")


class TaskViewSet(ExamineViewSetAPIMixin, viewsets.ModelViewSet):
    """
    Deprecated viewset for Home page. Use API V3 instead
    """

    model = Task
    queryset = model.objects.all()
    serializer_class = TaskHomeSerializer

    def get_examine_machinery_classes(self):
        from axis.scheduling.views.examine import TaskHomeMachinery

        return {
            "TaskHomeMachinery": TaskHomeMachinery,
        }

    def perform_create(self, serializer):
        serializer.save(assigner=self.request.user)


class TaskUserViewSet(ExamineViewSetAPIMixin, viewsets.ModelViewSet):
    """
    Deprecated viewset for Profile page. Use API V3 instead
    """

    model = Task
    queryset = model.objects.all()
    serializer_class = TaskUserSerializer

    def get_examine_machinery_classes(self):
        from axis.scheduling.views.examine import TaskUserMachinery

        return {
            "TaskUserMachinery": TaskUserMachinery,
        }

    def perform_create(self, serializer):
        serializer.save(assigner=self.request.user)
