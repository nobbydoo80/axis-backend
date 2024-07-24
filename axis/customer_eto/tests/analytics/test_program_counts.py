"""program_counts.py - Axis"""

__author__ = "Steven K"
__date__ = "11/2/20 11:13"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import datetime
import logging

from django.utils.timezone import now

from axis.core.tests.testcases import AxisTestCase
from axis.customer_eto.analytics import get_certified_program_counts
from axis.customer_eto.tests.analytics.test_appliances import ETO2022ProgramAnalyticsTestMixin
from axis.checklist.collection.test_mixins import CollectionRequestMixin
from axis.home.models import EEPProgramHomeStatus

log = logging.getLogger(__name__)


class ProgramCountAnalyticsTests(
    ETO2022ProgramAnalyticsTestMixin, CollectionRequestMixin, AxisTestCase
):
    def setUp(self):
        self.complete = EEPProgramHomeStatus.objects.get(state="complete")
        self.home_status = EEPProgramHomeStatus.objects.exclude(state="complete").get()
        self.rater_id = self.home_status.company_id
        self.builder_id = self.home_status.home.get_builder().id
        self.complete_sim = self.complete.floorplan.simulation

    def test_get_certified_program_counts(self):
        """Valid window"""
        self.assertIsNotNone(self.rater_id)
        self.assertIsNotNone(self.builder_id)

        self.complete.certification_date = now() - datetime.timedelta(days=180)
        self.complete.save()
        self.assertFalse(self.complete.home.bulk_uploaded)
        data = get_certified_program_counts(self.rater_id, self.builder_id)
        self.assertEqual(data["rater_builder_completed_homes"], 1)

    def test_get_certified_program_counts_outside_window(self):
        """Outside Valid window"""
        self.complete.certification_date = now() - datetime.timedelta(days=370)
        self.complete.save()
        self.assertFalse(self.complete.home.bulk_uploaded)

        data = get_certified_program_counts(self.rater_id, self.builder_id)
        self.assertEqual(data["rater_builder_completed_homes"], 0)
