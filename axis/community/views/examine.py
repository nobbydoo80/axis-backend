from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy

from axis import examine
from axis.core.mixins import AuthenticationMixin
from axis.core.models import RecentlyViewed
from axis.core.views.generic import AxisExamineView, AxisDatatableView
from axis.core.views.machinery import (
    AxisGeocodedMachineryMixin,
    object_relationships_machinery_factory,
)
from ..api import CommunityViewSet
from ..datatables import CommunitySubivisionListDatatable
from ..forms import CommunityForm
from ..models import Community

__author__ = "Autumn Valenta"
__date__ = "09-19-14 12:31 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


class CommunityExamineView(LoginRequiredMixin, AxisExamineView):
    """Builds the machineries required for loading the page."""

    model = Community

    def get_queryset(self):
        return Community.objects.filter_by_user(user=self.request.user)

    def get_machinery(self):
        machineries = {}
        kwargs = {
            "create_new": self.create_new,
            "context": {
                "request": self.request,
            },
        }
        community = self.object
        machinery = CommunityExamineMachinery(instance=community, **kwargs)
        machineries[machinery.type_name_slug] = machinery
        self.primary_machinery = machinery

        RelationshipsMachinery = object_relationships_machinery_factory(self.model)
        machinery = RelationshipsMachinery(instance=community, **kwargs)
        machineries["relationships"] = machinery

        return machineries

    def _get_subdivision_datatable(self):
        satellite_view = SatelliteSubdivisionDatatable()
        satellite_view.request = self.request
        satellite_view.kwargs = self.kwargs
        datatable = satellite_view.get_datatable(result_counter_id="id_subdivision_count")
        datatable.url = reverse(
            "community:view_subdivisions", kwargs={"pk": self.kwargs.get("pk", 0)}
        )
        return datatable

    def get_context_data(self, **kwargs):
        context = super(CommunityExamineView, self).get_context_data(**kwargs)
        context["subdivisions_datatable"] = self._get_subdivision_datatable()
        RecentlyViewed.objects.view(instance=self.object, by=self.request.user)
        return context


class SatelliteSubdivisionDatatable(AuthenticationMixin, AxisDatatableView):
    permission_required = "community.view_community"
    datatable_class = CommunitySubivisionListDatatable

    def get_queryset(self):
        if not self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            from axis.subdivision.models import Subdivision

            return Subdivision.objects.none()
        community = Community.objects.filter_by_user(self.request.user).get(pk=self.kwargs["pk"])
        queryset = community.subdivision_set.filter_by_user(
            self.request.user, show_attached=False
        ).select_related("builder_org")
        return queryset


class CommunityExamineMachineryMixin(AxisGeocodedMachineryMixin):
    model = Community
    form_class = CommunityForm
    api_provider = CommunityViewSet
    type_name = "community"

    detail_template = "examine/community/community_detail.html"
    form_template = "examine/community/community_form.html"

    delete_success_url = reverse_lazy("community:list")


class CommunityExamineMachinery(CommunityExamineMachineryMixin, examine.PrimaryMachinery):
    def get_helpers(self, instance):
        helpers = super(CommunityExamineMachinery, self).get_helpers(instance)
        helpers["page_title"] = "{} {}".format(self.get_verbose_name(instance), instance)
        return helpers

    def serialize_form_spec(self, instance, form):
        data = super(CommunityExamineMachinery, self).serialize_form_spec(instance, form)
        if hasattr(form.fields["name"], "relationship_add_url"):
            data["name"]["options"]["relationship_add_url"] = form.fields[
                "name"
            ].relationship_add_url
        return data
