"""seed.py - simulation"""

__author__ = "Steven K"
__date__ = "3/19/21 12:13"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import datetime
import logging

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from simulation.apps import app
from simulation.enumerations import SeedStatus
from simulation.models import (
    Seed,
    Simulation,
    get_ekotrope_outstanding_queryset,
    get_rem_outstanding_queryset,
)
from simulation.serializers.simulation.base import SeedSerializer

from axis.core.api_v3.filters import AxisFilterBackend, AxisSearchFilter, AxisOrderingFilter
from axis.ekotrope.models import Project as EkoProject
from axis.floorplan.api_v3 import SEED_SEARCH_FIELDS, SEED_ORDERING_FIELDS
from axis.floorplan.api_v3.filters import SeedFilter
from axis.remrate_data.models import Simulation as RemSimulation

log = logging.getLogger(__name__)


class SeedViewSet(
    viewsets.mixins.RetrieveModelMixin, viewsets.mixins.ListModelMixin, viewsets.GenericViewSet
):
    """
    retrieve:
        Get a Simulation Seed ID

        Returns a Simulation Seed. This is the bridge between the source data and the Axis
        simulation model.
    list:
        Get all Simulation Seed

        Returns all Simulation Seeds
    """

    model = Seed
    queryset = model.objects.all()
    filterset_class = SeedFilter
    filter_backends = [AxisFilterBackend, AxisSearchFilter, AxisOrderingFilter]
    search_fields = SEED_SEARCH_FIELDS
    ordering_fields = SEED_ORDERING_FIELDS
    serializer_class = SeedSerializer

    def get_queryset(self):
        queryset = super(SeedViewSet, self).get_queryset()
        queryset = queryset.filter_by_user(user=self.request.user)
        return self.get_serializer_class().get_prefetch_and_select_related_keys(queryset)

    @property
    def permission_classes(self):
        if self.action in [
            "list",
            "retrieve",
        ]:
            return (IsAuthenticated,)
        if self.action in [
            "summary",
        ]:
            return (IsAdminUser,)
        return (IsAuthenticated,)

    @action(detail=False)
    def summary(self, request, *args, **kwargs):
        """This will pull the daily summary of data"""
        end_day = kwargs.get("end_day")
        if end_day is None:
            end_day = datetime.datetime.today().replace(
                hour=0, minute=0, second=0, microsecond=0, tzinfo=datetime.timezone.utc
            )
        start_day = kwargs.get("start_day")
        if start_day is None:
            start_day = end_day - datetime.timedelta(days=1)

        eko_created = EkoProject.objects.filter(
            data__isnull=False,
            houseplan__data__isnull=False,
            analysis__data__isnull=False,
            created_date__gte=start_day,
            created_date__lt=end_day,
        )
        eko_outstanding = get_ekotrope_outstanding_queryset()

        rem_created = RemSimulation.objects.filter(
            export_type__in=app.REMRATE_DESIGN_MODELS,
            site__isnull=False,
            building__created_on__gte=start_day,
            building__created_on__lt=end_day,
        )
        rem_outstanding = get_rem_outstanding_queryset()

        axis_created = Simulation.objects.filter(
            created_date__gte=start_day, created_date__lt=end_day
        )

        failed = Seed.objects.filter(
            status=SeedStatus.FAILED, created_date__gte=start_day, created_date__lt=end_day
        )

        not_replicated = Seed.objects.filter(
            status=SeedStatus.NOT_REPLICATED, created_date__gte=start_day, created_date__lt=end_day
        )

        return Response(
            {
                "created_window": {
                    "start_window": str(start_day),
                    "end_window": str(end_day),
                    "remrate_sql": rem_created.count(),
                    "ekotrope": eko_created.count(),
                    "axis": axis_created.count(),
                    "failed": failed.count(),
                    "not_replicated": not_replicated.count(),
                },
                "outstanding": {
                    "remrate_sql": rem_outstanding.count(),
                    "ekotrope": eko_outstanding.count(),
                },
            }
        )
