"""Django AEC Models - Theses are the source data coming in on the rate database."""


import logging

from django.db import models

from axis.remrate_data.strings import FLOOR_LOCATIONS

__author__ = "Steven Klass"
__date__ = "06/09/2019 13:51"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class FrameFloor(models.Model):
    """Input Framing Floors"""

    result_number = models.IntegerField(null=True, db_column="LBLDGRUNNO", blank=True)
    building_number = models.IntegerField(db_column="LBLDGNO")
    name = models.CharField(max_length=93, db_column="SZFFNAME", blank=True)
    area = models.FloatField(null=True, db_column="FFFAREA", blank=True)
    location = models.FloatField(
        null=True, db_column="NFFLOC", max_length=2, choices=FLOOR_LOCATIONS
    )
    u_value = models.FloatField(null=True, db_column="FFFUO", blank=True)
    floor_type = models.IntegerField(db_column="LFFFLORTNO")
    rating_number = models.CharField(max_length=93, db_column="SFFRATENO", blank=True)

    class Meta:
        db_table = "FrameFlr"
        managed = False
