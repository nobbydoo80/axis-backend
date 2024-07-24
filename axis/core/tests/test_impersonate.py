"""impersonate.py: """

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.settings import api_settings as simplejwt_settings

from axis.core.tests.client import AxisClient
from axis.core.tests.testcases import ApiV3Tests
from .mixins import ImpersonateTestMixin

__author__ = "Artem Hruzd"
__date__ = "03/09/2020 15:13"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


User = get_user_model()


class ImpersonateViewTests(ImpersonateTestMixin, ApiV3Tests):
    client_class = AxisClient

    def test_basic_auth_conditions(self):
        """
        When a user is not logged in request.User == AnonymousUser
        When a user logs in request.user == User logged
        When a user logs out request.user == AnonymousUser
        :return:
        """
        non_admin_user = self.nonadmin_user
        url = reverse("auth:login")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(self.client.session.get("_auth_user_id"))

        response = self.client.post(
            url, data={"username": non_admin_user.username, "password": "password"}, follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.session["_auth_user_id"], str(non_admin_user.pk))
        self.assertNotEqual(self.client.cookies["access"].value, "")
        self.assertNotEqual(self.client.cookies["refresh"].value, "")

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.session["_auth_user_id"], str(non_admin_user.pk))

        url = reverse("auth:logout")
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.cookies["access"].value, "")
        self.assertEqual(self.client.cookies["refresh"].value, "")

        url = reverse("auth:login")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(self.client.session.get("_auth_user_id"))

    def test_session_impersonate_common_user_with_superuser(self):
        superuser = self.super_user
        non_admin_user = self.nonadmin_user

        self.assertTrue(
            self.client.login(username=superuser.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (superuser.username, superuser.pk),
        )

        url = reverse("apiv2:user-impersonate-start", kwargs={"pk": non_admin_user.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(self.client.session["_auth_user_id"], str(superuser.pk))
        self.assertEqual(self.client.session["_impersonate"], non_admin_user.pk)

        # check that our jwt token contain our session impersonated user
        url = reverse("jwt:token_obtain_pair")
        response = self.client.post(
            url, {"username": superuser.username, "password": "password"}, format="json"
        )

        impersonate_access_token = None
        for AuthToken in simplejwt_settings.AUTH_TOKEN_CLASSES:
            try:
                impersonate_access_token = AuthToken(response.data["access"])
            except TokenError:
                pass

        self.assertEqual(response.status_code, 200)
        self.assertEqual(impersonate_access_token.payload["user_id"], non_admin_user.pk)
        self.assertEqual(impersonate_access_token.payload["impersonator"], superuser.pk)

        url = reverse("apiv2:user-impersonate-stop")
        response = self.client.post(url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(self.client.session["_auth_user_id"], str(superuser.pk))
        self.assertIsNone(self.client.session.get("_impersonate"))

        # TODO: need to tell front-end to re-issue new tokens to update UI after stop impersonation
        # try to access to protected view with old impersonation token
        api_client = APIClient()
        api_client.credentials(HTTP_AUTHORIZATION="Bearer {}".format(impersonate_access_token))
        url = reverse("apiv2:messages-list")
        response = api_client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_jwt_impersonate_common_user_with_superuser(self):
        superuser = self.super_user
        non_admin_user = self.nonadmin_user

        api_client = APIClient()

        # obtain new token
        url = reverse("jwt:token_obtain_pair")
        response = api_client.post(
            url, {"username": superuser.username, "password": "password"}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        access_token = response.data["access"]
        refresh_token = response.data["refresh"]

        # start impersonation
        api_client.credentials(HTTP_AUTHORIZATION="Bearer " + access_token)
        url = reverse("apiv2:user-impersonate-start", kwargs={"pk": non_admin_user.pk})
        response = api_client.post(url, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.data["refresh"], "{}".format(refresh_token))
        self.assertNotEqual(response.data["access"], "{}".format(access_token))

        impersonate_access_token = None
        for AuthToken in simplejwt_settings.AUTH_TOKEN_CLASSES:
            try:
                impersonate_access_token = AuthToken(response.data["access"])
            except TokenError:
                pass
        self.assertEqual(impersonate_access_token.payload["user_id"], non_admin_user.pk)
        self.assertEqual(impersonate_access_token.payload["impersonator"], superuser.pk)

        self.assertEqual(api_client.session["_auth_user_id"], str(superuser.pk))
        self.assertEqual(api_client.session["_impersonate"], non_admin_user.pk)

        # try to access to protected view with new token
        api_client.credentials(HTTP_AUTHORIZATION="Bearer {}".format(impersonate_access_token))
        url = reverse("apiv2:messages-list")
        response = api_client.get(url)
        self.assertEqual(response.status_code, 200)

        # stop impersonation
        url = reverse("apiv2:user-impersonate-stop")
        api_client.credentials(HTTP_AUTHORIZATION="Bearer {}".format(impersonate_access_token))
        response = api_client.post(url, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.data["access"], "{}".format(access_token))
        self.assertNotEqual(response.data["access"], "{}".format(impersonate_access_token))

        # TODO: impersonate access token will be still valid. Do we need to black list it ?
        # try to access to protected view with old impersonation token
        api_client.credentials(HTTP_AUTHORIZATION="Bearer {}".format(impersonate_access_token))
        url = reverse("apiv2:messages-list")
        response = api_client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_malformed_jwt_token(self):
        """Verify that if we get a malformed bearer we return 401"""
        superuser = self.super_user

        api_client = APIClient()

        # obtain new token
        url = reverse("jwt:token_obtain_pair")
        response = api_client.post(
            url, {"username": superuser.username, "password": "password"}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        access_token = response.data["access"]

        url = reverse("apiv2:messages-list")
        api_client.credentials(HTTP_AUTHORIZATION="Bearer " + access_token)
        self.assertEqual(api_client.get(url).status_code, 200)

        # try to access anything with a malformed Bearer
        api_client = APIClient()
        api_client.credentials(HTTP_AUTHORIZATION="Bearer")
        self.assertEqual(api_client.get(url).status_code, 401)

        api_client = APIClient()
        api_client.credentials(HTTP_AUTHORIZATION="Bearer a b c")
        self.assertEqual(api_client.get(url).status_code, 401)
