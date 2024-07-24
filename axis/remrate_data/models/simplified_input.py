"""RemRate Models suitable for use by Axis """


import logging

from django.db import models

from ..strings import (
    SIMPLIFIED_INPUT_HOUSE_TYPES,
    SIMPLIFIED_INPUT_FOUNDATION_TYPES,
    INFILTRATION_EST_TYPES,
    INFILTRATION_UNITS,
)

__author__ = "Steven Klass"
__date__ = "06/10/2019 11:03"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class SimplifiedInput(models.Model):
    """SimpInp"""

    simulation = models.ForeignKey("Simulation", on_delete=models.CASCADE)
    building = models.ForeignKey("Building", on_delete=models.CASCADE)
    _result_number = models.IntegerField(db_column="lBldgRunNo")
    _building_number = models.IntegerField(db_column="lBldgNo")
    house_type = models.IntegerField(
        null=True, db_column="nSIHseType", choices=SIMPLIFIED_INPUT_HOUSE_TYPES
    )
    foundation_type = models.FloatField(
        null=True, db_column="nSIFndType", choices=SIMPLIFIED_INPUT_FOUNDATION_TYPES
    )
    pct_of_each_foundation_sl = models.FloatField(null=True, db_column="fSIFndPesl", blank=True)
    pct_of_each_foundation_oc = models.FloatField(null=True, db_column="fSIFndPeoc", blank=True)
    pct_of_each_foundation_ec = models.FloatField(null=True, db_column="fSIFndPeec", blank=True)
    pct_of_each_foundation_hc = models.FloatField(null=True, db_column="fSIFndPeHC", blank=True)
    pct_of_each_foundation_uf = models.FloatField(null=True, db_column="fSIFndPeUF", blank=True)
    pct_of_each_foundation_hf = models.FloatField(null=True, db_column="fSIFndPeHF", blank=True)
    pct_of_each_foundation_uw = models.FloatField(null=True, db_column="fSIFndPeUW", blank=True)
    pct_of_each_foundation_hw = models.FloatField(null=True, db_column="fSIFndPeHW", blank=True)
    conditioned_floor_area = models.FloatField(null=True, db_column="fSICFlArea", blank=True)
    number_of_bedrooms = models.IntegerField(null=True, db_column="nSIBedRms", blank=True)
    pct_of_each_floor_area_hb = models.FloatField(null=True, db_column="fSIPFlArHB", blank=True)
    pct_of_each_floor_area_fl = models.FloatField(null=True, db_column="fSIPFlArFL", blank=True)
    pct_of_each_floor_area_ml = models.FloatField(null=True, db_column="fSIPFlArML", blank=True)
    pct_of_each_floor_area_sl = models.FloatField(null=True, db_column="fSIPFlArSL", blank=True)
    pct_of_each_floor_area_tl = models.FloatField(null=True, db_column="fSIPFlArTL", blank=True)
    number_of_corners_hb = models.IntegerField(null=True, db_column="nSINoCrnHB", blank=True)
    number_of_corners_fl = models.IntegerField(null=True, db_column="nSINoCrnFL", blank=True)
    number_of_corners_ml = models.IntegerField(null=True, db_column="nSINoCrnML", blank=True)
    number_of_corners_sl = models.IntegerField(null=True, db_column="nSINoCrnSL", blank=True)
    number_of_corners_tl = models.IntegerField(null=True, db_column="nSINoCrnTL", blank=True)
    pct_open_above_hb = models.FloatField(null=True, db_column="fSIPOAboHB", blank=True)
    pct_open_above_fl = models.FloatField(null=True, db_column="fSIPOAboFL", blank=True)
    pct_open_above_ml = models.FloatField(null=True, db_column="fSIPOAboML", blank=True)
    pct_open_above_sl = models.FloatField(null=True, db_column="fSIPOAboSL", blank=True)
    pct_open_above_tl = models.FloatField(null=True, db_column="fSIPOAboTL", blank=True)
    ceiling_height_hb = models.FloatField(null=True, db_column="fSICeilHHB", blank=True)
    ceiling_height_fl = models.FloatField(null=True, db_column="fSICeilHFL", blank=True)
    ceiling_height_ml = models.FloatField(null=True, db_column="fSICeilHML", blank=True)
    ceiling_height_sl = models.FloatField(null=True, db_column="fSICeilHSL", blank=True)
    ceiling_height_tl = models.FloatField(null=True, db_column="fSICeilHTL", blank=True)
    pct_level_over_garage = models.FloatField(null=True, db_column="fSIPOGrge", blank=True)
    pct_catherdral_hb = models.FloatField(null=True, db_column="fSIPCathHB", blank=True)
    pct_catherdral_fl = models.FloatField(null=True, db_column="fSIPCathFL", blank=True)
    pct_catherdral_ml = models.FloatField(null=True, db_column="fSIPCathML", blank=True)
    pct_catherdral_sl = models.FloatField(null=True, db_column="fSIPCathSL", blank=True)
    pct_catherdral_tl = models.FloatField(null=True, db_column="fSIPCathTL", blank=True)
    infiltration_rate = models.FloatField(null=True, db_column="fSIInfRate", blank=True)
    infiltration_measure_type = models.IntegerField(
        null=True, db_column="nSIInfMTyp", choices=INFILTRATION_EST_TYPES
    )
    infiltration_units = models.IntegerField(
        null=True, db_column="nSIInfUnit", choices=INFILTRATION_UNITS
    )
    number_of_doors = models.IntegerField(null=True, db_column="nSINoDoors", blank=True)
    slab_depth_basement_level = models.FloatField(null=True, db_column="fSISlbDBmt", blank=True)
    slab_depth_level_1 = models.FloatField(null=True, db_column="fSlbD1L", blank=True)
    _ceiling_type_1 = models.FloatField(null=True, db_column="lSIClgT1No", blank=True)
    _ceiling_type_2 = models.FloatField(null=True, db_column="lSIClgT2No", blank=True)
    _wall_type_1 = models.FloatField(null=True, db_column="lSIWalT1No", blank=True)
    _wall_type_2 = models.FloatField(null=True, db_column="lSIWalT2No", blank=True)
    _foundation_wall_type = models.FloatField(null=True, db_column="lSIFndWTNo", blank=True)
    _floor_type = models.FloatField(null=True, db_column="lSIFlrTyNo", blank=True)
    _door_type = models.FloatField(null=True, db_column="lSIDorTyNo", blank=True)
    _slab_type = models.FloatField(null=True, db_column="lSISlbTyNo", blank=True)
    rating_number = models.CharField(max_length=93, db_column="sSIRateNo", blank=True)
    mobile_home_box_length = models.FloatField(null=True, db_column="fSIBoxLen", blank=True)
    mobile_home_box_width = models.FloatField(null=True, db_column="fSIBoxWid", blank=True)
    mobile_home_box_height = models.FloatField(null=True, db_column="fSIBoxHgt", blank=True)
    level_above_garage = models.FloatField(null=True, db_column="nSILvAbGar", blank=True)
