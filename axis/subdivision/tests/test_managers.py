"""test_managers.py: Django"""


__author__ = "Johnny Fang"
__date__ = "28/5/19 11:30 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Johnny Fang",
]

from axis.company.models import Company
from axis.core.tests.client import AxisClient
from axis.core.tests.factories import general_super_user_factory, basic_user_factory
from django.contrib.auth import get_user_model
from axis.core.tests.testcases import AxisTestCase
from axis.eep_program.models import EEPProgram
from axis.floorplan.models import Floorplan
from axis.floorplan.tests.mixins import FloorplanTestMixin
from axis.relationship.models import Relationship
from axis.subdivision.models import Subdivision, EEPProgramSubdivisionStatus, FloorplanApproval
from axis.subdivision.tests.mixins import SubdivisionManagerTestsMixin

User = get_user_model()


class SubdivisionManagerTests(SubdivisionManagerTestsMixin, AxisTestCase):
    """Tests Subdivision Managers"""

    client_class = AxisClient

    def test_filter_by_company(self):
        """A single builder is tied to a plot of land (subdivision)"""

        builder = User.objects.get(username="noperm_builderadmin")

        subdivisions = Subdivision.objects.filter_by_company(builder.company)
        filtered = subdivisions.first().builder_org

        self.assertEqual(filtered.name, builder.company.name)
        # Sanity checks
        self.assertGreater(subdivisions.count(), 0)
        self.assertLess(subdivisions.count(), Subdivision.objects.count())

    def test_filter_by_user_with_no_company(self):
        """Test filter_by_user"""

        class FakeUser(object):
            """My FakeUser class"""

            is_superuser = False

        result = Subdivision.objects.filter_by_user(FakeUser())
        self.assertEqual(result.count(), 0)

    def test_filter_by_user_with_superuser(self):
        """Test lookup based on user"""

        builder = User.objects.get(username="noperm_builderadmin")
        superuser = general_super_user_factory()
        superuser.company = builder.company
        superuser.save()

        subs_by_user = Subdivision.objects.filter_by_user(superuser)
        subs_by_company = Subdivision.objects.filter_by_company(superuser.company)

        id_list = subs_by_company.values_list("id")
        matched = subs_by_user.filter(id__in=id_list)
        # make sure they contain the same subdivisions
        self.assertEqual(matched.count(), id_list.count())

        # Sanity checks
        self.assertEqual(subs_by_user.count(), Subdivision.objects.count())
        self.assertGreater(subs_by_user.count(), 0)

        kwargs = {"name": Subdivision.objects.first().name}
        subs_by_user = Subdivision.objects.filter_by_user(superuser, **kwargs)
        expected_result = Subdivision.objects.filter(**kwargs)
        self.assertEqual(subs_by_user.count(), expected_result.count())

    def test_filter_by_user(self):
        """Test lookup based on user"""

        builder = User.objects.get(username="noperm_builderadmin")

        subs_by_user = Subdivision.objects.filter_by_user(builder)
        subs_by_company = Subdivision.objects.filter_by_company(builder.company)

        id_list = subs_by_company.values_list("id")
        matched = subs_by_user.filter(id__in=id_list)
        # make sure they contain the same subdivisions
        self.assertEqual(matched.count(), id_list.count())

        # Sanity checks
        self.assertEqual(subs_by_user.count(), subs_by_company.count())
        self.assertGreater(subs_by_user.count(), 0)
        self.assertLess(subs_by_user.count(), Subdivision.objects.count())

    def test_choice_items_from_instances(self):
        """Test choice_items_from_instances"""
        builder = User.objects.get(username="noperm_builderadmin")
        sub_ids = Subdivision.objects.filter_by_user(builder).values_list("id", flat=True)
        subs = Subdivision.objects.choice_items_from_instances(id__in=list(set(sub_ids)))

        self.assertEqual(len(subs), 2)

    def test_choice_items_from_instances_passing_user(self):
        """Test choice_items_from_instances"""
        builder = User.objects.get(username="noperm_builderadmin")
        sub_ids = Subdivision.objects.filter_by_user(builder).values_list("id", flat=True)
        subs = Subdivision.objects.choice_items_from_instances(user=builder)

        self.assertEqual(len(subs), len(sub_ids))

    def test_verify_for_company_with_incorrect_types(self):
        """Tests assertions work as expected"""
        self.assertRaises(
            AssertionError,
            Subdivision.objects.verify_for_company,
            {
                "company": EEPProgram.objects.first(),
                "builder": Company.objects.first(),
            },
        )

    def test_verify_for_company(self):
        """Test verify_for_company"""
        builder = User.objects.get(username="noperm_builderadmin")
        company = Company.objects.get(name=builder.company)
        sub = Subdivision.objects.verify_for_company(
            name="sub2", company=company, builder=builder.company
        )
        self.assertIsNotNone(sub)

        # now let's pass the subdivision id instead of name
        sub_using_id = Subdivision.objects.verify_for_company(
            name=sub.id, company=company, builder=builder.company, builder_name=builder.company.name
        )
        self.assertIsNotNone(sub_using_id)
        self.assertEqual(sub, sub_using_id)

        # now let's builder_name instead of name
        result = Subdivision.objects.verify_for_company(
            company=company, builder=builder.company, builder_name=builder.company.name
        )
        self.assertIsNone(result)

        # now lets' pass wrong id
        result = Subdivision.objects.verify_for_company(
            name=builder.company.id, company=company, builder=builder.company
        )
        self.assertIsNone(result)


class EEPProgramSubdivisionStatusManagerTests(SubdivisionManagerTestsMixin, AxisTestCase):
    """Tests managers for model: EEPProgramSubdivisionStatus"""

    def test_filter_company_is_eep_sponsor(self):
        """Tests lookup done based on a company"""

        companies = Company.objects.all()
        non_eep_owner = EEPProgramSubdivisionStatus.objects.filter_by_company(companies.first())

        eep = User.objects.get(username="eepadmin")
        eep_owner = EEPProgramSubdivisionStatus.objects.filter_by_company(eep.company)
        epp_program = EEPProgram.objects.filter(owner=eep.company)

        # makes sure we are getting back what's expected
        self.assertEqual(epp_program.first().owner, eep_owner.first().company)
        self.assertEqual(non_eep_owner.count(), 0)

        # Sanity checks
        self.assertEqual(eep_owner.count(), 1)
        self.assertEqual(companies.count(), 5)

    def test_filter_by_user(self):
        """Tests lookup performed based on given user"""

        eep = User.objects.get(username="eepadmin")
        eeps_by_company = EEPProgramSubdivisionStatus.objects.filter_by_company(eep.company)
        eeps = EEPProgramSubdivisionStatus.objects.filter_by_user(eep)

        # filter_by_user uses filter_by_company underneath,
        # so we should get the same result at the end
        self.assertEqual(eeps_by_company.first(), eeps.first())
        # sanity check
        self.assertEqual(eeps.count(), eeps_by_company.count())

    def test_filter_by_user_with_superuser(self):
        """Tests lookup performed based on given user"""
        eep = User.objects.get(username="eepadmin")
        superuser = general_super_user_factory()
        superuser.company = eep.company
        superuser.save()

        filtered_by_superuser = EEPProgramSubdivisionStatus.objects.filter_by_user(superuser)
        expected = EEPProgramSubdivisionStatus.objects.filter()

        # if user.is_superuser = True
        # then filter_by_user will use EEPProgramSubdivisionStatus.objects.filter()
        self.assertEqual(filtered_by_superuser.count(), expected.count())

    def test_filter_by_user_with_no_company(self):
        """Test filter_by_user"""

        class FakeUser(object):
            """My FakeUser class"""

            is_superuser = False

        result = EEPProgramSubdivisionStatus.objects.filter_by_user(FakeUser())
        self.assertEqual(result.count(), 0)

    def test_verify_and_create_for_company_with_incorrect_type(self):
        """Tests assertions work as expected"""
        self.assertRaises(
            AssertionError,
            EEPProgramSubdivisionStatus.objects.verify_and_create_for_company,
            {
                "company": Company.objects.first(),
                "subdivision": EEPProgram.objects.first(),
            },
        )

        self.assertRaises(
            AssertionError,
            EEPProgramSubdivisionStatus.objects.verify_and_create_for_company,
            {"company": Company.objects.first(), "eep_program": Subdivision.objects.first()},
        )

        self.assertRaises(
            AssertionError,
            EEPProgramSubdivisionStatus.objects.verify_and_create_for_company,
            {
                "company": Company.objects.first(),
                "subdivision": Subdivision.objects.first(),
                "eep_program": Subdivision.objects.first(),
            },
        )

    def test_verify_and_create_for_company_create(self):
        """Test verify_and_create_for_company actually creates EEPProgramSubdivisionStatus"""
        from axis.eep_program.tests.factories import basic_eep_program_factory
        from axis.subdivision.tests.factories import subdivision_factory

        eep_program = basic_eep_program_factory()
        subdivision = subdivision_factory()
        Relationship.objects.validate_or_create_relations_to_entity(subdivision, eep_program.owner)
        created_epss = EEPProgramSubdivisionStatus.objects.verify_and_create_for_company(
            eep_program.owner, subdivision, eep_program, create=True
        )
        self.assertIsNotNone(created_epss)
        epss = EEPProgramSubdivisionStatus.objects.filter(eep_program=eep_program).first()
        self.assertIsNotNone(epss)
        self.assertEqual(epss.eep_program, created_epss.eep_program)
        self.assertEqual(epss.subdivision, created_epss.subdivision)
        self.assertEqual(epss.company, created_epss.company)

    def test_verify_and_create_for_company_no_relationship(self):
        """Test verify_and_create_for_company actually creates EEPProgramSubdivisionStatus"""
        from axis.eep_program.tests.factories import basic_eep_program_factory
        from axis.subdivision.tests.factories import subdivision_factory

        eep_program = basic_eep_program_factory()
        eep_program.rater_incentive_dollar_value = 3.0
        eep_program.save()
        subdivision = subdivision_factory()
        # Relationship.objects.validate_or_create_relations_to_entity(subdivision,
        # eep_program.owner)
        created_epss = EEPProgramSubdivisionStatus.objects.verify_and_create_for_company(
            eep_program.owner, subdivision, eep_program, create=True
        )
        self.assertIsNotNone(created_epss)
        epss = EEPProgramSubdivisionStatus.objects.filter(eep_program=eep_program).first()
        self.assertIsNotNone(epss)
        self.assertEqual(epss.eep_program, created_epss.eep_program)
        self.assertEqual(epss.subdivision, created_epss.subdivision)
        self.assertEqual(epss.company, created_epss.company)

        eep_program.rater_incentive_dollar_value = 0.0
        company = eep_program.owner
        company.users.set([basic_user_factory()])

        created_eps = EEPProgramSubdivisionStatus.objects.verify_and_create_for_company(
            eep_program.owner, subdivision, eep_program, create=True
        )
        self.assertIsNotNone(created_eps)


class FloorplanApprovalQuerySetTest(FloorplanTestMixin, AxisTestCase):
    """Test for subdivision's FloorplanApprovalQuerySet"""

    def test_filter_by_company(self):
        """Test filter_by_company"""
        subdivision = Subdivision.objects.first()
        floorplan = Floorplan.objects.first()

        FloorplanApproval.objects.get_or_create(subdivision=subdivision, floorplan=floorplan)
        filtered_by_co = FloorplanApproval.objects.filter_by_company(floorplan.owner)
        ids = Floorplan.objects.filter_by_company(floorplan.owner, ids_only=True)
        expected = FloorplanApproval.objects.filter(floorplan__id__in=ids)

        self.assertIsNotNone(filtered_by_co)
        self.assertIsNotNone(expected)
        self.assertEqual(filtered_by_co.count(), expected.count())
        for item in filtered_by_co:
            self.assertIn(item.floorplan.id, ids)

    def test_filter_by_user(self):
        """Test filter_by_user"""
        subdivision = Subdivision.objects.first()
        floorplan = Floorplan.objects.first()
        user = User.objects.get(username="rateradmin")

        FloorplanApproval.objects.get_or_create(subdivision=subdivision, floorplan=floorplan)
        filtered_by_user = FloorplanApproval.objects.filter_by_user(user)
        ids = Floorplan.objects.filter_by_company(floorplan.owner, ids_only=True)
        expected = FloorplanApproval.objects.filter(floorplan__id__in=ids)

        self.assertIsNotNone(filtered_by_user)
        self.assertIsNotNone(expected)
        self.assertEqual(filtered_by_user.count(), expected.count())
        for item in filtered_by_user:
            self.assertIn(item.floorplan.id, ids)

    def test_filter_by_user_with_superuser(self):
        """Tests lookup performed based on given user"""
        user = User.objects.get(username="rateradmin")
        superuser = general_super_user_factory()
        superuser.company = user.company
        superuser.save()

        filtered_by_superuser = FloorplanApproval.objects.filter_by_user(superuser)
        expected = FloorplanApproval.objects.filter()

        # if user.is_superuser = True
        # then filter_by_user will use EEPProgramSubdivisionStatus.objects.filter()
        self.assertEqual(filtered_by_superuser.count(), expected.count())

    def test_filter_by_user_and_subdivision(self):
        """Test filter_by_user_and_subdivision"""
        from axis.floorplan.tests.factories import floorplan_factory
        from axis.subdivision.tests.factories import subdivision_factory

        subdivision = Subdivision.objects.first()
        floorplan = Floorplan.objects.first()
        FloorplanApproval.objects.get_or_create(subdivision=subdivision, floorplan=floorplan)

        subdivision2 = subdivision_factory()
        floorplan2 = floorplan_factory()
        floorplan_approval2 = FloorplanApproval.objects.get_or_create(
            subdivision=subdivision2, floorplan=floorplan2
        )

        user = User.objects.get(username="rateradmin")

        result = FloorplanApproval.objects.filter_by_user_and_subdivision(user, subdivision)
        ids = result.values_list("id")
        self.assertIsNotNone(result)
        self.assertGreater(FloorplanApproval.objects.count(), result.count())
        self.assertNotIn(floorplan_approval2[0].id, ids)
