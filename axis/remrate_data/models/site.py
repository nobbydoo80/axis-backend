"""RemRate Models suitable for use by Axis """


import logging

from django.db import models

from ..utils import compare_sets

__author__ = "Steven Klass"
__date__ = "06/10/2019 11:03"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class Site(models.Model):
    """Site"""

    simulation = models.OneToOneField("Simulation", on_delete=models.CASCADE)
    _result_number = models.IntegerField(db_column="lBldgRunNo")

    site_label = models.CharField(max_length=93, db_column="szSELabel", blank=True)
    city_number = models.IntegerField(null=True, db_column="ISECity", blank=True)
    elevation = models.FloatField(null=True, db_column="fSEElev", blank=True)
    num_heating_season_days = models.IntegerField(null=True, db_column="nSEHS", blank=True)
    num_cooling_season_days = models.IntegerField(null=True, db_column="nSECS", blank=True)
    julian_cooling_day_start = models.IntegerField(null=True, db_column="nSECSJSDay", blank=True)
    heating_days_b65 = models.IntegerField(null=True, db_column="nSEDegDayh", blank=True)
    cooling_days_b74 = models.IntegerField(null=True, db_column="nSEDegDayc", blank=True)
    avg_seasonal_heating_temp = models.FloatField(null=True, db_column="fSETAmbHS", blank=True)
    avg_seasonal_cooling_temp = models.FloatField(null=True, db_column="fSETambCS", blank=True)
    heating_days_user_editable = models.FloatField(null=True, db_column="fSEHDD65", blank=True)
    cooling_days_user_editable = models.FloatField(null=True, db_column="fSECDH74", blank=True)
    climate_zone = models.CharField(max_length=150, db_column="sCLIMZONE", blank=True, null=True)
    rating_number = models.CharField(max_length=93, db_column="sRateNo", blank=True)
    ashrae_weather_and_shielding_factor = models.FloatField(
        null=True, db_column="fASHRAEWSF", blank=True
    )
    annual_windspeed = models.FloatField(null=True, db_column="fAveWindSpd", blank=True)
    annual_ambient_air_temperature = models.FloatField(
        null=True, db_column="fAveAmbAirT", blank=True
    )

    def compare_to_home_status(self, home_status, **_unused):
        """Compare the elements to the home status"""

        match_items = [
            (
                self.climate_zone,
                "{}".format(home_status.home.city.county.climate_zone),
                str,
                "Home: Climate Zone",
                "warning",
            ),
        ]
        return compare_sets(match_items)
