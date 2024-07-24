"""RemRate Models suitable for use by Axis """

import logging

from django.db import models

from ..strings import DOE_CHALLENGE_OPTIONAL

__author__ = "Steven Klass"
__date__ = "06/10/2019 11:03"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class DOEChallenge(models.Model):
    """DOEChallenge - DOE Challenge Home"""

    simulation = models.OneToOneField("Simulation", on_delete=models.CASCADE)
    building = models.OneToOneField("Building", on_delete=models.CASCADE)
    _result_number = models.IntegerField(db_column="lBldgRunNo")
    _building_number = models.IntegerField(db_column="lBldgNo")
    home_builder_id = models.CharField(max_length=93, db_column="sDCBldrID", blank=True)
    verified_fenestration_requirements = models.BooleanField(
        null=True, db_column="nDCFenstrtn", blank=True
    )
    verified_insulation_requirements = models.BooleanField(
        null=True, db_column="nDCInsul", blank=True
    )
    verified_duct_location_requirements = models.BooleanField(
        null=True, db_column="nDCDuctLoc", blank=True
    )
    verified_appliance_requirements = models.BooleanField(
        null=True, db_column="nDCAppl", blank=True
    )
    verified_lighting_requirements = models.BooleanField(
        null=True, db_column="nDCLighting", blank=True
    )
    verified_fan_efficiency_requirements = models.BooleanField(
        null=True, db_column="nDCFanEff", blank=True
    )
    verified_indoor_air_quality_requirements = models.BooleanField(
        null=True, db_column="nDCAirQual", blank=True
    )
    verified_renewable_solar_electric_requirements = models.BooleanField(
        null=True, db_column="nDCSolarE", blank=True
    )
    verified_renewable_solar_hot_water_requirements = models.BooleanField(
        null=True, db_column="nDCSolarHW", blank=True
    )
    verified_water_efficiency = models.BooleanField(null=True, db_column="nDCWaterEff", blank=True)
    optional_indoor_air_plus = models.IntegerField(
        null=True, db_column="nDCAirPlus", blank=True, choices=DOE_CHALLENGE_OPTIONAL
    )
    optional_water_sense = models.IntegerField(
        null=True, db_column="nDCWtrSense", blank=True, choices=DOE_CHALLENGE_OPTIONAL
    )
    optional_ibhs_fortified = models.IntegerField(
        null=True, db_column="nDCIBHS", blank=True, choices=DOE_CHALLENGE_OPTIONAL
    )
    optional_quality_management_guidelines = models.IntegerField(
        null=True, db_column="nDCMGMT", blank=True, choices=DOE_CHALLENGE_OPTIONAL
    )
    optional_utility_bill_waiver = models.IntegerField(
        null=True, db_column="nDCWaiver", blank=True, choices=DOE_CHALLENGE_OPTIONAL
    )
    rating_number = models.CharField(null=True, max_length=93, db_column="sDCRateNo", blank=True)
    passive_home_certified = models.BooleanField(null=True, db_column="nDCPassiveHome", blank=True)
