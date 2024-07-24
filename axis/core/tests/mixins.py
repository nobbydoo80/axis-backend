"""impersonate.py: """

__author__ = "Artem Hruzd"
__date__ = "03/09/2020 15:13"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.contrib.auth import get_user_model

from axis.core.tests.factories import (
    basic_user_factory,
    builder_admin_factory,
    builder_user_factory,
)
from axis.company.tests.factories import base_company_factory
from axis.geographic.tests.factories import real_city_factory

User = get_user_model()


class ImpersonateTestMixin:
    @classmethod
    def setUpTestData(cls):
        cls.city = real_city_factory("Vineland", "NJ")

        # pivotal support user
        pivotal_company = base_company_factory(
            slug="pivotal-energy-solutions",
            company_type="general",
            city=cls.city,
        )
        basic_user_factory(
            username="admin", is_staff=True, is_superuser=True, company=pivotal_company
        )

        # admin and non admin user of company
        builder_company = base_company_factory(company_type="builder", city=cls.city)
        builder_admin_factory(company=builder_company)
        builder_user_factory(company=builder_company)


class ApproveTensorAccountTestMixin:
    @classmethod
    def setUpTestData(cls):
        from axis.core.tests.factories import (
            basic_user_factory,
            builder_admin_factory,
            builder_user_factory,
        )
        from axis.company.tests.factories import base_company_factory

        cls.city = real_city_factory("Georgetown", "DE")

        # pivotal support user
        pivotal_company = base_company_factory(
            slug="pivotal-energy-solutions", company_type="general", city=cls.city
        )
        basic_user_factory(
            username="admin", is_staff=True, is_superuser=True, company=pivotal_company
        )

        # admin and non admin user of company
        builder_company = base_company_factory(company_type="builder", city=cls.city)
        builder_admin_factory(company=builder_company)
        builder_user_factory(company=builder_company)

        basic_user_factory(company=None, is_approved=False)
