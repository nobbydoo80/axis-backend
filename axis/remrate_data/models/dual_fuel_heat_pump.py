"""RemRate Models suitable for use by Axis """


import logging

from django.db import models

from ..strings import FUEL_TYPES, HEATING_EFF_UNITS

__author__ = "Steven Klass"
__date__ = "06/10/2019 11:03"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class DualFuelHeatPump(models.Model):
    """DfhpType - Dual Fuel Heat Pumps"""

    simulation = models.ForeignKey("Simulation", on_delete=models.CASCADE)
    _result_number = models.IntegerField(db_column="lBldgRunNo")
    _source_dual_fuel_heat_pump_number = models.IntegerField(db_column="lDFTDFTNo")

    name = models.CharField(max_length=93, db_column="sDFTType", blank=True)
    fuel_type = models.IntegerField(null=True, db_column="nDFTFuel", choices=FUEL_TYPES)
    heating_hspf = models.FloatField(null=True, db_column="fDFTHHSPF")
    heating_capacity = models.FloatField(null=True, db_column="fDFTHCap47")
    backup_fuel_type = models.IntegerField(null=True, db_column="nDFTBFuel", choices=FUEL_TYPES)
    backup_heating_efficiency_units = models.IntegerField(
        null=True, db_column="nDFTBEffU", choices=HEATING_EFF_UNITS
    )
    backup_heating_seasonal_efficiency = models.FloatField(null=True, db_column="fDFTBSEff")
    backup_heating_capacity = models.FloatField(null=True, db_column="fDFTBCap")
    cooling_seer = models.FloatField(null=True, db_column="fDFTCSEER")
    cooling_capacity = models.FloatField(null=True, db_column="fDFTCCap")
    cooling_sensible_heat_fraction = models.FloatField(null=True, db_column="fDFTCSHF")
    is_desuperheater = models.BooleanField(default=False, db_column="nDFTDSHtr")
    switch_over_temperature = models.FloatField(null=True, db_column="fDFTSwitch")
    fan_control_type = models.IntegerField(null=True, db_column="nDFTFnCtrl")
    fan_defaults = models.BooleanField(default=False, db_column="nDFTFnDef")
    fan_high_speed = models.FloatField(null=True, db_column="fDFTFnHSpd")
    fan_low_speed = models.FloatField(null=True, db_column="fDFTFnLSpd")
    note = models.CharField(max_length=765, db_column="sDFTNote", blank=True)

    class Meta:
        ordering = ("simulation", "-heating_capacity", "-cooling_capacity")

    def __str__(self):
        return '"{}", Dual-Fuel Heat Pump {}/{} kBtuh ({}/{})'.format(
            self.name,
            self.heating_capacity,
            self.cooling_capacity,
            self.get_fuel_type_display(),
            self.get_backup_fuel_type_display(),
        )
