import logging

from django.db.models.query import Q

__author__ = "Autumn Valenta"
__date__ = "9/20/17 4:38 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class FilterByCompanyMixin(object):
    def get_filter_by_company_filter(self, company):
        """Returns a list of Q() objects needed to filter this queryset by a company."""
        return Q()

    def get_filter_by_user_filter(self, user):
        """Returns a list of Q() objects needed to filter this queryset by a user."""
        return Q()

    def filter_by_company(self, company):
        """Filters this queryset using Q() objects returned from get_filter_by_company_filter()"""
        filter = self.get_filter_by_company_filter(company)
        if filter is None:
            queryset = self.filter()
        else:
            queryset = self.filter(filter)
        return queryset.distinct()

    def filter_by_user(self, user):
        """Filters this queryset using Q() objects returned from get_filter_by_user_filter()"""
        filter = self.get_filter_by_user_filter(user)
        if filter is None:
            queryset = self.filter()
        else:
            queryset = self.filter(filter)
        return queryset.distinct()


class OwnedObjectMixin(FilterByCompanyMixin):
    """Filters by company/user based on a model field indicating an owning company."""

    # Hint for the field holding the owning company (e.g., 'eep_program__owner', 'company', etc)
    owner_field = None

    # Component filters used in building larger filters
    def get_owner_filter(self, company):
        return Q(**{self.owner_field: company})

    # Filter builders for main methods
    def get_filter_by_company_filter(self, company):
        filter = super(OwnedObjectMixin, self).get_filter_by_company_filter(company)
        filter |= self.get_owner_filter(company)
        return filter

    def get_filter_by_user_filter(self, user):
        if user.is_superuser:
            return None

        filter = super(OwnedObjectMixin, self).get_filter_by_user_filter(user)
        filter |= self.get_owner_filter(user.company)
        return filter


class AssociationObjectMixin(FilterByCompanyMixin):
    """Filters by company/user based on associations present."""

    # Component filters used in building larger filters
    def get_association_filter(self, company=None, user=None):
        assert company or user, "Must provide one of: company, user"

        if user:
            company = user.company

        q_association_constraints = Q(associations__is_active=True)

        q_association_target = Q(associations__company=company)
        if user:
            # Use OR, so that users implicitly get their company's stuff too.
            q_association_target |= Q(associations__user=user)

        return q_association_constraints & q_association_target

    # Filter builders for main methods
    def get_filter_by_company_filter(self, company):
        filter = super(AssociationObjectMixin, self).get_filter_by_company_filter(company)
        filter |= self.get_association_filter(company=company)
        return filter

    def get_filter_by_user_filter(self, user):
        if user.is_superuser:
            return None

        filter = super(AssociationObjectMixin, self).get_filter_by_user_filter(user)
        filter |= self.get_association_filter(user=user)
        return filter
