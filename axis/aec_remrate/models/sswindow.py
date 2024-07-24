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


class Sswindow(models.Model):
    """SunSpace Window"""

    result_number = models.IntegerField(null=True, db_column="LBLDGRUNNO", blank=True)
    lbldgno = models.IntegerField(db_column="LBLDGNO")
    szsswname = models.CharField(max_length=93, db_column="SZSSWNAME", blank=True)
    fsswarea = models.FloatField(null=True, db_column="FSSWAREA", blank=True)
    nsswor = models.FloatField(null=True, db_column="NSSWOR", blank=True)
    fsswsum = models.FloatField(null=True, db_column="FSSWSUM", blank=True)
    fsswwtr = models.FloatField(null=True, db_column="FSSWWTR", blank=True)
    lsswwdwtno = models.IntegerField(db_column="LSSWWDWTNO")
    ssswrateno = models.CharField(max_length=93, db_column="SSSWRATENO", blank=True)
    fssohdepth = models.FloatField(null=True, db_column="FSSOHDEPTH", blank=True)
    fssohtotop = models.FloatField(null=True, db_column="FSSOHTOTOP", blank=True)
    fssohtobtm = models.FloatField(null=True, db_column="FSSOHTOBTM", blank=True)
    fssadjsum = models.FloatField(null=True, db_column="FSSADJSUM", blank=True)
    fssadjwtr = models.FloatField(null=True, db_column="FSSADJWTR", blank=True)

    class Meta:
        db_table = "SSWindow"
        managed = False
