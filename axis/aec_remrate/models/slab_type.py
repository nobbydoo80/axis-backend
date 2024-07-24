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


class SlabType(models.Model):
    """Input Slab Types"""

    result_number = models.IntegerField(null=True, db_column="LBLDGRUNNO", blank=True)
    slab_type_number = models.IntegerField(primary_key=True, db_column="LSTSTNO")
    name = models.CharField(max_length=93, db_column="SSTTYPE", blank=True)
    perimeter_r_value = models.FloatField(null=True, db_column="FSTPINS", blank=True)
    radiant_floor = models.IntegerField(
        null=True, db_column="NSTRADIANT", choices=((True, 1), (False, 2))
    )

    # -- Not Used --
    fstuins = models.FloatField(null=True, db_column="FSTUINS", blank=True)
    fstfuwid = models.FloatField(null=True, db_column="FSTFUWID", blank=True)
    fstpinsdep = models.FloatField(null=True, db_column="FSTPINSDEP", blank=True)
    sstnote = models.CharField(max_length=765, db_column="SSTNOTE", blank=True)
    nstinsgrde = models.IntegerField(null=True, db_column="NSTINSGRDE", blank=True)
    nstflrcvr = models.IntegerField(null=True, db_column="NSTFLRCVR", blank=True)

    class Meta:
        db_table = "SlabType"
        managed = False
