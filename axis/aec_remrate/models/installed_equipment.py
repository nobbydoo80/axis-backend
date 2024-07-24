"""Django AEC Models - Theses are the source data coming in on the rate database."""


import logging

from django.db import models

from axis.remrate_data.strings import SYSTEM_TYPES, MECHANICAL_EQUIP_LOCATIONS

__author__ = "Steven Klass"
__date__ = "06/09/2019 13:51"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class InstalledEquipment(models.Model):
    """Installed Equipment"""

    equipment_number = models.IntegerField(primary_key=True, db_column="LEIEINO")
    result_number = models.IntegerField(null=True, db_column="LBLDGRUNNO", blank=True)
    building_number = models.IntegerField(db_column="LBLDGNO")
    heater_number = models.IntegerField(null=True, db_column="LEIHETNO", blank=True)

    ground_source_heat_pump_number = models.IntegerField(
        null=True, db_column="LEIGSTNO", blank=True
    )
    dual_fuel_heat_pump_number = models.IntegerField(null=True, db_column="LEIDFTNO", blank=True)
    air_conditioner_number = models.IntegerField(null=True, db_column="LEICLTNO", blank=True)
    hot_water_heater_number = models.IntegerField(null=True, db_column="LEIDHTNO", blank=True)
    air_source_heat_pump_number = models.IntegerField(null=True, db_column="LEIASTNO", blank=True)
    integrated_space_water_heater_number = models.IntegerField(
        null=True, db_column="LEIHDTNO", blank=True
    )
    dehumidifier_number = models.IntegerField(null=True, db_column="lDhuEqKey", blank=True)
    shared_equipment_number = models.IntegerField(null=True, db_column="lSharedEqKey", blank=True)

    system_type = models.IntegerField(null=True, db_column="NEISYSTYPE", choices=SYSTEM_TYPES)

    performance_adjustment_pct = models.FloatField(null=True, db_column="FEIPERADJ", blank=True)
    location = models.IntegerField(
        null=True, db_column="NEILOC", choices=MECHANICAL_EQUIP_LOCATIONS, blank=True
    )

    heating_load_served_pct = models.FloatField(null=True, db_column="FEIHLDSRV", blank=True)
    air_conditioner_load_served_pct = models.FloatField(
        null=True, db_column="FEICLDSRV", blank=True
    )
    hot_water_heater_load_served_pct = models.FloatField(
        null=True, db_column="FEIDLDSRV", blank=True
    )
    qty_installed = models.IntegerField(null=True, db_column="NEINOUNITS", blank=True)

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

    class Meta:
        db_table = "EqInst"
        managed = False
