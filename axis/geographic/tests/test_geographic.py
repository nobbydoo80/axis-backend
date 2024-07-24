"""geographic.py: Django geographic.tests"""


import logging
import random

from django.urls import reverse
from django.test import TestCase

from axis.core.tests.client import AxisClient
from axis.core.tests.testcases import AxisTestCase
from axis.geocoder.models import GeocodeResponse
from .factories import real_county_factory
from ..utils.legacy import format_geographic_input
from ..models import ClimateZone, County, City, Place

import sys

from ...core.tests.factories import general_admin_factory

if "test" in sys.argv:
    from .models import LogicalPlace

__author__ = "Steven Klass"
__date__ = "12/4/11 5:54 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


def network_on():
    return False


class GeographicTests(AxisTestCase):
    """Test out filehandling application"""

    client_class = AxisClient

    @classmethod
    def setUpTestData(cls):
        """Setup"""
        from django.contrib.contenttypes.models import ContentType

        real_county_factory("Maricopa", "AZ")
        real_county_factory("Pinal", "AZ")

        city = City.objects.last()
        city.place_fips = "9900000"
        city.save()

        cls.content_type = ContentType.objects.all()[0]
        cls.city = City.objects.get(name="Gilbert", county__state="AZ")
        general_admin_factory(company__city=cls.city)
        cls.street_line1 = "3316 East Maplewood Street"
        cls.zipcode = "85297-9348"

        cls.addr1_dict = dict(
            lot_number=40,
            street_line1=cls.street_line1,
            city=cls.city.name,
            state="AZ",
            zipcode=cls.zipcode,
        )

        cls.cross_street = "Pecos Rd and Higley Rd"
        cls.intersection = dict(intersection=cls.cross_street, city=cls.city, state="AZ")

    def test_climate_zones(self):
        """Test climate zones.  Note we are testing a sample of them"""
        for zone in ["2b", "2B"]:
            ClimateZone.objects.get_by_code("%s" % zone)

    def test_login_required(self):
        city = City.objects.first()
        url = reverse("city:view", kwargs={"pk": city.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(url, response["Location"], msg=url)
        self.assertIn(reverse("auth:login"), response["Location"])

        url = reverse("city:add")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(url, response["Location"], msg=url)
        self.assertIn(reverse("auth:login"), response["Location"])

        url = reverse("city:update", kwargs={"pk": city.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(url, response["Location"], msg=url)
        self.assertIn(reverse("auth:login"), response["Location"])

        url = reverse("city:delete", kwargs={"pk": city.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(url, response["Location"], msg=url)
        self.assertIn(reverse("auth:login"), response["Location"])

    def test_user_has_permissions(self):
        """Test that we can login and see communities"""
        user = self.admin_user
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        self.assertEqual(user.has_perm("geographic.change_city"), True)
        self.assertEqual(user.has_perm("geographic.add_city"), True)
        self.assertEqual(user.has_perm("geographic.delete_city"), True)
        self.assertEqual(user.has_perm("geographic.view_city"), True)

        city = City.objects.filter(place_fips__startswith="99000").get()

        url = reverse("city:view", kwargs={"pk": city.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        url = reverse("city:add")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.assertTrue(user.has_perm("geographic.change_city"))
        self.assertTrue(city.can_be_edited(user))

        url = reverse("city:update", kwargs={"pk": city.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        url = reverse("city:delete", kwargs={"pk": city.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_create_view(self):
        """Test creation of a City"""
        from axis.geographic.models import City

        user = self.admin_user
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        county = County.objects.get(name__iexact="Maricopa")

        # Create the Builder Agreement
        data = {
            "name": "Waddel",
            "county": county.id,
            "land_area_meters": 0,
            "water_area_meters": 0,
            "latitude": 0,
            "longitude": 0,
        }

        url = reverse("city:add")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)

        city = City.objects.get(name=data["name"])
        self.assertRedirects(response, city.get_absolute_url())

        response = self.client.get(city.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        for key, value in data.items():
            if key in ["county", "latitude", "longitude"]:
                continue
            self.assertEqual(getattr(response.context["object"], key), value)

        self.assertEqual(str(response.context["object"].county.id), str(county.id))

        for item in ["county", "latitude", "longitude"]:
            self.assertIsNotNone(getattr(response.context["object"], item))

        self.assertEqual(city.place_fips, "9900001")

    def test_update_view(self):
        """Test update of a City"""
        from axis.geographic.models import City

        user = self.admin_user
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        city = City.objects.all()[0]
        self.assertNotEqual(city.place_fips[:3], "990")
        city.place_fips = "9909999"
        city.save()

        data = {
            "name": city.name.lower(),
            "county": city.county.id,
            "land_area_meters": city.land_area_meters,
            "water_area_meters": city.water_area_meters,
            "latitude": city.longitude,
            "longitude": 0,
        }
        url = reverse("city:update", kwargs={"pk": city.id})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response = self.client.post(url, data=data)
        self.assertRedirects(response, city.get_absolute_url())
        response = self.client.get(city.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        for key, value in data.items():
            if key in ["county", "latitude", "longitude"]:
                continue
            self.assertEqual(getattr(response.context["object"], key), value)

        self.assertEqual(str(response.context["object"].county.id), str(city.county.id))

        for item in ["county", "latitude", "longitude"]:
            self.assertIsNotNone(getattr(response.context["object"], item))

    def test_delete_view(self):
        """Test delete a city"""
        user = self.admin_user
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        county = County.objects.get(name__iexact="Maricopa")

        # Create the Builder Agreement
        data = {
            "name": "Waddel",
            "county": county.id,
            "land_area_meters": 0,
            "water_area_meters": 0,
            "latitude": 0,
            "longitude": 0,
        }

        response = self.client.post(reverse("city:add"), data=data)
        self.assertEqual(response.status_code, 302)

        city = City.objects.get(name=data["name"])

        initial_city_count = City.objects.filter_by_company(user.company).all().count()

        self.assertRedirects(response, city.get_absolute_url())
        self.assertEqual(city.place_fips, "9900001")

        url = reverse("city:delete", kwargs={"pk": city.id})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response = self.client.post(url)
        self.assertRedirects(response, reverse("home"))
        cities = City.objects.filter_by_company(user.company)
        self.assertEqual(initial_city_count - 1, cities.count())

    def test_delete_defaults(self):
        """Will ensure that you can't delete default cities"""
        user = random.choice(list(self.user_model.objects.filter(is_company_admin=True)))
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )
        city = City.objects.all()[0]
        response = self.client.get(reverse("city:delete", kwargs={"pk": city.id}))
        self.assertEqual(response.status_code, 403)


class GeographicGeocodeDataToPlace(TestCase):
    """
    Tests that data from a geocode response updates data on a place object.
    """

    fixtures = ["test_geographic.json", "test_geocoder.json"]

    def setUp(self):
        self.geocode_response = GeocodeResponse.objects.get(pk=54)
        self.gr_place = self.geocode_response.broker.place
        self.place = Place.objects.create(cross_roads="Foo", state="ID")

    def test_geocode_updates_place_cross_roads(self):
        self.assertNotEqual(self.place.cross_roads, self.gr_place.intersection)
        self.place.geocode_response = self.geocode_response
        self.place.load_geocode_response_data()
        self.place.save()
        self.assertEqual(self.place.cross_roads, self.gr_place.intersection)

    def test_geocode_updates_place_city(self):
        self.assertIsNone(self.place.city)
        self.place.geocode_response = self.geocode_response
        self.place.load_geocode_response_data()
        self.place.save()
        self.assertEqual(self.place.city.name, self.gr_place.city)

    def test_geocode_updates_place_county(self):
        self.assertIsNone(self.place.county)
        self.place.geocode_response = self.geocode_response
        self.place.load_geocode_response_data()
        self.place.save()
        self.assertEqual(self.place.county.legal_statistical_area_description, self.gr_place.county)

    def test_geocode_updates_place_state(self):
        self.assertNotEqual(self.place.state, self.gr_place.state)
        self.place.geocode_response = self.geocode_response
        self.place.load_geocode_response_data()
        self.place.save()
        self.assertEqual(self.place.state, self.gr_place.state)


class GeographicPlaceAndPlacedModelDataSync(TestCase):
    """
    Test case that ensures ``PlacedModel`` subclasses geographic data stays in
    sync with their related ``Place`` object.

    """

    def setUp(self):
        self.geographic_data = {
            "cross_roads": "N Center & 1st N",
            "state": "ID",
            "address_override": True,
        }
        self.placed_obj = LogicalPlace.objects.create(**self.geographic_data)

    def test_placed_obj_creates_place(self):
        for f in self.placed_obj.DENORMALIZED_PLACE_FIELDS():
            try:
                self.assertEqual(getattr(self.placed_obj, f), getattr(self.placed_obj.place, f))
            except:
                raise

    def test_place_creates_nothing(self):
        place = Place.objects.create(**self.geographic_data)
        self.assertEqual(list(place.logicalplace_set.all()), [])

    def test_placed_obj_save_updates_place(self):
        self.placed_obj.cross_roads = "Washington St & Whitaker St"
        self.placed_obj.state = "RI"
        self.placed_obj.save()

        for f in self.placed_obj.DENORMALIZED_PLACE_FIELDS():
            self.assertEqual(getattr(self.placed_obj, f), getattr(self.placed_obj.place, f))

    def test_place_save_updates_placed_objs(self):
        place = self.placed_obj.place
        place.cross_roads = "Washington St & Whitaker St"
        place.state = "RI"
        place.save()

        for placed_obj in place.logicalplace_set.all():
            for f in placed_obj.DENORMALIZED_PLACE_FIELDS():
                self.assertEqual(getattr(place, f), getattr(placed_obj, f))


class GeographicUtilsFormatInputTestCase(TestCase):
    """
    Test case that exercises ``axis.geographic.utils.format_geographic_input``

    """

    def setUp(self):
        from axis.community.models import Community

        self.county_obj = County.objects.create(
            name="Madison",
            state="ID",
            legal_statistical_area_description="Madison County",
            land_area_meters=1215237613,
            water_area_meters=10412190,
            latitude=43.789709,
            longitude=-111.65655,
        )
        self.city_obj = City.objects.create(
            name="Rexburg",
            county=self.county_obj,
            land_area_meters=25280958,
            water_area_meters=213968,
            latitude=43.822893,
            longitude=-111.790988,
        )
        self.community_obj = Community.objects.create(
            name="Downtown",
            city=self.city_obj,
            county=self.county_obj,
            state="ID",
            latitude=43.822893,
            longitude=-111.790988,
        )

        self.zipcode = "83440"
        self.state = "ID"
        self.county = self.county_obj
        self.city = self.city_obj
        self.community = self.community_obj
        self.intersection = "N Center & 1st N"
        self.street_line1 = "36 E 1st N"
        self.street_line2 = "Unit A"

    def get_data(self, *attrs):
        """
        A helper method that returns a dictionary suitable for use with
        ``format_geographic_input`` container the keys listed in ``attrs``.
        """
        return {a: getattr(self, a) for a in attrs}

    def test_no_data(self):
        address, raw_parts, entity_type = format_geographic_input()
        self.assertEqual(address, "")
        self.assertEqual(entity_type, None)

    def test_only_zipcode(self):
        """
        At this time we do not ever expect to be handed only a zipcode, but
        still this tests that we get what is expected if only a zipcode is given.
        """
        address, raw_parts, entity_type = format_geographic_input(zipcode=self.zipcode)
        self.assertEqual(address, ", 83440")
        self.assertEqual(entity_type, None)

    def test_state_only(self):
        """
        At this time we do not ever expect to be handed only a state, but we
        still test that if it alone is handed in, we get what we expect.
        """
        address, raw_parts, entity_type = format_geographic_input(state=self.state)
        self.assertEqual(address, self.state)
        self.assertEqual(entity_type, None)

    def test_state_and_zipcode(self):
        """
        At this time we do not ever expect to be handed only a state and
        zipcode, but we still test that if it alone is handed in, we get what
        we expect.
        """
        data = self.get_data("state", "zipcode")
        address, raw_parts, entity_type = format_geographic_input(**data)
        self.assertEqual(address, "ID, 83440")
        self.assertEqual(entity_type, None)

    def test_county(self):
        data = self.get_data("county", "state", "zipcode")
        address, raw_parts, entity_type = format_geographic_input(**data)
        self.assertEqual(address, "Madison County, ID, 83440")
        self.assertEqual(entity_type, "county")

    def test_county_with_street_level(self):
        """
        Tests that the county is included when there is street-level data if
        there is no city data.
        """
        data = self.get_data("intersection", "county", "state", "zipcode")
        address, raw_parts, entity_type = format_geographic_input(**data)
        self.assertEqual(address, "N Center & 1st N, Madison County, ID, 83440")
        self.assertEqual(entity_type, "intersection")

        del data["intersection"]
        data["street_line1"] = self.street_line1

        address, raw_parts, entity_type = format_geographic_input(**data)
        self.assertEqual(address, "36 E 1st N, Madison County, ID, 83440")
        self.assertEqual(entity_type, "street_address")

    def test_county_with_city_and_street_level(self):
        """
        Tests that the county is not included when there is street-level data
        if there is city data.
        """
        data = self.get_data("intersection", "city", "county", "state", "zipcode")
        address, raw_parts, entity_type = format_geographic_input(**data)
        self.assertEqual(address, "N Center & 1st N, Rexburg, ID, 83440")
        self.assertEqual(entity_type, "intersection")

        del data["intersection"]
        data["street_line1"] = self.street_line1

        address, raw_parts, entity_type = format_geographic_input(**data)
        self.assertEqual(address, "36 E 1st N, Rexburg, ID, 83440")
        self.assertEqual(entity_type, "street_address")

    def test_city(self):
        data = self.get_data("city", "state")
        address, raw_parts, entity_type = format_geographic_input(**data)
        self.assertEqual(address, "Rexburg, Madison County, ID")
        self.assertEqual(entity_type, "city")

    def test_intersection(self):
        data = self.get_data("intersection", "city", "state", "zipcode")
        address, raw_parts, entity_type = format_geographic_input(**data)
        self.assertEqual(address, "N Center & 1st N, Rexburg, ID, 83440")
        self.assertEqual(entity_type, "intersection")

    def test_intersection_as_cross_roads(self):
        """
        Sometimes ``intersection`` is passed to the function as ``cross_roads``,
        so we need to be sure that always works.
        """
        data = self.get_data("intersection", "city", "state", "zipcode")
        data["cross_roads"] = data.pop("intersection")
        address, raw_parts, entity_type = format_geographic_input(**data)
        self.assertEqual(address, "N Center & 1st N, Rexburg, ID, 83440")
        self.assertEqual(entity_type, "intersection")

    def test_street_address(self):
        data = self.get_data("street_line1", "city", "state", "zipcode")
        address, raw_parts, entity_type = format_geographic_input(**data)
        self.assertEqual(address, "36 E 1st N, Rexburg, ID, 83440")
        self.assertEqual(entity_type, "street_address")

        data["street_line2"] = self.street_line2

        address, raw_parts, entity_type = format_geographic_input(**data)
        self.assertEqual(address, "36 E 1st N, Unit A, Rexburg, ID, 83440")
        self.assertEqual(entity_type, "street_address")

    def test_community_is_city(self):
        """
        Tests that a community without an intersection is geocoded as a city.

        Note that this is current behavior. It would be smart to account for
        latitude and longitude as well.
        """
        address, raw_parts, entity_type = format_geographic_input(community=self.community)
        self.assertEqual(address, "Rexburg, Madison County, ID")
        self.assertEqual(entity_type, "city")

    def test_community_with_intersection(self):
        """
        Tests that a community with an intersection has that intersection included.
        """
        self.community_obj.cross_roads = self.intersection
        self.community_obj.save()
        address, raw_parts, entity_type = format_geographic_input(community=self.community)
        self.assertEqual(address, "N Center & 1st N, Rexburg, ID")
        self.assertEqual(entity_type, "intersection")

    def test_community_with_intersection_and_intersection(self):
        """
        Tests that if both an intersection and a community with an intersection
        are passed in, the former takes precedence.
        """
        self.community_obj.intersection = "Foo & Bar"
        self.community_obj.save()
        data = self.get_data("intersection", "community")
        address, raw_parts, entity_type = format_geographic_input(**data)
        self.assertEqual(address, "N Center & 1st N, Rexburg, ID")
        self.assertEqual(entity_type, "intersection")

    def test_community_with_intersection_and_street_address(self):
        """
        Tests that if both street_lineN and a community with an intersection are
        passed in, the form takes precedence.
        """
        self.community_obj.cross_roads = "Foo & Bar"
        self.community_obj.save()
        data = self.get_data("street_line1", "community")
        address, raw_parts, entity_type = format_geographic_input(**data)
        self.assertEqual(address, "36 E 1st N, Rexburg, ID")
        self.assertEqual(entity_type, "street_address")

    def test_community_overrides(self):
        """
        When a community is passed in its city, county, and state data should
        take precedence over any of that same data that may have been passed in.
        """
        data = {
            "community": self.community,
            "city": "Foo City",
            "county": "Bar County",
            "state": "Ky",
        }
        address, raw_parts, entity_type = format_geographic_input(**data)
        self.assertEqual(address, "Rexburg, Madison County, ID")
        self.assertEqual(entity_type, "city")


class GeographicUtilsFormatInputWithPKsTestCase(GeographicUtilsFormatInputTestCase):
    """
    A test case that uses object pk's instead of model objects as arguments to
    format_geographic_input.

    """

    def setUp(self):
        super(GeographicUtilsFormatInputWithPKsTestCase, self).setUp()

        self.county = self.county_obj.pk
        self.city = self.city_obj.pk
        self.community = self.community_obj.pk
