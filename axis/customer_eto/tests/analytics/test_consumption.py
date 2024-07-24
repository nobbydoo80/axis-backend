"""consumption.py - Axis"""


__author__ = "Steven K"
__date__ = "10/30/20 10:50"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from axis.checklist.collection.test_mixins import CollectionRequestMixin
from axis.core.tests.testcases import AxisTestCase
from axis.customer_eto.analytics import get_output_analytics
from axis.customer_eto.tests.analytics.test_appliances import ETO2022ProgramAnalyticsTestMixin
from axis.home.models import EEPProgramHomeStatus

log = logging.getLogger(__name__)


class ConsumptionAnalyticsTests(
    ETO2022ProgramAnalyticsTestMixin, CollectionRequestMixin, AxisTestCase
):
    def setUp(self):
        self.complete = EEPProgramHomeStatus.objects.get(state="complete")
        self.home_status = EEPProgramHomeStatus.objects.exclude(state="complete").get()
        self.simulation = self.home_status.floorplan.simulation
        self.similar_simulations = [self.complete.floorplan.simulation]
        self.analysis = self.simulation.analyses.first().type

    def test_get_output_analytics(self):
        input_data = {
            "simulation_id": self.simulation.id,
            "similar_total_simulation_ids": [x.id for x in self.similar_simulations],
            "analysis_type": self.analysis,
            "similar_total_simulation_last_18mo_ids": [x.id for x in self.similar_simulations],
        }
        data = get_output_analytics(**input_data)
        self.assertEqual(len(data.keys()), 8)
        for k, v in data.items():
            self.assertTrue(isinstance(v, dict))
