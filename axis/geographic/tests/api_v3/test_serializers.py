"""test_serializers.py - Axis"""

__author__ = "Steven K"
__date__ = "10/14/21 08:20"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
from typing import Mapping

from django.test import TestCase

from axis.geographic.api_v3.serializers import (
    USStateSerializer,
    MetroSerializer,
    CountySerializer,
    CountyDetailSerializer,
    ClimateZoneSerializer,
    CitySerializer,
    CityDetailSerializer,
)
from axis.geographic.models import USState, Metro, County, ClimateZone, City
from axis.geographic.tests.factories import us_states_factory, real_city_factory

log = logging.getLogger(__name__)


class TestUSStateSerializer(TestCase):
    @classmethod
    def setUpTestData(cls):
        super(TestUSStateSerializer, cls).setUpTestData()
        us_states_factory("WI")

    def test_serializer(self):
        self.assertGreater(USState.objects.count(), 50)

        instance = USState.objects.get(abbr="WI")
        serializer = USStateSerializer(instance=instance)
        data = serializer.to_representation(instance)
        self.assertEqual(data["abbr"], instance.abbr)
        self.assertEqual(data["name"], instance.name)


class TestMetroSerializer(TestCase):
    @classmethod
    def setUpTestData(cls):
        super(TestMetroSerializer, cls).setUpTestData()
        real_city_factory("Gilbert", "AZ")

    def test_serializer(self):
        self.assertEqual(Metro.objects.count(), 1)
        instance = Metro.objects.get()
        serializer = MetroSerializer(instance=instance)
        data = serializer.to_representation(instance)
        self.assertEqual(data["id"], instance.id)
        self.assertEqual(data["name"], instance.name)
        self.assertEqual(data["cbsa_code"], instance.cbsa_code)


class TestClimateZoneSerializer(TestCase):
    @classmethod
    def setUpTestData(cls):
        super(TestClimateZoneSerializer, cls).setUpTestData()
        real_city_factory("Gilbert", "AZ")

    def test_serializer(self):
        self.assertEqual(ClimateZone.objects.count(), 1)
        instance = ClimateZone.objects.get()
        serializer = ClimateZoneSerializer(instance=instance)
        data = serializer.to_representation(instance)
        self.assertEqual(data["id"], instance.id)
        self.assertEqual(data["zone"], instance.zone)
        self.assertEqual(data["moisture_regime"], instance.moisture_regime)
        self.assertEqual(data["doe_zone"], instance.doe_zone)


class TestCountySerializers(TestCase):
    @classmethod
    def setUpTestData(cls):
        super(TestCountySerializers, cls).setUpTestData()
        real_city_factory("Watertown", "WI")

    def test_county_serializer(self):
        self.assertEqual(County.objects.count(), 2)
        instance = County.objects.first()
        serializer = CountySerializer(instance=instance)
        data = serializer.to_representation(instance)
        self.assertEqual(data["id"], instance.id)
        self.assertEqual(data["name"], instance.name)
        self.assertEqual(data["state"], instance.state)
        self.assertEqual(data["county_fips"], instance.county_fips)
        self.assertEqual(data["county_type"], instance.county_type)
        self.assertEqual(
            data["legal_statistical_area_description"], instance.legal_statistical_area_description
        )
        self.assertEqual(data["ansi_code"], instance.ansi_code)
        self.assertEqual(data["land_area_meters"], instance.land_area_meters)
        self.assertEqual(data["water_area_meters"], instance.water_area_meters)
        self.assertEqual(data["latitude"], instance.latitude)
        self.assertEqual(data["longitude"], instance.longitude)
        self.assertEqual(data["metro"], instance.metro_id)
        self.assertEqual(data["climate_zone"], instance.climate_zone_id)
        self.assertNotIn("climate_zone_info", data)
        self.assertNotIn("metro_info", data)

    def test_county_detail_serializer(self):
        self.assertEqual(County.objects.count(), 2)
        instance = County.objects.last()
        serializer = CountyDetailSerializer(instance=instance)
        data = serializer.to_representation(instance)
        self.assertEqual(data["id"], instance.id)
        self.assertEqual(data["name"], instance.name)
        self.assertEqual(data["state"], instance.state)
        self.assertEqual(data["county_fips"], instance.county_fips)
        self.assertEqual(data["county_type"], instance.county_type)
        self.assertEqual(
            data["legal_statistical_area_description"], instance.legal_statistical_area_description
        )
        self.assertEqual(data["ansi_code"], instance.ansi_code)
        self.assertEqual(data["land_area_meters"], instance.land_area_meters)
        self.assertEqual(data["water_area_meters"], instance.water_area_meters)
        self.assertEqual(data["latitude"], instance.latitude)
        self.assertEqual(data["longitude"], instance.longitude)
        self.assertEqual(data["metro"], instance.metro_id)
        self.assertEqual(data["climate_zone"], instance.climate_zone_id)
        self.assertIn("climate_zone_info", data)
        self.assertIn("metro_info", data)


class TestCitySerializers(TestCase):
    @classmethod
    def setUpTestData(cls):
        super(TestCitySerializers, cls).setUpTestData()
        real_city_factory("Watertown", "WI")

    def test_city_serializer(self):
        self.assertEqual(City.objects.count(), 2)
        instance = City.objects.first()
        serializer = CitySerializer(instance=instance)
        data = serializer.to_representation(instance)
        self.assertEqual(data["id"], instance.id)
        self.assertEqual(data["name"], instance.name)
        self.assertEqual(data["county"], instance.county_id)
        self.assertEqual(data["county_info"]["name"], instance.county.name)
        self.assertEqual(data["place_fips"], instance.place_fips)
        self.assertEqual(
            data["legal_statistical_area_description"], instance.legal_statistical_area_description
        )
        self.assertEqual(data["ansi_code"], instance.ansi_code)
        self.assertEqual(data["land_area_meters"], instance.land_area_meters)
        self.assertEqual(data["water_area_meters"], instance.water_area_meters)
        self.assertEqual(data["latitude"], instance.latitude)
        self.assertEqual(data["longitude"], instance.longitude)
        self.assertNotIn("climate_zone_info", data["county_info"])
        self.assertNotIn("metro_info", data["county_info"])

    def test_city_detail_serializer(self):
        self.assertEqual(City.objects.count(), 2)
        instance = City.objects.last()
        serializer = CityDetailSerializer(instance=instance)
        data = serializer.to_representation(instance)
        self.assertEqual(data["id"], instance.id)
        self.assertEqual(data["name"], instance.name)
        self.assertEqual(data["county"], instance.county_id)
        self.assertEqual(data["county_info"]["name"], instance.county.name)
        self.assertEqual(data["place_fips"], instance.place_fips)
        self.assertEqual(
            data["legal_statistical_area_description"], instance.legal_statistical_area_description
        )
        self.assertEqual(data["ansi_code"], instance.ansi_code)
        self.assertEqual(data["land_area_meters"], instance.land_area_meters)
        self.assertEqual(data["water_area_meters"], instance.water_area_meters)
        self.assertEqual(data["latitude"], instance.latitude)
        self.assertEqual(data["longitude"], instance.longitude)
        self.assertIn("climate_zone_info", data["county_info"])
        self.assertIn("metro_info", data["county_info"])
