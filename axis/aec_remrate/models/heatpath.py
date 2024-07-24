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


class Heatpath(models.Model):
    """Heat Paths"""

    result_number = models.IntegerField(null=True, db_column="LBLDGRUNNO", blank=True)
    lhptcttno = models.FloatField(null=True, db_column="LHPTCTTNO", blank=True)
    shppthname = models.CharField(max_length=93, db_column="SHPPTHNAME", blank=True)
    fhpptharea = models.FloatField(null=True, db_column="FHPPTHAREA", blank=True)
    fhppthrval = models.FloatField(null=True, db_column="FHPPTHRVAL", blank=True)
    fhplrval1 = models.FloatField(null=True, db_column="FHPLRVAL1", blank=True)
    fhplrval2 = models.FloatField(null=True, db_column="FHPLRVAL2", blank=True)
    fhplrval3 = models.FloatField(null=True, db_column="FHPLRVAL3", blank=True)
    fhplrval4 = models.FloatField(null=True, db_column="FHPLRVAL4", blank=True)
    fhplrval5 = models.FloatField(null=True, db_column="FHPLRVAL5", blank=True)
    fhplrval6 = models.FloatField(null=True, db_column="FHPLRVAL6", blank=True)
    fhplrval7 = models.FloatField(null=True, db_column="FHPLRVAL7", blank=True)
    fhplrval8 = models.FloatField(null=True, db_column="FHPLRVAL8", blank=True)

    class Meta:
        db_table = "HeatPath"
        managed = False
