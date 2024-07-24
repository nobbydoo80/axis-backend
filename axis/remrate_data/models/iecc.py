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


class IECC(models.Model):
    """IECC Data"""

    simulation = models.OneToOneField("Simulation", on_delete=models.CASCADE)
    _result_number = models.IntegerField(db_column="lBldgRunNo")
    rating_number = models.CharField(null=True, blank=True, max_length=93, db_column="SRATENO")

    iecc98_reference_heating_consumption = models.FloatField(db_column="f98IERHCn")
    iecc98_reference_cooling_consumption = models.FloatField(db_column="f98IERCCn")
    iecc98_reference_hot_water_consumption = models.FloatField(db_column="f98IERDCN")
    iecc98_reference_lights_appliance_consumption = models.FloatField(db_column="f98IERLACn")
    iecc98_reference_photo_voltaic_consumption = models.FloatField(db_column="f98IERPVCn")
    iecc98_reference_total_consumption = models.FloatField(db_column="f98IERTCn")
    iecc98_designed_heating_consumption = models.FloatField(db_column="f98IEDHCn")
    iecc98_designed_cooling_consumption = models.FloatField(db_column="f98IEDCCn")
    iecc98_designed_hot_water_consumption = models.FloatField(db_column="f98IEDDCN")
    iecc98_designed_lights_appliance_consumption = models.FloatField(db_column="f98IEDLACn")
    iecc98_designed_photo_voltaic_consumption = models.FloatField(db_column="f98IEDPVCn")
    iecc98_designed_total_consumption = models.FloatField(db_column="f98IEDTCn")
    meets_iecc98_consumption_compliance = models.BooleanField(default=False, db_column="b98IECC")
    iecc98_reference_overall_u0 = models.FloatField(db_column="f98IECCRUo")
    iecc98_designed_overall_u0 = models.FloatField(db_column="f98IECCDUo")
    passes_iecc98_ducts_overall_u0 = models.BooleanField(default=False, db_column="b98IECCDuP")
    passes_iecc98_overall_u0 = models.BooleanField(default=False, db_column="b98IECCuoP")

    iecc00_reference_heating_consumption = models.FloatField(db_column="f00IERHCn")
    iecc00_reference_cooling_consumption = models.FloatField(db_column="f00IERCCn")
    iecc00_reference_hot_water_consumption = models.FloatField(db_column="f00IERDCN")
    iecc00_reference_lights_appliance_consumption = models.FloatField(db_column="f00IERLACn")
    iecc00_reference_photo_voltaic_consumption = models.FloatField(db_column="f00IERPVCn")
    iecc00_reference_total_consumption = models.FloatField(db_column="f00IERTCn")
    iecc00_designed_heating_consumption = models.FloatField(db_column="f00IEDHCn")
    iecc00_designed_cooling_consumption = models.FloatField(db_column="f00IEDCCn")
    iecc00_designed_hot_water_consumption = models.FloatField(db_column="f00IEDDCN")
    iecc00_designed_lights_appliance_consumption = models.FloatField(db_column="f00IEDLACn")
    iecc00_designed_photo_voltaic_consumption = models.FloatField(db_column="f00IEDPVCn")
    iecc00_designed_total_consumption = models.FloatField(db_column="f00IEDTCn")
    meets_iecc00_consumption_compliance = models.BooleanField(default=False, db_column="b00IECC")
    iecc00_reference_overall_u0 = models.FloatField(db_column="f00IECCRUo")
    iecc00_designed_overall_u0 = models.FloatField(db_column="f00IECCDUo")
    passes_iecc00_ducts_overall_u0 = models.BooleanField(default=False, db_column="b00IECCDuP")
    passes_iecc00_overall_u0 = models.BooleanField(default=False, db_column="b00IECCuoP")

    iecc01_reference_heating_consumption = models.FloatField(db_column="f01IERHCn")
    iecc01_reference_cooling_consumption = models.FloatField(db_column="f01IERCCn")
    iecc01_reference_hot_water_consumption = models.FloatField(db_column="f01IERDCN")
    iecc01_reference_lights_appliance_consumption = models.FloatField(db_column="f01IERLACn")
    iecc01_reference_photo_voltaic_consumption = models.FloatField(db_column="f01IERPVCn")
    iecc01_reference_total_consumption = models.FloatField(db_column="f01IERTCn")
    iecc01_designed_heating_consumption = models.FloatField(db_column="f01IEDHCn")
    iecc01_designed_cooling_consumption = models.FloatField(db_column="f01IEDCCn")
    iecc01_designed_hot_water_consumption = models.FloatField(db_column="f01IEDDCN")
    iecc01_designed_lights_appliance_consumption = models.FloatField(db_column="f01IEDLACn")
    iecc01_designed_photo_voltaic_consumption = models.FloatField(db_column="f01IEDPVCn")
    iecc01_designed_total_consumption = models.FloatField(db_column="f01IEDTCn")
    meets_iecc01_consumption_compliance = models.BooleanField(default=False, db_column="b01IECC")
    iecc01_reference_overall_u0 = models.FloatField(db_column="f01IECCRUo")
    iecc01_designed_overall_u0 = models.FloatField(db_column="f01IECCDUo")
    passes_iecc01_ducts_overall_u0 = models.BooleanField(default=False, db_column="b01IECCDuP")
    passes_iecc01_overall_u0 = models.BooleanField(default=False, db_column="b01IECCuoP")

    iecc03_reference_heating_consumption = models.FloatField(db_column="f03IERHCn")
    iecc03_reference_cooling_consumption = models.FloatField(db_column="f03IERCCn")
    iecc03_reference_hot_water_consumption = models.FloatField(db_column="f03IERDCN")
    iecc03_reference_lights_appliance_consumption = models.FloatField(db_column="f03IERLACn")
    iecc03_reference_photo_voltaic_consumption = models.FloatField(db_column="f03IERPVCn")
    iecc03_reference_total_consumption = models.FloatField(db_column="f03IERTCn")
    iecc03_designed_heating_consumption = models.FloatField(db_column="f03IEDHCn")
    iecc03_designed_cooling_consumption = models.FloatField(db_column="f03IEDCCn")
    iecc03_designed_hot_water_consumption = models.FloatField(db_column="f03IEDDCN")
    iecc03_designed_lights_appliance_consumption = models.FloatField(db_column="f03IEDLACn")
    iecc03_designed_photo_voltaic_consumption = models.FloatField(db_column="f03IEDPVCn")
    iecc03_designed_total_consumption = models.FloatField(db_column="f03IEDTCn")
    passes_iecc03_consumption_compliance = models.BooleanField(default=False, db_column="b03IECC")

    iecc03_reference_overall_u0 = models.FloatField(db_column="f03IECCRUo")
    iecc03_designed_overall_u0 = models.FloatField(db_column="f03IECCDUo")
    passes_iecc03_ducts_overall_u0 = models.BooleanField(default=False, db_column="b03IECCDuP")
    passes_iecc03_overall_u0 = models.BooleanField(default=False, db_column="b03IECCuoP")

    iecc04_reference_heating_cost = models.FloatField(db_column="f04IERHCT")
    iecc04_reference_cooling_cost = models.FloatField(db_column="f04IERCCT")
    iecc04_reference_hot_water_cost = models.FloatField(db_column="f04IERDCT")
    iecc04_reference_lights_appliance_cost = models.FloatField(db_column="f04IERLACT")
    iecc04_reference_photo_voltaic_cost = models.FloatField(db_column="f04IERPVCT")
    iecc04_reference_service_cost = models.FloatField(db_column="f04IERSVCT")
    iecc04_reference_total_cost = models.FloatField(db_column="f04IERTCT")
    iecc04_designed_heating_cost = models.FloatField(db_column="f04IEDHCT")
    iecc04_designed_cooling_cost = models.FloatField(db_column="f04IEDCCT")
    iecc04_designed_hot_water_cost = models.FloatField(db_column="f04IEDDCT")
    iecc04_designed_lights_appliance_cost = models.FloatField(db_column="f04IEDLACT")
    iecc04_designed_photo_voltaic_cost = models.FloatField(db_column="f04IEDPVCT")
    iecc04_designed_service_cost = models.FloatField(db_column="f04IEDSVCT")
    iecc04_designed_total_cost = models.FloatField(db_column="f04IEDTCT")
    passes_iecc04_consumption_compliance = models.BooleanField(default=False, db_column="b04IECC")

    iecc04_reference_overall_u0 = models.FloatField(db_column="f04IECCRUA")
    iecc04_designed_overall_u0 = models.FloatField(db_column="f04IECCDUA")
    passes_iecc04_ducts_overall_u0 = models.BooleanField(default=False, db_column="b04IECCDuP")
    passes_iecc04_overall_ua_compliance = models.BooleanField(default=False, db_column="b04IECCuAP")
    passes_iecc04_code = models.BooleanField(default=False, db_column="bPass04IECC")

    iecc06_reference_heating_cost = models.FloatField(db_column="f06IERHCT")
    iecc06_reference_cooling_cost = models.FloatField(db_column="f06IERCCT")
    iecc06_reference_hot_water_cost = models.FloatField(db_column="f06IERDCT")
    iecc06_reference_lights_appliance_cost = models.FloatField(db_column="f06IERLACT")
    iecc06_reference_photo_voltaic_cost = models.FloatField(db_column="f06IERPVCT")
    iecc06_reference_service_cost = models.FloatField(db_column="f06IERSVCT")
    iecc06_reference_total_cost = models.FloatField(db_column="f06IERTCT")
    iecc06_designed_heating_cost = models.FloatField(db_column="f06IEDHCT")
    iecc06_designed_cooling_cost = models.FloatField(db_column="f06IEDCCT")
    iecc06_designed_hot_water_cost = models.FloatField(db_column="f06IEDDCT")
    iecc06_designed_lights_appliance_cost = models.FloatField(db_column="f06IEDLACT")
    iecc06_designed_photo_voltaic_cost = models.FloatField(db_column="f06IEDPVCT")
    iecc06_designed_service_cost = models.FloatField(db_column="f06IEDSVCT")
    iecc06_designed_total_cost = models.FloatField(db_column="f06IEDTCT")
    passes_iecc06_consumption_compliance = models.BooleanField(default=False, db_column="b06IECC")
    iecc06_reference_overall_u0 = models.FloatField(db_column="f06IECCRUA")
    iecc06_designed_overall_u0 = models.FloatField(db_column="f06IECCDUA")
    passes_iecc06_ducts_overall_u0 = models.BooleanField(default=False, db_column="b06IECCDuP")
    passes_iecc06_overall_ua_compliance = models.BooleanField(default=False, db_column="b06IECCuAP")
    passes_iecc06_code = models.BooleanField(default=False, db_column="bPass06IECC")

    iecc09_reference_heating_cost = models.FloatField(db_column="f09IERHCT")
    iecc09_reference_cooling_cost = models.FloatField(db_column="f09IERCCT")
    iecc09_reference_hot_water_cost = models.FloatField(db_column="f09IERDCT")
    iecc09_reference_lights_appliance_cost = models.FloatField(db_column="f09IERLACT")
    iecc09_reference_photo_voltaic_cost = models.FloatField(db_column="f09IERPVCT")
    iecc09_reference_service_cost = models.FloatField(db_column="f09IERSVCT")
    iecc09_reference_total_cost = models.FloatField(db_column="f09IERTCT")
    iecc09_designed_heating_cost = models.FloatField(db_column="f09IEDHCT")
    iecc09_designed_cooling_cost = models.FloatField(db_column="f09IEDCCT")
    iecc09_designed_hot_water_cost = models.FloatField(db_column="f09IEDDCT")
    iecc09_designed_lights_appliance_cost = models.FloatField(db_column="f09IEDLACT")
    iecc09_designed_photo_voltaic_cost = models.FloatField(db_column="f09IEDPVCT")
    iecc09_designed_service_cost = models.FloatField(db_column="f09IEDSVCT")
    iecc09_designed_total_cost = models.FloatField(db_column="f09IEDTCT")
    passes_iecc09_consumption_compliance = models.BooleanField(default=False, db_column="b09IECC")
    iecc09_reference_overall_u0 = models.FloatField(db_column="f09IECCRUA")
    iecc09_designed_overall_u0 = models.FloatField(db_column="f09IECCDUA")
    passes_iecc09_ducts_overall_u0 = models.BooleanField(default=False, db_column="b09IECCDuP")
    passes_iecc09_overall_ua_compliance = models.BooleanField(default=False, db_column="b09IECCuAP")
    passes_iecc09_code = models.BooleanField(default=False, db_column="bPass09IECC")

    iecc12_reference_heating_cost = models.FloatField(null=True, blank=True, db_column="f12IERHCT")
    iecc12_reference_cooling_cost = models.FloatField(null=True, blank=True, db_column="f12IERCCT")
    iecc12_reference_hot_water_cost = models.FloatField(
        null=True, blank=True, db_column="f12IERDCT"
    )
    iecc12_reference_lights_appliance_cost = models.FloatField(
        null=True, blank=True, db_column="f12IERLACT"
    )
    iecc12_reference_photo_voltaic_cost = models.FloatField(
        null=True, blank=True, db_column="f12IERPVCT"
    )
    iecc12_reference_service_cost = models.FloatField(null=True, blank=True, db_column="f12IERSVCT")
    iecc12_reference_total_cost = models.FloatField(null=True, blank=True, db_column="f12IERTCT")
    iecc12_designed_heating_cost = models.FloatField(null=True, blank=True, db_column="f12IEDHCT")
    iecc12_designed_cooling_cost = models.FloatField(null=True, blank=True, db_column="f12IEDCCT")
    iecc12_designed_hot_water_cost = models.FloatField(null=True, blank=True, db_column="f12IEDDCT")
    iecc12_designed_lights_appliance_cost = models.FloatField(
        null=True, blank=True, db_column="f12IEDLACT"
    )
    iecc12_designed_photo_voltaic_cost = models.FloatField(
        null=True, blank=True, db_column="f12IEDPVCT"
    )
    iecc12_designed_service_cost = models.FloatField(null=True, blank=True, db_column="f12IEDSVCT")
    iecc12_designed_total_cost = models.FloatField(null=True, blank=True, db_column="f12IEDTCT")
    passes_iecc12_consumption_compliance = models.BooleanField(
        null=True, default=False, db_column="b12IECC"
    )
    iecc12_reference_overall_u0 = models.FloatField(null=True, blank=True, db_column="f12IECCRUA")
    iecc12_designed_overall_u0 = models.FloatField(null=True, blank=True, db_column="f12IECCDUA")
    passes_iecc12_ducts_overall_u0 = models.BooleanField(
        null=True, default=False, db_column="b12IECCDuP"
    )
    passes_iecc12_overall_ua_compliance = models.BooleanField(
        null=True, default=False, db_column="b12IECCuAP"
    )
    passes_iecc12_code = models.BooleanField(null=True, default=False, db_column="bPass12IECC")

    iecc15_reference_heating_cost = models.FloatField(null=True, blank=True, db_column="f15IERHCT")
    iecc15_reference_cooling_cost = models.FloatField(null=True, blank=True, db_column="f15IERCCT")
    iecc15_reference_hot_water_cost = models.FloatField(
        null=True, blank=True, db_column="f15IERDCT"
    )
    iecc15_reference_lights_appliance_cost = models.FloatField(
        null=True, blank=True, db_column="f15IERLACT"
    )
    iecc15_reference_photo_voltaic_cost = models.FloatField(
        null=True, blank=True, db_column="f15IERPVCT"
    )
    iecc15_reference_service_cost = models.FloatField(null=True, blank=True, db_column="f15IERSVCT")
    iecc15_reference_total_cost = models.FloatField(null=True, blank=True, db_column="f15IERTCT")
    iecc15_designed_heating_cost = models.FloatField(null=True, blank=True, db_column="f15IEDHCT")
    iecc15_designed_cooling_cost = models.FloatField(null=True, blank=True, db_column="f15IEDCCT")
    iecc15_designed_hot_water_cost = models.FloatField(null=True, blank=True, db_column="f15IEDDCT")
    iecc15_designed_lights_appliance_cost = models.FloatField(
        null=True, blank=True, db_column="f15IEDLACT"
    )
    iecc15_designed_photo_voltaic_cost = models.FloatField(
        null=True, blank=True, db_column="f15IEDPVCT"
    )
    iecc15_designed_service_cost = models.FloatField(null=True, blank=True, db_column="f15IEDSVCT")
    iecc15_designed_total_cost = models.FloatField(null=True, blank=True, db_column="f15IEDTCT")
    passes_iecc15_consumption_compliance = models.BooleanField(
        null=True, blank=True, db_column="b15IECC"
    )
    iecc15_reference_overall_u0 = models.FloatField(null=True, blank=True, db_column="f15IECCRUA")
    iecc15_designed_overall_u0 = models.FloatField(null=True, blank=True, db_column="f15IECCDUA")
    passes_iecc15_ducts_overall_u0 = models.BooleanField(
        null=True, blank=True, db_column="b15IECCDuP"
    )
    passes_iecc15_overall_ua_compliance = models.BooleanField(
        null=True, blank=True, db_column="b15IECCuAP"
    )
    passes_iecc15_code = models.BooleanField(null=True, default=False, db_column="bPass15IECC")

    iecc18_reference_heating_cost = models.FloatField(null=True, blank=True, db_column="f18IERHCT")
    iecc18_reference_cooling_cost = models.FloatField(null=True, blank=True, db_column="f18IERCCT")
    iecc18_reference_hot_water_cost = models.FloatField(
        null=True, blank=True, db_column="f18IERDCT"
    )
    iecc18_reference_lights_appliance_cost = models.FloatField(
        null=True, blank=True, db_column="f18IERLACT"
    )
    iecc18_reference_photo_voltaic_cost = models.FloatField(
        null=True, blank=True, db_column="f18IERPVCT"
    )
    iecc18_reference_service_cost = models.FloatField(null=True, blank=True, db_column="f18IERSVCT")
    iecc18_reference_total_cost = models.FloatField(null=True, blank=True, db_column="f18IERTCT")
    iecc18_designed_heating_cost = models.FloatField(null=True, blank=True, db_column="f18IEDHCT")
    iecc18_designed_cooling_cost = models.FloatField(null=True, blank=True, db_column="f18IEDCCT")
    iecc18_designed_hot_water_cost = models.FloatField(null=True, blank=True, db_column="f18IEDDCT")
    iecc18_designed_lights_appliance_cost = models.FloatField(
        null=True, blank=True, db_column="f18IEDLACT"
    )
    iecc18_designed_photo_voltaic_cost = models.FloatField(
        null=True, blank=True, db_column="f18IEDPVCT"
    )
    iecc18_designed_service_cost = models.FloatField(null=True, blank=True, db_column="f18IEDSVCT")
    iecc18_designed_total_cost = models.FloatField(null=True, blank=True, db_column="f18IEDTCT")
    passes_iecc18_consumption_compliance = models.BooleanField(
        null=True, blank=True, db_column="b18IECC"
    )
    iecc18_reference_overall_u0 = models.FloatField(null=True, blank=True, db_column="f18IECCRUA")
    iecc18_designed_overall_u0 = models.FloatField(null=True, blank=True, db_column="f18IECCDUA")
    passes_iecc18_ducts_overall_u0 = models.BooleanField(
        null=True, blank=True, db_column="b18IECCDuP"
    )
    passes_iecc18_overall_ua_compliance = models.BooleanField(
        null=True, blank=True, db_column="b18IECCuAP"
    )
    passes_iecc18_code = models.BooleanField(null=True, default=False, db_column="bPass18IECC")

    iecc18_reference_mv_cost = models.FloatField(null=True, blank=True, db_column="f18IERMVCT")
    iecc18_design_mv_cost = models.FloatField(null=True, blank=True, db_column="f18IEDMVCT")

    iecc21_reference_heating_cost = models.FloatField(null=True, blank=True, db_column="f21IERHCT")
    iecc21_reference_cooling_cost = models.FloatField(null=True, blank=True, db_column="f21IERCCT")
    iecc21_reference_hot_water_cost = models.FloatField(
        null=True, blank=True, db_column="f21IERDCT"
    )
    iecc21_reference_lights_appliance_cost = models.FloatField(
        null=True, blank=True, db_column="f21IERLACT"
    )
    iecc21_reference_mv_cost = models.FloatField(null=True, blank=True, db_column="f21IERMVCT")
    iecc21_reference_photo_voltaic_cost = models.FloatField(
        null=True, blank=True, db_column="f21IERPVCT"
    )
    iecc21_reference_service_cost = models.FloatField(null=True, blank=True, db_column="f21IERSVCT")
    iecc21_reference_total_cost = models.FloatField(null=True, blank=True, db_column="f21IERTCT")
    iecc21_designed_heating_cost = models.FloatField(null=True, blank=True, db_column="f21IEDHCT")
    iecc21_designed_cooling_cost = models.FloatField(null=True, blank=True, db_column="f21IEDCCT")
    iecc21_designed_hot_water_cost = models.FloatField(null=True, blank=True, db_column="f21IEDDCT")
    iecc21_designed_lights_appliance_cost = models.FloatField(
        null=True, blank=True, db_column="f21IEDLACT"
    )
    iecc21_designed_mv_cost = models.FloatField(null=True, blank=True, db_column="f21IEDMVCT")
    iecc21_designed_photo_voltaic_cost = models.FloatField(
        null=True, blank=True, db_column="f21IEDPVCT"
    )
    iecc21_designed_service_cost = models.FloatField(null=True, blank=True, db_column="f21IEDSVCT")
    iecc21_designed_total_cost = models.FloatField(null=True, blank=True, db_column="f21IEDTCT")
    passes_iecc21_consumption_compliance = models.BooleanField(
        null=True, blank=True, db_column="b21IECC"
    )
    iecc21_reference_overall_u0 = models.FloatField(null=True, blank=True, db_column="f21IECCRUA")
    iecc21_designed_overall_u0 = models.FloatField(null=True, blank=True, db_column="f21IECCDUA")
    passes_iecc21_ducts_overall_u0 = models.BooleanField(
        null=True, blank=True, db_column="b21IECCDuP"
    )
    passes_iecc21_overall_ua_compliance = models.BooleanField(
        null=True, blank=True, db_column="b21IECCuAP"
    )
    passes_iecc21_code = models.BooleanField(null=True, default=False, db_column="bPass21IECC")
