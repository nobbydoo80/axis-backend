"""task_type.py: """


from rest_framework import viewsets

from axis.examine.api import ExamineViewSetAPIMixin
from axis.scheduling.models import TaskType
from axis.scheduling.serializers import TaskTypeSerializer

__author__ = "Artem Hruzd"
__date__ = "01/13/2020 12:46"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class TaskTypeViewSet(ExamineViewSetAPIMixin, viewsets.ModelViewSet):
    model = TaskType
    queryset = model.objects.all()
    serializer_class = TaskTypeSerializer

    def get_examine_machinery_class(self, raise_exception=True):
        from axis.scheduling.views.examine import TaskTypeMachinery

        return TaskTypeMachinery
