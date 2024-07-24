"""RemRate Models suitable for use by Axis """


import logging

from django.db import models

from ..managers import FoundationWallManager
from ..strings import FOUNDATION_WALL_LOCATIONS

__author__ = "Steven Klass"
__date__ = "06/10/2019 11:03"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class FoundationWall(models.Model):
    """Foundataion Walls"""

    simulation = models.ForeignKey("Simulation", on_delete=models.CASCADE)
    building = models.ForeignKey("Building", on_delete=models.CASCADE)
    type = models.ForeignKey("FoundationWallType", on_delete=models.CASCADE)
    _result_number = models.IntegerField(db_column="lBldgRunNo")
    _building_number = models.IntegerField(db_column="lBldgNo")
    name = models.CharField(max_length=93, db_column="szFWName", blank=True)
    length = models.FloatField(null=True, db_column="fFWLength")
    height = models.FloatField(null=True, db_column="fFWHeight")
    depth_below_grade = models.FloatField(null=True, db_column="fFWDBGrade")
    depth_above_grade = models.FloatField(null=True, db_column="fFWHAGrade")
    location = models.IntegerField(db_column="nFWLoc", choices=FOUNDATION_WALL_LOCATIONS)
    _foundation_wall_number = models.IntegerField(db_column="lFWFWTNo")
    rating_number = models.CharField(max_length=93, db_column="sFWRateNo", blank=True)

    objects = FoundationWallManager()

    def __str__(self):
        return '"{}", {}'.format(self.name, self.type)

    def is_shared_for_window(self, window):
        """Does this wall contain other shared windows with other orientations"""
        from .simulation import Simulation

        other_windows = (
            Simulation.objects.get(id=self.simulation_id)
            .window_set.filter(foundation_number=window.wall_number)
            .exclude(orientation=window.orientation)
        )
        return other_windows.count()
