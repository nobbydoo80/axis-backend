"""Django AEC Models - Theses are the source data coming in on the rate database."""


import logging

from django.db import models

from axis.remrate_data.strings import FUEL_TYPES, UTILITY_UNITS

__author__ = "Steven Klass"
__date__ = "06/09/2019 13:51"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class UtilityRates(models.Model):
    """Utility Rates"""

    result_number = models.IntegerField(null=True, db_column="LBLDGRUNNO", blank=True)
    name = models.CharField(max_length=93, db_column="SURNAME", blank=True)
    fuel_type = models.IntegerField(
        null=True, db_column="NURFUELTYP", choices=FUEL_TYPES, blank=True
    )
    utility_rate_no = models.IntegerField(db_column="LURURNO")
    units = models.IntegerField(null=True, choices=UTILITY_UNITS, db_column="NURUNITS", blank=True)

    class Meta:
        db_table = "UtilRate"
        managed = False
