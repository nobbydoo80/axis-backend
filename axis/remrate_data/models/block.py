"""RemRate Models suitable for use by Axis """


import logging

from django.db import models

from ..managers import BlockManager

__author__ = "Steven Klass"
__date__ = "06/10/2019 11:03"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class Block(models.Model):
    """Block - used to associate Block to Season Rate"""

    simulation = models.ForeignKey("Simulation", on_delete=models.CASCADE)
    seasonal_rate = models.ForeignKey("SeasonalRate", on_delete=models.CASCADE)
    _result_number = models.IntegerField(db_column="lBldgRunNo")
    _seasonal_rate_number = models.IntegerField(db_column="lBLSRNo")
    max_consumption = models.FloatField(null=True, db_column="fBLBlckMax", blank=True)
    dollars_per_unit_per_month = models.FloatField(null=True, db_column="fBLRate", blank=True)

    objects = BlockManager()

    def __str__(self):
        return "{} ${:.2f} $/kWH".format(self.max_consumption, self.dollars_per_unit_per_month)
