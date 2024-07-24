"""RemRate Models suitable for use by Axis """


import logging

from django.db import models

from ..strings import ORIENTATION_CHOICES, SHADING_FACTOR

__author__ = "Steven Klass"
__date__ = "06/10/2019 11:03"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class SunSpaceWindow(models.Model):
    """SSWindow - Sun Space Window"""

    simulation = models.ForeignKey("Simulation", on_delete=models.CASCADE)
    building = models.ForeignKey("Building", on_delete=models.CASCADE)
    type = models.ForeignKey("WindowType", on_delete=models.CASCADE)
    _result_number = models.IntegerField(db_column="lBldgRunNo")
    _building_number = models.IntegerField(db_column="lBldgNo")
    name = models.CharField(max_length=93, db_column="szSSWName", blank=True)
    glazing_area = models.FloatField(null=True, db_column="fSSWArea")
    orientation = models.IntegerField(null=True, db_column="nSSWOr", choices=ORIENTATION_CHOICES)
    interior_summer_shading_factor = models.FloatField(null=True, db_column="fSSWSum")
    interior_winter_shading_factor = models.FloatField(null=True, db_column="fSSWWtr")
    _window_type_number = models.IntegerField(db_column="lSSWWdwTNo")
    rating_number = models.CharField(max_length=93, db_column="sSSWRateNo", blank=True)
    overhang_depth = models.FloatField(null=True, db_column="fSSOHDepth")
    overhang_depth_to_top_of_window = models.FloatField(null=True, db_column="fSSOHToTop")
    overhang_depth_to_bottom_of_window = models.FloatField(null=True, db_column="fSSOHToBtm")
    adjacent_summer_shading_factor = models.FloatField(
        null=True, db_column="fSSAdjSum", choices=SHADING_FACTOR
    )
    adjacent_winter_shading_factor = models.FloatField(
        null=True, db_column="fSSAdjWtr", choices=SHADING_FACTOR
    )

    def __str__(self):
        return '"{}"'.format(self.name)
