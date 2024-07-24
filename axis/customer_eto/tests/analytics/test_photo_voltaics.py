"""test_photo_voltaics.py - Axis"""

__author__ = "Steven K"
__date__ = "3/17/22 15:33"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
from unittest import mock

from axis.gbr.tests.mocked_responses import gbr_mocked_response
from simulation.enumerations import PvCapacity
from simulation.tests.factories import simulation_factory

from axis.core.tests.testcases import AxisTestCase
from axis.customer_eto.analytics.photo_voltaics import eto_simulation_pv_characteristics

log = logging.getLogger(__name__)


class AnalyticsPVTests(AxisTestCase):
    @classmethod
    @mock.patch(
        "axis.gbr.gbr.GreenBuildingRegistryAPIConnect.post", side_effect=gbr_mocked_response
    )
    def setUpTestData(cls, _mock):
        super(AnalyticsPVTests, cls).setUpTestData()
        cls.simulation = simulation_factory(
            photovoltaic_count=2,
            photovoltaic__capacity=3,
            photovoltaic__capacity_units=PvCapacity.KWDC,
        )

    def test_eto_simulation_pv_characteristics_mismatch(self):
        result = eto_simulation_pv_characteristics(self.simulation.id, {"input": "6.1"})
        self.assertIn("6.0 kW", result["model_pv_characteristics"]["simulation"])
        self.assertIn("6.1 kW", result["model_pv_characteristics"]["checklist"])
        self.assertIsNotNone(result["model_pv_characteristics"]["warning"])
        self.assertEqual(len(result["model_pv_characteristics"]["warnings"]), 1)

    def test_eto_simulation_pv_characteristics_good_simulation(self):
        result = eto_simulation_pv_characteristics(self.simulation.id, {"input": "6.0001"})
        self.assertIn("6.0 kW", result["model_pv_characteristics"]["simulation"])
        self.assertIn("6.0 kW", result["model_pv_characteristics"]["checklist"])
        self.assertIsNone(result["model_pv_characteristics"]["warning"])
        self.assertEqual(result["model_pv_characteristics"]["warnings"], [])

        result = eto_simulation_pv_characteristics(self.simulation.id, {"input": "6.0 kW"})
        self.assertIn("6.0 kW", result["model_pv_characteristics"]["simulation"])
        self.assertIn("6.0 kW", result["model_pv_characteristics"]["checklist"])
        self.assertIsNone(result["model_pv_characteristics"]["warning"])
        self.assertEqual(result["model_pv_characteristics"]["warnings"], [])

    def test_eto_simulation_pv_characteristics_missing_data(self):
        result = eto_simulation_pv_characteristics(None, None)
        self.assertEqual(result["model_pv_characteristics"]["simulation"], None)
        self.assertEqual(result["model_pv_characteristics"]["checklist"], None)
        self.assertIsNone(result["model_pv_characteristics"]["warning"])
        self.assertEqual(result["model_pv_characteristics"]["warnings"], [])

        result = eto_simulation_pv_characteristics(self.simulation.id + 100, None)
        self.assertEqual(result["model_pv_characteristics"]["simulation"], None)
        self.assertEqual(result["model_pv_characteristics"]["checklist"], None)
        self.assertIsNone(result["model_pv_characteristics"]["warning"])
        self.assertEqual(result["model_pv_characteristics"]["warnings"], [])

        result = eto_simulation_pv_characteristics(None, {"input": None})
        self.assertEqual(result["model_pv_characteristics"]["simulation"], None)
        self.assertEqual(result["model_pv_characteristics"]["checklist"], None)
        self.assertIsNone(result["model_pv_characteristics"]["warning"])
        self.assertEqual(result["model_pv_characteristics"]["warnings"], [])

    def test_eto_simulation_pv_characteristics_bad_input_data(self):
        result = eto_simulation_pv_characteristics(self.simulation.id, {"input": "-"})
        self.assertEqual(result["model_pv_characteristics"]["simulation"], None)
        self.assertEqual(result["model_pv_characteristics"]["checklist"], None)
        self.assertIn("Invalid", result["model_pv_characteristics"]["warnings"][0])
        self.assertIn("Invalid", result["model_pv_characteristics"]["warning"])
