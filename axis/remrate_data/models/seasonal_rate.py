"""RemRate Models suitable for use by Axis """


import logging

from django.db import models

from ..strings import MONTHS

__author__ = "Steven Klass"
__date__ = "06/10/2019 11:03"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class SeasonalRate(models.Model):
    """Seasonal Rate Costs"""

    simulation = models.ForeignKey("Simulation", on_delete=models.CASCADE)
    rate = models.ForeignKey("UtilityRate", on_delete=models.CASCADE)
    _result_number = models.IntegerField(db_column="lBldgRunNo")
    _source_seasonal_rate_number = models.IntegerField(db_column="lSRSRNo")
    _utility_rate_no = models.IntegerField(db_column="lSRURNo")
    start_month = models.IntegerField(null=True, choices=MONTHS, db_column="nSRStrtMth")
    end_month = models.IntegerField(null=True, choices=MONTHS, db_column="nSRStopMth")
    cost = models.FloatField(null=True, db_column="fSRSvcChrg")

    def __str__(self):
        return "{:<40} Svc. Charge: ${:.2f}".format(
            "{} - {}".format(self.get_start_month_display(), self.get_end_month_display()),
            self.cost,
        )
