__author__ = "Steven Klass"
__date__ = "12/5/11 1:28 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

import re
import json
import logging

from django.urls import reverse

from rest_framework.test import APITestCase
from rest_framework import status

from axis.examine.tests.utils import MachineryDriver
from django.contrib.auth import get_user_model
from axis.core.tests.client import AxisClient
from axis.core.tests.testcases import AxisTestCase
from axis.company.tests.mixins import CompaniesAndUsersTestMixin
from axis.geographic.models import County, Metro, City
from .mixins import CommunityViewTestMixin
from ..models import Community
from ..views.examine import CommunityExamineMachinery
from ...geographic.tests.factories import real_city_factory

log = logging.getLogger(__name__)
User = get_user_model()


def get_create_intersection_address():
    return {
        "name": "Foobar",
        "city": City.objects.get(name="Gilbert").id,
        "cross_roads": "E Williams Field Rd & S Val Vista Dr",
    }


def get_update_intersection_address():
    return {
        "name": "BazFoo",
        "city": City.objects.get(name="Mesa").id,
        "cross_roads": "Main and Higley",
    }


class CommunityViewTests(CommunityViewTestMixin, AxisTestCase):
    """Test out community app"""

    client_class = AxisClient

    def test_login_required(self):
        community = Community.objects.first()

        url = reverse("community:view", kwargs={"pk": community.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(url, response["Location"], msg=url)
        self.assertIn(reverse("auth:login"), response["Location"])

        url = reverse("community:add")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(url, response["Location"], msg=url)
        self.assertIn(reverse("auth:login"), response["Location"])

    def test_user_has_permissions(self):
        """Test that we can login and see communities"""
        user = self.get_admin_user()
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )
        self.assertEqual(user.has_perm("community.view_community"), True)
        self.assertEqual(user.has_perm("community.change_community"), True)
        self.assertEqual(user.has_perm("community.add_community"), True)
        self.assertEqual(user.has_perm("community.delete_community"), True)

        community = Community.objects.filter_by_user(user).first()

        url = reverse("community:list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        url = reverse("community:view", kwargs={"pk": community.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        url = reverse("community:add")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_examine_create(self):
        user = self.admin_user
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        driver = MachineryDriver(CommunityExamineMachinery, create_new=True)
        driver.bind(get_create_intersection_address())

        response = driver.submit(self.client, method="post")
        response_object = driver.get_response_object()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Community.objects.filter(id=response_object["id"]).exists(), True)

    def test_examine_update(self):
        user = self.admin_user
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        driver = MachineryDriver(CommunityExamineMachinery, instance=Community.objects.all()[0])
        driver.set_ignore_fields(
            "modified_date",
            "city_name",
            "metro_name",
            "geocoded_address",
            "cross_roads_display",
            "city_display",
        )
        driver.bind(get_update_intersection_address())

        client_object = driver.get_client_object()

        response = driver.submit(self.client, method="patch")
        response_object = driver.get_response_object()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(client_object, response_object)

    def test_examine_intl_create(self):
        user = self.admin_user
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        driver = MachineryDriver(CommunityExamineMachinery, create_new=True)

        driver.bind(
            dict(
                name="International",
                city=real_city_factory("Bonao", country="DO").pk,
                cross_roads="Callle La Altagracia & AV Espana",
            ),
        )

        response = driver.submit(self.client, method="post")
        response_object = driver.get_response_object()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Community.objects.filter(id=response_object["id"]).exists(), True)


class ApiTests(CompaniesAndUsersTestMixin, APITestCase):
    include_company_types = ["rater", "provider"]
    include_unrelated_companies = False

    def setUp(self):
        user = User.objects.filter(
            company__company_type__in=["rater", "provider"], is_company_admin=True
        ).first()
        self.assertIsNotNone(user.company)
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        self.create_data = {
            "website": "http://maps.google.com/",
            "city": City.objects.first().pk,
            "cross_roads": "E Williams Field Rd & S Val Vista Dr",
            "name": "Community A",
            "metro": Metro.objects.first().pk,
            "confirmed_address": True,
            "is_active": False,
            "longitude": -111.755679,
            "county": County.objects.first().pk,
            "modified_date": "2012-12-30T19:33:57",
            "state": "AZ",
            "created_date": "2012-11-27T19:55:43",
            "latitude": 33.3066625,
            "slug": "community-a-gilbert-az",
        }

    def test_list(self):
        response = self.client.get(reverse("apiv2:community-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create(self):
        response = self.client.post(reverse("apiv2:community-list"), data=self.create_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_detail(self):
        self.test_create()
        obj = Community.objects.last()
        response = self.client.get(reverse("apiv2:community-detail", kwargs={"pk": obj.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update(self):
        self.test_create()
        obj = Community.objects.last()
        response = self.client.put(
            reverse("apiv2:community-detail", kwargs={"pk": obj.pk}), data=self.create_data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete(self):
        self.test_create()
        obj = Community.objects.last()
        response = self.client.delete(reverse("apiv2:community-detail", kwargs={"pk": obj.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
