"""legacy_views.py: Django customer_aps"""


import logging

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.detail import DetailView

import datatableview.helpers

from axis.customer_aps.models import LegacyAPSBuilder, LegacyAPSSubdivision, LegacyAPSHome
from axis.core.views.views import AuthenticationMixin
from axis.core.views.generic import LegacyAxisDatatableView, AxisDetailView, AxisDetailMixin

__author__ = "Steven Klass"
__date__ = "4/25/12 8:21 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class APSLegacyBuilderListView(AuthenticationMixin, LegacyAxisDatatableView):
    permission_required = "customer_aps.view_legacyapsbuilder"
    datatable_options = {
        "columns": [
            ("Name", ["builder__name"], datatableview.helpers.link_to_model),
            (
                "Builder ID",
                ["aps_id"],
            ),
            (
                "City",
                ["mail_city"],
            ),
            (
                "State",
                ["mail_state"],
            ),
            "phone",
        ]
    }

    show_add_button = False

    def get_queryset(self):
        return LegacyAPSBuilder.objects.all()

    def get_column_Builder_ID_data(self, obj, *args, **kwargs):
        return obj.aps_id

    def get_column_City_data(self, obj, *args, **kwargs):
        return obj.mail_city

    def get_column_State_data(self, obj, *args, **kwargs):
        return obj.mail_state


class APSLegacyBuilderDetailView(AuthenticationMixin, AxisDetailView):
    """Detail View"""

    permission_required = "customer_aps.view_legacyapsbuilder"
    show_edit_button = False
    show_delete_button = False
    model = LegacyAPSBuilder


class APSLegacySubdivisionListView(AuthenticationMixin, LegacyAxisDatatableView):
    permission_required = "customer_aps.view_legacyapssubdivision"
    datatable_options = {
        "columns": [
            ("Name", ["sub"], datatableview.helpers.link_to_model),
            (
                "Subdivision ID",
                ["aps_id"],
            ),
            (
                "City",
                ["sub_loc_city"],
            ),
            (
                "State",
                ["sub_loc_zip"],
            ),
            (
                "Community",
                ["mstr_plan"],
            ),
        ]
    }

    show_add_button = False

    def get_queryset(self):
        return LegacyAPSSubdivision.objects.all()

    def get_column_Subdivision_Id_data(self, obj, *args, **kwargs):
        return obj.aps_id

    def get_column_City_data(self, obj, *args, **kwargs):
        return obj.sub_loc_city

    def get_column_State_data(self, obj, *args, **kwargs):
        return obj.sub_loc_zip

    def get_column_Community_data(self, obj, *args, **kwargs):
        return obj.mstr_plan


class APSLegacySubdivisionDetailView(AuthenticationMixin, AxisDetailView):
    show_edit_button = False
    show_delete_button = False
    model = LegacyAPSSubdivision
    permission_required = "customer_aps.view_legacyapshome"
    template_name = "customer_aps/legacyapssubdivision_detail.html"


class APSLegacyHomeListView(AuthenticationMixin, LegacyAxisDatatableView):
    permission_required = "customer_aps.view_legacyapshome"
    datatable_options = {
        "columns": [
            ("Lot Number", ["lot_no"], datatableview.helpers.link_to_model),
            (
                "Address",
                ["addr_no", "addr_dir", "addr_name", "addr_sufx"],
            ),
            ("Site ID", ["aps_id"], "get_column_Site_Id_data"),
            (
                "City",
                ["lt_city"],
            ),
            (
                "ZIP Code",
                ["lt_zip"],
            ),
            (
                "Subdivision",
                ["legacy_subdivision__sub"],
            ),
        ]
    }

    show_add_button = False

    def get_queryset(self):
        if self.kwargs.get("subdivision_id"):
            return LegacyAPSHome.objects.filter(
                legacy_subdivision__id=self.kwargs.get("subdivision")
            )
        ids = list(
            LegacyAPSHome.objects.order_by("-ck_req_date").values_list("id", flat=True)[:500]
        )
        return LegacyAPSHome.objects.order_by("-ck_req_date").filter(id__in=ids)

    def get_column_Site_Id_data(self, obj, *args, **kwargs):
        return '<a href="{}">{}</a>'.format(obj.aps_home.get_absolute_url(), obj.aps_id)

    def get_column_Address_data(self, obj, *args, **kwargs):
        # Filter out None values and join into string
        return " ".join(filter(None, [obj.addr_no, obj.addr_dir, obj.addr_name, obj.addr_sufx]))

    def get_column_City_data(self, obj, *args, **kwargs):
        return obj.lt_city

    def get_column_Zip_Code_data(self, obj, *args, **kwargs):
        return obj.lt_zip

    def get_column_Subdivision_data(self, obj, *args, **kwargs):
        return '<a href="{}">{}</a>'.format(
            obj.legacy_subdivision.get_absolute_url(), obj.legacy_subdivision
        )


class APSLegacyHomeDetailView(AuthenticationMixin, AxisDetailView):
    show_edit_button = False
    show_delete_button = False
    model = LegacyAPSHome
    permission_required = "customer_aps.view_legacyapshome"
    template_name = "customer_aps/legacyapshome_detail.html"
