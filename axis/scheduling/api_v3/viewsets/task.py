# -*- coding: utf-8 -*-
"""task.py: """

__author__ = "Artem Hruzd"
__date__ = "10/10/2022 19:54"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

import django_auto_prefetching
import icalendar
from django.apps import apps
from django.http import HttpResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from axis.core.api_v3.filters import AxisSearchFilter, AxisOrderingFilter, AxisFilterBackend
from axis.core.api_v3.viewsets import NestedHistoryViewSet
from axis.filehandling.models import AsynchronousProcessedDocument
from axis.scheduling.api_v3 import TASK_ORDERING_FIELDS, TASK_SEARCH_FIELDS
from axis.scheduling.api_v3.filters import TaskFilter
from axis.scheduling.api_v3.serializers import TaskFlatListSerializer, TaskSerializer
from axis.scheduling.api_v3.serializers.task import (
    TaskChangeStateSerializer,
    TaskChangeStatusSerializer,
    TaskExportToCalSerializer,
)
from axis.scheduling.models import Task
from axis.scheduling.tasks import scheduling_task_report_task

frontend_app = apps.get_app_config("frontend")


class SchedulingTaskViewSet(viewsets.ModelViewSet):
    """ """

    model = Task
    queryset = model.objects.all()
    filter_backends = [AxisFilterBackend, AxisSearchFilter, AxisOrderingFilter]
    serializer_class = TaskSerializer
    search_fields = TASK_SEARCH_FIELDS
    ordering_fields = TASK_ORDERING_FIELDS

    def get_queryset(self):
        queryset = super(SchedulingTaskViewSet, self).get_queryset()
        queryset = queryset.filter_by_user(user=self.request.user)
        return django_auto_prefetching.prefetch(queryset, self.get_serializer_class())

    @property
    def filterset_class(self):
        return TaskFilter

    @property
    def permission_classes(self):
        if self.action in [
            "list",
            "retrieve",
        ]:
            return (IsAuthenticated,)

        return (IsAuthenticated,)

    @action(detail=False, serializer_class=TaskFlatListSerializer)
    def flat_list(self, request, *args, **kwargs):
        return super(SchedulingTaskViewSet, self).list(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(assigner=self.request.user)

    @action(detail=False, methods=["patch"], serializer_class=TaskChangeStateSerializer)
    def change_state(self, request):
        """
        Change state for list of `task_ids`
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["patch"], serializer_class=TaskChangeStatusSerializer)
    def change_status(self, request):
        """
        Change status for list of `task_ids`
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], serializer_class=TaskExportToCalSerializer)
    def export_to_cal(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tasks = self.get_queryset().filter(id__in=serializer.validated_data["task_ids"])

        cal = icalendar.Calendar()
        cal.add("prodid", "-// AXIS //")
        cal.add("version", "2.0")

        for task in tasks:
            event = icalendar.Event()
            event.add("summary", "AXIS Task {} from {}".format(task, task.assigner))
            event.add("dtstart", task.datetime)
            event.add("description", task.note)
            if task.home_id:
                event.add("location", task.home.get_home_address_display())

            cal.add_component(event)

        response = HttpResponse(cal.to_ical(), content_type="text/calendar")
        response["Filename"] = "filename.ics"  # IE needs this
        response["Content-Disposition"] = 'attachment; filename="axis_scheduled_tasks.ics"'
        return response

    @action(detail=False, methods=["get"])
    def create_scheduling_task_report(self, request):
        task_ids = list(self.filter_queryset(self.get_queryset()).values_list("id", flat=True))
        asynchronous_process_document = AsynchronousProcessedDocument(
            download=True, company=request.user.company
        )
        asynchronous_process_document.download = True
        asynchronous_process_document.company = self.request.user.company
        asynchronous_process_document.save()

        scheduling_task_report_task.delay(
            asynchronous_process_document_id=asynchronous_process_document.id,
            task_ids=task_ids,
            user_id=self.request.user.id,
        )
        return Response(
            {
                "asynchronous_process_document_id": asynchronous_process_document.id,
                "asynchronous_process_document_url": request.build_absolute_uri(
                    asynchronous_process_document.get_absolute_url()
                ),
            },
            status=status.HTTP_200_OK,
        )


class SchedulingTaskNestedHistoryViewSet(NestedHistoryViewSet):
    model = Task.history.model
    queryset = model.objects.all()
    permission_classes = (IsAuthenticated,)
    filter_backends = [AxisFilterBackend, AxisSearchFilter, AxisOrderingFilter]
    search_fields = TASK_SEARCH_FIELDS
    ordering_fields = TASK_ORDERING_FIELDS
