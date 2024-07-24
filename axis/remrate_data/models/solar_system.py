"""RemRate Models suitable for use by Axis """

import logging

from django.db import models

from ..strings import SOLAR_TYPES, LOOP_TYPES, SOLAR_ORIENTATION, COLLECTOR_SPECS

__author__ = "Steven Klass"
__date__ = "06/10/2019 11:03"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class SolarSystem(models.Model):
    """ActSolar - Solar Systems"""

    simulation = models.OneToOneField("Simulation", on_delete=models.CASCADE)
    building = models.OneToOneField("Building", on_delete=models.CASCADE)
    _result_number = models.IntegerField(db_column="lBldgRunNo")
    _building_number = models.IntegerField(db_column="lBldgNo")
    type = models.IntegerField(null=True, choices=SOLAR_TYPES, db_column="nASSystem")
    collector_loop_type = models.IntegerField(null=True, choices=LOOP_TYPES, db_column="nASLoop")
    collector_area = models.FloatField(null=True, db_column="fASColArea")
    orientation = models.IntegerField(null=True, choices=SOLAR_ORIENTATION, db_column="nASOr")
    tilt = models.FloatField(null=True, db_column="nASTilt")
    specs = models.IntegerField(null=True, choices=COLLECTOR_SPECS, db_column="nASSpecs")
    storage_volume = models.FloatField(null=True, db_column="fASStgVol")
    rating_number = models.CharField(max_length=93, db_column="sASRateNo")

    def __str__(self):
        volume = " ({} Gal)".format(self.storage_volume) if self.storage_volume else ""
        return "{} facing {} from {} sq/ft{}".format(
            self.get_type_display(), self.get_orientation_display(), self.collector_area, volume
        )
