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


class Sscmnwal(models.Model):
    """SunSpace Common Wall"""

    result_number = models.IntegerField(null=True, db_column="LBLDGRUNNO", blank=True)
    lbldgno = models.IntegerField(db_column="LBLDGNO")
    szsscname = models.CharField(max_length=93, db_column="SZSSCNAME", blank=True)
    fsscarea = models.FloatField(null=True, db_column="FSSCAREA", blank=True)
    nsscmtyp = models.FloatField(null=True, db_column="NSSCMTYP", blank=True)
    fsscmthk = models.FloatField(null=True, db_column="FSSCMTHK", blank=True)
    fsscins = models.FloatField(null=True, db_column="FSSCINS", blank=True)
    nsscfan = models.FloatField(null=True, db_column="NSSCFAN", blank=True)
    fsscflrate = models.FloatField(null=True, db_column="FSSCFLRATE", blank=True)
    ssscrateno = models.CharField(max_length=93, db_column="SSSCRATENO", blank=True)

    class Meta:
        db_table = "SSCmnWal"
        managed = False
