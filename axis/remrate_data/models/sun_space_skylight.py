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


class SunSpaceSkylight(models.Model):
    """SSSkLght - Sun Space Sky Light"""

    simulation = models.ForeignKey("Simulation", on_delete=models.CASCADE)
    building = models.ForeignKey("Building", on_delete=models.CASCADE)
    type = models.ForeignKey("WindowType", on_delete=models.CASCADE)
    _result_number = models.IntegerField(db_column="lBldgRunNo")
    _building_number = models.IntegerField(db_column="lBldgNo")
    name = models.CharField(max_length=93, db_column="szSSSName", blank=True)
    glazing_area = models.FloatField(null=True, db_column="fSSSArea")
    orientation = models.IntegerField(null=True, db_column="nSSSOr", choices=ORIENTATION_CHOICES)
    pitch = models.FloatField(null=True, db_column="fSSSPitch")
    summer_shading_factor = models.FloatField(
        null=True, db_column="fSSSSum", choices=SHADING_FACTOR
    )
    winter_shading_factor = models.FloatField(
        null=True, db_column="fSSSWtr", choices=SHADING_FACTOR
    )
    _window_type_number = models.IntegerField(db_column="lSSSWdwTNo")
    rating_number = models.CharField(max_length=93, db_column="sSSSRateNo", blank=True)

    def __str__(self):
        return '"{}", {}'.format(self.name, self.type)
