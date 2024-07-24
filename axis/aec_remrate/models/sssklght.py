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


class Sssklght(models.Model):
    """SunSpace Skylight"""

    result_number = models.IntegerField(null=True, db_column="LBLDGRUNNO", blank=True)
    lbldgno = models.IntegerField(db_column="LBLDGNO")
    szsssname = models.CharField(max_length=93, db_column="SZSSSNAME", blank=True)
    fsssarea = models.FloatField(null=True, db_column="FSSSAREA", blank=True)
    nsssor = models.FloatField(null=True, db_column="NSSSOR", blank=True)
    fssspitch = models.FloatField(null=True, db_column="FSSSPITCH", blank=True)
    fssssum = models.FloatField(null=True, db_column="FSSSSUM", blank=True)
    fssswtr = models.FloatField(null=True, db_column="FSSSWTR", blank=True)
    lssswdwtno = models.IntegerField(db_column="LSSSWDWTNO")
    ssssrateno = models.CharField(max_length=93, db_column="SSSSRATENO", blank=True)

    class Meta:
        db_table = "SSSkLght"
        managed = False
