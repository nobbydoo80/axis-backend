"""test_signals.py - Axis"""

__author__ = "Steven K"
__date__ = "6/18/21 08:25"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
import re
from unittest.mock import Mock
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core import mail
from django.urls import reverse

from axis.company.models import Company
from axis.core.middleware import DynamicSiteDomainMiddleware
from axis.core.signals import user_registered_additional_setup
from axis.core.tests.client import AxisClient
from axis.core.tests.factories import rater_user_factory
from axis.core.tests.mixins import ApproveTensorAccountTestMixin
from axis.core.tests.testcases import ApiV3Tests

log = logging.getLogger(__name__)
User = get_user_model()


class TensorAccountSignalTests(ApproveTensorAccountTestMixin, ApiV3Tests):
    client_class = AxisClient

    def _register_a_new_user(self, data=None):
        if not data:
            data = {}
        with patch("captcha.fields.ReCaptchaField.validate") as validate_method:
            url = reverse("register_anonymous")

            response = self.client.get(url)
            self.assertTrue(response.status_code, 200)

            default_data = {
                "company": "",
                "first_name": "first",
                "last_name": "last",
                "email": "me@example.com",
                "cell_phone": "321-456-7689",
                "work_phone": "321-456-7689",
                "title": "title",
                "department": "department",
                "password1": "Xpassword1",
                "password2": "Xpassword1",
                "tos": True,
            }
            default_data.update(data)
            # Register a user
            validate_method.return_value = True
            response = self.client.post(url, data=default_data)

            self.assertRedirects(
                response, reverse("tensor_registration:anonymous_registration_complete")
            )

            # Dude has registered
            self.assertEqual(len(mail.outbox), 1)
            self.assertIn("Account registration invitation", mail.outbox[0].subject)

            # Activate the user
            email = mail.outbox[0].body
            activation_url = re.findall(
                r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
                email,
            )[0]

            # Trailing slash in URL means activation key will be 2nd to last in the list
            activation_key = activation_url.split("/")[-2]

            url = reverse(
                "tensor_registration:anonymous_activate",
                kwargs={"activation_key": str(activation_key)},
            )
            response = self.client.get(url)
            self.assertRedirects(
                response, reverse("tensor_registration:anonymous_activation_complete")
            )

    def test_anonymous_user_activation_notification_with_company(self):
        self.assertEqual(len(mail.outbox), 0)

        company = Company.objects.exclude(slug="pivotal-energy-solutions").first()
        self.assertTrue(company.users.filter(is_company_admin=True, is_active=True).exists())

        self._register_a_new_user(data={"company": company.id})

        # Verify user was activated successfully
        self.assertEqual(len(mail.outbox), 3)  # One to pivotal / One to the company

        self.assertIn("A new user is requesting to use AXIS as member of", mail.outbox[1].subject)
        self.assertIn("A new user is requesting to use AXIS as member of", mail.outbox[2].subject)

    def test_anonymous_user_activation_notification_without_company(self):
        self.assertEqual(len(mail.outbox), 0)
        pivotal_user = self.user_model.objects.get(
            username="admin", company__slug="pivotal-energy-solutions"
        )

        self._register_a_new_user()

        # Verify user was activated successfully
        self.assertEqual(len(mail.outbox), 2)  # One to pivotal

        self.assertIn("A new user is requesting to use AXIS without", mail.outbox[1].subject)
        self.assertIn(pivotal_user.email, mail.outbox[1].to[0])

    def test_anonymous_user_activation_notification_without_company_approval(self):
        self.assertEqual(len(mail.outbox), 0)
        pivotal_user = self.user_model.objects.get(
            username="admin", company__slug="pivotal-energy-solutions"
        )

        self._register_a_new_user()

        # Verify user was activated successfully
        self.assertEqual(len(mail.outbox), 2)  # One to pivotal

        self.assertIn("A new user is requesting to use AXIS without", mail.outbox[1].subject)
        self.assertIn(pivotal_user.email, mail.outbox[1].to[0])

        # Now need to approve a user
        email = mail.outbox[1].body

        user = User.objects.filter(is_approved=False).order_by("id").last()
        approval_url = reverse("auth:approve_tensor_account", kwargs={"pk": user.pk})

        self.assertIn(approval_url, email)

        self.assertTrue(
            self.client.login(username=pivotal_user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login"
            % (self.super_user.username, self.super_user.pk),
        )
        # print(mail.outbox[1].alternatives[0][0])

    def test_user_registered_set_customer_site(self):
        hi_site = Site.objects.create(
            name="homeinnovation", domain="homeinnovation.pivotalenergy.net"
        )

        pivotal_user = self.user_model.objects.get(
            username="admin", company__slug="pivotal-energy-solutions"
        )

        with self.settings(SITE_ID=1):
            self._register_a_new_user()

            user = User.objects.order_by("id").last()

            request = Mock()
            request.get_host = lambda: "homeinnovation.pivotalenergy.net"
            my_middleware = DynamicSiteDomainMiddleware(request)
            my_middleware(request)

            user_registered_additional_setup(sender=None, user=user, request=request)

            user.refresh_from_db()

            self.assertEqual(user.site, hi_site)

    def test_user_registered_set_default_site(self):
        example_site = Site.objects.get(domain="example.com")

        pivotal_user = self.user_model.objects.get(
            username="admin", company__slug="pivotal-energy-solutions"
        )
        with self.subTest("Use default site for registration"):
            with self.settings(SITE_ID=1):
                self._register_a_new_user()

                user = User.objects.order_by("id").last()

                request = Mock()
                request.get_host = lambda: "Unknown domain"
                request.return_value = None

                my_middleware = DynamicSiteDomainMiddleware(request)
                my_middleware(request)

                user_registered_additional_setup(sender=None, user=user, request=request)

                user.refresh_from_db()

                self.assertEqual(user.site, example_site)

    def test_user_registered_set_company_access(self):
        # companies list in registration form is only show companies with Admin
        rater_user = rater_user_factory(is_company_admin=True)
        pivotal_user = self.user_model.objects.get(
            username="admin", company__slug="pivotal-energy-solutions"
        )
        with self.subTest("Registered User must have company access to default company"):
            self._register_a_new_user(data={"company": rater_user.company.id})

            user = User.objects.order_by("id").last()
            self.assertEqual(user.companies.count(), 1)
            self.assertEqual(user.default_company, user.company)

            # clean mailbox for new registrations
            mail.outbox.clear()

        with self.subTest("Registered User without company"):
            self._register_a_new_user(
                {
                    "email": "another@example.com",
                }
            )

            user = User.objects.order_by("id").last()
            self.assertEqual(user.companies.count(), 0)
            self.assertIsNone(user.default_company)
