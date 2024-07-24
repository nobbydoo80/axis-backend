"""views.py: Django subdivision"""


import logging

from axis.core.mixins import AuthenticationMixin
from axis.core.views.generic import AxisDatatableView
from axis.relationship.models import Relationship
from ..models import Subdivision
from .. import datatables

__author__ = "Steven Klass"
__date__ = "3/5/12 11:25 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class SubdivisionListView(AuthenticationMixin, AxisDatatableView):
    """CBV for listing Subdivisions"""

    permission_required = "subdivision.view_subdivision"
    datatable_class = datatables.SubdivisionListDatatable

    prefetch_related = [
        "relationships",
        "relationships__company",
    ]

    select_related = [
        "builder_org",
        "community",
        "city__county",
    ]

    def get_queryset(self):
        """Narrow this based on your company"""
        queryset = Subdivision.objects.filter_by_user(user=self.request.user, show_attached=True)
        queryset = (
            queryset.prefetch_related(*self.prefetch_related)
            .select_related(*self.select_related)
            .distinct()
        )
        return queryset

    def get_datatable_kwargs(self, **kwargs):
        """Updates kwargs"""
        kwargs = super(SubdivisionListView, self).get_datatable_kwargs(**kwargs)

        if self.request.headers.get("x-requested-with") == "XMLHttpRequest" and not hasattr(
            self, "_company_relationships"
        ):
            self._company_relationships = Relationship.objects.filter_companies_for_company(
                self.request.company
            ).select_related("company")
            self._company_relationship_ids = self._company_relationships.values_list(
                "object_id", flat=True
            )

            attached = Relationship.objects.filter_subdivisions_for_company(
                self.request.company, show_attached=True
            )
            self._attached = list(
                attached.filter(is_attached=True, is_owned=False).values_list(
                    "object_id", flat=True
                )
            )

            kwargs["hints"] = {
                "company_relationships": self._company_relationships,
                "company_relationship_ids": self._company_relationship_ids,
                "attached": self._attached,
            }

        return kwargs

    def get_datatable(self, **kwargs):
        """Gets an instance of Datatable and adds/delete columns"""
        datatable = super(SubdivisionListView, self).get_datatable()

        if not self.request.user.has_perm("subdivision.change_subdivision"):
            del datatable.columns["associations"]

        # Hide data columns from the view depending on the user's company type.
        # This is slightly more explicit than adding in columns dynamically.
        company_type = self.request.company.company_type

        if company_type != "qa":
            del datatable.columns["qa"]

        if company_type == "builder":
            del datatable.columns["builder"]
        elif company_type in ["rater", "provider"]:
            del datatable.columns["rater"]

        return datatable

    def get_context_data(self, **kwargs):
        context = super(SubdivisionListView, self).get_context_data(**kwargs)
        context["verbose_name_plural"] = "Subdivisions/MF Developments"
        return context
