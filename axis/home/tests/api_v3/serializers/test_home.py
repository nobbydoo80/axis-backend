"""test_home.py - axis"""

__author__ = "Steven K"
__date__ = "7/7/22 11:31"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from axis.core.tests.testcases import ApiV3Tests
from axis.geocoder.api_v3.serializers import GeocodeMatchesSerializer
from axis.geocoder.models import Geocode
from axis.geographic.tests.factories import real_city_factory
from axis.home.api_v3.serializers import HomeAddressIsUniqueRequestDataSerializer
from axis.home.models import Home
from axis.home.tests.factories import home_factory

log = logging.getLogger(__name__)


class TestHomeAddressIsUniqueRequestDataSerializer(ApiV3Tests):
    """Test HomeAddressIsUniqueRequestDataSerializer Serializer"""

    @classmethod
    def setUpTestData(cls):
        cls.city = real_city_factory("Providence", "RI")

    def test_basic_exists(self):
        """We have no similar homes so this should always work"""
        data = {
            "street_line1": "479 Washington St",
            "city": self.city.id,
            "zipcode": 34342,
            "is_multi_family": False,
        }

        source_home = home_factory(
            street_line1=data["street_line1"].lower(),
            street_line2=data.get("street_line2"),
            is_multi_family=data["is_multi_family"],
            zipcode=data["zipcode"],
            city=self.city,
            geocode=None,
        )

        serializer = HomeAddressIsUniqueRequestDataSerializer(data=data)
        self.assertTrue(serializer.is_valid(raise_exception=True))

        unique, home = serializer.get_home_is_unique()
        self.assertFalse(unique)
        self.assertEqual(source_home, home)

    def test_basic_multiples_exists(self):
        """We have duplicates (it happens) so always use the first one."""
        data = {
            "street_line1": "479 Washington St",
            "city": self.city.id,
            "zipcode": 34342,
            "is_multi_family": False,
        }

        source_home = home_factory(
            street_line1=data["street_line1"].lower(),
            street_line2=data.get("street_line2"),
            is_multi_family=data["is_multi_family"],
            zipcode=data["zipcode"],
            city=self.city,
            geocode=None,
        )
        source_home_2 = home_factory(
            street_line1=data["street_line1"].lower(),
            street_line2=data.get("street_line2"),
            is_multi_family=data["is_multi_family"],
            zipcode=data["zipcode"],
            city=self.city,
            geocode=None,
        )
        self.assertEqual(Home.objects.count(), 2)

        serializer = HomeAddressIsUniqueRequestDataSerializer(data=data)
        self.assertTrue(serializer.is_valid(raise_exception=True))

        unique, home = serializer.get_home_is_unique()
        self.assertFalse(unique)
        self.assertEqual(source_home, home)

    def test_street_line2_exists(self):
        """Verify we can navigate street line 2."""
        data = {
            "street_line1": "479 Washington St",
            "street_line2": "#2",
            "city": self.city.id,
            "zipcode": 34342,
            "is_multi_family": True,
        }

        source_home = home_factory(
            street_line1=data["street_line1"].lower(),
            street_line2=data.get("street_line2"),
            is_multi_family=data["is_multi_family"],
            zipcode=data["zipcode"],
            city=self.city,
            geocode=None,
        )

        home_factory(
            street_line1=data["street_line1"],
            street_line2="#3",
            is_multi_family=data["is_multi_family"],
            zipcode=data["zipcode"],
            city=self.city,
            geocode=None,
        )

        serializer = HomeAddressIsUniqueRequestDataSerializer(data=data)
        self.assertTrue(serializer.is_valid(raise_exception=True))

        unique, home = serializer.get_home_is_unique()
        self.assertEqual(source_home, home)
        self.assertFalse(unique)

    def test_basic_non_exists(self):
        """Verify that we will geocode the address if we don't have one."""
        data = {
            "street_line1": "479 Washington St",
            "street_line2": "#2",
            "city": self.city.id,
            "zipcode": 34342,
            "is_multi_family": True,
        }
        initial = Geocode.objects.count()
        serializer = HomeAddressIsUniqueRequestDataSerializer(data=data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        unique, home = serializer.get_home_is_unique()
        self.assertTrue(unique)
        self.assertIsNone(home)
        self.assertEqual(Geocode.objects.count(), initial + 1)

    def test_geo_exists_exists(self):
        """Here we verify that we pull out the geocoded response as the source of truth"""
        data = {
            "street_line1": "479 Washington St",
            "city": self.city.id,
            "zipcode": 34342,
            "is_multi_family": True,
        }

        geo_serializer = GeocodeMatchesSerializer(data=data)
        geo_serializer.is_valid(raise_exception=True)
        geocode, create = geo_serializer.save()

        source_home = home_factory(
            street_line1="44000 Washington Road",  # Should get caught on geocoded address
            street_line2="",
            is_multi_family=data["is_multi_family"],
            zipcode=data["zipcode"],
            city=self.city,
            geocode_response=geocode.get_valid_responses()[0],
        )

        serializer = HomeAddressIsUniqueRequestDataSerializer(data=data)
        self.assertTrue(serializer.is_valid(raise_exception=True))

        unique, home = serializer.get_home_is_unique()
        self.assertEqual(source_home, home)
        self.assertFalse(unique)

    def test_exceptions(self):
        """Verify our exceptions"""
        data = {
            "street_line1": "479 Washington St",
            "street_line2": "#2",
            "city": self.city.id,
            "zipcode": 34342,
            "is_multi_family": True,
        }

        serializer = HomeAddressIsUniqueRequestDataSerializer(data=data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        self.assertRaises(NotImplementedError, serializer.save, data)
        self.assertRaises(NotImplementedError, serializer.create, data)
        self.assertRaises(NotImplementedError, serializer.update, None, data)

    def test_lot_number_included(self):
        data = {
            "lot_number": "100",
            "street_line1": "479 Washington St",
            "street_line2": "#2",
            "city": self.city.id,
            "zipcode": 34342,
            "is_multi_family": True,
        }

        source_home = home_factory(
            lot_number=data["lot_number"].lower(),
            street_line1=data["street_line1"].lower(),
            street_line2=data.get("street_line2"),
            is_multi_family=data["is_multi_family"],
            zipcode=data["zipcode"],
            city=self.city,
            geocode=None,
        )

        serializer = HomeAddressIsUniqueRequestDataSerializer(data=data)
        self.assertTrue(serializer.is_valid(raise_exception=True))

        unique, home = serializer.get_home_is_unique()
        self.assertEqual(source_home, home)
        self.assertFalse(unique)

        # Even if we don't pass it the lot_number now it still isn't unique
        data.pop("lot_number")

        serializer = HomeAddressIsUniqueRequestDataSerializer(data=data)
        self.assertTrue(serializer.is_valid(raise_exception=True))

        unique, home = serializer.get_home_is_unique()
        self.assertEqual(source_home, home)
        self.assertFalse(unique)

        # But if we put in a different lot number we are golden
        data["lot_number"] = "101"

        serializer = HomeAddressIsUniqueRequestDataSerializer(data=data)
        self.assertTrue(serializer.is_valid(raise_exception=True))

        unique, home = serializer.get_home_is_unique()
        self.assertIsNone(home)
        self.assertTrue(unique)
