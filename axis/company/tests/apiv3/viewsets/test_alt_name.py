"""nested_alt_name.py: """


from django.urls import reverse_lazy
from rest_framework import status

from axis.company.models import AltName
from axis.company.models import BuilderOrganization
from axis.company.strings import COMPANY_TYPES_MAPPING
from axis.company.tests.factories import builder_organization_factory, utility_organization_factory
from axis.company.tests.mixins import CompaniesAndUsersTestMixin
from axis.core.tests.factories import builder_user_factory, provider_user_factory
from axis.core.tests.testcases import ApiV3Tests

__author__ = "Artem Hruzd"
__date__ = "03/20/2020 20:03"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class TestNestedAltNameViewSet(ApiV3Tests):
    def test_list(self):
        builder_organization = builder_organization_factory()
        user = builder_user_factory(company=builder_organization)
        AltName.objects.create(company=builder_organization, name="test")
        list_url = reverse_lazy("api_v3:company-alt_names-list", args=(builder_organization.id,))
        kwargs = dict(url=list_url, user=user)
        data = self.list(**kwargs)
        self.assertEqual(len(data), builder_organization.altname_set.count())
        self.assertGreater(builder_organization.altname_set.count(), 0)

    def test_create_as_company_admin_member(self):
        builder_organization = builder_organization_factory()
        user = builder_user_factory(company=builder_organization, is_company_admin=True)

        self.assertEqual(user.company.altname_set.count(), 0)
        list_url = reverse_lazy("api_v3:company-alt_names-list", args=(user.company.id,))
        kwargs = dict(url=list_url, user=user, data=dict(name="test"))
        _ = self.create(**kwargs)
        self.assertEqual(user.company.altname_set.count(), 1)

    def test_create_as_company_admin_from_other_company(self):
        provider_user = provider_user_factory()
        builder_organization = builder_organization_factory()
        builder_user_factory(company=builder_organization, is_company_admin=True)

        self.assertEqual(builder_organization.altname_set.count(), 0)

        list_url = reverse_lazy("api_v3:company-alt_names-list", args=(builder_organization.id,))
        self.create(
            url=list_url,
            user=provider_user,
            data=dict(name="test"),
            expected_status=status.HTTP_403_FORBIDDEN,
        )
        self.assertEqual(builder_organization.altname_set.count(), 0)


class TestAltNameViewSet(ApiV3Tests):
    def test_retrieve_as_company_admin_member(self):
        utility_company = utility_organization_factory()
        user = builder_user_factory(company=utility_company, is_company_admin=True)

        self.assertEqual(utility_company.altname_set.count(), 0)
        alt_name = AltName.objects.create(company=utility_company, name="test")
        self.assertEqual(user.company.altname_set.count(), 1)

        retrieve_url = reverse_lazy("api_v3:alt_names-detail", args=(alt_name.id,))
        data = self.retrieve(url=retrieve_url, user=user)
        self.assertEqual(data["id"], alt_name.id)

    def test_update_as_company_admin_member(self):
        utility_company = utility_organization_factory()
        user = builder_user_factory(company=utility_company, is_company_admin=True)

        self.assertEqual(user.company.altname_set.count(), 0)
        alt_name = AltName.objects.create(company=user.company, name="test")
        self.assertEqual(user.company.altname_set.count(), 1)

        update_url = reverse_lazy("api_v3:alt_names-detail", args=(alt_name.id,))
        kwargs = dict(
            url=update_url,
            user=user,
            data=dict(
                name="test2",
                company=123,  # company must be ignored
            ),
            partial=True,
        )
        data = self.update(**kwargs)
        self.assertEqual(data["name"], "test2")

    def test_delete_as_company_admin_member(self):
        utility_company = utility_organization_factory()
        user = builder_user_factory(company=utility_company, is_company_admin=True)

        self.assertEqual(user.company.altname_set.count(), 0)
        alt_name = AltName.objects.create(company=user.company, name="test")
        self.assertEqual(user.company.altname_set.count(), 1)

        list_url = reverse_lazy("api_v3:alt_names-detail", args=(alt_name.id,))
        kwargs = dict(url=list_url, user=user)
        self.delete(**kwargs)
        self.assertEqual(user.company.altname_set.count(), 0)

    def test_retrieve_as_company_admin_from_other_company(self):
        provider_user = provider_user_factory()
        builder_organization = builder_organization_factory()
        builder_user_factory(company=builder_organization, is_company_admin=True)

        alt_name = AltName.objects.create(company=builder_organization, name="test")
        self.assertEqual(builder_organization.altname_set.count(), 1)

        url = reverse_lazy("api_v3:alt_names-detail", args=(alt_name.id,))
        self.retrieve(
            url=url,
            user=provider_user,
            expected_status=status.HTTP_404_NOT_FOUND,
        )
