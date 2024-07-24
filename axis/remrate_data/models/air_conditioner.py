"""RemRate Models suitable for use by Axis """


import logging

from django.db import models

from ..strings import COOLING_TYPES, COOLING_EFF_UNITS, PUMP_ENERGY_UNITS, FUEL_TYPES

__author__ = "Steven Klass"
__date__ = "06/10/2019 11:03"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class AirConditioner(models.Model):
    """ClgType - Air Coolers"""

    simulation = models.ForeignKey("Simulation", on_delete=models.CASCADE)
    _result_number = models.IntegerField(db_column="lBldgRunNo")
    _source_air_conditioner_number = models.FloatField(db_column="lCETCETNo")
    name = models.CharField(max_length=93, db_column="sCETType", blank=True)
    type = models.IntegerField(null=True, db_column="nCETSystTp", choices=COOLING_TYPES)
    fuel_type = models.IntegerField(null=True, db_column="nCETFuelTp", choices=FUEL_TYPES)
    output_capacity = models.FloatField(null=True, db_column="fCETRatCap")
    efficiency = models.FloatField(null=True, db_column="fCETEff")
    sensible_heat_fraction = models.FloatField(null=True, db_column="fCETSHF")
    efficiency_unit = models.IntegerField(
        null=True, choices=COOLING_EFF_UNITS, db_column="nCETEffUTp"
    )
    is_desuperheater = models.BooleanField(default=False, db_column="nCETDSHtr")
    fan_control_type = models.IntegerField(null=True, db_column="nCETFnCtrl")
    fan_defaults = models.BooleanField(default=False, db_column="nCETFnDef")
    fan_high_speed = models.FloatField(null=True, db_column="fCETFnHSpd")
    fan_low_speed = models.FloatField(null=True, db_column="fCETFnLSpd")
    note = models.CharField(max_length=765, db_column="sCETNote", blank=True, null=True)
    fan_power = models.FloatField(null=True, db_column="fCETFanPwr")
    pump_energy = models.FloatField(null=True, db_column="fCETPmpEng")
    pump_energy_units = models.IntegerField(
        null=True, db_column="nCETPmpTyp", choices=PUMP_ENERGY_UNITS
    )
    fan_electric_default = models.BooleanField(default=False, db_column="nCETFanDef")

    class Meta:
        ordering = ("simulation", "-output_capacity")

    def __str__(self):
        return '"{}", A/C {} {}'.format(
            self.name, self.efficiency, self.get_efficiency_unit_display()
        )
