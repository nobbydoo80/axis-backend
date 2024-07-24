"""fixturecompilers.py: Django subdivision"""


__author__ = "Steven Klass"
__date__ = "3/26/14 7:28 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]
import logging

from axis.company.tests.mixins import CompaniesAndUsersTestMixin
from axis.core.models import User
from axis.geographic.models import City

log = logging.getLogger(__name__)


class SubdivisionBase:
    @classmethod
    def create_intersection_address_kwargs(cls):
        return {
            "name": "Foobar",
            "city": City.objects.get(name="Gilbert").id,
            "cross_roads": "E Williams Field Rd & S Val Vista Dr",
        }

    @classmethod
    def update_intersection_address_kwargs(cls):
        return {
            "name": "BazFoo",
            "city": City.objects.get(name="Mesa").id,
            "cross_roads": "Main and Higley",
        }


class SubdivisionViewTestMixin(CompaniesAndUsersTestMixin, SubdivisionBase):
    include_company_types = ["rater", "hvac", "eep"]
    include_unrelated_companies = False

    @classmethod
    def setUpTestData(cls):
        super(SubdivisionViewTestMixin, cls).setUpTestData()

        from axis.geographic.tests.factories import real_city_factory
        from axis.core.tests.factories import builder_admin_factory
        from axis.eep_program.tests.factories import basic_eep_program_checklist_factory
        from axis.community.tests.factories import community_factory
        from axis.subdivision.tests.factories import subdivision_factory
        from axis.relationship.models import Relationship
        from axis.company.models import Company
        from axis.geographic.models import City

        from axis.geocoder.models import Geocode

        city = real_city_factory("Gilbert", "AZ")
        city2 = real_city_factory("Mesa", "AZ")

        rater = User.objects.get(company__company_type="rater", is_company_admin=True)
        hvac = User.objects.get(company__company_type="hvac", is_company_admin=True)
        eep = User.objects.get(company__company_type="eep", is_company_admin=True)
        builder = builder_admin_factory(
            username="noperm_builderadmin", company__is_customer=False, company__city=city
        )

        basic_eep_program_checklist_factory(no_close_dates=True, owner=eep.company)
        companies = [rater.company, hvac.company, eep.company, builder.company]
        Relationship.objects.create_mutual_relationships(*companies)

        subdivision = subdivision_factory(
            builder_org=Company.objects.filter(company_type=Company.BUILDER_COMPANY_TYPE).get(
                id=builder.company.id
            ),
            city=city,
        )

        for company in companies:
            Relationship.objects.validate_or_create_relations_to_entity(subdivision, company)

        create_addr = cls.create_intersection_address_kwargs()
        update_addr = cls.update_intersection_address_kwargs()

        create_kwargs = create_addr.copy()
        del create_kwargs["name"]
        community_1 = community_factory(city=city)

        for company in companies:
            Relationship.objects.validate_or_create_relations_to_entity(community_1, company)

        # This shows how to add a Geocode response object - Notice I created a "real" City..
        Geocode.objects.get_matches(raw_address=None, **create_addr)
        Geocode.objects.get_matches(raw_address=None, **update_addr)

        assert City.objects.all().count() == 2
        assert Company.objects.all().count() == 4
        assert Geocode.objects.get(
            raw_address__icontains="E Williams Field Rd & S Val Vista Dr, Gilbert, AZ"
        )


class SubdivisionManagerTestsMixin(SubdivisionBase):
    @classmethod
    def setUpTestData(cls):
        from axis.geographic.tests.factories import real_city_factory
        from axis.core.tests.factories import (
            hvac_admin_factory,
            rater_admin_factory,
            eep_admin_factory,
            builder_admin_factory,
        )
        from axis.eep_program.tests.factories import basic_eep_program_checklist_factory
        from axis.company.tests.factories import builder_organization_factory
        from axis.community.tests.factories import community_factory
        from axis.subdivision.tests.factories import subdivision_factory
        from axis.relationship.models import Relationship
        from axis.company.models import Company
        from axis.geographic.models import City
        from axis.subdivision.models import EEPProgramSubdivisionStatus
        from axis.subdivision.tests.test_views import SubdivisionViewTestMixin
        from axis.geocoder.models import Geocode

        city = real_city_factory("Gilbert", "AZ")
        city2 = real_city_factory("Mesa", "AZ")

        rater = rater_admin_factory(username="rateradmin", company__city=city)
        hvac = hvac_admin_factory(username="hvacadmin", company__city=city)
        eep = eep_admin_factory(username="eepadmin", company__city=city)
        builder = builder_admin_factory(
            username="noperm_builderadmin", company__is_customer=False, company__city=city
        )
        company = builder_organization_factory(name="Test co", city=city2)
        another_builder = builder_admin_factory(username="noperm_builderadmin2", company=company)

        eep_program = basic_eep_program_checklist_factory(no_close_dates=True, owner=eep.company)
        companies = [rater.company, hvac.company, eep.company, builder.company]
        Relationship.objects.create_mutual_relationships(*companies)

        subdivision = subdivision_factory(
            builder_org=Company.objects.filter(company_type=Company.BUILDER_COMPANY_TYPE).get(
                id=builder.company.id
            ),
            city=city,
        )

        eep_sub = subdivision_factory(
            name="sub1",
            builder_org=Company.objects.filter(company_type=Company.BUILDER_COMPANY_TYPE).get(
                id=another_builder.company.id
            ),
            city=city,
        )
        subdivision_factory(
            name="sub2",
            builder_org=Company.objects.filter(company_type=Company.BUILDER_COMPANY_TYPE).get(
                id=builder.company.id
            ),
            city=city,
        )

        kwargs = {"subdivision": eep_sub, "eep_program": eep_program, "company": eep.company}
        EEPProgramSubdivisionStatus.objects.create(**kwargs)

        for company in companies:
            Relationship.objects.validate_or_create_relations_to_entity(subdivision, company)

        create_addr = SubdivisionViewTestMixin().create_intersection_address_kwargs()
        update_addr = SubdivisionViewTestMixin().update_intersection_address_kwargs()

        create_kwargs = create_addr.copy()
        create_kwargs["city"] = city
        del create_kwargs["name"]
        community_1 = community_factory(**create_kwargs)

        for company in companies:
            Relationship.objects.validate_or_create_relations_to_entity(community_1, company)

        # This shows how to add a Geocode response object - Notice I created a "real" City..
        Geocode.objects.get_matches(raw_address=None, **create_addr)
        Geocode.objects.get_matches(raw_address=None, **update_addr)

        assert City.objects.all().count() == 2
        assert Company.objects.all().count() == 5
        assert Geocode.objects.get(
            raw_address__icontains="E Williams Field Rd & S Val Vista Dr, Gilbert, AZ"
        )
