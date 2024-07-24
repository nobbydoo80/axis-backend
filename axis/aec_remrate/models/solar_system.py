"""Django AEC Models - Theses are the source data coming in on the rate database."""


import logging

from django.db import models

from axis.remrate_data.strings import SOLAR_TYPES, LOOP_TYPES, SOLAR_ORIENTATION, COLLECTOR_SPECS

__author__ = "Steven Klass"
__date__ = "06/09/2019 13:51"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class SolarSystem(models.Model):
    """Solar System"""

    result_number = models.IntegerField(null=True, db_column="LBLDGRUNNO", blank=True)
    building_number = models.IntegerField(db_column="LBLDGNO")
    type = models.IntegerField(null=True, choices=SOLAR_TYPES, db_column="NASSYSTEM", blank=True)
    collector_loop_type = models.IntegerField(
        null=True, choices=LOOP_TYPES, db_column="NASLOOP", blank=True
    )
    collector_area = models.FloatField(null=True, db_column="FASCOLAREA", blank=True)
    orientation = models.IntegerField(
        null=True, choices=SOLAR_ORIENTATION, db_column="NASOR", blank=True
    )
    tilt = models.FloatField(null=True, db_column="NASTILT", blank=True)
    specs = models.IntegerField(
        null=True, choices=COLLECTOR_SPECS, db_column="NASSPECS", blank=True
    )
    storage_volume = models.FloatField(null=True, db_column="FASSTGVOL", blank=True)
    rating_number = models.CharField(max_length=93, db_column="SASRATENO", blank=True)

    class Meta:
        db_table = "ActSolar"
        managed = False
