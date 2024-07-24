"""RemRate Models suitable for use by Axis """


import logging

from django.db import models

__author__ = "Steven Klass"
__date__ = "06/10/2019 11:03"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class Version(models.Model):
    """Version - Version"""

    lid = models.IntegerField(primary_key=True, db_column="lID")
    major = models.IntegerField(null=True, db_column="lVersion", blank=True)
    minor = models.IntegerField(null=True, db_column="lMinor", blank=True)
