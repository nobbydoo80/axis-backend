"""RemRate Models suitable for use by Axis """


import logging

from django.db import models

from ..strings import (
    FUEL_TYPES,
    HEATING_EFF_UNITS,
    COOLING_EFF_UNITS,
    FAN_CONTROL_TYPES,
)

__author__ = "Steven Klass"
__date__ = "06/10/2019 11:03"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class AirSourceHeatPump(models.Model):
    """AshpType - Air Source Heat Pumps"""

    simulation = models.ForeignKey("Simulation", on_delete=models.CASCADE)
    _result_number = models.IntegerField(db_column="lBldgRunNo")
    _source_air_source_heat_pump_number = models.IntegerField(db_column="lASTASTNo")

    name = models.CharField(null=True, max_length=93, db_column="sASTType", blank=True)
    fuel_type = models.IntegerField(null=True, db_column="nASTFuel", choices=FUEL_TYPES)
    heating_capacity = models.FloatField(null=True, db_column="fASTHCap47")
    heating_efficiency = models.FloatField(null=True, db_column="FASTHEFF")
    heating_efficiency_units = models.IntegerField(
        null=True, db_column="NASTHEFFU", choices=HEATING_EFF_UNITS
    )
    cooling_capacity = models.FloatField(null=True, db_column="fASTCCAP")
    cooling_efficiency = models.FloatField(null=True, db_column="FASTCEFF")
    cooling_efficiency_units = models.IntegerField(
        null=True, db_column="NASTCEFFU", choices=COOLING_EFF_UNITS
    )
    sensible_heat_fraction = models.FloatField(null=True, db_column="fASTSHF")
    is_desuperheater = models.BooleanField(default=False, db_column="nASTDSHtr")
    note = models.CharField(null=True, max_length=765, db_column="sASTNote", blank=True)
    backup_capacity = models.FloatField(null=True, db_column="fASTBKUPCP")
    fan_control_type = models.IntegerField(
        null=True, db_column="nASTFnCtrl", choices=FAN_CONTROL_TYPES
    )
    fan_defaults = models.BooleanField(default=False, db_column="nASTFnDef")
    fan_high_speed = models.FloatField(null=True, db_column="fASTFnHSpd")
    fan_low_speed = models.FloatField(null=True, db_column="fASTFnLSpd")
    heating_capacity_17f = models.FloatField(null=True, db_column="fASTHCap17")

    def __str__(self):
        return '"{}", Air-Source heat Pump Htg: {} kBtuh, {} {}.  Clg: {} kBtuh, {} {}'.format(
            self.name,
            self.heating_capacity,
            self.heating_efficiency,
            self.get_heating_efficiency_units_display(),
            self.cooling_capacity,
            self.cooling_efficiency,
            self.get_cooling_efficiency_units_display(),
        )

    class Meta:
        ordering = ("simulation", "-heating_capacity", "-cooling_capacity")
