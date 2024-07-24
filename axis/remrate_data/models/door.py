"""RemRate Models suitable for use by Axis """


import logging

from django.db import models

from ..managers import DoorManager

__author__ = "Steven Klass"
__date__ = "06/10/2019 11:03"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class Door(models.Model):
    """Door - Door"""

    simulation = models.ForeignKey("Simulation", on_delete=models.CASCADE)
    building = models.ForeignKey("Building", on_delete=models.CASCADE)
    type = models.ForeignKey("DoorType", on_delete=models.CASCADE)

    _result_number = models.IntegerField(db_column="lBldgRunNo")
    _building_number = models.IntegerField(db_column="lBldgNo")
    name = models.CharField(max_length=93, db_column="szDOName", blank=True)
    area = models.FloatField(null=True, db_column="fNOArea")
    wall_number = models.IntegerField(null=True, db_column="nDOWallNum")
    _door_type_number = models.IntegerField(db_column="lDODoorTNo")
    u_value = models.FloatField(null=True, db_column="fDOUo")
    rating_number = models.CharField(max_length=93, db_column="sDORateNo", blank=True)

    objects = DoorManager()

    def __str__(self):
        return '"{}", {}'.format(self.name, self.type)

    def get_attached_object(self):
        """Return the attached wall"""
        if self.wall_number:
            for idx, wall in enumerate(self.simulation.abovegradewall_set.order_by("pk"), start=1):
                if idx == self.wall_number:
                    return wall

    def get_orientation(self):
        return 5  # TODO Fix me.
