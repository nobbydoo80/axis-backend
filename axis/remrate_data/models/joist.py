"""RemRate Models suitable for use by Axis """


import logging

from django.db import models

from ..managers import JoistManager
from ..strings import JOIST_ABOVE_GRADE_WALL_LOCATIONS, INSULATION_GRADES

__author__ = "Steven Klass"
__date__ = "06/10/2019 11:03"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class Joist(models.Model):
    """Rim and Joist data"""

    simulation = models.ForeignKey("Simulation", on_delete=models.CASCADE)
    building = models.ForeignKey("Building", on_delete=models.CASCADE)

    _result_number = models.IntegerField(null=True, db_column="lBldgRunNo")
    _building_number = models.IntegerField(db_column="lBldgNo")
    name = models.CharField(max_length=93, db_column="szRJName", blank=True)
    area = models.FloatField(null=True, db_column="fRJArea")
    location = models.IntegerField(
        null=True, db_column="nRJLoc", choices=JOIST_ABOVE_GRADE_WALL_LOCATIONS
    )
    continuous_insulation_r_value = models.FloatField(null=True, db_column="fRJCoInsul")
    cavity_insulation_r_value = models.FloatField(null=True, db_column="fRJFrInsul")
    spacing = models.FloatField(null=True, db_column="fRJSpacing")
    u_value = models.FloatField(null=True, db_column="fRJUo")
    insulation_thickness = models.FloatField(null=True, db_column="fRJInsulTh")
    rating_number = models.CharField(max_length=93, db_column="sRJRateNo", blank=True)
    insulation_grade = models.IntegerField(
        null=True, db_column="nRJInsGrde", choices=INSULATION_GRADES
    )

    objects = JoistManager()

    def get_r_value(self):
        """Get the R-Value"""
        return "%.1f" % (1 / self.u_value)
