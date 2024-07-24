"""apshome_views.py: Django """


import logging
from operator import attrgetter
from django.contrib import messages

from django.db.models.query_utils import Q
from django.http import HttpResponseRedirect
from django.urls import reverse
import datatableview.helpers

from axis.core.views.views import AuthenticationMixin
from axis.core.views.generic import LegacyAxisDatatableView, AxisDetailView, AxisUpdateView
from axis.filehandling.views import AsynchronousProcessedDocumentCreateView
from axis.home.models import Home
from axis.customer_aps.models import APSHome
from axis.incentive_payment.models import IncentivePaymentStatus
from ..forms import APSBulkHomeAsynchronousProcessedDocumentForm, APSHomeManualMatchForm

__author__ = "Steven Klass"
__date__ = "4/25/12 8:41 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class APSHomeListView(AuthenticationMixin, LegacyAxisDatatableView):
    """APS Homes List View"""

    permission_required = "customer_aps.view_apshome"
    model = APSHome
    show_add_button = True

    datatable_options = {
        "columns": [
            ("Premise ID", "premise_id", datatableview.helpers.link_to_model),
            ("Meter Set Date", "meterset_date", datatableview.helpers.format_date("%m/%d/%Y")),
            (
                "Address",
                ["raw_street_number", "raw_prefix", "raw_street_name", "raw_suffix"],
                datatableview.helpers.attrgetter("get_raw_addr"),
            ),
            ("City", "raw_city"),
            ("ZIP Code", "raw_zip"),
            ("Matched", None, datatableview.helpers.make_boolean_checkmark(key=attrgetter("home"))),
            ("Confirmed", "confirmed_address", datatableview.helpers.make_boolean_checkmark),
        ],
        "ordering": ["-meterset_date"],
    }

    def get_add_url(self):
        return reverse("aps_bulk_homes_add")


class APSHomeDetailView(AuthenticationMixin, AxisDetailView):
    permission_required = "customer_aps.view_apshome"

    show_delete_button = False

    def get_edit_url(self):
        return reverse("aps_homes_update_view", kwargs={"pk": self.object.id})

    def get_context_data(self, **kwargs):
        context = super(APSHomeDetailView, self).get_context_data(**kwargs)
        try:
            stats = self.object.home.homestatuses.filter(
                eep_program__owner__slug="aps"
            ).values_list("id", flat=True)
            show_ipp = IncentivePaymentStatus.objects.filter_by_user(self.request.user).filter(
                home_status_id__in=stats
            )
        except AttributeError:
            show_ipp = False
        context["show_ipp"] = show_ipp
        if self.object.home:
            context["axis_match_display"] = self.get_axis_match_display()
        return context

    def get_axis_match_display(self):
        axis_home = self.object.home

        if self.request.company.display_raw_addresses and axis_home.geocode_response:
            address_target = axis_home.geocode_response.geocode
            field_prefix = "raw_"
        else:
            address_target = axis_home
            field_prefix = ""

        def _address_field(name):
            try:
                field = getattr(address_target, "%s%s" % (field_prefix, name))
            except AttributeError:
                return getattr(axis_home, name)
            else:
                if not field:
                    field = getattr(axis_home, name)
            return field

        return {
            "street_line1": _address_field("street_line1"),
            "city": _address_field("city"),
            "state": _address_field("state"),
            "zipcode": _address_field("zipcode"),
        }


class APSHomeUpdateView(AuthenticationMixin, AxisUpdateView):
    """Update View"""

    permission_required = "customer_aps.change_apshome"
    form_class = APSHomeManualMatchForm
    model = APSHome
    allow_geocoding = False

    def get_cancel_url(self):
        return reverse("aps_homes_detail_view", kwargs={"pk": self.kwargs.get("pk")})

    def get_form(self, form_class=None):
        """Get the form"""
        form = super(APSHomeUpdateView, self).get_form(form_class)

        qs = Q(apshome__isnull=True)
        if self.object.home:
            qs = Q(apshome__isnull=True) | Q(apshome=self.object)

        if self.object.raw_zip:
            qs2 = Q(zipcode__startswith=self.object.raw_zip[:3])
            if self.object.raw_street_name:
                qs2 |= Q(street_line1__icontains=self.object.raw_street_name)
        elif self.object.raw_street_name:
            qs2 = Q(zipcode=self.object.raw_zip)
        else:
            qs2 = qs

        qs = Home.objects.filter_by_company(self.request.user.company).filter(qs, qs2)

        form.fields["home"].queryset = qs
        return form

    def form_valid(self, form):
        if self.object and "home" in form.cleaned_data:
            self.object.home = form.cleaned_data["home"]
            self.object.save()
            if self.object.legacyapshome_set.count():
                messages.error(
                    self.request,
                    "You have both an Axis home and a legacy APS home " "attached to this record!",
                )
        return HttpResponseRedirect(self.get_success_url())

    def get_form_kwargs(self):
        kwargs = super(APSHomeUpdateView, self).get_form_kwargs()
        kwargs.update({"user": self.request.user})
        return kwargs


class APSBulkHomeAsynchronousProcessedDocumentCreateView(AsynchronousProcessedDocumentCreateView):
    permission_required = "customer_aps.add_apshome"
    form_class = APSBulkHomeAsynchronousProcessedDocumentForm
    template_name = "filehandling/asynchronousprocesseddocument_form.html"

    def get_context_data(self, **kwargs):
        context = super(AsynchronousProcessedDocumentCreateView, self).get_context_data(**kwargs)
        context["title"] = "APS Meterset Upload"
        return context

    def get_cancel_url(self):
        return reverse("aps_homes_list_view")
