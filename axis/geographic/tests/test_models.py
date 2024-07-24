"""test_models.py - Axis"""

import logging

from axis.core.tests.testcases import AxisTestCase
from axis.geographic.models import County, City

log = logging.getLogger(__name__)

__author__ = "Steven K"
__date__ = "3/11/21 11:06"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]


class GeographicModelTests(AxisTestCase):
    @classmethod
    def setUpTestData(cls):
        County.objects.create(
            name="St. Tammany",
            state="LA",
            county_fips="22103",
            ansi_code="01629503",
            legal_statistical_area_description="St. Tammany Parish",
            county_type="2",
            land_area_meters=2189966775,
            water_area_meters=721668349,
            latitude=30.410022,
            longitude=-89.951962,
        )

        County.objects.create(
            name="Ste. Genevieve",
            state="MO",
            county_fips="29186",
            ansi_code="00765806",
            legal_statistical_area_description="Ste. Genevieve County",
            county_type="1",
            land_area_meters=1292799524,
            water_area_meters=19740673,
            latitude=37.89018,
            longitude=-90.18117,
        )

        County.objects.create(
            name="District of Columbia",
            state="DC",
            county_fips="11001",
            ansi_code="01702382",
            legal_statistical_area_description="District of Columbia",
            county_type=None,
            land_area_meters=158114680,
            water_area_meters=18884970,
            latitude=38.904149,
            longitude=-77.017094,
        )

        County.objects.create(
            name="Yavapai",
            state="AZ",
            county_fips="04025",
            ansi_code="00042809",
            legal_statistical_area_description="Yavapai County",
            county_type="1",
            land_area_meters=21039764981,
            water_area_meters=11501683,
            latitude=34.630044,
            longitude=-112.573745,
        )

    def test_get_county_by_string_parish_or_county(self):
        """Geocoders like to return the parish/county in the name"""
        county = County.objects.get_by_string("St Tammany Parish", "LA")
        self.assertEqual(County.objects.get(state="LA"), county)
        county = County.objects.get_by_string("St Tammany")
        self.assertEqual(County.objects.get(state="LA"), county)

        county = County.objects.get_by_string("Ste Genevieve County", "MO")
        self.assertEqual(County.objects.get(state="MO"), county)
        county = County.objects.get_by_string("Ste Genevieve")
        self.assertEqual(County.objects.get(state="MO"), county)

        # This is a special case we need to handle
        # All geocoders come back with a different response but for DC there is only one county
        county = County.objects.get_by_string("City of Washington", "DC")
        self.assertEqual(County.objects.get(state="DC"), county)
        county = County.objects.get_by_string("Washington", "DC")
        self.assertEqual(County.objects.get(state="DC"), county)

    def test_get_city_by_string_with_state(self):
        city, created = City.objects.get_or_create_by_string(name="Cordes Junction", state="AZ")
        self.assertEqual(created, True)
        self.assertEqual(City.objects.count(), 1)
        self.assertEqual(city.name, "Cordes Junction")
        self.assertEqual(city.county.name, "Yavapai")
        self.assertAlmostEqual(city.latitude, 34.327, 2)
        self.assertAlmostEqual(city.longitude, -112.118, 2)
        self.assertEqual(city.place_fips, "9900000")

        city, created = City.objects.get_or_create_by_string(name="Cordes Junction", state="AZ")
        self.assertEqual(created, False)
        self.assertEqual(City.objects.count(), 1)

        city, created = City.objects.get_or_create_by_string(
            name="Cordes Junction", county=County.objects.get(state="AZ")
        )
        self.assertEqual(created, False)
        self.assertEqual(City.objects.count(), 1)

    def test_get_city_by_string_with_county(self):
        city, _ = City.objects.get_or_create_by_string(
            name="Cordes Junction", county=County.objects.get(state="AZ")
        )

        self.assertEqual(City.objects.count(), 1)
        self.assertEqual(city.name, "Cordes Junction")
        self.assertEqual(city.county.name, "Yavapai")
        self.assertAlmostEqual(city.latitude, 34.327, 2)
        self.assertAlmostEqual(city.longitude, -112.118, 2)
        self.assertEqual(city.place_fips, "9900000")
