import logging

from django.urls import reverse
from rest_framework.status import HTTP_403_FORBIDDEN, HTTP_200_OK, HTTP_404_NOT_FOUND
from rest_framework.test import APIClient

from axis.core.tests.factories import basic_user_factory
from axis.core.tests.testcases import AxisTestCase

from simulation.tests.serializers.hpxml.base import HpxmlSimulationSerializerTestCase

__author__ = "Benjamin Stürmer"
__date__ = "05/03/2023 13:51"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Benjamin Stürmer",
]

log = logging.getLogger(__name__)


class HESAPITest(AxisTestCase):
    """Tests of the hpxml method of the Home Energy Score API"""

    client_class = APIClient

    def login(self, *, is_superuser: bool):
        password = "testpw"
        user = basic_user_factory(password=password, is_superuser=is_superuser)
        self.client.login(username=user.username, password=password)

    def get_response(self, sim_id: int):
        url = reverse("apiv2:hes-hpxml", kwargs={"sim_id": sim_id})
        response = self.client.get(url)
        return response

    def test_non_superuser_blocked(self):
        """Only users with the superuser privilege should be able to access the HPXML route"""
        self.login(is_superuser=False)
        response = self.get_response(sim_id=123456789)
        self.assertEqual(HTTP_403_FORBIDDEN, response.status_code)

    def test_get_valid_response(self):
        self.login(is_superuser=True)
        sim = HpxmlSimulationSerializerTestCase.get_sim()
        response = self.get_response(sim_id=sim.id)
        self.assertEqual(HTTP_200_OK, response.status_code)

    def test_404(self):
        self.login(is_superuser=True)
        response = self.get_response(sim_id=123456789)
        self.assertEqual(HTTP_404_NOT_FOUND, response.status_code)
