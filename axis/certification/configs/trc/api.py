import logging
from datetime import timedelta

from django.utils.timezone import now
from django.db.models.query import Q

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.routers import SimpleRouter

from ... import models
from . import serializers
from . import utils


__author__ = "Autumn Valenta"
__date__ = "9/20/17 4:38 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


# Viewsets
class TRCViewSet(viewsets.ViewSet):
    url_basename = "trc_projects"  # Used for name reversals

    def get_project_statuses(self):
        return models.WorkflowStatus.objects.filter_by_user(self.request.user).filter(
            certifiable_object__type="project"
        )

    def get_project_status(self):
        return self.get_project_statuses().get(id=self.kwargs["pk"])

    @action(detail=True, methods=["get"])
    def summary(self, request, *args, **kwargs):
        """Returns a TRC-friendly serialization of a whole Project tree."""
        project_status = self.get_project_status()
        serializer = serializers.SummarySerializer(
            project_status,
            context={
                "request": request,
                "type": "project",
            },
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"])
    def changed(self, request, *args, **kwargs):
        """Returns items modified within the last 7 days."""
        one_week_ago = now() - timedelta(days=7)
        queryset = self.get_project_statuses().filter(
            Q(modified_date__gte=one_week_ago)
            | Q(certifiable_object__modified_date__gte=one_week_ago)
        )
        object_list = list(queryset)

        serializer = serializers.SummarySerializer(
            instance=object_list,
            many=True,
            context={
                "request": request,
                "type": "project",
            },
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"])
    def project_import(self, request, *args, **kwargs):
        serializer = serializers.ImportSerializer(
            data=request.data,
            context={
                "request": request,
            },
        )
        try:
            is_valid = serializer.is_valid()
        except Exception as e:
            log.exception("TRC import API error during serializer validation; see traceback")
            return Response(
                {
                    "message": "Internal error during validation step.",
                    "error": "{}".format(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        if is_valid:
            workflowstatus = serializer.save()
            response_serializer = serializers.SummarySerializer(
                workflowstatus,
                context={
                    "request": request,
                    "type": "project",
                },
            )
            return Response(response_serializer.data, status=status.HTTP_200_OK)

        error_data = getattr(serializer, "raw_errors", serializer.errors)
        return Response(
            {
                "message": "Validation error for data.",
                "errors": error_data,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(detail=True, methods=["patch"])
    def escalate(self, request, *args, **kwargs):
        """Sets the elevation flag on a WorkflowStatus"""
        workflowstatus = self.get_project_status()
        workflowstatus.data["escalated"] = now()
        workflowstatus.save()

        # Notify company admins
        utils.send_escalated_notification(workflowstatus)

        return Response(
            {
                "id": workflowstatus.pk,
                "escalated": workflowstatus.data["escalated"],
            }
        )

    @action(detail=True, methods=["patch"])
    def deescalate(self, request, *args, **kwargs):
        """Sets the elevation flag on a WorkflowStatus"""
        workflowstatus = self.get_project_status()
        workflowstatus.data["escalated"] = None
        workflowstatus.save()
        return Response(
            {
                "id": workflowstatus.pk,
                "escalated": workflowstatus.data["escalated"],
            }
        )


# Build urlpatterns for insertion in axis/certification/api/urls.py
viewset_urls = ((r"certification/trc", TRCViewSet),)

router = SimpleRouter()
for url, viewset in viewset_urls:
    router.register(url, viewset, viewset.url_basename)
urlpatterns = router.urls
