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


class AboveGradeWall(models.Model):
    """Input Above Grade Walls"""

    result_number = models.IntegerField(null=True, db_column="LBLDGRUNNO", blank=True)
    building_number = models.IntegerField(db_column="LBLDGNO")
    name = models.CharField(max_length=93, db_column="SZAGNAME", blank=True)
    gross_area = models.FloatField(null=True, db_column="FAGAREA", blank=True)
    location = models.FloatField(null=True, db_column="NAGLOC", blank=True)
    color = models.FloatField(null=True, db_column="NAGCOL", blank=True)
    u_value = models.FloatField(null=True, db_column="FAGUO", blank=True)
    wall_number = models.FloatField(null=True, db_column="LAGWALLTNO", blank=True)
    rating_number = models.CharField(max_length=93, db_column="SAGRATENO", blank=True)

    class Meta:
        db_table = "AGWall"
        managed = False
