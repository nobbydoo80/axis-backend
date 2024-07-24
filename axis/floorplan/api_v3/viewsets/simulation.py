__author__ = "Steven K"
__date__ = "3/19/21 12:13"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

import django_auto_prefetching
import xmltodict
from botocore.exceptions import ClientError
from django.core.exceptions import ObjectDoesNotExist
from django.http.response import HttpResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_extensions.mixins import NestedViewSetMixin
from simulation.enumerations import (
    SourceType,
    AnalysisStatus,
    OpenStudioAnalysisSourceName,
)
from simulation.managers import AnalysisQuerySet
from simulation.models import (
    Project,
    MechanicalEquipment,
    FoundationWall,
    AboveGradeWall,
    Roof,
    FrameFloor,
    Window,
    Slab,
    Skylight,
    RimJoist,
    Door,
    Photovoltaic,
    Analysis,
    Infiltration,
    Lights,
    Appliances,
    Location,
    UtilityRate,
)
from simulation.models import Simulation
from simulation.serializers.rem.blg import (
    get_blg_simulation_from_floorplan,
)
from simulation.serializers.rem.xml import SimulationSerializer as RemXMLSimulationSerializer
from simulation.serializers.simulation.base import (
    ProjectSerializer,
    MechanicalEquipmentSerializer,
    FoundationWallSerializer,
    AboveGradeWallSerializer,
    RoofSerializer,
    FrameFloorSerializer,
    WindowSerializer,
    SlabSerializer,
    SkylightSerializer,
    RimJoistSerializer,
    DoorSerializer,
    PhotovoltaicSerializer,
    AnalysisSerializer,
    InfiltrationSerializer,
    LightsSerializer,
    AppliancesSerializer,
    LocationSerializer,
    UtilityRateSerializer,
)
from simulation.serializers.simulation.compare import SimulationDiffSerializer
from simulation.serializers.simulation.examine import FloorplanSimulationReadOnlySerializer
from simulation.tasks import get_open_studio_eri_result

from axis.core.api_v3.filters import AxisFilterBackend, AxisSearchFilter, AxisOrderingFilter
from axis.floorplan.api_v3 import SIMULATION_SEARCH_FIELDS, SIMULATION_ORDERING_FIELDS
from axis.floorplan.api_v3.filters import SimulationFilter
from axis.floorplan.api_v3.permissions import (
    SimulationCreatePermission,
    SimulationUpdatePermission,
    SimulationDeletePermission,
)
from axis.floorplan.api_v3.serializers import (
    SimulationSerializer,
    SimulationListSerializer,
    SimulationVersionsSerializer,
)
from axis.floorplan.api_v3.serializers.simulation import (
    SimulationTaskSerializer,
    SimulationOSERIAnalysisTypeSerializer,
)

log = logging.getLogger(__name__)


class SimulationViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    """
    Simulation viewset

    remxml:
        Download RemXML for a RemRate Simulation
    blg_remxml:
        Returns RemXML from a BLG File
    blg_compare:
        Returns differences between BLG and SQL Simulation.
    summary:
        Return basic Simulation info including analyses and seed data
    versions:
        Returns a list of Simulation versions

    """

    model = Simulation
    queryset = model.objects.all()
    filterset_class = SimulationFilter
    filter_backends = [AxisFilterBackend, AxisSearchFilter, AxisOrderingFilter]
    search_fields = SIMULATION_SEARCH_FIELDS
    ordering_fields = SIMULATION_ORDERING_FIELDS
    ordering = ("-id",)

    def get_queryset(self):
        queryset = super(SimulationViewSet, self).get_queryset()
        queryset = queryset.filter_by_user(user=self.request.user)
        return queryset

    def get_permissions(self):
        self.permission_classes = (IsAuthenticated,)
        if self.action in ["create", "create_bulk"]:
            self.permission_classes = (SimulationCreatePermission,)
        if self.action in ["list", "retrieve", "remxml", "blg_remxml"]:
            self.permission_classes = (IsAuthenticated,)
        if self.action in ["update", "partial_update", "open_studio_eri"]:
            self.permission_classes = (SimulationUpdatePermission,)
        if self.action in ["destroy"]:
            self.permission_classes = (SimulationDeletePermission,)
        return super(SimulationViewSet, self).get_permissions()

    def get_serializer_class(self):
        if self.action == "list":
            return SimulationListSerializer
        elif self.action == "versions":
            return SimulationVersionsSerializer
        elif self.action == "summary":
            return FloorplanSimulationReadOnlySerializer
        elif self.action == "open_studio_eri":
            return SimulationOSERIAnalysisTypeSerializer
        return SimulationSerializer

    @swagger_auto_schema(
        methods=["get"],
        responses={
            "200": openapi.Response(
                "RemXML Attachment", schema=openapi.Schema(type=openapi.TYPE_FILE)
            )
        },
    )
    @action(methods=["get"], detail=True)
    def remxml(self, request, pk):
        """Returns RemXML from simulation"""

        obj = self.get_object()
        if obj.source_type not in [
            SourceType.REMRATE_SQL,
            SourceType.REMRATE_BLG,
            SourceType.REMRATE_XML,
        ]:
            return Response(
                {"error": "Only XML from REM Data sources allowed"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = RemXMLSimulationSerializer(instance=obj).data
        xml = xmltodict.unparse(data, pretty=True)
        response = HttpResponse(xml, content_type="application/xml", status=status.HTTP_200_OK)
        response["Content-Disposition"] = f"attachment; filename=RemXML_{obj.id}.xml"
        return response

    @swagger_auto_schema(
        methods=["get"],
        responses={
            "200": openapi.Response(
                "RemXML Attachment", schema=openapi.Schema(type=openapi.TYPE_FILE)
            )
        },
    )
    @action(methods=["get"], detail=True)
    def blg_remxml(self, request, pk):
        """Returns RemXML from a BLG File that has a bound floorplan and associated to the
        simulation"""
        obj = self.get_object()
        try:
            instance = get_blg_simulation_from_floorplan(obj.floorplan)
        except (OSError, ObjectDoesNotExist, ClientError) as err:
            return Response(
                {"error": f"Associated Floorplan or BLG File does not exist - {err}"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except (ValidationError, ValueError) as err:
            return Response(
                {"error": f"Associated Floorplan unable to be converted - {err}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = RemXMLSimulationSerializer(instance=instance).data
        xml = xmltodict.unparse(data, pretty=True)
        response = HttpResponse(xml, content_type="application/xml", status=status.HTTP_200_OK)
        response["Content-Disposition"] = f"attachment; filename=RemBLG_{obj.id}.xml"
        return response

    @swagger_auto_schema(
        methods=["get"],
        responses={"200": SimulationDiffSerializer},
    )
    @action(methods=["get"], detail=True)
    def blg_compare(self, request, pk):
        """Returns differences between BLG and SQL Simulations for a given Simulation"""

        obj = self.get_object()
        try:
            blg_instance = get_blg_simulation_from_floorplan(obj.floorplan)
        except (OSError, ObjectDoesNotExist, IOError, ClientError) as err:
            return Response(
                {"error": f"Associated Floorplan or BLG File does not exist - {err}"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except (ValidationError, ValueError) as err:
            return Response(
                {"error": f"Associated Floorplan unable to be converted - {err}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        diff_serializer = SimulationDiffSerializer(
            data={"sim_1": obj.id, "sim_2": blg_instance.id}, context={"compare_remxml": True}
        )
        if not diff_serializer.is_valid(raise_exception=False):
            return Response(
                {"error": "Invalid Serializer - Bad Data", "errors": diff_serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(diff_serializer.data, status=status.HTTP_200_OK)

    @action(methods=["get"], detail=True, serializer_class=FloorplanSimulationReadOnlySerializer)
    def summary(self, *args, **kwargs):
        return super().retrieve(*args, **kwargs)

    @action(methods=["get"], detail=False)
    def versions(self, request):
        queryset = self.get_queryset()
        versions_list = list(
            queryset.values_list("version", flat=True).order_by("version").distinct()
        )
        versions_list.sort(
            key=lambda s: [int(u) for u in s.split(".") if u.isdigit()], reverse=True
        )
        serializer = self.get_serializer_class()(data={"versions": versions_list})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        responses={"201": SimulationTaskSerializer},
    )
    @action(
        methods=["post"],
        detail=True,
        url_path=r"open-studio-eri",
        filter_backends=[],
        permission_classes=[IsAuthenticated, SimulationUpdatePermission],
    )
    def open_studio_eri(self, request: Request, pk: int) -> Response:
        """Trigger the generation of an OpenStudio-ERI score.   Note: If no data is passed in the
        POST a default ERICalculation for version 2019AB will be generated.
        :param: pk Simulation ID

        """

        data = {k: v[0] if isinstance(v, list) else v for k, v in dict(request.data).items()}
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        simulation = Simulation.objects.get(pk=pk)
        analysis_types = AnalysisQuerySet().get_open_studio_analysis_types(serializer.data)
        existing = simulation.analyses.filter(type__in=analysis_types)
        if existing.exclude(status__in=[AnalysisStatus.COMPLETE, AnalysisStatus.FAILED]).exists():
            return Response(
                {"error": "Already Processing", "code": "bad_request"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        analyses = Analysis.objects.get_or_create_open_studio_analyses(
            simulation=simulation, calculations=serializer.data
        )
        # Update the status
        analyses.update(status=AnalysisStatus.PENDING)
        # Kick off the job
        task = get_open_studio_eri_result.delay(simulation.id)
        # Update the task_ids
        analyses.update(task=task.id)

        serializer = SimulationTaskSerializer(
            data={
                "id": simulation.id,
                "analysis_ids": list(existing.values_list("id", flat=True)),
                "status": AnalysisStatus.PENDING,
                "task_id": task.id,
            }
        )
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        responses={"200": SimulationTaskSerializer},
    )
    @open_studio_eri.mapping.get
    def get_os_eri(self, request: Request, pk: int) -> Response:
        simulation = self.get_object()
        existing = simulation.analyses.filter(source_name__in=OpenStudioAnalysisSourceName.values)
        if not existing.exists():
            return Response(
                {"error": "No simulation has been dispatched"}, status=status.HTTP_400_BAD_REQUEST
            )

        statuses = list(set(existing.values_list("status", flat=True)))
        task_status = AnalysisStatus.STARTED
        if "failed" in statuses:
            task_status = AnalysisStatus.FAILED
        elif len(statuses) == 1:
            task_status = AnalysisStatus(statuses[0])
        task_id = existing.first().task

        serializer = SimulationTaskSerializer(
            data={
                "id": simulation.id,
                "analysis_ids": list(existing.values_list("id", flat=True)),
                "status": task_status,
                "task_id": task_id,
            }
        )
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class NestedProjectViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    model = Project
    serializer_class = ProjectSerializer
    queryset = model.objects.all()
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        qs = super(NestedProjectViewSet, self).get_queryset()
        return qs


class NestedMechanicalEquipmentsViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    model = MechanicalEquipment
    serializer_class = MechanicalEquipmentSerializer
    queryset = model.objects.all()
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        qs = super(NestedMechanicalEquipmentsViewSet, self).get_queryset()
        return qs


class NestedFoundationWallViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    model = FoundationWall
    serializer_class = FoundationWallSerializer
    queryset = model.objects.all()
    permission_classes = (IsAuthenticated,)


class NestedAboveGradeWallViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    model = AboveGradeWall
    serializer_class = AboveGradeWallSerializer
    queryset = model.objects.all()
    permission_classes = (IsAuthenticated,)


class NestedRoofViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    model = Roof
    serializer_class = RoofSerializer
    queryset = model.objects.all()
    permission_classes = (IsAuthenticated,)


class NestedFrameFloorViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    model = FrameFloor
    serializer_class = FrameFloorSerializer
    queryset = model.objects.all()
    permission_classes = (IsAuthenticated,)


class NestedWindowViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    model = Window
    serializer_class = WindowSerializer
    queryset = model.objects.all()
    permission_classes = (IsAuthenticated,)


class NestedSlabViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    model = Slab
    serializer_class = SlabSerializer
    queryset = model.objects.all()
    permission_classes = (IsAuthenticated,)


class NestedSkylightViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    model = Skylight
    serializer_class = SkylightSerializer
    queryset = model.objects.all()
    permission_classes = (IsAuthenticated,)


class NestedRimJoistViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    model = RimJoist
    serializer_class = RimJoistSerializer
    queryset = model.objects.all()
    permission_classes = (IsAuthenticated,)


class NestedDoorViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    model = Door
    serializer_class = DoorSerializer
    queryset = model.objects.all()
    permission_classes = (IsAuthenticated,)


class NestedPhotovoltaicViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    model = Photovoltaic
    serializer_class = PhotovoltaicSerializer
    queryset = model.objects.all()
    permission_classes = (IsAuthenticated,)


class NestedAnalyticsViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    model = Analysis
    serializer_class = AnalysisSerializer
    queryset = model.objects.all()
    permission_classes = (IsAuthenticated,)


class NestedInfiltrationViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    model = Infiltration
    serializer_class = InfiltrationSerializer
    queryset = model.objects.all()
    permission_classes = (IsAuthenticated,)


class NestedLightsViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    model = Lights
    serializer_class = LightsSerializer
    queryset = model.objects.all()
    permission_classes = (IsAuthenticated,)


class NestedAppliancesViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    model = Appliances
    serializer_class = AppliancesSerializer
    queryset = model.objects.all()
    permission_classes = (IsAuthenticated,)


class NestedLocationViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    model = Location
    serializer_class = LocationSerializer
    queryset = model.objects.all()
    permission_classes = (IsAuthenticated,)


class NestedUtilityRateViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    model = UtilityRate
    serializer_class = UtilityRateSerializer
    queryset = model.objects.all()
    permission_classes = (IsAuthenticated,)
