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


class SunSpaceMass(models.Model):
    """SSMass - Sun Space Mass"""

    simulation = models.ForeignKey("Simulation", on_delete=models.CASCADE)
    building = models.ForeignKey("Building", on_delete=models.CASCADE)
    _result_number = models.IntegerField(db_column="lBldgRunNo")
    _building_number = models.IntegerField(db_column="lBldgNo")
    name = models.CharField(max_length=93, db_column="szSSMName", blank=True)
    area = models.FloatField(null=True, db_column="fSSMArea")
    type = models.IntegerField(null=True, db_column="nSSMType", choices=MASS_TYPES)
    thickness = models.FloatField(null=True, db_column="fSSMThk")
    water_storage_volume = models.FloatField(null=True, db_column="fSSMWVol")
    rating_number = models.CharField(max_length=93, db_column="sSSMRateNo", blank=True)

    def __str__(self):
        return '"{}" ({})'.format(self.name, self.area)
