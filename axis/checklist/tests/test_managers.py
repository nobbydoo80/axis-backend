from django.contrib.auth import get_user_model
from axis.core.tests.testcases import AxisTestCase
from axis.home.models import EEPProgramHomeStatus
from ..models import Answer, Question
from .factories import answer_factory


__author__ = "Michael Jeffrey"
__date__ = "11/9/15 4:40 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Michael Jeffrey",
]

User = get_user_model()


class AnswerManagerTests(AxisTestCase):
    """
    All tests assume all companies have mutual relationships with each other.
    """

    @classmethod
    def setUpTestData(cls):
        from axis.checklist.tests.factories import (
            question_factory,
            answer_factory,
            checklist_factory,
            question_choice_factory,
        )
        from axis.core.tests.factories import (
            eep_admin_factory,
            rater_admin_factory,
            provider_admin_factory,
        )
        from axis.home.tests.factories import eep_program_home_status_factory, home_factory
        from axis.eep_program.tests.factories import basic_eep_program_factory
        from axis.relationship.models import Relationship

        eep_user = eep_admin_factory(company__name="EEP1")
        rater_user = rater_admin_factory(
            company__name="Rater1"
        )  # Matt Douglas  - Earth Advantage Institute
        provider_user = provider_admin_factory(company__name="Provider1")  # Scott Leonard - PECI

        # Question to be shared
        question_one = question_factory()
        question_choices = [
            question_choice_factory(choice="one", is_considered_failure=True),
            question_choice_factory(choice="two"),
        ]
        question_two = question_factory(question_choices=question_choices)
        question_three = question_factory(is_optional=True)
        # To keep stats from being automatically certified
        question_four = question_factory()
        questions = [question_one, question_two, question_three, question_four]

        # Checklist to start split
        checklist_one = checklist_factory(name="Regular Checklist 1", questions=questions)
        checklist_two = checklist_factory(name="QA Checklist 1", questions=questions)

        # Programs different checklists, same questions.
        program_one = basic_eep_program_factory(
            name="Regular Program 1",
            required_checklists=[checklist_one],
            owner=eep_user.company,
            no_close_dates=True,
        )
        program_two = basic_eep_program_factory(
            name="QA Program 1",
            required_checklists=[checklist_two],
            owner=eep_user.company,
            no_close_dates=True,
        )

        # Home for programs to attach to
        home = home_factory()

        # Regular and QA Home Status
        status_one = eep_program_home_status_factory(
            company=rater_user.company, eep_program=program_one, home=home
        )
        status_two = eep_program_home_status_factory(
            company=provider_user.company, eep_program=program_two, home=home
        )

        # Make mutual relationships
        import operator

        companies = map(operator.attrgetter("company"), [eep_user, rater_user, provider_user])
        Relationship.objects.create_mutual_relationships(*companies)

        # Answer questions
        answer_factory(question_one, home, rater_user, answer="Rater Answer")
        answer_factory(question_two, home, rater_user, answer="two")
        answer_factory(question_one, home, provider_user, answer="Provider Answer")
        answer_factory(question_two, home, provider_user, answer="one")

    def test_rater_can_only_retrieve_own_program_answers(self):
        """
        Rater can only view Answers from regular program.
        """
        rater_user = User.objects.get(company__name="Rater1")

        answers = Answer.objects.filter_by_company(rater_user.company)

        self.assertGreater(answers.count(), 0)
        self.assertLess(answers.count(), Answer.objects.count())
        self.assertEqual(answers.count(), 2)  # Answered 2 questions in fixture compiler

    def test_provider_can_retrieve_own_and_mutual_relations_program_answers(self):
        """
        Provider can view Raters answers and QA answers.
        """
        provider_user = User.objects.get(company__name="Provider1")

        answers = Answer.objects.filter_by_company(provider_user.company)

        self.assertGreater(answers.count(), 0)
        # Answered 2 questions for Rater's AND Provider's programs in fixture compiler.
        # Provider can see all answers so far.
        self.assertEqual(answers.count(), 4)

    def test_raters_answers_pointing_to_question_on_multiple_checklists_only_affect_one_program(
        self,
    ):
        """
        Rater's program with shared questions pct_complete is calculated independently.
        """
        rater_user = User.objects.get(company__name="Rater1")

        pct_completes = list(
            set(EEPProgramHomeStatus.objects.values_list("pct_complete", flat=True))
        )

        self.assertEqual(len(pct_completes), 1)
        self.assertEqual(round(pct_completes[0], 2), round((float(2) / 3) * 100, 2))

        # Create Answer for Rater Program
        stat = EEPProgramHomeStatus.objects.get(company=rater_user.company)
        unanswered_questions = list(
            filter(lambda x: not x.is_optional, stat.get_unanswered_questions())
        )
        self.assertEqual(len(unanswered_questions), 1)
        question = Question.objects.get(id=unanswered_questions[0].id)
        answer_factory(question, stat.home, rater_user)

        pct_completes = list(
            set(EEPProgramHomeStatus.objects.values_list("pct_complete", flat=True))
        )

        self.assertEqual(len(pct_completes), 2)
        self.assertIn(round((float(2) / 3) * 100, 2), [float(round(x, 2)) for x in pct_completes])
        self.assertIn(100, pct_completes)

    def test_providers_answers_pointing_to_question_on_multiple_checklists_only_affect_one_program(
        self,
    ):
        """
        Provider's program with shared questions pct_complete is calculated independently,
        despite having access to Rater's Answers.
        """
        provider_user = User.objects.get(company__name="Provider1")

        pct_completes = list(
            set(EEPProgramHomeStatus.objects.values_list("pct_complete", flat=True))
        )

        self.assertEqual(len(pct_completes), 1)
        self.assertEqual(round(pct_completes[0], 2), round((float(2) / 3) * 100, 2))

        # Create Answer for Provider program
        stat = EEPProgramHomeStatus.objects.get(company=provider_user.company)
        unanswered_questions = list(
            filter(lambda x: not x.is_optional, stat.get_unanswered_questions())
        )
        self.assertEqual(len(unanswered_questions), 1)
        question = Question.objects.get(id=unanswered_questions[0].id)
        answer_factory(question, stat.home, provider_user)

        pct_completes = list(
            set(EEPProgramHomeStatus.objects.values_list("pct_complete", flat=True))
        )

        self.assertEqual(len(pct_completes), 2)
        self.assertIn(round((float(2) / 3) * 100, 2), [float(round(x, 2)) for x in pct_completes])
        self.assertIn(100, pct_completes)
