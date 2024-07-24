"""managers.py: Django """

__author__ = "Steven Klass"
__date__ = "3/11/12 10:47 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

import logging
from django.db import models
from django.db.models import QuerySet

log = logging.getLogger(__name__)


class RemRateUserManager(QuerySet):
    def filter_by_company(self, company, **kwargs):
        """A way to trim down the list of objects by company"""
        return self.filter(company=company, is_active=True, **kwargs)

    def filter_by_user(self, user, **kwargs):
        """A way to trim down the list of objects by user"""
        if user.is_superuser:
            return self.filter(**kwargs)
        try:
            kwargs["company"] = user.company
        except AttributeError:
            return self.none()
        return self.filter_by_company(**kwargs)
