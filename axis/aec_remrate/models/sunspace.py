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


class Sunspace(models.Model):
    """Sunspace"""

    result_number = models.IntegerField(null=True, db_column="LBLDGRUNNO", blank=True)
    lbldgno = models.IntegerField(db_column="LBLDGNO")
    fssrfarea = models.FloatField(null=True, db_column="FSSRFAREA", blank=True)
    fssrfins = models.FloatField(null=True, db_column="FSSRFINS", blank=True)
    fssagwarea = models.FloatField(null=True, db_column="FSSAGWAREA", blank=True)
    fssagwins = models.FloatField(null=True, db_column="FSSAGWINS", blank=True)
    fssbgwarea = models.FloatField(null=True, db_column="FSSBGWAREA", blank=True)
    fssbgwins = models.FloatField(null=True, db_column="FSSBGWINS", blank=True)
    fssarea = models.FloatField(null=True, db_column="FSSAREA", blank=True)
    fssfrmins = models.FloatField(null=True, db_column="FSSFRMINS", blank=True)
    fssslbper = models.FloatField(null=True, db_column="FSSSLBPER", blank=True)
    fssslbdep = models.FloatField(null=True, db_column="FSSSLBDEP", blank=True)
    fssslbthk = models.FloatField(null=True, db_column="FSSSLBTHK", blank=True)
    fssslbpins = models.FloatField(null=True, db_column="FSSSLBPINS", blank=True)
    fssslbuins = models.FloatField(null=True, db_column="FSSSLBUINS", blank=True)
    sssrateno = models.CharField(max_length=93, db_column="SSSRATENO", blank=True)

    class Meta:
        db_table = "SunSpace"
        managed = False
