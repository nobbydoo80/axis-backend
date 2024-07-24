"""RemRate Models suitable for use by Axis """


import logging

from django.db import models

from ..managers import UtilityRateManager
from ..strings import FUEL_TYPES, UTILITY_UNITS

__author__ = "Steven Klass"
__date__ = "06/10/2019 11:03"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class UtilityRate(models.Model):
    """Utility Rates"""

    simulation = models.ForeignKey("Simulation", on_delete=models.CASCADE)
    _result_number = models.IntegerField(db_column="lBldgRunNo")
    _source_utility_rate_no = models.IntegerField(db_column="lURURNo")
    name = models.CharField(max_length=93, db_column="sURName", blank=True)
    fuel_type = models.IntegerField(null=True, db_column="nURFuelTyp", choices=FUEL_TYPES)
    units = models.IntegerField(null=True, choices=UTILITY_UNITS, db_column="nURUnits")

    objects = UtilityRateManager()

    def __str__(self):
        return '"{}": {}'.format(self.get_fuel_type_display(), self.name)
