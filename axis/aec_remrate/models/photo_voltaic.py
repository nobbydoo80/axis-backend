"""Django AEC Models - Theses are the source data coming in on the rate database."""


import logging

from django.db import models

from axis.remrate_data.strings import LOOP_TYPES

__author__ = "Steven Klass"
__date__ = "06/09/2019 13:51"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class PhotoVoltaic(models.Model):
    """Photo Voltaics"""

    result_number = models.IntegerField(null=True, db_column="LBLDGRUNNO", blank=True)
    building_number = models.IntegerField(db_column="LBLDGNO")
    type = models.IntegerField(null=True, choices=LOOP_TYPES, db_column="NPVCOLTYPE", blank=True)
    area = models.FloatField(null=True, db_column="FPVAREA", blank=True)
    peak_power = models.FloatField(null=True, db_column="FPVPOWER", blank=True)
    tilt = models.FloatField(null=True, db_column="FPVTILT", blank=True)
    orientation = models.IntegerField(null=True, choices=LOOP_TYPES, db_column="NPVOR", blank=True)
    inverter_efficiency = models.FloatField(null=True, db_column="FPVINVEFF", blank=True)
    rating_number = models.CharField(max_length=93, db_column="sPVRateNo", blank=True)
    name = models.CharField(max_length=93, db_column="SPVNAME", blank=True)
    number_bedrooms = models.IntegerField(blank=True, null=True, db_column="nPVNumBeds")

    class Meta:
        db_table = "PhotoVol"
        managed = False
