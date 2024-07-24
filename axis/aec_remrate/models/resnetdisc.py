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


class Resnetdisc(models.Model):
    """RESNET Questions"""

    result_number = models.IntegerField(null=True, db_column="LBLDGRUNNO", blank=True)
    lbldgno = models.IntegerField(db_column="LBLDGNO")
    nrdq1 = models.IntegerField(null=True, db_column="NRDQ1", blank=True)
    nrdq2a = models.IntegerField(null=True, db_column="NRDQ2A", blank=True)
    nrdq2b = models.IntegerField(null=True, db_column="NRDQ2B", blank=True)
    nrdq2c = models.IntegerField(null=True, db_column="NRDQ2C", blank=True)
    nrdq2d = models.IntegerField(null=True, db_column="NRDQ2D", blank=True)
    nrdq2e = models.IntegerField(null=True, db_column="NRDQ2E", blank=True)
    srdq2eothr = models.CharField(max_length=765, db_column="SRDQ2EOTHR", blank=True)
    nrdq3a = models.IntegerField(null=True, db_column="NRDQ3A", blank=True)
    nrdq3b = models.IntegerField(null=True, db_column="NRDQ3B", blank=True)
    nrdq3c = models.IntegerField(null=True, db_column="NRDQ3C", blank=True)
    nrdq4hvaci = models.IntegerField(null=True, db_column="NRDQ4HVACI", blank=True)
    nrdq4hvacb = models.IntegerField(null=True, db_column="NRDQ4HVACB", blank=True)
    nrdq4thmli = models.IntegerField(null=True, db_column="NRDQ4THMLI", blank=True)
    nrdq4thmlb = models.IntegerField(null=True, db_column="NRDQ4THMLB", blank=True)
    nrdq4airsi = models.IntegerField(null=True, db_column="NRDQ4AIRSI", blank=True)
    nrdq4airsb = models.IntegerField(null=True, db_column="NRDQ4AIRSB", blank=True)
    nrdq4wini = models.IntegerField(null=True, db_column="NRDQ4WINI", blank=True)
    nrdq4winb = models.IntegerField(null=True, db_column="NRDQ4WINB", blank=True)
    nrdq4appli = models.IntegerField(null=True, db_column="NRDQ4APPLI", blank=True)
    nrdq4applb = models.IntegerField(null=True, db_column="NRDQ4APPLB", blank=True)
    nrdq4cnsti = models.IntegerField(null=True, db_column="NRDQ4CNSTI", blank=True)
    nrdq4cnstb = models.IntegerField(null=True, db_column="NRDQ4CNSTB", blank=True)
    nrdq4othri = models.IntegerField(null=True, db_column="NRDQ4OTHRI", blank=True)
    nrdq4othrb = models.IntegerField(null=True, db_column="NRDQ4OTHRB", blank=True)
    srdq4othr = models.CharField(max_length=765, db_column="SRDQ4OTHR", blank=True)
    nrdq5 = models.IntegerField(null=True, db_column="NRDQ5", blank=True)
    srateno = models.CharField(max_length=93, db_column="SRATENO", blank=True)

    class Meta:
        db_table = "ResnetDisc"
        managed = False
