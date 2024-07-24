__author__ = "Johnny Fang"
__date__ = "4/6/19 2:20 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Johnny Fang",
]

import logging

from django.urls import reverse

from axis.company.models import Company
from axis.company.tests.factories import builder_organization_factory
from axis.core.tests.client import AxisClient
from axis.core.tests.testcases import AxisTestCase
from axis.examine.tests.utils import MachineryDriver
from axis.geocoder.models import GeocodeResponse
from axis.geographic.tests.factories import real_city_factory
from axis.subdivision.models import Subdivision
from axis.subdivision.serializers import SubdivisionSerializer
from axis.subdivision.tests.mixins import SubdivisionViewTestMixin
from axis.subdivision.views import SubdivisionExamineMachinery

log = logging.getLogger(__name__)


class SubdivisionViewSetTests(SubdivisionViewTestMixin, AxisTestCase):
    client_class = AxisClient

    def test_validate(self):
        """Tests form is validated correctly - builder_org is populated based on filter_by_user"""

        user = self.get_admin_user(company_type="rater")
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )
        url = reverse("apiv2:subdivision-validate")
        builder_org = Company.objects.filter(company_type=Company.BUILDER_COMPANY_TYPE).first()
        response = self.client.post(url, {"builder_org": builder_org.pk, "name": builder_org.name})
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            url, {"builder_org": builder_org.pk + 1, "name": builder_org.name}
        )
        self.assertContains(response, "Select a valid choice", status_code=400)

    def test_examine_intl_create(self):
        city = real_city_factory("Bonao", country="DO")
        builder = builder_organization_factory(city=city)

        user = self.admin_user
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        driver = MachineryDriver(SubdivisionExamineMachinery, create_new=True, request_user=user)
        driver.bind(
            dict(
                name="International",
                city=city.pk,
                cross_roads="Callle La Altagracia & AV Espana",
                builder_org=builder.pk,
            ),
        )

        response = driver.submit(self.client, method="post")
        response_object = driver.get_response_object()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Subdivision.objects.filter(id=response_object["id"]).exists(), True)

    def test_display_raw_address_bug_zd41381(self):
        # We found a bug where on display raw addresses.
        user = self.admin_user
        user.company.display_raw_addresses = True
        user.company.save()
        user.refresh_from_db()

        instance = Subdivision.objects.get()

        class Fake_req:
            pass

        Fake_req.user = user

        self.assertEqual(instance.geocode_response, None)
        geo_response = GeocodeResponse.objects.first()
        instance.geocode_response = geo_response
        instance.save()

        serializer = SubdivisionSerializer(instance=instance, context={"request": Fake_req})
        data = serializer.to_representation(instance=instance)
        self.assertEqual(data["geocode_response"], geo_response.id)
