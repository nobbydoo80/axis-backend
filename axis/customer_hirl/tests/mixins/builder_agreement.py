"""builder_agreement.py: """

__author__ = "Artem Hruzd"
__date__ = "01/22/2021 22:04"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.apps import apps
from axis.company.models import SponsorPreferences
from axis.company.tests.factories import provider_organization_factory, builder_organization_factory
from axis.core.tests.factories import provider_user_factory, builder_user_factory
from axis.geographic.tests.factories import real_city_factory

customer_hirl_app = apps.get_app_config("customer_hirl")


class BuilderAgreementHIRLMixin:
    """Fixture for Home View tests"""

    @classmethod
    def setUpTestData(cls):
        city = real_city_factory("Providence", "RI")
        hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG, city=city
        )
        provider_user_factory(
            first_name="NGBS",
            last_name="Admin",
            company=hirl_company,
            is_company_admin=True,
            username=customer_hirl_app.BUILDER_AGREEMENT_COUNTER_SIGNING_USERNAME,
        )

        builder_org = builder_organization_factory(city=city)
        company_admin_builder_user = builder_user_factory(
            is_company_admin=True, company=builder_org
        )

        SponsorPreferences.objects.create(sponsor=hirl_company, sponsored_company=builder_org)

        company_admin_builder_user.company.update_permissions()
