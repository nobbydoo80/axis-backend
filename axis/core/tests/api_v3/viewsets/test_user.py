"""user.py: """

__author__ = "Artem Hruzd"
__date__ = "05/11/2020 14:16"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.apps import apps
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.urls import reverse_lazy
from django.utils import timezone
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.settings import api_settings as simplejwt_settings

from axis.company.models import SponsorPreferences
from axis.company.tests.factories import provider_organization_factory
from axis.core.tests.factories import rater_admin_factory, provider_user_factory
from axis.core.tests.mixins import ImpersonateTestMixin
from axis.core.tests.testcases import ApiV3Tests
from axis.customer_hirl.tests.factories import verifier_agreement_factory
from axis.customer_hirl.verifier_agreements.states import VerifierAgreementStates
from axis.user_management.models import Accreditation
from axis.user_management.tests.factories import accreditation_factory

User = get_user_model()
customer_hirl_app = apps.get_app_config("customer_hirl")


class TestImpersonateUserViewSet(ImpersonateTestMixin, ApiV3Tests):
    """
    Impersonation workflow for api v3
    """

    def test_impersonate_common_user_with_superuser(self):
        superuser = self.super_user
        non_admin_user = self.nonadmin_user

        # obtain new token
        url = reverse_lazy("api_v3:token_obtain_pair")
        response = self.client.post(
            url, {"username": superuser.username, "password": "password"}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        access_token = response.data["access"]
        refresh_token = response.data["refresh"]

        # start impersonation
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + access_token)
        url = reverse_lazy("api_v3:users-impersonate-start", kwargs={"pk": non_admin_user.pk})
        response = self.client.get(url, format="json")
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

        self.assertEqual(self.client.session["_auth_user_id"], str(superuser.pk))
        self.assertEqual(self.client.session["_impersonate"], non_admin_user.pk)

        # try to access to protected view with new token
        self.client.credentials(HTTP_AUTHORIZATION="Bearer {}".format(impersonate_access_token))
        url = reverse_lazy("api_v3:cities-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # stop impersonation
        url = reverse_lazy("api_v3:users-impersonate-stop")
        self.client.credentials(HTTP_AUTHORIZATION="Bearer {}".format(impersonate_access_token))
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.data["access"], "{}".format(access_token))
        self.assertNotEqual(response.data["access"], "{}".format(impersonate_access_token))

        # try to access to protected view with old impersonation token
        self.client.credentials(HTTP_AUTHORIZATION="Bearer {}".format(impersonate_access_token))
        url = reverse_lazy("api_v3:cities-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_impersonate_as_impersonated_user(self):
        superuser = self.super_user
        non_admin_user = self.nonadmin_user

        # obtain new token
        url = reverse_lazy("api_v3:token_obtain_pair")
        response = self.client.post(
            url, {"username": superuser.username, "password": "password"}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        access_token = response.data["access"]
        refresh_token = response.data["refresh"]

        # start impersonation
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + access_token)
        url = reverse_lazy("api_v3:users-impersonate-start", kwargs={"pk": non_admin_user.pk})
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.data["refresh"], "{}".format(refresh_token))
        self.assertNotEqual(response.data["access"], "{}".format(access_token))

        impersonate_access_token = response.data["access"]

        # start impersonation with impersonate_access_token
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + impersonate_access_token)
        url = reverse_lazy("api_v3:users-impersonate-start", kwargs={"pk": non_admin_user.pk})
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 200)

    def test_impersonation_list_as_superuser(self):
        url = reverse_lazy("api_v3:users-impersonation-list")
        data = self.list(url=url, user=self.super_user)
        self.assertEqual(
            len(data), User.objects.exclude(Q(is_staff=True) | Q(is_superuser=True)).count()
        )

    def test_impersonation_list_as_impersonated_user(self):
        superuser = self.super_user
        non_admin_user = self.nonadmin_user

        # obtain new token
        url = reverse_lazy("api_v3:token_obtain_pair")
        response = self.client.post(
            url, {"username": superuser.username, "password": "password"}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        access_token = response.data["access"]

        # start impersonation
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + access_token)
        url = reverse_lazy("api_v3:users-impersonate-start", kwargs={"pk": non_admin_user.pk})
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 200)

        url = reverse_lazy("api_v3:users-impersonation-list")
        response = self.client.get(url, format="json")
        data = response.data.get("results")

        self.assertEqual(
            len(data),
            User.objects.exclude(
                Q(is_staff=True) | Q(is_superuser=True) | Q(is_active=False) | Q(is_approved=False)
            ).count(),
        )

    def test_impersonation_list_as_common_user(self):
        url = reverse_lazy("api_v3:users-impersonation-list")
        with self.assertRaises(AssertionError):
            self.list(url=url, user=self.nonadmin_user)

    def test_info_as_common_user(self):
        url = reverse_lazy("api_v3:token_obtain_pair")
        response = self.client.post(
            url, {"username": self.nonadmin_user.username, "password": "password"}, format="json"
        )
        self.assertEqual(response.status_code, 200)

        # check info response
        url = reverse_lazy("api_v3:users-info")
        response = self.client.get(url)
        self.assertIsNone(response.data["impersonated"])
        self.assertEqual(response.data["user"]["username"], self.nonadmin_user.username)
        self.assertEqual(response.data["session_key"], self.client.session.session_key)
        self.assertIsNotNone(response.data["csrftoken"])

    def test_info_as_impersonated_user(self):
        # obtain new token
        url = reverse_lazy("api_v3:token_obtain_pair")
        response = self.client.post(
            url, {"username": self.super_user.username, "password": "password"}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        access_token = response.data["access"]

        # start impersonation
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + access_token)
        url = reverse_lazy("api_v3:users-impersonate-start", kwargs={"pk": self.nonadmin_user.pk})
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 200)

        # check info response
        url = reverse_lazy("api_v3:users-info")
        response = self.client.get(url)
        self.assertEqual(response.data["impersonated"]["username"], self.nonadmin_user.username)
        self.assertEqual(response.data["user"]["username"], self.super_user.username)
        self.assertEqual(response.data["session_key"], self.client.session.session_key)
        self.assertIsNotNone(response.data["csrftoken"])


class TestChangePasswordUserViewSet(ImpersonateTestMixin, ApiV3Tests):
    def test_change_password(self):
        non_admin_user = self.nonadmin_user

        # obtain new token
        url = reverse_lazy("api_v3:token_obtain_pair")
        response = self.client.post(
            url, {"username": non_admin_user.username, "password": "password"}, format="json"
        )

        self.assertEqual(response.status_code, 200)

        # check info response
        new_password = "Test@Password123"
        url = reverse_lazy("api_v3:users-change-password")
        response = self.client.patch(
            url,
            {
                "old_password": "password",
                "password": new_password,
                "confirmed_password": new_password,
            },
        )
        self.assertEqual(response.status_code, 200)

        non_admin_user.refresh_from_db()
        self.assertTrue(non_admin_user.check_password(new_password))


class TestUserViewSet(ApiV3Tests):
    def test_customer_hirl_find_verifier_list(self):
        hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )
        hirl_user = provider_user_factory(
            first_name="NGBS", last_name="Admin", company=hirl_company, is_company_admin=True
        )
        verifier_user = rater_admin_factory(
            first_name="Verifier User", company__name="Verifier Company"
        )
        SponsorPreferences.objects.create(
            sponsor=hirl_company, sponsored_company=verifier_user.company
        )
        verifier_user.company.update_permissions()

        # active accreditation
        accreditation = accreditation_factory(
            trainee=verifier_user,
            name=Accreditation.NGBS_2020_NAME,
            state=Accreditation.ACTIVE_STATE,
            manual_expiration_date=timezone.now() + timezone.timedelta(days=365),
        )
        # verifier agreement
        verifier_agreement = verifier_agreement_factory(
            owner=hirl_company,
            verifier=verifier_user,
            state=VerifierAgreementStates.COUNTERSIGNED,
        )

        find_verifier_url = reverse_lazy("api_v3:users-customer-hirl-find-verifier-list")
        data = self.list(url=find_verifier_url, user=hirl_user)
        self.assertEqual(data[0]["first_name"], verifier_user.first_name)
        self.assertEqual(
            data[0]["customer_hirl_enrolled_verifier_agreements_info"][0]["id"],
            verifier_agreement.id,
        )
        self.assertEqual(
            data[0]["accreditations_info"][0]["id"],
            accreditation.id,
        )
