"""api.py: Django """


import logging

from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.http import HttpResponse
from django.urls import reverse
from rest_framework import serializers, viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_403_FORBIDDEN,
)

from axis.company.models import Company
from axis.home.models import EEPProgramHomeStatus
from axis.remrate_data.models import Simulation as RemSimulation

from simulation.enumerations import Orientation
from simulation.models import Simulation
from simulation.serializers.hpxml import HesHpxmlSimulationSerializer, EventType, Transaction

from .models import HESSimulationStatus, HESCredentials
from .functions import trigger_generation_task_for_home_status

__author__ = "Steven K"
__date__ = "11/12/2019 09:03"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

log = logging.getLogger(__name__)
app = apps.get_app_config("hes")


class HESPerms(BasePermission):
    """Base Perms for HES"""

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.user.is_superuser or view.action is None:
            return True

        if view.action in ["list", "retrieve"]:
            return "hes.view_hessimulationstatus" in request.user.get_all_permissions()

        if view.action in ["create", "generate", "verify"]:
            return "hes.add_hessimulationstatus" in request.user.get_all_permissions()

        if view.action in ["update", "partial_update"]:
            return "hes.change_hessimulationstatus" in request.user.get_all_permissions()

        if view.action in ["destroy", "partial_update"]:
            return "hes.delete_hessimulationstatus" in request.user.get_all_permissions()

        return False


class HESSimulationStatusSerializer(serializers.ModelSerializer):
    company = serializers.PrimaryKeyRelatedField(
        queryset=Company.objects.all(), label="Owner", required=False
    )

    home_status = serializers.PrimaryKeyRelatedField(
        queryset=EEPProgramHomeStatus.objects.all(), label="Project", required=False
    )

    rem_simulation = serializers.PrimaryKeyRelatedField(
        queryset=RemSimulation.objects.all(), label="RemSimulation", required=False
    )

    simulation = serializers.PrimaryKeyRelatedField(
        queryset=Simulation.objects.all(), label="Simulation", required=True
    )

    simulation_errors = serializers.SerializerMethodField(read_only=True)
    report_download_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = HESSimulationStatus
        fields = (
            "pk",
            "company",
            "home_status",
            "rem_simulation",
            "simulation_errors",
            "report_download_url",
        )

    def get_report_download_url(self, obj):
        """Get us a Download Report download url"""
        if obj.hpxml and obj.worst_case_simulation:
            url = reverse("apiv2:hes-report", kwargs={"pk": obj.pk})
            return url


class HESSimulationStatusViewSet(viewsets.ModelViewSet):
    """This enables HES Score Generation and status"""

    model = HESSimulationStatus
    serializer_class = HESSimulationStatusSerializer
    permission_classes = (HESPerms,)

    def get_queryset(self):
        return self.model.objects.filter_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        _validate_user_credentials(request)
        return super(HESSimulationStatusViewSet, self).create(request, *args, **kwargs)

    def perform_create(self, serializer):
        if "company" not in serializer.validated_data:
            return serializer.save(company=self.request.user.company)
        return serializer.save()

    @action(detail=False, methods=["post"])
    def generate(self, request):
        """
        Trigger the generation of a Home Energy Score
        Request parameters:
          - home_status_id: Database ID of the EEPProgramHomeStatus for which to generate an HEScore
          - external_id: The value to be passed to the external_id field of the Home Energy Score request;
                         this is a custom field that we can put any value we like into
          - orientation: The orientation of the home. If no value is passed, the home status's orientation
                         annotation will be used. If no orientation is available, four orientations will
                         be simulated and the worst case used.
        """
        request_data = {k: v for k, v in request.data.items()}

        home_status_id = request_data.get("home_status_id")
        if home_status_id is None:
            return Response(
                data={"error": "Missing parameter 'home_status_id'"}, status=HTTP_400_BAD_REQUEST
            )

        try:
            home_status = EEPProgramHomeStatus.objects.get(id=home_status_id)
        except EEPProgramHomeStatus.DoesNotExist:
            return Response(
                data={"error": f"No home status found with ID '{home_status_id}'"},
                status=HTTP_404_NOT_FOUND,
            )

        hes_api_credentials = _get_hes_api_credentials(request, home_status)
        if hes_api_credentials is None:
            return Response(data={"error": "Missing HES API Credentials"}, status=500)

        try:
            task, hes_sim_status, is_sim_status_new = trigger_generation_task_for_home_status(
                home_status=home_status,
                hes_api_credentials=hes_api_credentials,
                external_id=request_data.get("external_id"),
                orientation=request_data.get("orientation"),
            )
        except ValueError as err:
            return Response(data={"error": f"{err}"}, status=500)

        data = {
            "pk": hes_sim_status.pk,
            "state": hes_sim_status.status,
            "status": f"Running SimulationStatus {hes_sim_status.id} with task {task.id}",
        }
        return Response(data, status=HTTP_201_CREATED if is_sim_status_new else HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path=r"hpxml/(?P<sim_id>\w+)")
    def hpxml(self, request: Request, sim_id: int) -> HttpResponse:
        """
        Download the HPXML representation of the home that we would submit to Home Energy Score.
        This is a feature for developers, meant to aid in diagnosing errors
        Request parameters:
          - sim_id: Database ID of the Simulation for which to generate the HPXML
        """
        try:
            is_superuser = request.user.is_superuser
        except AttributeError:
            is_superuser = False

        if not is_superuser:
            return Response("This is a developer resource", status=HTTP_403_FORBIDDEN)

        try:
            sim = Simulation.objects.get(id=sim_id)
        except Simulation.DoesNotExist:
            return Response(f"No Simulation with ID {sim_id} exists", status=HTTP_404_NOT_FOUND)

        # For the sake of simplicity, we don't bother getting the orientation from annotations,
        # and we don't get the address from the home. Neither of these are generally pertinent
        # to the question of whether the HPXML is valid and correct, so we don't really need
        # them for this function's current use case.
        hpxml = HesHpxmlSimulationSerializer(
            instance=sim,
            orientation=Orientation.NORTH,
            event_type=EventType.PRECONSTRUCTION,
            transaction=Transaction.CREATE,
            external_id="Test HPXML generated by the hpxml API method",
        ).hpxml

        response = HttpResponse(hpxml)
        response["Content-Disposition"] = f"attachment; filename={sim_id}.hpxml.xml"
        return response

    @action(detail=True, methods=["get"])
    def report(self):
        """Serve the Home Energy Score label PDF file"""
        object = self.get_object()

        if not object.worst_case_simulation:
            return HttpResponse("Not found", status=status.HTTP_204_NO_CONTENT)
        document = object.worst_case_simulation.customer_documents.filter(type="document").first()
        if document is None:
            return HttpResponse("Not found", status=status.HTTP_204_NO_CONTENT)

        filename = object.hpxml.external_id if object.hpxml.external_id else None
        if filename is None:
            if object.home_status and object.home_status.home:
                filename = object.home_status.home.pk
            else:
                filename = object.rem_simulation.pk

        response = HttpResponse(document, content_type="application/pdf")
        response["Content-Disposition"] = "attachment; filename=%s.pdf" % filename
        return response


def _get_hes_api_credentials(request, home_status: EEPProgramHomeStatus) -> HESCredentials | None:
    """Try getting credentials out of the current user. If none are found there, look for credentials
    linked to the company the home status belongs to."""
    try:
        hes_api_credentials = _validate_user_credentials(request)
    except ValidationError:
        hes_api_credentials = HESCredentials.objects.filter(company=home_status.company)
        hes_api_credentials = hes_api_credentials.first()

    return hes_api_credentials


def _validate_user_credentials(request):
    try:
        return request.user.hes_credentials
    except ObjectDoesNotExist:
        raise ValidationError("Missing HES Credentials - update your user profile")
