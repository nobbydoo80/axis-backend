"""water_loop_heat_pump.py - Axis"""

__author__ = "Steven K"
__date__ = "7/22/21 12:50"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from django.db import models

log = logging.getLogger(__name__)


class WaterLoopHeatPump(models.Model):
    """This is used in a shared Equipment when a cooling tower is used."""

    simulation = models.ForeignKey("Simulation", on_delete=models.CASCADE)
    _result_number = models.IntegerField(db_column="lBldgRunNo")
    _source_water_loop_heat_pump_number = models.IntegerField(db_column="lWlhpEqKey")
    name = models.CharField(max_length=31, db_column="sName", blank=True, null=True)
    heating_efficiency = models.FloatField(null=True, db_column="fHtgEff", help_text="COP")
    heating_capacity = models.FloatField(null=True, db_column="fHtgCap", help_text="kBtuh")
    cooling_efficiency = models.FloatField(null=True, db_column="fClgEff", help_text="EER")
    cooling_capacity = models.FloatField(null=True, db_column="fClgCap", help_text="kBtuh")
    sensible_heat_fraction = models.FloatField(null=True, db_column="fClgSHF")
    note = models.CharField(null=True, max_length=765, db_column="sNote", blank=True)
