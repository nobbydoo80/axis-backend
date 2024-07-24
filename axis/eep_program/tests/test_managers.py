"""test_managers.py: Django eep_program managers tests"""


from django.contrib.auth import get_user_model
from django.db.models import Q
from django_input_collection.models import CollectionRequest

from axis.company.models import Company
from axis.core.tests.testcases import AxisTestCase
from axis.eep_program.models import EEPProgram
from axis.eep_program.tests.factories import basic_eep_program_factory

from axis.eep_program.tests.mixins import EEPProgramManagerTestMixin
from axis.subdivision.models import Subdivision, EEPProgramSubdivisionStatus
from axis.subdivision.tests.factories import subdivision_factory

__author__ = "Michael Jeffrey"
__date__ = "11/4/15 4:33 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = ["Michael Jeffrey", "Johnny Fang"]

User = get_user_model()


class EEPProgramManagerTests(EEPProgramManagerTestMixin, AxisTestCase):
    """Tests for eep_program managers"""

    @staticmethod
    def get_non_eep_user():
        """Method to get non eep_user"""
        return User.objects.exclude(company__company_type="eep").first()

    def test_opt_in_program_not_addable_by_not_opted_in_company(self):
        """
        Given a Program marked as opt-in.
        And a Company is not opted in
        When they request the list of addable programs
        Then they should not retrieve the Program
        """
        regular_user = self.get_non_eep_user()
        other_user = User.objects.exclude(company=regular_user.company).first()
        program = EEPProgram.objects.filter_by_user(regular_user).first()
        self.assertIsNotNone(program)

        program.opt_in = True
        program.opt_in_out_list.set([other_user.company])
        program.save()

        addable_programs = EEPProgram.objects.filter_active_for_home_status_creation_by_user(
            regular_user
        )

        self.assertNotIn(program, addable_programs)

    def test_all_programs_addable_by_super_user(self):
        """
        For a superuser request the list of addable programs then they should retrieve all
        the user's programs
        """
        eep_user = User.objects.get(company__name="EEP1")
        user_eep_programs = EEPProgram.objects.filter_active_for_home_status_creation_by_user(
            eep_user
        )
        eep_user.is_superuser = True
        all_eep_user_programs = EEPProgram.objects.filter_active_for_home_status_creation_by_user(
            eep_user
        )
        self.assertGreater(all_eep_user_programs.count(), user_eep_programs.count())

    def test_opt_in_program_addable_by_opted_in_company(self):
        """
        Given a Program marked as opt-in.
        And a Company is opted in.
        When they request the list of addable programs
        Then they should retrieve the Program
        """
        regular_user = self.get_non_eep_user()
        program = EEPProgram.objects.filter_by_user(regular_user).first()
        self.assertIsNotNone(program)

        program.opt_in = True
        program.opt_in_out_list.set([regular_user.company])
        program.save()

        addable_programs = EEPProgram.objects.filter_active_for_home_status_creation_by_user(
            regular_user
        )

        self.assertIn(program, addable_programs)

    def test_opt_out_program_not_addable_by_opted_out_company(self):
        """
        Given a Program marked as opt-out
        And a Company is opted out
        When they request the list of addable programs
        Then they should not retrieve the Program
        """
        regular_user = self.get_non_eep_user()
        program = EEPProgram.objects.filter_by_user(regular_user).first()
        self.assertIsNotNone(program)

        program.opt_in = False
        program.opt_in_out_list.set([regular_user.company])
        program.save()

        addable_programs = EEPProgram.objects.filter_active_for_home_status_creation_by_user(
            regular_user
        )

        self.assertNotIn(program, addable_programs)

    def test_opt_out_program_addable_by_not_opted_out_company(self):
        """
        Given a Program marked as opt-out
        And a Company is not opted out
        When they request the list of addable programs
        Then they should retrieve the Program
        """
        regular_user = self.get_non_eep_user()
        other_user = User.objects.exclude(company=regular_user.company).first()
        program = EEPProgram.objects.filter_by_user(regular_user).first()
        self.assertIsNotNone(program)

        program.opt_in = False
        program.opt_in_out_list.set([other_user.company])
        program.save()

        addable_programs = EEPProgram.objects.filter_active_for_home_status_creation_by_user(
            regular_user
        )

        self.assertIn(program, addable_programs)

    def test_opt_in_program_empty_list_not_addable(self):
        """
        Given a Program marked as opt-in
        And no Companies in the list
        When a Company requests the list of addable programs
        Then they should not retrieve the Program
        """
        regular_user = self.get_non_eep_user()
        program = EEPProgram.objects.filter_by_user(regular_user).first()
        self.assertIsNotNone(program)

        program.opt_in = True
        program.opt_in_out_list.set([])
        program.save()

        addable_programs = EEPProgram.objects.filter_active_for_home_status_creation_by_user(
            regular_user
        )

        self.assertNotIn(program, addable_programs)

    def test_opt_out_program_empty_list_addable(self):
        """
        Given a Program marked as opt-out
        And no Companies in the list
        When a Company requests the list of addable programs
        Then they should retrieve the Program
        """
        regular_user = self.get_non_eep_user()
        program = EEPProgram.objects.filter_by_user(regular_user).first()
        self.assertIsNotNone(program)

        program.opt_in = False
        program.opt_in_out_list.set([])
        program.save()

        addable_programs = EEPProgram.objects.filter_active_for_home_status_creation_by_user(
            regular_user
        )

        self.assertIn(program, addable_programs)

    def test_owner_can_retrieve_own_programs(self):
        """
        The User's company is the owner of the EEPProgram.
        They should be able to get it. Always.
        """
        eep_user = User.objects.get(company__name="EEP1")
        programs = EEPProgram.objects.filter_by_company(eep_user.company)

        self.assertGreater(programs.count(), 0)
        self.assertLess(programs.count(), EEPProgram.objects.count())
        # Allow for relationship returned programs
        self.assertGreaterEqual(
            programs.count(), EEPProgram.objects.filter(owner=eep_user.company).count()
        )

    def test_mutual_relation_can_retrieve_unrestricted_programs(self):
        """
        The User's company has a mutual relationship with the EEPProgram's Owner.
        There is no company type specified in the viewable_by_company_type field.
        They should be able to see relationships program.
        """
        eep_user = User.objects.get(company__name="EEP1")
        general_user = User.objects.get(company__name="General1")
        # extra filters added so the test will throw an error if an unrestricted program
        # doesn't exist.
        non_restricted_program = EEPProgram.objects.get(
            name="Regular Program 1", viewable_by_company_type__isnull=True, owner=eep_user.company
        )

        # Assert mutual relationship exists

        programs = EEPProgram.objects.filter_by_company(general_user.company)

        self.assertIn(non_restricted_program, list(programs))

    def test_mutual_relation_matching_restriction_can_retrieve_restricted_program(self):
        """
        The User's company has a mutual relationship with the EEPProgram's Owner.
        There is a company type specified in the viewable_by_company_type field.
        The User's company is one of those company types.
        They should be able to see the relationships program.
        """
        eep_user = User.objects.get(company__name="EEP1")
        general_user = User.objects.get(company__name="General1")
        # extra filters added so the test will throw an error if a restricted program doesn't exist.
        kwargs = {
            "name": "Regular Program 2",
            "viewable_by_company_type__contains": general_user.company.company_type,
            "owner": eep_user.company,
        }
        restricted_program = EEPProgram.objects.get(**kwargs)

        # Assert mutual relationship
        programs = EEPProgram.objects.filter_by_company(general_user.company)

        self.assertIn(restricted_program, list(programs))

    def test_test_mutual_relation_not_matching_restriction_cannot_retrieve_restricted_program(self):
        """
        The User's company has a mutual relationship with the EEPProgram's Owner.
        There is a company type specified in the viewable_by_company_type field.
        The User's company is not one of those company types.
        They should not be able to see relationships program.
        """
        general_user = User.objects.get(company__name="General1")
        owner_company = EEPProgram.objects.get(name="QA Program 3").owner
        # extra filters and exclude added so the test will throw an error if a
        # restricted program doesn't exist.
        restricted_program = (
            EEPProgram.objects.filter(
                name="QA Program 3", owner=owner_company, viewable_by_company_type__isnull=False
            )
            .exclude(viewable_by_company_type__contains=general_user.company.company_type)
            .get()
        )

        # Assert mutual relationship

        programs = EEPProgram.objects.filter_by_company(general_user.company)

        self.assertNotIn(restricted_program, list(programs))

    def test_mutual_relation_rater_can_retrieve_unrestricted_programs(self):
        """
        Rater can add regular programs.
        This test is assuming a real world setup of Field QA,
        where programs are restricted to Raters and Builders only.
        """
        rater_user = User.objects.get(company__name="Rater1")
        non_restricted_program = EEPProgram.objects.get(
            name="Regular Program 1", viewable_by_company_type__isnull=True
        )

        programs = EEPProgram.objects.filter_by_company(rater_user.company)

        self.assertNotEqual(programs.count(), EEPProgram.objects.count())
        self.assertIn(non_restricted_program, list(programs))

    def test_mutual_relation_rater_cannot_retrieve_restricted_programs(self):
        """
        Rater can not add QA programs.
        This test is assuming a real world setup of Field QA,
        where programs are restricted to Raters and Builders only.
        """
        rater_user = User.objects.get(company__name="Rater1")
        qa_program = EEPProgram.objects.get(
            name="QA Program 3", viewable_by_company_type__contains="qa"
        )

        programs = EEPProgram.objects.filter_by_company(rater_user.company)

        self.assertNotEqual(programs.count(), EEPProgram.objects.count())
        self.assertNotIn(qa_program, list(programs))

    def test_mutual_relation_provider_can_retrieve_unrestricted_programs(self):
        """
        Provider can add regular programs.
        This test is assuming a real world setup of Field QA,
        where programs are restricted to Raters and Builders only.
        """
        provider_user = User.objects.get(company__name="Provider1")
        non_restricted_program = EEPProgram.objects.get(
            name="Regular Program 1", viewable_by_company_type__isnull=True
        )

        programs = EEPProgram.objects.filter_by_company(provider_user.company)

        self.assertNotEqual(programs.count(), EEPProgram.objects.count())
        self.assertIn(non_restricted_program, list(programs))

    def test_mutual_relation_provider_can_retrieve_restricted_programs(self):
        """
        Provider can add QA programs.
        This test is assuming a real world setup of Field QA,
        where programs are restricted to Raters and Builders only.
        """
        provider_user = User.objects.get(company__name="Provider1")
        qa_program = EEPProgram.objects.get(
            name="QA Program 3", viewable_by_company_type__contains="provider"
        )
        qa_program_owner = qa_program.owner
        qa_program_owner.is_eep_sponsor = True
        qa_program_owner.is_customer = True
        qa_program_owner.save()

        programs = EEPProgram.objects.filter_by_company(provider_user.company)

        self.assertNotEqual(programs.count(), EEPProgram.objects.count())
        self.assertIn(qa_program, list(programs))

    def test_order_by_customer_status(self):
        """
        Test EEPProgramQuerySet order_by_customer_status

        result must be ordered by Is a paying customer and oldest programs first
        """
        qa_program = EEPProgram.objects.order_by_customer_status()
        eep_programs = EEPProgram.objects.order_by("-owner__is_customer", "program_start_date")
        self.assertEqual(qa_program.count(), eep_programs.count())
        self.assertEqual(qa_program.first(), eep_programs.first())
        self.assertEqual(qa_program.last(), eep_programs.last())

    def test_filter_potential_sponsors_for_user_with_superuser(self):
        """Test manager filter_potential_sponsors_for_user()"""
        companies = Company.objects.filter(Q(company_type="eep") | Q(is_eep_sponsor=True))
        provider_user = User.objects.get(company__name="Provider1")
        provider_user.is_superuser = True
        provider_user.save()
        result = EEPProgram.objects.filter_potential_sponsors_for_user(provider_user)
        self.assertEqual(result.count(), companies.count())

    def test_filter_potential_sponsors_for_user(self):
        """Test manager filter_potential_sponsors_for_user()"""
        provider_user = User.objects.get(company__name="Provider1")
        my_rels = provider_user.company.relationships.get_companies()
        my_rels = my_rels.filter(is_customer=False).values_list("id", flat=True)
        expected = Company.objects.filter(id__in=list(my_rels) + [provider_user.company.id])
        result = EEPProgram.objects.filter_potential_sponsors_for_user(provider_user)
        self.assertEqual(result.count(), expected.count())

    def test_filter_potential_sponsors_for_user_for_eep_company(self):
        """Test manager filter_potential_sponsors_for_user()"""
        eep_user = User.objects.get(company__name="EEP1")
        companies = Company.objects.filter(Q(company_type="eep") | Q(is_eep_sponsor=True))
        expected = companies.filter(id=eep_user.company.id)
        result = EEPProgram.objects.filter_potential_sponsors_for_user(eep_user)
        self.assertEqual(result.count(), expected.count())

    def test_filter_potential_sponsors_for_user_general_user(self):
        """Test manager filter_potential_sponsors_for_user()"""
        user = User.objects.get(company__name="General1")
        user.company.is_customer = False
        expected = user.company.sponsors.filter(Q(company_type="eep") | Q(is_eep_sponsor=True))
        result = EEPProgram.objects.filter_potential_sponsors_for_user(user)
        self.assertEqual(result.count(), expected.count())

    def test_filter_by_company_ignoring_dates(self):
        """
        To test this and make sure it works as expected we are going to do the following:
        we need a coupele of EEPPrograms:
            1 that has a program_start_date with todays day + 1
            1 with a program_start_date of today or before
        then we can filter_by_company() withOUT 'ignore_dates' so we can check that we are only
        getting back programs that start today or before
        the we can filter_by_company()  using 'ignore_dates' so we can check that we get all
        programs back
        """
        import datetime

        kwargs = {"ignore_dates": True}
        eep_kwargs = {
            "program_start_date": datetime.date.today() + datetime.timedelta(days=2),
            "program_close_date": datetime.date.today() + datetime.timedelta(days=12),
            "program_submit_date": datetime.date.today() + datetime.timedelta(days=22),
            "program_end_date": datetime.date.today() + datetime.timedelta(days=32),
            "is_public": True,
        }
        basic_eep_program_factory(**eep_kwargs)

        provider_user = User.objects.get(company__name="Provider1")
        # non_restricted_program = EEPProgram.objects.get(name='Regular Program 1',
        #                                                 viewable_by_company_type__isnull=True)

        filtered_programs = EEPProgram.objects.filter_by_company(provider_user.company)
        all_programs = EEPProgram.objects.all()
        self.assertGreater(all_programs.count(), filtered_programs.count())
        # now let's ignore dates!
        filtered_programs_ignore_date = EEPProgram.objects.filter_by_company(
            provider_user.company, **kwargs
        )
        self.assertGreater(filtered_programs_ignore_date.count(), filtered_programs.count())

    def test_filter_by_company_visible_for_use(self):
        """Only get back programs visible_for_use if 'visible_for_use'"""
        import datetime

        kwargs = {"visible_for_use": True}
        eep_kwargs = {
            "program_visibility_date": datetime.date.today() + datetime.timedelta(days=2),
            "is_public": True,
        }
        basic_eep_program_factory(**eep_kwargs)
        provider_user = User.objects.get(company__name="Provider1")
        filtered_programs = EEPProgram.objects.filter_by_company(provider_user.company)
        all_programs = EEPProgram.objects.all()
        self.assertGreater(all_programs.count(), filtered_programs.count())
        # now let's ignore dates!
        programs_visible_for_use = EEPProgram.objects.filter_by_company(
            provider_user.company, **kwargs
        )
        self.assertGreater(filtered_programs.count(), programs_visible_for_use.count())

    def test_filter_eep_sponsors_company_with_a_relationship_with_user(self):
        """
        Test that makes sure that only eep_sponsors companies that I have relationship with
        are returned i.e. companies that are eep_sponsor and also own those eep programs
        """
        eep_sponsor_co = Company.objects.filter(is_eep_sponsor=True)
        user = User.objects.get(company__name="General1")
        user.company.is_customer = False
        sponsoring_co = eep_sponsor_co.first()
        sponsoring_co.sponsored_preferences.create(
            sponsor=sponsoring_co, sponsored_company=user.company
        )
        user_co = EEPProgram.objects.filter_by_company(user.company)

        # first let's make sure that the Program owner is the same - duh!
        self.assertEqual(sponsoring_co.name, user_co.first().owner.name)
        self.assertEqual(sponsoring_co.name, user_co.last().owner.name)
        # our user.company makes up a part of all the programs
        self.assertGreater(EEPProgram.objects.count(), user_co.count())

    def test_filter_neea_eep_sponsors_company_with_a_relationship_with_user(self):
        """
        Test that makes sure that only eep_sponsors companies that I have relationship with are
        returned i.e. companies that are eep_sponsor and also own those eep programs
        Earth Advantage Certified Home is a private Program offered by NEEA to
        Earth Advantage (Rater)
        We keep is_public=False so it doesn't show up for anyone, ever.
        Then explicitly add it to the queryset for NEEA and EA.
        Supers can see it because we bypass all this filtering in filter_by_user
        """
        program_name = "NEEA Program"
        basic_eep_program_factory(name=program_name, slug="earth-advantage-certified-home")
        eep_sponsor_co = Company.objects.filter(is_eep_sponsor=True)
        user = User.objects.get(company__name="General1")
        user.company.is_customer = False
        user.company.slug = "neea"
        sponsoring_co = eep_sponsor_co.first()
        sponsoring_co.sponsored_preferences.create(
            sponsor=sponsoring_co, sponsored_company=user.company
        )
        user_co = EEPProgram.objects.filter_by_company(user.company)

        self.assertIn(program_name, user_co.values_list("name", flat=True))
        # Our user.company makes up a part of all the programs
        self.assertGreater(EEPProgram.objects.count(), user_co.count())

    def test_filter_by_user_using_superuser(self):
        """Test using filter_by_user with is_superuser"""
        user = User.objects.get(company__name="General1")
        user.is_superuser = True
        kwargs = {"ignore_dates": True, "visible_for_use": True}
        filtered = EEPProgram.objects.filter_by_user(user, **kwargs)
        expected = EEPProgram.objects.all()

        self.assertTrue(filtered.count(), expected.count())
        self.assertSetEqual(
            set(filtered.values_list("name", flat=True)),
            set(expected.values_list("name", flat=True)),
        )

    def test_make_sure_user_has_attr_company(self):
        """
        If user argument passed to filter_by_user doesn't have company attribute it returns an
        empty queryset
        """

        class FakeUser(object):
            """class to fake user"""

            is_superuser = False

        filtered = EEPProgram.objects.filter_by_user(FakeUser())

        self.assertTrue(filtered.count() == 0)

    def test_filter_by_collection_support(self):
        """Test that verifies that only eep_programs with collection_requests are returned"""
        basic_eep = basic_eep_program_factory(name="with-collection-request")
        collection_request, _ = CollectionRequest.objects.get_or_create()
        basic_eep.collection_request = collection_request
        basic_eep.save()
        result = EEPProgram.objects.filter_by_collection_support()

        self.assertTrue(result.count() > 0)
        self.assertGreater(EEPProgram.objects.count(), result.count())

    def test_filter_by_questions(self):
        """Test for manager filter_by_question()"""
        from axis.checklist.tests.factories import checklist_factory

        eep_program = EEPProgram.objects.get(name="QA Program 3")
        checklist = checklist_factory()
        eep_program.required_checklists.add(checklist)
        result_dict = EEPProgram.objects.filter_questions(eep_program)

        self.assertTrue(len(result_dict.keys()) > 0)

    def test_program_and_requirement_validation_no_program_name(self):
        """Test for manager verify_for_company() , case when no name is given [EEPProgram.name]"""
        company = Company.objects.first()
        subdivision = Subdivision.objects.first()
        result = EEPProgram.objects.verify_for_company(company=company, subdivision=subdivision)
        self.assertIsNone(result)

    def test_program_and_requirement_validation_no_ignore_missing_no_name(self):
        """
        Test for manager verify_for_company() , case when no name is given [EEPProgram.name] and
        ignore_missing flag passed as argument
        """
        company = Company.objects.first()
        subdivision = Subdivision.objects.first()
        result = EEPProgram.objects.verify_for_company(
            company=company, subdivision=subdivision, ignore_missing=True
        )
        self.assertIsNone(result)

    def test_program_and_requirement_validation_name_represents_int(self):
        """Test for manager verify_for_company() case when value passed to name attr
        represents_integer
        """
        eep_user = User.objects.get(company__name="EEP1")
        eep_user_program = EEPProgram.objects.filter(owner=eep_user.company).first()
        subdivision = Subdivision.objects.first()
        result = EEPProgram.objects.verify_for_company(
            name=eep_user_program.id,
            company=eep_user.company,
            subdivision=subdivision,
            ignore_missing=True,
        )
        eep_program = EEPProgram.objects.filter_by_company(eep_user.company).get(
            id=int(eep_user_program.id)
        )

        self.assertIsNotNone(result)
        self.assertEqual(result, eep_program)

    def test_program_does_not_exist(self):
        """
        Test for manager verify_for_company() case when program does not exists
        i.e. program name does not exist
        """
        existing_companies_ids = Company.objects.values_list("id", flat=True)
        non_existing_id = max(existing_companies_ids) + 1
        company = Company.objects.first()
        subdivision = Subdivision.objects.first()
        result = EEPProgram.objects.verify_for_company(
            name=non_existing_id, company=company, subdivision=subdivision, ignore_missing=True
        )

        self.assertIsNone(result)

    def test_program_and_requirements_validation(self):
        """
        Test for manager verify_for_company() , everything that the manager expects is fine,
        no problems should arise and a result is expected back
        """
        company = Company.objects.first()
        name = (
            EEPProgram.objects.filter_by_company(company=company)
            .values_list("name", flat=True)
            .first()
        )
        subdivision = Subdivision.objects.first()
        result = EEPProgram.objects.verify_for_company(
            name=name, company=company, subdivision=subdivision
        )

        self.assertIsNotNone(result)

    def test_program_exists_no_relation(self):
        """
        Test for manager verify_for_company() case when program does exists but
        there is no relationship
        """
        company = Company.objects.first()
        name = EEPProgram.objects.values_list("name", flat=True).first()
        subdivision = Subdivision.objects.first()
        result = EEPProgram.objects.verify_for_company(
            name=name, company=company, subdivision=subdivision
        )
        self.assertIsNone(result)

    def test_program_not_in_use(self):
        """
        Test for manager verify_for_company() case when program does exists and is not in use.
        EEPProgramSubdivisionStatus - Each company manages their own Programs.
        This allows for that.
        """
        company = Company.objects.first()
        name = (
            EEPProgram.objects.filter_by_company(company=company)
            .values_list("name", flat=True)
            .first()
        )
        subdivision = subdivision_factory()
        result = EEPProgram.objects.verify_for_company(
            name=name, company=company, subdivision=subdivision
        )

        self.assertIsNotNone(result)

    def test_program_is_in_use(self):
        """
        Test for manager verify_for_company() case when program is already in use.
        it raises a log.warning!
        """
        company = Company.objects.first()
        eep_program = EEPProgram.objects.filter_by_company(company=company).first()
        subdivision = subdivision_factory()
        EEPProgramSubdivisionStatus.objects.create(
            subdivision=subdivision, eep_program=eep_program, company=Company.objects.last()
        )
        result = EEPProgram.objects.verify_for_company(
            name=eep_program.name, company=company, subdivision=subdivision
        )

        self.assertIsNotNone(result)
