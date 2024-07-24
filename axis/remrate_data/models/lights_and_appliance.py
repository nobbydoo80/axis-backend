"""RemRate Models suitable for use by Axis """

import logging

from django.db import models

from ..strings import (
    FUEL_TYPES,
    LIGHT_APP_LOCATIONS,
    LIGHT_APP_WASHER_EFFICIENCY_PRESETS,
    LIGHT_APP_WASHER_PRESETS,
    LIGHT_APP_DISHWASHER_PRESETS,
)
from ..utils import compare_sets

__author__ = "Steven Klass"
__date__ = "06/10/2019 11:03"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class LightsAndAppliance(models.Model):
    """LightApp - Lights and Appliances"""

    simulation = models.OneToOneField("Simulation", on_delete=models.CASCADE)
    building = models.OneToOneField("Building", on_delete=models.CASCADE)
    _result_number = models.IntegerField(db_column="lBldgRunNo")
    _building_number = models.IntegerField(db_column="lBldgNo")

    oven_fuel = models.IntegerField(null=True, db_column="FLAOVNFUEL", choices=FUEL_TYPES)
    rating_number = models.CharField(max_length=93, db_column="SLARATENO", blank=True)
    default_loads = models.BooleanField(default=False, db_column="NLAUSEDEF")
    refrigerator_kw_yr = models.FloatField(null=True, db_column="FLAREFKWH")

    dishwasher_energy_factor = models.FloatField(null=True, db_column="FLADISHWEF")
    dishwasher_location = models.IntegerField(
        blank=True, null=True, db_column="nLADishLoc", choices=LIGHT_APP_LOCATIONS
    )
    dishwasher_presets = models.IntegerField(
        blank=True, null=True, db_column="nLADishPre", choices=LIGHT_APP_DISHWASHER_PRESETS
    )
    shared_hot_water_equipment_number_for_dishwasher = models.IntegerField(
        blank=True, null=True, db_column="nLADishDhw"
    )
    dishwasher_electric_rate = models.FloatField(null=True, db_column="fLADishElec")
    dishwasher_gas_rate = models.FloatField(null=True, db_column="fLADishGas")
    dishwasher_gas_cost = models.FloatField(null=True, db_column="fLADishGCst")
    dishwasher_loads_per_week = models.IntegerField(blank=True, null=True, db_column="nLADishLoad")

    pct_florescent = models.FloatField(null=True, db_column="FLAFLRCENT")
    ceiling_fan_cfm_watt = models.FloatField(null=True, db_column="FLAFANCFM")
    ceiling_fan_count = models.IntegerField(blank=True, null=True, db_column="nLAFanCnt")

    pct_interior_cfl = models.FloatField(null=True, db_column="FLACFLCENT")
    pct_exterior_cfl = models.FloatField(null=True, db_column="FLACFLEXT")
    pct_garage_cfl = models.FloatField(null=True, db_column="FLACFLGAR")
    pct_interior_led = models.FloatField(null=True, db_column="FLALEDINT")
    pct_exterior_led = models.FloatField(null=True, db_column="FLALEDEXT")
    pct_garage_led = models.FloatField(null=True, db_column="FLALEDGAR")
    refrigerator_location = models.IntegerField(db_column="NLAREFLOC", choices=LIGHT_APP_LOCATIONS)
    dishwasher_capacity = models.FloatField(null=True, db_column="FLADISHWCAP")
    dishwasher_kw_yr = models.FloatField(null=True, db_column="FLADISHWYR")
    oven_induction = models.BooleanField(default=False, db_column="NLAOVNIND")
    oven_convection = models.BooleanField(default=False, db_column="NLAOVNCON")
    oven_location = models.IntegerField(
        blank=True, null=True, db_column="nLAOvnLoc", choices=LIGHT_APP_LOCATIONS
    )

    clothes_dryer_fuel = models.IntegerField(null=True, db_column="FLADRYFUEL", choices=FUEL_TYPES)
    clothes_dryer_location = models.IntegerField(db_column="NLADRYLOC", choices=LIGHT_APP_LOCATIONS)
    clothes_dryer_moisture_sensing = models.BooleanField(default=False, db_column="NLADRYMOIST")
    clothes_dryer_energy_factor = models.FloatField(null=True, db_column="FLADRYEF")
    clothes_dryer_modified_energy_factor = models.FloatField(null=True, db_column="FLADRYMEF")
    clothes_dryer_gas_energy_factor = models.FloatField(null=True, db_column="FLADRYGASEF")
    dwelling_units_per_dryer = models.IntegerField(blank=True, null=True, db_column="nLADryUnit")

    clothes_washer_location = models.IntegerField(
        db_column="NLAWASHLOC", choices=LIGHT_APP_LOCATIONS
    )
    clothes_washer_label_energy_rating = models.FloatField(null=True, db_column="FLAWASHLER")
    clothes_washer_capacity = models.FloatField(null=True, db_column="FLAWASHCAP")
    clothes_washer_electric_rate = models.FloatField(null=True, db_column="FLAWASHELEC")
    clothes_washer_gas_rate = models.FloatField(null=True, db_column="FLAWASHGAS")
    clothes_washer_gas_cost = models.FloatField(null=True, db_column="FLAWASHGCST")
    clothes_washer_efficiency = models.IntegerField(
        null=True, db_column="FLAWASHEFF", blank=True, choices=LIGHT_APP_WASHER_EFFICIENCY_PRESETS
    )
    clothes_washer_presets = models.IntegerField(
        blank=True, null=True, db_column="nLAWashPre", choices=LIGHT_APP_WASHER_PRESETS
    )
    dwelling_units_per_clothes_washer = models.IntegerField(
        blank=True, null=True, db_column="nLAWashUnit"
    )
    shared_hot_water_equipment_number_for_clothes_washer = models.IntegerField(
        blank=True, null=True, db_column="nLAWashDhw"
    )
    clothes_washer_iwf = models.FloatField(blank=True, null=True, db_column="fLAWashIWF")
    clothes_washer_loads_per_week = models.IntegerField(
        blank=True, null=True, db_column="nLAWashLoad"
    )

    def __str__(self):
        data = []

        if self.pct_interior_led:
            data.append("Interior LED: %s" % round(self.pct_interior_led, 2))
        elif self.pct_interior_cfl:
            data.append("Interior CFL: %s" % round(self.pct_interior_cfl, 2))
        elif self.pct_florescent:
            data.append("Florescent: %s" % round(self.pct_florescent, 2))

        if self.pct_exterior_led:
            data.append("Exterior LED: %s" % round(self.pct_exterior_led, 2))
        elif self.pct_exterior_cfl:
            data.append("Exterior CFL: %s" % round(self.pct_exterior_cfl, 2))

        if self.pct_garage_led:
            data.append("Garage LED: %s" % round(self.pct_garage_led, 2))
        elif self.pct_garage_cfl:
            data.append("Garage CFL: %s" % round(self.pct_garage_cfl, 2))

        return ", ".join(data) if data else "-"

    def compare_to_home_status(self, home_status, **kwargs):  # pylint: disable=unused-argument
        """Compares this to the home status"""
        items = [
            (self.pct_interior_cfl, kwargs.get("lighting_pct"), int),
            (self.pct_interior_cfl, kwargs.get("lighting_pct_2016"), int),
            (self.dishwasher_energy_factor, kwargs.get("dishwasher_ef"), int),
        ]

        if kwargs.get("refrigerator_conditioned_area") is not None:
            items.append(
                [
                    self.refrigerator_location,
                    1,
                    int,
                    kwargs.get("refrigerator_conditioned_area")[1],
                    "error",
                ]
            )
        if kwargs.get("clothes_dryer_conditioned_area") is not None:
            items.append(
                [
                    self.clothes_dryer_location,
                    1,
                    int,
                    kwargs.get("clothes_dryer_conditioned_area")[1],
                    "error",
                ]
            )

        match_items = []
        for fields in items:
            try:
                cmp1, cmp2, _type, label, warning_type = fields
            except ValueError:
                try:
                    cmp1, cmp2, _type, label = fields
                    warning_type = "warning"
                except ValueError:
                    cmp1, cmp2, _type = fields
                    # This is fugly did I really do this..
                    label = "Checklist: {}".format(cmp2[1] if cmp2 else "-")
                    cmp2 = cmp2[0] if cmp2 else None
                    warning_type = "warning"
            if cmp2 is None:
                continue
            match_items.append((cmp1, cmp2, _type, label, warning_type))
        return compare_sets(match_items)
