import logging
from django.db.models import QuerySet
from axis.core.managers.utils import queryset_user_is_authenticated

__author__ = "Steven K"
__date__ = "11/12/2019 09:05"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

log = logging.getLogger(__name__)


class HESQuerySet(QuerySet):
    """Allow querying by the owner"""

    def filter_by_company(self, company):
        return self.filter(company=company)

    @queryset_user_is_authenticated
    def filter_by_user(self, user):
        return self.filter_by_company(user.company)
