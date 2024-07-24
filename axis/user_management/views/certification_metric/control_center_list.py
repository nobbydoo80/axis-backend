"""control_center_list.py: """

from django.apps import apps
from django.db.models import Q

from axis.core.mixins import AuthenticationMixin
from axis.core.views.generic import AxisFilterView
from axis.home.models import EEPProgramHomeStatus
from axis.company.models import Company
from axis.eep_program.models import EEPProgram
from axis.user_management.datatables import CertificationMetricControlCenterListDatatable
from axis.user_management.filters import CertificationMetricFilter
from axis.user_management.forms import CertificationMetricControlCenterListFilterForm

__author__ = "Artem Hruzd"
__date__ = "10/30/2019 18:14"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

user_management_app = apps.get_app_config("user_management")


class CertificationMetricControlCenterListView(AuthenticationMixin, AxisFilterView):
    datatable_class = CertificationMetricControlCenterListDatatable
    form_class = CertificationMetricControlCenterListFilterForm
    show_add_button = False
    template_name = "certification_metric/control_center_base_list.html"
    filterset_class = CertificationMetricFilter

    def has_permission(self):
        return (
            self.request.user.is_superuser
            or self.request.user.is_company_admin
            and self.request.user.company.slug
            in user_management_app.CERTIFICATION_METRIC_APPLICABLE_COMPANIES_SLUGS
        )

    @property
    def certification_metrics(self):
        """
        A rater should be able to see his own metrics.
        Admins of the company the rater works for
        should see all metrics for all users and admins of that company.
        :return: EEPProgramHomeStatus queryset
        """
        if self.request.user.is_superuser:
            return EEPProgramHomeStatus.objects.exclude(
                rater_of_record=None,
                customer_hirl_rough_verifier=None,
                customer_hirl_final_verifier=None,
            )

        if (
            self.request.user.company.slug
            in user_management_app.CERTIFICATION_METRIC_APPLICABLE_COMPANIES_SLUGS
        ):
            return EEPProgramHomeStatus.objects.filter(
                eep_program__in=self.request.user.company.eepprogram_set.all()
            ).exclude(
                rater_of_record=None,
                customer_hirl_rough_verifier=None,
                customer_hirl_final_verifier=None,
            )

        if (
            self.request.user.company.company_type == "rater"
            and not self.request.user.is_company_admin
        ):
            return EEPProgramHomeStatus.objects.filter(
                Q(rater_of_record=self.request.user)
                | Q(customer_hirl_rough_verifier=self.request.user)
                | Q(customer_hirl_final_verifier=self.request.user)
            )

        if self.request.user.is_company_admin:
            company_users = self.request.user.company.users.all()
            return EEPProgramHomeStatus.objects.filter(
                Q(rater_of_record__in=company_users)
                | Q(customer_hirl_rough_verifier__in=company_users)
                | Q(customer_hirl_final_verifier__in=company_users)
            )

        return EEPProgramHomeStatus.objects.none()

    def get_queryset(self):
        return self.filterset_class(
            data=self.request.GET,
            request=self.request,
            queryset=self.certification_metrics,
        ).qs.select_related(
            "eep_program",
            "customer_hirl_final_verifier",
            "customer_hirl_final_verifier__company",
            "customer_hirl_rough_verifier",
            "customer_hirl_rough_verifier__company",
            "rater_of_record",
            "rater_of_record__company",
            "home",
        )

    def get_form_kwargs(self):
        kwargs = super(CertificationMetricControlCenterListView, self).get_form_kwargs()
        kwargs["user"] = self.request.user
        kwargs["companies"] = Company.objects.filter(
            pk__in=self.certification_metrics.values_list(
                "rater_of_record__company__pk", flat=True
            ).distinct()
        ).distinct()
        kwargs["eep_programs"] = EEPProgram.objects.filter(
            id__in=self.certification_metrics.values_list("eep_program__id", flat=True).distinct()
        )
        return kwargs
