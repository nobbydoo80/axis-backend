"""Django AEC Models - Theses are the source data coming in on the rate database."""


import logging

from django.db import models

from axis.remrate_data.strings import H2O_HEATER_TYPES, FUEL_TYPES

__author__ = "Steven Klass"
__date__ = "06/09/2019 13:51"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class HotWaterHeater(models.Model):
    """Hot Water Heaters"""

    result_number = models.IntegerField(null=True, db_column="LBLDGRUNNO", blank=True)
    hot_water_heater_number = models.FloatField(null=True, db_column="LDETDETNO", blank=True)
    name = models.CharField(max_length=93, db_column="SDETTYPE", blank=True)
    type = models.IntegerField(
        null=True, db_column="NDETSYSTTP", choices=H2O_HEATER_TYPES, blank=True
    )
    fuel_type = models.IntegerField(
        null=True, db_column="NDETFUELTP", choices=FUEL_TYPES, blank=True
    )
    size = models.FloatField(null=True, db_column="FDETTNKVOL", blank=True)
    extra_tank_insulation_r_value = models.FloatField(null=True, db_column="FDETTNKINS", blank=True)
    energy_factor = models.FloatField(null=True, db_column="FDETENERGY", blank=True)
    recovery_efficiency = models.FloatField(null=True, db_column="FDETRECEFF", blank=True)
    comment = models.CharField(max_length=765, db_column="SDETNOTE", blank=True)

    class Meta:
        db_table = "DhwType"
        managed = False
