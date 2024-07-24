"""test_disambiguation.py - Axis"""

import logging

from django.core.exceptions import ObjectDoesNotExist

from axis.core.tests.testcases import AxisTestCase
from axis.geocoder.api_v3.serializers import city_matcher, GeocodeCityMatchesSerializer
from axis.geographic.models import City, County, Metro
from axis.geographic.tests.factories import real_county_factory, us_states_factory
from axis.geographic.utils import resolve_state, resolve_city, resolve_county

log = logging.getLogger(__name__)

__author__ = "Steven K"
__date__ = "3/11/21 08:04"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]


class ResolveStateTests(AxisTestCase):
    def test_resolve_state_exists(self):
        us_states_factory("AZ")
        obj = resolve_state("AZ")
        self.assertEqual(obj.abbr, "AZ")
        self.assertEqual(obj.name, "Arizona")

    def test_resolve_state(self):
        obj = resolve_state("AZ")
        self.assertEqual(obj.abbr, "AZ")
        self.assertEqual(obj.name, "Arizona")

    def test_resolve_none(self):
        obj = resolve_state(None)
        self.assertEqual(obj, None)

    def test_resolve_name(self):
        obj = resolve_state("MaInE")
        self.assertEqual(obj.abbr, "ME")
        self.assertEqual(obj.name, "Maine")

    def test_bad_resolve_name(self):
        self.assertRaises(KeyError, resolve_state, "FOO")

    def test_resolve_dc(self):
        obj = resolve_state("DC")
        self.assertEqual(obj.abbr, "DC")
        self.assertEqual(obj.name, "District of Columbia")


class ResolveCountyTests(AxisTestCase):
    def test_resolve_exists(self):
        real_county_factory("Maricopa", "AZ")
        self.assertEqual(County.objects.count(), 1)
        with self.subTest("By Name"):
            obj = resolve_county("MARICOPA", "az")
            self.assertEqual(County.objects.count(), 1)

            self.assertEqual(obj.name, "Maricopa")
            self.assertIsNotNone(obj.latitude)
            self.assertIsNotNone(obj.longitude)
            self.assertIsNotNone(obj.climate_zone)
            self.assertIsNotNone(obj.metro)

        # print(json.dumps(model_to_dict(obj), indent=4))
        with self.subTest("By Legal Name"):
            obj = resolve_county("Maricopa County", "az")
            self.assertEqual(obj.legal_statistical_area_description, "Maricopa County")

        with self.subTest("By only name"):
            obj = resolve_county("maricopa")
            self.assertEqual(County.objects.count(), 1)
            self.assertEqual(obj.name, "Maricopa")

    def test_resolve_create(self):
        self.assertEqual(County.objects.count(), 0)
        obj = resolve_county("MARICOPA", "az")
        self.assertEqual(County.objects.count(), 1)
        self.assertEqual(obj.name, "Maricopa")
        self.assertIsNotNone(obj.latitude)
        self.assertIsNotNone(obj.longitude)
        self.assertIsNotNone(obj.climate_zone)
        self.assertIsNotNone(obj.metro)

    def test_resolve_create_fairfax(self):
        # Fairfax VA - Because they liked the name so much lets use it twice.
        obj = real_county_factory("Fairfax", "VA")
        self.assertEqual(County.objects.count(), 2)
        self.assertEqual(obj.name, "Fairfax")
        obj = resolve_county("Fairfax", "VA")
        self.assertEqual(County.objects.count(), 2)
        self.assertEqual(obj.name, "Fairfax")

    def test_resolve_create_fairfax_2(self):
        # Fairfax VA - Because they liked the name so much lets use it twice.
        obj = resolve_county("Fairfax", "VA")
        self.assertEqual(County.objects.count(), 2)
        self.assertEqual(obj.name, "Fairfax")

    def test_resolve_periods_partial(self):
        """We need to handle the periods - Our source puts in the periods `St. Francis`"""
        obj = resolve_county("St Clair County", "AL")
        self.assertEqual(obj.name, "St. Clair")

    def test_resolve_parish_borough_census(self):
        obj = resolve_county("Aleutians East Borough", "AK")
        self.assertEqual(obj.name, "Aleutians East")

        obj = resolve_county("Aleutians West Census Area", "AK")
        self.assertEqual(obj.name, "Aleutians West")

        obj = resolve_county("East Baton Rouge Parish", "LA")
        self.assertEqual(obj.name, "East Baton Rouge")

        obj = resolve_county("Anchorage Municipality", "AK")
        self.assertEqual(obj.name, "Anchorage")

    def test_resolve_dc(self):
        obj = resolve_county("District of Columbia", "DC")
        self.assertEqual(obj.name, "District of Columbia")

    def test_bad_resolve_name(self):
        self.assertRaises(ObjectDoesNotExist, resolve_county, "FOO", "MT")
        self.assertRaises(ObjectDoesNotExist, resolve_county, None, "MT")

    def test_resolve_self(self):
        obj = resolve_county("MARICOPA", "az")
        self.assertEqual(resolve_county(obj), obj)


class ResolveCityTests(AxisTestCase):
    @classmethod
    def setUpTestData(cls):
        from axis.geographic.tests.factories import real_county_factory

        real_county_factory("Yavapai", "AZ", include_cities=False)

    def test_resolve_city_params(self):
        """We found a bug where an object would create multiple entities."""

        resolve_city(name="cordes junction", state_abbreviation="AZ")

        self.assertEqual(City.objects.count(), 1)
        city = City.objects.get()
        self.assertEqual(city.name, "Cordes Junction")
        self.assertEqual(city.county.name, "Yavapai")
        self.assertEqual(city.country.abbr, "US")
        self.assertAlmostEqual(city.latitude, 34.327, 2)
        self.assertAlmostEqual(city.longitude, -112.118, 2)
        self.assertEqual(city.place_fips, "9900000")
        self.assertEqual(County.objects.count(), 1)
        self.assertEqual(Metro.objects.count(), 1)

    def test_resolve_city_params_county(self):
        """We found a bug where an object would create multiple entities."""
        self.assertEqual(City.objects.count(), 0)

        resolve_city(name="cordes junction", county=County.objects.first())

        self.assertEqual(City.objects.count(), 1)
        city = City.objects.get()
        self.assertEqual(city.name, "Cordes Junction")
        self.assertEqual(city.county.name, "Yavapai")
        self.assertEqual(city.country.abbr, "US")
        self.assertAlmostEqual(city.latitude, 34.327, 2)
        self.assertAlmostEqual(city.longitude, -112.118, 2)
        self.assertEqual(city.place_fips, "9900000")
        self.assertEqual(County.objects.count(), 1)
        self.assertEqual(Metro.objects.count(), 1)

    def test_resolve_city_with_state_appended_params(self):
        """We found a bug where an object would create multiple entities."""
        self.assertEqual(City.objects.count(), 0)

        resolve_city(name="cordes junction AZ")

        self.assertEqual(City.objects.count(), 1)

        city = City.objects.get()
        self.assertEqual(city.name, "Cordes Junction")
        self.assertEqual(city.county.name, "Yavapai")
        self.assertEqual(city.country.abbr, "US")
        self.assertAlmostEqual(city.latitude, 34.327, 2)
        self.assertAlmostEqual(city.longitude, -112.118, 2)
        self.assertEqual(city.place_fips, "9900000")
        self.assertEqual(County.objects.count(), 1)
        self.assertEqual(Metro.objects.count(), 1)

        self.assertEqual(County.objects.count(), 1)
        self.assertEqual(Metro.objects.count(), 1)

    def test_resolve_city_with_state_comma_appended(self):
        """We found a bug where an object would create multiple entities."""
        self.assertEqual(City.objects.count(), 0)

        resolve_city(name="cordes junction, AZ")

        self.assertEqual(City.objects.count(), 1)

        city = City.objects.get()
        self.assertEqual(city.name, "Cordes Junction")
        self.assertEqual(city.county.name, "Yavapai")
        self.assertEqual(city.country.abbr, "US")
        self.assertAlmostEqual(city.latitude, 34.327, 2)
        self.assertAlmostEqual(city.longitude, -112.118, 2)
        self.assertEqual(city.place_fips, "9900000")
        self.assertEqual(County.objects.count(), 1)
        self.assertEqual(Metro.objects.count(), 1)

        self.assertEqual(County.objects.count(), 1)
        self.assertEqual(Metro.objects.count(), 1)

    def test_resolve_city_with_country_params(self):
        """Mke sure we can find an international country"""
        self.assertEqual(City.objects.count(), 0)

        resolve_city(name="charlotte amalie", country="VI")

        self.assertEqual(City.objects.count(), 1)

        city = City.objects.get()
        self.assertEqual(city.name, "Charlotte Amalie")
        self.assertIsNone(city.county)
        self.assertEqual(city.country.abbr, "VI")
        self.assertAlmostEqual(city.latitude, 18.341, 2)
        self.assertAlmostEqual(city.longitude, -64.930, 2)
        self.assertEqual(city.place_fips, "9900000")

    def test_resolve_city_with_country_together_params(self):
        """Mke sure we can find an international country"""
        self.assertEqual(City.objects.count(), 0)

        resolve_city(name="charlotte amalie, VI")

        self.assertEqual(City.objects.count(), 1)

        city = City.objects.get()
        self.assertEqual(city.name, "Charlotte Amalie")
        self.assertIsNone(city.county)
        self.assertEqual(city.country.abbr, "VI")
        self.assertAlmostEqual(city.latitude, 18.341, 2)
        self.assertAlmostEqual(city.longitude, -64.930, 2)
        self.assertEqual(city.place_fips, "9900000")

        resolve_city(name="charlotte amalie, VI")
        self.assertEqual(City.objects.count(), 1)

    def test_city_matcher(self):
        """Test out our city name matcher"""
        cities = [
            "West St. Paul, MN (Dakota)",
            "St. Lawrence, PA (Berks)",
            "St. Louis, MO (St. Louis)",
            "Port O'Connor, TX (Calhoun)",
            "Islamorada, Village of Islands, FL (Monroe)",
            "Austin TX",
            "St. Louis MO",
            "Loíza, PR",
            "Corazón, PR",
            "Agar, SD, (Sully)",
        ]
        for city in cities:
            with self.subTest(f"city_matcher Resolve {city}"):
                city = city_matcher.match(city)
                self.assertIsNotNone(city)

        cities += [
            "Austin, Texas",
            "San Germán, Puerto Rico",
            "Juncos, puerto rico",
            "test, dominican republic",
        ]
        for city in cities:
            with self.subTest(f"parse_one_liner {city}"):
                result = GeocodeCityMatchesSerializer().parse_one_liner(city)
                self.assertNotEqual(result["name"], city)
                self.assertIsNotNone(result["country"])

        for city in cities:
            with self.subTest(f"resolve_city {city}"):
                result = resolve_city(city)
                self.assertIsNotNone(result)
                self.assertIsNotNone(result.country)
