"""home.py: """

__author__ = "Artem Hruzd"
__date__ = "01/08/2021 21:25"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.urls import reverse_lazy
from rest_framework import status

from axis.core.tests.factories import builder_admin_factory
from axis.core.tests.testcases import ApiV3Tests
from axis.geocoder.models import Geocode
from axis.geographic.tests.factories import real_city_factory
from axis.home.tests.factories import home_factory
from axis.scheduling.models import ConstructionStage


class HomeViewSetTests(ApiV3Tests):
    @classmethod
    def setUpTestData(cls):
        cls.city = real_city_factory("Gilbert", "AZ")
        ConstructionStage.objects.create(name="Starting", is_public=True, order=1)
        builder_admin_factory(username="builder_1", company__city=cls.city)

    def test_home_address_is_unique(self):
        builder = self.get_admin_user("builder")
        street_line1 = "480 Washington St"
        street_line2 = ""
        is_multi_family = False
        zipcode = "34342"
        city = real_city_factory("Providence", "RI")
        city2 = real_city_factory("Oconomowoc", "WI")

        Geocode.objects.get_matches(
            street_line1=street_line1, city=city, state=city.state, zipcode=zipcode
        )
        geocode = Geocode.objects.first()
        geocode_response = geocode.responses.first()

        home = home_factory(
            street_line1=street_line1,
            street_line2=street_line2,
            is_multi_family=is_multi_family,
            zipcode=zipcode,
            city=city,
            geocode=None,
        )

        confirmed_home = home_factory(
            street_line1=street_line1,
            street_line2=street_line2,
            is_multi_family=is_multi_family,
            zipcode=zipcode,
            city=city,
            geocode=geocode,
        )

        list_url = reverse_lazy("api_v3:homes-home-address-is-unique")
        self.client.force_authenticate(user=builder)
        # try unconfirmed existing address
        response = self.client.post(
            list_url,
            data={
                "street_line1": street_line1,
                "street_line2": street_line2,
                "is_multi_family": is_multi_family,
                "zipcode": zipcode,
                "city": city.pk,
                "geocode_response": None,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["is_unique"])
        self.assertIsNotNone(response.data["home_id"])
        # try unconfirmed non existing address
        response = self.client.post(
            list_url,
            data={
                "street_line1": "Nowhere ln",
                "street_line2": street_line2,
                "is_multi_family": is_multi_family,
                "zipcode": "54829",
                "city": self.city.pk,
                "geocode_response": None,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_unique"])
        self.assertIsNone(response.data["home_id"])

        # try confirmed existing address
        response = self.client.post(
            list_url,
            data={
                "street_line1": street_line1,
                "street_line2": street_line2,
                "is_multi_family": is_multi_family,
                "zipcode": zipcode,
                "city": city.pk,
                "geocode_response": geocode_response.pk,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["is_unique"])
        self.assertIsNotNone(response.data["home_id"])

        # try confirmed non existing address, but with existing geocode_response
        response = self.client.post(
            list_url,
            data={
                "street_line1": "Nowhere ln",
                "is_multi_family": is_multi_family,
                "zipcode": "54829",
                "city": self.city.pk,
                "geocode_response": geocode_response.pk,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["is_unique"])
        self.assertIsNotNone(response.data["home_id"])

    def test_intl_home_address_is_unique(self):
        builder = self.get_admin_user("builder")
        street_line1 = "Autop. Juan Pablo Duarte KM. 28"
        street_line2 = ""
        is_multi_family = False
        zipcode = "51000"
        city = real_city_factory("Santiago de los caballeros", country="DO")

        geocode_response = Geocode.objects.get_matches(
            street_line1=street_line1, city=city, zipcode=zipcode
        ).first()
        geocode = geocode_response.geocode

        home = home_factory(
            street_line1=street_line1,
            street_line2=street_line2,
            is_multi_family=is_multi_family,
            zipcode=zipcode,
            city=city,
            geocode=None,
        )

        confirmed_home = home_factory(
            street_line1=street_line1,
            street_line2=street_line2,
            is_multi_family=is_multi_family,
            zipcode=zipcode,
            city=city,
            geocode=geocode,
        )

        list_url = reverse_lazy("api_v3:homes-home-address-is-unique")
        self.client.force_authenticate(user=builder)
        # try unconfirmed existing address
        response = self.client.post(
            list_url,
            data={
                "street_line1": street_line1,
                "street_line2": street_line2,
                "is_multi_family": is_multi_family,
                "zipcode": zipcode,
                "city": city.pk,
                "geocode_response": None,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["is_unique"])
        self.assertIsNotNone(response.data["home_id"])
        # try unconfirmed non existing address
        response = self.client.post(
            list_url,
            data={
                "street_line1": "Nowhere ln",
                "street_line2": street_line2,
                "is_multi_family": is_multi_family,
                "zipcode": "54829",
                "city": self.city.pk,
                "geocode_response": None,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_unique"])
        self.assertIsNone(response.data["home_id"])

        # try confirmed existing address
        response = self.client.post(
            list_url,
            data={
                "street_line1": street_line1,
                "street_line2": street_line2,
                "is_multi_family": is_multi_family,
                "zipcode": zipcode,
                "city": city.pk,
                "geocode_response": geocode_response.pk,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["is_unique"])
        self.assertIsNotNone(response.data["home_id"])

        # try confirmed non existing address, but with existing geocode_response
        response = self.client.post(
            list_url,
            data={
                "street_line1": "Nowhere ln",
                "is_multi_family": is_multi_family,
                "zipcode": "54829",
                "city": self.city.pk,
                "geocode_response": geocode_response.pk,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["is_unique"])
        self.assertIsNotNone(response.data["home_id"])
