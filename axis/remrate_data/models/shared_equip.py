"""shared_equip.py - Axis"""

__author__ = "Steven K"
__date__ = "7/22/21 12:14"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from django.db import models

from ..strings import (
    SHARED_EQUIPMENT_TYPES,
    FUEL_TYPES,
    SHARED_EFFICIENCY_UNITS,
    SHARED_DISTRIBUTION_TYPES,
)

log = logging.getLogger(__name__)


class SharedEquipment(models.Model):
    simulation = models.ForeignKey("Simulation", on_delete=models.CASCADE)
    ground_source_heat_pump = models.ForeignKey(
        "GroundSourceHeatPump", on_delete=models.CASCADE, null=True
    )
    water_loop_heat_pump = models.ForeignKey(
        "WaterLoopHeatPump", on_delete=models.CASCADE, null=True
    )
    _result_number = models.IntegerField(db_column="lBldgRunNo")
    _source_shared_equipment_number = models.IntegerField(db_column="lSharedEqKey")
    name = models.CharField(max_length=31, db_column="sName", blank=True, null=True)
    type = models.IntegerField(
        db_column="nSystem", blank=True, null=True, choices=SHARED_EQUIPMENT_TYPES
    )
    fuel_type = models.IntegerField(db_column="nFuel", blank=True, null=True, choices=FUEL_TYPES)
    rated_efficiency = models.FloatField(db_column="fRatedEff", blank=True, null=True)
    rated_efficiency_unit = models.IntegerField(
        db_column="nRatedEffUnit", blank=True, null=True, choices=SHARED_EFFICIENCY_UNITS
    )
    boiler_capacity = models.FloatField(db_column="fBoilerCap", blank=True, null=True)
    chiller_capacity = models.FloatField(db_column="fChillerCap", blank=True, null=True)
    gshp_capacity = models.FloatField(db_column="fGndLoopCap", blank=True, null=True)
    gshp_pump_power = models.FloatField(db_column="fGndLoopPump", blank=True, null=True)

    units_served = models.IntegerField(db_column="nBlgLoopUnits", blank=True, null=True)
    loop_pump_power = models.FloatField(db_column="fBlgLoopPumpPwr", blank=True, null=True)

    distribution_type = models.IntegerField(
        db_column="nTerminalType", blank=True, null=True, choices=SHARED_DISTRIBUTION_TYPES
    )

    fan_coil_watts = models.FloatField(db_column="fFanCoil", blank=True, null=True)
    note = models.CharField(max_length=255, db_column="sNote", blank=True, null=True)

    heating_equipment_number = models.IntegerField(
        null=True, db_column="lHtgEqKey", help_text="Htg Equip"
    )
    cooling_equipment_number = models.IntegerField(
        null=True, db_column="lClgEqKey", help_text="Clg Equip"
    )

    gshp_number = models.IntegerField(null=True, db_column="lGshpEqKey", help_text="GSHP Equip")
    wlhp_number = models.IntegerField(null=True, db_column="lWlhpEqKey", help_text="WLHP Equip")
