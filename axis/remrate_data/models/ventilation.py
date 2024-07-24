"""ventilation.py - Axis"""

__author__ = "Steven K"
__date__ = "7/22/21 11:16"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from django.db import models

from ..strings import INFILTRATION_TYPES

log = logging.getLogger(__name__)


class Ventilation(models.Model):
    simulation = models.ForeignKey("Simulation", on_delete=models.CASCADE)
    _result_number = models.IntegerField(db_column="lBldgRunNo")
    _source_building_number = models.IntegerField(db_column="lBldgNo")
    rating_number = models.CharField(max_length=31, db_column="sMVRateNo", blank=True)
    name = models.CharField(max_length=31, db_column="sMVName", blank=True, null=True)
    type = models.IntegerField(
        db_column="nMVType", blank=True, null=True, choices=INFILTRATION_TYPES
    )
    rate = models.FloatField(db_column="fMVRate", blank=True, null=True, help_text="Delivered CFM")
    hours_per_day = models.IntegerField(
        db_column="nMVHrsDay", blank=True, null=True, help_text="Hours/Day"
    )
    fan_power = models.FloatField(db_column="fMVFanPwr", blank=True, null=True)

    ashrae_recovery_efficiency = models.FloatField(db_column="fMVASRE", blank=True, null=True)
    atre_recovery_efficiency = models.FloatField(db_column="fMVATRE", blank=True, null=True)

    not_measured = models.IntegerField(db_column="nMVNotMsrd", blank=True, null=True)
    use_defaults = models.IntegerField(db_column="nMVWattDflt", blank=True, null=True)

    uses_ecm_fan = models.IntegerField(db_column="nMVFanMotor", blank=True, null=True)
    duct_system_number = models.IntegerField(db_column="nMVDuctNo", blank=True, null=True)
    shared_multi_family_system = models.IntegerField(db_column="nMVShrdMF", blank=True, null=True)

    heating_equipment_number = models.IntegerField(
        null=True, db_column="nMVHtgNo", help_text="Preconditioning Htg Equip"
    )
    cooling_equipment_number = models.IntegerField(
        null=True, db_column="nMVClgNo", help_text="Preconditioning Clg Equip"
    )

    total_shared_system_cfm = models.FloatField(db_column="fMVShrdCFM", blank=True, null=True)

    outside_air_pct = models.FloatField(db_column="fMVOAPct", blank=True, null=True)
    recirculated_air_pct = models.FloatField(db_column="fMVReCirc", blank=True, null=True)
