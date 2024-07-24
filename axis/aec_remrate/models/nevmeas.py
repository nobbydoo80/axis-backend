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


class Nevmeas(models.Model):
    """Nevada Measures"""

    lnmnmno = models.IntegerField(primary_key=True, db_column="LNMNMNO")
    snmcity = models.CharField(max_length=300, db_column="SNMCITY", blank=True)
    snmhouse = models.CharField(max_length=300, db_column="SNMHOUSE", blank=True)
    snmfnd = models.CharField(max_length=300, db_column="SNMFND", blank=True)
    snmhtg = models.CharField(max_length=300, db_column="SNMHTG", blank=True)
    snmclg = models.CharField(max_length=300, db_column="SNMCLG", blank=True)
    snmdhwft = models.CharField(max_length=300, db_column="SNMDHWFT", blank=True)
    snmmeatyp = models.CharField(max_length=300, db_column="SNMMEATYP", blank=True)
    snmmeadsc = models.CharField(max_length=765, db_column="SNMMEADSC", blank=True)
    fnmkwh = models.FloatField(null=True, db_column="FNMKWH", blank=True)
    fnmtherm = models.FloatField(null=True, db_column="FNMTHERM", blank=True)

    class Meta:
        db_table = "NevMeas"
        managed = False
