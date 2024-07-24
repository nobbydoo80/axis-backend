"""views.py: Django customer_appraisal_institute"""


import logging
import os

from datatableview import helpers
from django.http import HttpResponse, Http404
from django.urls import reverse_lazy
from django.views.generic import FormView

from axis.core.mixins import AuthenticationMixin
from axis.core.views.generic import LegacyAxisDatatableView
from axis.home.models import EEPProgramHomeStatus
from .forms import GreenEnergyEfficientAddendumForm
from .geea_data import GEEAData, flatten_filled_values_in_pdf

__author__ = "Steven Klass"
__date__ = "6/2/13 9:03 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class GreenEnergyEfficientAddendumHomesListView(AuthenticationMixin, LegacyAxisDatatableView):
    """This will simply provide a list view for the Program Home Status"""

    permission_required = "customer_appraisal_institute.view_geeadata"
    template_name = "home/eepprogramhomestatus_list.html"

    datatable_options = {
        "columns": [
            ("Address", ["home__lot_number", "home__street_line1", "home__street_line2"]),
            ("Subdivision", "home__subdivision__name"),
            ("Floorplan", "floorplan__name"),
            ("Program", "eep_program__name"),
            ("State", "state"),
        ],
    }

    def get_queryset(self):
        queryset = EEPProgramHomeStatus.objects.filter_by_user(user=self.request.user)
        queryset = queryset.filter(
            floorplan__remrate_target__isnull=False, certification_date__isnull=False
        ).select_related("floorplan", "eep_program", "home__subdivision__community")
        return queryset

    def get_column_Address_data(self, obj, *args, **kwargs):
        designator = ""
        if obj.home.address_override:
            designator = "▵"
        elif obj.home.confirmed_address:
            designator = "◦"
        name = "{}{}{}".format(
            obj.home.street_line1,
            ", {}".format(obj.home.street_line2) if obj.home.street_line2 else "",
            " {}".format(designator) if designator else "",
        )
        return helpers.link_to_model(obj.home, text=name)

    def get_column_Subdivision_data(self, obj, *args, **kwargs):
        subdivision = obj.home.subdivision
        name = "{}{}{}".format(
            subdivision.name,
            " at {}".format(subdivision.community) if subdivision.community else "",
            " ({})".format(subdivision.builder_name) if subdivision.builder_name else "",
        )
        return helpers.link_to_model(obj.home.subdivision, text=name)

    def get_column_Floorplan_data(self, obj, *args, **kwargs):
        return helpers.link_to_model(obj.floorplan, text=obj.floorplan.name)

    def get_column_Program_data(self, obj, *args, **kwargs):
        return helpers.link_to_model(obj.eep_program)

    def get_column_State_data(self, obj, *args, **kwargs):
        return obj.state_description


class GreenEnergyEfficientAddendumView(GreenEnergyEfficientAddendumHomesListView, FormView):
    """Inherits the datatble from the above List view, but adds some form workflow."""

    permission_required = None
    form_class = GreenEnergyEfficientAddendumForm
    template_name = "customer_appraisal_institute/green_energy_efficient_addendum.html"
    success_url = reverse_lazy("home")

    def has_permission(self):
        return True

    def get(self, request, *args, **kwargs):
        # Use this in conjunction with the url kwarg for 'home_status' (instead of a form submission)
        if "home_status" not in kwargs:
            raise Http404
        try:
            home_status = EEPProgramHomeStatus.objects.get(id=kwargs["home_status"])
        except EEPProgramHomeStatus.DoesNotExist:
            raise Http404
        return self.generate_report(home_status)

    def generate_report(self, home_status):
        pdf_form_file = os.path.abspath(
            os.path.dirname(__file__) + "/sources/ResidentialGreenandEnergyEfficientAddendum.pdf"
        )
        assert os.path.exists(pdf_form_file), "File does not exist {}".format(pdf_form_file)

        # from axis.customer_appraisal_institute import GEEA_FAKE_DATA
        data = GEEAData(self.request.user, home_status).data
        pdf_stream = flatten_filled_values_in_pdf(pdf_form_file, data)

        attachment_name = "G&EEA_{}.pdf".format(home_status.home.street_line1)
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = "attachement; filename={}".format(attachment_name)
        response.write(pdf_stream.getvalue())

        return response

    def get_form_kwargs(self):
        kwargs = super(GreenEnergyEfficientAddendumView, self).get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_invalid(self, form):
        log.warning(form.errors)
        return super(GreenEnergyEfficientAddendumView, self).form_invalid(form)

    def form_valid(self, form):
        """Generates the PDF document for the submitted ID list."""
        home_stats = EEPProgramHomeStatus.objects.filter(id__in=form.cleaned_data["homes"])
        return self.generate_report(home_stats[0])

    def get_context_data(self, **kwargs):
        # This is a necessary evil born from the weird inheritance structure of this view.
        # The get() method of a ListView normally adds object_list to the context kwargs, but the
        # FormView.post() doesn't do such a thing, and so this method's chain of super() calls
        # results in the ListView getting confused about why the 'object_list' isn't there.
        if "object_list" not in kwargs:
            self.object_list = kwargs["object_list"] = self.get_queryset()
        context = super(GreenEnergyEfficientAddendumView, self).get_context_data(**kwargs)
        context["form"] = self.get_form(self.form_class)
        return context
