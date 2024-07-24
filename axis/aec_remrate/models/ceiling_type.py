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


class CeilingType(models.Model):
    """These are the ceiling types which are used by the roof."""

    result_number = models.IntegerField(null=True, db_column="LBLDGRUNNO", blank=True)
    ceiling_number = models.IntegerField(primary_key=True, db_column="LCTCTNO")
    composite_insulation_number = models.FloatField(null=True, db_column="LCTCOMPNO", blank=True)
    note = models.CharField(max_length=255, db_column="SCTNOTE")
    style = models.IntegerField(choices=((1, "Vaulted"), (2, "Attic")), db_column="NCTCEILTYP")
    continuous_insulation = models.FloatField(null=True, db_column="FCTCONTINS", blank=True)
    cavity_insulation = models.FloatField(null=True, db_column="FCTCVTYINS", blank=True)

    # -- Not Used --
    fctgypthk = models.FloatField(null=True, db_column="FCTGYPTHK", blank=True)
    fctrftrwdt = models.FloatField(null=True, db_column="FCTRFTRWDT", blank=True)
    fctrftrhgt = models.FloatField(null=True, db_column="FCTRFTRHGT", blank=True)
    fctrftrspc = models.FloatField(null=True, db_column="FCTRFTRSPC", blank=True)
    fctcinsthk = models.FloatField(null=True, db_column="FCTCINSTHK", blank=True)
    bctqfvalid = models.FloatField(null=True, db_column="BCTQFVALID", blank=True)
    nctinstyp = models.IntegerField(null=True, db_column="NCTINSTYP", blank=True)
    fctunrdep = models.FloatField(null=True, db_column="FCTUNRDEP", blank=True)
    fctunrrvl = models.FloatField(null=True, db_column="FCTUNRRVL", blank=True)
    fctclgwid = models.FloatField(null=True, db_column="FCTCLGWID", blank=True)
    fctclgrse = models.FloatField(null=True, db_column="FCTCLGRSE", blank=True)
    fcttrshgt = models.FloatField(null=True, db_column="FCTTRSHGT", blank=True)
    fcthelhgt = models.FloatField(null=True, db_column="FCTHELHGT", blank=True)
    fctvntspc = models.FloatField(null=True, db_column="FCTVNTSPC", blank=True)
    nctqftyp = models.IntegerField(null=True, db_column="NCTQFTYP", blank=True)
    fctff = models.FloatField(null=True, db_column="FCTFF", blank=True)
    bctdfltff = models.IntegerField(null=True, db_column="BCTDFLTFF", blank=True)
    nctinsgrde = models.IntegerField(null=True, db_column="NCTINSGRDE", blank=True)

    class Meta:
        db_table = "CeilType"
        managed = False
