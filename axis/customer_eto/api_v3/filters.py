__author__ = "Rajesh Pethe"
__date__ = "12/15/2022 17:43:50"
__copyright__ = "Copyright 2011-2022 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Rajesh Pethe",
    "Steven Klass",
]


from django_filters import rest_framework as filters

from axis.customer_eto.models import ETOAccount


class ProjectTrackerFilter(filters.FilterSet):
    program = filters.CharFilter(
        field_name="home_status__eep_program__slug", lookup_expr="icontains"
    )
    submit_status = filters.CharFilter(field_name="submit_status", lookup_expr="icontains")
    rater_slug = filters.CharFilter(field_name="submit_user__company__slug", lookup_expr="iexact")


class ETOAccountFilter(filters.FilterSet):
    class Meta:
        model = ETOAccount
        fields = ("company",)
