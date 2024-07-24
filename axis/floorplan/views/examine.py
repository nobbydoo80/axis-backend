__author__ = "Michael Jeffrey"
__date__ = "1/15/16 4:05 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = ["Michael Jeffrey", "Artem Hruzd"]
import logging

from django.urls import reverse_lazy
from simulation.serializers.rem.blg import get_blg_simulation_from_floorplan
from simulation.serializers.simulation.base import SimulationSerializer

from axis import examine
from axis.annotation.machinery import annotations_machinery_factory
from ..api import (
    FloorplanViewSet,
    FloorplanRemrateViewSet,
    FloorplanEkotropeViewSet,
    FloorplanApprovalViewSet,
)
from ..forms import (
    FloorplanRemrateForm,
    FloorplanEkotropeForm,
    FloorplanApprovalForm,
)
from ..models import Floorplan


log = logging.getLogger(__name__)


def get_floorplan_annotations_machinery_class():
    NotesMachinery = annotations_machinery_factory(
        Floorplan,
        type_slug="note",
        **{
            # Use table-driven template stuff
            "template_set": "table",
            "regionset_template": None,
            "region_template": None,
            "detail_template": "examine/annotation/note_table_detail.html",
            "form_template": "examine/annotation/note_table_form.html",
            "visible_fields": ["content", "user", "created_on", "is_public"],
            "verbose_names": {
                "content": "Note",
                "user": "User",
                "created_on": "Date",
                "is_public": "Is Public",
            },
        },
    )
    return NotesMachinery


# Simulation input types for REM, Ekotrope
class FloorplanRemrateExamineMachinery(examine.ExamineMachinery):
    model = Floorplan
    form_class = FloorplanRemrateForm
    api_provider = FloorplanRemrateViewSet
    type_name = "floorplan_remrate"

    detail_template = "examine/floorplan/floorplan_remrate_detail.html"
    form_template = "examine/floorplan/floorplan_remrate_form.html"

    def can_delete_object(self, instance, user=None):
        # TODO: do we ever want to allow deletion?
        return False

    def can_edit_object(self, instance, user=None):
        if user.is_superuser:
            return True

        if instance.is_restricted:
            return False

        if user.company.company_type in ["rater", "provider"]:
            return True

        return False

    def get_region_dependencies(self):
        return {"floorplan": [{"field_name": "id", "serialize_as": "id"}]}

    def get_helpers(self, instance):
        helpers = super(FloorplanRemrateExamineMachinery, self).get_helpers(instance)
        helpers["can_download_xml"] = (
            instance.can_download_xml(self.context["request"].user) and not self.create_new
        )
        helpers["show_simulation_specifics"] = self.context["request"].user.is_superuser
        return helpers


class FloorplanEkotropeExamineMachinery(examine.ExamineMachinery):
    model = Floorplan
    form_class = FloorplanEkotropeForm
    api_provider = FloorplanEkotropeViewSet
    type_name = "floorplan_ekotrope"

    detail_template = "examine/floorplan/floorplan_ekotrope_detail.html"
    form_template = "examine/floorplan/floorplan_ekotrope_form.html"

    def can_delete_object(self, instance, user=None):
        # TODO: do we ever want to allow deletion?
        return False

    def can_edit_object(self, instance, user=None):
        if user.is_superuser:
            return True

        if user.company.company_type in ["rater", "provider"]:
            return hasattr(user, "ekotropeauthdetails")

        return False

    def get_region_dependencies(self):
        return {"floorplan": [{"field_name": "id", "serialize_as": "id"}]}

    def get_form_kwargs(self, instance):
        kwargs = super(FloorplanEkotropeExamineMachinery, self).get_form_kwargs(instance)
        kwargs["request"] = self.context["request"]
        return kwargs

    def get_helpers(self, instance):
        helpers = super(FloorplanEkotropeExamineMachinery, self).get_helpers(instance)
        helpers["show_simulation_specifics"] = self.context["request"].user.is_superuser
        return helpers


class FloorplanSystemsExamineMachinery(examine.ReadonlyMachinery):
    model = Floorplan
    type_name = "floorplan_systems"
    api_provider = FloorplanViewSet

    detail_template = "examine/floorplan/systems_detail.html"

    def get_default_instruction(self, instance):
        return None

    def _format_url_name(self, url_name, **kwargs):
        return url_name.format(model="floorplan")

    def get_region_dependencies(self):
        return {"floorplan": [{"field_name": "id", "serialize_as": "id"}]}


class FloorplanBLGExamineMachinery(examine.ReadonlyMachinery):
    model = Floorplan
    api_provider = FloorplanViewSet
    type_name = "floorplan_blg"

    detail_template = "examine/floorplan/floorplan_blg_detail.html"

    def serialize_object(self, instance: Floorplan) -> dict:
        simulation = get_blg_simulation_from_floorplan(instance)
        serializer = SimulationSerializer(instance=simulation)
        return serializer.data

    def _format_url_name(self, url_name, **kwargs):
        return url_name.format(model="floorplan")


class FloorplanApprovalStatusMachinery(examine.SingleObjectMachinery):
    model = Floorplan
    form_class = FloorplanApprovalForm
    type_name = "floorplan_approval"
    api_provider = FloorplanApprovalViewSet

    detail_template = "examine/floorplan/floorplan_reviewed_status_detail.html"
    form_template = "examine/floorplan/floorplan_reviewed_status_form.html"

    def can_edit_object(self, instance, user):
        return user.is_superuser or self.context.get("is_approval_entity")

    def can_delete_object(self, instance, user):
        return False
