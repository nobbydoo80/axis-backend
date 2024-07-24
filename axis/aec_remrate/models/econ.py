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


class Econ(models.Model):
    """Economics"""

    result_number = models.IntegerField(null=True, db_column="LBLDGRUNNO", blank=True)
    lececno = models.IntegerField(primary_key=True, db_column="LECECNO")
    leccrno = models.IntegerField(db_column="LECCRNO")
    fecimpcst = models.FloatField(null=True, db_column="FECIMPCST", blank=True)
    fecwtlife = models.FloatField(null=True, db_column="FECWTLIFE", blank=True)
    necmorterm = models.FloatField(null=True, db_column="NECMORTERM", blank=True)
    fecmorrate = models.FloatField(null=True, db_column="FECMORRATE", blank=True)
    fecpvf = models.FloatField(null=True, db_column="FECPVF", blank=True)
    fecsavtot = models.FloatField(null=True, db_column="FECSAVTOT", blank=True)
    fecmaint = models.FloatField(null=True, db_column="FECMAINT", blank=True)
    fecnetsav = models.FloatField(null=True, db_column="FECNETSAV", blank=True)
    fecmorcst = models.FloatField(null=True, db_column="FECMORCST", blank=True)
    fecpvsav = models.FloatField(null=True, db_column="FECPVSAV", blank=True)
    necrankcr = models.FloatField(null=True, db_column="NECRANKCR", blank=True)
    feccutoff = models.FloatField(null=True, db_column="FECCUTOFF", blank=True)
    fecmaxlim = models.FloatField(null=True, db_column="FECMAXLIM", blank=True)
    necmeasint = models.FloatField(null=True, db_column="NECMEASINT", blank=True)

    class Meta:
        db_table = "Econ"
        managed = False
