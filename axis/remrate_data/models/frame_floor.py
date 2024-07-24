"""RemRate Models suitable for use by Axis """


import logging

from django.db import models

from ..managers import FrameFloorManager
from ..strings import FLOOR_LOCATIONS

__author__ = "Steven Klass"
__date__ = "06/10/2019 11:03"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class FrameFloor(models.Model):
    """Framing Floors"""

    simulation = models.ForeignKey("Simulation", on_delete=models.CASCADE)
    building = models.ForeignKey("Building", on_delete=models.CASCADE)
    type = models.ForeignKey("FloorType", on_delete=models.CASCADE)

    _result_number = models.IntegerField(db_column="lBldgRunNo")
    _building_number = models.IntegerField(db_column="lBldgNo")
    name = models.CharField(max_length=93, db_column="szFFName", blank=True)
    area = models.FloatField(null=True, db_column="fFFArea")
    location = models.IntegerField(db_column="nFFLoc", choices=FLOOR_LOCATIONS)
    u_value = models.FloatField(db_column="fFFUo")
    _floor_type_number = models.IntegerField(db_column="lFFFlorTNo")
    rating_number = models.CharField(max_length=93, db_column="sFFRateNo", blank=True)

    objects = FrameFloorManager()

    def __str__(self):
        return '"{}", {}'.format(self.name, self.type)

    class Meta:
        ordering = ("simulation", "area")

    def get_r_value(self):
        """Get the R-Value"""
        return "%.1f" % (1 / self.u_value)
