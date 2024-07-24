"""RemRate Models suitable for use by Axis """


import logging

from django.db import models

from ..managers import DuctManager
from ..strings import DUCT_LOCATIONS, DUCT_TYPES

__author__ = "Steven Klass"
__date__ = "06/10/2019 11:03"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class Duct(models.Model):
    """Duct - Duct"""

    simulation = models.ForeignKey("Simulation", on_delete=models.CASCADE)
    building = models.ForeignKey("Building", on_delete=models.CASCADE)
    duct_system = models.ForeignKey("DuctSystem", on_delete=models.CASCADE)

    _result_number = models.IntegerField(db_column="lBldgRunNo")
    _building_number = models.IntegerField(db_column="lBldgNo")
    _duct_system_number = models.IntegerField(db_column="lDUDSNo")

    area = models.FloatField(null=True, db_column="fDUArea")
    location = models.IntegerField(null=True, choices=DUCT_LOCATIONS, db_column="nDULoc")
    r_value = models.FloatField(null=True, db_column="fDUIns")
    type = models.IntegerField(null=True, choices=DUCT_TYPES, db_column="nDUDctType")
    rating_number = models.CharField(max_length=93, db_column="sDURateNo", blank=True)

    objects = DuctManager()

    def __str__(self):
        return "{} Duct: {} ({})".format(
            self.get_type_display(), self.get_location_display(), self.area
        )
