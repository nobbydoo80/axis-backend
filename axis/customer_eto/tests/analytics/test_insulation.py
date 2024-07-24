"""insulation.py - Axis"""

__author__ = "Steven K"
__date__ = "11/2/20 10:28"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from axis.core.tests.testcases import AxisTestCase
from axis.customer_eto.analytics import get_insulation_analytics
from axis.customer_eto.tests.analytics.test_appliances import ETO2022ProgramAnalyticsTestMixin
from axis.checklist.collection.test_mixins import CollectionRequestMixin
from axis.home.models import EEPProgramHomeStatus

log = logging.getLogger(__name__)


class InsulationAnalyticsTests(
    ETO2022ProgramAnalyticsTestMixin, CollectionRequestMixin, AxisTestCase
):
    def setUp(self):
        self.complete = EEPProgramHomeStatus.objects.get(state="complete")
        self.home_status = EEPProgramHomeStatus.objects.exclude(state="complete").get()
        self.simulation = self.home_status.floorplan.simulation
        self.complete_sim = self.complete.floorplan.simulation
        self.analysis = self.simulation.analyses.first().type

    def test_get_insulation_analytics(self):
        input_data = {
            "simulation_id": self.simulation.id,
            "similar_insulation_simulation_ids": [self.complete_sim.id],
            "analysis_type": self.analysis,
            "similar_insulation_simulation_last_18mo_ids": [self.complete_sim.id],
        }

        data = get_insulation_analytics(**input_data)
        expected = {
            "total_frame_floor_area",
            "dominant_floor_insulation_r_value",
            "total_slab_floor_area",
            "dominant_slab_insulation_r_value",
            "total_above_grade_wall_area",
            "dominant_above_grade_wall_r_value",
            "total_ceiling_area",
            "dominant_ceiling_r_value",
            "dominant_window_u_value",
            "dominant_window_shgc_value",
            "total_window_area",
        }
        self.assertEqual(set(list(data.keys())), expected)
