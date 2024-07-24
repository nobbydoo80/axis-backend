import logging
import re
from io import StringIO
from unittest import mock

from django.core.management import call_command

from axis.core.tests.testcases import AxisTestCase
from axis.hes.models import HESSimulationStatus
from axis.hes.tests.mixins import HESTestMixin
from .mocked_responses import doe_mocked_soap_responses

__author__ = "Benjamin S"
__date__ = "6/29/2022 14:50"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Benjamin S",
]

log = logging.getLogger(__name__)


class GenerateHesScoreTest(HESTestMixin, AxisTestCase):
    """Tests of the generate_hes_score command bundled with this package"""

    @mock.patch("axis.hes.hes.DOEInterface.get", side_effect=doe_mocked_soap_responses)
    @mock.patch("axis.hes.hes.DOEInterface.post", side_effect=doe_mocked_soap_responses)
    def test_basic_execution(self, *args):
        """Verify that the command works as expected with typical inputs"""
        result = self._invoke(home_status_ids=self.home_status.pk)
        self.assertIn(f"Task has been created", result)

        match = re.search(r"HESSimulationStatus (\d+)", result)
        self.assertIsNotNone(match)
        hes_simulation_status_id = match.group(1)

        simulation_status = HESSimulationStatus.objects.get(pk=hes_simulation_status_id)
        self.assertEqual(simulation_status.company, self.home_status.company)

        self.assertEqual(
            simulation_status.rem_simulation, self.home_status.floorplan.remrate_target
        )

        self.assertEqual(simulation_status.home_status, self.home_status)

    def test_invalid_command_execution(self):
        """Verify that the command generates expected errors when invoked incorrectly"""

        # We should get an exception if we invoke the command with no arguments
        with self.assertRaises(Exception):
            self._invoke()

    @staticmethod
    def _invoke(**kwargs) -> str:
        out = StringIO()
        call_command("generate_hes_score", stdout=out, **kwargs)
        return out.getvalue()
