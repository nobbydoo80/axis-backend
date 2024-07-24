"""RemRate Models suitable for use by Axis """


import logging

from django.db import models

from ..strings import DOOR_TYPES

__author__ = "Steven Klass"
__date__ = "06/10/2019 11:03"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class DoorType(models.Model):
    """DoorType - Door Type"""

    simulation = models.ForeignKey("Simulation", on_delete=models.CASCADE)

    _result_number = models.IntegerField(db_column="lBldgRunNo")
    _source_door_type_number = models.IntegerField(db_column="lDTDTNo")
    name = models.CharField(max_length=93, db_column="sDTType", blank=True)
    door_type = models.IntegerField(null=True, db_column="nDTType", choices=DOOR_TYPES)
    r_value = models.FloatField(null=True, db_column="fDTRValue")
    note = models.CharField(max_length=765, db_column="sDTNote", blank=True)

    def __str__(self):
        return '"{}" R={}'.format(self.name, self.r_value)