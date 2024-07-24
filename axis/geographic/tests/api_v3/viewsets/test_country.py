"""test_country.py - axis"""

__author__ = "Steven K"
__date__ = "7/25/22 14:19"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from django.urls import reverse_lazy
from rest_framework import status
from rest_framework.test import APITestCase

from axis.core.tests.factories import rater_user_factory
from axis.geographic.models import Country
from axis.geographic.tests.factories import real_city_factory
from axis.geographic.utils.country import get_usa_default, resolve_country

log = logging.getLogger(__name__)


class TestCountryViewset(APITestCase):
    @classmethod
    def setUpTestData(cls):
        super(TestCountryViewset, cls).setUpTestData()
        cls.usa = get_usa_default()
        cls.germany = resolve_country("DE")
        cls.dominican_republic = resolve_country("DO")
        cls.city = real_city_factory("Pensacola", "FL")
        cls.user = rater_user_factory(
            company__city=cls.city,
            company__counties=[cls.city.county],
            company__countries=[cls.usa, cls.germany],
        )

    def test_setup(self):
        self.assertEqual(Country.objects.all().count(), 3)
        self.assertEqual(self.user.company.countries.count(), 2)

    def test_no_auth(self):
        with self.subTest("List View"):
            url = reverse_lazy("api_v3:countries-list")
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        with self.subTest("Detail"):
            url = reverse_lazy("api_v3:countries-detail", kwargs={"pk": self.usa.pk})
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_view(self):
        url = reverse_lazy("api_v3:countries-list")
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["count"], 3)

    def test_list_filter_name(self):
        url = reverse_lazy("api_v3:countries-list") + "?search=Germany"
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["count"], 1)

    def test_list_filter_abbr(self):
        url = reverse_lazy("api_v3:countries-list") + "?search=US"
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["count"], 1)

    def test_list_filter_attached(self):
        with self.subTest("All"):
            url = reverse_lazy("api_v3:countries-list")
            self.client.force_authenticate(user=self.user)
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.json()["count"], Country.objects.count())

        with self.subTest("Attached"):
            url = reverse_lazy("api_v3:countries-list") + "?is_attached=attached"
            self.client.force_authenticate(user=self.user)
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(
                response.json()["count"], Country.objects.filter_by_user(self.user).count()
            )

        with self.subTest("Unattached"):
            url = reverse_lazy("api_v3:countries-list") + "?is_attached=unattached"
            self.client.force_authenticate(user=self.user)
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(
                response.json()["count"],
                Country.objects.exclude(
                    id__in=Country.objects.filter_by_user(self.user).values_list("id")
                ).count(),
            )

    def test_detail_view(self):
        url = reverse_lazy("api_v3:countries-detail", kwargs={"pk": self.usa.pk})
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("abbr", response.json())
        self.assertIn("name", response.json())
