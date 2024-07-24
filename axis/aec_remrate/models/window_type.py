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


class WindowType(models.Model):
    """Input Window Types"""

    result_number = models.IntegerField(null=True, db_column="LBLDGRUNNO", blank=True)
    window_type_number = models.IntegerField(primary_key=True, db_column="LWDTWINNO")
    name = models.CharField(max_length=93, db_column="SWDTTYPE", blank=True)
    shgc = models.FloatField(null=True, db_column="FWDTSHGC", blank=True)
    u_value = models.FloatField(null=True, db_column="FWDTUVALUE", blank=True)
    comment = models.CharField(max_length=765, db_column="SWDTNOTE", blank=True)

    class Meta:
        db_table = "WndwType"
        managed = False
