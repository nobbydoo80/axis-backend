"""tests.py: Django geocoder"""


__author__ = "Peter Landry"
__date__ = "12/4/13 5:47 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = ["Peter Landry", "Steven Klass"]

import json

import logging

from django.test import TestCase
from rest_framework.test import APIClient

from axis.geographic.tests.factories import real_city_factory

from ..models import Geocode, GeocodeResponse


log = logging.getLogger(__name__)


class GeocoderAPITests(TestCase):
    client_class = APIClient

    def setUp(self):
        from axis.core.tests.factories import basic_user_factory

        self.api_endpoint = "/api/v2/geocode/matches/"

        self.city = real_city_factory("Gilbert", "AZ")
        self.home_base_address = {
            "street_line1": "2548 South Loren Lane",
            "city": self.city.id,
            "state": self.city.county.state,
            "zipcode": "85250",
            "confirmed_address": "false",
            "is_multi_family": "false",
            "address_override": "false",
            "address_designator": "",
        }
        self.unconfirmed_base_address = self.home_base_address.copy()
        self.unconfirmed_base_address.update(
            {"street_line1": "Nowhere Ln", "zipcode": "54829", "confirmed_address": False}
        )

        self.user = basic_user_factory()

    def test_get_confirmed_match(self):
        """This simply verifies the basics api get matches works"""
        self.assertEqual(Geocode.objects.count(), 0)
        self.assertEqual(GeocodeResponse.objects.count(), 0)

        self.assertEqual(self.client.login(username=self.user.username, password="password"), True)
        response = self.client.get(self.api_endpoint, data=self.home_base_address)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data["matches"]), 1)
        match = data["matches"][0]
        self.assertIsNotNone(match["response"])
        self.assertIsNotNone(match["address"])
        # pprint.pprint(json.loads(response.content))

    def test_get_unconfirmed_match(self):
        """This simply verifies the basics of get matches works"""
        self.assertEqual(Geocode.objects.count(), 0)
        self.assertEqual(GeocodeResponse.objects.count(), 0)
        self.assertEqual(self.client.login(username=self.user.username, password="password"), True)
        response = self.client.get(self.api_endpoint, data=self.unconfirmed_base_address)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data["matches"]), 0)
