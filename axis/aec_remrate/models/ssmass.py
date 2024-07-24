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


class Ssmass(models.Model):
    """SunSpace Mass"""

    result_number = models.IntegerField(null=True, db_column="LBLDGRUNNO", blank=True)
    lbldgno = models.IntegerField(db_column="LBLDGNO")
    szssmname = models.CharField(max_length=93, db_column="SZSSMNAME", blank=True)
    fssmarea = models.FloatField(null=True, db_column="FSSMAREA", blank=True)
    nssmtype = models.FloatField(null=True, db_column="NSSMTYPE", blank=True)
    fssmthk = models.FloatField(null=True, db_column="FSSMTHK", blank=True)
    fssmwvol = models.FloatField(null=True, db_column="FSSMWVOL", blank=True)
    sssmrateno = models.CharField(max_length=93, db_column="SSSMRATENO", blank=True)

    class Meta:
        db_table = "SSMass"
        managed = False
