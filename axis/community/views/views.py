"""views.py: Django community"""


import logging

from django.views.generic import RedirectView
from axis.core.mixins import AuthenticationMixin
from axis.core.views.generic import AxisDatatableView
from axis.relationship.models import Relationship
from ..models import Community
from ...core.utils import get_frontend_url
from .. import datatables

__author__ = "Steven Klass"
__date__ = "3/5/12 11:25 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class CommunityListView(AuthenticationMixin, AxisDatatableView):
    permission_required = "community.view_community"
    datatable_class = datatables.CommunityListDatatable

    select_related = {
        "city",
        "metro",
    }

    def get_queryset(self):
        queryset = Community.objects.filter_by_user(
            user=self.request.user, show_attached=True
        ).select_related(*self.select_related)

        if not hasattr(self, "_attached"):
            attached = Relationship.objects.filter_communities_for_company(
                self.request.company, show_attached=True
            )
            self._attached = list(
                attached.filter(is_attached=True, is_owned=False).values_list(
                    "object_id", flat=True
                )
            )

        return queryset

    def get_datatable_kwargs(self):
        kwargs = super(CommunityListView, self).get_datatable_kwargs()
        user = self.request.user
        if not user.is_superuser and user.has_perm("community.change_community"):
            kwargs["columns"] = self.datatable_class._meta.columns[:-1]

        return kwargs


class LegacyCommunityListRedirectView(RedirectView):
    """
    Temporary view to redirect old legacy links to new Frontend
    """

    def get_redirect_url(self, *args, **kwargs):
        return get_frontend_url("community")
