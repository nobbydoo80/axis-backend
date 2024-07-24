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


class Block(models.Model):
    """Utility Block information"""

    result_number = models.IntegerField(null=True, db_column="LBLDGRUNNO", blank=True)
    lblsrno = models.IntegerField(db_column="LBLSRNO")
    fblblckmax = models.FloatField(null=True, db_column="FBLBLCKMAX", blank=True)
    fblrate = models.FloatField(null=True, db_column="FBLRATE", blank=True)

    class Meta:
        db_table = "Block"
        managed = False
