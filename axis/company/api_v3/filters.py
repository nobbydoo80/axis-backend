"""filters.py: """

__author__ = "Artem Hruzd"
__date__ = "03/20/2020 19:48"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.db.models import Q
from django_filters import rest_framework as filters

from axis.company.api_v3 import COMPANY_FILTER_FIELDS
from axis.company.models import AltName, SponsorPreferences, Company, CompanyAccess, CompanyRole

from axis.company.strings import COMPANY_TYPES
from axis.geographic.models import USState, Country


class CompanyIsAttachedChoiceFilter(filters.ChoiceFilter):
    def __init__(self, *args, **kwargs):
        kwargs["choices"] = [
            ("", "All"),
            ("attached", "Attached"),
            ("unattached", "Unattached"),
        ]
        kwargs["help_text"] = (
            "“unattached” objects are safe to view, they’re just "
            "not officially connected to you yet"
        )
        self.is_relationship_based = kwargs.pop("is_relationship_based", True)
        super().__init__(*args, **kwargs)

    def filter(self, qs, value):
        if (
            not getattr(self, "parent")
            or not getattr(self.parent, "request")
            or not getattr(self.parent.request, "user")
            or not getattr(self.parent.request.user, "company")
        ):
            return qs

        base_kwargs = {}
        if self.is_relationship_based:
            base_kwargs = dict(show_attached=True, include_self=True)

        if value == "attached":
            qs = qs.filter_by_user(user=self.parent.request.user, **base_kwargs)
        elif value == "unattached":
            attached_ids = qs.filter_by_company(
                self.parent.request.user.company, **base_kwargs
            ).values_list("id", flat=True)
            qs = qs.exclude(id__in=list(attached_ids)).distinct()

        return qs


class CompanyFilter(filters.FilterSet):
    is_attached = CompanyIsAttachedChoiceFilter()
    active_customer_hirl_builder_agreements_count = filters.RangeFilter()
    company_type = filters.MultipleChoiceFilter(
        field_name="company_type",
        choices=COMPANY_TYPES,
    )
    city__county__state = filters.ModelMultipleChoiceFilter(
        field_name="city__county__state",
        to_field_name="abbr",
        queryset=USState.objects.all(),
    )
    city__country = filters.ModelMultipleChoiceFilter(
        field_name="city__country",
        to_field_name="pk",
        queryset=Country.objects.all(),
    )

    class Meta:
        model = Company
        fields = COMPANY_FILTER_FIELDS


class AltNameFilter(filters.FilterSet):
    class Meta:
        model = AltName
        fields = [
            "company",
        ]


class AffiliationsPreferencesFilter(filters.FilterSet):
    """
    Filtering for Affiliations preferences
    """

    class Meta:
        model = SponsorPreferences
        fields = ["can_edit_profile", "can_edit_identity_fields", "notify_sponsor_on_update"]


class SponsoringPreferencesFilter(filters.FilterSet):
    """
    Filtering for Sponsoring preferences
    """

    class Meta:
        model = SponsorPreferences
        fields = ["can_edit_profile", "can_edit_identity_fields", "notify_sponsor_on_update"]


class CompanyAccessRoleChoiceFilter(filters.MultipleChoiceFilter):
    """
    Support isnull filter for "general" user role
    """

    def __init__(self, *args, **kwargs):
        kwargs["choices"] = [
            ("", "All"),
            ("general_user", "General User"),
            (CompanyRole.IS_COMPANY_ADMIN, "Is Company Admin"),
        ]
        super().__init__(*args, **kwargs)

    def filter(self, qs, value):
        if not value:
            return qs

        if (
            not getattr(self, "parent")
            or not getattr(self.parent, "request")
            or not getattr(self.parent.request, "user")
            or not getattr(self.parent.request.user, "company")
        ):
            return qs

        query = Q(roles__slug__in=value)
        if "general_user" in value:
            query |= Q(roles__isnull=True)

        return qs.filter(query).distinct()


class CompanyAccessFilter(filters.FilterSet):
    roles = CompanyAccessRoleChoiceFilter()

    class Meta:
        model = CompanyAccess
        fields = (
            "user",
            "company",
            "user__is_active",
            "user__is_approved",
        )


class CompanyRoleFilter(filters.FilterSet):
    class Meta:
        model = CompanyRole
        fields = (
            "slug",
            "name",
        )
