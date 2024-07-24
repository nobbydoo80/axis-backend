"""filters.py: """

__author__ = "Artem Hruzd"
__date__ = "07/07/2020 13:11"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.db.models import Q
from django_filters import rest_framework as filters
from localflavor.us.us_states import STATE_CHOICES

from axis.core.utils.utils import YEAR_CHOICES
from axis.customer_eto.utils import ETO_REGIONS, get_zipcodes_for_eto_region_id
from axis.company.models import BuilderOrganization, Company
from axis.customer_hirl.models import HIRLProject
from axis.eep_program.models import EEPProgram

from axis.home.api_v3 import EEP_PROGRAM_HOME_STATUS_FILTER_FIELDS, HOME_FILTER_FIELDS
from axis.home.models import EEPProgramHomeStatus, Home


class CertificationLevelFilter(filters.BaseInFilter):
    field_name = "certification_level"
    lookup_expr = "in"


class EEPProgramHomeStatusFilter(filters.FilterSet):
    id = filters.BaseInFilter(field_name="id", lookup_expr="in")
    eep_program__slug = filters.ModelMultipleChoiceFilter(
        to_field_name="slug", queryset=EEPProgram.objects.all()
    )
    state = filters.MultipleChoiceFilter(choices=EEPProgramHomeStatus.get_state_choices())
    home__city__county__state = filters.MultipleChoiceFilter(
        field_name="home__city__county__state", choices=STATE_CHOICES
    )
    created_date__gte = filters.DateFilter(
        field_name="created_date", lookup_expr="gte", label="Date Created is greater then or equal"
    )
    created_date__lte = filters.DateFilter(
        field_name="created_date", lookup_expr="lte", label="Date Created is less then or equal"
    )
    created_date__range = filters.DateRangeFilter(
        field_name="created_date", label="Date Created range"
    )
    certification_date__gte = filters.DateFilter(
        field_name="certification_date",
        lookup_expr="gte",
        label="Date Certification is greater then or equal",
    )
    certification_date__lte = filters.DateFilter(
        field_name="certification_date",
        lookup_expr="lte",
        label="Date Certification is less then or equal",
    )

    certification_date__gte_or_isnull = filters.DateFilter(
        field_name="certification_date",
        label="Date Certification is greater then or equal or NULL",
        method="get_certification_date__gte_or_isnull",
    )
    certification_date__lte_or_isnull = filters.DateFilter(
        field_name="certification_date",
        method="get_certification_date__lte_or_isnull",
        label="Date Certification is less then or equal or NULL",
    )

    customer_hirl_project__billing_state = filters.MultipleChoiceFilter(
        choices=HIRLProject.BILLING_STATE_CHOICES, method="get_customer_hirl_project__billing_state"
    )

    certification_level = filters.MultipleChoiceFilter(
        field_name="certification_level",
        choices=[
            ("Emerald", "Emerald"),
            ("Silver", "Silver"),
            ("Gold", "Gold"),
            ("Bronze", "Bronze"),
            ("Certified", "Certified"),
        ],
        method="filter_certification_level",
    )

    additional_filter = filters.MultipleChoiceFilter(
        field_name="filter_additional_parameter",
        choices=[
            ("true", True),
            ("false", False),
        ],
        method="filter_additional_parameter",
    )

    class Meta:
        model = EEPProgramHomeStatus
        fields = EEP_PROGRAM_HOME_STATUS_FILTER_FIELDS

    def filter_certification_level(self, queryset, name, values):
        filtered_queryset = queryset.annotate_customer_hirl_certification_level().filter(
            certification_level__in=values
        )
        return filtered_queryset

    def get_certification_date__gte_or_isnull(self, queryset, field_name, value):
        return queryset.filter(
            Q(certification_date__gte=value) | Q(certification_date__isnull=True)
        )

    def get_certification_date__lte_or_isnull(self, queryset, field_name, value):
        return queryset.filter(
            Q(certification_date__lte=value) | Q(certification_date__isnull=True)
        )

    def get_customer_hirl_project__billing_state(self, queryset, field_name, value):
        return queryset.filter(
            Q(customer_hirl_project__billing_state__in=value)
            | Q(customer_hirl_project__manual_billing_state__in=value),
        )

    def filter_additional_parameter(self, queryset, name, values):
        # Get green_energy_badges value
        green_energy_badges = values[0]
        # Get hud_disaster_case_number value
        hud_disaster_case_number = values[1]
        # Get sampling
        sampling = values[2]
        # Get is_appeals_project
        is_appeals_project = values[3]
        # Get is_require_wri_certification
        is_require_wri_certification = values[4]
        # Get building_will_include_non_residential_space
        building_will_include_non_residential_space = values[5]
        # Get seeking_hud_mortgage_insurance_premium_reduction
        seeking_hud_mortgage_insurance_premium_reduction = values[6]
        # Get seeking_fannie_mae_green_financing
        seeking_fannie_mae_green_financing = values[7]
        # Get seeking_freddie_mac_green_financing
        seeking_freddie_mac_green_financing = values[8]
        # Get intended_to_be_affordable_housing
        intended_to_be_affordable_housing = values[9]
        # Get is_built_to_rent
        is_build_to_rent = values[10]

        q_objects = Q()

        if green_energy_badges == "true":
            q_objects |= Q(customer_hirl_project__green_energy_badges__isnull=False)

        if hud_disaster_case_number == "true":
            q_objects |= Q(customer_hirl_project__hud_disaster_case_number__isnull=False)

        if sampling == "true":
            q_objects |= Q(customer_hirl_project__registration__sampling__isnull=False)

        if is_appeals_project == "true":
            q_objects |= Q(customer_hirl_project__is_appeals_project=True)

        if is_require_wri_certification == "true":
            q_objects |= Q(customer_hirl_project__is_require_wri_certification=True)

        if building_will_include_non_residential_space == "true":
            q_objects |= Q(
                customer_hirl_project__registration__building_will_include_non_residential_space=True
            )

        if seeking_hud_mortgage_insurance_premium_reduction == "true":
            q_objects |= Q(
                customer_hirl_project__registration__seeking_hud_mortgage_insurance_premium_reduction=True
            )

        if seeking_fannie_mae_green_financing == "true":
            q_objects |= Q(
                customer_hirl_project__registration__seeking_fannie_mae_green_financing=True
            )

        if seeking_freddie_mac_green_financing == "true":
            q_objects |= Q(
                customer_hirl_project__registration__seeking_freddie_mac_green_financing=True
            )

        if intended_to_be_affordable_housing == "true":
            q_objects |= Q(
                customer_hirl_project__registration__intended_to_be_affordable_housing=True
            )

        if is_build_to_rent == "true":
            q_objects |= Q(customer_hirl_project__registration__is_build_to_rent=True)
        return queryset.filter(q_objects)


class CustomerHIRLCertifiedProjectsByMonthMetricsFilter(filters.FilterSet):
    years = filters.MultipleChoiceFilter(choices=YEAR_CHOICES, method="get_years")
    eep_program__slug = filters.ModelMultipleChoiceFilter(
        to_field_name="slug", queryset=EEPProgram.objects.all()
    )

    class Meta:
        model = EEPProgramHomeStatus
        fields = ("years", "customer_hirl_project__registration__is_build_to_rent")

    @property
    def qs(self):
        queryset = super(CustomerHIRLCertifiedProjectsByMonthMetricsFilter, self).qs
        queryset = queryset.filter(certification_date__isnull=False)
        return queryset

    def get_years(self, queryset, field_name, value):
        return queryset.filter(certification_date__year__in=value)

    def get_years(self, queryset, field_name, value):
        return queryset.filter(certification_date__year__in=value)


class HomeFilter(filters.FilterSet):
    eto_region = filters.ChoiceFilter(
        method="get_eto_region", choices=[(k, v) for k, v in ETO_REGIONS.items()]
    )
    homestatus__state = filters.ChoiceFilter(
        method="get_homestatus__state",
        choices=EEPProgramHomeStatus.get_state_choices()
        + [("-1", "Not certified"), ("-2", "Not Certified (exclude abandoned)")],
        help_text="Filter Homes by program state",
    )
    builder_organization = filters.BaseInFilter(
        method="get_builder_organization", help_text="Filter Homes by Builder organization(s)"
    )

    class Meta:
        model = Home
        fields = HOME_FILTER_FIELDS

    def get_eto_region(self, queryset, field_name, value):
        return queryset.filter(zipcode__in=get_zipcodes_for_eto_region_id(int(value)))

    def get_homestatus__state(self, queryset, field_name, value):
        if value == "-1":
            return queryset.exclude(homestatuses__state="complete")
        elif value == "-2":
            return queryset.exclude(
                Q(homestatuses__state="complete") | Q(homestatuses__state="abandoned")
            )
        return queryset.filter(homestatuses__state=value)

    def get_builder_organization(self, queryset, field_name, value):
        if not self.request or not self.request.user.is_authenticated:
            return queryset
        companies = (
            Company.objects.filter(company_type=Company.BUILDER_COMPANY_TYPE)
            .filter_by_user(user=self.request.user)
            .filter(id__in=self.request.GET.getlist("builder_organization"))
        )
        return Home.objects.filter_by_multiple_companies(companies, show_attached=True)
