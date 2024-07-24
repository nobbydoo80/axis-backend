"""Django AEC Models - Theses are the source data coming in on the rate database."""


import logging

from django.db import models

from axis.remrate_data.strings import WELL_TYPES

__author__ = "Steven Klass"
__date__ = "06/09/2019 13:51"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class GshpWell(models.Model):
    """Ground Source Heat Pump Well"""

    result_number = models.IntegerField(db_column="lBldgRunNo")
    ground_source_heat_pump_well_number = models.IntegerField(db_column="lGWellNo")
    well_type = models.IntegerField(
        db_column="nGWType", choices=WELL_TYPES, verbose_name="Well Type"
    )
    number_of_wells = models.FloatField(
        db_column="fGWNoWells", verbose_name="Number of Wells or Trenches"
    )
    well_depth_trench_length = models.FloatField(
        db_column="fGWDepth", verbose_name="Well Depth or Trench Length"
    )
    loop_flow_gpm = models.FloatField(db_column="fGWLpFlow", verbose_name="Loop Flow (GPM)")
    rating_number = models.CharField(
        max_length=93, db_column="sRateNo", blank=True, verbose_name=""
    )

    class Meta:
        db_table = "GshpWell"
        managed = False
