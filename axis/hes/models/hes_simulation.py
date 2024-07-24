import logging

from functools import cached_property

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils import formats
from simple_history.models import HistoricalRecords
from simulation.enumerations import Orientation
from ..enumerations import NEW, STATUS_CHOICES

__author__ = "Benjamin S"
__date__ = "6/8/2022 09:05"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Benjamin S",
]

log = logging.getLogger(__name__)


class HESSimulation(models.Model):
    """The Results of an HES Simulation"""

    home_status = models.ForeignKey(
        "home.EEPProgramHomeStatus",
        on_delete=models.CASCADE,
        related_name="hes_simulations",
        blank=True,
        null=True,
    )

    simulation_status = models.ForeignKey(
        "HESSimulationStatus",
        on_delete=models.CASCADE,
        related_name="hes_simulations",
        blank=True,
        null=True,
    )

    orientation = models.CharField(
        max_length=64, choices=Orientation.choices, blank=True, null=True
    )

    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default=NEW)

    # If an error occurred while attempting to run this simulation on the Home Energy
    # Score API, then the text of the error will be stored here
    error = models.TextField(blank=True, null=True)

    # The ID assigned the building by the Home Energy Score API
    building_id = models.CharField(max_length=64, blank=True, null=True)
    address = models.CharField(max_length=128, blank=True, null=True)
    city = models.CharField(max_length=32, blank=True, null=True)
    state = models.CharField(max_length=4, blank=True, null=True)
    zip_code = models.CharField(max_length=16, blank=True, null=True)
    conditioned_floor_area = models.IntegerField(blank=True, null=True)
    year_built = models.CharField(max_length=16, blank=True, null=True)
    cooling_present = models.BooleanField(null=True, default=None)
    base_score = models.IntegerField(blank=True, null=True)
    package_score = models.IntegerField(blank=True, null=True)
    cost_savings = models.FloatField(blank=True, null=True)
    assessment_type = models.CharField(max_length=32, blank=True, null=True)
    assessment_date = models.DateField(blank=True, null=True)
    label_number = models.CharField(max_length=32, blank=True, null=True)
    qualified_assessor_id = models.CharField(max_length=32, blank=True, null=True)
    hescore_version = models.CharField(max_length=32, blank=True, null=True)

    utility_electric = models.FloatField(blank=True, null=True)
    utility_natural_gas = models.FloatField(blank=True, null=True)
    utility_fuel_oil = models.FloatField(blank=True, null=True)
    utility_lpg = models.FloatField(blank=True, null=True)
    utility_cord_wood = models.FloatField(blank=True, null=True)
    utility_pellet_wood = models.FloatField(blank=True, null=True)
    utility_generated = models.FloatField(blank=True, null=True)
    estimated_annual_energy_cost = models.FloatField(blank=True, null=True)

    source_energy_total_base = models.FloatField(blank=True, null=True)
    source_energy_asset_base = models.FloatField(blank=True, null=True)

    average_state_cost = models.FloatField(blank=True, null=True)
    average_state_eui = models.FloatField(blank=True, null=True)

    # Extended Data
    weather_station_location = models.CharField(max_length=32, blank=True, null=True)
    create_label_date = models.DateField(blank=True, null=True)

    source_energy_total_package = models.FloatField(blank=True, null=True)
    source_energy_asset_package = models.FloatField(blank=True, null=True)

    # In the HES API, values labeled "base" refer to the home as defined by the assessment.
    # "package" refers to the recommended upgrade package that the HES API generates.
    base_cost = models.FloatField(blank=True, null=True)
    package_cost = models.FloatField(blank=True, null=True)

    site_energy_base = models.FloatField(blank=True, null=True)
    site_energy_package = models.FloatField(blank=True, null=True)

    site_eui_base = models.FloatField(blank=True, null=True)
    site_eui_package = models.FloatField(blank=True, null=True)
    source_eui_base = models.FloatField(blank=True, null=True)
    source_eui_package = models.FloatField(blank=True, null=True)

    carbon_base = models.FloatField(blank=True, null=True)
    carbon_package = models.FloatField(blank=True, null=True)

    utility_electric_base = models.FloatField(blank=True, null=True)
    utility_electric_package = models.FloatField(blank=True, null=True)
    utility_natural_gas_base = models.FloatField(blank=True, null=True)
    utility_natural_gas_package = models.FloatField(blank=True, null=True)
    utility_fuel_oil_base = models.FloatField(blank=True, null=True)
    utility_fuel_oil_package = models.FloatField(blank=True, null=True)
    utility_lpg_base = models.FloatField(blank=True, null=True)
    utility_lpg_package = models.FloatField(blank=True, null=True)
    utility_cord_wood_base = models.FloatField(blank=True, null=True)
    utility_cord_wood_package = models.FloatField(blank=True, null=True)
    utility_pellet_wood_base = models.FloatField(blank=True, null=True)
    utility_pellet_wood_package = models.FloatField(blank=True, null=True)
    utility_generated_base = models.FloatField(blank=True, null=True)
    utility_generated_package = models.FloatField(blank=True, null=True)

    updated_at = models.DateTimeField(auto_now=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    history = HistoricalRecords()

    customer_documents = GenericRelation("filehandling.CustomerDocument")

    class Meta:
        # Any given HESSimulationStatus may have only one simulation record for each orientation
        unique_together = ["simulation_status", "orientation"]

    def normalized_hes_result(self, user=None):
        """Used by a number of tools"""

        sim_date = self.updated_at
        if user:
            sim_date = sim_date.astimezone(user.timezone_preference)

        return {
            "engine": "DOE HES Score",
            "valid": True,
            "version": self.hescore_version,
            "simulation_date": formats.date_format(sim_date, "SHORT_DATETIME_FORMAT"),
            "hers_score": "-",
            "hes_score": self.base_score,
            "costs": {
                "annual_heating_cost": "-",
                "annual_cooling_cost": "-",
                "annual_hot_water_cost": "-",
                "annual_light_and_appliances_cost": "-",
                "annual_generation": "-",
                "total_annual_costs": "-",
                "total_annual_costs_with_generation": self.base_cost,
                "annual_oil_cost": "-",
                "annual_propane_cost": "-",
                "annual_wood_cost": "-",
                "annual_gas_cost": "-",
                "annual_electric_cost": "-",
            },
            "consumption": {
                "total_heating_consumption": "-",
                "total_cooling_consumption": "-",
                "total_hot_water_consumption": "-",
                "total_onsite_generation": self.utility_generated,
                "total_energy_consumption": self.site_energy_package,
                "total_oil_consumption": self.utility_fuel_oil,
                "total_propane_consumption": "-",
                "total_wood_consumption": self.utility_cord_wood,
                "total_gas_consumption": self.utility_natural_gas,
                "total_electric_consumption": self.utility_electric,
            },
        }

    @cached_property
    def company(self) -> str:
        return self.home_status.company
