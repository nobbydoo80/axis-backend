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


class Costrate(models.Model):
    """Cost Rate analysis"""

    lcrcrno = models.IntegerField(primary_key=True, db_column="LCRCRNO")
    result_number = models.IntegerField(null=True, db_column="LBLDGRUNNO", blank=True)
    fcrhtg = models.FloatField(null=True, db_column="FCRHTG", blank=True)
    fcrhtg2 = models.FloatField(null=True, db_column="FCRHTG2", blank=True)
    fcrhtgsav = models.FloatField(null=True, db_column="FCRHTGSAV", blank=True)
    fcrclg = models.FloatField(null=True, db_column="FCRCLG", blank=True)
    fcrclg2 = models.FloatField(null=True, db_column="FCRCLG2", blank=True)
    fcrclgsav = models.FloatField(null=True, db_column="FCRCLGSAV", blank=True)
    fcrhw = models.FloatField(null=True, db_column="FCRHW", blank=True)
    fcrhw2 = models.FloatField(null=True, db_column="FCRHW2", blank=True)
    fcrhwsav = models.FloatField(null=True, db_column="FCRHWSAV", blank=True)
    fcrla = models.FloatField(null=True, db_column="FCRLA", blank=True)
    fcrla2 = models.FloatField(null=True, db_column="FCRLA2", blank=True)
    fcrlasav = models.FloatField(null=True, db_column="FCRLASAV", blank=True)
    fcrsc = models.FloatField(null=True, db_column="FCRSC", blank=True)
    fcrsc2 = models.FloatField(null=True, db_column="FCRSC2", blank=True)
    fcrscsav = models.FloatField(null=True, db_column="FCRSCSAV", blank=True)
    fcrtot = models.FloatField(null=True, db_column="FCRTOT", blank=True)
    fcrtot2 = models.FloatField(null=True, db_column="FCRTOT2", blank=True)
    fcrtotsav = models.FloatField(null=True, db_column="FCRTOTSAV", blank=True)
    fcrrating = models.FloatField(null=True, db_column="FCRRATING", blank=True)
    fcrrating2 = models.FloatField(null=True, db_column="FCRRATING2", blank=True)
    fcr1ycf = models.FloatField(null=True, db_column="FCR1YCF", blank=True)

    class Meta:
        db_table = "CostRate"
        managed = False
