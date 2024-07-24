"""RemRate Models suitable for use by Axis """


import logging

from django.db import models

from ..managers import FuelSummaryManager
from ..strings import FUEL_TYPES, UTILITY_UNITS

__author__ = "Steven Klass"
__date__ = "06/10/2019 11:03"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class FuelSummary(models.Model):
    """Fuel Summary"""

    simulation = models.ForeignKey("Simulation", on_delete=models.CASCADE)
    _result_number = models.IntegerField(db_column="lBldgRunNo")
    fuel_type = models.IntegerField(null=True, db_column="nFSFuel", choices=FUEL_TYPES)
    fuel_units = models.IntegerField(null=True, db_column="nFSUnits", choices=UTILITY_UNITS)
    heating_consumption = models.FloatField(null=True, db_column="fFSHCons")
    cooling_consumption = models.FloatField(null=True, db_column="fFSCCons")
    hot_water_consumption = models.FloatField(null=True, db_column="fFSWCons")
    lights_and_appliances_consumption = models.FloatField(null=True, db_column="fFSLACons")
    total_cost = models.FloatField(null=True, db_column="fFSTotCost")
    rating_number = models.CharField(max_length=93, db_column="sRateNo")
    photo_voltaics_consumption = models.FloatField(null=True, db_column="fFSPVCons")
    total_consumption = models.FloatField(null=True, db_column="fFSTotCons")

    objects = FuelSummaryManager()

    def __str__(self):
        return "{} ${}".format(self.get_fuel_type_display(), round(self.total_cost, 2))
