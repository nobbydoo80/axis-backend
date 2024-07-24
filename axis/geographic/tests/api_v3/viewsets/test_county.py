"""test_county.py - Axis"""

__author__ = "Steven K"
__date__ = "10/14/21 11:21"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
from django.urls import reverse_lazy
from rest_framework.test import APITestCase
from rest_framework import status

from axis.core.tests.factories import rater_user_factory
from axis.geographic.models import City, County
from ...factories import real_county_factory

log = logging.getLogger(__name__)


class TestCountyViewset(APITestCase):
    @classmethod
    def setUpTestData(cls):
        super(TestCountyViewset, cls).setUpTestData()
        real_county_factory("Maricopa", "AZ")
        cls.county = real_county_factory("Pinal", "AZ")
        cls.city = City.objects.first()
        cls.user = rater_user_factory(company__city=cls.city, company__counties=[cls.county])

    def test_no_auth(self):
        with self.subTest("List View"):
            url = reverse_lazy("api_v3:counties-list")
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        with self.subTest("Detail"):
            url = reverse_lazy("api_v3:counties-detail", kwargs={"pk": self.city.pk})
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        with self.subTest("County Cities"):
            url = reverse_lazy(
                "api_v3:county-cities-list", kwargs={"parent_lookup_county_id": self.county.pk}
            )
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_view(self):
        url = reverse_lazy("api_v3:counties-list")
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["count"], 2)

    def test_list_filter_name(self):
        url = reverse_lazy("api_v3:counties-list") + "?search=Pinal"
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["count"], 1)
        self.assertNotIn("metro_info", response.json()["results"][0])
        self.assertNotIn("climate_zone_info", response.json()["results"][0])

    def test_list_filter_county_state(self):
        url = reverse_lazy("api_v3:counties-list") + "?search=NM"
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["count"], 0)

    def test_list_filter_attached(self):
        with self.subTest("All"):
            url = reverse_lazy("api_v3:counties-list")
            self.client.force_authenticate(user=self.user)
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.json()["count"], County.objects.count())

        with self.subTest("Attached"):
            url = reverse_lazy("api_v3:counties-list") + "?is_attached=attached"
            self.client.force_authenticate(user=self.user)
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(
                response.json()["count"], County.objects.filter_by_user(self.user).count()
            )

        with self.subTest("Unattached"):
            url = reverse_lazy("api_v3:counties-list") + "?is_attached=unattached"
            self.client.force_authenticate(user=self.user)
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(
                response.json()["count"],
                County.objects.exclude(
                    id__in=County.objects.filter_by_user(self.user).values_list("id")
                ).count(),
            )

    def test_detail_view(self):
        url = reverse_lazy("api_v3:counties-detail", kwargs={"pk": self.county.pk})
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("metro_info", response.json())
        self.assertIn("climate_zone_info", response.json())

    def test_county_cities(self):
        url = reverse_lazy(
            "api_v3:county-cities-list", kwargs={"parent_lookup_county_id": self.county.pk}
        )
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["count"], City.objects.filter(county=self.county).count())
