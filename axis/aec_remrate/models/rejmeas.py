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


class Rejmeas(models.Model):
    """Rejected Measures"""

    result_number = models.IntegerField(null=True, db_column="LBLDGRUNNO", blank=True)
    lrmrmno = models.IntegerField(primary_key=True, db_column="LRMRMNO")
    lrmcrno = models.IntegerField(db_column="LRMCRNO")
    lrmparno = models.FloatField(null=True, db_column="LRMPARNO", blank=True)
    nrmmult = models.FloatField(null=True, db_column="NRMMULT", blank=True)
    srmcomp = models.CharField(max_length=153, db_column="SRMCOMP", blank=True)
    srmexist = models.CharField(max_length=153, db_column="SRMEXIST", blank=True)
    srmprop = models.CharField(max_length=153, db_column="SRMPROP", blank=True)
    srmtreat = models.CharField(max_length=363, db_column="SRMTREAT", blank=True)
    srmtreatd = models.CharField(max_length=363, db_column="SRMTREATD", blank=True)
    frmlife = models.FloatField(null=True, db_column="FRMLIFE", blank=True)
    frmcost = models.FloatField(null=True, db_column="FRMCOST", blank=True)
    nrmrejreas = models.FloatField(null=True, db_column="NRMREJREAS", blank=True)
    srmrejreas = models.CharField(max_length=153, db_column="SRMREJREAS", blank=True)

    class Meta:
        db_table = "RejMeas"
        managed = False
