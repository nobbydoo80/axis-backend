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


class Hercinfo(models.Model):
    """HERC Info"""

    result_number = models.IntegerField(null=True, db_column="LBLDGRUNNO", blank=True)
    lbldgno = models.IntegerField(null=True, db_column="LBLDGNO", blank=True)
    shiusritem = models.CharField(max_length=765, db_column="SHIUSRITEM", blank=True)
    shiitmtype = models.CharField(max_length=765, db_column="SHIITMTYPE", blank=True)

    class Meta:
        db_table = "HercInfo"
        managed = False
