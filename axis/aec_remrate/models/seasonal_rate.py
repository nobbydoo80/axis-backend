"""Django AEC Models - Theses are the source data coming in on the rate database."""


import logging

from django.db import models

from axis.remrate_data.strings import MONTHS

__author__ = "Steven Klass"
__date__ = "06/09/2019 13:51"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class SeasonalRate(models.Model):
    """Seasonal Rate Costs"""

    result_number = models.IntegerField(null=True, db_column="LBLDGRUNNO", blank=True)
    utility_rate_no = models.IntegerField(db_column="LSRURNO")
    seasonal_rate_no = models.IntegerField(null=True, db_column="lSRSRNo", blank=True)
    start_month = models.IntegerField(null=True, choices=MONTHS, db_column="NSRSTRTMTH", blank=True)
    end_month = models.IntegerField(null=True, choices=MONTHS, db_column="NSRSTOPMTH", blank=True)
    cost = models.FloatField(null=True, db_column="FSRSVCCHRG", blank=True)

    class Meta:
        db_table = "SeasnRat"
        managed = False
