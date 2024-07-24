"""fixturecompilers.py: Django eep_program"""


__author__ = "Steven Klass"
__date__ = "9/19/14 10:30 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

import logging

from axis.company.models import Company
from axis.company.tests.mixins import CompaniesAndUsersTestMixin

from axis.geographic.tests.factories import real_city_factory
from axis.scheduling.models import ConstructionStage


log = logging.getLogger(__name__)


class EEPProgramsTestMixin(CompaniesAndUsersTestMixin):
    """Fixture for model EEPPrograms"""

    include_company_types = ["builder", "eep", "provider", "general"]
    include_noperms_user = False

    @classmethod
    def setUpTestData(cls):
        super(EEPProgramsTestMixin, cls).setUpTestData()

        from axis.checklist.tests.factories import (
            question_factory,
            question_choice_factory,
            checklist_factory,
        )
        from axis.eep_program.tests.factories import (
            basic_eep_program_checklist_factory,
            basic_eep_program_factory,
        )

        ConstructionStage.objects.create(name="Started", is_public=True, order=1)
        ConstructionStage.objects.create(name="Completed", is_public=True, order=100)

        # Used for View Tests
        owner = Company.objects.get(name__istartswith="unrelated", company_type="eep")
        basic_eep_program_factory(name="Basic", owner=owner, no_close_dates=True)

        # Used outside of this.
        owner = (
            Company.objects.exclude(name__istartswith="unrelated").filter(company_type="eep").get()
        )

        fail_kw = {"document_required": True, "photo_required": True, "comment_required": True}
        na_kw = {"display_as_failure": True, "comment_required": True}
        pass_fail = [
            question_choice_factory(choice="Pass", choice_order=1),
            question_choice_factory(choice="Fail", choice_order=2, **fail_kw),
            question_choice_factory(choice="N/A", choice_order=3, **na_kw),
        ]

        basic_questions = [
            question_factory(question="Describe the front door", priority=1, allow_bulk_fill=True),
            question_factory(
                question="Verify the front door is on.",
                priority=2,
                allow_bulk_fill=True,
                question_choices=pass_fail,
            ),
            question_factory(
                question="Enter the date the door was installed",
                priority=3,
                allow_bulk_fill=True,
                type="date",
            ),
            question_factory(
                question="How many panels is the door",
                priority=4,
                allow_bulk_fill=True,
                type="integer",
            ),
            question_factory(
                question="What is the thickness of the door",
                priority=4,
                allow_bulk_fill=True,
                type="float",
                unit="inches",
            ),
        ]

        clists = [
            checklist_factory(
                name="Test Basic 5",
                questions=basic_questions,
                group=owner.group,
                public=True,
                add_section=True,
            )
        ]

        basic_eep_program_checklist_factory(
            name="Single Checklist - Basic",
            max_hers_score=False,
            allow_sampling=True,
            required_checklists=clists,
            builder_incentive_dollar_value=0,
            owner=owner,
            no_close_dates=True,
        )

        from axis.checklist.models import Question, QuestionChoice

        assert Question.objects.count() == 5, "Missing Questinos"
        assert Question.objects.filter(type="multiple-choice").count() == 1, "Missing MC Questinos"
        assert Question.objects.filter(type="date").count() == 1, "Missing date Questinos"
        assert Question.objects.filter(type="integer").count() == 1, "Missing int Questinos"
        assert Question.objects.filter(type="float").count() == 1, "Missing float Questinos"
        assert Question.objects.filter(type="open").count() == 1, "Missing open Questinos"
        assert QuestionChoice.objects.count() == 3, "Missing Choices"

        assert Company.objects.filter(company_type="builder").count() == 2, "Builders"


class EEPProgramManagerTestMixin:
    """Fixture for EEPProgram's manager"""

    @classmethod
    def setUpTestData(cls):
        from axis.eep_program.tests.factories import basic_eep_program_factory
        from axis.core.tests.factories import (
            rater_admin_factory,
            provider_admin_factory,
            qa_admin_factory,
            eep_admin_factory,
            general_admin_factory,
        )
        from axis.relationship.models import Relationship
        import operator

        cls.city = real_city_factory(name="Gilbert", state="AZ")

        qa_user = qa_admin_factory(company__city=cls.city)
        eep_user = eep_admin_factory(company__name="EEP1", company__city=cls.city)
        eep_user_2 = eep_admin_factory(company__name="EEP2")
        rater_user = rater_admin_factory(company__name="Rater1", company__city=cls.city)
        provider_user = provider_admin_factory(company__name="Provider1", company__city=cls.city)
        general_user = general_admin_factory(company__name="General1", company__city=cls.city)

        # Assortment of programs to test against
        eep_program = basic_eep_program_factory(
            name="Regular Program 1",
            owner=eep_user.company,
            no_close_dates=True,
        )
        eep_program_2 = basic_eep_program_factory(
            name="Regular Program 2",
            owner=eep_user.company,
            viewable_by_company_type="general",
            no_close_dates=True,
        )

        # eep_program_3 AND qa_eep_program slugs are pretty similar this is necessary
        eep_program_3_kwargs = dict()
        eep_program_3_kwargs["slug"] = "program-3"
        eep_program_3 = basic_eep_program_factory(
            name="Regular Program 3",
            owner=eep_user.company,
            viewable_by_company_type="general",
            no_close_dates=True,
            **eep_program_3_kwargs,
        )
        qa_program_kwargs = dict()
        qa_program_kwargs["is_qa_program"] = True
        qa_program_kwargs["slug"] = "program-3-qa"
        qa_eep_program = basic_eep_program_factory(
            name="QA Program 3",
            owner=qa_user.company,
            viewable_by_company_type="qa, provider",
            no_close_dates=True,
            **qa_program_kwargs,
        )

        # Extra program from different owner to add corner case
        eep_program_5 = basic_eep_program_factory(owner=eep_user_2.company, no_close_dates=True)

        # create relationships
        users = [qa_user, eep_user, rater_user, provider_user, general_user]
        Relationship.objects.create_mutual_relationships(
            *map(operator.attrgetter("company"), users)
        )
        assert qa_eep_program.is_qa_program
        assert qa_eep_program.slug == "program-3-qa"
        assert qa_eep_program.owner == qa_user.company

        assert eep_program.owner == eep_user.company
        assert eep_program_2.owner == eep_user.company
        assert eep_program_3.owner == eep_user.company
        assert eep_program_3.slug == "program-3"
        assert eep_program_5.owner == eep_user_2.company


class EEPProgramHomeStatusTestMixin:
    """Fixture for EEPProgram's model that relies heavily on EEPProgramHomeStatus"""

    @classmethod
    def setUpTestData(cls):
        from axis.eep_program.tests.factories import basic_eep_program_factory
        from axis.core.tests.factories import eep_admin_factory
        from axis.core.tests.factories import rater_user_factory
        from axis.home.tests.factories import eep_program_custom_home_status_factory
        from axis.core.tests.factories import utility_admin_factory
        from axis.company.tests.factories import hvac_organization_factory
        from axis.relationship.models import Relationship
        from axis.relationship.utils import create_or_update_spanning_relationships
        from axis.home.tests.factories import custom_home_factory

        cls.city = real_city_factory(name="Gilbert", state="AZ")

        eep_user = eep_admin_factory(company__name="EEP3", company__city=cls.city)
        eep_program = basic_eep_program_factory(
            name="Regular Program 3",
            owner=eep_user.company,
            no_close_dates=True,
        )
        rater_user = rater_user_factory(company__city=cls.city)
        kwargs = {
            "eep_program": eep_program,
            "home__city": cls.city,
            "company": rater_user.company,
            "home__is_multi_family": False,
        }
        home_status = eep_program_custom_home_status_factory(**kwargs)

        # we need an  Utility company (electric and gas)
        utility_kwars = {"company__electricity_provider": True, "company__gas_provider": True}
        utility_admin = utility_admin_factory(
            company__name="Utility1", company__city=cls.city, **utility_kwars
        )

        create_or_update_spanning_relationships(utility_admin.company, home_status.home)

        # home_status - home & eep_program unique_together
        eep_user4 = eep_admin_factory(company__name="EEP4", company__city=cls.city)
        eep_program2 = basic_eep_program_factory(
            name="Regular Program 4",
            owner=eep_user4.company,
            no_close_dates=True,
        )

        hvac_kwargs = {"hquito_accredited": None}
        hvac_co = hvac_organization_factory(name="HVAC1", city=cls.city, **hvac_kwargs)
        home = custom_home_factory(city=cls.city)
        kwargs = {"eep_program": eep_program2, "home": home}
        home_status2 = eep_program_custom_home_status_factory(**kwargs)
        Relationship.objects.create_mutual_relationships(home_status2.company, hvac_co)
        Relationship.objects.validate_or_create_relations_to_entity(home, hvac_co)


class ProgramSpecsGenFixtureMixin:
    """Fixture for Program Specs Gen"""

    @classmethod
    def setUpTestData(cls):
        from axis.eep_program.tests.factories import basic_eep_program_checklist_factory
        from axis.checklist.tests.factories import (
            question_factory,
            question_choice_factory,
            checklist_factory,
        )
        from axis.core.tests.factories import eep_admin_factory

        cls.city = real_city_factory(name="Gilbert", state="AZ")

        eep_admin_factory(
            company__is_eep_sponsor=True,
            company__slug="neea",
            company__name="NEEA",
            company__city=cls.city,
        )
        eep_user = eep_admin_factory(company__name="EEP3", company__city=cls.city)

        fail_kw = {"document_required": True, "photo_required": True, "comment_required": True}
        na_kw = {"display_as_failure": True, "comment_required": True}
        pass_fail = [
            question_choice_factory(choice="Pass", choice_order=1),
            question_choice_factory(choice="Fail", choice_order=2, **fail_kw),
            question_choice_factory(choice="N/A", choice_order=3, **na_kw),
        ]

        basic_questions = [
            question_factory(
                question="Describe the front door",
                priority=1,
                description="Describe the front door",
                allow_bulk_fill=True,
            ),
            question_factory(
                question="Verify the front door is on.",
                priority=2,
                description="is the front door on?",
                allow_bulk_fill=True,
                question_choices=pass_fail,
            ),
            question_factory(
                question="Enter the date the door was installed",
                priority=3,
                description="When was the door installed?",
                allow_bulk_fill=True,
                type="date",
            ),
            question_factory(
                question="How many panels is the door",
                priority=4,
                description="number of panels",
                allow_bulk_fill=True,
                type="integer",
            ),
            question_factory(
                question="What is the thickness of the door",
                priority=4,
                description="in inches how thick is the door?",
                allow_bulk_fill=True,
                type="float",
                unit="inches",
            ),
        ]

        clists = [
            checklist_factory(
                name="Test Basic 5",
                questions=basic_questions,
                group=eep_user.company.group,
                public=True,
                add_section=True,
            )
        ]

        basic_eep_program_checklist_factory(
            name="Single Checklist - Basic",
            slug="test-program",
            max_hers_score=False,
            allow_sampling=True,
            required_checklists=clists,
            builder_incentive_dollar_value=0,
            owner=eep_user.company,
            no_close_dates=True,
        )

        from axis.eep_program.models import EEPProgram

        program = EEPProgram.objects.get(name="Single Checklist - Basic")
        assert program.required_checklists.count() == 1, "Checklist was not added to EEPProgram"

        from axis.checklist.models import Question, QuestionChoice

        assert Question.objects.count() == 5, "Missing Questinos"
        assert Question.objects.filter(type="multiple-choice").count() == 1, "Missing MC Questinos"
        assert Question.objects.filter(type="date").count() == 1, "Missing date Questinos"
        assert Question.objects.filter(type="integer").count() == 1, "Missing int Questinos"
        assert Question.objects.filter(type="float").count() == 1, "Missing float Questinos"
        assert Question.objects.filter(type="open").count() == 1, "Missing open Questinos"
        assert QuestionChoice.objects.count() == 3, "Missing Choices"
