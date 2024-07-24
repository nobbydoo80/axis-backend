"""Django AEC Models - Theses are the source data coming in on the rate database."""


import logging

from django.db import models

from axis.remrate_data.strings import ORIENTATION_CHOICES

__author__ = "Steven Klass"
__date__ = "06/09/2019 13:51"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class Window(models.Model):
    """Input Windows"""

    result_number = models.IntegerField(null=True, db_column="LBLDGRUNNO", blank=True)
    building_number = models.IntegerField(db_column="LBLDGNO")
    name = models.CharField(max_length=93, db_column="SZWDNAME", blank=True)
    area = models.FloatField(null=True, db_column="FWDAREA", blank=True)
    orientation = models.IntegerField(null=True, db_column="NWDOR", choices=ORIENTATION_CHOICES)
    interior_shading_summer = models.FloatField(null=True, db_column="FWDSUMSHAD", blank=True)
    interior_shading_winter = models.FloatField(null=True, db_column="FWDWTRSHAD", blank=True)
    roof_number = models.FloatField(null=True, db_column="NWDSURFNUM", blank=True)
    foundation_number = models.FloatField(null=True, db_column="NWDSURFTYP", blank=True)
    window_type_number = models.IntegerField(null=True, db_column="LWDWINTNO", blank=True)
    rating_number = models.CharField(max_length=93, db_column="SWDRATENO", blank=True)
    overhang_depth = models.FloatField(null=True, db_column="FWDOHDEPTH", blank=True)
    overhang_depth_to_top_of_window = models.FloatField(
        null=True, db_column="FWDOHTOTOP", blank=True
    )
    overhang_depth_to_bottom_of_window = models.FloatField(
        null=True, db_column="FWDOHTOBTM", blank=True
    )
    adjacent_shading_summer = models.FloatField(null=True, db_column="FWDADJSUM", blank=True)
    adjacent_shading_winter = models.FloatField(null=True, db_column="FWDADJWTR", blank=True)
    window_operates = models.IntegerField(null=True, blank=True, db_column="nWDOperate")

    class Meta:
        db_table = "Window"
        managed = False
