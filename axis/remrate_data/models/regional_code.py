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


class RegionalCode(models.Model):
    """Regional Code Results"""

    simulation = models.OneToOneField("Simulation", on_delete=models.CASCADE)
    _result_number = models.IntegerField(db_column="lBldgRunNo", verbose_name="Key to building run")
    rating_number = models.CharField(max_length=93, db_column="SRATENO", blank=True, null=True)
    nv_energy_plus_rebate = models.FloatField(db_column="fNVRebate", blank=True, null=True)

    ny_eccc_2010_reference_heating_consumption = models.FloatField(
        db_column="fNYECRHCn", blank=True, null=True
    )
    ny_eccc_2010_reference_cooling_consumption = models.FloatField(
        db_column="fNYECRCCn", blank=True, null=True
    )
    ny_eccc_2010_reference_hot_water_consumption = models.FloatField(
        db_column="fNYECRDCN", blank=True, null=True
    )
    ny_eccc_2010_reference_lights_appliance_consumption = models.FloatField(
        db_column="fNYECRLACn", blank=True, null=True
    )
    ny_eccc_2010_reference_photo_voltaic_consumption = models.FloatField(
        db_column="fNYECRPVCn", blank=True, null=True
    )
    ny_eccc_2010_reference_total_consumption = models.FloatField(
        db_column="fNYECRTCn", blank=True, null=True
    )
    ny_eccc_2010_designed_heating_consumption = models.FloatField(
        db_column="fNYECDHCn", blank=True, null=True
    )
    ny_eccc_2010_designed_cooling_consumption = models.FloatField(
        db_column="fNYECDCCn", blank=True, null=True
    )
    ny_eccc_2010_designed_hot_water_consumption = models.FloatField(
        db_column="fNYECDDCN", blank=True, null=True
    )
    ny_eccc_2010_designed_lights_appliance_consumption = models.FloatField(
        db_column="fNYECDLACn", blank=True, null=True
    )
    ny_eccc_2010_designed_photo_voltaic_consumption = models.FloatField(
        db_column="fNYECDPVCn", blank=True, null=True
    )
    ny_eccc_2010_designed_total_consumption = models.FloatField(
        db_column="fNYECDTCn", blank=True, null=True
    )
    passes_ny_eccc_2010_consumption_compliance = models.BooleanField(
        null=True, default=False, db_column="bNYECC"
    )

    nv_ecc_reference_heating_consumption = models.FloatField(
        db_column="fNVECRHCn", blank=True, null=True
    )
    nv_ecc_reference_cooling_consumption = models.FloatField(
        db_column="fNVECRCCn", blank=True, null=True
    )
    nv_ecc_reference_hot_water_consumption = models.FloatField(
        db_column="fNVECRDCN", blank=True, null=True
    )
    nv_ecc_reference_lights_appliance_consumption = models.FloatField(
        db_column="fNVECRLACn", blank=True, null=True
    )
    nv_ecc_reference_photo_voltaic_consumption = models.FloatField(
        db_column="fNVECRPVCn", blank=True, null=True
    )
    nv_ecc_reference_total_consumption = models.FloatField(
        db_column="fNVECRTCn", blank=True, null=True
    )
    nv_ecc_designed_heating_consumption = models.FloatField(
        db_column="fNVECDHCn", blank=True, null=True
    )
    nv_ecc_designed_cooling_consumption = models.FloatField(
        db_column="fNVECDCCn", blank=True, null=True
    )
    nv_ecc_designed_hot_water_consumption = models.FloatField(
        db_column="fNVECDDCN", blank=True, null=True
    )
    nv_ecc_designed_lights_appliance_consumption = models.FloatField(
        db_column="fNVECDLACn", blank=True, null=True
    )
    nv_ecc_designed_photo_voltaic_consumption = models.FloatField(
        db_column="fNVECDPVCn", blank=True, null=True
    )
    nv_ecc_designed_total_consumption = models.FloatField(
        db_column="fNVECDTCn", blank=True, null=True
    )
    passes_nv_ecc_consumption_compliance = models.BooleanField(
        null=True, default=False, db_column="bNVECC"
    )

    nc_2012_reference_heating_cost = models.FloatField(db_column="fNCRHCT", blank=True, null=True)
    nc_2012_reference_cooling_cost = models.FloatField(db_column="fNCRCCT", blank=True, null=True)
    nc_2012_reference_hot_water_cost = models.FloatField(db_column="fNCRDCT", blank=True, null=True)
    nc_2012_reference_lights_appliance_cost = models.FloatField(
        db_column="fNCRLACT", blank=True, null=True
    )
    nc_2012_reference_photo_voltaic_cost = models.FloatField(
        db_column="fNCRPVCT", blank=True, null=True
    )
    nc_2012_reference_service_cost = models.FloatField(db_column="fNCRSVCT", blank=True, null=True)
    nc_2012_reference_total_cost = models.FloatField(db_column="fNCRTCT", blank=True, null=True)
    nc_2012_designed_heating_cost = models.FloatField(db_column="fNCDHCT", blank=True, null=True)
    nc_2012_designed_cooling_cost = models.FloatField(db_column="fNCDCCT", blank=True, null=True)
    nc_2012_designed_hot_water_cost = models.FloatField(db_column="fNCDDCT", blank=True, null=True)
    nc_2012_designed_lights_appliance_cost = models.FloatField(
        db_column="fNCDLACT", blank=True, null=True
    )
    nc_2012_designed_photo_voltaic_cost = models.FloatField(
        db_column="fNCDPVCT", blank=True, null=True
    )
    nc_2012_designed_service_cost = models.FloatField(db_column="fNCDSVCT", blank=True, null=True)
    nc_2012_designed_total_cost = models.FloatField(db_column="fNCDTCT", blank=True, null=True)
    passes_nc_2012_cost_compliance = models.BooleanField(
        null=True, default=False, db_column="bNCMeetCT"
    )

    nc_2012_reference_overall_ua = models.FloatField(db_column="fNCRUA", blank=True, null=True)
    nc_2012_designed_overall_ua = models.FloatField(db_column="fNCDUA", blank=True, null=True)
    nc_2012_passing_ducts = models.BooleanField(null=True, default=False, db_column="bNCDctPass")
    passes_nc_2012_overall_ua_compliance = models.BooleanField(
        null=True, default=False, db_column="bNCUAPass"
    )
    passes_nc_2012_code = models.BooleanField(null=True, default=False, db_column="bNCPass")

    nc_hero_2012_reference_heating_cost = models.FloatField(
        db_column="fNCHRHCT", blank=True, null=True
    )
    nc_hero_2012_reference_cooling_cost = models.FloatField(
        db_column="fNCHRCCT", blank=True, null=True
    )
    nc_hero_2012_reference_hot_water_cost = models.FloatField(
        db_column="fNCHRDCT", blank=True, null=True
    )
    nc_hero_2012_reference_lights_appliance_cost = models.FloatField(
        db_column="fNCHRLACT", blank=True, null=True
    )
    nc_hero_2012_reference_photo_voltaic_cost = models.FloatField(
        db_column="fNCHRPVCT", blank=True, null=True
    )
    nc_hero_2012_reference_service_cost = models.FloatField(
        db_column="fNCHRSVCT", blank=True, null=True
    )
    nc_hero_2012_reference_total_cost = models.FloatField(
        db_column="fNCHRTCT", blank=True, null=True
    )
    nc_hero_2012_designed_heating_cost = models.FloatField(
        db_column="fNCHDHCT", blank=True, null=True
    )
    nc_hero_2012_designed_cooling_cost = models.FloatField(
        db_column="fNCHDCCT", blank=True, null=True
    )
    nc_hero_2012_designed_hot_water_cost = models.FloatField(
        db_column="fNCHDDCT", blank=True, null=True
    )
    nc_hero_2012_designed_lights_appliance_cost = models.FloatField(
        db_column="fNCHDLACT", blank=True, null=True
    )
    nc_hero_2012_designed_photo_voltaic_cost = models.FloatField(
        db_column="fNCHDPVCT", blank=True, null=True
    )
    nc_hero_2012_designed_service_cost = models.FloatField(
        db_column="fNCHDSVCT", blank=True, null=True
    )
    nc_hero_2012_designed_total_cost = models.FloatField(
        db_column="fNCHDTCT", blank=True, null=True
    )
    passes_nc_hero_2012_cost_compliance = models.BooleanField(
        null=True, default=False, db_column="bNCHMeetCT"
    )

    nc_hero_2012_reference_overall_ua = models.FloatField(
        db_column="fNCHRUA", blank=True, null=True
    )
    nc_hero_2012_designed_overall_ua = models.FloatField(db_column="fNCHDUA", blank=True, null=True)
    nc_hero_2012_passing_ducts = models.BooleanField(
        null=True, default=False, db_column="bNCHDctPass"
    )
    passes_nc_hero_2012_overall_ua_compliance = models.BooleanField(
        null=True, default=False, db_column="bNCHUAPass"
    )
    passes_nc_hero_2012_code = models.BooleanField(null=True, default=False, db_column="bNCHPass")

    ny_eccc_2016_reference_heating_cost = models.FloatField(
        db_column="FNYRHCT", null=True, blank=True
    )
    ny_eccc_2016_reference_cooling_cost = models.FloatField(
        db_column="FNYRCCT", null=True, blank=True
    )
    ny_eccc_2016_reference_hot_water_cost = models.FloatField(
        db_column="FNYRDCT", null=True, blank=True
    )
    ny_eccc_2016_reference_lights_appliance_cost = models.FloatField(
        db_column="FNYRLACT", null=True, blank=True
    )
    ny_eccc_2016_reference_photo_voltaic_cost = models.FloatField(
        db_column="FNYRPVCT", null=True, blank=True
    )
    ny_eccc_2016_reference_service_cost = models.FloatField(
        db_column="FNYRSVCT", null=True, blank=True
    )
    ny_eccc_2016_reference_total_cost = models.FloatField(
        db_column="FNYRTCT", null=True, blank=True
    )
    ny_eccc_2016_designed_heating_cost = models.FloatField(
        db_column="FNYDHCT", null=True, blank=True
    )
    ny_eccc_2016_designed_cooling_cost = models.FloatField(
        db_column="FNYDCCT", null=True, blank=True
    )
    ny_eccc_2016_designed_hot_water_cost = models.FloatField(
        db_column="FNYDDCT", null=True, blank=True
    )
    ny_eccc_2016_designed_lights_appliance_cost = models.FloatField(
        db_column="FNYDLACT", null=True, blank=True
    )
    ny_eccc_2016_designed_photo_voltaic_cost = models.FloatField(
        db_column="FNYDPVCT", null=True, blank=True
    )
    ny_eccc_2016_designed_service_cost = models.FloatField(
        db_column="FNYDSVCT", null=True, blank=True
    )
    ny_eccc_2016_designed_total_cost = models.FloatField(db_column="FNYDTCT", null=True, blank=True)
    passes_ny_eccc_2016_cost_compliance = models.BooleanField(
        null=True, default=False, db_column="BNYMEETCT", blank=True
    )
    ny_eccc_2016_reference_overall_ua = models.FloatField(db_column="FNYRUA", null=True, blank=True)
    ny_eccc_2016_designed_overall_ua = models.FloatField(db_column="FNYDUA", null=True, blank=True)
    ny_eccc_2016_passing_ducts = models.BooleanField(
        null=True, default=False, db_column="BNYDCTPASS", blank=True
    )
    passes_ny_eccc_2016_overall_ua_compliance = models.BooleanField(
        null=True, default=False, db_column="BNYUAPASS", blank=True
    )
    passes_ny_eccc_2016_code = models.BooleanField(
        null=True, default=False, db_column="BNYPASS", blank=True
    )

    ny_design_costing = models.FloatField(db_column="FNYDMVCT", null=True, blank=True)
    ny_reference_costing = models.FloatField(db_column="FNYRMVCT", null=True, blank=True)
