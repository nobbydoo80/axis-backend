"""RemRate Models suitable for use by Axis """


import logging

from django.db import models

from ..strings import FUEL_TYPES, ISWH_TYPES, ISWH_DIST_TYPES, FAN_CONTROL_TYPES, PUMP_ENERGY_UNITS

__author__ = "Steven Klass"
__date__ = "06/10/2019 11:03"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class IntegratedSpaceWaterHeater(models.Model):
    """HtDhType - Integrated Space / Water Heaters"""

    simulation = models.ForeignKey("Simulation", on_delete=models.CASCADE)
    _result_number = models.IntegerField(db_column="lBldgRunNo")
    _source_integrated_space_water_heater_number = models.IntegerField(db_column="lHTDHTDNo")
    name = models.CharField(max_length=93, db_column="sHTDType", blank=True)
    fuel_type = models.FloatField(null=True, db_column="nHTDFuel", choices=FUEL_TYPES, blank=True)
    type = models.IntegerField(null=True, db_column="NHTDSYSTTP", choices=ISWH_TYPES, blank=True)
    distribution_type = models.FloatField(
        null=True, db_column="NHTDDISTTP", choices=ISWH_DIST_TYPES
    )
    output_capacity = models.FloatField(null=True, db_column="FHTDRATCAP")
    space_heating_efficiency = models.FloatField(null=True, db_column="FHTDSPHTE")
    water_heating_energy_factor = models.FloatField(null=True, db_column="FHTDWHEF")
    water_heating_recovery_efficiency = models.FloatField(null=True, db_column="FHTDWHRE")
    tank_size = models.FloatField(null=True, db_column="FHTDTNKSZ")
    tank_insulation = models.FloatField(null=True, db_column="FHTDTNKIN")
    fan_control_type = models.IntegerField(
        null=True, db_column="nHTDFnCtrl", choices=FAN_CONTROL_TYPES
    )
    fan_defaults = models.BooleanField(default=False, db_column="nHTDFnDef")
    fan_high_speed = models.FloatField(null=True, db_column="fHTDFnHSpd")
    fan_low_speed = models.FloatField(null=True, db_column="fHTDFnLSpd")
    note = models.CharField(max_length=765, db_column="sHTDNote", blank=True)
    auxiliary_electric = models.FloatField(null=True, db_column="fHTDAuxElc", blank=True)
    auxiliary_electric_type = models.IntegerField(
        null=True, db_column="nHTDAuxETp", choices=PUMP_ENERGY_UNITS, blank=True
    )
    auxiliary_defaults = models.BooleanField(default=False, db_column="nHTDAuxDef")

    class Meta:
        ordering = ("simulation", "-output_capacity")

    def __str__(self):
        return '"{}", {} {} kBtuh ({})'.format(
            self.name, self.get_type_display(), self.output_capacity, self.get_fuel_type_display()
        )
