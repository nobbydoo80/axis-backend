"""Django AEC Models - Theses are the source data coming in on the rate database."""


import logging

from django.db import models

__author__ = "Steven Klass"
__date__ = "06/09/2019 13:51"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class Door(models.Model):
    """Input Door"""

    result_number = models.IntegerField(null=True, db_column="LBLDGRUNNO", blank=True)
    building_number = models.IntegerField(db_column="LBLDGNO")
    name = models.CharField(max_length=93, db_column="SZDONAME", blank=True)
    area = models.FloatField(null=True, db_column="FNOAREA", blank=True)
    wall_number = models.IntegerField(null=True, db_column="NDOWALLNUM", blank=True)
    door_type = models.IntegerField(db_column="LDODOORTNO")
    u_value = models.FloatField(null=True, db_column="FDOUO", blank=True)
    rater_number = models.CharField(max_length=93, db_column="SDORATENO", blank=True)

    class Meta:
        db_table = "Door"
        managed = False
