"""test_api.py: Django geographic"""


import json
import logging
import time

from django.urls import reverse

from axis.core.tests.client import AxisClient
from axis.core.tests.factories import builder_admin_factory
from axis.core.tests.testcases import AxisTestCase
from axis.geocoder.models import Geocode, GeocodeResponse
from axis.geographic.tests.factories import real_city_factory
from axis.home.models import Home
from axis.home.views.machineries import HomeExamineMachinery

__author__ = "Steven Klass"
__date__ = "5/15/13 10:56 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

from axis.scheduling.models import ConstructionStage

log = logging.getLogger(__name__)


class HomeApiUniquenessTests(AxisTestCase):
    """
    Test that homes created through the api go through the
    same scrutiny to make sure we don't create duplicate addresses.
    """

    client_class = AxisClient

    @classmethod
    def setUpTestData(cls):
        cls.city = real_city_factory("Gilbert", "AZ")
        ConstructionStage.objects.create(name="Starting", is_public=True, order=1)
        builder_admin_factory(username="builder_1", company__city=cls.city)

    def setUp(self):
        self.geocode_api_endpoint = "/api/v2/geocode/matches/"

        self.county = self.city.county
        self.builder = self.get_admin_user("builder")
        self.builder_company = self.builder.company

        self.base_kwargs = {
            "city": self.city.pk,
            "county": self.county.pk,
            "builder": self.builder_company.pk,
            "user": self.builder.pk,
            "lot_number": "lot",
            "street_line1": "291 S Park Grove Ln",
            "street_line2": "",
            "is_multi_family": False,
            "zipcode": "85296",
            "state": "AZ",
        }

        self.assertEqual(Geocode.objects.count(), 0)
        self.assertEqual(GeocodeResponse.objects.count(), 0)

    def _confirmed_gecode_response(self):
        return

    def _verify_confirmed(self, home, city_is_id=True, **kwargs):
        city = kwargs.get("city")
        if city_is_id:
            from axis.geographic.models import City

            city = City.objects.get(id=kwargs.get("city"))

        self.assertEqual(home.lot_number, kwargs.get("lot_number"))
        self.assertEqual(home.street_line1, kwargs.get("street_line1"))
        self.assertEqual(home.street_line2, kwargs.get("street_line2", None))
        self.assertEqual(home.city, city)
        self.assertEqual(home.state, kwargs.get("state"))
        self.assertEqual(home.zipcode, kwargs.get("zipcode"))
        self.assertEqual(home.county, city.county)
        self.assertEqual(home.bulk_uploaded, kwargs.get("bulk_uploaded", False))
        self.assertAlmostEqual(home.longitude, -111.7737, 3)
        self.assertAlmostEqual(home.latitude, 33.3445, 3)
        self.assertIsNotNone(home.climate_zone)
        self.assertEqual(home.climate_zone, city.county.climate_zone)
        self.assertIsNotNone(home.metro)
        self.assertEqual(home.metro, city.county.metro)
        self.assertEqual(home.confirmed_address, True)
        self.assertEqual(home.is_multi_family, kwargs.get("is_multi_family", False))
        self.assertEqual(home.address_override, False)
        self.assertIsNotNone(home.place)
        self.assertIsNotNone(home.geocode_response)

    def _verify_unconfirmed(self, home, city_is_id=True, **kwargs):
        city = kwargs.get("city")
        if city_is_id:
            from axis.geographic.models import City

            city = City.objects.get(id=kwargs.get("city"))

        self.assertEqual(home.lot_number, kwargs.get("lot_number"))
        self.assertEqual(home.street_line1, kwargs.get("street_line1"))
        self.assertEqual(home.street_line2, kwargs.get("street_line2", None))
        self.assertEqual(home.city, city)
        self.assertEqual(home.state, kwargs.get("state"))
        self.assertEqual(home.zipcode, kwargs.get("zipcode"))
        self.assertEqual(home.county, city.county)
        self.assertEqual(home.alt_name, kwargs.get("alt_name"))
        self.assertEqual(home.bulk_uploaded, kwargs.get("bulk_uploaded", False))
        self.assertIsNone(home.longitude)
        self.assertIsNone(home.latitude)
        self.assertIsNotNone(home.climate_zone)
        self.assertEqual(home.climate_zone, city.county.climate_zone)
        self.assertIsNotNone(home.metro)
        self.assertEqual(home.metro, city.county.metro)
        self.assertEqual(home.confirmed_address, False)
        self.assertEqual(home.is_multi_family, kwargs.get("is_multi_family", False))
        self.assertEqual(home.address_override, False)
        self.assertIsNotNone(home.place)
        self.assertIsNone(home.geocode_response)

    def get_url(self, machinery):
        return reverse("apiv2:home-list") + machinery(create_new=True).parameterize_context()

    def test_unconfirmed_add(self):
        self.assertEqual(Geocode.objects.count(), 0)
        self.assertEqual(GeocodeResponse.objects.count(), 0)
        self.assertEqual(Home.objects.count(), 0)

        self.assertEqual(
            self.client.login(username=self.builder.username, password="password"), True
        )
        url = self.get_url(HomeExamineMachinery)
        response = self.client.post(url, data=self.base_kwargs)
        self.assertEqual(response.status_code, 201)

        self.assertEqual(Home.objects.count(), 1)
        self._verify_unconfirmed(Home.objects.get(), **self.base_kwargs)
        self.assertEqual(Geocode.objects.count(), 1)
        self.assertEqual(GeocodeResponse.objects.count(), 2)

    def test_confirmed_add(self):
        self.assertEqual(Geocode.objects.count(), 0)
        self.assertEqual(GeocodeResponse.objects.count(), 0)
        self.assertEqual(Home.objects.count(), 0)

        self.assertEqual(
            self.client.login(username=self.builder.username, password="password"), True
        )
        response = self.client.get(self.geocode_api_endpoint, data=self.base_kwargs)
        self.assertEqual(response.status_code, 200)

        geocode_response = json.loads(response.content)
        self.assertEqual(len(geocode_response["matches"]), 1)

        url = self.get_url(HomeExamineMachinery)

        kwargs = self.base_kwargs.copy()
        kwargs["geocode_response"] = geocode_response["matches"][0]["response"]
        response = self.client.post(url, data=kwargs)
        self.assertEqual(response.status_code, 201, response.content)

        self.assertEqual(Home.objects.count(), 1)
        self._verify_confirmed(Home.objects.get(), **kwargs)
        self.assertEqual(Geocode.objects.count(), 1)
        self.assertEqual(GeocodeResponse.objects.count(), 2)

    def _create_confirmed_home(self):
        from axis.geographic.models import City
        from axis.geocoder.models import GeocodeResponse

        response = self.client.get(self.geocode_api_endpoint, data=self.base_kwargs)
        self.assertEqual(response.status_code, 200)
        geocode_response = json.loads(response.content)
        self.assertEqual(len(geocode_response["matches"]), 1)

        kwargs = self.base_kwargs.copy()
        kwargs["geocode_response"] = GeocodeResponse.objects.get(
            id=geocode_response["matches"][0]["response"]
        )
        kwargs["city"] = City.objects.get(id=kwargs.get("city"))
        kwargs["county"] = kwargs["city"].county

        del kwargs["builder"]
        del kwargs["user"]

        home = Home.objects.create(**kwargs)
        self.assertEqual(Home.objects.count(), 1)
        self._verify_confirmed(Home.objects.get(), city_is_id=False, **kwargs)
        return home

    def _create_unconfirmed_home(self):
        from axis.geographic.models import City

        kwargs = self.base_kwargs.copy()
        kwargs["city"] = City.objects.get(id=kwargs.get("city"))
        kwargs["county"] = kwargs["city"].county

        del kwargs["builder"]
        del kwargs["user"]

        home = Home.objects.create(**kwargs)
        self.assertEqual(Home.objects.count(), 1)
        self._verify_unconfirmed(Home.objects.get(), city_is_id=False, **kwargs)
        return home

    def test_verify_confirmed_back_to_back(self):
        self.assertEqual(
            self.client.login(username=self.builder.username, password="password"), True
        )
        home = self._create_confirmed_home()

        time.sleep(1)  # sleep ensures that we relook up the address (for this we shouldn't anyway)

        url = self.get_url(HomeExamineMachinery)

        kwargs = self.base_kwargs.copy()
        kwargs["geocode_response"] = home.geocode_response.id
        response = self.client.post(url, data=kwargs)
        self.assertEqual(response.status_code, 400)

        response_data = json.loads(response.content)
        self.assertEqual(Home.objects.count(), 1)
        self.assertIn("already exists in Axis", response_data.get("non_field_errors", [""])[0])
        self._verify_confirmed(Home.objects.get(), **kwargs)
        self.assertEqual(Geocode.objects.count(), 1)
        self.assertEqual(GeocodeResponse.objects.count(), 2)

    def test_verify_unconfirmed_back_to_back(self):
        self.assertEqual(
            self.client.login(username=self.builder.username, password="password"), True
        )
        home = self._create_unconfirmed_home()

        time.sleep(1)  # sleep ensures that we relook up the address (for this we shouldn't anyway)

        url = self.get_url(HomeExamineMachinery)

        response = self.client.post(url, data=self.base_kwargs)
        self.assertEqual(response.status_code, 400)

        response_data = json.loads(response.content)
        self.assertEqual(Home.objects.count(), 1)
        self.assertEqual(
            "already exists in Axis" in response_data.get("non_field_errors", [""])[0],
            True,
        )
        self._verify_unconfirmed(Home.objects.get(), **self.base_kwargs)

        # Now keep in mind these are 0 because we have never geocoded anything
        # (which is not normal - when the user hits save it automatically attempts a geocode.)
        self.assertEqual(Geocode.objects.count(), 0)
        self.assertEqual(GeocodeResponse.objects.count(), 0)

    def test_verify_unconfirmed_to_confirmed(self):
        self.assertEqual(
            self.client.login(username=self.builder.username, password="password"), True
        )
        home = self._create_unconfirmed_home()
        self.assertEqual(Home.objects.count(), 1)

        time.sleep(1)  # sleep ensures that we relook up the address (for this we shouldn't anyway)

        url = self.get_url(HomeExamineMachinery)

        response = self.client.get(self.geocode_api_endpoint, data=self.base_kwargs)
        self.assertEqual(response.status_code, 200)
        geocode_response = json.loads(response.content)
        self.assertEqual(len(geocode_response["matches"]), 1)

        kwargs = self.base_kwargs.copy()
        kwargs["geocode_response"] = geocode_response["matches"][0]["response"]

        response = self.client.post(url, data=kwargs)
        self.assertEqual(response.status_code, 400)

        response_data = json.loads(response.content)

        self.assertEqual(Home.objects.count(), 1)
        self.assertIn("already exists in Axis", response_data.get("non_field_errors", [""])[0])
        # Nothing should have happened..
        self._verify_unconfirmed(Home.objects.get(), **kwargs)
        self.assertEqual(Geocode.objects.count(), 1)
        self.assertEqual(GeocodeResponse.objects.count(), 2)

    def test_verify_confirmed_to_unconfirmed(self):
        self.assertEqual(
            self.client.login(username=self.builder.username, password="password"), True
        )
        home = self._create_confirmed_home()

        time.sleep(1)  # sleep ensures that we relook up the address (for this we shouldn't anyway)

        url = self.get_url(HomeExamineMachinery)

        response = self.client.post(url, data=self.base_kwargs)
        self.assertEqual(response.status_code, 400)

        response_data = json.loads(response.content)
        self.assertEqual(Home.objects.count(), 1)
        self.assertIn("already exists in Axis", response_data.get("non_field_errors", [""])[0])
        self._verify_confirmed(Home.objects.get(), **self.base_kwargs)
        self.assertEqual(Geocode.objects.count(), 1)
        self.assertEqual(GeocodeResponse.objects.count(), 2)
