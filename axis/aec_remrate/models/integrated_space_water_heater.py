"""Django AEC Models - Theses are the source data coming in on the rate database."""


import logging

from django.db import models

from axis.remrate_data.strings import ISWH_TYPES, FUEL_TYPES

__author__ = "Steven Klass"
__date__ = "06/09/2019 13:51"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class IntegratedSpaceWaterHeater(models.Model):
    """Integrated Space / Water Heaters"""

    result_number = models.IntegerField(null=True, db_column="LBLDGRUNNO", blank=True)
    integrated_space_water_heater_number = models.IntegerField(
        null=True, db_column="LHTDHTDNO", blank=True
    )
    name = models.CharField(max_length=93, db_column="SHTDTYPE", blank=True)
    type = models.IntegerField(null=True, db_column="NHTDSYSTTP", choices=ISWH_TYPES, blank=True)
    fuel_type = models.FloatField(null=True, db_column="NHTDFUEL", choices=FUEL_TYPES, blank=True)
    rated_output_capacity = models.FloatField(null=True, db_column="FHTDRATCAP", blank=True)
    # -- Not Used --
    nhtddisttp = models.FloatField(null=True, db_column="NHTDDISTTP", blank=True)
    fhtdsphte = models.FloatField(null=True, db_column="FHTDSPHTE", blank=True)
    fhtdwhef = models.FloatField(null=True, db_column="FHTDWHEF", blank=True)
    fhtdwhre = models.FloatField(null=True, db_column="FHTDWHRE", blank=True)
    fhtdtnksz = models.FloatField(null=True, db_column="FHTDTNKSZ", blank=True)
    fhtdtnkin = models.FloatField(null=True, db_column="FHTDTNKIN", blank=True)
    nhtdfnctrl = models.IntegerField(null=True, db_column="NHTDFNCTRL", blank=True)
    nhtdfndef = models.IntegerField(null=True, db_column="NHTDFNDEF", blank=True)
    fhtdfnhspd = models.FloatField(null=True, db_column="FHTDFNHSPD", blank=True)
    fhtdfnlspd = models.FloatField(null=True, db_column="FHTDFNLSPD", blank=True)
    shtdnote = models.CharField(max_length=765, db_column="SHTDNOTE", blank=True)
    fhtdauxelc = models.FloatField(null=True, db_column="FHTDAUXELC", blank=True)
    nhtdauxetp = models.IntegerField(null=True, db_column="NHTDAUXETP", blank=True)
    nhtdauxdef = models.IntegerField(null=True, db_column="NHTDAUXDEF", blank=True)

    class Meta:
        db_table = "HtDhType"
        managed = False
