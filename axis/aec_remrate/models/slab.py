"""Django AEC Models - Theses are the source data coming in on the rate database."""


import logging

from django.db import models

__author__ = "Steven Klass"
__date__ = "06/09/2019 13:51"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

from axis.remrate_data.strings import SLAB_LOCATIONS

log = logging.getLogger(__name__)


class Slab(models.Model):
    """Input Slabs"""

    result_number = models.IntegerField(null=True, db_column="LBLDGRUNNO", blank=True)
    building_number = models.IntegerField(db_column="LBLDGNO")
    name = models.CharField(max_length=93, db_column="SZSFNAME", blank=True)
    slab_type = models.IntegerField(db_column="LSFSLABTNO")

    # -- Not Used --
    fsfarea = models.FloatField(null=True, db_column="FSFAREA", blank=True)
    fsfdep = models.FloatField(null=True, db_column="FSFDEP", blank=True)
    fsfper = models.FloatField(null=True, db_column="FSFPER", blank=True)
    fsfexper = models.FloatField(null=True, db_column="FSFEXPER", blank=True)
    fsfonper = models.FloatField(null=True, db_column="FSFONPER", blank=True)
    ssfrateno = models.CharField(max_length=93, db_column="SSFRATENO", blank=True)

    location = models.IntegerField(
        null=True, blank=True, db_column="nSFLoc", choices=SLAB_LOCATIONS
    )

    class Meta:
        db_table = "Slab"
        managed = False
