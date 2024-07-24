"""control_center_base_list.py: """

from django.apps import apps
from axis.core.mixins import AuthenticationMixin
from axis.core.views.generic import AxisFilterView
from axis.user_management.datatables import AccreditationControlCenterListDatatable
from axis.user_management.filters import AccreditationFilter
from axis.user_management.forms import AccreditationControlCenterListFilterForm
from axis.user_management.models import Accreditation

__author__ = "Artem Hruzd"
__date__ = "10/30/2019 18:14"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

user_management_app = apps.get_app_config("user_management")


class AccreditationControlCenterListView(AuthenticationMixin, AxisFilterView):
    queryset = Accreditation.objects.all()
    datatable_class = AccreditationControlCenterListDatatable
    form_class = AccreditationControlCenterListFilterForm
    show_add_button = False
    template_name = "accreditation/control_center_list.html"

    def has_permission(self):
        return (
            self.request.company.slug
            in user_management_app.ACCREDITATION_APPLICABLE_COMPANIES_SLUGS
            or self.request.user.is_superuser
        )

    def get_queryset(self):
        return AccreditationFilter(
            data=self.request.GET, request=self.request, queryset=self.queryset
        ).qs

    def get_form_kwargs(self):
        kwargs = super(AccreditationControlCenterListView, self).get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(AccreditationControlCenterListView, self).get_context_data(**kwargs)

        context["accreditation_state_choices"] = Accreditation.STATE_CHOICES
        if self.request.user.is_superuser:
            context["company_choices"] = Accreditation.objects.distinct().values_list(
                "approver__company__pk", "approver__company__name"
            )
        return context
