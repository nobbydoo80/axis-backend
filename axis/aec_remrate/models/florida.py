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


class Florida(models.Model):
    """Florida - Results"""

    result_number = models.IntegerField(db_column="LBLDGRUNNO")
    building_number = models.IntegerField(db_column="LBLDGNO")
    type = models.IntegerField(db_column="NTYPE", blank=True)
    worst_case = models.IntegerField(db_column="NWORSTCASE", blank=True)
    permit_off = models.CharField(max_length=51, db_column="SPERMITOFF", blank=True)
    permit_number = models.CharField(max_length=51, db_column="SPERMITNO", blank=True)
    juristdiction = models.CharField(max_length=51, db_column="SJURISDCTN", blank=True)
    rating_number = models.CharField(max_length=31, db_column="SRATENO", blank=True)

    class Meta:
        db_table = "Florida"
        managed = False
