"""test_views.py: Django core"""

__author__ = "Steven Klass"
__date__ = "4/25/13 3:59 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

import logging
import random
import sys
from unittest import mock
from unittest.mock import patch

from django.contrib.auth import SESSION_KEY
from django.core import mail
from django.db.models import Q
from django.urls import reverse

from axis.core.tests.testcases import AxisTestCase, ApiV3Tests
from .client import AxisClient
from .mixins import ApproveTensorAccountTestMixin
from ...company.tests.mixins import CompaniesAndUsersTestMixin

log = logging.getLogger(__name__)


class ProfileViewTests(CompaniesAndUsersTestMixin, AxisTestCase):
    include_company_types = ["rater"]
    include_unrelated_companies = False
    client_class = AxisClient

    def test_login_required(self):
        user = self.random_user

        url = reverse("profile:list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(url, response["Location"], msg=url)
        self.assertIn(reverse("auth:login"), response["Location"])

        url = reverse("profile:detail", kwargs={"pk": 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(url, response["Location"], msg=url)
        self.assertIn(reverse("auth:login"), response["Location"])

        response = self.client.get(reverse("profile:public_list"))
        msg = "Received: %s Expected: %s User %s (%s) unable to access %s" % (
            response.status_code,
            302,
            user.username,
            user.company.company_type,
            reverse("profile:public_list"),
        )
        self.assertEqual(response.status_code, 302, msg=msg)

    def test_user_has_permissions(self):
        """Test that we can login and see profiles"""
        user = self.random_user
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        url = reverse("profile:list")
        response = self.client.get(url)
        msg = "Received: %s Expected: %s User %s (%s) unable to access %s" % (
            response.status_code,
            200,
            user.username,
            user.company.company_type,
            reverse("profile:list"),
        )
        self.assertEqual(response.status_code, 200, msg=msg)

        url = reverse("profile:detail", kwargs={"pk": user.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse("profile:public_list"))
        self.assertEqual(response.status_code, 200)


class CoreViewTests(CompaniesAndUsersTestMixin, AxisTestCase):
    include_company_types = ["builder", "general"]
    include_unrelated_companies = False
    client_class = AxisClient

    def test_login_logout(self):
        """Test that we can't see profiles without logging in"""
        response = self.client.get(reverse("auth:login"))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse("auth:logout"))
        self.assertEqual(response.status_code, 302)

    def test_logout_ability(self):
        users = self.user_model.objects.exclude(
            Q(username__istartswith="noperm_") | Q(is_superuser=True)
        )
        user = random.choice(list(users))
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )
        response = self.client.get(reverse("auth:logout"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/")
        self.assertTrue(SESSION_KEY not in self.client.session)

    def test_ajax_login(self):
        """Test the ajax-login"""
        user = self.random_user

        response = self.client.post(
            reverse("auth:ajax-login"),
            {"username": user.username, "password": "password"},
            ajax=True,
        )
        self.assertEqual(response.status_code, 200)

    def test_no_login_home(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

    def test_home(self):
        """Test that once we are logged in we have something usefull"""
        users = self.user_model.objects.exclude(
            Q(username__istartswith="noperm_") | Q(is_superuser=True)
        )
        user = random.choice(list(users))
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

    def test_basic_search(self):
        """Test that we can't search unless we are logged in."""
        response = self.client.get(reverse("basic_search"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("basic_search"), response["Location"])
        self.assertIn(reverse("auth:login"), response["Location"])


class DevNull(object):
    def write(self, data):
        pass


class CoreMiscViewTests(CompaniesAndUsersTestMixin, AxisTestCase):
    include_company_types = ["provider", "general"]
    include_unrelated_companies = False
    client_class = AxisClient

    def setUp(self):
        self.old_stderr = sys.stderr
        sys.stderr = DevNull()
        logging.disable(200)

    def tearDown(self):
        sys.stderr = self.old_stderr
        logging.disable(logging.NOTSET)

    def test_swagger_docs_as_anonymous(self):
        response = self.client.get(reverse("api_v3_swagger"))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse("api_v3_redoc"))
        self.assertEqual(response.status_code, 200)

        response = self.client.get("{}?format=openapi".format(reverse("api_v3_swagger")))
        self.assertEqual(response.status_code, 200)

        response = self.client.get("{}?format=openapi".format(reverse("api_v3_redoc")))
        self.assertEqual(response.status_code, 200)

    def test_swagger_docs(self):
        self.assertTrue(
            self.client.login(username=self.super_user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login"
            % (self.super_user.username, self.super_user.pk),
        )
        response = self.client.get(reverse("api_v3_swagger"))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse("api_v3_redoc"))
        self.assertEqual(response.status_code, 200)

        response = self.client.get("{}?format=openapi".format(reverse("api_v3_swagger")))
        self.assertEqual(response.status_code, 200)

        response = self.client.get("{}?format=openapi".format(reverse("api_v3_redoc")))
        self.assertEqual(response.status_code, 200)

    @patch("captcha.fields.ReCaptchaField.validate")
    def test_contact_view(self, validate_method):
        from axis.core.tests.factories import general_super_user_factory

        # created a companies required by certification_admin task
        general_super_user_factory(company__slug="pivotal-energy-solutions")

        response = self.client.get(reverse("contact"))
        self.assertEqual(response.status_code, 200)

        data = {
            "name": "Bob Johnson",
            "email": "big_johnson@home.com",
            "phone": "800-212-2001",
            "subject": "I want Axis!",
            "message": "This is a giant\nThree liner..\nLove ya\n",
            "body": "",
            "captcha": "XXX",
        }
        validate_method.return_value = True

        with self.subTest("Failing body"):
            data["body"] = "x"
            response = self.client.post(reverse("contact"), data=data)
            self.assertEqual(response.status_code, 302)

            self.assertEqual(len(mail.outbox), 0)

        data["body"] = ""
        with self.subTest("Failing Porn"):
            data["message"] = "some sex and love in .ru"
            response = self.client.post(reverse("contact"), data=data)
            self.assertEqual(response.status_code, 302)

            self.assertEqual(len(mail.outbox), 0)

        data["message"] = "This is a giant\nThree liner..\nLove ya\n"
        with self.subTest("Passing"):
            response = self.client.post(reverse("contact"), data=data)
            self.assertEqual(response.status_code, 302)

            self.assertEqual(len(mail.outbox), 1)
            self.assertIn("Pivotal Contact Request:", mail.outbox[0].subject)
            self.assertIn(data["subject"], mail.outbox[0].subject)

            self.assertIn(data["name"], mail.outbox[0].body)
            self.assertIn(data["email"], mail.outbox[0].body)
            self.assertIn(data["phone"], mail.outbox[0].body)
            self.assertIn(data["message"].split("\n")[0], mail.outbox[0].body)
            self.assertIn(data["message"].split("\n")[1], mail.outbox[0].body)
            self.assertIn(data["message"].split("\n")[2], mail.outbox[0].body)

            self.assertEqual(len(mail.outbox[0].alternatives), 1)
            self.assertEqual(mail.outbox[0].alternatives[0][1], "text/html")

            self.assertIn(data["name"], mail.outbox[0].alternatives[0][0])
            self.assertIn(data["email"], mail.outbox[0].alternatives[0][0])
            self.assertIn(data["phone"], mail.outbox[0].alternatives[0][0])
            self.assertIn(data["message"].split("\n")[0], mail.outbox[0].alternatives[0][0])
            self.assertIn(data["message"].split("\n")[1], mail.outbox[0].alternatives[0][0])
            self.assertIn(data["message"].split("\n")[2], mail.outbox[0].alternatives[0][0])


class ApproveTensorAccountTests(ApproveTensorAccountTestMixin, ApiV3Tests):
    client_class = AxisClient

    def test_approval_by_company_admin(self):
        builder_company_admin_user = self.get_admin_user(company_type="builder")

        new_not_approved_user = self.user_model.objects.get(is_approved=False)
        new_not_approved_user.company = builder_company_admin_user.company
        new_not_approved_user.save()

        self.assertTrue(
            self.client.login(username=builder_company_admin_user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login"
            % (builder_company_admin_user.username, builder_company_admin_user.pk),
        )

        self.client.get(
            reverse("auth:approve_tensor_account", kwargs={"pk": new_not_approved_user.pk})
        )

        new_not_approved_user.refresh_from_db()
        self.assertEqual(new_not_approved_user.is_approved, True)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Your AXIS account has been approved")

    def test_approval_by_pivotal_support(self):
        from axis.company.models import Company

        company = Company.objects.first()
        pivotal_user = self.user_model.objects.get(
            username="admin", company__slug="pivotal-energy-solutions"
        )

        self.assertTrue(
            self.client.login(username=pivotal_user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login"
            % (pivotal_user.username, pivotal_user.pk),
        )

        new_not_approved_user = self.user_model.objects.get(is_approved=False)
        new_not_approved_user.is_active = True
        new_not_approved_user.is_approved = False
        new_not_approved_user.company = None
        new_not_approved_user.save()

        data = {"company": company.id}

        url = reverse("auth:approve_tensor_account", kwargs={"pk": new_not_approved_user.pk})

        response = self.client.post(url, data=data)
        self.assertRedirects(response, reverse("admin:core_user_changelist"))

        new_not_approved_user.refresh_from_db()
        self.assertTrue(new_not_approved_user.is_approved)
        self.assertEqual(new_not_approved_user.company, company)

        # check that we send email to new user
        self.assertGreaterEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Your AXIS account has been approved")

    def test_login_required(self):
        new_not_approved_user = self.user_model.objects.get(is_approved=False)

        url = reverse("auth:approve_tensor_account", kwargs={"pk": new_not_approved_user.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(url, response["Location"], msg=url)
        self.assertIn(reverse("auth:login"), response["Location"])

    def test_approval_by_user_from_different_company(self):
        builder_company_admin_user = self.get_admin_user(company_type="builder")

        new_not_approved_user = self.user_model.objects.get(is_approved=False)
        self.assertTrue(
            self.client.login(username=builder_company_admin_user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login"
            % (builder_company_admin_user.username, builder_company_admin_user.pk),
        )

        new_not_approved_user.refresh_from_db()
        self.assertEqual(new_not_approved_user.is_approved, False)

    def test_approval_by_non_company_admin_user(self):
        builder_user = self.get_nonadmin_user(company_type="builder")
        new_not_approved_user = self.user_model.objects.get(is_approved=False)
        self.assertTrue(
            self.client.login(username=builder_user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login"
            % (builder_user.username, builder_user.pk),
        )
        new_not_approved_user.refresh_from_db()
        self.assertEqual(new_not_approved_user.is_approved, False)
