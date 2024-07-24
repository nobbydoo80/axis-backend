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


class SunSpace(models.Model):
    """SunSpace- Sun Space"""

    simulation = models.OneToOneField("Simulation", on_delete=models.CASCADE)
    building = models.OneToOneField("Building", on_delete=models.CASCADE)
    _result_number = models.IntegerField(db_column="lBldgRunNo")
    _building_number = models.IntegerField(db_column="lBldgNo")
    roof_area = models.FloatField(null=True, db_column="fSSRfArea")
    roof_insulation = models.FloatField(null=True, db_column="fSSRFIns")
    above_grade_wall_area = models.FloatField(null=True, db_column="fSSAGWArea")
    above_grade_wall_insulation = models.FloatField(null=True, db_column="fSSAGWIns")
    below_grade_wall_area = models.FloatField(null=True, db_column="fSSBGWArea")
    below_grade_wall_insulation = models.FloatField(null=True, db_column="fSSBGWIns")
    floor_area = models.FloatField(null=True, db_column="fSSArea")
    floor_insulation = models.FloatField(null=True, db_column="fSSFrmIns")
    frame_floor_perimeter = models.FloatField(null=True, db_column="fSSSlbPer")
    slab_floor_depth = models.FloatField(null=True, db_column="fSSSlbDep")
    slab_floor_thickness = models.FloatField(null=True, db_column="fSSSlbThk")
    slab_floor_perimeter_insulation = models.FloatField(null=True, db_column="fSSSlbPIns")
    slab_floor_underslab_insulation = models.FloatField(null=True, db_column="fSSSlbUIns")
    rating_number = models.CharField(max_length=93, db_column="sSSRateNo", blank=True)

    def __str__(self):
        return "{} ({})".format(self.roof_area, self.roof_insulation)
