"""test_city.py - Axis"""

__author__ = "Steven K"
__date__ = "10/14/21 10:34"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import json
import logging

from django.forms import model_to_dict
from django.urls import reverse_lazy
from rest_framework.test import APITestCase
from rest_framework import status

from axis.core.tests.factories import rater_user_factory
from axis.core.tests.testcases import ApiV3Tests
from axis.geocoder.api_v3.serializers import (
    GeocodeCityMatchesSerializer,
    GeocodeCitySerializer,
)
from axis.geographic.models import City, Country
from axis.geographic.api_v3.serializers import BaseCitySerializer
from axis.geographic.utils.country import resolve_country
from ...factories import real_county_factory

log = logging.getLogger(__name__)


class TestCitySerializer(ApiV3Tests):
    def test_us_full_geocode_create(self):
        """This will test out the full API from geocoder"""

        city = "ixonia"
        county = real_county_factory("Jefferson", "WI")
        City.objects.all().delete()

        # This is where the user looks up info.
        input_data = {"name": city, "county": county.pk}
        serializer = GeocodeCityMatchesSerializer(data=input_data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        obj, create = serializer.save()

        # Now we request for responses
        serializer = GeocodeCitySerializer(instance=obj)
        results = serializer.data
        self.assertEqual(len(results.get("valid_responses")), 1)

        # The user selects the right one.
        data = results["valid_responses"][0]
        data["geocode_response"] = data.pop("id")

        # print(json.dumps(data, indent=4))

        # Now create the actual item
        serializer = BaseCitySerializer(data=data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        obj = serializer.save()

        # Verify it's what we wanted
        self.assertEqual(City.objects.count(), 1)
        self.assertEqual(obj, City.objects.first())

        self.assertIsNotNone(obj.id)
        self.assertEqual(obj.name, "Ixonia")
        self.assertEqual(obj.county, county)
        self.assertEqual(obj.country.abbr, "US")
        self.assertEqual(obj.place_fips, 9900000)
        self.assertEqual(
            obj.legal_statistical_area_description,
            "Unregistered Ixonia (9900000)",
        )
        self.assertEqual(obj.ansi_code, 9900000)
        self.assertEqual(obj.land_area_meters, 0.0)
        self.assertEqual(obj.water_area_meters, 0.0)
        self.assertAlmostEqual(obj.latitude, 43.14, 2)
        self.assertAlmostEqual(obj.longitude, -88.597, 3)
        self.assertEqual(obj.geocode_response_id, data["geocode_response"])

        obj = serializer.save()
        self.assertEqual(City.objects.count(), 1)
        self.assertEqual(obj, City.objects.first())

    def test_non_geoocode_create(self):
        """This will work through the same thing but we don't use a choice we want our own"""

        city = "GARBAGE"
        county = real_county_factory("Jefferson", "WI")
        City.objects.all().delete()

        # This is where the user looks up info.
        input_data = {"name": city, "county": county.pk}
        serializer = GeocodeCityMatchesSerializer(data=input_data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        obj, create = serializer.save()

        # Now we request for responses
        serializer = GeocodeCitySerializer(instance=obj)
        results = serializer.data

        self.assertEqual(len(results.get("valid_responses")), 0)

        # The user selects Nothing.
        data = input_data

        # Now create the actual item
        serializer = BaseCitySerializer(data=data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        obj = serializer.save()

        # Verify it's what we wanted
        self.assertEqual(City.objects.count(), 1)
        self.assertEqual(obj, City.objects.first())

        self.assertIsNotNone(obj.id)
        self.assertEqual(obj.name, "GARBAGE")
        self.assertEqual(obj.county, county)
        self.assertEqual(obj.country.abbr, "US")
        self.assertEqual(obj.place_fips, 9900000)
        self.assertEqual(
            obj.legal_statistical_area_description,
            "Unregistered GARBAGE (9900000)",
        )
        self.assertEqual(obj.ansi_code, 9900000)
        self.assertEqual(obj.land_area_meters, 0.0)
        self.assertEqual(obj.water_area_meters, 0.0)
        self.assertEqual(obj.latitude, 0.0)
        self.assertEqual(obj.longitude, 0.0)
        self.assertIsNone(obj.geocode_response_id)

        obj = serializer.save()
        self.assertEqual(City.objects.count(), 1)
        self.assertEqual(obj, City.objects.first())

    def test_non_us_full_geocode_create(self):
        """This will test out the full API from geocoder"""

        city = "Santiago de los caballeros"
        country = resolve_country("DO").abbr  #  Dominican Republic
        self.assertTrue(Country.objects.filter(abbr=country).exists())
        self.assertFalse(City.objects.filter(name__iexact=city).exists())

        # This is where the user looks up info.
        input_data = {"name": city, "country": country}
        serializer = GeocodeCityMatchesSerializer(data=input_data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        geo_obj, create = serializer.save()  # Our geocode object

        # Now we request for responses
        serializer = GeocodeCitySerializer(instance=geo_obj)
        results = serializer.data
        self.assertEqual(len(results.get("valid_responses")), 1)

        # The user selects the right one. # Our GeocodeResponse ->
        # GeocodeCityBrokeredResponseSerializer
        data = results["valid_responses"][0]
        data["geocode_response"] = data.pop("id")

        # Now create the actual item
        serializer = BaseCitySerializer(data=data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        obj = serializer.save()
        self.assertEqual(City.objects.count(), 1)
        self.assertEqual(obj, City.objects.first())

        self.assertIsNotNone(obj.id)
        self.assertEqual(obj.name, "Santiago De Los Caballeros")
        self.assertEqual(obj.county, None)
        self.assertEqual(obj.country.abbr, "DO")
        self.assertEqual(obj.place_fips, 9900000)
        self.assertEqual(
            obj.legal_statistical_area_description,
            "Unregistered Santiago De Los Caballeros (9900000)",
        )
        self.assertEqual(obj.ansi_code, 9900000)
        self.assertEqual(obj.land_area_meters, 0.0)
        self.assertEqual(obj.water_area_meters, 0.0)
        self.assertEqual(obj.latitude, 19.4791963)
        self.assertEqual(obj.longitude, -70.6930568)
        self.assertEqual(obj.geocode_response_id, data["geocode_response"])

        obj = serializer.save()
        self.assertEqual(City.objects.count(), 1)
        self.assertEqual(obj, City.objects.first())

    def test_non_us_full_geocode_create_bad(self):
        """This will test out the full API from geocoder"""

        city = "GARBAGE"
        country = resolve_country("DO")  #  Dominican Republic
        self.assertFalse(City.objects.filter(name__iexact=city).exists())

        # This is where the user looks up info.
        input_data = {"name": city, "country": country.abbr}
        serializer = GeocodeCityMatchesSerializer(data=input_data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        geo_obj, create = serializer.save()  # Our geocode object

        # Now we request for responses
        serializer = GeocodeCitySerializer(instance=geo_obj)
        results = serializer.data
        self.assertEqual(len(results.get("valid_responses")), 0)

        # The user selects nothing
        data = input_data

        # Now create the actual item
        serializer = BaseCitySerializer(data=data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        obj = serializer.save()
        self.assertEqual(City.objects.count(), 1)
        self.assertEqual(obj, City.objects.first())

        # Verify it's what we wanted
        self.assertEqual(City.objects.count(), 1)
        self.assertEqual(obj, City.objects.first())

        self.assertIsNotNone(obj.id)
        self.assertEqual(obj.name, "GARBAGE")
        self.assertIsNone(obj.county)
        self.assertEqual(obj.country.abbr, "DO")
        self.assertEqual(obj.place_fips, 9900000)
        self.assertEqual(
            obj.legal_statistical_area_description,
            "Unregistered GARBAGE (9900000)",
        )
        self.assertEqual(obj.ansi_code, 9900000)
        self.assertEqual(obj.land_area_meters, 0.0)
        self.assertEqual(obj.water_area_meters, 0.0)
        self.assertEqual(obj.latitude, 0.0)
        self.assertEqual(obj.longitude, 0.0)
        self.assertIsNone(obj.geocode_response_id)

        obj = serializer.save()
        self.assertEqual(City.objects.count(), 1)
        self.assertEqual(obj, City.objects.first())


class TestCityViewset(APITestCase):
    @classmethod
    def setUpTestData(cls):
        super(TestCityViewset, cls).setUpTestData()
        real_county_factory("Maricopa", "AZ")
        cls.pinal = real_county_factory("Pinal", "AZ")
        cls.maricopa = real_county_factory("Maricopa", "AZ")
        cls.city = City.objects.first()
        cls.user = rater_user_factory(company__city=cls.city, company__counties=[cls.maricopa])
        resolve_country("BO")
        resolve_country("VI")

    def test_no_auth(self):
        with self.subTest("List View"):
            url = reverse_lazy("api_v3:cities-list")
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        with self.subTest("Detail"):
            url = reverse_lazy("api_v3:cities-detail", kwargs={"pk": self.city.pk})
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        with self.subTest("Create"):
            url = reverse_lazy("api_v3:cities-list")
            response = self.client.post(url, data={"name": "foo", "country": "VI"})
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        with self.subTest("Update"):
            url = reverse_lazy("api_v3:cities-detail", kwargs={"pk": self.city.pk})
            response = self.client.put(url, data={"country": "VI"})
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_view(self):
        url = reverse_lazy("api_v3:cities-list")
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["count"], 89)

    def test_list_filter_name(self):
        url = reverse_lazy("api_v3:cities-list") + "?search=Gilbert"
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["count"], 1)
        self.assertIn("county_info", response.json()["results"][0])
        self.assertNotIn("metro_info", response.json()["results"][0]["county_info"])
        self.assertNotIn("climate_zone_info", response.json()["results"][0]["county_info"])

    def test_list_filter_county_name(self):
        url = reverse_lazy("api_v3:cities-list") + "?search=maricopa"
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["count"], 46)

    def test_list_filter_county_state(self):
        url = reverse_lazy("api_v3:cities-list") + "?search=NM"
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["count"], 0)

    def test_list_filter_attached(self):
        with self.subTest("All"):
            url = reverse_lazy("api_v3:cities-list")
            self.client.force_authenticate(user=self.user)
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.json()["count"], City.objects.count())

        with self.subTest("Attached"):
            url = reverse_lazy("api_v3:cities-list") + "?is_attached=attached"
            self.client.force_authenticate(user=self.user)
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(
                response.json()["count"], City.objects.filter_by_user(self.user).count()
            )

        with self.subTest("Unattached"):
            url = reverse_lazy("api_v3:cities-list") + "?is_attached=unattached"
            self.client.force_authenticate(user=self.user)
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(
                response.json()["count"],
                City.objects.exclude(
                    id__in=City.objects.filter_by_user(self.user).values_list("id")
                ).count(),
            )

    def test_detail_view(self):
        url = reverse_lazy("api_v3:cities-detail", kwargs={"pk": self.city.pk})
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("county_info", response.json())
        self.assertIn("metro_info", response.json()["county_info"])
        self.assertIn("climate_zone_info", response.json()["county_info"])

    def test_create(self):
        """Verify we can create data"""
        url = reverse_lazy("api_v3:cities-list")
        self.client.force_authenticate(user=self.user)
        response = self.client.post(url, data={"name": "FOO", "country": "BO"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.user.is_company_admin = True
        self.user.save()
        self.user.refresh_from_db()

        self.client.force_authenticate(user=self.user)
        response = self.client.post(url, data={"name": "FOO", "country": "BO"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update(self):
        """Verify we can update data"""
        data = model_to_dict(self.city)
        data["country"] = self.city.country.abbr
        data.pop("geocode_response")
        data["state"] = "VT"

        url = reverse_lazy("api_v3:cities-detail", kwargs={"pk": self.city.pk})
        self.client.force_authenticate(user=self.user)
        response = self.client.put(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.user.is_company_admin = True
        self.user.save()
        self.user.refresh_from_db()

        self.client.force_authenticate(user=self.user)
        response = self.client.put(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
