"""test_views.py: Django search"""


import logging
import os

from django.urls import reverse

from axis.company.tests.mixins import CompaniesAndUsersTestMixin
from axis.core.tests.client import AxisClient
from axis.core.tests.testcases import AxisTestCase

__author__ = "Artem Hruzd"
__date__ = "06/03/19 3:59 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
]

log = logging.getLogger(__name__)


class SearchViewTests(CompaniesAndUsersTestMixin, AxisTestCase):
    include_company_types = ["rater"]
    include_unrelated_companies = False
    client_class = AxisClient

    def test_login_required(self):
        url = reverse("search:search")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(url, response["Location"], msg=url)
        self.assertIn(reverse("auth:login"), response["Location"])

    def test_user_has_permissions(self):
        user = self.random_user
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        url = reverse("search:search")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
