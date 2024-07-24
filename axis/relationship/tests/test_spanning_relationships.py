"""test_spanning_relationships.py: Django relationships"""

import logging

from django.contrib.auth import get_user_model

from axis.core.tests.client import AxisClient
from axis.core.tests.testcases import AxisTestCase
from ..models import Relationship
from ..utils import (
    create_or_update_spanning_relationships,
    AUTO_ASSIGNMENT_MAP,
    get_auto_assigned_companies,
)

__author__ = "Steven Klass"
__date__ = "9/1/15 8:51 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)
User = get_user_model()


class RelationshipSpanningTests(AxisTestCase):
    """Test out Relationships and Spanning Relationships"""

    client_class = AxisClient

    @classmethod
    def setUpTestData(cls):
        from axis.geographic.tests.factories import city_factory
        from axis.geographic.models import City
        from axis.core.tests.factories import non_company_user_factory
        from axis.company.tests.factories import builder_organization_factory
        from axis.company.strings import COMPANY_TYPES
        from axis.community.models import Community
        from axis.community.tests.factories import community_factory
        from axis.subdivision.models import Subdivision
        from axis.subdivision.tests.factories import subdivision_factory

        # We can't delete this imports because of eval function on line 110
        from axis.core.tests.factories import (
            rater_user_factory,
            rater_admin_factory,
            provider_user_factory,
            provider_admin_factory,
            eep_user_factory,
            eep_admin_factory,
            builder_user_factory,
            builder_admin_factory,
            utility_user_factory,
            utility_admin_factory,
            hvac_user_factory,
            hvac_admin_factory,
            qa_user_factory,
            qa_admin_factory,
            general_user_factory,
            general_admin_factory,
            general_super_user_factory,
            non_company_user_factory,
        )
        from axis.company.tests.factories import (
            rater_organization_factory,
            provider_organization_factory,
            eep_organization_factory,
            builder_organization_factory,
            utility_organization_factory,
            hvac_organization_factory,
            qa_organization_factory,
            general_organization_factory,
        )

        from axis.company.models import Company, BuilderOrganization

        from axis.eep_program.tests.factories import basic_eep_program_factory
        from axis.eep_program.models import EEPProgram

        from axis.home.tests.factories import custom_home_factory
        from axis.home.models import Home

        from axis.floorplan.tests.factories import basic_custom_home_floorplan_factory
        from axis.floorplan.models import Floorplan

        from axis.relationship.models import Relationship

        cls.city = city = city_factory(name="Gilbert", county__name="Maricopa", county__state="AZ")
        base_kwargs = {}

        companies = {}
        for company_type in dict(COMPANY_TYPES).keys():
            if company_type not in [
                "builder",
                "eep",
                "provider",
                "rater",
                "general",
                "utility",
                "qa",
            ]:
                continue
            company_factory = eval("{}_organization_factory".format(company_type))

            kw = base_kwargs.copy()
            if company_type == "eep":
                # Add in ETO and APS
                kw["company__slug"] = "eto"
                kw["company__name"] = "ETO"
                kw["company__is_eep_sponsor"] = True

            if company_type == "utility":
                kw["company__slug"] = "srp"
                kw["company__name"] = "SRP"
                kw["company__is_eep_sponsor"] = True
                kw["company__electricity_provider"] = True
                kw["company__gas_provider"] = False
                admin_factory = eval("{}_admin_factory".format(company_type))
                srp_admin = admin_factory(
                    username="{}srpadmin".format(company_type), company__city=city, **kw
                )

                kw["company__slug"] = "aps"
                kw["company__name"] = "APS"
                kw["company__is_eep_sponsor"] = True

            if company_type == "qa":
                kw["company__slug"] = "csg-qa"

            if company_type == "general":
                unrelated = company_factory(
                    name="unrelated_non_customer_{}".format(company_type),
                    city=city,
                    is_customer=False,
                )
                # This ensures perms aren't established - no company..
                no_perm_user = non_company_user_factory(username="noperm_user", **kw)
                no_perm_user.company = unrelated
                no_perm_user.save()
                continue

            admin_factory = eval("{}_admin_factory".format(company_type))
            admin = admin_factory(username="{}admin".format(company_type), company__city=city, **kw)
            companies[company_type] = admin.company

        builder_org = Company.objects.get(id=companies["builder"].id)
        builder_org2 = builder_organization_factory(city=city, name="builder_2", **base_kwargs)

        _comps = list(companies.values()) + [builder_org2, srp_admin.company]
        Relationship.objects.create_mutual_relationships(*_comps)

        # perms = list(set([x.split(".")[-1].split("_")[0] for x in list(no_perm_user.get_all_permissions()) if
        #                   not x.startswith("messaging")]))
        # assert perms == ['view'], "Non-Customers now have {!r} perms - they should only have view".format(perms)

        community = community_factory(city=cls.city, **base_kwargs)
        subdivision = subdivision_factory(
            city=cls.city, community=community, builder_org=builder_org, **base_kwargs
        )
        subdivision_factory(
            city=cls.city, builder_org=builder_org, name="no_community", **base_kwargs
        )

        eep_program = basic_eep_program_factory(
            name="ETO", slug="eto", owner=companies.get("eep"), no_close_dates=True, **base_kwargs
        )

        eep_program = basic_eep_program_factory(
            name="APS",
            slug="aps-energy-star-v3-2014",
            owner=companies.get("utility"),
            no_close_dates=True,
            **base_kwargs,
        )

        home = custom_home_factory(city=city, builder_org=builder_org, **base_kwargs)

        floorplan = basic_custom_home_floorplan_factory(owner=companies["rater"])

        # Assertions
        assert Company.objects.all().count() == 9, "Company count mismatch {}".format(
            Company.objects.count()
        )
        assert User.objects.all().count() == 8, "User count mismatch {}".format(
            User.objects.count()
        )

        for company_type in companies:
            assert (
                Community.objects.filter_by_company(companies[company_type]).count() == 0
            ), "{} has Community Rels".format(company_type)
            rels = Subdivision.objects.filter_by_company(companies[company_type]).count()
            if company_type == "builder":
                assert rels == 2, "{} has {} Subdivision Rels".format(company_type, rels)
            else:
                assert rels == 0, "{} has {} Subdivision Rels".format(company_type, rels)
            assert unrelated not in Company.objects.filter_by_company(companies[company_type])

        assert Community.objects.all().count() == 1, "Community {}".format(
            Community.objects.count()
        )
        assert Subdivision.objects.all().count() == 2, "Subdivisions {}".format(
            Subdivision.objects.all()
        )
        assert City.objects.all().count() == 1, "Cities {}".format(City.objects.all())
        assert EEPProgram.objects.all().count() == 2, "Programs {}".format(EEPProgram.objects.all())
        assert Home.objects.all().count() == 1, "Homes {}".format(Home.objects.all())
        assert Floorplan.objects.all().count() == 1, "Floorplans {}".format(Floorplan.objects.all())

        # assert EEPProgramHomeStatus.objects.filter_by_company(companies['provider']).count() == 4; "Provider Relationships.."
        # assert EEPProgramHomeStatus.objects.filter(pct_complete__gte=99.9, certification_date__isnull=True).count() == 1

    def setUp(self):
        from axis.company.models import Company
        from axis.community.models import Community
        from axis.subdivision.models import Subdivision
        from axis.floorplan.models import Floorplan
        from axis.eep_program.models import EEPProgram
        from axis.home.models import Home

        assert Company.objects.all().count() == 9, "Companies {}".format(
            Company.objects.all().count()
        )
        self.builder_org = Company.objects.exclude(name="builder_2").get(company_type="builder")
        self.builder_org2 = Company.objects.get(company_type="builder", name="builder_2")
        self.eep_org = Company.objects.get(company_type="eep", slug="eto")
        self.provider_org = Company.objects.get(company_type="provider")
        self.rater_org = Company.objects.get(company_type="rater")
        self.unrelated_org = Company.objects.get(company_type="general")
        self.utility_org = Company.objects.get(company_type="utility", slug="srp")
        self.csg_qa = Company.objects.get(company_type="qa")

        self.community = Community.objects.all().get()
        self.subdivision = Subdivision.objects.get(community__isnull=True)
        self.floorplan = Floorplan.objects.all().get()
        self.eto_program = EEPProgram.objects.get(slug="eto")
        self.aps_program = EEPProgram.objects.get(slug__icontains="aps")
        self.home = Home.objects.all().get()

    def test_company_input_types(self):
        """This simply tests the various way of inputing companies"""
        from axis.company.models import Company
        from axis.community.models import Community

        create_or_update_spanning_relationships(None, self.subdivision)
        self.assertEqual(self.subdivision.relationships.count(), 1)

        create_or_update_spanning_relationships(self.rater_org, self.community)
        self.assertEqual(Community.objects.filter_by_company(self.rater_org).count(), 1)
        self.assertEqual(self.community.relationships.count(), 1)

        create_or_update_spanning_relationships(
            [self.provider_org, self.unrelated_org], self.community
        )
        self.assertEqual(self.community.relationships.count(), 3)

        companies = Company.objects.filter(id__in=[self.eep_org.id, self.utility_org.id])
        create_or_update_spanning_relationships(companies, self.community)
        self.assertEqual(self.community.relationships.count(), 5)

    def test_basic_span(self):
        """This simply verifies the normal use case.  Two companies have relationships with each other
        This will simply propagate the companies down"""

        create_or_update_spanning_relationships(self.rater_org, self.community)
        self.assertEqual(self.community.relationships.count(), 1)

        self.subdivision.community = self.community

        create_or_update_spanning_relationships(self.provider_org, self.subdivision)
        self.assertEqual(self.subdivision.relationships.count(), 3)

        reported = list(self.subdivision.relationships.values_list("company", flat=True))
        actual = [self.builder_org.id, self.provider_org.id, self.rater_org.id]
        self.assertEqual(set(reported), set(actual))

    def test_unrelated_span(self):
        """This should not propagate the unrelated company down as there is no relationship in place"""

        create_or_update_spanning_relationships(
            [self.rater_org, self.unrelated_org], self.community
        )
        self.assertEqual(self.community.relationships.count(), 2)

        self.subdivision.community = self.community

        create_or_update_spanning_relationships(self.provider_org, self.subdivision)
        self.assertEqual(self.subdivision.relationships.count(), 3)

        reported = list(self.subdivision.relationships.values_list("company", flat=True))
        actual = [self.builder_org.id, self.provider_org.id, self.rater_org.id]
        self.assertEqual(set(reported), set(actual))

    def test_parent_implied_span(self):
        """This should ensure that if a relation is not owned (implied) that it carries over."""

        create_or_update_spanning_relationships(self.rater_org, self.community)
        self.assertEqual(self.community.relationships.count(), 1)

        self.community.relationships.update(is_owned=False)
        self.assertEqual(self.community.relationships.filter(is_owned=False).count(), 1)

        self.subdivision.community = self.community

        create_or_update_spanning_relationships(self.provider_org, self.subdivision)
        reported = list(self.subdivision.relationships.values_list("company", flat=True))
        actual = [self.builder_org.id, self.provider_org.id, self.rater_org.id]
        self.assertEqual(set(reported), set(actual))

        implied = self.subdivision.relationships.filter(is_owned=False).get()
        self.assertEqual(implied.company.id, self.rater_org.id)

    def test_parent_is_attached_span(self):
        """This should ensure that parent flags (is_viewable, is_attached) carry over"""

        create_or_update_spanning_relationships(self.provider_org, self.community)

        is_not_attached = self.community.relationships.first()
        is_not_attached.is_attached = False
        is_not_attached.save()
        self.assertEqual(self.community.relationships.filter(is_attached=False).count(), 1)

        self.subdivision.community = self.community

        create_or_update_spanning_relationships(self.eep_org, self.subdivision)
        reported = list(self.subdivision.relationships.values_list("company", flat=True))
        actual = [self.builder_org.id, self.provider_org.id, self.eep_org.id]
        self.assertEqual(set(reported), set(actual))

        sub_not_attached = self.subdivision.relationships.filter(is_attached=False).get()
        self.assertEqual(sub_not_attached.company.id, is_not_attached.company.id)

    def test_parent_is_viewable_span(self):
        """This should ensure that parent flags (is_viewable, is_attached) carry over"""

        create_or_update_spanning_relationships(self.provider_org, self.community)

        is_not_viewable = self.community.relationships.first()
        is_not_viewable.is_viewable = False
        is_not_viewable.save()
        self.assertEqual(self.community.relationships.filter(is_viewable=False).count(), 1)

        self.subdivision.community = self.community

        create_or_update_spanning_relationships(self.eep_org, self.subdivision)
        reported = list(self.subdivision.relationships.values_list("company", flat=True))
        actual = [self.builder_org.id, self.provider_org.id, self.eep_org.id]
        self.assertEqual(set(reported), set(actual))

        sub_not_viewable = self.subdivision.relationships.filter(is_viewable=False).get()
        self.assertEqual(sub_not_viewable.company.id, is_not_viewable.company.id)

    def test_parent_exclude_subdivision_builders_span(self):
        """This should ensure that parent flags (is_viewable, is_attached) carry over"""

        create_or_update_spanning_relationships(self.builder_org2, self.community)

        self.subdivision.community = self.community

        create_or_update_spanning_relationships(self.eep_org, self.subdivision)

        reported = list(self.subdivision.relationships.values_list("company", flat=True))
        actual = [self.builder_org.id, self.eep_org.id]
        self.assertEqual(set(reported), set(actual))

    def test_home_waterfall_span(self):
        """This will validate the waterfall from a community to subdiivison to a home actually works."""

        actual = [self.builder_org.id, self.rater_org.id]

        create_or_update_spanning_relationships(
            [
                self.builder_org2,
                self.rater_org,
            ],
            self.community,
        )

        self.subdivision.community = self.community
        create_or_update_spanning_relationships(None, self.subdivision)

        reported = list(self.subdivision.relationships.values_list("company", flat=True))
        self.assertEqual(set(reported), set(actual))

        self.home.subdivision = self.subdivision
        create_or_update_spanning_relationships(None, self.home)

        reported = list(self.home.relationships.values_list("company", flat=True))
        self.assertEqual(set(reported), set(actual))

    def test_homestatus_waterfall_span(self):
        """This will validate the waterfall from a community to subdiivison to a home actually works."""
        from axis.home.models import EEPProgramHomeStatus

        actual = [self.builder_org.id, self.rater_org.id]

        create_or_update_spanning_relationships(
            [
                self.builder_org2,
                self.rater_org,
            ],
            self.community,
        )

        self.subdivision.community = self.community
        create_or_update_spanning_relationships(None, self.subdivision)
        reported = list(self.subdivision.relationships.values_list("company", flat=True))
        self.assertEqual(set(reported), set(actual))

        self.home.subdivision = self.subdivision
        create_or_update_spanning_relationships(None, self.home)
        reported = list(self.home.relationships.values_list("company", flat=True))
        self.assertEqual(set(reported), set(actual))

        status = EEPProgramHomeStatus.objects.create(
            company=self.rater_org,
            floorplan=self.floorplan,
            eep_program=self.aps_program,
            home=self.home,
        )

        create_or_update_spanning_relationships(None, status)

        reported = list(self.home.relationships.values_list("company", flat=True))

        actual = [self.builder_org.id, self.rater_org.id, self.aps_program.owner.id]
        self.assertEqual(set(reported), set(actual))

    def test_homestatus_implied_input(self):
        """When we assign a home status the program owner should become an implied company"""
        from axis.home.models import EEPProgramHomeStatus

        status = EEPProgramHomeStatus.objects.create(
            company=self.rater_org,
            floorplan=self.floorplan,
            eep_program=self.aps_program,
            home=self.home,
        )
        create_or_update_spanning_relationships(None, status)
        reported = list(self.home.relationships.values_list("company", flat=True))
        actual = [self.builder_org.id, self.rater_org.id, self.aps_program.owner.id]
        self.assertEqual(set(reported), set(actual))

        self.assertEqual(self.home.relationships.get(company__slug="aps").is_owned, False)

    def test_homestatus_implied_auto_add_direct_relationships(self):
        """When we assign a program to a home the owner should become an implied
        company UNLESS auto_add_direct_relationships is True"""
        from axis.home.models import EEPProgramHomeStatus

        aps = self.aps_program.owner
        aps.auto_add_direct_relationships = True
        aps.save()

        status = EEPProgramHomeStatus.objects.create(
            company=self.rater_org,
            floorplan=self.floorplan,
            eep_program=self.aps_program,
            home=self.home,
        )
        create_or_update_spanning_relationships(None, status)
        reported = list(self.home.relationships.values_list("company", flat=True))
        actual = [self.builder_org.id, self.rater_org.id, self.aps_program.owner.id]
        self.assertEqual(set(reported), set(actual))

        self.assertEqual(self.home.relationships.get(company__slug="aps").is_owned, True)

    def test_forced_direct_relationships(self):
        """When we use the AUTO_ASSIGNMENT_MAP we can automatically assign direct relationships"""
        from axis.home.models import EEPProgramHomeStatus

        status = EEPProgramHomeStatus.objects.create(
            company=self.rater_org,
            floorplan=self.floorplan,
            eep_program=self.eto_program,
            home=self.home,
        )

        create_or_update_spanning_relationships(None, status)

        reported = list(self.home.relationships.values_list("company", flat=True))
        actual = [self.builder_org.id, self.rater_org.id, self.eto_program.owner.id, self.csg_qa.id]

        self.assertEqual(set(reported), set(actual))

        self.assertEqual(self.home.relationships.get(company__slug="eto").is_owned, True)
        self.assertEqual(self.home.relationships.get(company__slug="csg-qa").is_owned, True)

    def test_utility_hints_waterfall(self):
        """Verify the utility hints are getting passed down"""
        from ..utils import modify_relationships

        actual = [self.builder_org.id, self.utility_org.id]

        create_or_update_spanning_relationships(
            [self.builder_org2, self.utility_org], self.community
        )

        self.subdivision.community = self.community
        create_or_update_spanning_relationships(None, self.subdivision)

        reported = list(self.subdivision.relationships.values_list("company", flat=True))
        self.assertEqual(set(reported), set(actual))

        # This will set the initial hint declaration
        modify_relationships(
            self.subdivision,
            {"electric_utility": self.utility_org, "builder": self.builder_org},
            User.objects.get(company=self.builder_org),
        )

        self.assertEqual(self.utility_org, self.subdivision.get_electric_company())
        self.assertEqual(None, self.subdivision.get_gas_company())

        self.home.subdivision = self.subdivision
        create_or_update_spanning_relationships(None, self.home)
        reported = list(self.home.relationships.values_list("company", flat=True))
        self.assertEqual(set(reported), set(actual))

        self.assertEqual(self.utility_org, self.home.get_electric_company())
        self.assertEqual(None, self.home.get_gas_company())

    def test_auto_deletion(self):
        """Make sure this will catch any deletion items"""
        from axis.home.models import EEPProgramHomeStatus

        status = EEPProgramHomeStatus.objects.create(
            company=self.rater_org,
            floorplan=self.floorplan,
            eep_program=self.aps_program,
            home=self.home,
        )

        # We add in a rogue SRP utility
        create_or_update_spanning_relationships(self.utility_org, status)

        reported = list(self.home.relationships.values_list("company", flat=True))
        actual = [self.builder_org.id, self.rater_org.id, self.aps_program.owner.id]
        self.assertEqual(set(reported), set(actual))

    def test_flooplan_basic(self):
        """This will loosely test floorplan spanning"""

        create_or_update_spanning_relationships(None, self.floorplan)
        reported = list(self.floorplan.relationships.values_list("company", flat=True))

        self.assertEqual(set(reported), set([self.floorplan.owner.id]))

    def test_flooplan_spanning(self):
        """This will loosely test floorplan spanning"""

        from axis.home.models import EEPProgramHomeStatus

        actual = [self.builder_org.id, self.rater_org.id, self.aps_program.owner.id]

        create_or_update_spanning_relationships(
            [
                self.builder_org2,
                self.rater_org,
            ],
            self.community,
        )

        self.subdivision.community = self.community
        self.home.subdivision = self.subdivision

        status = EEPProgramHomeStatus.objects.create(
            company=self.rater_org,
            floorplan=self.floorplan,
            eep_program=self.aps_program,
            home=self.home,
        )

        create_or_update_spanning_relationships(None, status)
        create_or_update_spanning_relationships(None, self.floorplan)
        reported = list(self.floorplan.relationships.values_list("company", flat=True))

        self.assertEqual(set(reported), set(actual))

    def test_push_down_relationships(self):
        """This verifies that when you push down relationships indirect relationships push down."""
        from ..models import Relationship

        community_filter_by_company = self.community._meta.model.objects.filter_by_company
        subdivision_filter_by_company = self.subdivision._meta.model.objects.filter_by_company
        home_filter_by_company = self.home._meta.model.objects.filter_by_company

        self.assertEqual(
            community_filter_by_company(self.rater_org, id=self.community.id).count(), 0
        )
        self.assertEqual(
            community_filter_by_company(
                self.rater_org, id=self.community.id, show_attached=1
            ).count(),
            0,
        )
        self.assertEqual(
            subdivision_filter_by_company(self.rater_org, id=self.subdivision.id).count(), 0
        )
        self.assertEqual(
            subdivision_filter_by_company(
                self.rater_org, id=self.subdivision.id, show_attached=1
            ).count(),
            0,
        )
        self.assertEqual(home_filter_by_company(self.rater_org, id=self.home.id).count(), 0)
        self.assertEqual(
            home_filter_by_company(self.rater_org, id=self.home.id, show_attached=1).count(), 0
        )

        Relationship.objects.validate_or_create_relations_to_entity(
            self.home, self.provider_org, self.rater_org
        )
        Relationship.objects.validate_or_create_relations_to_entity(
            self.subdivision, self.provider_org, self.rater_org
        )
        Relationship.objects.validate_or_create_relations_to_entity(
            self.community, self.provider_org, self.rater_org
        )

        self.assertEqual(
            community_filter_by_company(self.rater_org, id=self.community.id).count(), 0
        )
        self.assertEqual(
            community_filter_by_company(
                self.rater_org, id=self.community.id, show_attached=1
            ).count(),
            1,
        )
        self.assertEqual(
            subdivision_filter_by_company(self.rater_org, id=self.subdivision.id).count(), 0
        )
        self.assertEqual(
            subdivision_filter_by_company(
                self.rater_org, id=self.subdivision.id, show_attached=1
            ).count(),
            1,
        )
        self.assertEqual(home_filter_by_company(self.rater_org, id=self.home.id).count(), 0)
        self.assertEqual(
            home_filter_by_company(self.rater_org, id=self.home.id, show_attached=1).count(), 1
        )

        self.home.subdivision = self.subdivision
        self.home.save()
        self.subdivision.community = self.community
        self.subdivision.save()

        create_or_update_spanning_relationships(self.rater_org, self.community, push_down=True)

        self.assertEqual(
            community_filter_by_company(self.rater_org, id=self.community.id).count(), 1
        )
        self.assertEqual(
            community_filter_by_company(
                self.rater_org, id=self.community.id, show_attached=1
            ).count(),
            1,
        )
        self.assertEqual(
            subdivision_filter_by_company(self.rater_org, id=self.subdivision.id).count(), 1
        )
        self.assertEqual(
            subdivision_filter_by_company(
                self.rater_org, id=self.subdivision.id, show_attached=1
            ).count(),
            1,
        )
        self.assertEqual(home_filter_by_company(self.rater_org, id=self.home.id).count(), 1)
        self.assertEqual(
            home_filter_by_company(self.rater_org, id=self.home.id, show_attached=1).count(), 1
        )

    def test_push_down_relationships_verified(self):
        """This verifies that when you don't down relationships they push down."""
        from ..models import Relationship

        community_filter_by_company = self.community._meta.model.objects.filter_by_company
        subdivision_filter_by_company = self.subdivision._meta.model.objects.filter_by_company
        home_filter_by_company = self.home._meta.model.objects.filter_by_company

        Relationship.objects.validate_or_create_relations_to_entity(
            self.home, self.provider_org, self.rater_org
        )
        Relationship.objects.validate_or_create_relations_to_entity(
            self.subdivision, self.provider_org, self.rater_org
        )
        Relationship.objects.validate_or_create_relations_to_entity(
            self.community, self.provider_org, self.rater_org
        )

        self.home.subdivision = self.subdivision
        self.home.save()
        self.subdivision.community = self.community
        self.subdivision.save()

        # log.error("\n\n\n HERE \n\n")

        create_or_update_spanning_relationships(self.rater_org, self.community, push_down=False)

        self.assertEqual(
            community_filter_by_company(self.rater_org, id=self.community.id).count(), 1
        )
        self.assertEqual(
            community_filter_by_company(
                self.rater_org, id=self.community.id, show_attached=1
            ).count(),
            1,
        )
        self.assertEqual(
            subdivision_filter_by_company(self.rater_org, id=self.subdivision.id).count(), 0
        )
        self.assertEqual(
            subdivision_filter_by_company(
                self.rater_org, id=self.subdivision.id, show_attached=1
            ).count(),
            1,
        )
        self.assertEqual(home_filter_by_company(self.rater_org, id=self.home.id).count(), 0)
        self.assertEqual(
            home_filter_by_company(self.rater_org, id=self.home.id, show_attached=1).count(), 1
        )

    def test_get_auto_assigned_companies_auto_assignment_map_basic(self):
        """This verifies that if you have a program slug and list some programs these will
        automatically get assigned."""
        from axis.company.models import Company
        from axis.eep_program.models import EEPProgram
        from axis.home.models import EEPProgramHomeStatus

        self.eep_org.slug = "neea"
        self.eep_org.save()
        self.assertTrue(Company.objects.filter(slug="neea").exists())

        self.provider_org.slug = "clearesult-qa"
        self.provider_org.save()
        self.assertTrue(Company.objects.filter(slug="clearesult-qa").exists())

        self.eto_program.slug = "utility-incentive-v1-single-family"
        self.eto_program.save()
        self.assertTrue(
            EEPProgram.objects.filter(slug="utility-incentive-v1-single-family").exists()
        )

        self.assertIn("utility-incentive-v1-single-family", AUTO_ASSIGNMENT_MAP)

        status = EEPProgramHomeStatus.objects.create(
            company=self.rater_org,
            floorplan=self.floorplan,
            eep_program=self.eto_program,
            home=self.home,
        )

        direct, implied = get_auto_assigned_companies(
            EEPProgramHomeStatus.objects.filter(id=status.pk)
        )

        self.assertEqual(set(direct), {"neea", "clearesult-qa", status.company.slug})
        self.assertEqual(set(implied), set())

        create_or_update_spanning_relationships(self.rater_org, status)
        relations = self.home.relationships.all().values_list("company__slug", flat=True)
        expected = {"neea", "clearesult-qa", status.company.slug, self.home.get_builder().slug}
        self.assertEqual(set(relations), expected)

    def test_get_auto_assigned_companies_auto_assignment_map_qa_requirements(self):
        """This verifies if you have a qa requirement it will be respected"""
        from axis.company.models import Company
        from axis.eep_program.models import EEPProgram
        from axis.home.models import Home, EEPProgramHomeStatus
        from axis.qa.models import QARequirement

        self.eep_org.slug = "neea"
        self.eep_org.save()
        self.assertTrue(Company.objects.filter(slug="neea").exists())

        self.provider_org.slug = "clearesult-qa"
        self.provider_org.save()
        self.assertTrue(Company.objects.filter(slug="clearesult-qa").exists())

        self.utility_org.slug = "pacific-power"
        self.utility_org.save()
        self.assertTrue(Company.objects.filter(slug="pacific-power").exists())

        self.csg_qa.slug = "pac_power_qa"
        self.csg_qa.save()
        self.assertTrue(Company.objects.filter(slug="pac_power_qa").exists())

        # Add a the normal QA Requirement
        QARequirement.objects.create(
            eep_program=self.eto_program,
            type="file",
            gate_certification=True,
            qa_company=self.provider_org,
            coverage_pct=0,
        )

        # Add a requirement that when the utility is used this QA program goes on it.
        requirement = QARequirement.objects.create(
            eep_program=self.eto_program,
            type="file",
            gate_certification=True,
            qa_company=self.csg_qa,
            coverage_pct=0,
        )
        requirement.required_companies.add(self.utility_org)
        self.assertEqual(requirement.required_companies.count(), 1)

        self.eto_program.slug = "utility-incentive-v1-single-family"
        self.eto_program.save()
        self.assertTrue(
            EEPProgram.objects.filter(slug="utility-incentive-v1-single-family").exists()
        )

        self.assertIn("utility-incentive-v1-single-family", AUTO_ASSIGNMENT_MAP)

        Home.objects.filter(id=self.home.id).update(state="WA")
        self.home = Home.objects.get(id=self.home.id)
        self.assertTrue(Home.objects.filter(state="WA").exists())

        status = EEPProgramHomeStatus.objects.create(
            company=self.rater_org,
            floorplan=self.floorplan,
            eep_program=self.eto_program,
            home=self.home,
        )
        self.assertTrue(EEPProgram.objects.filter(home__state="WA").exists())

        create_or_update_spanning_relationships(self.rater_org, status)

        relations = self.home.relationships.all().values_list("company__slug", flat=True)
        expected = {"neea", "clearesult-qa", status.company.slug, self.home.get_builder().slug}
        self.assertEqual(set(relations), expected)

        # Now lets add the utility.
        # When we add a utility and then run create_or_update_spanning

        Relationship.objects.validate_or_create_relations_to_entity(self.home, self.utility_org)
        relations = self.home.relationships.all().values_list("company__slug", flat=True)
        expected.add(self.utility_org.slug)
        self.assertEqual(set(relations), expected)

        direct, implied = get_auto_assigned_companies(
            EEPProgramHomeStatus.objects.filter(id=status.pk)
        )

        self.assertEqual(
            set(direct), {"neea", "clearesult-qa", status.company.slug, self.csg_qa.slug}
        )
        self.assertEqual(set(implied), set())

        # If you see an issue dig in here.
        # from django.db.models import Count
        # req = QARequirement.objects.filter_for_add(status.home, user=None).annotate(
        #     n_required_companies=Count('required_companies')).filter(
        #     eep_program=status.eep_program_id, n_required_companies__gt=0)
        # self.assertEqual(req.count(), 1)
        # self.assertEqual(req.get(), requirement)

        # Finally verify the relationship is created.
        create_or_update_spanning_relationships(self.rater_org, status)
        relations = self.home.relationships.all().values_list("company__slug", flat=True)
        expected.add(self.csg_qa.slug)
        self.assertEqual(set(relations), expected)

        # Now lets go a step further and test out the sp incentive payer
        self.assertIsNone(status.standardprotocolcalculator_set.first())
        from axis.customer_neea.models import StandardProtocolCalculator

        sp = StandardProtocolCalculator.objects.create(home_status=status)
        self.assertEqual(status.standardprotocolcalculator_set.first(), sp)

        # Nothing should change but we are in the sp_calc loop
        sp.incentive_paying_organization_id = self.utility_org.id
        sp.save()

        create_or_update_spanning_relationships(self.rater_org, status)
        relations = self.home.relationships.all().values_list("company__slug", flat=True)
        self.assertEqual(set(relations), expected)
