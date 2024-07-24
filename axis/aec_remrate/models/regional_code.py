"""Django AEC Models - Theses are the source data coming in on the rate database."""


import logging

from django.db import models

__author__ = "Steven Klass"
__date__ = "06/09/2019 13:51"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class RegionalCode(models.Model):
    """Results of local regional code results"""

    result_number = models.IntegerField(db_column="lBldgRunNo", verbose_name="Key to building run")
    rating_number = models.CharField(max_length=93, db_column="SRATENO", blank=True)
    nv_energy_plus_rebate = models.FloatField(db_column="fNVRebate")

    ny_eccc_2010_reference_heating_consumption = models.FloatField(db_column="fNYECRHCn")
    ny_eccc_2010_reference_cooling_consumption = models.FloatField(db_column="fNYECRCCn")
    ny_eccc_2010_reference_hot_water_consumption = models.FloatField(db_column="fNYECRDCN")
    ny_eccc_2010_reference_lights_appliance_consumption = models.FloatField(db_column="fNYECRLACn")
    ny_eccc_2010_reference_photo_voltaic_consumption = models.FloatField(db_column="fNYECRPVCn")
    ny_eccc_2010_reference_total_consumption = models.FloatField(db_column="fNYECRTCn")
    ny_eccc_2010_designed_heating_consumption = models.FloatField(db_column="fNYECDHCn")
    ny_eccc_2010_designed_cooling_consumption = models.FloatField(db_column="fNYECDCCn")
    ny_eccc_2010_designed_hot_water_consumption = models.FloatField(db_column="fNYECDDCN")
    ny_eccc_2010_designed_lights_appliance_consumption = models.FloatField(db_column="fNYECDLACn")
    ny_eccc_2010_designed_photo_voltaic_consumption = models.FloatField(db_column="fNYECDPVCn")
    ny_eccc_2010_designed_total_consumption = models.FloatField(db_column="fNYECDTCn")
    passes_ny_eccc_2010_consumption_compliance = models.BooleanField(
        default=False, db_column="bNYECC"
    )

    nv_ecc_reference_heating_consumption = models.FloatField(db_column="fNVECRHCn")
    nv_ecc_reference_cooling_consumption = models.FloatField(db_column="fNVECRCCn")
    nv_ecc_reference_hot_water_consumption = models.FloatField(db_column="fNVECRDCN")
    nv_ecc_reference_lights_appliance_consumption = models.FloatField(db_column="fNVECRLACn")
    nv_ecc_reference_photo_voltaic_consumption = models.FloatField(db_column="fNVECRPVCn")
    nv_ecc_reference_total_consumption = models.FloatField(db_column="fNVECRTCn")
    nv_ecc_designed_heating_consumption = models.FloatField(db_column="fNVECDHCn")
    nv_ecc_designed_cooling_consumption = models.FloatField(db_column="fNVECDCCn")
    nv_ecc_designed_hot_water_consumption = models.FloatField(db_column="fNVECDDCN")
    nv_ecc_designed_lights_appliance_consumption = models.FloatField(db_column="fNVECDLACn")
    nv_ecc_designed_photo_voltaic_consumption = models.FloatField(db_column="fNVECDPVCn")
    nv_ecc_designed_total_consumption = models.FloatField(db_column="fNVECDTCn")
    passes_nv_ecc_consumption_compliance = models.BooleanField(default=False, db_column="bNVECC")

    nc_2012_reference_heating_cost = models.FloatField(db_column="fNCRHCT")
    nc_2012_reference_cooling_cost = models.FloatField(db_column="fNCRCCT")
    nc_2012_reference_hot_water_cost = models.FloatField(db_column="fNCRDCT")
    nc_2012_reference_lights_appliance_cost = models.FloatField(db_column="fNCRLACT")
    nc_2012_reference_photo_voltaic_cost = models.FloatField(db_column="fNCRPVCT")
    nc_2012_reference_service_cost = models.FloatField(db_column="fNCRSVCT")
    nc_2012_reference_total_cost = models.FloatField(db_column="fNCRTCT")
    nc_2012_designed_heating_cost = models.FloatField(db_column="fNCDHCT")
    nc_2012_designed_cooling_cost = models.FloatField(db_column="fNCDCCT")
    nc_2012_designed_hot_water_cost = models.FloatField(db_column="fNCDDCT")
    nc_2012_designed_lights_appliance_cost = models.FloatField(db_column="fNCDLACT")
    nc_2012_designed_photo_voltaic_cost = models.FloatField(db_column="fNCDPVCT")
    nc_2012_designed_service_cost = models.FloatField(db_column="fNCDSVCT")
    nc_2012_designed_total_cost = models.FloatField(db_column="fNCDTCT")
    passes_nc_2012_cost_compliance = models.BooleanField(default=False, db_column="bNCMeetCT")

    nc_2012_reference_overall_ua = models.FloatField(db_column="fNCRUA")
    nc_2012_designed_overall_ua = models.FloatField(db_column="fNCDUA")
    nc_2012_passing_ducts = models.BooleanField(default=False, db_column="bNCDctPass")
    passes_nc_2012_overall_ua_compliance = models.BooleanField(default=False, db_column="bNCUAPass")
    passes_nc_2012_code = models.BooleanField(default=False, db_column="bNCPass")

    nc_hero_2012_reference_heating_cost = models.FloatField(db_column="fNCHRHCT")
    nc_hero_2012_reference_cooling_cost = models.FloatField(db_column="fNCHRCCT")
    nc_hero_2012_reference_hot_water_cost = models.FloatField(db_column="fNCHRDCT")
    nc_hero_2012_reference_lights_appliance_cost = models.FloatField(db_column="fNCHRLACT")
    nc_hero_2012_reference_photo_voltaic_cost = models.FloatField(db_column="fNCHRPVCT")
    nc_hero_2012_reference_service_cost = models.FloatField(db_column="fNCHRSVCT")
    nc_hero_2012_reference_total_cost = models.FloatField(db_column="fNCHRTCT")
    nc_hero_2012_designed_heating_cost = models.FloatField(db_column="fNCHDHCT")
    nc_hero_2012_designed_cooling_cost = models.FloatField(db_column="fNCHDCCT")
    nc_hero_2012_designed_hot_water_cost = models.FloatField(db_column="fNCHDDCT")
    nc_hero_2012_designed_lights_appliance_cost = models.FloatField(db_column="fNCHDLACT")
    nc_hero_2012_designed_photo_voltaic_cost = models.FloatField(db_column="fNCHDPVCT")
    nc_hero_2012_designed_service_cost = models.FloatField(db_column="fNCHDSVCT")
    nc_hero_2012_designed_total_cost = models.FloatField(db_column="fNCHDTCT")
    passes_nc_hero_2012_cost_compliance = models.BooleanField(default=False, db_column="bNCHMeetCT")

    nc_hero_2012_reference_overall_ua = models.FloatField(db_column="fNCHRUA")
    nc_hero_2012_designed_overall_ua = models.FloatField(db_column="fNCHDUA")
    nc_hero_2012_passing_ducts = models.BooleanField(default=False, db_column="bNCHDctPass")
    passes_nc_hero_2012_overall_ua_compliance = models.BooleanField(
        default=False, db_column="bNCHUAPass"
    )
    passes_nc_hero_2012_code = models.BooleanField(default=False, db_column="bNCHPass")

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

    class Meta:
        db_table = "RegionalCode"
        managed = False
