"""test_tasks.py - axis"""

__author__ = "Steven K"
__date__ = "1/18/23 11:11"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import datetime
import logging
from unittest import mock

from axis.annotation.models import Annotation
from axis.core.tests.testcases import AxisTestCase
from axis.customer_eto.tests.program_checks.test_eto_2022 import ETO2022ProgramCompleteTestMixin
from axis.gbr.models import GreenBuildingRegistry, GbrStatus
from axis.gbr.tests.mocked_responses import gbr_mocked_response
from axis.home.models import EEPProgramHomeStatus
from axis.home.tasks import certify_single_home

log = logging.getLogger(__name__)


@mock.patch("axis.gbr.gbr.GreenBuildingRegistryAPIConnect.post", side_effect=gbr_mocked_response)
class GBRHomeStatusEPSSerializerTests(ETO2022ProgramCompleteTestMixin, AxisTestCase):
    def test_auto_gbr_creation_process(self, _mock):
        self.assertEqual(self.home_status.certification_date, None)
        self.assertEqual(self.home_status.state, "inspection")
        self.assertEqual(GreenBuildingRegistry.objects.count(), 0)
        # Make the transition
        self.home_status.make_transition("qa_transition")
        self.home_status.refresh_from_db()
        self.assertEqual(self.home_status.state, "qa_pending")
        self.assertEqual(GreenBuildingRegistry.objects.count(), 1)
        self.assertIsNotNone(self.home_status.home.gbr.gbr_id)
        self.assertEqual(self.home_status.home.gbr.status, GbrStatus.LEGACY_IMPORT)

    def test_auto_gbr_no_annotations_creation_process(self, _mock):
        Annotation.objects.all().delete()
        self.assertEqual(self.home_status.certification_date, None)
        self.assertEqual(self.home_status.state, "inspection")
        self.assertEqual(GreenBuildingRegistry.objects.count(), 0)
        # Make the transition
        self.home_status.make_transition("qa_transition")
        self.home_status.refresh_from_db()
        self.assertEqual(self.home_status.state, "qa_pending")
        self.assertEqual(GreenBuildingRegistry.objects.count(), 1)
        self.assertIsNotNone(self.home_status.home.gbr.gbr_id)
        self.assertEqual(self.home_status.home.gbr.status, GbrStatus.PROPERTY_VALID)

    def test_auto_gbr_assessment_creation_process(self, _mock):
        # Setup a basic home with no annotations ready for certification
        Annotation.objects.all().delete()
        EEPProgramHomeStatus.objects.filter(pk=self.home_status.pk).update(
            state="certification_pending",
        )
        gbr = GreenBuildingRegistry.objects.create(
            gbr_id="foo", home=self.home_status.home, status=GbrStatus.PROPERTY_VALID
        )
        self.home_status.refresh_from_db()
        self.assertIsNotNone(self.home_status.home.gbr.gbr_id)
        self.assertEqual(self.home_status.home.gbr.status, GbrStatus.PROPERTY_VALID)

        # Certify and verify that we kick of this thing
        certify_single_home(
            self.provider_user,
            self.home_status,
            datetime.datetime.today(),
            bypass_check=True,  # Skip Gating QA
        )

        self.home_status.refresh_from_db()
        self.assertEqual(self.home_status.state, "complete")

        gbr.refresh_from_db()
        self.assertEqual(gbr.status, GbrStatus.ASSESSMENT_CREATED)
        self.assertIsNotNone(gbr.api_result)
