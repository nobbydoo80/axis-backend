"""RemRate Models suitable for use by Axis """


import logging

from django.db import models

from ..strings import H2O_HEATER_TYPES, FUEL_TYPES

__author__ = "Steven Klass"
__date__ = "06/10/2019 11:03"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class HotWaterHeater(models.Model):
    """DhwType - Hot Water Heaters"""

    simulation = models.ForeignKey("Simulation", on_delete=models.CASCADE)
    _result_number = models.IntegerField(db_column="lBldgRunNo")
    _source_hot_water_heater_number = models.FloatField(db_column="lDETDETNo")
    name = models.CharField(max_length=93, db_column="sDETType", blank=True)
    type = models.IntegerField(null=True, db_column="nDETSystTp", choices=H2O_HEATER_TYPES)
    fuel_type = models.IntegerField(null=True, db_column="nDETFuelTp", choices=FUEL_TYPES)
    tank_size = models.FloatField(null=True, db_column="fDETTnkVol")
    extra_tank_insulation_r_value = models.FloatField(null=True, db_column="fDETTnkIns", blank=True)
    energy_factor = models.FloatField(null=True, db_column="fDETEnergy")
    recovery_efficiency = models.FloatField(null=True, db_column="fDETRecEff")
    note = models.CharField(max_length=765, db_column="sDETNote", blank=True, null=True)

    class Meta:
        ordering = ("simulation", "-tank_size")

    def __str__(self):
        name = '"{}", {}'.format(self.name, self.get_type_display())
        if self.tank_size and self.tank_size > 0:
            name += " {} gal".format(self.tank_size)
        name += " ({})".format(self.get_fuel_type_display())
        return name
