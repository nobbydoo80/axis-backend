"""serializers.py - Axis"""

import logging

from rest_framework.exceptions import ValidationError

from axis.company.tests.mixins import CompaniesAndUsersTestMixin
from axis.core.tests.testcases import ApiV3Tests
from axis.geographic.api_v3.serializers import BaseCitySerializer
from axis.geographic.models import City, County, USState, Country
from axis.geographic.tests.factories import real_city_factory, real_county_factory
from axis.geographic.utils.country import resolve_country
from axis.geographic.utils.legacy import format_geographic_input

from axis.geocoder.api_v3.serializers import (
    GeocodeMatchesSerializer,
    GeocodeCityMatchesSerializer,
    GeocodeCitySerializer,
)
from ...models import Geocode

__author__ = "Steven K"
__date__ = "4/16/20 07:52"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

log = logging.getLogger(__name__)


class GeocodeTestBase(CompaniesAndUsersTestMixin):
    include_company_types = ["general", "builder", "rater"]

    @classmethod
    def setUpTestData(cls):
        cls.watertown = real_city_factory("Watertown", "WI")
        super(GeocodeTestBase, cls).setUpTestData()


class TestGeocodeMatchesStreetSerializer(GeocodeTestBase, ApiV3Tests):
    """Test GeocodeMatch Serializer"""

    def test_street_to_internal_value(self):
        """Test out the conversion to an internal value"""
        data = {
            "street_line1": "200 North Church Street",
            "city": self.watertown.pk,
            "zipcode": "53094",
        }
        serializer = GeocodeMatchesSerializer(data=data)
        self.assertTrue(serializer.is_valid(raise_exception=True))

        vd = serializer.validated_data.copy()
        self.assertEqual(vd["street_line1"], data["street_line1"])
        self.assertEqual(vd["city"].pk, self.watertown.pk)
        self.assertEqual(vd["zipcode"], data["zipcode"])
        self.assertEqual(vd["street_line2"], "")
        self.assertEqual(vd["intersection"], "")

    def test_save_single_and_geocode(self):
        data = {
            "street_line1": "200 North Church Street",
            "city": self.watertown.pk,
            "zipcode": "53094",
        }

        serializer = GeocodeMatchesSerializer(data=data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        obj, created = serializer.save()

        self.assertEqual(obj.raw_address, "200 North Church Street, Watertown, WI, 53094")
        self.assertEqual(obj.entity_type, "street_address")
        self.assertEqual(obj.raw_street_line1, data["street_line1"])
        self.assertEqual(obj.raw_zipcode, data["zipcode"])
        self.assertEqual(obj.raw_city.pk, data["city"])
        self.assertEqual(obj.raw_street_line2, "")
        self.assertEqual(obj.raw_cross_roads, "")
        self.assertIsNotNone(obj.created_date)
        self.assertIsNotNone(obj.modified_date)
        self.assertEqual(obj.responses.count(), 2)

        bing = obj.responses.get(engine="Bing")
        self.assertEqual(bing.geocode.pk, obj.pk)
        b_keys = [
            "__type",
            "bbox",
            "name",
            "point",
            "address",
            "confidence",
            "entityType",
            "geocodePoints",
            "matchCodes",
        ]
        self.assertEqual(set(bing.place.keys()), set(b_keys))

        google = obj.responses.get(engine="Google")
        self.assertEqual(google.geocode.pk, obj.pk)
        g_keys = ["place_id", "address_components", "formatted_address", "types", "geometry"]
        self.assertEqual(set(google.place.keys()), set(g_keys))

    def test_google_single_address_broker(self):
        """Verify that as we parse this we get real normalized data."""

        data = {
            "street_line1": "200 North Church Street",
            "city": self.watertown.pk,
            "zipcode": "53094",
        }

        serializer = GeocodeMatchesSerializer(data=data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        obj, created = serializer.save()

        google = obj.responses.get(engine="Google")
        self.assertEqual(google.geocode.pk, obj.pk)

        # for k, v in google.broker.place.__dict__.items():
        #     print('self.assertEqual(\'google.broker.place.%s\', %r)' % (k, v))

        self.assertEqual(google.broker.place.street_line1, "200 N Church St")
        self.assertEqual(google.broker.place.street_line2, None)
        self.assertEqual(google.broker.place.city, "Watertown")
        self.assertEqual(google.broker.place.state, "WI")
        self.assertEqual(google.broker.place.county, "Jefferson County")
        self.assertEqual(google.broker.place.country, "US")
        self.assertEqual(google.broker.place.zipcode, "53094")
        self.assertEqual(google.broker.place.neighborhood, None)
        self.assertEqual(google.broker.place.intersection, None)
        self.assertAlmostEqual(google.broker.place.latitude, 43.1960, 3)
        self.assertAlmostEqual(google.broker.place.longitude, -88.7287, 3)
        self.assertEqual(
            google.broker.place.formatted_address, "200 N Church St, Watertown, WI 53094"
        )
        self.assertEqual(google.broker.place.entity_type, "street_address")
        self.assertEqual(google.broker.place.is_confirmed, True)
        self.assertEqual(
            google.broker.place.search_string, "200 North Church Street, Watertown, WI, 53094"
        )
        self.assertEqual(google.broker.place.url_sent, None)
        self.assertEqual(
            google.broker.place.map_url,
            "https://maps.google.com/?q=200+North+Church+Street%2C+Watertown%2C+WI%2C+53094",
        )
        self.assertEqual(google.broker.place.geocoder_engine_name, "Google")
        self.assertIsNotNone(google.broker.place.response)
        self.assertIsNotNone(google.broker.place.geocode_date)
        self.assertEqual(google.broker.place.correlation_distance_km, 0.1)
        self.assertEqual(google.broker.place.street_number, "200")
        self.assertEqual(google.broker.place.route, "N Church St")

    def test_bing_single_address_broker(self):
        """Verify that as we parse this we get real normalized data."""

        data = {
            "street_line1": "200 North Church Street",
            "city": self.watertown.pk,
            "zipcode": "53094",
        }

        serializer = GeocodeMatchesSerializer(data=data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        obj, created = serializer.save()

        bing = obj.responses.get(engine="Bing")
        self.assertEqual(bing.geocode.pk, obj.pk)

        # for k, v in bing.broker.place.__dict__.items():
        #     print('self.assertEqual(\'bing.broker.place.%s\', %r)' % (k, v))
        self.assertEqual(bing.broker.place.street_line1, "200 N Church St")
        self.assertEqual(bing.broker.place.street_line2, None)
        self.assertEqual(bing.broker.place.city, "Watertown")
        self.assertEqual(bing.broker.place.state, "WI")
        self.assertEqual(bing.broker.place.county, None)
        self.assertEqual(bing.broker.place.country, "US")
        self.assertEqual(bing.broker.place.zipcode, "53094")
        self.assertEqual(bing.broker.place.neighborhood, None)
        self.assertEqual(bing.broker.place.intersection, None)
        self.assertAlmostEqual(bing.broker.place.latitude, 43.1960, 3)
        self.assertAlmostEqual(bing.broker.place.longitude, -88.7287, 3)
        self.assertEqual(
            bing.broker.place.formatted_address, "200 N Church St, Watertown, WI 53094"
        )
        self.assertEqual(bing.broker.place.entity_type, "street_address")
        self.assertEqual(bing.broker.place.is_confirmed, True)
        self.assertEqual(
            bing.broker.place.search_string, "200 North Church Street, Watertown, WI, 53094"
        )
        self.assertEqual(bing.broker.place.url_sent, None)
        self.assertEqual(
            bing.broker.place.map_url,
            "//www.bing.com/maps/?v=2&where1=200+North+Church+Street%2C+Watertown%2C+WI%2C+53094",
        )
        self.assertEqual(bing.broker.place.geocoder_engine_name, "Bing")
        self.assertEqual(bing.broker.place.correlation_distance_km, 0.1)

    def test_intl_address_geocode(self):
        """Test the Serializer for Matches"""
        City.objects.all().delete()
        city = real_city_factory("Santiago de los caballeros", country=resolve_country("DO").abbr)

        data = {
            "street_line1": "autop. juan pablo duarte km. 28",
            "city": city.pk,
            "zipcode": "51000",
        }

        serializer = GeocodeMatchesSerializer(data=data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        obj, created = serializer.save()

        with self.subTest("GeocodeMatchesSerializer Intl"):
            self.assertEqual(
                obj.raw_address,
                "autop. juan pablo duarte km. 28, Santiago De Los Caballeros, 51000, DO",
            )
            self.assertEqual(obj.entity_type, "street_address")
            self.assertEqual(obj.raw_street_line1, data["street_line1"])
            self.assertEqual(obj.raw_zipcode, data["zipcode"])
            self.assertEqual(obj.raw_city.pk, data["city"])
            self.assertEqual(obj.raw_country, city.country)
            self.assertEqual(obj.raw_street_line2, "")
            self.assertEqual(obj.raw_cross_roads, "")
            self.assertIsNotNone(obj.created_date)
            self.assertIsNotNone(obj.modified_date)
            self.assertEqual(obj.responses.count(), 2)

        with self.subTest("Google Broker"):
            google = obj.responses.get(engine="Google")
            self.assertEqual(google.geocode.pk, obj.pk)

            # for k, v in google.broker.place.__dict__.items():
            #     print(f"self.assertEqual(google.broker.place.{k}, {v!r})")

            self.assertEqual(google.broker.place.street_line1, "Km. 28 Autop. Juan Pablo Duarte")
            self.assertEqual(google.broker.place.street_line2, None)
            self.assertEqual(google.broker.place.city, "Santiago De Los Caballeros")
            self.assertEqual(google.broker.place.state, None)
            self.assertEqual(google.broker.place.county, None)
            self.assertEqual(google.broker.place.country, "DO")
            self.assertEqual(google.broker.place.zipcode, "51000")
            self.assertEqual(google.broker.place.neighborhood, None)
            self.assertEqual(google.broker.place.intersection, None)
            self.assertAlmostEqual(google.broker.place.latitude, 19.4359, 3)
            self.assertAlmostEqual(google.broker.place.longitude, -70.6609, 3)
            self.assertEqual(
                google.broker.place.formatted_address,
                "Autop. Juan Pablo Duarte Km. 28, Santiago De Los Caballeros 51000, DO",
            )
            self.assertEqual(google.broker.place.entity_type, "street_address")
            self.assertEqual(google.broker.place.is_confirmed, True)
            self.assertEqual(
                google.broker.place.search_string,
                "autop. juan pablo duarte km. 28, Santiago De Los Caballeros, 51000, DO",
            )
            self.assertEqual(google.broker.place.url_sent, None)
            self.assertEqual(
                google.broker.place.map_url,
                "https://maps.google.com/?q=autop.+juan+pablo+duarte+km.+28%2C+Santiago+De+Los+Caballeros%2C+51000%2C+DO",
            )
            self.assertEqual(google.broker.place.geocoder_engine_name, "Google")
            self.assertIsNotNone(google.broker.place.geocode_date)
            self.assertEqual(google.broker.place.correlation_distance_km, 0.1)
            self.assertEqual(google.broker.place.suite, None)
            self.assertEqual(google.broker.place.street_number, "Km. 28")
            self.assertEqual(google.broker.place.route, "Autop. Juan Pablo Duarte")

        with self.subTest("Bing Broker"):
            bing = obj.responses.get(engine="Bing")
            self.assertEqual(bing.geocode.pk, obj.pk)
            # for k, v in bing.broker.place.__dict__.items():
            #     print(f"self.assertEqual(bing.broker.place.{k}, {v!r})")

            self.assertEqual(bing.broker.place.street_line1, "Calle Autopista Duarte")
            self.assertEqual(bing.broker.place.street_line2, None)
            self.assertEqual(bing.broker.place.city, "Santiago de los Caballeros")
            self.assertEqual(bing.broker.place.state, None)
            self.assertEqual(bing.broker.place.county, None)
            self.assertEqual(bing.broker.place.country, "DO")
            self.assertEqual(bing.broker.place.zipcode, None)
            self.assertEqual(bing.broker.place.neighborhood, None)
            self.assertEqual(bing.broker.place.intersection, None)
            self.assertAlmostEqual(bing.broker.place.latitude, 19.4445, 3)
            self.assertAlmostEqual(bing.broker.place.longitude, -70.6716, 3)
            self.assertEqual(
                bing.broker.place.formatted_address,
                "Calle Autopista Duarte Santiago de los Caballeros, Santiago",
            )
            self.assertEqual(bing.broker.place.entity_type, "street_address")
            self.assertEqual(bing.broker.place.is_confirmed, False)
            self.assertEqual(
                bing.broker.place.search_string,
                "autop. juan pablo duarte km. 28, Santiago De Los Caballeros, 51000, DO",
            )
            self.assertEqual(bing.broker.place.url_sent, None)
            self.assertEqual(
                bing.broker.place.map_url,
                "//www.bing.com/maps/?v=2&where1=autop.+juan+pablo+duarte+km.+28%2C+Santiago+De+Los+Caballeros%2C+51000%2C+DO",
            )
            self.assertEqual(bing.broker.place.geocoder_engine_name, "Bing")

            self.assertIsNotNone(bing.broker.place.geocode_date)
            self.assertEqual(bing.broker.place.correlation_distance_km, 0.1)


class TestGeocodeMatchesIntersectionSerializer(GeocodeTestBase, ApiV3Tests):
    """Test GeocodeMatch Serializer"""

    def test_intersection_to_internal_value(self):
        """Test out the conversion to an internal value"""
        data = {
            "intersection": "Main / Church St",
            "city": self.watertown.pk,
        }
        serializer = GeocodeMatchesSerializer(data=data)
        self.assertTrue(serializer.is_valid(raise_exception=True))

        vd = serializer.validated_data
        self.assertEqual(vd["street_line1"], "")
        self.assertEqual(vd["city"].pk, self.watertown.pk)
        self.assertEqual(vd["zipcode"], "")
        self.assertEqual(vd["street_line2"], "")
        self.assertEqual(vd["intersection"], data.get("intersection"))

    def test_internal_value_conflict(self):
        """Test out the conversion only support intersections OR streets not both."""
        data = {
            "street_line1": "200 North Church Street",
            "city": self.watertown.pk,
            "zipcode": "53094",
            "intersection": "foo",
        }
        serializer = GeocodeMatchesSerializer(data=data)
        self.assertRaises(ValidationError, serializer.is_valid, raise_exception=True)

        data = {
            "street_line2": "200 North Church Street",
            "city": self.watertown.pk,
            "intersection": "foo",
        }
        serializer = GeocodeMatchesSerializer(data=data)
        self.assertRaises(ValidationError, serializer.is_valid, raise_exception=True)

    def test_save_intersection_and_geocode(self):
        data = {
            "street_line1": "200 North Church Street",
            "city": self.watertown.pk,
            "zipcode": "53094",
        }

        serializer = GeocodeMatchesSerializer(data=data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        serializer.save()

        # print(Geocode.objects.first().__dict__)
        # for item in GeocodeResponse.objects.all():
        #     print(item.__dict__)
        # print(GeocodeResponse.objects.all())


class TestGeocodeMatchesTroubleMakersSerializer(ApiV3Tests):
    """Test GeocodeMatch Serializer.  These are trouble makeers.."""

    @classmethod
    def setUpTestData(cls):
        resolve_country("PR")
        resolve_country("VI")

    def test_puerto_rico_confirmed_address(self):
        "192 Av. Dr. Francisco Susoni, Hatillo, 00659, Puerto Rico"
        serializer = BaseCitySerializer(data=dict(name="Hatillo", country="PR"))
        self.assertTrue(serializer.is_valid(raise_exception=True))
        city = serializer.save()
        self.assertEqual(city.name, "Hatillo")
        input_data = {
            "street_line1": "192 Av. Dr. Francisco Susoni",
            "street_line2": "",
            "city": city,
            "country": "PR",
            "zipcode": "00659",
        }

        raw_address, raw_parts, entity_type = format_geographic_input(**input_data)
        geocode, created = Geocode.objects.get_or_create(
            raw_address=raw_address, entity_type=entity_type, defaults=raw_parts
        )
        geocode.refresh_from_db()

        self.assertEqual(geocode.responses.count(), 2)
        google = geocode.responses.get(engine="Google").get_normalized_fields()
        # for k, v in google.items():
        #     print(f"self.assertEqual(google.get('{k}'), {v!r})")
        self.assertAlmostEqual(google.get("latitude"), 18.4880, 3)
        self.assertAlmostEqual(google.get("longitude"), -66.8196, 3)
        self.assertEqual(google.get("street_line1"), "192 Av. Dr. Francisco Susoni")
        self.assertEqual(google.get("zipcode"), "00659")
        self.assertEqual(google.get("country").abbr, "PR")
        self.assertEqual(google.get("state"), None)
        self.assertEqual(google.get("county"), None)
        self.assertEqual(google.get("city"), city)
        self.assertEqual(google.get("confirmed_address"), True)

        bing = geocode.responses.get(engine="Bing").get_normalized_fields()
        # for k, v in bing.items():
        #     print(f"self.assertEqual(bing.get('{k}'), {v!r})")
        self.assertAlmostEqual(bing.get("latitude"), 18.4880, 3)
        self.assertAlmostEqual(bing.get("longitude"), -66.8195, 3)
        self.assertEqual(bing.get("street_line1"), "192 Ave Dr Susoni")
        self.assertEqual(bing.get("zipcode"), "00659")
        self.assertEqual(google.get("country").abbr, "PR")
        self.assertEqual(google.get("state"), None)
        self.assertEqual(google.get("county"), None)
        self.assertEqual(bing.get("city"), city)
        self.assertEqual(bing.get("confirmed_address"), True)

    def test_puerto_rico_bad_address(self):
        serializer = BaseCitySerializer(data=dict(name="Bayamón", country="PR"))
        self.assertTrue(serializer.is_valid(raise_exception=True))
        city = serializer.save()
        self.assertEqual(city.name, "Bayamón")
        input_data = {
            "street_line1": "Ext Villa Rica R23 Calle 11",
            "street_line2": "",
            "city": city,
            "state": "PR",
            "zipcode": "00959",
        }
        raw_address, raw_parts, entity_type = format_geographic_input(**input_data)
        geocode, created = Geocode.objects.get_or_create(
            raw_address=raw_address, entity_type=entity_type, defaults=raw_parts
        )
        geocode.refresh_from_db()
        self.assertEqual(geocode.responses.count(), 2)
        google = geocode.responses.get(engine="Google").get_normalized_fields()
        # for k, v in google.items():
        #     print(f"self.assertEqual(google.get('{k}'), {v!r})")
        self.assertAlmostEqual(google.get("latitude"), 18.3795, 3)
        self.assertAlmostEqual(google.get("longitude"), -66.1789, 3)
        self.assertEqual(google.get("zipcode"), "00957")
        self.assertEqual(google.get("country").abbr, "PR")
        self.assertEqual(google.get("state"), None)
        self.assertEqual(google.get("county"), None)
        self.assertEqual(google.get("city").id, city.id)
        self.assertEqual(google.get("confirmed_address"), False)

        # We are not looking at Bing here it's really wrong
        bing = geocode.responses.get(engine="Bing").get_normalized_fields()
        # for k, v in bing.items():
        #     print(f"self.assertEqual(bing.get('{k}'), {v!r})")
        self.assertAlmostEqual(bing.get("latitude"), 18.3865, 3)
        self.assertAlmostEqual(bing.get("longitude"), -66.1580, 3)
        self.assertEqual(bing.get("state"), None)
        self.assertEqual(bing.get("country").abbr, "PR")
        self.assertEqual(bing.get("county"), None)
        self.assertIsNotNone(bing.get("city"), None)
        self.assertEqual(bing.get("confirmed_address"), False)

    def test_virgin_islands(self):
        """This will flex out city creation for a geocoded address"""
        geocode, created = Geocode.objects.get_or_create(
            raw_address="Kingshill USVI 00850", entity_type="city"
        )
        geocode.refresh_from_db()

        google = geocode.responses.get(engine="Google").get_normalized_fields()
        # for k, v in google.items():
        #     print(f"self.assertEqual(google.get('{k}'), {v!r})")
        self.assertAlmostEqual(google.get("latitude"), 17.7230, 3)
        self.assertAlmostEqual(google.get("longitude"), -64.7822, 3)
        self.assertEqual(google.get("zipcode"), None)
        self.assertEqual(google.get("country").abbr, "VI")
        self.assertEqual(google.get("state"), None)
        self.assertEqual(google.get("county"), None)
        self.assertEqual(google.get("city"), None)
        self.assertEqual(google.get("confirmed_address"), False)

        bing = geocode.responses.get(engine="Bing").get_normalized_fields()
        # for k, v in bing.items():
        #     print(f"self.assertEqual(bing.get('{k}'), {v!r})")

        self.assertAlmostEqual(bing.get("latitude"), 17.7248, 3)
        self.assertAlmostEqual(bing.get("longitude"), -64.7930, 3)
        self.assertEqual(bing.get("zipcode"), "00850")
        self.assertEqual(google.get("country").abbr, "VI")
        self.assertEqual(google.get("state"), None)
        self.assertEqual(google.get("county"), None)
        self.assertEqual(bing.get("city"), City.objects.get())
        self.assertEqual(bing.get("confirmed_address"), False)

        self.assertEqual(City.objects.get().county, None)

    def test_import_usvi(self):
        cities = [
            "Charlotte Amalie East, St Thomas, USVI",
            "Mandal, St Thomas, USVI",
        ]
        for idx, location in enumerate(cities, start=1):
            geocode, created = Geocode.objects.get_or_create(
                raw_address=location, entity_type="city", immediate=True
            )
            geocode.refresh_from_db()
            geocode.responses.get(engine="Google").get_normalized_fields()
            geocode.responses.get(engine="Bing").get_normalized_fields()
            self.assertEqual(City.objects.filter(country__abbr="VI").count(), idx)

        self.assertEqual(City.objects.filter(country__abbr="VI").count(), 2)

    def test_fairfax_county_bing_bug2(self):
        """This has a city of Fairfax coming from bing.  We handle it in the get_county_by string
        Refer to test_matches_fairfax_county
        """
        fairfax = real_city_factory("Fairfax", "VA")
        self.assertEqual(County.objects.count(), 1)
        self.assertEqual(City.objects.count(), 1)

        input_data = {
            "street_line1": "3999 University Dr",
            "city": fairfax.pk,
            "zipcode": "22030",
        }

        serializer = GeocodeMatchesSerializer(data=input_data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        obj, created = serializer.save()

        self.assertEqual(obj.raw_address, "3999 University Dr, Fairfax, VA, 22030")
        self.assertEqual(obj.entity_type, "street_address")
        self.assertEqual(obj.immediate, False)
        self.assertEqual(obj.raw_street_line1, "3999 University Dr")
        self.assertEqual(obj.raw_street_line2, "")
        self.assertEqual(obj.raw_zipcode, "22030")
        self.assertEqual(obj.raw_city, fairfax)
        self.assertEqual(obj.raw_county, fairfax.county)
        self.assertEqual(obj.raw_state, USState.objects.get(abbr=fairfax.county.state))
        self.assertEqual(obj.raw_cross_roads, "")

        bing = obj.responses.get(engine="Bing")
        self.assertEqual(bing.geocode.pk, obj.pk)

        self.assertEqual(County.objects.count(), 1)
        self.assertEqual(City.objects.count(), 1)
        self.assertEqual(bing.broker.place.county, "City of Fairfax")

        google = obj.responses.get(engine="Google")
        self.assertEqual(google.geocode.pk, obj.pk)
        self.assertEqual(google.broker.place.county, None)


class TestGeocodeCityMatchesSerializer(ApiV3Tests):
    """Test GeocodeMatch Serializer.  These are trouble makeers.."""

    def test_matches_greenfield(self):
        """Greenfield is a new city that isn't in our db."""
        self.county = real_county_factory("Saratoga", "NY")

        self.assertFalse(City.objects.filter(name="Greenfield").exists())
        self.assertTrue(County.objects.filter(name="Saratoga", state="NY").exists())

        input_data = {
            "name": "greenfield",
            "county": self.county.pk,
        }
        serializer = GeocodeCityMatchesSerializer(data=input_data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        obj, created = serializer.save()
        with self.subTest("Geocode City Data"):
            self.assertEqual(obj.raw_address, "greenfield, Saratoga NY")
            self.assertEqual(obj.entity_type, "city")
            self.assertEqual(obj.raw_country.abbr, "US")
            self.assertEqual(obj.immediate, True)
            self.assertEqual(obj.raw_street_line1, "")
            self.assertEqual(obj.raw_street_line2, "")
            self.assertEqual(obj.raw_zipcode, "")
            self.assertEqual(obj.raw_city, None)
            self.assertEqual(obj.raw_county, self.county)
            self.assertEqual(obj.raw_state, USState.objects.get(abbr=self.county.state))
            self.assertEqual(obj.raw_cross_roads, "")

            self.assertEqual(County.objects.count(), 1)
            self.assertFalse(City.objects.filter(name="Greenfield").exists())

        #
        bing = obj.responses.get(engine="Bing")
        with self.subTest("Geocode Bing Raw data"):
            self.assertEqual(bing.geocode.pk, obj.pk)
            self.assertEqual(bing.engine, "Bing")
            self.assertEqual(bing.place["name"], "Greenfield, NY")
            self.assertEqual(bing.place["confidence"], "High")
            self.assertEqual(bing.place["entityType"], "PopulatedPlace")
            self.assertEqual(bing.place["matchCodes"], ["Good"])

        with self.subTest("Geocode Bing Parsed"):
            self.assertEqual(bing.broker.place.street_line1, None)
            self.assertEqual(bing.broker.place.street_line2, None)
            self.assertEqual(bing.broker.place.city, "Greenfield")
            self.assertEqual(bing.broker.place.state, "NY")
            self.assertEqual(bing.broker.place.county, "Saratoga County")
            self.assertEqual(bing.broker.place.country, "US")
            self.assertEqual(bing.broker.place.zipcode, None)
            self.assertEqual(bing.broker.place.neighborhood, None)
            self.assertEqual(bing.broker.place.intersection, None)
            self.assertAlmostEqual(bing.broker.place.latitude, 43.106, 2)
            self.assertAlmostEqual(bing.broker.place.longitude, -73.864, 2)
            self.assertEqual(bing.broker.place.formatted_address, "Greenfield, Saratoga County NY")
            self.assertEqual(bing.broker.place.entity_type, "city")
            self.assertEqual(bing.broker.place.is_confirmed, True)
            self.assertEqual(bing.broker.place.search_string, "greenfield, Saratoga NY")
            self.assertEqual(bing.broker.place.url_sent, None)
            self.assertEqual(bing.broker.place.geocoder_engine_name, "Bing")
            self.assertEqual(bing.broker.place.correlation_distance_km, 0.1)

        google = obj.responses.get(engine="Google")
        with self.subTest("Geocode Google Raw data"):
            self.assertEqual(google.engine, "Google")
            self.assertEqual(google.place["formatted_address"], "Greenfield, NY 12833, USA")
            self.assertEqual(google.place["types"], ["locality", "political"])

        with self.subTest("Geocode Google Parsed"):
            self.assertEqual(google.broker.place.street_line1, None)
            self.assertEqual(google.broker.place.street_line2, None)
            self.assertEqual(google.broker.place.city, "Greenfield")
            self.assertEqual(google.broker.place.state, "NY")
            self.assertEqual(google.broker.place.county, "Saratoga County")
            self.assertEqual(google.broker.place.country, "US")
            self.assertEqual(google.broker.place.zipcode, "12833")
            self.assertEqual(google.broker.place.neighborhood, None)
            self.assertEqual(google.broker.place.intersection, None)
            self.assertAlmostEqual(google.broker.place.latitude, 43.103, 2)
            self.assertAlmostEqual(google.broker.place.longitude, -73.864, 2)
            self.assertEqual(
                google.broker.place.formatted_address, "Greenfield, Saratoga County NY"
            )
            self.assertEqual(google.broker.place.entity_type, "city")
            self.assertEqual(google.broker.place.is_confirmed, True)
            self.assertEqual(google.broker.place.search_string, "greenfield, Saratoga NY")
            self.assertEqual(google.broker.place.url_sent, None)
            self.assertEqual(google.broker.place.geocoder_engine_name, "Google")
            self.assertEqual(google.broker.place.correlation_distance_km, 0.1)
            self.assertEqual(google.broker.place.suite, None)
            self.assertEqual(google.broker.place.street_number, None)
            self.assertEqual(google.broker.place.route, None)

    def test_matches_US_Town(self):
        """Ixonia Wisconsin is a new city that isn't in our db."""
        city = "ixonia"
        county = real_county_factory("Jefferson", "WI")
        City.objects.all().delete()

        input_data = {"name": city, "county": county.pk}
        serializer = GeocodeCityMatchesSerializer(data=input_data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        obj, create = serializer.save()

        with self.subTest("Geocode City Data"):
            self.assertEqual(obj.raw_address, "ixonia, Jefferson WI")
            self.assertEqual(obj.entity_type, "city")
            self.assertEqual(obj.raw_country.abbr, "US")
            self.assertEqual(obj.immediate, True)
            self.assertEqual(obj.raw_street_line1, "")
            self.assertEqual(obj.raw_street_line2, "")
            self.assertEqual(obj.raw_zipcode, "")
            self.assertEqual(obj.raw_city, None)
            self.assertEqual(obj.raw_county, county)
            self.assertEqual(obj.raw_state, USState.objects.get(abbr=county.state))
            self.assertEqual(obj.raw_cross_roads, "")

            self.assertEqual(County.objects.count(), 1)
            self.assertFalse(City.objects.filter(name__iexact=city).exists())

        #
        bing = obj.responses.get(engine="Bing")
        with self.subTest("Geocode Bing Raw data"):
            self.assertEqual(bing.geocode.pk, obj.pk)
            self.assertEqual(bing.engine, "Bing")
            self.assertEqual(bing.place["name"], "Ixonia, WI")
            self.assertEqual(bing.place["confidence"], "High")
            self.assertEqual(bing.place["entityType"], "PopulatedPlace")
            self.assertEqual(bing.place["matchCodes"], ["Ambiguous"])

        with self.subTest("Geocode Bing Parsed"):
            self.assertEqual(bing.broker.place.street_line1, None)
            self.assertEqual(bing.broker.place.street_line2, None)
            self.assertEqual(bing.broker.place.city, "Ixonia")
            self.assertEqual(bing.broker.place.state, "WI")
            self.assertEqual(bing.broker.place.county, "Jefferson County")
            self.assertEqual(bing.broker.place.country, "US")
            self.assertEqual(bing.broker.place.zipcode, None)
            self.assertEqual(bing.broker.place.neighborhood, None)
            self.assertEqual(bing.broker.place.intersection, None)
            self.assertEqual(bing.broker.place.latitude, 43.14390182)
            self.assertEqual(bing.broker.place.longitude, -88.59204102)
            self.assertEqual(bing.broker.place.formatted_address, "Ixonia, Jefferson County WI")
            self.assertEqual(bing.broker.place.entity_type, "city")
            self.assertEqual(bing.broker.place.is_confirmed, True)
            self.assertEqual(bing.broker.place.search_string, "ixonia, Jefferson WI")
            self.assertEqual(bing.broker.place.url_sent, None)
            self.assertEqual(bing.broker.place.geocoder_engine_name, "Bing")
            self.assertEqual(bing.broker.place.correlation_distance_km, 0.1)

        google = obj.responses.get(engine="Google")
        with self.subTest("Geocode Google Raw data"):
            self.assertEqual(google.engine, "Google")
            self.assertEqual(google.place["formatted_address"], "Ixonia, WI 53036, USA")
            self.assertEqual(google.place["types"], ["locality", "political"])

        with self.subTest("Geocode Google Parsed"):
            self.assertEqual(google.broker.place.street_line1, None)
            self.assertEqual(google.broker.place.street_line2, None)
            self.assertEqual(google.broker.place.city, "Ixonia")
            self.assertEqual(google.broker.place.state, "WI")
            self.assertEqual(google.broker.place.county, "Jefferson County")
            self.assertEqual(google.broker.place.country, "US")
            self.assertEqual(google.broker.place.zipcode, "53036")
            self.assertEqual(google.broker.place.neighborhood, None)
            self.assertEqual(google.broker.place.intersection, None)
            self.assertEqual(google.broker.place.latitude, 43.1438923)
            self.assertEqual(google.broker.place.longitude, -88.59732300000002)
            self.assertEqual(google.broker.place.formatted_address, "Ixonia, Jefferson County WI")
            self.assertEqual(google.broker.place.entity_type, "city")
            self.assertEqual(google.broker.place.is_confirmed, True)
            self.assertEqual(google.broker.place.search_string, "ixonia, Jefferson WI")
            self.assertEqual(google.broker.place.url_sent, None)
            self.assertEqual(google.broker.place.geocoder_engine_name, "Google")
            self.assertEqual(google.broker.place.correlation_distance_km, 0.1)
            self.assertEqual(google.broker.place.suite, None)
            self.assertEqual(google.broker.place.street_number, None)
            self.assertEqual(google.broker.place.route, None)

    def test_matches_Non_US(self):
        """Santiago de los caballeros, Dominican Republic is a new city that isn't in our db."""

        city = "Santiago de los caballeros"
        country = resolve_country("DO")  #  Dominican Republic

        self.assertFalse(City.objects.filter(name=city).exists())
        self.assertTrue(Country.objects.filter(abbr=country).exists())

        input_data = {"name": city, "country": country.abbr}

        serializer = GeocodeCityMatchesSerializer(data=input_data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        obj, create = serializer.save()

        with self.subTest("Geocode City Data"):
            self.assertEqual(
                obj.raw_address,
                f"{city}, {country}",
            )
            self.assertEqual(obj.entity_type, "city")
            self.assertEqual(obj.raw_country, country)
            self.assertEqual(obj.immediate, True)
            self.assertEqual(obj.raw_street_line1, "")
            self.assertEqual(obj.raw_street_line2, "")
            self.assertEqual(obj.raw_zipcode, "")
            self.assertEqual(obj.raw_city, None)
            self.assertEqual(obj.raw_county, None)
            self.assertEqual(obj.raw_state, None)
            self.assertEqual(obj.raw_cross_roads, "")

            self.assertEqual(County.objects.count(), 0)
            self.assertFalse(City.objects.filter(name="city").exists())

        bing = obj.responses.get(engine="Bing")
        with self.subTest("Geocode Bing Raw data"):
            self.assertEqual(bing.geocode.pk, obj.pk)
            self.assertEqual(bing.engine, "Bing")
            self.assertEqual(bing.place["name"], "Santiago de los Caballeros, Dominican Republic")
            self.assertEqual(bing.place["confidence"], "High")
            self.assertEqual(bing.place["entityType"], "PopulatedPlace")
            self.assertEqual(bing.place["matchCodes"], ["Good"])

        with self.subTest("Geocode Bing Parsed"):
            self.assertEqual(bing.broker.place.street_line1, None)
            self.assertEqual(bing.broker.place.street_line2, None)
            self.assertEqual(bing.broker.place.city, "Santiago de los Caballeros")
            self.assertEqual(bing.broker.place.state, None)
            self.assertEqual(bing.broker.place.county, None)
            self.assertEqual(bing.broker.place.country, "DO")
            self.assertEqual(bing.broker.place.zipcode, None)
            self.assertEqual(bing.broker.place.neighborhood, None)
            self.assertEqual(bing.broker.place.intersection, None)
            self.assertEqual(bing.broker.place.latitude, 19.45039368)
            self.assertEqual(bing.broker.place.longitude, -70.69090271)
            self.assertEqual(
                bing.broker.place.formatted_address,
                "Santiago de los Caballeros DO",
            )
            self.assertEqual(bing.broker.place.entity_type, "city")
            self.assertEqual(bing.broker.place.is_confirmed, True)
            self.assertEqual(bing.broker.place.search_string, "Santiago de los caballeros, DO")
            self.assertEqual(bing.broker.place.url_sent, None)
            self.assertEqual(bing.broker.place.geocoder_engine_name, "Bing")
            self.assertEqual(bing.broker.place.correlation_distance_km, 0.1)

        google = obj.responses.get(engine="Google")
        with self.subTest("Geocode Google Raw data"):
            self.assertEqual(google.engine, "Google")
            self.assertEqual(
                google.place["formatted_address"], "Santiago De Los Caballeros, Dominican Republic"
            )
            self.assertEqual(google.place["types"], ["locality", "political"])

        with self.subTest("Geocode Google Parsed"):
            self.assertEqual(google.broker.place.street_line1, None)
            self.assertEqual(google.broker.place.street_line2, None)
            self.assertEqual(google.broker.place.city, "Santiago De Los Caballeros")
            self.assertEqual(google.broker.place.state, None)
            self.assertEqual(google.broker.place.county, None)
            self.assertEqual(google.broker.place.country, "DO")
            self.assertEqual(google.broker.place.zipcode, None)
            self.assertEqual(google.broker.place.neighborhood, None)
            self.assertEqual(google.broker.place.intersection, None)
            self.assertEqual(google.broker.place.latitude, 19.4791963)
            self.assertEqual(google.broker.place.longitude, -70.6930568)
            self.assertEqual(
                google.broker.place.formatted_address,
                "Santiago De Los Caballeros DO",
            )
            self.assertEqual(google.broker.place.entity_type, "city")
            self.assertEqual(google.broker.place.is_confirmed, True)
            self.assertEqual(google.broker.place.search_string, "Santiago de los caballeros, DO")
            self.assertEqual(google.broker.place.url_sent, None)
            self.assertEqual(google.broker.place.geocoder_engine_name, "Google")
            self.assertEqual(google.broker.place.correlation_distance_km, 0.1)
            self.assertEqual(google.broker.place.suite, None)
            self.assertEqual(google.broker.place.street_number, None)
            self.assertEqual(google.broker.place.route, None)

    def test_matches_Non_US_GeocodeCitySerializer(self):
        """Santiago de los caballeros, Dominican Republic is a new city that isn't in our db."""
        city = "Santiago de los caballeros"
        country = resolve_country("DO")

        self.assertFalse(City.objects.filter(name=city).exists())
        input_data = {"name": city, "country": country.abbr}

        serializer = GeocodeCityMatchesSerializer(data=input_data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        obj, created = serializer.save()

        serializer = GeocodeCitySerializer(instance=obj)
        results = serializer.data

        self.assertEqual(results.get("raw_address"), "Santiago de los caballeros, DO")
        self.assertEqual(results.get("entity_type"), "city")
        self.assertIsNotNone(results.get("modified_date"))
        self.assertIsNotNone(results.get("created_date"))
        self.assertEqual(results.get("immediate"), True)
        self.assertEqual(results.get("raw_county"), None)
        self.assertEqual(results.get("raw_state"), None)
        self.assertEqual(results.get("raw_country"), country.pk)
        self.assertEqual(len(results.get("responses")), 2)
        self.assertEqual(len(results.get("valid_responses")), 1)

        # Now we are ready for a hand-off to our geographic app.
