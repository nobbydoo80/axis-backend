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


class Lainst(models.Model):
    """Lights and Appliances Installed"""

    result_number = models.IntegerField(null=True, db_column="LBLDGRUNNO", blank=True)
    lbldgno = models.IntegerField(db_column="LBLDGNO")
    slainame = models.CharField(max_length=765, db_column="SLAINAME", blank=True)
    nlaitype = models.FloatField(null=True, db_column="NLAITYPE", blank=True)
    nlailoc = models.FloatField(null=True, db_column="NLAILOC", blank=True)
    nlaifuel = models.FloatField(null=True, db_column="NLAIFUEL", blank=True)
    flairate = models.FloatField(null=True, db_column="FLAIRATE", blank=True)
    nlairateu = models.FloatField(null=True, db_column="NLAIRATEU", blank=True)
    flaiuse = models.FloatField(null=True, db_column="FLAIUSE", blank=True)
    nlaiuseu = models.FloatField(null=True, db_column="NLAIUSEU", blank=True)
    nlaiqty = models.IntegerField(db_column="NLAIQTY")
    nlaieff = models.IntegerField(db_column="NLAIEFF", null=True)

    class Meta:
        db_table = "LAInst"
        managed = False
