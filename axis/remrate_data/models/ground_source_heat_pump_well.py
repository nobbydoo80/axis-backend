"""RemRate Models suitable for use by Axis """


import logging

from django.db import models

from ..strings import WELL_TYPES

__author__ = "Steven Klass"
__date__ = "06/10/2019 11:03"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class GroundSourceHeatPumpWell(models.Model):
    """Ground source heat pump well"""

    simulation = models.OneToOneField("Simulation", on_delete=models.CASCADE)
    _result_number = models.IntegerField(db_column="lBldgRunNo")
    _source_ground_source_heat_pump = models.IntegerField(db_column="lGWellNo")
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

    def __str__(self):
        return "({}) {} GSHP Well ({}ft at {} GPM)".format(
            self.number_of_wells,
            self.get_well_type_display(),
            self.well_depth_trench_length,
            self.loop_flow_gpm,
        )
