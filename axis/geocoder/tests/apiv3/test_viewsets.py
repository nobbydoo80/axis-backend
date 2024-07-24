"""viewsets.py - Axis"""

__author__ = "Steven K"
__date__ = "9/24/21 10:35"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import json
import logging

from django.urls import reverse_lazy
from rest_framework import status

from axis.company.tests.factories import base_company_factory
from axis.core.tests.factories import basic_user_factory
from axis.core.tests.testcases import ApiV3Tests

from axis.geographic.models import County, City
from axis.geographic.tests.factories import real_city_factory, real_county_factory
from axis.geographic.utils.city import resolve_city
from axis.geographic.utils.country import resolve_country

log = logging.getLogger(__name__)


class TestGeocoderViewset(ApiV3Tests):
    """Test GeocodeMatch Serializer"""

    @classmethod
    def setUpTestData(cls):
        cls.city = real_city_factory("Gilbert", "AZ")
        pivotal_company = base_company_factory(
            slug="pivotal-energy-solutions",
            company_type="general",
            city=cls.city,
        )
        cls.user = basic_user_factory(
            username="admin", is_staff=True, is_superuser=True, company=pivotal_company
        )

    def test_matches_fairfax_county(self):
        """
        Bing returns a "City of Fairfax" for the county.
        """
        url = reverse_lazy("api_v3:geocoder-matches")

        fairfax = real_city_factory("Fairfax", "VA")
        initial_county_count = County.objects.count()
        self.assertEqual(initial_county_count, 2)
        self.assertEqual(
            set(County.objects.values_list("name", flat=True)), {"Maricopa", "Fairfax"}
        )
        initial_city_count = City.objects.count()
        self.assertEqual(initial_city_count, 2)
        self.assertEqual(set(City.objects.values_list("name", flat=True)), {"Gilbert", "Fairfax"})

        kwargs = dict(
            url=url,
            user=self.user,
            data=dict(
                street_line1="3999 University Dr",
                street_line2="",
                city=fairfax.pk,
                zipcode="22030",
            ),
            expected_status=status.HTTP_201_CREATED,
        )
        obj = self.create(**kwargs)

        self.assertIn(kwargs["data"]["street_line1"], obj["raw_address"])
        self.assertIn(kwargs["data"]["zipcode"], obj["raw_address"])
        self.assertIn(fairfax.name, obj["raw_address"])

        self.assertEqual(County.objects.count(), initial_city_count)
        self.assertEqual(City.objects.count(), initial_city_count)

        self.assertEqual(len(obj["responses"]), 2)
        self.assertEqual(len(obj["valid_responses"]), 2)

        # Note the first one has the higher probability

        self.assertEqual(obj["valid_responses"][0]["city"], fairfax.pk)
        self.assertEqual(obj["valid_responses"][0]["county"], fairfax.county.pk)

    def test_intl_matches_viewset(self):
        city = real_city_factory("Santiago de los caballeros", country="DO")

        url = reverse_lazy("api_v3:geocoder-matches")

        kwargs = dict(
            url=url,
            user=self.user,
            data=dict(
                street_line1="autop. juan pablo duarte km. 28",
                street_line2="",
                city=city.pk,
                zipcode="51000",
            ),
            expected_status=status.HTTP_201_CREATED,
        )
        data = self.create(**kwargs)
        self.assertEqual(len(data["responses"]), 2)
        self.assertEqual(len(data["valid_responses"]), 1)

        with self.subTest("Google Response"):
            valid_response = next((x for x in data["valid_responses"] if "google" in x["map_url"]))
            response = next((x for x in data["responses"] if "google" in x["map_url"]))

            self.assertIsNotNone(valid_response["geocode"])
            self.assertEqual(valid_response["geocode"], response["geocode"])
            self.assertIsNotNone(valid_response["created_date"])
            self.assertEqual(valid_response["created_date"], response["created_date"])
            self.assertEqual(valid_response["street_line1"], "Km. 28 Autop. Juan Pablo Duarte")
            self.assertEqual(valid_response["street_line1"], response["street_line1"])
            self.assertIsNone(valid_response["county"])
            self.assertEqual(valid_response["county"], response["county"])
            self.assertIsNotNone(valid_response["county_info"])
            self.assertEqual(valid_response["county_info"], response["county_info"])
            self.assertIsNone(valid_response["state"])
            self.assertEqual(valid_response["state"], response["state"])
            self.assertEqual(valid_response["country"], "DO")
            self.assertEqual(valid_response["country"], response["country"])
            self.assertEqual(valid_response["zipcode"], "51000")
            self.assertEqual(valid_response["zipcode"], response["zipcode"])

            self.assertAlmostEqual(valid_response["latitude"], 19.4359, 3)
            self.assertEqual(valid_response["latitude"], response["latitude"])
            self.assertEqual(valid_response["longitude"], -70.6609011)
            self.assertEqual(valid_response["longitude"], response["longitude"])
            self.assertEqual(
                valid_response["formatted_address"],
                "Autop. Juan Pablo Duarte Km. 28, Santiago De Los Caballeros 51000, DO",
            )
            self.assertEqual(valid_response["formatted_address"], response["formatted_address"])
            self.assertEqual(valid_response["entity_type"], "street_address")
            self.assertEqual(valid_response["entity_type"], response["entity_type"])
            self.assertIsNotNone(response["map_url"])
            self.assertEqual(valid_response["map_url"], response["map_url"])
            self.assertIsNotNone(valid_response["geocode_date"])
            self.assertIsNotNone(response["geocode_date"])
            self.assertIsNotNone(response["geocode_date"])

        # Note we intentionally are not looking at Bing.  It's not even close.
        with self.subTest("Bing Response"):
            response = next((x for x in data["responses"] if "bing" in x["map_url"]))
            self.assertIsNotNone(response["geocode"])
            self.assertIsNotNone(response["created_date"])
            self.assertIsNotNone(response["created_date"])
            self.assertEqual(valid_response["street_line1"], "Km. 28 Autop. Juan Pablo Duarte")
            self.assertIsNone(response["county"])
            self.assertIsNotNone(response["county_info"])
            self.assertIsNone(response["state"])
            self.assertEqual(valid_response["country"], "DO")
            self.assertEqual(valid_response["zipcode"], "51000")
            self.assertAlmostEqual(response["latitude"], 19.4445, 3)
            self.assertAlmostEqual(response["longitude"], -70.6716, 3)
            self.assertEqual(
                response["formatted_address"],
                "Calle Autopista Duarte Santiago de los Caballeros, Santiago",
            )
            self.assertEqual(response["entity_type"], "street_address")
            self.assertIsNotNone(response["map_url"])
            self.assertIsNotNone(response["geocode_date"])

    def test_address_already_in_db(self):
        """If the city is not right we want to make sure that when we send valid responses back
        the city is actually added to the db as real choice.  The user still can say no but this
        city is now available"""
        # This city is close to the read deal. But is not the right one.
        city = real_city_factory("Santiago de los caballeros", country="DO")

        url = reverse_lazy("api_v3:geocoder-matches")

        kwargs = dict(
            url=url,
            user=self.user,
            data=dict(
                street_line1="autop. juan pablo duarte km. 28",
                street_line2="",
                city=city.pk,
                zipcode="51000",
            ),
            expected_status=status.HTTP_201_CREATED,
        )
        data = self.create(**kwargs)

        self.assertEqual(len(data["responses"]), 2)
        self.assertEqual(len(data["valid_responses"]), 1)

        # Attempt to redo this
        kwargs["expected_status"] = status.HTTP_200_OK
        data = self.create(**kwargs)
        self.assertEqual(len(data["responses"]), 2)
        self.assertEqual(len(data["valid_responses"]), 1)

    def test_intl_matches_viewset_wrong_city(self):
        """If the city is not right we want to make sure that when we send valid responses back
        the city is actually added to the db as real choice.  The user still can say no but this
        city is now available"""
        # This city is close to the read deal. But is not the right one.
        city = real_city_factory("Tamboril", country="DO")

        url = reverse_lazy("api_v3:geocoder-matches")

        kwargs = dict(
            url=url,
            user=self.user,
            data=dict(
                street_line1="autop. juan pablo duarte km. 28",
                street_line2="",
                city=city.pk,
                zipcode="51000",
            ),
            expected_status=status.HTTP_201_CREATED,
        )
        data = self.create(**kwargs)
        self.assertEqual(len(data["responses"]), 2)
        self.assertEqual(len(data["valid_responses"]), 0)

        self.assertNotEqual(city.pk, data["responses"][0]["city"])
        new_city = City.objects.get(id=data["responses"][0]["city"])
        self.assertEqual(new_city.name, "Santiago De Los Caballeros")
        self.assertEqual(City.objects.count(), 3)


class TestGeocodeCityMatchesViewset(ApiV3Tests):
    """Test GeocodeMatch Serializer"""

    @classmethod
    def setUpTestData(cls):
        cls.county = real_county_factory("Saratoga", "NY")
        cls.city = City.objects.first()
        pivotal_company = base_company_factory(
            slug="pivotal-energy-solutions",
            company_type="general",
            city=cls.city,
        )
        cls.user = basic_user_factory(
            username="admin", is_staff=True, is_superuser=True, company=pivotal_company
        )

    def test_city_matches_greenfield(self):
        self.assertFalse(City.objects.filter(name="Greenfield").exists())
        self.assertTrue(County.objects.filter(name="Saratoga", state="NY").exists())

        url = reverse_lazy("api_v3:geocoder-city-matches")

        kwargs = dict(
            url=url,
            user=self.user,
            data=dict(
                name="greenfield",
                county=self.county.pk,
            ),
            expected_status=status.HTTP_201_CREATED,
        )
        data = self.create(**kwargs)

        self.assertEqual(data["raw_address"], "greenfield, Saratoga NY")
        self.assertEqual(data["entity_type"], "city")
        self.assertIsNotNone(data["modified_date"])
        self.assertIsNotNone(data["created_date"])
        self.assertEqual(data["immediate"], True)
        self.assertEqual(data["raw_county"], County.objects.get(name="Saratoga", state="NY").id)
        self.assertEqual(data["raw_state"], "NY")
        self.assertEqual(len(data["responses"]), 2)
        self.assertEqual(len(data["valid_responses"]), 1)

    def test_city_matches_greenfield_response_serializer(self):
        self.assertFalse(City.objects.filter(name="Greenfield").exists())
        self.assertTrue(County.objects.filter(name="Saratoga", state="NY").exists())

        url = reverse_lazy("api_v3:geocoder-city-matches")

        kwargs = dict(
            url=url,
            user=self.user,
            data=dict(
                name="greenfield",
                county=self.county.pk,
            ),
            expected_status=status.HTTP_201_CREATED,
        )
        data = self.create(**kwargs)
        self.assertEqual(len(data["responses"]), 2)
        self.assertEqual(len(data["valid_responses"]), 1)
        county = County.objects.get(name="Saratoga", state="NY")
        with self.subTest("Bing Response"):
            valid_response = next((x for x in data["responses"] if "bing" in x["map_url"]))
            response = next((x for x in data["responses"] if "bing" in x["map_url"]))

            self.assertIsNotNone(valid_response["geocode"])
            self.assertEqual(valid_response["geocode"], response["geocode"])
            self.assertIsNotNone(valid_response["created_date"])
            self.assertEqual(valid_response["created_date"], response["created_date"])
            self.assertEqual(valid_response["name"], "Greenfield")
            self.assertEqual(valid_response["name"], response["name"])
            self.assertEqual(valid_response["county"], county.id)
            self.assertEqual(valid_response["county"], response["county"])
            self.assertIsNotNone(valid_response["county_info"])
            self.assertEqual(valid_response["county_info"], response["county_info"])
            self.assertEqual(valid_response["state"], "NY")
            self.assertEqual(valid_response["state"], response["state"])
            self.assertAlmostEqual(valid_response["latitude"], 43.1068, 3)
            self.assertEqual(valid_response["latitude"], response["latitude"])
            self.assertAlmostEqual(valid_response["longitude"], -73.8642, 3)
            self.assertEqual(valid_response["longitude"], response["longitude"])
            self.assertEqual(valid_response["formatted_address"], "Greenfield, Saratoga County NY")
            self.assertEqual(valid_response["formatted_address"], response["formatted_address"])
            self.assertEqual(valid_response["entity_type"], "city")
            self.assertEqual(valid_response["entity_type"], response["entity_type"])
            self.assertEqual(valid_response["map_url"], response["map_url"])
            self.assertIsNotNone(valid_response["geocode_date"])
            self.assertEqual(valid_response["geocode_date"], response["geocode_date"])

        with self.subTest("Google Response"):
            valid_response = next((x for x in data["responses"] if "google" in x["map_url"]))
            response = next((x for x in data["responses"] if "google" in x["map_url"]))

            self.assertIsNotNone(valid_response["geocode"])
            self.assertEqual(valid_response["geocode"], response["geocode"])
            self.assertIsNotNone(valid_response["created_date"])
            self.assertEqual(valid_response["created_date"], response["created_date"])
            self.assertEqual(valid_response["name"], "Greenfield")
            self.assertEqual(valid_response["name"], response["name"])
            self.assertEqual(valid_response["county"], county.id)
            self.assertEqual(valid_response["county"], response["county"])
            self.assertIsNotNone(valid_response["county_info"])
            self.assertEqual(valid_response["county_info"], response["county_info"])
            self.assertEqual(valid_response["state"], "NY")
            self.assertEqual(valid_response["state"], response["state"])
            self.assertAlmostEqual(valid_response["latitude"], 43.1036, 3)
            self.assertEqual(valid_response["latitude"], response["latitude"])
            self.assertAlmostEqual(valid_response["longitude"], -73.8640, 3)
            self.assertEqual(valid_response["longitude"], response["longitude"])
            self.assertEqual(valid_response["formatted_address"], "Greenfield, Saratoga County NY")
            self.assertEqual(valid_response["formatted_address"], response["formatted_address"])
            self.assertEqual(valid_response["entity_type"], "city")
            self.assertEqual(valid_response["entity_type"], response["entity_type"])
            self.assertEqual(valid_response["map_url"], response["map_url"])
            self.assertIsNotNone(valid_response["geocode_date"])
            self.assertEqual(valid_response["geocode_date"], response["geocode_date"])

    def test_intl_city_matches_response_serializer(self):
        self.assertFalse(City.objects.filter(name="Charlotte Amalie").exists())

        url = reverse_lazy("api_v3:geocoder-city-matches")

        kwargs = dict(
            url=url,
            user=self.user,
            data=dict(
                name="Charlotte Amalie",
                country=resolve_country("VI").abbr,
            ),
            expected_status=status.HTTP_201_CREATED,
        )
        data = self.create(**kwargs)
        self.assertEqual(len(data["responses"]), 2)
        self.assertEqual(len(data["valid_responses"]), 1)

        with self.subTest("Google Response"):
            valid_response = next((x for x in data["valid_responses"] if "google" in x["map_url"]))
            response = next((x for x in data["responses"] if "google" in x["map_url"]))

            self.assertIsNotNone(valid_response["geocode"])
            self.assertEqual(valid_response["geocode"], response["geocode"])
            self.assertIsNotNone(valid_response["created_date"])
            self.assertEqual(valid_response["created_date"], response["created_date"])
            self.assertEqual(valid_response["name"], "Charlotte Amalie")
            self.assertEqual(valid_response["name"], response["name"])
            self.assertIsNone(valid_response["county"])
            self.assertEqual(valid_response["county"], response["county"])
            self.assertIsNotNone(valid_response["county_info"])
            self.assertEqual(valid_response["county_info"], response["county_info"])
            self.assertIsNone(valid_response["state"])
            self.assertEqual(valid_response["state"], response["state"])
            self.assertAlmostEqual(valid_response["latitude"], 18.3419, 3)
            self.assertEqual(valid_response["latitude"], response["latitude"])
            self.assertAlmostEqual(valid_response["longitude"], -64.9307, 3)
            self.assertEqual(valid_response["longitude"], response["longitude"])
            self.assertEqual(valid_response["formatted_address"], "Charlotte Amalie VI")
            self.assertEqual(valid_response["formatted_address"], response["formatted_address"])
            self.assertEqual(valid_response["entity_type"], "city")
            self.assertEqual(valid_response["entity_type"], response["entity_type"])
            self.assertEqual(valid_response["map_url"], response["map_url"])
            self.assertIsNotNone(valid_response["geocode_date"])
            self.assertIsNotNone(response["geocode_date"])

        with self.subTest("Bing Response"):
            response = next((x for x in data["responses"] if "bing" in x["map_url"]))
            self.assertIsNotNone(response["geocode"])
            self.assertIsNotNone(response["created_date"])
            self.assertIsNotNone(response["created_date"])
            self.assertEqual(response["name"], "Charlotte Amalie")
            self.assertIsNone(response["county"])
            self.assertIsNotNone(response["county_info"])
            self.assertIsNone(response["state"])
            self.assertAlmostEqual(response["latitude"], 18.3417, 3)
            self.assertAlmostEqual(response["longitude"], -64.9322, 3)
            self.assertEqual(response["formatted_address"], "Charlotte Amalie VI")
            self.assertEqual(response["entity_type"], "city")
            self.assertIsNotNone(response["map_url"])
            self.assertIsNotNone(response["geocode_date"])

    def test_completely_bogus(self):
        """
        Bing returns a "City of Fairfax" for the county.
        """
        url = reverse_lazy("api_v3:geocoder-matches")

        city = real_city_factory("Lake Holiday", "VA")

        kwargs = dict(
            url=url,
            user=self.user,
            data=dict(
                street_line1="sads",
                street_line2="",
                city=city.pk,
                zipcode="34324",
            ),
            expected_status=status.HTTP_201_CREATED,
        )
        obj = self.create(**kwargs)

        self.assertIn(kwargs["data"]["street_line1"], obj["raw_address"])
        self.assertIn(kwargs["data"]["zipcode"], obj["raw_address"])
        self.assertIn(city.name, obj["raw_address"])

        self.assertEqual(len(obj["responses"]), 2)
        self.assertEqual(len(obj["valid_responses"]), 0)

        # print(json.dumps(obj["responses"][0], indent=4))

    def test_resolve_city_no_county(self):
        city = resolve_city(name="Lake Frederick", state_abbreviation="VA")
        self.assertIsNotNone(city.geocode_response)
        self.assertEqual(city.geocode_response.geocode.entity_type, "city")
        self.assertEqual(city.geocode_response.geocode.raw_address, "Lake Frederick, VA")
        self.assertEqual(city.geocode_response.geocode.raw_city, None)
        self.assertEqual(city.geocode_response.geocode.raw_county, None)
        self.assertEqual(city.geocode_response.geocode.raw_country, resolve_country("US"))
        self.assertEqual(city.geocode_response.geocode.raw_state.abbr, "VA")
        self.assertIsNotNone(city.geocode_response)
        self.assertIsNotNone(city.latitude)
        self.assertIsNotNone(city.longitude)
        self.assertEqual(city.county.name, "Frederick")
        self.assertIsNotNone(city.county.latitude)
        self.assertIsNotNone(city.county.longitude)

        # This is to ensure we created it from our data.
        self.assertEqual(city.county.climate_zone.as_string(), "4A")

    def test_zd40968(self):
        """
        Bing returns a "City of Fairfax" for the county.
        """
        url = reverse_lazy("api_v3:geocoder-matches")
        city = resolve_city(name="Lake Frederick VA")

        self.assertIn("Frederick", city.county.name)
        self.assertEqual(city.country, resolve_country("US"))

        kwargs = dict(
            url=url,
            user=self.user,
            data=dict(
                street_line1="125 Wake Robin Court",
                street_line2="",
                city=city.pk,
                zipcode="22663",
            ),
            expected_status=status.HTTP_201_CREATED,
        )
        obj = self.create(**kwargs)

        self.assertIn(kwargs["data"]["street_line1"], obj["raw_address"])
        self.assertIn(kwargs["data"]["zipcode"], obj["raw_address"])
        self.assertIn(city.name, obj["raw_address"])

        self.assertEqual(len(obj["responses"]), 3)
        self.assertEqual(len(obj["valid_responses"]), 0)

    def test_artem_failure(self):
        """This comes back with türkiye"""
        city = resolve_city(name="Agar, SD, (Sully)")

        kwargs = dict(
            url=reverse_lazy("api_v3:geocoder-matches"),
            user=self.user,
            data=dict(
                street_line1="sdad",
                street_line2="sad",
                city=city.pk,
                zipcode="4324",
            ),
            expected_status=status.HTTP_201_CREATED,
        )
        obj = self.create(**kwargs)
        self.assertEqual(len(obj["responses"]), 2)
        self.assertEqual(len(obj["valid_responses"]), 0)

    def test_virginia_beach_failure(self):
        """Here we get the city as a valid answer - A bit odd but we need to handle it"""
        county = real_county_factory("Virginia Beach", "VA")
        city = county.city_set.first()
        kwargs = dict(
            url=reverse_lazy("api_v3:geocoder-matches"),
            user=self.user,
            data=dict(
                street_line1="222 Central Park Avenue",
                street_line2="",
                city=city.pk,
                zipcode="23462",
            ),
            expected_status=status.HTTP_201_CREATED,
        )
        obj = self.create(**kwargs)
        self.assertEqual(len(obj["responses"]), 2)
        self.assertEqual(len(obj["valid_responses"]), 1)
