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


class Version(models.Model):
    """Version"""

    lid = models.IntegerField(primary_key=True, db_column="lID")
    major = models.IntegerField(null=True, db_column="lVersion", blank=True)
    minor = models.IntegerField(null=True, db_column="lMinor", blank=True)

    class Meta:
        db_table = "Version"
        managed = False
