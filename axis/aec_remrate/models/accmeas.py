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


class Accmeas(models.Model):
    """Measures"""

    result_number = models.IntegerField(null=True, db_column="LBLDGRUNNO", blank=True)
    lamamno = models.IntegerField(primary_key=True, db_column="LAMAMNO")
    lamcrno = models.IntegerField(db_column="LAMCRNO")
    lamparno = models.FloatField(null=True, db_column="LAMPARNO", blank=True)
    nammult = models.FloatField(null=True, db_column="NAMMULT", blank=True)
    samcomp = models.CharField(max_length=153, db_column="SAMCOMP", blank=True)
    samexist = models.CharField(max_length=153, db_column="SAMEXIST", blank=True)
    samprop = models.CharField(max_length=153, db_column="SAMPROP", blank=True)
    samtreat = models.CharField(max_length=363, db_column="SAMTREAT", blank=True)
    samtreatd = models.CharField(max_length=363, db_column="SAMTREATD", blank=True)
    famlife = models.FloatField(null=True, db_column="FAMLIFE", blank=True)
    famcost = models.FloatField(null=True, db_column="FAMCOST", blank=True)
    famyrsav = models.FloatField(null=True, db_column="FAMYRSAV", blank=True)
    famsir = models.FloatField(null=True, db_column="FAMSIR", blank=True)
    fampvsav = models.FloatField(null=True, db_column="FAMPVSAV", blank=True)
    famsp = models.FloatField(null=True, db_column="FAMSP", blank=True)
    famrating = models.FloatField(null=True, db_column="FAMRATING", blank=True)
    fam1ycf = models.FloatField(null=True, db_column="FAM1YCF", blank=True)

    class Meta:
        db_table = "AccMeas"
        managed = False
