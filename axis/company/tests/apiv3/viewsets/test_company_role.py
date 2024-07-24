__author__ = "Artem Hruzd"
__date__ = "02/23/2023 17:19"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


from django.apps import apps
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from rest_framework import status

from axis.company.models import CompanyRole
from axis.company.tests.factories import (
    company_role_factory,
)
from axis.core.tests.factories import (
    provider_user_factory,
    builder_user_factory,
)
from axis.core.tests.testcases import ApiV3Tests

User = get_user_model()
customer_hirl_app = apps.get_app_config("customer_hirl")


class TestCompanyAccessViewSet(ApiV3Tests):
    def test_list(self):
        list_url = reverse_lazy("api_v3:company_roles-list")
        user = provider_user_factory()

        is_company_admin_role = company_role_factory(
            name="Is Company Admin", slug=CompanyRole.IS_COMPANY_ADMIN
        )
        custom_role = company_role_factory(name="Custom Role")

        company_accesses = CompanyRole.objects.filter_by_user(user=user)
        self.assertEqual(company_accesses.count(), 2)

        kwargs = dict(url=list_url, user=user)
        data = self.list(**kwargs)

        self.assertEqual(len(data), company_accesses.count())

    def test_create(self):
        create_url = reverse_lazy("api_v3:company_roles-list")
        builder_user = builder_user_factory(
            first_name="builder", company__name="builder", is_company_admin=True
        )
        superuser = builder_user_factory(
            first_name="superuser", company__name="builder2", is_superuser=True
        )

        is_company_admin_role = company_role_factory(
            name="Is Company Admin", slug=CompanyRole.IS_COMPANY_ADMIN
        )
        custom_role = company_role_factory(name="Custom Role")

        with self.subTest("Create Company Role as common user is prohibited"):
            self.create(
                url=create_url,
                user=builder_user,
                data=dict(
                    name="New Role",
                    slug="new_role",
                ),
                expected_status=status.HTTP_403_FORBIDDEN,
            )

        with self.subTest("Create Company Access as super for any user"):
            data = self.create(
                url=create_url,
                user=superuser,
                data=dict(
                    name="New Role",
                    slug="new_role",
                ),
            )

            self.assertEqual(data["name"], "New Role")
            self.assertEqual(data["slug"], "new_role")
