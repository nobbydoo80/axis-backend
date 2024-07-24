"""views.py: Django """


import logging
import tempfile

from django.http import HttpResponse

from axis.core.mixins import AuthenticationMixin
from axis.core.views.generic import AxisDatatableView, AxisDetailView
from axis.customer_aps.reports import ECBSVGBuilder
from axis.floorplan.models import Floorplan
from axis.subdivision.models import Subdivision
from .datatables import SubdivisionReportDatatable

__author__ = "Steven Klass"
__date__ = "3/3/12 5:55 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


# FIXME: We've got some query count problems here, scaling with the number of companies that get
# their own columns in the table.  Too many lookups against subdivision.relationships.all()
class SubdivisionReportList(AuthenticationMixin, AxisDatatableView):
    permission_required = "subdivision.view_subdivision"
    template_name = "report/subdivision_report.html"
    datatable_class = SubdivisionReportDatatable

    show_add_button = False

    def get_queryset(self):
        return Subdivision.objects.filter_by_user(user=self.request.user, show_attached=True)

    def get_datatable_kwargs(self):
        kwargs = super(SubdivisionReportList, self).get_datatable_kwargs()
        if not self.request.user.company.is_eep_sponsor:
            kwargs["subdivision_ids"] = list(self.get_queryset().values_list("id", flat=True))
        return kwargs


class ECBReportView(AuthenticationMixin, AxisDetailView):
    permission_required = "subdivision.view_subdivision"

    pk_url_kwarg = "subdivision_id"
    template_name = "report/energy_cost_analysis.html"
    svg = False
    download = False  # only applies if svg is True

    show_edit_button = False
    show_delete_button = False

    def get(self, request, *args, **kwargs):
        if self.svg:
            return self.get_svg(request, *args, **kwargs)

        self.remdata, self.floorplans = self.get_data()

        return super(ECBReportView, self).get(request, *args, **kwargs)

    def get_svg(self, request, *args, **kwargs):
        remdata, floorplans = self.get_data()

        # Master data list.  First two slots are reserved for labels
        data = [[] for i in range(8)]
        for item in floorplans:
            data[0].append(item.name)
            data[1].append(str(item.square_footage))

        # This would be a lambda, but try..except is hard in there
        def clamp(value):
            try:
                return str(int(round(value, 0)))
            except:
                return ""

        # For each data item, round the graphed values and place them into the master list
        for item in remdata:
            if item and hasattr(item, "results") and item.results:
                results = item.results
                values = map(
                    clamp,
                    [
                        results.get_heating_and_cooling_total_cost(),
                        results.hot_water_cost,
                        results.lights_and_appliances_total_cost,
                        results.service_cost,
                        results.total_cost,
                        results.get_monthly_total_cost(),
                    ],
                )
                values = list(values)
            else:
                values = ["" for i in range(len(data[2:]))]
            # Drop each value into its spot in the master list
            for stack in data[2:]:
                stack.append(values.pop(0))

        # Generate the SVG
        filename = tempfile.NamedTemporaryFile()
        svgObject = ECBSVGBuilder(filename=filename, data=data)
        response = HttpResponse(content_type="image/svg+xml")
        response.write(svgObject.build())
        filename.close()

        if self.download:
            response["Content-Disposition"] = "attachment; filename=ecb.svg"
        return response

    def get_queryset(self):
        # FIXME: This wasn't limited by the previous function-based view
        return Subdivision.objects.all()

    def get_data(self):
        obj = self.get_object()
        floorplans = Floorplan.objects.filter(subdivision=obj, is_active=True)
        floorplans = list(floorplans.order_by("square_footage"))
        remdata = [f.remrate_target for f in floorplans]
        return remdata, floorplans

    def get_context_data(self, **kwargs):
        context = super(ECBReportView, self).get_context_data(**kwargs)
        obj = self.get_object()
        show_picture = obj.eep_programs.filter(owner__slug="aps").exists()
        context.update(
            {
                "floorplans": self.floorplans,
                "remdata": self.remdata,
                "show_energy_star_picture": show_picture,
            }
        )
        return context
