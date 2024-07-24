"""tests.py: Django geocoder"""

import logging
import time

from django.test import TestCase

from ..engines import GEOCODER_ENGINES
from ..models import Geocode, GeocodeResponse

__author__ = "Peter Landry"
__date__ = "12/4/13 5:47 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = ["Peter Landry", "Steven Klass"]

log = logging.getLogger(__name__)


class GeocoderTests(TestCase):
    def test_simple_model(self):
        self.assertEqual(Geocode.objects.count(), 0)
        g = Geocode.objects.create(raw_address="479 Washington St, Providence, RI, 34342")
        self.assertEqual(Geocode.objects.count(), 1)
        self.assertIsNotNone(g.created_date)
        self.assertIsNotNone(g.modified_date)

    def test_geocoderesponse_json(self):
        """Test that geocoding engine result JSON is stored in the ``GeocodeResponse`.place`
        object."""
        g = Geocode.objects.create(raw_address="479 Washington St, Providence, RI, 34342")
        self.assertEqual(g.responses.count(), 2)
        for response in g.responses.all():
            # Here we just want to verify that we have a response
            self.assertIsNotNone(response.place)
            self.assertTrue(isinstance(response.place, dict))


class GeocoderPlaceTests(TestCase):
    def setUp(self):
        from axis.geographic.tests.factories import real_city_factory

        self.city = real_city_factory(name="Gilbert", state="AZ")
        self.base_address = {
            "street_line1": "2548 South Loren Lane",
            "city": self.city,
            "state": self.city.county.state,
            "zipcode": "85250",
        }
        self.bad_address = self.base_address.copy()
        self.bad_address.update({"street_line1": "nowhere ln", "zipcode": "54829"})

    def set_unconfirmed_geocode_responses(self, responses):
        for response in responses.all():
            if response.engine == "Google":
                GeocodeResponse.objects.filter(id=response.id).update(
                    place=response.place | {"types": ["NON_ENTITY"]}
                )
            elif response.engine == "Bing":
                GeocodeResponse.objects.filter(id=response.id).update(
                    place=response.place | {"confidence": "LOW"}
                )

    def test_get_matches(self):
        """This simply verifies the basics of get matches works"""
        self.assertEqual(Geocode.objects.count(), 0)
        self.assertEqual(GeocodeResponse.objects.count(), 0)

        matches = Geocode.objects.get_matches(**self.base_address)
        self.assertEqual(len(matches), 1)
        self.assertEqual(Geocode.objects.count(), 1)

        g = Geocode.objects.all().get()
        self.assertIsNotNone(g.created_date)
        self.assertIsNotNone(g.modified_date)

        self.assertEqual(GeocodeResponse.objects.count(), len(GEOCODER_ENGINES.keys()))

        for response in g.responses.all():
            self.assertEqual(response.geocode.id, g.id)
            self.assertIsNotNone(response.engine)
            self.assertIsNotNone(response.place)
            self.assertIsNotNone(response.created_date)
            self.assertEqual(response.broker.place.is_confirmed, True)

    def test_get_matches_unconfirmed(self):
        """This will verify that we don't get anything back on unconfirmed homes"""
        self.assertEqual(Geocode.objects.count(), 0)
        self.assertEqual(GeocodeResponse.objects.count(), 0)

        matches = Geocode.objects.get_matches(**self.bad_address)
        self.assertEqual(len(matches), 0)
        self.assertEqual(Geocode.objects.count(), 1)

        g = Geocode.objects.all().get()
        self.assertIsNotNone(g.created_date)
        self.assertIsNotNone(g.modified_date)

        self.assertEqual(GeocodeResponse.objects.count(), len(GEOCODER_ENGINES.keys()))

        for response in g.responses.all():
            self.assertEqual(response.geocode.id, g.id)
            self.assertIsNotNone(response.engine)
            self.assertIsNotNone(response.place)
            self.assertIsNotNone(response.created_date)
            self.assertEqual(response.broker.place.is_confirmed, False)

    def test_get_unconfirmed_to_confirmed_matches(self):
        """This will verify that we can re-geocode and get an address until we get a
        valid response and stop"""
        self.assertEqual(GeocodeResponse.objects.count(), 0)
        Geocode.objects.get_matches(**self.base_address)
        self.set_unconfirmed_geocode_responses(GeocodeResponse.objects.all())

        matches = Geocode.objects.get_matches(**self.base_address)
        self.assertEqual(len(matches), 0)

        time.sleep(1)

        # Now get a valid response
        matches = Geocode.objects.get_matches(**self.base_address)

        self.assertEqual(len(matches), 1)
        self.assertEqual(Geocode.objects.count(), 1)
        self.assertEqual(GeocodeResponse.objects.count(), 4)

        time.sleep(1)

        # Now try a third time and simply hold this because it's confirmed.
        matches = Geocode.objects.get_matches(**self.base_address)

        self.assertEqual(len(matches), 1)
        self.assertEqual(Geocode.objects.count(), 1)
        self.assertEqual(GeocodeResponse.objects.count(), 4)

    def test_back_to_back_regeocode_denied(self):
        """This ensures that you cannot simply hit this thing over and over.  Our timeout is
        short but exists"""

        Geocode.objects.get_matches(**self.base_address)
        self.set_unconfirmed_geocode_responses(GeocodeResponse.objects.all())

        matches = Geocode.objects.get_matches(**self.base_address)
        self.assertEqual(len(matches), 0)

        matches = Geocode.objects.get_matches(**self.base_address)
        self.assertEqual(len(matches), 0)

        matches = Geocode.objects.get_matches(**self.base_address)
        self.assertEqual(len(matches), 0)

        self.assertEqual(Geocode.objects.count(), 1)
        self.assertEqual(GeocodeResponse.objects.count(), 2)

    def test_get_google_normalized_fields(self):
        """Verify we get our noramlized data back out of Google"""
        self.assertEqual(Geocode.objects.count(), 0)
        self.assertEqual(GeocodeResponse.objects.count(), 0)

        matches = Geocode.objects.get_matches(**self.base_address)
        self.assertEqual(Geocode.objects.count(), 1)
        self.assertEqual(GeocodeResponse.objects.count(), 2)

        gr = GeocodeResponse.objects.get(engine="Google")
        data = gr.get_normalized_fields()

        # for k, v in data.items():
        #     print(f"self.assertEqual(data['{k}'], {v!r})")

        self.assertAlmostEqual(data["latitude"], 33.3037, 3)
        self.assertAlmostEqual(data["longitude"], -111.7876, 3)
        self.assertEqual(data["street_line1"], "2548 S Loren Ln")
        self.assertEqual(data["zipcode"], "85295")
        self.assertEqual(data["state"], "AZ")
        self.assertEqual(data["country"].abbr, "US")
        self.assertEqual(data["county"], self.base_address.get("city").county)
        self.assertEqual(data["city"], self.base_address.get("city"))
        self.assertEqual(data["confirmed_address"], True)

    def test_get_bing_normalized_fields(self):
        """Verify we get our noramlized data back out of Bing"""
        self.assertEqual(Geocode.objects.count(), 0)
        primary_match = Geocode.objects.get_matches(**self.base_address).get()
        GeocodeResponse.objects.exclude(id=primary_match.id).get()
        data = GeocodeResponse.objects.get(engine="Bing").get_normalized_fields()

        # for k, v in data.items():
        #     print(f"self.assertEqual(data['{k}'], {v!r})")

        self.assertAlmostEqual(data["latitude"], 33.3037, 3)
        self.assertAlmostEqual(data["longitude"], -111.7876, 3)
        self.assertEqual(data["street_line1"], "2548 S Loren Ln")
        self.assertEqual(data["zipcode"], "85295")
        self.assertEqual(data["state"], "AZ")
        self.assertEqual(data["country"], self.base_address.get("city").country)
        self.assertEqual(data["county"], self.base_address.get("city").county)
        self.assertEqual(data["city"], self.base_address.get("city"))
        self.assertEqual(data["confirmed_address"], True)

    def test_addr_street_line2(self):
        self.assertEqual(Geocode.objects.count(), 0)
        self.assertEqual(GeocodeResponse.objects.count(), 0)

        addresss = self.base_address | {"street_line2": "#2"}
        Geocode.objects.get_matches(**addresss)

        data = GeocodeResponse.objects.get(engine="Google").get_normalized_fields()
        self.assertEqual(data["street_line1"], "2548 S Loren Ln")
        self.assertEqual(data["street_line2"], "2")
