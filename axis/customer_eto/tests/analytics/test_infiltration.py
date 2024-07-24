"""infiltration.py - Axis"""

__author__ = "Steven K"
__date__ = "10/30/20 11:10"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from axis.core.tests.testcases import AxisTestCase
from axis.customer_eto.analytics import get_duct_analytics, get_infiltration_analytics
from axis.customer_eto.tests.analytics.test_appliances import ETO2022ProgramAnalyticsTestMixin
from axis.home.models import EEPProgramHomeStatus

log = logging.getLogger(__name__)


class InfitrationAnalyticsTests(ETO2022ProgramAnalyticsTestMixin, AxisTestCase):
    def setUp(self):
        self.complete = EEPProgramHomeStatus.objects.get(state="complete")
        self.home_status = EEPProgramHomeStatus.objects.exclude(state="complete").get()
        self.simulation = self.home_status.floorplan.simulation
        self.similar_simulations = [self.complete.floorplan.simulation]
        self.analysis = self.simulation.analyses.first().type

    def test_get_duct_analytics(self):
        input_data = {
            "simulation_id": self.simulation.id,
            "similar_heating_simulation_ids": [x.id for x in self.similar_simulations],
            "analysis_type": self.analysis,
            "similar_heating_simulation_last_18mo_ids": [x.id for x in self.similar_simulations],
        }
        data = get_duct_analytics(**input_data)
        self.assertEqual(len(data.keys()), 6)
        for k, v in data.items():
            self.assertTrue(isinstance(v, dict))

    def test_get_infiltration_analytics(self):
        input_data = {
            "simulation_id": self.simulation.id,
            "similar_insulation_simulation_ids": [x.id for x in self.similar_simulations],
            "analysis_type": self.analysis,
            "similar_insulation_simulation_last_18mo_ids": [x.id for x in self.similar_simulations],
        }
        data = get_infiltration_analytics(**input_data)
        self.assertEqual(len(data.keys()), 1)
        for k, v in data.items():
            self.assertTrue(isinstance(v, dict))
