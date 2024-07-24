"""home.py - Axis"""

__author__ = "Steven K"
__date__ = "10/28/21 15:58"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
import time

from axis.core.tests.client import AxisClient
from axis.core.tests.factories import builder_admin_factory
from axis.core.tests.testcases import AxisTestCase
from axis.geocoder.engines import GEOCODER_ENGINES
from axis.geocoder.models import Geocode, GeocodeResponse
from axis.geographic.tests.factories import real_city_factory
from axis.home.models import Home
from axis.scheduling.models import ConstructionStage

log = logging.getLogger(__name__)


class HomeModelVerifyOrCreateTests(AxisTestCase):
    """Test out homes app"""

    client_class = AxisClient

    @classmethod
    def setUpTestData(cls):
        cls.city = real_city_factory("Gilbert", "AZ")
        cls.county = cls.city.county
        ConstructionStage.objects.create(name="Starting", is_public=True, order=1)
        cls.builder = builder_admin_factory(username="builder_1", company__city=cls.city)
        cls.builder_company = cls.builder.company

        cls.home_kwargs = {
            "city": cls.city,
            "street_line1": "291 S Park Grove Ln",
            "zipcode": "85296",
            "state": "AZ",
        }
        cls.base_kwargs = cls.home_kwargs.copy()
        cls.base_kwargs.update(
            {
                "lot_number": "110",
                "county": cls.county,
                "builder": cls.builder_company,
                "user": cls.builder,
            }
        )

    def test_find_similar(self):
        """Test out the functionaity of find_similar"""
        home = Home.objects.create(street_line2=None, geocode_response=None, **self.home_kwargs)
        similar = Home.objects.filter_similar(
            street_line2=None, geocode_response=None, **self.home_kwargs
        )
        self.assertEqual(similar.count(), 1)
        self.assertEqual(similar.get(), home)
        kwargs = self.home_kwargs.copy()
        kwargs.update({"street_line1": "291 S PARK GROVE LN"})
        similar = Home.objects.filter_similar(street_line2="", geocode_response=None, **kwargs)
        self.assertEqual(similar.count(), 1)
        self.assertEqual(similar.get(), home)
        kwargs.update({"street_line1": "291 S PARK GROVE RD"})
        similar = Home.objects.filter_similar(street_line2=None, geocode_response=None, **kwargs)
        self.assertEqual(similar.count(), 0)

        self.assertEqual(
            Home.objects.filter_similar(
                lot_number=home.lot_number,
                street_line1=home.street_line1,
                street_line2=home.street_line2,
                city=home.city,
                zipcode=home.zipcode,
            ).count(),
            1,
        )
        self.assertEqual(
            Home.objects.filter_similar(
                lot_number="111",
                street_line1=home.street_line1,
                street_line2=home.street_line2,
                city=home.city,
                zipcode=home.zipcode,
            ).count(),
            0,
        )

    def test_idempotency(self):
        """Verify that we will get"""
        home_1, create = Home.objects.verify_and_create_for_user(**self.base_kwargs)
        self.assertTrue(create)

        home_2_kwargs = self.base_kwargs.copy()
        home_2_kwargs["lot_number"] = "111"
        home_2, create = Home.objects.verify_and_create_for_user(**home_2_kwargs)
        self.assertTrue(create)
        self.assertEqual(Home.objects.count(), 2)

        # Verify that we find our existing home
        home_3, create = Home.objects.verify_and_create_for_user(create=False, **self.base_kwargs)
        self.assertIsNone(home_3)
        self.assertFalse(create)

        # Verify that we don't create a home
        home_3, create = Home.objects.verify_and_create_for_user(**self.base_kwargs)
        self.assertIsNone(home_3)
        self.assertFalse(create)

        # Verify that we find our existing home
        home_4, create = Home.objects.verify_and_create_for_user(create=False, **home_2_kwargs)
        self.assertIsNone(home_4)
        self.assertFalse(create)

        # Verify that we don't create a home
        home_4, create = Home.objects.verify_and_create_for_user(**home_2_kwargs)
        self.assertIsNone(home_4)
        self.assertFalse(create)

        self.assertEqual(Home.objects.first().lot_number, "110")
        self.assertEqual(Home.objects.last().lot_number, "111")
        self.assertEqual(Home.objects.count(), 2)

    def test_find_similar_street_line2(self):
        """Test out the functionaity of find_similar"""
        home = Home.objects.create(street_line2="#A", geocode_response=None, **self.home_kwargs)
        similar = Home.objects.filter_similar(
            street_line2="#A", geocode_response=None, **self.home_kwargs
        )
        self.assertEqual(similar.count(), 1)
        self.assertEqual(similar.get(), home)
        similar = Home.objects.filter_similar(
            street_line2="#a", geocode_response=None, **self.home_kwargs
        )
        self.assertEqual(similar.count(), 1)

    def test_find_similar_geocode_response(self):
        """
        Test out the functionaity of find_similar.
        This one will ensure the geocoded answer comes back
        different (but still statistically likely) and then we need to find that
        """

        home, create = Home.objects.verify_and_create_for_user(create=True, **self.base_kwargs)
        self.assertNotEqual(self.base_kwargs.get("street_line1").lower(), "123 street line".lower())
        self.assertEqual(home.street_line1, "291 S Park Grove Ln")

        similar = Home.objects.filter_similar(
            street_line2=None, geocode_response=home.geocode_response, **self.home_kwargs
        )
        self.assertEqual(similar.count(), 1)
        self.assertEqual(similar.get(), home)

        self.assertEqual(
            Home.objects.filter_similar(
                lot_number=home.lot_number,
                street_line1=home.street_line1,
                street_line2=home.street_line2,
                city=home.city,
                zipcode=home.zipcode,
            ).count(),
            1,
        )
        # Here we find one with the same lot number tied to it.
        self.assertEqual(
            Home.objects.filter_similar(
                lot_number="111",
                street_line1=home.street_line1,
                street_line2=home.street_line2,
                city=home.city,
                zipcode=home.zipcode,
                geocode_response=home.geocode_response,
            ).count(),
            0,
        )

    def _setup_intl(self):
        self.intl_city = real_city_factory("Tamboril", country="DO")
        self.intl_home_kwargs = {
            "city": self.intl_city,
            "street_line1": "Autop. Juan Pablo Duarte KM. 28",
            "zipcode": "51000",
        }
        self.intl_base_kwargs = self.intl_home_kwargs.copy()
        self.intl_base_kwargs.update(
            {
                "lot_number": "lot",
                "builder": self.builder_company,
                "user": self.builder,
            }
        )

    def test_find_similar_international(self):
        self._setup_intl()
        home = Home.objects.create(**self.intl_home_kwargs)
        with self.subTest("Basic (No street_line2 and no geocode_response)"):
            self.assertEqual(
                Home.objects.filter_similar(
                    street_line2=None, geocode_response=None, **self.intl_home_kwargs
                ).get(),
                home,
            )
            self.assertEqual(
                Home.objects.filter_similar(
                    street_line2="", geocode_response=None, **self.intl_home_kwargs
                ).get(),
                home,
            )
            self.assertEqual(
                Home.objects.filter_similar(
                    street_line2="A", geocode_response=None, **self.intl_home_kwargs
                ).count(),
                0,
            )

        Home.objects.filter(id=home.id).update(street_line2="#2")
        with self.subTest("Street Line 2 no geocode_response)"):
            self.assertEqual(
                Home.objects.filter_similar(
                    street_line2="#2", geocode_response=None, **self.intl_home_kwargs
                ).get(),
                home,
            )
            self.assertEqual(
                Home.objects.filter_similar(
                    street_line2="", geocode_response=None, **self.intl_home_kwargs
                ).count(),
                0,
            )

        # Now set off the geocoded responses
        from axis.geocoder.api_v3.serializers import GeocodeMatchesSerializer

        data = self.intl_home_kwargs.copy()
        data.update(dict(city=self.intl_home_kwargs["city"].id))
        serializer = GeocodeMatchesSerializer(data=data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        geocode, _created = serializer.save()
        Home.objects.filter(id=home.id).update(
            street_line1="FOO BAR", street_line2=None, geocode_response=geocode.responses.first()
        )

        with self.subTest("Looking at Bound Geocode Response"):
            self.assertEqual(
                Home.objects.filter_similar(
                    street_line2=None, geocode_response=None, **self.intl_home_kwargs
                ).get(),
                home,
            )
            self.assertEqual(
                Home.objects.filter_similar(
                    street_line2="",
                    geocode_response=geocode.responses.first(),
                    **self.intl_home_kwargs,
                ).get(),
                home,
            )

        Home.objects.filter(id=home.id).update(
            street_line1=self.intl_home_kwargs["street_line1"],
            street_line2=None,
            geocode_response=None,
        )
        with self.subTest("Looking at UnBound Geocode Response"):
            self.assertEqual(
                Home.objects.filter_similar(
                    geocode_response=geocode.responses.first(),
                    **self.intl_home_kwargs,
                ).get(),
                home,
            )

    def test_verify_for_user_international(self):
        self._setup_intl()
        with self.subTest("Verify"):
            Home.objects.verify_for_user(**self.intl_base_kwargs)
        with self.subTest("Create"):
            home, create = Home.objects.verify_and_create_for_user(
                create=True, **self.intl_base_kwargs
            )
            self.assertTrue(create)
            self.assertEqual(Home.objects.get(), home)

    def test_basic_verify(self):
        """Test for verify_and_create_for_user()"""
        self.assertEqual(Geocode.objects.count(), 0)
        self.assertEqual(GeocodeResponse.objects.count(), 0)

        home = Home.objects.verify_for_user(**self.base_kwargs)
        self.assertIsNone(home)

        home, created = Home.objects.verify_and_create_for_user(**self.base_kwargs)
        self.assertIsNotNone(home)
        self.assertTrue(created)

        self.assertEqual(Geocode.objects.count(), 1)
        self.assertEqual(GeocodeResponse.objects.count(), len(GEOCODER_ENGINES.keys()))
        # Make sure our history came along
        self.assertEqual(home.history.count(), 1)
        self.assertEqual(home.history.get().history_user, self.builder)

    def test_basic_verify_and_create_confirmed(self):
        """Test for verify_and_create_for_user"""
        self.assertEqual(Geocode.objects.count(), 0)
        self.assertEqual(GeocodeResponse.objects.count(), 0)

        kwargs = {"alt_name": "foo", "bulk_uploaded": True}
        kwargs.update(self.base_kwargs)

        home, create = Home.objects.verify_and_create_for_user(create=True, **kwargs)
        self.assertIsNotNone(home)
        self.assertEqual(create, True)
        self._verify_confirmed(home, **kwargs)
        self.assertEqual(Geocode.objects.count(), 1)
        self.assertEqual(GeocodeResponse.objects.count(), len(GEOCODER_ENGINES.keys()))

    def _verify_confirmed(self, home, **kwargs):
        self.assertEqual(home.lot_number, kwargs.get("lot_number"))
        self.assertEqual(home.street_line1, kwargs.get("street_line1"))
        self.assertEqual(home.street_line2, kwargs.get("street_line2", None))
        self.assertEqual(home.city, kwargs.get("city"))
        self.assertEqual(home.state, kwargs.get("state"))
        self.assertEqual(home.zipcode, kwargs.get("zipcode"))
        self.assertEqual(home.county, kwargs.get("city").county)
        self.assertEqual(home.alt_name, kwargs.get("alt_name"))
        self.assertEqual(home.bulk_uploaded, kwargs.get("bulk_uploaded", False))
        self.assertAlmostEqual(home.longitude, -111.7737, 3)
        self.assertAlmostEqual(home.latitude, 33.3445, 3)
        self.assertIsNotNone(home.climate_zone)
        self.assertEqual(home.climate_zone, kwargs.get("city").county.climate_zone)
        self.assertIsNotNone(home.metro)
        self.assertEqual(home.metro, kwargs.get("city").county.metro)
        self.assertEqual(home.confirmed_address, True)
        self.assertEqual(home.is_multi_family, kwargs.get("is_multi_family", False))
        self.assertEqual(home.address_override, False)
        self.assertIsNotNone(home.place)
        self.assertIsNotNone(home.geocode_response)

    def test_basic_verify_and_create_unconfirmed(self):
        """Test for verify_and_create_for_user"""

        kwargs = {
            "alt_name": "foo",
            "bulk_uploaded": False,
        }
        kwargs.update(self.base_kwargs)
        kwargs.update({"street_line1": "Nowhere ln", "zipcode": "54829"})

        home, create = Home.objects.verify_and_create_for_user(create=True, **kwargs)
        self.assertIsNotNone(home)
        self.assertEqual(create, True)
        self._verify_unconfirmed(home, **kwargs)
        self.assertEqual(Geocode.objects.count(), 1)
        self.assertEqual(GeocodeResponse.objects.count(), len(GEOCODER_ENGINES.keys()))

    def _verify_unconfirmed(self, home, **kwargs):
        self.assertEqual(home.lot_number, kwargs.get("lot_number"))
        self.assertEqual(home.street_line1, kwargs.get("street_line1"))
        self.assertEqual(home.street_line2, kwargs.get("street_line2", None))
        self.assertEqual(home.city, kwargs.get("city"))
        self.assertEqual(home.state, kwargs.get("state"))
        self.assertEqual(home.zipcode, kwargs.get("zipcode"))
        self.assertEqual(home.county, kwargs.get("city").county)
        self.assertEqual(home.alt_name, kwargs.get("alt_name"))
        self.assertEqual(home.bulk_uploaded, kwargs.get("bulk_uploaded", False))
        self.assertIsNone(home.longitude)
        self.assertIsNone(home.latitude)
        self.assertIsNotNone(home.climate_zone)
        self.assertEqual(home.climate_zone, kwargs.get("city").county.climate_zone)
        self.assertIsNotNone(home.metro)
        self.assertEqual(home.metro, kwargs.get("city").county.metro)
        self.assertEqual(home.confirmed_address, False)
        self.assertEqual(home.is_multi_family, kwargs.get("is_multi_family", False))
        self.assertEqual(home.address_override, False)
        self.assertIsNotNone(home.place)
        self.assertIsNone(home.geocode_response)

    def test_verify_and_create_confirmed_back_to_back(self):
        """Test ensures the same input address does not create duplicate addresss"""

        home, create = Home.objects.verify_and_create_for_user(create=True, **self.base_kwargs)
        self.assertEqual(Home.objects.all().count(), 1)
        self.assertIsNotNone(home)
        self.assertEqual(create, True)

        time.sleep(1)  # sleep ensures that we relook up the address (for this we shouldn't anyway)

        home, create = Home.objects.verify_and_create_for_user(create=True, **self.base_kwargs)
        self.assertEqual(Home.objects.all().count(), 1)
        self.assertIsNotNone(home)
        self.assertEqual(create, False)

        self._verify_confirmed(home, **self.base_kwargs)
        self.assertEqual(Geocode.objects.count(), 1)
        self.assertEqual(GeocodeResponse.objects.count(), len(GEOCODER_ENGINES.keys()))

    def test_verify_and_create_unconfirmed_back_to_back(self):
        """Test ensures the same input address does not create duplicate address"""
        kwargs = self.base_kwargs.copy()
        kwargs.update({"street_line1": "Nowhere ln", "zipcode": "54829"})

        home, create = Home.objects.verify_and_create_for_user(create=True, **kwargs)
        self.assertEqual(Home.objects.all().count(), 1)
        self.assertIsNotNone(home)
        self.assertEqual(create, True)

        time.sleep(1)  # sleep ensures that we relook up the address (for this we shouldn't anyway)

        home, create = Home.objects.verify_and_create_for_user(create=True, **kwargs)

        self.assertEqual(Home.objects.all().count(), 1)
        self.assertIsNotNone(home)
        self.assertEqual(create, False)

        self._verify_unconfirmed(home, **kwargs)
        self.assertEqual(Geocode.objects.count(), 1)
        self.assertEqual(GeocodeResponse.objects.count(), len(list(GEOCODER_ENGINES.keys())))

    def test_verify_and_create_confirmed_to_unconfirmed(self):
        """Test ensures the same input address does not create duplicate addresss"""
        home, create = Home.objects.verify_and_create_for_user(create=True, **self.base_kwargs)
        self.assertEqual(Home.objects.all().count(), 1)
        self.assertIsNotNone(home)
        self.assertEqual(create, True)

        time.sleep(1)  # sleep ensures that we relook up the address (for this we shouldn't anyway)

        home, create = Home.objects.verify_and_create_for_user(create=True, **self.base_kwargs)

        self.assertEqual(Home.objects.all().count(), 1)
        self.assertIsNotNone(home)
        self.assertEqual(create, False)

        self._verify_confirmed(home, **self.base_kwargs)

        self.assertEqual(Geocode.objects.count(), 1)
        self.assertEqual(GeocodeResponse.objects.count(), len(GEOCODER_ENGINES.keys()))

    def test_create_confirmed_multi_family(self):
        """
        Verify that we don't create duplicate unconfirmed MF addressess - when MF set we ignore
        street_line2
        """

        kwargs = {"is_multi_family": True, "street_line2": "#1"}
        kwargs.update(self.base_kwargs)

        home, create = Home.objects.verify_and_create_for_user(create=True, **kwargs)
        self.assertIsNotNone(home)
        self.assertEqual(create, True)
        self._verify_confirmed(home, **kwargs)
        self.assertEqual(Geocode.objects.count(), 1)
        self.assertEqual(GeocodeResponse.objects.count(), len(GEOCODER_ENGINES.keys()))

        time.sleep(1)  # sleep ensures that we relook up the address (for this we shouldn't anyway)

        kwargs = {"is_multi_family": True, "street_line2": "#2"}
        kwargs.update(self.base_kwargs)

        home, create = Home.objects.verify_and_create_for_user(create=True, **kwargs)
        self.assertIsNotNone(home)
        self.assertEqual(create, True)
        self._verify_confirmed(home, **kwargs)

        self.assertEqual(Home.objects.all().count(), 2)

        self.assertEqual(Geocode.objects.count(), 1)
        self.assertEqual(GeocodeResponse.objects.count(), len(GEOCODER_ENGINES.keys()))

    def test_create_confirmed_multi_family_back_to_back(self):
        """
        Verify that we don't create duplicate confirmed MF addressess - when MF set we ignore
        street_line2
        """

        kwargs = {"is_multi_family": True, "street_line2": "#1"}
        kwargs.update(self.base_kwargs)

        home, create = Home.objects.verify_and_create_for_user(create=True, **kwargs)
        self.assertIsNotNone(home)
        self.assertEqual(create, True)
        self._verify_confirmed(home, **kwargs)
        self.assertEqual(Geocode.objects.count(), 1)
        self.assertEqual(GeocodeResponse.objects.count(), len(GEOCODER_ENGINES.keys()))

        time.sleep(1)  # sleep ensures that we relook up the address (for this we shouldn't anyway)

        home, create = Home.objects.verify_and_create_for_user(create=True, **kwargs)
        self.assertIsNotNone(home)
        self.assertEqual(create, False)
        self._verify_confirmed(home, **kwargs)

        self.assertEqual(Home.objects.all().count(), 1)

        self.assertEqual(Geocode.objects.count(), 1)
        self.assertEqual(GeocodeResponse.objects.count(), len(GEOCODER_ENGINES.keys()))

    def test_create_unconfirmed_multi_family(self):
        """
        Verify that we don't create duplicate unconfirmed MF addressess - when MF set we ignore
        street_line2
        """
        kwargs = {"is_multi_family": True, "street_line2": "#1"}
        kwargs.update(self.base_kwargs)
        kwargs.update({"street_line1": "Nowhere ln", "zipcode": "54829"})

        home, create = Home.objects.verify_and_create_for_user(create=True, **kwargs)
        self.assertIsNotNone(home)
        self.assertEqual(create, True)
        self._verify_unconfirmed(home, **kwargs)
        self.assertEqual(Geocode.objects.count(), 1)
        self.assertEqual(GeocodeResponse.objects.count(), len(GEOCODER_ENGINES.keys()))

        time.sleep(1)  # sleep ensures that we relook up the address (for this we shouldn't anyway)

        kwargs = {"is_multi_family": True, "street_line2": "#2"}
        kwargs.update(self.base_kwargs)
        kwargs.update({"street_line1": "Nowhere ln", "zipcode": "54829"})

        home, create = Home.objects.verify_and_create_for_user(create=True, **kwargs)
        self.assertIsNotNone(home)
        self.assertEqual(create, True)
        self._verify_unconfirmed(home, **kwargs)

        self.assertEqual(Home.objects.all().count(), 2)

        self.assertEqual(Geocode.objects.count(), 1)
        self.assertEqual(GeocodeResponse.objects.count(), len(list(GEOCODER_ENGINES.keys())))
