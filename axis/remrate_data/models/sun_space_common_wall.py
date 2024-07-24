"""RemRate Models suitable for use by Axis """


import logging

from django.db import models

from ..strings import MASS_TYPES

__author__ = "Steven Klass"
__date__ = "06/10/2019 11:03"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class SunSpaceCommonWall(models.Model):
    """SSCmnWal - SunSpace Common Wall"""

    simulation = models.ForeignKey("Simulation", on_delete=models.CASCADE)
    building = models.ForeignKey("Building", on_delete=models.CASCADE)
    _result_number = models.IntegerField(db_column="lBldgRunNo")
    _building_number = models.IntegerField(db_column="lBldgNo")
    name = models.CharField(max_length=93, db_column="szSSCName", blank=True)
    area = models.FloatField(null=True, db_column="fSSCArea")
    type = models.IntegerField(null=True, db_column="nSSCMTyp", choices=MASS_TYPES)
    thickness = models.FloatField(null=True, db_column="fSSCMThk")
    insulation_r_value = models.FloatField(null=True, db_column="fSSCIns")
    automatic_fan_coupling = models.BooleanField(default=False, db_column="nSSCFan")
    fan_flow_rate = models.FloatField(null=True, db_column="fSSCFlRate")
    rating_number = models.CharField(max_length=93, db_column="sSSCRateNo", blank=True)

    def __str__(self):
        return '"{}" ({})'.format(self.name, self.area)
