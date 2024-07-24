__author__ = "Steven Klass"
__date__ = "3/3/12 5:38 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = ["Steven Klass", "Artem Hruzd"]

import logging

import datatableview.helpers
from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.utils import formats

from axis.core.mixins import AuthenticationMixin
from axis.core.views.generic import (
    LegacyAxisDatatableView,
    AxisDetailView,
)
from axis.ekotrope.models import HousePlan
from axis.floorplan.utils import (
    serialize_floorplan_input_rem_rate,
    serialize_floorplan_input_ekotrope,
)
from axis.home.models import Home
from axis.remrate_data.models import Simulation, DESIGN_MODELS

log = logging.getLogger(__name__)

frontend_app = apps.get_app_config("frontend")


class FloorplanInputMixin(AuthenticationMixin):
    """Accepts a 'mode' kwarg when put into a urls list, and uses the matching input model."""

    mode = None  # urls 'as_view()' must specify 'remrate' or 'ekotrope'
    show_add_button = False
    show_edit_button = False

    def get_model(self):
        model = None
        if self.mode == "remrate":
            model = Simulation
        elif self.mode == "ekotrope":
            model = HousePlan

        if model:
            self.model = model
            return self.model
        raise ValueError("Unrecognized view mode set: %r" % self.mode)

    def get_queryset(self, **kwargs):
        self.model = self.get_model()
        return self.model.objects.filter_by_user(user=self.request.user, **kwargs)

    def get_object(self):
        queryset = self.get_queryset()
        try:
            obj = queryset.get(pk=self.kwargs["pk"])
        except self.model.DoesNotExist:
            raise Http404()
        return obj


class FloorplanInputListView(FloorplanInputMixin, LegacyAxisDatatableView):
    permission_required = "remrate_data.view_simulation"

    def get_queryset(self, **kwargs):
        if self.mode == "remrate":
            kwargs["export_type__in"] = [1] + DESIGN_MODELS
        queryset = super(FloorplanInputListView, self).get_queryset(**kwargs)
        if self.mode == "remrate":
            queryset = queryset.order_by("-simulation_date")
        return queryset

    def get_datatable_options(self):
        # HEY LISTEN!  We upgraded datatables to 1.0 so we should use DT classes.
        if self.mode == "remrate":
            datatable_options = {
                "columns": [
                    ("Name", "building__project__name"),
                    ("Address", "building__project__property_address"),
                    ("Plan/Model", "building__project__builder_model"),
                    ("Community/Develop", "building__project__builder_development"),
                    ("Builder", "building__project__builder_name"),
                    ("Rating Number", "rating_number"),
                    ("BLG File", "building__filename"),
                    ("Upload", "building__created_on"),
                ],
            }
        elif self.mode == "ekotrope":
            datatable_options = {
                "columns": [
                    ("Name", "name"),
                    (
                        "Address",
                        ["data", "project__data"],
                        lambda obj, **kwargs: obj.project.data.get("location", {}).get(
                            "streetAddress", "-"
                        ),
                    ),
                    (
                        "Plan/Model",
                        ["data", "project__data"],
                        lambda obj, **kwargs: obj.project.data.get("model", "-"),
                    ),
                    (
                        "Community/Develop",
                        ["data", "project__data"],
                        lambda obj, **kwargs: obj.project.data.get("community", "-"),
                    ),
                    (
                        "Builder",
                        ["data", "project__data"],
                        lambda obj, **kwargs: obj.project.data.get("builder", "-"),
                    ),
                    ("Ekotrope ID", "id"),
                    (
                        "Import Date",
                        ["created_date"],
                        datatableview.helpers.format_date("%m/%d/%Y"),
                    ),
                ],
            }
        if self.request.user.is_superuser:
            datatable_options["columns"].append(("Import Error", "import_failed"))
        return datatable_options

    def get_column_Name_data(self, obj, *args, **kwargs):
        try:
            return datatableview.helpers.link_to_model(obj, text=kwargs["default_value"])
        except Simulation.DoesNotExist:
            log.warning("Unable to find building for simulation ID %s", obj.id)
            return "-"

    def get_column_Upload_data(self, obj, *args, **kwargs):
        try:
            tz = self.request.user.timezone_preference
            dts = obj.building.created_on.astimezone(tz)
            return formats.date_format(dts, "SHORT_DATETIME_FORMAT")
        except ObjectDoesNotExist:
            return "-"

    def get_column_Import_Error_data(self, obj, *args, **kwargs):
        failure = False
        if obj.get_validation_errors():
            failure = True
        return "Yes" if failure else "-"


class FloorplanInputDetailView(FloorplanInputMixin, AxisDetailView):
    permission_required = "floorplan.view_floorplan"

    def get_context_data(self, **kwargs):
        context = super(FloorplanInputDetailView, self).get_context_data(**kwargs)
        context["summary"] = self.get_summary_data(self.object)

        try:
            context["errors"] = self.object.get_validation_errors()
        except AttributeError:
            context["errors"] = []

        try:
            h_ids = self.object.floorplan.homestatuses.all().values_list("home_id", flat=True)
            context["homes"] = Home.objects.filter_by_user(user=self.request.user).filter(
                id__in=list(h_ids)
            )
        except ObjectDoesNotExist:
            pass

        return context

    def get_summary_data(self, obj):
        # If I were a better man, I'd have made serializers out of these, but it so much work and
        # I'm losing my mind.
        if self.mode == "remrate":
            serializer_f = serialize_floorplan_input_rem_rate
        elif self.mode == "ekotrope":
            serializer_f = serialize_floorplan_input_ekotrope
        return serializer_f(obj)
