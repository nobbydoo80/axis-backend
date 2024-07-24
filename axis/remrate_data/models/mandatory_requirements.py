"""RemRate Models suitable for use by Axis """

import logging

from django.db import models

__author__ = "Steven Klass"
__date__ = "06/10/2019 11:03"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class MandatoryRequirements(models.Model):
    """MandReq - Mandatory Requirements"""

    simulation = models.OneToOneField("Simulation", on_delete=models.CASCADE)
    building = models.OneToOneField("Building", on_delete=models.CASCADE)
    _result_number = models.IntegerField(db_column="lBldgRunNo")
    _building_number = models.IntegerField(db_column="lBldgNo")

    verified_iecc04 = models.BooleanField(default=False, db_column="nMRIECC04")
    verified_iecc06 = models.BooleanField(default=False, db_column="nMRIECC06")
    verified_iecc09 = models.BooleanField(default=False, db_column="nMRIECC09")
    verified_energy_star_v2_thermal_bypass_checklist = models.BooleanField(
        default=False, db_column="nMRESV2TBC"
    )
    verified_energy_star_v2_products = models.BooleanField(default=False, db_column="nMRESV2PRD")
    verified_energy_star_v3_thermal_enclosure_checklist = models.BooleanField(
        default=False, db_column="nMRESV3TEC"
    )
    verified_energy_star_v3_hvac_contractor_checklist = models.BooleanField(
        default=False, db_column="nMRESV3HC"
    )
    verified_energy_star_v3_hvac_rater_checklist = models.BooleanField(
        default=False, db_column="nMRESV3HR"
    )
    verified_energy_star_v3_water_management_checklist = models.BooleanField(
        default=False, db_column="nMRESV3WM"
    )
    verified_energy_star_v3_indoor_air_plus = models.BooleanField(
        default=False, db_column="nMRESV3AP"
    )
    verified_energy_star_v3_refrigerators = models.BooleanField(
        default=False, db_column="nMRESV3RF"
    )
    verified_energy_star_v3_ceiling_fans = models.BooleanField(default=False, db_column="nMRESV3CF")
    verified_energy_star_v3_exhaust_fans = models.BooleanField(default=False, db_column="nMRESV3EF")
    verified_energy_star_v3_dishwashers = models.BooleanField(default=False, db_column="nMRESV3DW")
    energy_star_v3_refrigerators = models.IntegerField(db_column="nMRESV3NRF")
    energy_star_v3_ceiling_fans = models.IntegerField(db_column="nMRESV3NCF")
    energy_star_v3_exhaust_fans = models.IntegerField(db_column="nMRESV3NEF")
    energy_star_v3_dishwashers = models.IntegerField(db_column="nMRESV3NDW")
    rating_number = models.CharField(null=True, max_length=93, db_column="sMRRateNo", blank=True)
    verified_iecc10_ny = models.BooleanField(default=False, db_column="nMRIECCNY")
    energy_star_v3basement_qualifies_for_saf_exclusion = models.BooleanField(
        default=False, db_column="nMRESV3SAF"
    )
    energy_star_v3_basement_floor_area = models.FloatField(db_column="fMRESV3BFA")
    energy_star_v3_basement_bedrooms = models.BooleanField(default=False, db_column="nMRESV3NBB")
    verified_iecc12 = models.BooleanField(default=False, db_column="nMRIECC12")
    meets_florida_requirements = models.BooleanField(default=False, db_column="NMRFLORIDA")
    energy_star_v3_slab_exempt = models.BooleanField(default=False, db_column="NMRESV3SLAB")
    verified_iecc15 = models.BooleanField(null=True, blank=True, db_column="NMRIECC15")
    energy_star_version_to_qualify = models.CharField(
        null=True, max_length=31, db_column="sMResQual4", blank=True
    )

    verified_iecc18 = models.BooleanField(null=True, db_column="NMRIECC18", blank=True)
    verified_iecc15_mi = models.BooleanField(null=True, db_column="NMRIECCMI", blank=True)

    energy_star_mf_clothes_washer_no_ES_option = models.IntegerField(
        null=True, db_column="NMRESMFWSHR", blank=True
    )
    energy_star_mf_clothes_dryer_no_ES_option = models.IntegerField(
        null=True, db_column="NMRESMFDRYR", blank=True
    )
    energy_star_mf_uses_class_aw_windows = models.IntegerField(
        null=True, db_column="NMRESMFWIN", blank=True
    )
    verified_iecc18_nc = models.BooleanField(null=True, db_column="NMRIECCNC", blank=True)
    verified_ngbs_2015 = models.BooleanField(null=True, db_column="nMRNGBS15", blank=True)

    verified_iecc21 = models.BooleanField(null=True, db_column="NMRIECC21", blank=True)
