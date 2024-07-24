"""Django AEC Models - Theses are the source data coming in on the rate database."""


import logging

from django.db import models

from axis.remrate_data.strings import FUEL_TYPES

__author__ = "Steven Klass"
__date__ = "06/09/2019 13:51"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class DualFuelHeatPump(models.Model):
    """Dual Fuel Heat Pumps"""

    result_number = models.IntegerField(null=True, db_column="LBLDGRUNNO", blank=True)
    dual_fuel_heat_pump_number = models.FloatField(null=True, db_column="LDFTDFTNO", blank=True)
    name = models.CharField(max_length=93, db_column="SDFTTYPE", blank=True)
    fuel_type = models.IntegerField(null=True, db_column="NDFTFUEL", choices=FUEL_TYPES, blank=True)
    backup_fuel_type = models.IntegerField(
        null=True, db_column="NDFTBFUEL", choices=FUEL_TYPES, blank=True
    )
    heating_rated_output_capacity = models.FloatField(null=True, db_column="FDFTHCAP47", blank=True)
    cooling_rated_output_capacity = models.FloatField(null=True, db_column="FDFTCCAP", blank=True)
    # -- Not Used --
    fdfthhspf = models.FloatField(null=True, db_column="FDFTHHSPF", blank=True)
    ndftbeffu = models.FloatField(null=True, db_column="NDFTBEFFU", blank=True)
    fdftbseff = models.FloatField(null=True, db_column="FDFTBSEFF", blank=True)
    fdftbcap = models.FloatField(null=True, db_column="FDFTBCAP", blank=True)
    fdftcseer = models.FloatField(null=True, db_column="FDFTCSEER", blank=True)
    fdftcshf = models.FloatField(null=True, db_column="FDFTCSHF", blank=True)
    ndftdshtr = models.FloatField(null=True, db_column="NDFTDSHTR", blank=True)
    fdftswitch = models.FloatField(null=True, db_column="FDFTSWITCH", blank=True)
    ndftfnctrl = models.IntegerField(null=True, db_column="NDFTFNCTRL", blank=True)
    ndftfndef = models.IntegerField(null=True, db_column="NDFTFNDEF", blank=True)
    fdftfnhspd = models.FloatField(null=True, db_column="FDFTFNHSPD", blank=True)
    fdftfnlspd = models.FloatField(null=True, db_column="FDFTFNLSPD", blank=True)
    sdftnote = models.CharField(max_length=765, db_column="SDFTNOTE", blank=True)

    class Meta:
        db_table = "DfhpType"
        managed = False
