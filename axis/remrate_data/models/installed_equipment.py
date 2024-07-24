"""RemRate Models suitable for use by Axis """


import logging

from django.db import models

from ..managers import InstalledEquipmentManager
from ..strings import SYSTEM_TYPES, MECHANICAL_EQUIP_LOCATIONS

__author__ = "Steven Klass"
__date__ = "06/10/2019 11:03"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class InstalledEquipment(models.Model):
    """Installed Equipment"""

    simulation = models.ForeignKey("Simulation", on_delete=models.CASCADE)
    building = models.ForeignKey("Building", on_delete=models.CASCADE)
    heater = models.ForeignKey("Heater", on_delete=models.CASCADE, null=True)
    ground_source_heat_pump = models.ForeignKey(
        "GroundSourceHeatPump", on_delete=models.CASCADE, null=True
    )
    dual_fuel_heat_pump = models.ForeignKey("DualFuelHeatPump", on_delete=models.CASCADE, null=True)
    air_conditioner = models.ForeignKey("AirConditioner", on_delete=models.CASCADE, null=True)
    hot_water_heater = models.ForeignKey("HotWaterHeater", on_delete=models.CASCADE, null=True)
    air_source_heat_pump = models.ForeignKey(
        "AirSourceHeatPump", on_delete=models.CASCADE, null=True
    )
    integrated_space_water_heater = models.ForeignKey(
        "IntegratedSpaceWaterHeater", on_delete=models.CASCADE, null=True
    )
    dehumidifier = models.ForeignKey("Dehumidifier", on_delete=models.CASCADE, null=True)
    shared_equipment = models.ForeignKey("SharedEquipment", on_delete=models.CASCADE, null=True)

    _source_equipment_number = models.IntegerField(db_column="lEIEINo")
    _result_number = models.IntegerField(db_column="lBldgRunNo")
    _building_number = models.IntegerField(db_column="lBldgNo")

    _heater_number = models.IntegerField(null=True, db_column="lEIHETNo", blank=True)

    _ground_source_heat_pump_number = models.IntegerField(
        null=True, db_column="lEIGSTNo", blank=True
    )
    _dual_fuel_heat_pump_number = models.IntegerField(null=True, db_column="lEIDFTNo", blank=True)
    _air_conditioner_number = models.IntegerField(null=True, db_column="lEICLTNo", blank=True)
    _hot_water_heater_number = models.IntegerField(null=True, db_column="lEIDHTNo", blank=True)
    _air_source_heat_pump_number = models.IntegerField(null=True, db_column="lEIASTNO", blank=True)
    _integrated_space_water_heater_number = models.IntegerField(
        null=True, db_column="lEIHDTNO", blank=True
    )
    _dehumidifier_number = models.IntegerField(null=True, db_column="lDhuEqKey", blank=True)
    _shared_equipment_number = models.IntegerField(null=True, db_column="lSharedEqKey", blank=True)

    system_type = models.IntegerField(null=True, db_column="nEISysType", choices=SYSTEM_TYPES)
    performance_adjustment_pct = models.FloatField(null=True, db_column="fEIPerAdj", blank=True)
    location = models.IntegerField(
        null=True, db_column="nEILoc", choices=MECHANICAL_EQUIP_LOCATIONS
    )
    heating_load_served_pct = models.FloatField(null=True, db_column="fEIHLdSrv")
    air_conditioner_load_served_pct = models.FloatField(null=True, db_column="fEICLdSrv")
    hot_water_heater_load_served_pct = models.FloatField(null=True, db_column="fEIDLdSrv")
    qty_installed = models.IntegerField(null=True, db_column="nEINoUnits")

    distribution_system_efficiency = models.FloatField(null=True, db_column="fEIDSE", blank=True)

    clothes_washer_load_served_pct = models.FloatField(
        null=True, db_column="fCWLoadSrvd", blank=True
    )
    dishwasher_load_served_pct = models.FloatField(null=True, db_column="fDWLoadSrvd", blank=True)
    dehumidifier_load_served_pct = models.FloatField(
        null=True, db_column="fDhuLoadSrvd", blank=True
    )
    mechanical_ventilation_heating_load_served_pct = models.FloatField(
        null=True, db_column="fMVHtgLoadSrvd", blank=True
    )
    mechanical_ventilation_cooling_load_served_pct = models.FloatField(
        null=True, db_column="fMVClgLoadSrvd", blank=True
    )
    hot_water_units_served = models.IntegerField(null=True, db_column="nDwellUnitsDhw", blank=True)
    preconditioned_shared_mechanical_ventilation = models.IntegerField(
        null=True, db_column="nPrecondSharedMV", blank=True
    )

    objects = InstalledEquipmentManager()

    class Meta:
        ordering = ("simulation", "heater", "air_conditioner", "ground_source_heat_pump")

    def __str__(self):
        return "{},  {} [{}] Qty: {} Serving: {}".format(
            self.get_system_type_display(),
            self.get_equipment(),
            self.get_location_display(),
            self.qty_installed,
            self.pct_served(),
        )

    def basic_display(self):
        """A very simple display"""
        return "%s, (%s) Qty: %s Serving: %s" % (
            self.get_system_type_display(),
            self.get_location_display(),
            self.qty_installed,
            self.pct_served(),
        )

    # pylint: disable=inconsistent-return-statements
    def get_equipment(self):
        """Get the equipment"""
        equip = [
            "heater",
            "ground_source_heat_pump",
            "dual_fuel_heat_pump",
            "air_conditioner",
            "hot_water_heater",
            "air_source_heat_pump",
            "integrated_space_water_heater",
            "dehumidifier",
            "shared_equipment",
        ]
        for equipment in equip:
            if getattr(self, equipment) is not None:
                return getattr(self, equipment)

    def pct_served(self):
        """Get the systems percentage servied"""
        if self.system_type in [1]:
            return "{}% heating".format(
                round(self.heating_load_served_pct, 1)
                if self.heating_load_served_pct is not None
                else 0
            )
        elif self.system_type in [2]:
            return "{}% cooling".format(
                round(self.air_conditioner_load_served_pct, 1)
                if self.air_conditioner_load_served_pct is not None
                else 0
            )
        elif self.system_type in [3]:
            return "{}% hot water".format(
                round(self.hot_water_heater_load_served_pct, 1)
                if self.hot_water_heater_load_served_pct is not None
                else 0
            )
        else:
            ans = []
            if self.heating_load_served_pct:
                ans.append("{}% heating".format(round(self.heating_load_served_pct, 1)))
            if self.air_conditioner_load_served_pct:
                ans.append("{}% cooling".format(round(self.air_conditioner_load_served_pct, 1)))
            if self.hot_water_heater_load_served_pct:
                ans.append("{}% hot water".format(round(self.hot_water_heater_load_served_pct, 1)))
            return ", ".join(ans) if ans else "Nothing."
