"""Django AEC Models - Theses are the source data coming in on the rate database."""


import logging

from django.db import models

from axis.remrate_data.strings import DUCT_LOCATIONS

__author__ = "Steven Klass"
__date__ = "06/09/2019 13:51"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class Duct(models.Model):
    """Duct Information"""

    result_number = models.IntegerField(null=True, db_column="LBLDGRUNNO", blank=True)
    building_number = models.IntegerField(db_column="LBLDGNO")
    duct_system_number = models.IntegerField(primary_key=True, db_column="LDUDSNO")
    area = models.FloatField(null=True, db_column="FDUAREA", blank=True)
    location = models.IntegerField(
        null=True, choices=DUCT_LOCATIONS, db_column="NDULOC", blank=True
    )
    insulation = models.FloatField(null=True, db_column="FDUINS", blank=True)
    type = models.IntegerField(
        null=True, choices=((1, "Supply"), (2, "Return")), db_column="NDUDCTTYPE", blank=True
    )
    rating_number = models.CharField(max_length=93, db_column="SDURATENO", blank=True)

    class Meta:
        db_table = "Duct"
        managed = False
