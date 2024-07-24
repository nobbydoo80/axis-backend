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


class Skylight(models.Model):
    """Skylight"""

    result_number = models.IntegerField(null=True, db_column="LBLDGRUNNO", blank=True)
    lbldgno = models.IntegerField(db_column="LBLDGNO")
    szskname = models.CharField(max_length=93, db_column="SZSKNAME", blank=True)
    fskglzarea = models.FloatField(null=True, db_column="FSKGLZAREA", blank=True)
    nskor = models.FloatField(null=True, db_column="NSKOR", blank=True)
    fskpitch = models.FloatField(null=True, db_column="FSKPITCH", blank=True)
    fsksumshad = models.FloatField(null=True, db_column="FSKSUMSHAD", blank=True)
    fskwtrshad = models.FloatField(null=True, db_column="FSKWTRSHAD", blank=True)
    nsksurfnum = models.FloatField(null=True, db_column="NSKSURFNUM", blank=True)
    lskwintno = models.IntegerField(db_column="LSKWINTNO")
    sskrateno = models.CharField(max_length=93, db_column="SSKRATENO", blank=True)

    class Meta:
        db_table = "Skylight"
        managed = False
