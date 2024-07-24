"""test_models.py: api browwer"""


import logging

from django.test import TestCase
from axis.core.tests.factories import non_company_user_factory
from .factories import question_factory, answer_factory
from ..models import Answer

__author__ = "Autumn Valenta"
__date__ = "4/23/13 12:14 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]

from ...geographic.tests.factories import real_city_factory

log = logging.getLogger(__name__)


class AnswerModelTests(TestCase):
    def test_get_conflicting_answers(self):
        """
        Tests that ``Answer.get_conflicting_answers()`` answers that share
        ``is_considered_failure=False``

        """
        from axis.home.tests.factories import custom_home_factory

        city = real_city_factory("Gilbert", "AZ")
        home = custom_home_factory(street_line1="256 w oxford ln", city=city, zipcode="85233")
        question = question_factory()
        user = non_company_user_factory()
        failure_kwargs = {
            "home": home,
            "question": question,
            "user": user,
            "system_no": None,
            "is_considered_failure": True,
        }

        success_kwargs = failure_kwargs.copy()
        success_kwargs.update(dict(is_considered_failure=False))

        answer1_failure = answer_factory(**failure_kwargs)
        answer2_failure = answer_factory(**failure_kwargs)
        answer3_success = answer_factory(**success_kwargs)

        # Failures will return 1, but failures are allowed to exist alongside of successes.
        conflicts = answer1_failure.get_conflicting_answers()
        self.assertEqual(conflicts.count(), 1)
        self.assertEqual(conflicts.get(), answer3_success)

        conflicts = answer2_failure.get_conflicting_answers()
        self.assertEqual(conflicts.count(), 1)
        self.assertEqual(conflicts.get(), answer3_success)

        self.assertEqual(answer3_success.get_conflicting_answers().count(), 0)

    def test_conflicting_answer_deletes_old_successes(self):
        """Verifies that new successes remove old successes via the ``save()`` execution."""

        from axis.home.tests.factories import custom_home_factory

        user = non_company_user_factory()
        self.assertIsNotNone(user.pk)

        home = custom_home_factory()
        self.assertIsNotNone(home.pk)

        question = question_factory()
        self.assertIsNotNone(question.pk)

        answer_kwargs = {"home": home, "question": question, "user": user, "answer": "X"}
        answer, create = Answer.objects.get_or_create(**answer_kwargs)

        self.assertIsNotNone(answer.pk)
        self.assertTrue(create)

        answer_kwargs = {"home": home, "question": question, "user": user, "answer": "Y"}
        answer_2, create = Answer.objects.get_or_create(**answer_kwargs)

        self.assertIsNotNone(answer_2.pk)
        self.assertTrue(create)

        self.assertEqual(Answer.objects.count(), 1)
        self.assertEqual(Answer.objects.get(), answer_2)
        self.assertEqual(answer_2.get_conflicting_answers().count(), 0)
