import logging

from django.urls import reverse

from axis.examine.machinery import ExamineMachinery
from axis.floorplan.api import FloorplanViewSet
from axis.floorplan.forms import HomeStatusFloorplanForm
from axis.floorplan.models import Floorplan
from axis.home.models import EEPProgramHomeStatus

__author__ = "Artem Hruzd"
__date__ = "06-24-19 5:44 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class HomeStatusFloorplanExamineMachinery(ExamineMachinery):
    model = Floorplan
    form_class = HomeStatusFloorplanForm
    api_provider = FloorplanViewSet
    type_name = "floorplan"

    template_set = "panel"
    regionset_template = "examine/home/floorplan_regionset.html"
    region_template = "examine/home/floorplan_region.html"
    detail_template = "examine/home/floorplan_detail.html"
    form_template = "examine/home/floorplan_form.html"
    delete_confirmation_template = "examine/home/floorplan_delete_confirmation.html"

    delete_name = "Remove"

    def get_context(self):
        context = super(HomeStatusFloorplanExamineMachinery, self).get_context()
        context["home_status_id"] = "__home_status_id__"
        context["subdivision_id"] = "__subdivision_id__"
        return context

    def get_helpers(self, instance):
        helpers = super(HomeStatusFloorplanExamineMachinery, self).get_helpers(instance)

        # This is called when we initialize the helpers and not everytime.
        if hasattr(self.context["request"].user, "ekotropeauthdetails"):
            from axis.ekotrope.utils import stub_project_list

            # this desperately needs async
            stub_project_list(self.context["request"].user.ekotropeauthdetails)

        helpers["can_download_xml"] = (
            instance.can_download_xml(self.context["request"].user) and not self.create_new
        )
        return helpers

    def get_verbose_name(self, instance=None):
        return "Floorplan"

    def get_form_kwargs(self, instance):
        if self.create_new or not instance:  # When in create mode, the template handles stuff
            mode = None
        else:
            mode = instance.input_data_type
        return {
            "user": self.context["request"].user,
            "mode": mode,
        }

    def get_region_dependencies(self):
        return {
            "home_status": [
                {
                    "field_name": "id",
                    "serialize_as": "home_status_id",
                }
            ],
        }

    def get_relatedobjects_endpoint(self, instance):
        return None

    def can_delete_object(self, instance, user=None):
        return self.can_edit_object(instance, user)

    def get_delete_endpoint(self, instance):
        if not instance.pk:
            return None

        endpoint = "apiv2:home_status_floorplans-detail"

        # Figure out the "through" instance for the m2m
        home_status_id = self.context["home_status_id"]
        through_model_class = EEPProgramHomeStatus.floorplans.through
        through_instance = through_model_class.objects.filter(
            eepprogramhomestatus__id=home_status_id, floorplan=instance
        ).last()
        return reverse(endpoint, kwargs={"pk": through_instance.pk if through_instance else None})

    def get_default_actions(self, instance):
        """Adds the Ekotrope submission action."""
        actions = super(HomeStatusFloorplanExamineMachinery, self).get_default_actions(instance)
        if instance.remrate_data_file and instance.can_be_simulated(self.context["request"].user):
            actions.insert(
                -1, self.Action(name="Simulate", instruction="simulate", style="default")
            )
        return actions

    def get_edit_actions(self, instance):
        """Returns panel actions."""
        actions = super(HomeStatusFloorplanExamineMachinery, self).get_edit_actions(instance)
        # in case when we creating eep_program_home status
        # we should hide save button for floorplan, because we do not have
        # parent id to save it
        if "home_status_id" in self.context:
            if not self.context["home_status_id"]:
                for i, action in enumerate(actions):
                    if action["instruction"] == "save":
                        actions.pop(i)
        return actions
