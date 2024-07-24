__author__ = "Autumn Valenta"
__date__ = "08/22/16 5:00 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


from django.apps import apps
from django.views.generic import RedirectView

from axis.company.models import Company
from axis.core.mixins import AuthenticationMixin
from axis.core.utils import get_frontend_url
from axis.core.views.generic import AxisFilterView
from axis.customer_hirl.builder_agreements.filters import BuilderAgreementFilter
from axis.customer_hirl.models import BuilderAgreement
from . import forms, datatables

app = apps.get_app_config("customer_hirl")


class ActiveEnrollmentRedirectView(RedirectView):
    """Redirect depending on enrollment existance."""

    def get_redirect_url(self):  # pylint: disable=arguments-differ
        """Redirect to user's active enrollment or creation page if one does not exist."""
        client_agreement = (
            BuilderAgreement.objects.filter_by_user(user=self.request.user)
            .exclude(state=BuilderAgreement.EXPIRED)
            .first()
        )
        if client_agreement:
            return client_agreement.get_absolute_url()
        return get_frontend_url("hi", "client_agreements", "create")


class BuilderAgreementFilterView(AuthenticationMixin, AxisFilterView):
    """Agreement datatableview of enrolled companies."""

    model = BuilderAgreement
    permission_required = "customer_hirl.change_builderagreement"
    show_add_button = False
    template_name = "customer_hirl/builder_agreements_filter_list.html"

    form_class = forms.FilterForm
    datatable_class = datatables.FilterDatatable

    def has_permission(self):
        """Require that the user is from the customer running the enrollment."""
        if not self.request.user:
            return False

        if not self.request.user.company:
            return False

        if self.request.company.slug == app.CUSTOMER_SLUG:
            return True

        if self.request.user.company.company_type == Company.RATER_COMPANY_TYPE:
            return True

        return super(BuilderAgreementFilterView, self).has_permission()

    def get_queryset(self):
        queryset = self.model.objects.filter_by_user(user=self.request.user).select_related(
            "company", "company__hirlcompanyclient"
        )
        queryset = BuilderAgreementFilter(
            data=self.request.GET,
            request=self.request,
            queryset=queryset,
        ).qs
        return queryset

    def get_context_data(self, **kwargs):
        context = super(BuilderAgreementFilterView, self).get_context_data(**kwargs)
        context["verbose_name_plural"] = "Client Agreements"
        return context
