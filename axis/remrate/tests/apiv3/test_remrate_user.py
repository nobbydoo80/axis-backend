"""remrate_user.py: """

from django.urls import reverse_lazy
from unittest import mock
from django.conf import settings

from axis.company.tests.mixins import CompaniesAndUsersTestMixin
from axis.core.tests.testcases import ApiV3Tests
from axis.remrate.api_v3.viewsets import NestedRemRateUserViewSet, RemRateUserViewSet

__author__ = "Rajesh Pethe"
__date__ = "07/13/2020 17:18"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
    "Rajesh Pethe",
]

orig_create_db_user = NestedRemRateUserViewSet.create_db_user
orig_update_db_user = RemRateUserViewSet.update_db_user
orig_delete_db_user = RemRateUserViewSet.delete_db_user


def mock_db_actions(self, *args, **_kwargs):
    if settings.DATABASES["default"]["ENGINE"] != "django.db.backends.mysql":
        return None

    if self.action == "create":
        return orig_create_db_user(self, args[0])
    elif self.action == "update":
        return orig_update_db_user(self, args[0])
    elif self.action == "destroy":
        return orig_delete_db_user(self, args[0])


class TestRemrateUserViewSet(CompaniesAndUsersTestMixin, ApiV3Tests):
    include_company_types = ["rater", "general", "provider"]
    include_unrelated = False
    include_noperms = False

    def test_permissions(self):
        user = self.get_nonadmin_user(company_type="general")
        list_url = reverse_lazy("api_v3:company-remrate_users-list", args=(user.company.id,))

        self.client.force_authenticate(user=user)
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, 403)

    def test_auth_required(self):
        """Test that we can't see remrate users without logging in"""

        rater_user = self.get_admin_user(company_type="rater")
        rater_org = rater_user.company

        list_url = reverse_lazy("api_v3:company-remrate_users-list", args=(rater_org.id,))
        update_url = reverse_lazy("api_v3:remrate_users-detail", args=(rater_user.id,))
        delete_url = reverse_lazy("api_v3:remrate_users-detail", args=(rater_user.id,))

        response = self.client.get(list_url)
        self.assertEqual(response.status_code, 401)

        response = self.client.put(update_url)
        self.assertEqual(response.status_code, 401)

        response = self.client.patch(update_url)
        self.assertEqual(response.status_code, 401)

        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, 401)

    @mock.patch(
        "axis.remrate.api_v3.viewsets.NestedRemRateUserViewSet.create_db_user",
        side_effect=mock_db_actions,
        autospec=True,
    )
    @mock.patch(
        "axis.remrate.api_v3.viewsets.RemRateUserViewSet.update_db_user",
        side_effect=mock_db_actions,
        autospec=True,
    )
    @mock.patch(
        "axis.remrate.api_v3.viewsets.RemRateUserViewSet.delete_db_user",
        side_effect=mock_db_actions,
        autospec=True,
    )
    def test_crud(self, *args):
        """Test CRUD works as expected."""

        provider_user = self.get_admin_user(company_type="provider")
        provider_org = provider_user.company
        create_url = reverse_lazy("api_v3:company-remrate_users-list", args=(provider_org.id,))
        kwargs = dict(
            url=create_url,
            user=provider_user,
            data=dict(
                username="testuser",
                password="PassString1",
                confirm_password="PassString1",
                company=provider_org.id,
            ),
        )

        self.create(**kwargs)

        list_url = reverse_lazy("api_v3:company-remrate_users-list", args=(provider_org.id,))
        kwargs = dict(url=list_url, user=provider_user)
        data = self.list(**kwargs)
        self.assertEqual(len(data), 1)

        pk = data[0].get("id")
        self.assertEqual(data[0].get("username"), "testuser")

        update_url = reverse_lazy("api_v3:remrate_users-detail", args=(pk,))
        update_data = dict(
            username="testuser",
            password="PassString123",
            confirm_password="PassString123",
            company=provider_org.id,
        )
        self.update(update_url, provider_user, data=update_data)

        delete_url = reverse_lazy("api_v3:remrate_users-detail", args=(pk,))
        self.delete(delete_url, provider_user)

    @mock.patch(
        "axis.remrate.api_v3.viewsets.NestedRemRateUserViewSet.create_db_user",
        side_effect=mock_db_actions,
        autospec=True,
    )
    def test_validation(self, mock):
        """Test username and password strength validation works."""

        user = self.get_admin_user(company_type="provider")
        provider_org = user.company
        create_url = reverse_lazy("api_v3:company-remrate_users-list", args=(provider_org.id,))
        self.client.force_authenticate(user=user)
        data = dict(
            username="testuser", password="pass1", confirm_password="pass1", company=provider_org.id
        )

        # Weak password
        response = self.client.post(create_url, data=data)
        self.assertEqual(response.status_code, 400)

        # Password mismatch
        data["password"] = "Pa55word123"
        data["confirm_password"] = "PaSSword123"
        response = self.client.post(create_url, data=data)
        self.assertEqual(response.status_code, 400)

        # Still weak password
        data["password"] = "string"
        data["confirm_password"] = "string"
        response = self.client.post(create_url, data=data)
        self.assertEqual(response.status_code, 400)

        # Reserved username
        data["username"] = "root"
        data["password"] = "Pa55word123"
        data["confirm_password"] = "Pa55word123"
        response = self.client.post(create_url, data=data)
        self.assertEqual(response.status_code, 400)

        # Reserved password
        data["username"] = "tempuser"
        data["password"] = "Pa55w0rd"
        data["confirm_password"] = "Pa55w0rd"
        response = self.client.post(create_url, data=data)
        self.assertEqual(response.status_code, 400)

        # Create a duplicate
        data["username"] = "tempuser"
        data["password"] = "Pa55word123"
        data["confirm_password"] = "Pa55word123"
        response = self.client.post(create_url, data=data)
        self.assertEqual(response.status_code, 201)

        # Re-create duplicate, fails.
        data["username"] = "tempuser"
        data["password"] = "Pa55word123"
        data["confirm_password"] = "Pa55word123"
        response = self.client.post(create_url, data=data)
        self.assertEqual(response.status_code, 400)
