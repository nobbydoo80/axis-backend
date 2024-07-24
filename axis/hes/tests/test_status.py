"""test_status.py: Django Test the utils status."""
import json
import logging
from unittest import mock

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from axis.company.models import Company
from axis.core.tests.testcases import AxisTestCase
from axis.hes.models import HESSimulationStatus, HESSimulation
from axis.hes.tests.mixins import HESTestMixin
from axis.hes.tests.mocked_responses import doe_mocked_soap_responses, validation_mock
from axis.hes.utils import get_hes_status
from axis.home.models import EEPProgramHomeStatus
from axis.remrate_data.models import Simulation
from axis.remrate_data.tests.factories import simulation_factory

__author__ = "Steven K"
__date__ = "11/25/2019 14:50"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

log = logging.getLogger(__name__)


class HESStatusTest(HESTestMixin, AxisTestCase):
    """Verifies the values returned by the get_hes_status() utility function"""

    client_class = APIClient

    def setUp(self):
        super(HESStatusTest, self).setUp()
        self.base_url = reverse("apiv2:hes-generate")
        self.home_status = EEPProgramHomeStatus.objects.get()
        self.bad_company = Company.objects.get(name="unrelated__rater")
        self.good_rater = self.home_status.company
        self.unrelated_rem_simulation = Simulation.objects.get(company=self.bad_company)
        self.available_rem_simulation = simulation_factory(company=self.good_rater)
        self.home_status = EEPProgramHomeStatus.objects.get()

        self.user = self.good_rater.users.filter(is_company_admin=True).get()
        msg = "User %s [pk=%s] is not allowed to login"
        self.assertTrue(
            self.client.login(username=self.user.username, password="password"),
            msg=msg % (self.user.username, self.user.pk),
        )

    def test_get_hes_sim_status_orientation_before_results_generated(self):
        """If we call worst_case_orientation(), it should return None if we haven't actually run the
        simulation yet to determine the worst case"""
        hes_sim_status = HESSimulationStatus.objects.create()
        self.assertIsNone(hes_sim_status.worst_case_simulation)
        self.assertIsNone(hes_sim_status.worst_case_orientation)

    def test_status(self):
        """Test the basics of the status"""

        # We pass in a user_id of 0 to get around the lru_cache from getting hit
        data = get_hes_status(home_status_id=self.home_status.pk, user_id=0)

        self.assertEqual(data["can_create"], False)
        self.assertEqual(data["can_update"], False)
        self.assertEqual(data["status"], "Score has not been generated")
        self.assertEqual(data["has_simulation"], False)
        self.assertEqual(data["simulation_endpoint"], reverse("apiv2:hes-generate"))
        self.assertEqual(data["simulation_id"], self.home_status.floorplan.simulation.pk)
        self.assertEqual(data["company_id"], self.home_status.company.pk)
        self.assertEqual(data["simulation_status_id"], None)
        self.assertEqual(data["wc_simulation_id"], None)
        self.assertEqual(data["disabled"], True)

    @mock.patch("axis.hes.hes.DOEInterface.post", side_effect=doe_mocked_soap_responses)
    @mock.patch("axis.hes.hes.DOEInterface.get", side_effect=doe_mocked_soap_responses)
    @mock.patch("simulation.serializers.hpxml.NrelHpxmlValidator", side_effect=validation_mock)
    def test_complete_set(self, *args):
        """Test the basics of a complete status"""

        data = {"home_status_id": self.home_status.pk}
        response = self.client.post(self.base_url, data)
        self.assertEqual(status.HTTP_201_CREATED, response.status_code, response.json())

        hes_sim_status = HESSimulationStatus.objects.get()
        data = get_hes_status(home_status_id=self.home_status.pk)
        self.assertEqual(data["can_create"], False)
        self.assertEqual(data["can_update"], False)
        self.assertEqual(data["status"], "complete")
        self.assertEqual(data["has_simulation"], True)
        self.assertEqual(data["simulation_endpoint"], reverse("apiv2:hes-generate"))
        self.assertEqual(data["simulation_id"], self.home_status.floorplan.simulation_id)
        self.assertEqual(data["company_id"], self.home_status.company.pk)
        self.assertEqual(data["simulation_status_id"], hes_sim_status.pk)
        self.assertEqual(data["wc_simulation_id"], HESSimulation.objects.first().pk)
        self.assertEqual(data["disabled"], False)
        self.assertEqual(data["wc_orientation"], hes_sim_status.worst_case_orientation)
