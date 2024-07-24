"""metro.py - axis"""

__author__ = "Steven K"
__date__ = "7/25/22 15:27"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from django.db import models
from django.db.models import QuerySet

log = logging.getLogger(__name__)


class MetroManager(models.Manager):
    def get_queryset(self):
        return MetroQuerySet(self.model, using=self._db)

    def get_by_natural_key(self, name):
        return self.get(name=name)


class MetroQuerySet(QuerySet):
    pass
