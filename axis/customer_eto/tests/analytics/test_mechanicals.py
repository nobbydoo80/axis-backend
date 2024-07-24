"""mechanicals.py - Axis"""

__author__ = "Steven K"
__date__ = "11/2/20 10:40"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from axis.core.tests.testcases import AxisTestCase
from axis.customer_eto.analytics import (
    get_mechanical_analytics,
    eto_heating_load_allocations,
    get_mechanical_water_analytics,
)
from axis.customer_eto.tests.analytics.test_appliances import (
    ETO2022ProgramAnalyticsTestMixin,
)
from axis.checklist.collection.test_mixins import CollectionRequestMixin
from axis.home.models import EEPProgramHomeStatus

log = logging.getLogger(__name__)


class MechanicalsAnalyticsTests(
    ETO2022ProgramAnalyticsTestMixin, CollectionRequestMixin, AxisTestCase
):
    def setUp(self):
        self.complete = EEPProgramHomeStatus.objects.get(state="complete")
        self.home_status = EEPProgramHomeStatus.objects.exclude(state="complete").get()
        self.simulation = self.home_status.floorplan.simulation
        self.complete_sim = self.complete.floorplan.simulation
        self.analysis = self.simulation.analyses.first().type

    def test_get_mechanical_analytics(self):
        input_data = {
            "simulation_id": self.simulation.id,
            "similar_heating_simulation_ids": [self.complete_sim.id],
            "analysis_type": self.analysis,
            "similar_heating_simulation_last_18mo_ids": [self.complete_sim.id],
        }

        data = get_mechanical_analytics(**input_data)
        expected = {
            "air_conditioner_cooling_capacity",
            "ground_source_heat_pump_cooling_efficiency",
            "air_source_heat_pump_heating_capacity",
            "air_source_heat_pump_cooling_efficiency",
            "heater_heating_efficiency",
            "air_source_heat_pump_heating_efficiency",
            "heater_heating_capacity",
            "ground_source_heat_pump_heating_efficiency",
            "ground_source_heat_pump_cooling_capacity",
            "air_source_heat_pump_cooling_capacity",
            "ground_source_heat_pump_heating_capacity",
            "air_conditioner_cooling_efficiency",
        }
        self.assertEqual(set(list(data.keys())), expected)

    def test_get_mechanical_water_analytics(self):
        input_data = {
            "simulation_id": self.simulation.id,
            "similar_hot_water_simulation_ids": [self.complete_sim.id],
            "analysis_type": self.analysis,
            "similar_hot_water_simulation_last_18mo_ids": [self.complete_sim.id],
        }
        data = get_mechanical_water_analytics(**input_data)
        expected = {
            "water_heater_tank_size",
            "water_heater_energy_factor",
        }
        self.assertEqual(set(list(data.keys())), expected)

    def test_eto_heating_load_allocations(self):
        data = eto_heating_load_allocations(simulation_id=self.simulation.id)
        self.assertIn("heating_load_allocations", data)
        self.assertEqual(data["heating_load_allocations"]["warning"], None)

    def test_eto_heating_load_allocations_warning(self):
        self.simulation.mechanical_equipment.filter(heater__isnull=False).update(
            heating_percent_served=5
        )
        data = eto_heating_load_allocations(simulation_id=self.simulation.id)
        self.assertIn("heating_load_allocations", data)
        self.assertIsNotNone(data["heating_load_allocations"]["warning"])
