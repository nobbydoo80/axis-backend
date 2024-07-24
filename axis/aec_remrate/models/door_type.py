"""Django AEC Models - Theses are the source data coming in on the rate database."""


import logging

from django.db import models

from axis.remrate_data.strings import DOOR_TYPES

__author__ = "Steven Klass"
__date__ = "06/09/2019 13:51"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class DoorType(models.Model):
    """Input Door Type"""

    result_number = models.IntegerField(null=True, db_column="LBLDGRUNNO", blank=True)
    door_type_number = models.IntegerField(primary_key=True, db_column="LDTDTNO")
    name = models.CharField(max_length=93, db_column="SDTTYPE", blank=True)
    door_type = models.IntegerField(null=True, db_column="NDTTYPE", choices=DOOR_TYPES, blank=True)
    r_value = models.FloatField(null=True, db_column="FDTRVALUE", blank=True)
    note = models.CharField(max_length=765, db_column="SDTNOTE", blank=True)

    class Meta:
        db_table = "DoorType"
        managed = False
