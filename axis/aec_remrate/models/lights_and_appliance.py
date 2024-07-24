"""Django AEC Models - Theses are the source data coming in on the rate database."""


import logging

from django.db import models

from axis.remrate_data.strings import FUEL_TYPES

__author__ = "Steven Klass"
__date__ = "06/09/2019 13:51"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class LightsAndAppliance(models.Model):
    """Lights and Appliances"""

    result_number = models.IntegerField(null=True, db_column="LBLDGRUNNO", blank=True)
    building_number = models.IntegerField(db_column="LBLDGNO")
    oven_fuel = models.IntegerField(
        null=True, db_column="FLAOVNFUEL", choices=FUEL_TYPES, blank=True
    )
    clothes_dryer_fuel = models.IntegerField(
        null=True, db_column="FLADRYFUEL", choices=FUEL_TYPES, blank=True
    )
    refrigerator_kw_yr = models.FloatField(null=True, db_column="FLAREFKWH", blank=True)
    dishwasher_energy_factor = models.FloatField(null=True, db_column="FLADISHWEF", blank=True)
    ceiling_fan_cfm_watt = models.FloatField(null=True, db_column="FLAFANCFM", blank=True)
    pct_florescent = models.FloatField(null=True, db_column="FLAFLRCENT", blank=True)
    pct_interior_cfl = models.FloatField(null=True, db_column="FLACFLCENT", blank=True)
    pct_exterior_cfl = models.FloatField(null=True, db_column="FLACFLEXT", blank=True)
    pct_garage_cfl = models.FloatField(null=True, db_column="FLACFLGAR", blank=True)
    clothes_dryer_energy_factor = models.FloatField(null=True, db_column="FLADRYEF", blank=True)
    clothes_washer_ler = models.FloatField(null=True, db_column="FLAWASHLER", blank=True)
    clothes_washer_capacity = models.FloatField(null=True, db_column="FLAWASHCAP", blank=True)

    clothes_washer_efficiency = models.FloatField(null=True, db_column="FLAWASHEFF", blank=True)
    pct_interior_led = models.FloatField(null=True, db_column="FLALEDINT")
    pct_exterior_led = models.FloatField(null=True, db_column="FLALEDEXT")
    pct_garage_led = models.FloatField(null=True, db_column="FLALEDGAR")

    # -- Not Used --
    slarateno = models.CharField(max_length=93, db_column="SLARATENO", blank=True)
    nlausedef = models.FloatField(null=True, db_column="NLAUSEDEF", blank=True)
    nlarefloc = models.IntegerField(db_column="NLAREFLOC")
    fladishwcap = models.FloatField(null=True, db_column="FLADISHWCAP", blank=True)
    fladishwyr = models.FloatField(null=True, db_column="FLADISHWYR", blank=True)
    nlaovnind = models.IntegerField(db_column="NLAOVNIND")
    nlaovncon = models.IntegerField(db_column="NLAOVNCON")
    nladryloc = models.IntegerField(db_column="NLADRYLOC")
    nladrymoist = models.IntegerField(db_column="NLADRYMOIST")
    fladrymef = models.FloatField(null=True, db_column="FLADRYMEF", blank=True)
    fladrygasef = models.FloatField(null=True, db_column="FLADRYGASEF", blank=True)
    nlawashloc = models.IntegerField(db_column="NLAWASHLOC")
    flawashelec = models.FloatField(null=True, db_column="FLAWASHELEC", blank=True)
    flawashgas = models.FloatField(null=True, db_column="FLAWASHGAS", blank=True)
    flawashgcst = models.FloatField(null=True, db_column="FLAWASHGCST", blank=True)

    number_fans = models.IntegerField(blank=True, null=True, db_column="nLAFanCnt")
    oven_location = models.IntegerField(blank=True, null=True, db_column="nLAOvnLoc")

    clothes_washer_presets = models.IntegerField(blank=True, null=True, db_column="nLAWashPre")
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

    dishwasher_location = models.IntegerField(blank=True, null=True, db_column="nLADishLoc")
    dishwasher_presets = models.IntegerField(blank=True, null=True, db_column="nLADishPre")
    shared_hot_water_equipment_number_for_dishwasher = models.IntegerField(
        blank=True, null=True, db_column="nLADishDhw"
    )
    dishwasher_electric_rate = models.FloatField(null=True, db_column="fLADishElec")
    dishwasher_gas_rate = models.FloatField(null=True, db_column="fLADishGas")
    dishwasher_gas_cost = models.FloatField(null=True, db_column="fLADishGCst")
    dishwasher_loads_per_week = models.IntegerField(blank=True, null=True, db_column="nLADishLoad")

    dwelling_units_per_dryer = models.IntegerField(blank=True, null=True, db_column="nLADryUnit")

    class Meta:
        db_table = "LightApp"
        managed = False
