"""mixins.py - Axis"""

__author__ = "Steven K"
__date__ = "9/20/21 13:38"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from axis.company.models import BuilderOrganization, Company
from axis.company.tests.factories import rater_organization_factory
from axis.core.tests.factories import (
    rater_admin_factory,
    provider_admin_factory,
    builder_user_factory,
    utility_admin_factory,
)
from axis.geographic.tests.factories import real_city_factory
from axis.relationship.models import Relationship
from axis.remrate_data.tests.factories import simulation_factory as rem_simulation_factory
from .factories import floorplan_factory

log = logging.getLogger(__name__)


class FloorplanTestMixin:
    @classmethod
    def setUpTestData(cls):
        from axis.subdivision.tests.factories import subdivision_factory

        cls.city = real_city_factory("McAlester", "OK")
        rater = rater_admin_factory(
            company__slug="rater", username="rateradmin", company__city=cls.city
        )
        provider = provider_admin_factory(
            company__slug="provider", username="provideradmin", company__city=cls.city
        )
        builder = builder_user_factory(company__slug="builder", company__city=cls.city)
        eep_sponsor = utility_admin_factory(
            company__is_eep_sponsor=True, company__slug="sponsor", company__city=cls.city
        )
        comps = [rater.company, provider.company, builder.company, eep_sponsor.company]
        Relationship.objects.create_mutual_relationships(*comps)

        rem_simulation = rem_simulation_factory(company=rater.company, air_conditioning_count=1)
        bldr = Company.objects.filter(company_type=Company.BUILDER_COMPANY_TYPE).get(slug="builder")

        subdivision = subdivision_factory(city=cls.city, builder_org=bldr)

        floorplan = floorplan_factory(
            owner=rater.company,
            remrate_target=rem_simulation,
            subdivision=subdivision,
        )

        # We are all friends
        Relationship.objects.create_mutual_relationships(
            rater.company, provider.company, builder.company, eep_sponsor.company
        )

        Relationship.objects.validate_or_create_relations_to_entity(
            subdivision, rater.company, [provider.company, builder.company, eep_sponsor.company]
        )

        # These were "shared"
        Relationship.objects.validate_or_create_relations_to_entity(floorplan, provider.company)
        Relationship.objects.validate_or_create_relations_to_entity(floorplan, builder.company)
        Relationship.objects.validate_or_create_relations_to_entity(floorplan, eep_sponsor.company)

        rater_organization_factory(slug="unrelated_rater", city=cls.city)
        rem_simulation_factory(company=rater.company)
