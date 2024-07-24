"""Django AEC Models - Theses are the source data coming in on the rate database."""


import logging

from django.db import models

from axis.remrate_data.strings import HEATING_EFF_UNITS, COOLING_EFF_UNITS, FUEL_TYPES

__author__ = "Steven Klass"
__date__ = "06/09/2019 13:51"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class AirSourceHeatPump(models.Model):
    """Air Source Heat Pumps"""

    result_number = models.IntegerField(null=True, db_column="LBLDGRUNNO", blank=True)
    air_source_heat_pump_number = models.FloatField(null=True, db_column="LASTASTNO", blank=True)
    name = models.CharField(max_length=93, db_column="SASTTYPE", blank=True)
    fuel_type = models.IntegerField(db_column="NASTFUEL", choices=FUEL_TYPES, null=True)
    heating_rated_output_capacity = models.FloatField(null=True, db_column="FASTHCAP47", blank=True)
    heating_efficiency = models.FloatField(null=True, db_column="FASTHEFF", blank=True)
    heating_efficiency_units = models.IntegerField(
        db_column="NASTHEFFU", choices=HEATING_EFF_UNITS, null=True
    )
    cooling_rated_output_capacity = models.FloatField(null=True, db_column="FASTCCAP", blank=True)
    cooling_efficiency = models.FloatField(null=True, db_column="FASTCEFF", blank=True)
    cooling_efficiency_units = models.IntegerField(
        db_column="NASTCEFFU", choices=COOLING_EFF_UNITS, null=True
    )

    # -- Not Used --
    fastshf = models.FloatField(null=True, db_column="FASTSHF", blank=True)
    nastdshtr = models.FloatField(null=True, db_column="NASTDSHTR", blank=True)
    sastnote = models.CharField(max_length=765, db_column="SASTNOTE", blank=True)
    fastbkupcp = models.FloatField(null=True, db_column="FASTBKUPCP", blank=True)
    nastfnctrl = models.IntegerField(null=True, db_column="NASTFNCTRL", blank=True)
    nastfndef = models.IntegerField(null=True, db_column="NASTFNDEF", blank=True)
    fastfnhspd = models.FloatField(null=True, db_column="FASTFNHSPD", blank=True)
    fastfnlspd = models.FloatField(null=True, db_column="FASTFNLSPD", blank=True)
    fasthcap17 = models.FloatField(null=True, db_column="FASTHCAP17", blank=True)

    class Meta:
        db_table = "AshpType"
        managed = False
