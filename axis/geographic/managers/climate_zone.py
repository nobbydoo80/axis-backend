"""climate_zone.py - axis"""

__author__ = "Steven K"
__date__ = "7/25/22 15:27"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from django.db import models
from django.db.models.query import QuerySet

log = logging.getLogger(__name__)


class ClimateZoneManager(models.Manager):
    def get_queryset(self):
        return ClimateZoneQuerySet(self.model, using=self._db)

    def get_by_natural_key(self, doe_zone):
        return self.get(doe_zone=doe_zone)

    def get_by_code(self, code):
        return self.get_queryset().get_by_code(code)


class ClimateZoneQuerySet(QuerySet):
    def get_by_code(self, code):
        """Return the Climate Zone by code"""
        code = str(code)
        if len(code) > 2:
            raise TypeError("Expecting 2 digit code")
        zone, moisture = code[0], None
        if len(code) > 1:
            moisture = code[1].upper()
        log.debug("Looking up %s" % code)
        return self.get(zone=zone, moisture_regime=moisture)
