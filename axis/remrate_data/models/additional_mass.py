"""RemRate Models suitable for use by Axis """


import logging

from django.db import models

from ..strings import MASS_LOCATIONS, MASS_TYPES

__author__ = "Steven Klass"
__date__ = "06/10/2019 11:03"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class AdditionalMass(models.Model):
    """AddMass - Additional Mass"""

    simulation = models.ForeignKey("Simulation", on_delete=models.CASCADE)
    building = models.ForeignKey("Building", on_delete=models.CASCADE)

    _result_number = models.IntegerField(db_column="lBldgRunNo")
    _building_number = models.IntegerField(db_column="lBldgNo")
    name = models.CharField(max_length=93, db_column="szAMName", blank=True)
    area = models.FloatField(null=True, db_column="fAMArea")
    location = models.IntegerField(null=True, db_column="nAMLoc", choices=MASS_LOCATIONS)
    type = models.IntegerField(null=True, db_column="nAMType", choices=MASS_TYPES)
    thickness = models.FloatField(null=True, db_column="fAMThk")
    rating_number = models.CharField(max_length=93, db_column="sAMRateNo", blank=True)

    def __str__(self):
        return '"{}", {}'.format(self.name, self.get_type_display())
