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


class Addmass(models.Model):
    """Mass"""

    result_number = models.IntegerField(null=True, db_column="LBLDGRUNNO", blank=True)
    building_number = models.IntegerField(db_column="LBLDGNO")
    szamname = models.CharField(max_length=93, db_column="SZAMNAME", blank=True)
    famarea = models.FloatField(null=True, db_column="FAMAREA", blank=True)
    namloc = models.FloatField(null=True, db_column="NAMLOC", blank=True)
    namtype = models.FloatField(null=True, db_column="NAMTYPE", blank=True)
    famthk = models.FloatField(null=True, db_column="FAMTHK", blank=True)
    samrateno = models.CharField(max_length=93, db_column="SAMRATENO", blank=True)

    class Meta:
        db_table = "AddMass"
        managed = False
