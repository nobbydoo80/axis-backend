"""test_views.py: Django messaging"""


import logging
import os
from unittest import mock

from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from axis.company.tests.mixins import CompaniesAndUsersTestMixin
from axis.core.tests.client import AxisClient
from axis.core.tests.testcases import AxisTestCase

__author__ = "Steven Klass"
__date__ = "06/03/19 4:59 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

from axis.messaging.models import Message
from axis.messaging.tests.factories import (
    modern_message_cls_factory,
    modern_message_registry_factory,
)
from axis.messaging.tokens import unsubscribe_email_token

log = logging.getLogger(__name__)


class MessageViewTests(CompaniesAndUsersTestMixin, AxisTestCase):
    include_company_types = ["builder", "eep"]
    include_unrelated_companies = False

    client_class = AxisClient

    def test_login_required(self):
        url = reverse("messaging:list")
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

        url = reverse("messaging:list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_unsubscribe_email(self):
        user = self.get_random_user()
        message_name = str("TestClassMessage")
        modern_message_cls = modern_message_cls_factory(message_name)

        message_registry, message_categories = modern_message_registry_factory(
            modern_messages=[
                modern_message_cls,
            ]
        )

        modern_message_cls().send(user=user)

        message = Message.objects.get()

        uid = urlsafe_base64_encode(force_bytes(message.user.pk))
        mname = urlsafe_base64_encode(force_bytes(message.modern_message))
        token = unsubscribe_email_token.make_token(message.user)

        url = reverse(
            "messaging:unsubscribe_email", kwargs={"uidb64": uid, "mnameb64": mname, "token": token}
        )

        with mock.patch.dict("axis.messaging.views.MESSAGE_REGISTRY", message_registry, clear=True):
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, "messaging/unsubscribe_email.html")

    def test_unsubscribe_email_with_invalid_data(self):
        user = self.get_random_user()
        message_name = str("TestClassMessage")
        modern_message_cls = modern_message_cls_factory(message_name)

        message_registry, message_categories = modern_message_registry_factory(
            modern_messages=[
                modern_message_cls,
            ]
        )

        modern_message_cls().send(user=user)

        message = Message.objects.get()

        uid = urlsafe_base64_encode(force_bytes(message.user.pk))
        mname = urlsafe_base64_encode(force_bytes(message.modern_message))
        token = unsubscribe_email_token.make_token(message.user)

        # incorrect user id
        url = reverse(
            "messaging:unsubscribe_email",
            kwargs={"uidb64": "incorrectuidb64", "mnameb64": mname, "token": token},
        )

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "messaging/unsubscribe_email_invalid.html")

        # incorrect message id
        url = reverse(
            "messaging:unsubscribe_email",
            kwargs={"uidb64": uid, "mnameb64": "incorrectmnameb64", "token": token},
        )

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "messaging/unsubscribe_email_invalid.html")

        # incorrect token
        url = reverse(
            "messaging:unsubscribe_email",
            kwargs={"uidb64": uid, "mnameb64": mname, "token": "incorrecttoken"},
        )

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "messaging/unsubscribe_email_invalid.html")
