"""api.py: Floorplan"""

import logging

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

from axis.ekotrope.models import HousePlan
from axis.examine.api.restframework import ExamineViewSetAPIMixin
from axis.relationship.utils import create_or_update_spanning_relationships
from axis.remrate_data.models import Simulation
from .models import Floorplan
from .serializers import (
    FloorplanSerializer,
    FloorplanRemrateSerializer,
    FloorplanEkotropeSerializer,
    FloorplanApprovalSerializer,
)
from .utils import clear_approval_and_request_new

__author__ = "Autumn Valenta"
__date__ = "5/27/13 10:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]

log = logging.getLogger(__name__)


class FloorplanViewSet(ExamineViewSetAPIMixin, viewsets.ModelViewSet):
    model = Floorplan
    queryset = model.objects.all()
    serializer_class = FloorplanSerializer

    def filter_queryset(self, queryset):
        return queryset.filter_by_user(self.request.user, show_attached=True)

    @action(detail=False)
    def rem_data_fields(self, request):
        """Fetches the REM data values that are used for auto-populating Floorplan fields."""

        request_data = self.request.query_params
        remrate_target_id = request_data.get("id")

        if not remrate_target_id:
            return Response({})

        queryset = Simulation.objects.all()  # filter_by_user(self.request.user)
        try:
            remrate_target = queryset.get(id=remrate_target_id)
        except Simulation.DoesNotExist:
            return Response({})

        hvacs = remrate_target.airconditioner_set.all()
        try:
            vents = [remrate_target.infiltration.get_ventilation_system()]
        except ObjectDoesNotExist:
            vents = []

        unique_name = Floorplan.objects.find_unique_floorplan_name(
            remrate_target.building_name, self.request.user.company
        )

        return Response(
            {
                "hvac_systems": hvacs.count(),
                "ventilation_systems": len(vents),
                "name": unique_name,
                "number": remrate_target.id,
                "square_footage": remrate_target.buildinginfo.conditioned_area,
            }
        )

    @action(detail=False)
    def ekotrope_fields(self, request):
        """Fetches the REM data values that are used for auto-populating Floorplan fields."""

        request_data = self.request.query_params
        houseplan_id = request_data.get("id")

        if not houseplan_id:
            return Response({})

        queryset = HousePlan.objects.filter_by_user(self.request.user)
        try:
            houseplan = queryset.get(id=houseplan_id)
        except HousePlan.DoesNotExist:
            return Response({})

        # If the item is newly arrived in Axis and isn't fully imported, this might not be
        # available.
        from axis.ekotrope.utils import import_houseplan
        from axis.ekotrope.models import EkotropeAuthDetails

        project = houseplan.project
        auth_details = EkotropeAuthDetails.objects.filter(user__company=project.company).first()
        houseplan = import_houseplan(auth_details, houseplan.project, houseplan_id, houseplan.name)

        project = houseplan.project
        unique_name = Floorplan.objects.find_unique_floorplan_name(
            name=project.data["community"], company=self.request.user.company
        )

        return Response(
            {
                "name": unique_name,
                "number": houseplan.id,
                "square_footage": houseplan.data["thermalEnvelope"]["summary"]["conditionedArea"],
            }
        )

    def get_examine_machinery_classes(self):
        from axis.home.views.machineries import (
            ActiveFloorplanExamineMachinery,
            HomeStatusFloorplanExamineMachinery,
        )
        from .views.examine import (
            FloorplanApprovalStatusMachinery,
            FloorplanSystemsExamineMachinery,
            FloorplanBLGExamineMachinery,
        )

        return {
            None: HomeStatusFloorplanExamineMachinery,
            "FloorplanSystemsExamineMachinery": FloorplanSystemsExamineMachinery,
            "FloorplanBLGExamineMachinery": FloorplanBLGExamineMachinery,
            "HomeStatusFloorplanExamineMachinery": HomeStatusFloorplanExamineMachinery,
            "ActiveFloorplanExamineMachinery": ActiveFloorplanExamineMachinery,
            "FloorplanApprovalStatusMachinery": FloorplanApprovalStatusMachinery,
        }

    def get_machinery(self, *args, **kwargs):
        home_status_id = self.request.query_params.get("home_status_id") or self.request.data.get(
            "home_status_id"
        )

        kwargs["context"] = {
            "home_status_id": home_status_id,
        }
        return super(FloorplanViewSet, self).get_machinery(*args, **kwargs)

    def _determine_homestatus(self):
        from axis.home.models import EEPProgramHomeStatus

        if "home_status_id" in self.request.data:
            homestatus_id = self.request.data["home_status_id"]
        else:
            homestatus_id = None

        if homestatus_id:
            homestatuses = EEPProgramHomeStatus.objects.filter_by_user(self.request.user)
            return homestatuses.get(pk=homestatus_id)
        return None

    def perform_create(self, serializer):
        self._created = True
        self._save(serializer, owner=self.request.company)

    def perform_update(self, serializer):
        self._created = False
        self._save(serializer)

    def _save(self, serializer, **save_kwargs):  # noqa: C901
        # pre-save

        obj = serializer.instance
        pk = None
        if obj:
            pk = obj.pk
            save_kwargs["owner"] = obj.owner

        # Make sure this is valid before we save, but don't use it until post-save
        self.homestatus = self._determine_homestatus()
        _form = None
        if self.request.data.get("remrate_data_file_raw"):
            form_class = self.get_examine_machinery_class().form_class
            _form = form_class(data=self.request.data, instance=obj, raw_file_only=True)
            _form._owner = self.request.user.company
            if not _form.is_valid():
                errors = _form.errors
                if "remrate_data_file_raw" in errors:
                    errors["remrate_data_file"] = errors.pop("remrate_data_file_raw")
                raise ValidationError(errors)  # bad request

        existing = self.filter_queryset(self.queryset).filter_for_uniqueness(
            name=serializer.validated_data["name"],
            remrate_target=serializer.validated_data.get("remrate_target"),
            ekotrope_houseplan=serializer.validated_data.get("ekotrope_houseplan"),
            simulation=serializer.validated_data.get("simulation"),
            owner=obj.owner if obj else self.request.user.company,
            id=obj.pk if obj else None,
        )
        if existing.exists():
            raise ValidationError(
                {
                    "non_field_errors": [
                        "A floorplan with this name is already using this Simulation Data"
                    ]
                }
            )

        save_kwargs["home_status"] = self.homestatus

        # save
        obj = serializer.save(**save_kwargs)

        # post-save
        if _form:
            # Rebuild form from corrected instance object.  We know it will be valid, so move
            # immediately to the save process.
            _form = form_class(data=self.request.data, instance=obj, raw_file_only=True)
            _form._owner = self.request.user.company
            _form.is_valid()
            _form.save()

        if self.homestatus:
            if self._created:
                self.homestatus.floorplans.add(obj)

            self.homestatus.floorplan = self.homestatus.calculate_active_floorplan()
            self.homestatus.save()

            from axis.home.tasks import update_home_states

            update_home_states(
                eepprogramhomestatus_id=self.homestatus.id, user_id=self.request.user.id
            )

            self.homestatus.validate_references()

            if self.homestatus.eep_program.require_floorplan_approval:
                # Verify that the floorplan in question is related to the approval entity
                # FIXME: Simplifying the logic from previous versions makes it appear that this
                # check is entirely redundant; if the floorplan in on the homestatus, then the
                # relationship will always exist on the floorplan.
                approval_entity = self.homestatus.eep_program.owner
                if Floorplan.objects.filter_by_company(approval_entity).filter(id=obj.id).exists():
                    # Only want to clear if the simulation data changed
                    if pk is None:  # Floorplan just now created
                        changed_fields = [
                            field
                            for field in ["remrate_data_file", "remrate_target"]
                            if getattr(obj, field)
                        ]
                    else:
                        base_obj = self.model.objects.get(id=obj.id)
                        changed_fields = [
                            field
                            for field in ["remrate_data_file", "remrate_target"]
                            if getattr(obj, field) != getattr(base_obj, field)
                        ]
                    if changed_fields:
                        clear_approval_and_request_new(
                            obj,
                            self.homestatus,
                            approval_entity,
                            self.request.user,
                            changed_fields=changed_fields,
                        )
        if pk:
            base_obj = self.model.objects.get(id=obj.id)
            changed_fields = [
                field
                for field in ["remrate_data_file", "remrate_target"]
                if getattr(obj, field) != getattr(base_obj, field)
            ]
            if changed_fields:
                if "remrate_target" in changed_fields and base_obj.simulation:
                    simulation_seed = obj.remrate_target.simulation_seeds.get()
                    try:
                        obj.simulation = simulation_seed.simulation
                    except ObjectDoesNotExist:
                        from simulation.tasks import convert_seed

                        convert_seed.delay(simulation_seed.id)
                        obj.simulation = None
        create_or_update_spanning_relationships(self.request.user.company, obj)
        return obj


class FloorplanRemrateViewSet(ExamineViewSetAPIMixin, viewsets.ModelViewSet):
    model = Floorplan
    queryset = model.objects.all()
    serializer_class = FloorplanRemrateSerializer

    @action(detail=True, methods=["get"])
    def diff(self, request, *args, **kwargs):
        from simulation.serializers.rem.blg import get_blg_simulation_from_floorplan
        from simulation.serializers.simulation.compare import SimulationDiffSerializer

        obj = self.get_object()
        try:
            blg_instance = get_blg_simulation_from_floorplan(obj)
        except (ValidationError, ValueError, IOError, OSError) as err:
            return Response(
                {"error": f"BLG File does not exist or could not be parsed - {err}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        diff_serializer = SimulationDiffSerializer(
            data={"sim_1": obj.simulation.id, "sim_2": blg_instance.id},
            context={"compare_remxml": True},
        )
        if not diff_serializer.is_valid(raise_exception=False):
            return Response(
                {"error": "Invalid Serializer - Bad Data", "errors": diff_serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(diff_serializer.data, status=status.HTTP_200_OK)

    def get_examine_machinery_class(self, raise_exception=True):
        from .views.examine import FloorplanRemrateExamineMachinery

        return FloorplanRemrateExamineMachinery

    def perform_update(self, serializer):
        obj = serializer.instance

        form_class = self.get_examine_machinery_class().form_class
        _form = form_class(data=self.request.data, instance=obj)
        _form._owner = self.request.user.company

        if not _form.is_valid():
            errors = _form.errors
            if "remrate_data_file_raw" in errors:
                errors["remrate_data_file"] = errors.pop("remrate_data_file_raw")
            raise ValidationError(errors)

        obj = serializer.save()
        _form = form_class(data=self.request.data, instance=obj)
        _form._owner = self.request.user.company
        _form.is_valid()
        _form.save()

        return obj


class FloorplanEkotropeViewSet(ExamineViewSetAPIMixin, viewsets.ModelViewSet):
    model = Floorplan
    queryset = model.objects.all()
    serializer_class = FloorplanEkotropeSerializer

    def get_examine_machinery_class(self, raise_exception=True):
        from .views.examine import FloorplanEkotropeExamineMachinery

        return FloorplanEkotropeExamineMachinery


class FloorplanApprovalViewSet(ExamineViewSetAPIMixin, viewsets.ModelViewSet):
    model = Floorplan  # Targets a floorplan to update all approvals on
    queryset = model.objects.all()
    serializer_class = FloorplanApprovalSerializer

    def get_examine_machinery_class(self, raise_exception=True):
        from .views.examine import FloorplanApprovalStatusMachinery

        return FloorplanApprovalStatusMachinery
