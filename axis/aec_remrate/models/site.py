"""Django AEC Models - Theses are the source data coming in on the rate database."""


import logging

from django.db import models

__author__ = "Steven Klass"
__date__ = "06/09/2019 13:51"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class Site(models.Model):
    """Site"""

    result_number = models.IntegerField(null=True, db_column="LBLDGRUNNO", blank=True)
    site_label = models.CharField(max_length=93, db_column="SZSELABEL", blank=True)
    city_number = models.IntegerField(null=True, db_column="ISECITY", blank=True)
    elevation = models.FloatField(null=True, db_column="FSEELEV", blank=True)
    num_heating_season_days = models.FloatField(null=True, db_column="NSEHS", blank=True)
    num_cooling_season_days = models.FloatField(null=True, db_column="NSECS", blank=True)
    julian_cooling_day_start = models.FloatField(null=True, db_column="NSECSJSDAY", blank=True)
    heating_days_b65 = models.FloatField(null=True, db_column="NSEDEGDAYH", blank=True)
    cooling_days_b74 = models.FloatField(null=True, db_column="NSEDEGDAYC", blank=True)
    avg_seasonal_heating_temp = models.FloatField(null=True, db_column="FSETAMBHS", blank=True)
    avg_seasonal_cooling_temp = models.FloatField(null=True, db_column="FSETAMBCS", blank=True)
    heating_days_user_editable = models.FloatField(null=True, db_column="FSEHDD65", blank=True)
    cooling_days_user_editable = models.FloatField(null=True, db_column="FSECDH74", blank=True)
    climate_zone = models.CharField(max_length=150, db_column="SCLIMZONE", blank=True)
    rating_number = models.CharField(max_length=93, db_column="SRATENO", blank=True)
    ashrae_weather_and_shielding_factor = models.FloatField(
        null=True, db_column="fASHRAEWSF", blank=True
    )
    annual_windspeed = models.FloatField(null=True, db_column="fAveWindSpd", blank=True)
    annual_ambient_air_temperature = models.FloatField(
        null=True, db_column="fAveAmbAirT", blank=True
    )

    class Meta:
        db_table = "Site"
        managed = False
