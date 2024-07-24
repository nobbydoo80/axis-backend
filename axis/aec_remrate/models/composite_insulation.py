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


class CompositeInsulation(models.Model):
    """Defines a wall or ceiling cavity and it associated data"""

    result_number = models.IntegerField(null=True, db_column="LBLDGRUNNO", blank=True)
    composite_insulation_number = models.IntegerField(primary_key=True, db_column="LTCTTCTTNO")
    name = models.CharField(max_length=93, db_column="STCTTYPE", blank=True)
    u_value = models.FloatField(null=True, db_column="FTCTUO", blank=True)

    # -- Not Used --
    ntctqfval = models.FloatField(null=True, db_column="NTCTQFVAL", blank=True)
    stctlnm1 = models.CharField(max_length=93, db_column="STCTLNM1", blank=True)
    stctlnm2 = models.CharField(max_length=93, db_column="STCTLNM2", blank=True)
    stctlnm3 = models.CharField(max_length=93, db_column="STCTLNM3", blank=True)
    stctlnm4 = models.CharField(max_length=93, db_column="STCTLNM4", blank=True)
    stctlnm5 = models.CharField(max_length=93, db_column="STCTLNM5", blank=True)
    stctlnm6 = models.CharField(max_length=93, db_column="STCTLNM6", blank=True)

    class Meta:
        db_table = "CompType"
        managed = False
