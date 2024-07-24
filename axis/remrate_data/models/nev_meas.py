"""RemRate Models suitable for use by Axis """


import logging

from django.db import models

__author__ = "Steven Klass"
__date__ = "06/10/2019 11:03"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class NevMeas(models.Model):
    """NevMeas"""

    _source_nev_measure_number = models.IntegerField(unique=True, db_column="lNMNMNo")
    city_name = models.CharField(max_length=300, db_column="sNMCity", blank=True)
    house_type = models.CharField(max_length=300, db_column="sNMHouse", blank=True)
    foundation_type = models.CharField(max_length=300, db_column="sNMFnd", blank=True)
    heating_fuel_type = models.CharField(max_length=300, db_column="sNMHTG", blank=True)
    cooling_type = models.CharField(max_length=300, db_column="sNMCLG", blank=True)
    hot_water_fuel_type = models.CharField(max_length=300, db_column="sNMDHWFT", blank=True)
    measure_type = models.CharField(max_length=300, db_column="sNMMEATYP", blank=True)
    measure_description = models.CharField(max_length=765, db_column="sNMMEADSC", blank=True)
    kwh_savings = models.FloatField(null=True, db_column="fNMKWH", blank=True)
    therm_savings = models.FloatField(null=True, db_column="fNMTherm", blank=True)
