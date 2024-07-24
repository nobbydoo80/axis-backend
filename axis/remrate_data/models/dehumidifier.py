"""dehumidifier.py - Axis"""

__author__ = "Steven K"
__date__ = "7/22/21 10:31"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from django.db import models

from ..strings import FUEL_TYPES, HUMIDIFIER_TYPES

log = logging.getLogger(__name__)


class Dehumidifier(models.Model):
    """Dehumidifier"""

    simulation = models.ForeignKey("Simulation", on_delete=models.CASCADE)
    _result_number = models.IntegerField(db_column="lBldgRunNo")
    _source_humidifier_number = models.FloatField(db_column="lDhuEqKey")
    name = models.CharField(max_length=32, db_column="sName", blank=True, null=True)
    type = models.IntegerField(null=True, db_column="nSystem", choices=HUMIDIFIER_TYPES)
    fuel_type = models.IntegerField(null=True, db_column="nFuel", choices=FUEL_TYPES)
    capacity = models.FloatField(null=True, db_column="fCapacity")
    efficiency = models.FloatField(
        null=True, db_column="fEfficiency", help_text="Unit is IEF which is liters/kWh"
    )
    note = models.CharField(max_length=255, db_column="sNote", blank=True, null=True)
