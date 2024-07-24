"""api.py: remrate data"""
import logging

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Project, HousePlan
from .serializers import AxisHousePlanListingSerializer
from .tasks import import_project_tree
from .utils import stub_project_list, stub_houseplan_list

__author__ = "Autumn Valenta"
__date__ = "5/27/13 10:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]

log = logging.getLogger(__name__)


class RemoteObjectMixin(object):
    """Core queryset for successfully imported object."""

    def get_queryset(self):
        return self.model.objects.filter(import_failed=False)

    def filter_queryset(self, queryset):
        return queryset.filter_by_user(self.request.user)


class ProjectViewSet(RemoteObjectMixin, ModelViewSet):
    model = Project

    def get_queryset(self):
        if hasattr(self, "request"):
            if hasattr(self.request.user, "ekotropeauthdetails"):
                stub_project_list(self.request.user.ekotropeauthdetails)
        return super(ProjectViewSet, self).get_queryset()


class UnattachedProjectViewSet(ProjectViewSet):
    def filter_queryset(self, queryset):
        queryset = super(UnattachedProjectViewSet, self).filter_queryset(queryset)
        return queryset.filter(houseplan__floorplan__isnull=True).order_by("-created_date")


class HousePlanViewSet(RemoteObjectMixin, ModelViewSet):
    model = HousePlan
    serializer_class = AxisHousePlanListingSerializer

    def get_queryset(self):
        if hasattr(self, "request"):
            if hasattr(self.request.user, "ekotropeauthdetails"):
                project_id = self.request.query_params.get("project")
                if project_id:
                    stub_houseplan_list(self.request.user.ekotropeauthdetails, project_id)
        return super(HousePlanViewSet, self).get_queryset()

    def filter_queryset(self, queryset):
        queryset = super(HousePlanViewSet, self).filter_queryset(queryset)
        project_id = self.request.query_params.get("project")
        if project_id:
            queryset = queryset.filter(project__id=project_id)
        return queryset

    @action(
        detail=False,
        methods=["get"],
        url_path="refresh-projects",
        url_name="refresh-projects",
    )
    def refresh_projects(self, request, pk=None, *args, **kwargs):
        """This will pull new projects into axis"""
        if not hasattr(self.request.user, "ekotropeauthdetails"):
            return Response(
                {"error": "Missing Ekotrope auth details"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        new_projects = stub_project_list(self.request.user.ekotropeauthdetails)
        for project in new_projects:
            import_project_tree.delay(self.request.user.ekotropeauthdetails.pk, project["id"])
        if not new_projects:
            msg = "Nothing to do"
            return Response({"msg": msg}, status=status.HTTP_200_OK)
        msg = "Dispatched `import_project_tree` on %d new projects" % len(new_projects)
        return Response({"msg": msg}, status=status.HTTP_201_CREATED)


class UnattachedHousePlanViewSet(HousePlanViewSet):
    def filter_queryset(self, queryset):
        queryset = super(UnattachedHousePlanViewSet, self).filter_queryset(queryset)
        return queryset.filter(floorplan__isnull=True).order_by("-created_date")
