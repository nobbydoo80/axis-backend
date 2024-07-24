"""Django AEC Models - Theses are the source data coming in on the rate database."""


import logging

from django.db import models

from axis.remrate_data.strings import HEATER_TYPES, FUEL_TYPES, SEEP_HEAT_UNITS

__author__ = "Steven Klass"
__date__ = "06/09/2019 13:51"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class Heater(models.Model):
    """Heaters"""

    result_number = models.IntegerField(null=True, db_column="LBLDGRUNNO", blank=True)
    heater_number = models.FloatField(null=True, db_column="LHETHETNO", blank=True)
    name = models.CharField(max_length=93, db_column="SHETTYPE", blank=True)
    type = models.IntegerField(null=True, db_column="NHETSYSTTP", choices=HEATER_TYPES, blank=True)
    fuel_type = models.IntegerField(
        null=True, db_column="NHETFUELTP", choices=FUEL_TYPES, blank=True
    )
    rated_output_capacity = models.FloatField(null=True, db_column="FHETRATCAP", blank=True)
    seasonal_equipment_efficiency = models.FloatField(null=True, db_column="FHETEFF", blank=True)
    seasonal_equipment_efficiency_unit = models.IntegerField(
        null=True, db_column="NHETEFFUTP", choices=SEEP_HEAT_UNITS, blank=True
    )
    heat_pump_energy = models.FloatField(null=True, db_column="FHETFANPWR", blank=True)
    heat_pump_energy_units = models.IntegerField(null=True, db_column="NHETPMPTYP", blank=True)
    comment = models.CharField(max_length=765, db_column="SHETNOTE", blank=True)
    # -- Not Used ---
    nhetdshtr = models.FloatField(null=True, db_column="NHETDSHTR", blank=True)
    nhetfnctrl = models.IntegerField(null=True, db_column="NHETFNCTRL", blank=True)
    nhetfndef = models.IntegerField(null=True, db_column="NHETFNDEF", blank=True)
    fhetfnhspd = models.FloatField(null=True, db_column="FHETFNHSPD", blank=True)
    fhetfnlspd = models.FloatField(null=True, db_column="FHETFNLSPD", blank=True)
    fhetauxelc = models.FloatField(null=True, db_column="FHETAUXELC", blank=True)
    nhetauxetp = models.IntegerField(null=True, db_column="NHETAUXETP", blank=True)
    nhetauxdef = models.IntegerField(null=True, db_column="NHETAUXDEF", blank=True)
    fhetpmpeng = models.FloatField(null=True, db_column="FHETPMPENG", blank=True)
    fhetrcap17 = models.FloatField(null=True, db_column="FHETRCAP17", blank=True)

    class Meta:
        db_table = "HtgType"
        managed = False
