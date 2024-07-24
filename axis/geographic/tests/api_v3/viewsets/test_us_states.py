"""us_states.py - Axis"""

__author__ = "Steven K"
__date__ = "10/14/21 10:01"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
from django.urls import reverse_lazy
from rest_framework.test import APITestCase
from rest_framework import status

from axis.core.tests.factories import rater_user_factory
from ...factories import us_states_factory, real_city_factory

log = logging.getLogger(__name__)


class TestUSStateViewset(APITestCase):
    @classmethod
    def setUpTestData(cls):
        super(TestUSStateViewset, cls).setUpTestData()
        us_states_factory("WI")
        cls.city = real_city_factory("Gilbert", "AZ")
        cls.user = rater_user_factory(company__city=cls.city)

    def test_no_auth(self):
        url = reverse_lazy("api_v3:us_states-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_view(self):
        url = reverse_lazy("api_v3:us_states-list")
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.json()), 50)

    def test_list_filter_name(self):
        url = reverse_lazy("api_v3:us_states-list") + "?search=Arizona"
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)

    def test_list_filter_abbr(self):
        url = reverse_lazy("api_v3:us_states-list") + "?search=NM"
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)
