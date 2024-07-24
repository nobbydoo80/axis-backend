"""test_views.py: Django customer_earth_advantage.appraisal_addendum"""


__author__ = "Rajesh Pethe"
__date__ = "4/29/2020 9:25 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Rajesh Pethe",
]

import logging
from django.urls import reverse
from axis.core.tests.client import AxisClient
from axis.core.tests.factories import general_super_user_factory
from axis.core.tests.testcases import AxisTestCase
from axis.hes.tests.mixins import HESTestMixin
from axis.home.models import EEPProgramHomeStatus
from axis.remrate_data.tests.factories import simulation_factory as rem_simulation_factory


log = logging.getLogger(__name__)


class CustomerEarthAdvantageAppraisalAddendumViewTests(HESTestMixin, AxisTestCase):
    """Test out builder agreeement application"""

    client_class = AxisClient

    def test_login_required(self):
        """Test that we can't see companies without logging in."""
        urls = [
            reverse("earth_advantage:eaaa_addendum", kwargs={"home_status": 0}),
        ]

        LOGIN_URL = reverse("auth:login")
        redirect_format = "{url}?next={from_url}"

        for url in urls:
            response = self.client.get(url)
            self.assertRedirects(response, redirect_format.format(url=LOGIN_URL, from_url=url))

    def test_company_user_has_permissions(self):
        """Test that we can login and see Customer Appraisal"""
        user = general_super_user_factory()

        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )
        self.assertEqual(user.has_perm("home.change_home"), True)

    def test_get_green_addendum(self):
        user = general_super_user_factory()

        status = EEPProgramHomeStatus.objects.get()
        if status.floorplan.remrate_target is None:
            status.floorplan.remrate_target = rem_simulation_factory(
                company__name="unrelated__rater"
            )
            status.floorplan.save()

        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg=f"User {user.username} [pk={user.pk}] is not allowed to login",
        )

        url = reverse("earth_advantage:eaaa_addendum", kwargs={"home_status": status.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response["content-type"], "application/pdf")
