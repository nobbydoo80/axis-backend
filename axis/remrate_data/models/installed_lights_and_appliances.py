"""RemRate Models suitable for use by Axis """


import logging

from django.db import models

from ..strings import (
    INSTALLED_LAP_TYPES,
    MECHANICAL_EQUIP_LOCATIONS,
    INSTALLED_LAP_FUEL,
    INSTALLED_LAP_UNITS,
    INSTALLED_LAP_USE_UNITS,
)

__author__ = "Steven Klass"
__date__ = "06/10/2019 11:03"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class InstalledLightsAndAppliances(models.Model):
    """LAInst Installed Lights and Appliances"""

    simulation = models.ForeignKey("Simulation", on_delete=models.CASCADE)
    building = models.ForeignKey("Building", on_delete=models.CASCADE)
    _result_number = models.IntegerField(db_column="lBldgRunNo")
    _building_number = models.IntegerField(db_column="lBldgNo")

    name = models.CharField(max_length=765, db_column="SLAINAME", blank=True)
    type = models.IntegerField(null=True, db_column="NLAITYPE", choices=INSTALLED_LAP_TYPES)
    location = models.IntegerField(
        null=True, db_column="NLAILOC", choices=MECHANICAL_EQUIP_LOCATIONS
    )
    fuel_type = models.IntegerField(null=True, db_column="NLAIFUEL", choices=INSTALLED_LAP_FUEL)
    energy_use_rate = models.FloatField(null=True, db_column="FLAIRATE")
    energy_use_rate_unit = models.IntegerField(
        null=True, db_column="NLAIRATEU", choices=INSTALLED_LAP_UNITS
    )
    usage_amount = models.FloatField(null=True, db_column="FLAIUSE")
    usage_amount_unit = models.IntegerField(
        null=True, db_column="NLAIUSEU", choices=INSTALLED_LAP_USE_UNITS
    )
    quantity = models.IntegerField(db_column="NLAIQTY")
    efficiency = models.IntegerField(db_column="NLAIEFF", null=True)

    def __str__(self):
        return '{} "{}" ({}) {}'.format(
            self.get_type_display(),
            self.name,
            self.energy_use_rate,
            self.get_energy_use_rate_unit_display(),
        )
