"""test_views.py: Django customer_appraisal_institute"""


import logging

from django.urls import reverse

from axis.core.tests.client import AxisClient
from axis.core.tests.factories import general_super_user_factory
from axis.core.tests.testcases import ApiV3Tests
from axis.home.models import EEPProgramHomeStatus
from axis.home.tests.factories import custom_home_with_basic_eep_factory_and_remrate

__author__ = "Steven Klass"
__date__ = "6/2/13 9:25 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class CustomerAppraisalInstituteViewTests(ApiV3Tests):
    """Test out builder agreeement application"""

    client_class = AxisClient

    @classmethod
    def setUpTestData(cls):
        super(CustomerAppraisalInstituteViewTests, cls).setUpTestData()
        from axis.home.tests.factories import custom_home_with_basic_eep_factory_and_remrate

        custom_home_with_basic_eep_factory_and_remrate(eep_program__no_close_dates=True)

    def test_login_required(self):
        """Test that we can't see companies without logging in."""
        urls = [
            reverse("appraisal_institute:green_addendum", kwargs={"home_status": 0}),
        ]

        LOGIN_URL = reverse("auth:login")
        redirect_format = "{url}?next={from_url}"

        for url in urls:
            response = self.client.get(url)
            self.assertRedirects(response, redirect_format.format(url=LOGIN_URL, from_url=url))

    def test_company_user_has_permissions(self):
        """Test that we can login and see Customer Appraisal"""
        user = general_super_user_factory()
        home = custom_home_with_basic_eep_factory_and_remrate()
        status = EEPProgramHomeStatus.objects.get(home=home)

        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )
        self.assertEqual(user.has_perm("home.change_home"), True)

    def test_get_green_addendum(self):
        user = general_super_user_factory()
        home = custom_home_with_basic_eep_factory_and_remrate()

        status = EEPProgramHomeStatus.objects.get(home=home)
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        url = reverse("appraisal_institute:green_addendum", kwargs={"home_status": status.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
