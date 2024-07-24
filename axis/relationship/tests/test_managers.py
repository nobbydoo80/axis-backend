"""test_managers.py: """

__author__ = "Artem Hruzd"
__date__ = "11/04/2021 1:05 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from axis.company.tests.factories import (
    builder_organization_factory,
    provider_organization_factory,
    developer_organization_factory,
)
from axis.core.tests.testcases import AxisTestCase
from axis.relationship.models import Relationship
from axis.company.models import Company


class TestRelationshipManagers(AxisTestCase):
    def test_create_mutual_relationships_with_multiple_companies(self):
        builder_company = builder_organization_factory()
        provider_company = provider_organization_factory()
        developer_company = developer_organization_factory()

        available_companies = [builder_company, provider_company, developer_company]
        Relationship.objects.create_mutual_relationships(*available_companies)

        self.assertEqual(builder_company.relationships.count(), 2)
        self.assertEqual(provider_company.relationships.count(), 2)
        self.assertEqual(developer_company.relationships.count(), 2)

    def test_create_mutual_relationships_with_strict_company_types(self):
        builder_organization_factory()
        builder_company = Company.objects.get(company_type=Company.BUILDER_COMPANY_TYPE)
        provider_organization_factory()
        provider_company = Company.objects.get(company_type=Company.PROVIDER_COMPANY_TYPE)
        developer_organization_factory()
        developer_company = Company.objects.get(company_type=Company.DEVELOPER_COMPANY_TYPE)

        available_companies = [builder_company, provider_company, developer_company]
        Relationship.objects.create_mutual_relationships(*available_companies)

        self.assertEqual(builder_company.relationships.count(), 2)
        self.assertEqual(provider_company.relationships.count(), 2)
        self.assertEqual(developer_company.relationships.count(), 2)

    def test_create_mutual_relationships_with_empty_list(self):
        available_companies = []
        Relationship.objects.create_mutual_relationships(*available_companies)
