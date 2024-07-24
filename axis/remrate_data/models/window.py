"""RemRate Models suitable for use by Axis """


import logging

from django.db import models

from ..managers import WindowManager
from ..strings import ORIENTATION_CHOICES, SHADING_FACTOR, WINDOW_OPERATES

__author__ = "Steven Klass"
__date__ = "06/10/2019 11:03"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class Window(models.Model):
    """Window - Windows"""

    simulation = models.ForeignKey("Simulation", on_delete=models.CASCADE)
    building = models.ForeignKey("Building", on_delete=models.CASCADE)
    type = models.ForeignKey("WindowType", on_delete=models.CASCADE)

    _result_number = models.IntegerField(db_column="lBldgRunNo")
    _building_number = models.IntegerField(db_column="lBldgNo")
    name = models.CharField(max_length=93, db_column="szWDName", blank=True)
    area = models.FloatField(null=True, db_column="fWDArea")
    orientation = models.IntegerField(null=True, db_column="nWDOr", choices=ORIENTATION_CHOICES)
    interior_shading_summer_factor = models.FloatField(null=True, db_column="fWDSumShad")
    interior_shading_winter_factor = models.FloatField(null=True, db_column="fWDWtrShad")
    wall_number = models.IntegerField(null=True, db_column="nWDSurfNum")
    foundation_number = models.FloatField(null=True, db_column="nWDSurfTyp")
    _window_type_number = models.IntegerField(db_column="lWDWinTNo")
    rating_number = models.CharField(max_length=93, db_column="sWDRateNo", blank=True)
    overhang_depth = models.FloatField(null=True, db_column="fWDOHDepth")
    overhang_depth_to_top_of_window = models.FloatField(null=True, db_column="fWDOHToTop")
    overhang_depth_to_bottom_of_window = models.FloatField(null=True, db_column="fWDOHToBtm")
    adjacent_shading_summer_factor = models.FloatField(
        null=True, db_column="fWDAdjSum", choices=SHADING_FACTOR
    )
    adjacent_shading_winter_factor = models.FloatField(
        null=True, db_column="fWDAdjWtr", choices=SHADING_FACTOR
    )
    window_operates = models.IntegerField(
        null=True, blank=True, db_column="nWDOperate", choices=WINDOW_OPERATES
    )

    objects = WindowManager()

    def __str__(self):
        return '"{}", {}'.format(self.name, self.type)

    def get_attached_object(self):
        """Return the attached wall"""
        if self.wall_number:
            for idx, wall in enumerate(self.simulation.abovegradewall_set.order_by("pk"), start=1):
                if idx == self.wall_number:
                    return wall
        elif self.foundation_number:
            for idx, wall in enumerate(self.simulation.foundationwall_set.order_by("pk"), start=1):
                if idx == self.foundation_number:
                    return wall
