"""country.py - axis"""

__author__ = "Steven K"
__date__ = "7/25/22 15:39"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from django.db.models import QuerySet

log = logging.getLogger(__name__)


class CountryQuerySet(QuerySet):
    def filter_by_company(self, company, **kwargs):
        kwargs.pop("include_self", None)
        if company is None:
            return self.none()
        return self.filter(id__in=company.countries.values_list("id").filter(**kwargs))

    def filter_by_user(self, user, **kwargs):
        kwargs.pop("include_self", None)
        if user.is_superuser:
            return self.all()
        return self.filter_by_company(company=user.company, **kwargs)
