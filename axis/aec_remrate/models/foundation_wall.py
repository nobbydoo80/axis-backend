"""Django AEC Models - Theses are the source data coming in on the rate database."""


import logging

from django.db import models

from axis.remrate_data.strings import FOUNDATION_WALL_LOCATIONS

__author__ = "Steven Klass"
__date__ = "06/09/2019 13:51"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class FoundationWall(models.Model):
    """Input Foundation Walls"""

    result_number = models.IntegerField(null=True, db_column="LBLDGRUNNO", blank=True)
    building_number = models.IntegerField(null=True, db_column="LBLDGNO", blank=True)
    name = models.CharField(max_length=93, db_column="SZFWNAME", blank=True)
    length = models.FloatField(null=True, db_column="FFWLENGTH", blank=True)
    height = models.FloatField(null=True, db_column="FFWHEIGHT", blank=True)
    depth_below_grade = models.FloatField(null=True, db_column="FFWDBGRADE", blank=True)
    depth_above_grade = models.FloatField(null=True, db_column="FFWHAGRADE", blank=True)
    location = models.IntegerField(null=True, db_column="NFWLOC", choices=FOUNDATION_WALL_LOCATIONS)
    wall_type = models.IntegerField(null=True, db_column="LFWFWTNO", blank=True)
    rating_number = models.CharField(max_length=93, db_column="SFWRATENO", blank=True)

    class Meta:
        db_table = "FndWall"
        managed = False
