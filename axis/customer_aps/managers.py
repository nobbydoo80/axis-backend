"""managers.py: Django customer_aps"""


import logging

from django.db import models

__author__ = "Steven Klass"
__date__ = "9/7/12 3:10 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class APSManager(models.Manager):
    """Generic Manager"""

    def filter_by_company(self, company, **kwargs):
        """A way to trim down the list of objects by company"""
        if company.slug != "aps":
            return self.none()
        return self.filter(**kwargs)

    def filter_by_user(self, user, **kwargs):
        """A way to trim down the list of objects by user"""
        if user.is_superuser:
            return self.filter(**kwargs)
        try:
            kwargs["company"] = user.company
        except AttributeError:
            return self.none()
        return self.filter_by_company(**kwargs)
