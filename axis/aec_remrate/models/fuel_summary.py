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


class FuelSummary(models.Model):
    """Fuel Summary"""

    result_number = models.IntegerField(null=True, db_column="LBLDGRUNNO", blank=True)
    fuel_type = models.IntegerField(null=True, db_column="NFSFUEL", choices=FUEL_TYPES, blank=True)
    fuel_units = models.IntegerField(null=True, db_column="NFSUNITS", blank=True)
    heating_cons = models.FloatField(null=True, db_column="FFSHCONS", blank=True)
    cooling_cons = models.FloatField(null=True, db_column="FFSCCONS", blank=True)
    hot_water_cons = models.FloatField(null=True, db_column="FFSWCONS", blank=True)
    lights_and_appliances_cons = models.FloatField(null=True, db_column="FFSLACONS", blank=True)
    total_cost = models.FloatField(null=True, db_column="FFSTOTCOST", blank=True)
    photo_voltaics = models.FloatField(null=True, db_column="FFSPVCONS", blank=True)
    rating_number = models.CharField(max_length=93, db_column="SRATENO", blank=True)

    class Meta:
        db_table = "FuelSum"
