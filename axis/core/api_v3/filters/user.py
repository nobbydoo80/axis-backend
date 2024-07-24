"""user.py: """

__author__ = "Artem Hruzd"
__date__ = "01/06/2020 21:24"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
    "Naruhito Kaide",
]

from django.contrib.auth import get_user_model
from django.db.models import Q, Count, Case, When, CharField, Value
from django_filters import rest_framework as filters

from axis.company.strings import COMPANY_TYPES
from axis.core.api_v3 import USER_FILTER_FIELDS
from axis.geographic.models import USState
from axis.user_management.models import Accreditation

User = get_user_model()


class UserFilter(filters.FilterSet):
    without_company = filters.BooleanFilter(field_name="company", lookup_expr="isnull")
    company__company_type = filters.MultipleChoiceFilter(
        field_name="company__company_type", choices=COMPANY_TYPES
    )

    class Meta:
        model = User
        fields = USER_FILTER_FIELDS
        filter_overrides = {
            "hirluserprofile__is_qa_designee": {"extra": lambda f: {"distinct": True}}
        }


class HIRLFindVerifierFilter(filters.FilterSet):
    us_states = filters.CharFilter(field_name="us_states", method="filter_us_states")
    accreditations__name = filters.CharFilter(
        field_name="accreditations__name", method="filter_accreditations_name"
    )

    class Meta:
        model = User
        fields = ("us_states", "accreditations__name")

    def filter_accreditations_name(self, queryset, name, value):
        return queryset.annotate(
            _filter_active_accreditations_count_by_name=Count(
                "accreditations",
                filter=Q(**{name: value}) & ~Q(accreditations__state=Accreditation.INACTIVE_STATE),
                distinct=True,
            ),
        ).filter(_filter_active_accreditations_count_by_name__gt=0)

    def filter_us_states(self, queryset, name, value):
        filtered_queryset = queryset.filter(
            Q(company__state=value)
            | Q(customer_hirl_enrolled_verifier_agreements__us_states__abbr__icontains=value)
        )
        final_queryset = filtered_queryset.annotate(
            is_or=Case(
                When(company__state=value, then=Value(0)),
                default=Value(1),
                output_field=CharField(),
            )
        ).order_by("is_or")
        return final_queryset
