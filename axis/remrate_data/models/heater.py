"""RemRate Models suitable for use by Axis """


import logging

from django.db import models

from ..strings import (
    HEATER_TYPES,
    FUEL_TYPES,
    HEATING_EFF_UNITS,
    FAN_CONTROL_TYPES,
    AUX_ELEC_UNITS,
    PUMP_ENERGY_UNITS,
)

__author__ = "Steven Klass"
__date__ = "06/10/2019 11:03"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class Heater(models.Model):
    """HtgType - Heaters"""

    simulation = models.ForeignKey("Simulation", on_delete=models.CASCADE)
    _result_number = models.IntegerField(db_column="lBldgRunNo")
    _source_heater_number = models.FloatField(db_column="lHETHETNo")
    name = models.CharField(max_length=93, db_column="sHETType", blank=True)
    type = models.IntegerField(null=True, db_column="nHETSystTp", choices=HEATER_TYPES)
    fuel_type = models.IntegerField(null=True, db_column="nHETFuelTp", choices=FUEL_TYPES)
    output_capacity = models.FloatField(null=True, db_column="fHETRatCap")
    efficiency = models.FloatField(null=True, db_column="fHETEff")
    efficiency_unit = models.IntegerField(
        null=True, db_column="nHETEffUTp", choices=HEATING_EFF_UNITS
    )
    is_desuperheater = models.BooleanField(default=False, db_column="nHETDSHtr")
    fan_control_type = models.IntegerField(
        null=True, db_column="nHETFnCtrl", choices=FAN_CONTROL_TYPES
    )
    fan_defaults = models.BooleanField(default=False, db_column="nHETFnDef")
    fan_high_speed = models.FloatField(null=True, db_column="fHETFnHSpd")
    fan_low_speed = models.FloatField(null=True, db_column="fHETFnLSpd")
    note = models.CharField(null=True, max_length=765, db_column="sHETNote", blank=True)
    auxiliary_electric = models.FloatField(null=True, db_column="fHETAuxElc", blank=True)
    auxiliary_electric_type = models.IntegerField(
        null=True, db_column="nHETAuxETp", choices=AUX_ELEC_UNITS, blank=True
    )
    auxiliary_defaults = models.BooleanField(default=False, db_column="nHETAuxDef")
    fan_power = models.FloatField(null=True, db_column="fHETFanPwr")
    pump_energy = models.FloatField(null=True, db_column="fHETPmpEng")
    pump_energy_units = models.IntegerField(
        null=True, db_column="nHETPmpTyp", choices=PUMP_ENERGY_UNITS
    )
    rated_output_capacity_17f = models.FloatField(null=True, db_column="fHETRCap17")

    class Meta:
        ordering = ("simulation", "-output_capacity")

    def __str__(self):
        return '"{}", {} {} kBtuh ({}) - {} {}'.format(
            self.name,
            self.get_type_display(),
            self.output_capacity,
            self.get_fuel_type_display(),
            self.efficiency,
            self.get_efficiency_unit_display(),
        )
