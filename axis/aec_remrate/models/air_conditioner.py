"""Django AEC Models - Theses are the source data coming in on the rate database."""


import logging

from django.db import models

from axis.remrate_data.strings import COOLING_TYPES, FUEL_TYPES, SEEP_UNITS

__author__ = "Steven Klass"
__date__ = "06/09/2019 13:51"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class AirConditioner(models.Model):
    """Air Conditioners"""

    result_number = models.IntegerField(null=True, db_column="LBLDGRUNNO", blank=True)
    air_conditioner_number = models.FloatField(null=True, db_column="LCETCETNO", blank=True)
    name = models.CharField(max_length=93, db_column="SCETTYPE", blank=True)
    type = models.IntegerField(null=True, db_column="NCETSYSTTP", choices=COOLING_TYPES, blank=True)
    fuel_type = models.IntegerField(
        null=True, db_column="NCETFUELTP", choices=FUEL_TYPES, blank=True
    )
    rated_output_capacity = models.FloatField(null=True, db_column="FCETRATCAP", blank=True)
    seasonal_equipment_efficiency = models.FloatField(null=True, db_column="FCETEFF", blank=True)
    sensible_heat_fraction = models.FloatField(null=True, db_column="FCETSHF", blank=True)
    seasonal_equipment_efficiency_unit = models.IntegerField(
        null=True, choices=SEEP_UNITS, db_column="NCETEFFUTP", blank=True
    )
    comment = models.CharField(max_length=765, db_column="SCETNOTE", blank=True)
    heat_pump_energy = models.FloatField(null=True, db_column="FCETFANPWR", blank=True)
    heat_pump_energy_units = models.IntegerField(null=True, db_column="NCETPMPTYP", blank=True)

    # -- Not Used --
    ncetdshtr = models.FloatField(null=True, db_column="NCETDSHTR", blank=True)
    ncetfnctrl = models.IntegerField(null=True, db_column="NCETFNCTRL", blank=True)
    ncetfndef = models.IntegerField(null=True, db_column="NCETFNDEF", blank=True)
    fcetfnhspd = models.FloatField(null=True, db_column="FCETFNHSPD", blank=True)
    fcetfnlspd = models.FloatField(null=True, db_column="FCETFNLSPD", blank=True)
    fcetpmpeng = models.FloatField(null=True, db_column="FCETPMPENG", blank=True)
    ncetfandef = models.IntegerField(null=True, db_column="NCETFANDEF", blank=True)

    class Meta:
        db_table = "ClgType"
        managed = False
