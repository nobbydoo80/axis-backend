"""contact_card.py: """

__author__ = "Artem Hruzd"
__date__ = "05/12/2021 21:36"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.db.models import Q
from django_filters import rest_framework as filters

from axis.core.api_v3 import CONTACT_CARD_FILTER_FIELDS
from axis.core.models import ContactCard
from axis.company.models import Company


class ContactCardFilter(filters.FilterSet):
    without_company = filters.BooleanFilter(field_name="company", lookup_expr="isnull")
    without_user = filters.BooleanFilter(field_name="user", lookup_expr="isnull")

    company_and_related_users = filters.ModelChoiceFilter(
        queryset=Company.objects.all(),
        method="get_company_and_related_users",
        help_text="Selects Contact Card for provided Company and related Users",
    )

    class Meta:
        model = ContactCard
        fields = CONTACT_CARD_FILTER_FIELDS

    def get_company_and_related_users(self, queryset, name, company):
        return queryset.filter(Q(company=company) | Q(user__company=company, user__is_active=True))
