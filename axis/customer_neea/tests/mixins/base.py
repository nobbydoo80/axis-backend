"""base.py - Axis"""

__author__ = "Steven K"
__date__ = "7/20/21 09:20"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging


log = logging.getLogger(__name__)


class CustomerNEEABaseTestMixin:
    """Basic NEEA fixture tests"""

    @classmethod
    def setUpTestData(cls):
        from axis.geographic.tests.factories import real_city_factory
        from axis.company.models import SponsorPreferences, Company
        from axis.geographic.models import City, County
        from axis.core.tests.factories import utility_user_factory
        from axis.company.tests.factories import (
            utility_organization_factory,
            general_organization_factory,
        )
        from axis.core.tests.factories import (
            provider_admin_factory,
            eep_admin_factory,
            rater_admin_factory,
            builder_admin_factory,
            hvac_admin_factory,
        )
        from axis.relationship.models import Relationship
        from axis.customer_neea.models import PNWZone

        real_city_factory("Portland", "OR")
        cls.city = City.objects.get(county__name="Multnomah")
        for county in County.objects.filter(state="OR"):
            PNWZone.objects.create(county=county, heating_zone=1, cooling_zone=2)

        neea_user = eep_admin_factory(
            company__is_eep_sponsor=True,
            company__slug="neea",
            company__city=cls.city,
            company__name="NEEA",
        )

        cls.neea = neea_user.company

        cls.ber_user = provider_admin_factory(
            company__name="Building Efficiency Resources",
            company__slug="ber",
            company__city=cls.city,
        )

        cls.ea_user = rater_admin_factory(
            company__name="Earth Advantage",
            company__slug="earth_advantage",
            company__city=cls.city,
        )

        cls.builder = builder_admin_factory(
            company__name="Brentwood Homes",
            company__slug="brentwood_homes",
            company__city=cls.city,
        )

        cls.electricity_provider = utility_organization_factory(
            slug="pacific-power",
            is_customer=True,
            name="Pacific Power",
            city=cls.city,
            gas_provider=False,
            electricity_provider=True,
        )
        cls.gas_provider = utility_organization_factory(
            slug="nw-natural-gas",
            is_customer=True,
            name="NW Natural Gas",
            city=cls.city,
            gas_provider=True,
            electricity_provider=False,
        )

        # utility company users
        utility_user_factory(is_company_admin=True, company=cls.electricity_provider)
        utility_user_factory(is_company_admin=True, company=cls.electricity_provider)
        utility_user_factory(company=cls.electricity_provider)

        utility_user_factory(is_company_admin=True, company=cls.gas_provider)
        utility_user_factory(company=cls.gas_provider)
        utility_user_factory(company=cls.gas_provider)

        # utility company sponsors
        bpa_sponsor = general_organization_factory(slug="bpa", city=cls.city)

        SponsorPreferences.objects.get_or_create(
            sponsor=bpa_sponsor, sponsored_company=cls.electricity_provider
        )
        SponsorPreferences.objects.get_or_create(
            sponsor=bpa_sponsor, sponsored_company=cls.gas_provider
        )

        cls.hvac = hvac_admin_factory(
            company__name="Pyramid Heating & Cooling",
            company__slug="pyramid_hvac",
            company__city=cls.city,
        )

        # Two unknown companies who have no relationship to NEEA
        cls.unk_bldr = builder_admin_factory(
            company__name="Unk Builder",
            company__slug="unk_builder",
            company__city=cls.city,
        )
        cls.unk_hvac = hvac_admin_factory(
            company__name="Unk hvac",
            company__slug="unk_hvac",
            company__city=cls.city,
        )

        SponsorPreferences.objects.get_or_create(
            sponsor=cls.neea, sponsored_company=cls.ber_user.company
        )
        SponsorPreferences.objects.get_or_create(
            sponsor=cls.neea, sponsored_company=cls.ea_user.company
        )

        assert Company.objects.get(slug="ber").sponsors.count() == 1
        assert Company.objects.get(slug="earth_advantage").sponsors.count() == 1

        Relationship.objects.create_mutual_relationships(
            cls.neea,
            cls.ea_user.company,
            cls.ber_user.company,
            cls.electricity_provider,
            cls.gas_provider,
            cls.builder.company,
            cls.hvac.company,
        )

        Relationship.objects.create_mutual_relationships(
            cls.ea_user.company,
            cls.ber_user.company,
            cls.unk_bldr.company,
            cls.electricity_provider,
            cls.gas_provider,
            cls.unk_hvac.company,
        )

        assert cls.unk_bldr.company not in list(cls.neea.relationships.get_companies())
        assert cls.unk_hvac.company not in list(cls.neea.relationships.get_companies())
