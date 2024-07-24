""" Tests for sampleset models. """


from django.conf import settings
from django.test import TestCase

from axis.core.tests.testcases import AxisTestCaseUserMixin
from axis.checklist.models import Answer
from .mixins import SampleSetTestMixin
from .. import strings
from ..models import SampleSet, SampleSetHomeStatus

__author__ = "Autumn Valenta"
__date__ = "07-09-14  4:31 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


class SampleSetModelTests(SampleSetTestMixin, TestCase, AxisTestCaseUserMixin):
    def test_add_home_status(self):
        """
        Target homestatus gets added to the sampleset if there is room in its current revision.
        """
        from axis.home.models import EEPProgramHomeStatus

        generic = SampleSet.objects.get(uuid="generic")
        full = SampleSet.objects.get(uuid="full")
        home_status = EEPProgramHomeStatus.objects.get(company__name="loose_objects")

        sshs = generic.add_home_status(home_status)
        self.assertEqual(sshs.home_status, home_status)
        self.assertEqual(sshs.revision, generic.revision)
        sshs.delete()

        msg = strings.SAMPLESET_FULL
        self.assertRaisesMessage(
            Exception,
            msg.format(max_size=settings.SAMPLING_MAX_SIZE),
            full.add_home_status,
            home_status,
        )

    def test_add_home_status_to_revision(self):
        """
        Target homestatus gets added to the sampleset at the specific revision requested.
        """
        from axis.home.models import EEPProgramHomeStatus

        multistage = SampleSet.objects.get(uuid="multistage")
        home_status = EEPProgramHomeStatus.objects.get(company__name="loose_objects")

        # "multistage" sampleset has 3 revisions in it: 0, 1, 2
        self.assertNotEqual(multistage.revision, 1)
        old_count = multistage.samplesethomestatus_set.filter(revision=1).count()
        old_current_count = multistage.samplesethomestatus_set.current().count()
        sshs = multistage.add_home_status(home_status, revision=1)
        self.assertEqual(sshs.home_status, home_status)
        self.assertEqual(sshs.revision, 1)
        self.assertEqual(
            old_count + 1, multistage.samplesethomestatus_set.filter(revision=1).count()
        )
        self.assertEqual(old_current_count, multistage.samplesethomestatus_set.current().count())
        self.assertNotIn(sshs, multistage.samplesethomestatus_set.current())

    def test_add_home_status_duplicate(self):
        """
        Target homestatus is detected in the sampleset for the given revision/is_test_home values.
        """
        from axis.home.models import EEPProgramHomeStatus

        generic = SampleSet.objects.get(uuid="generic")
        home_status = EEPProgramHomeStatus.objects.get(company__name="loose_objects")

        self.assertEqual(generic.home_statuses.filter(id=home_status.id).exists(), False)
        sshs1 = generic.add_home_status(home_status)
        sshs2 = generic.add_home_status(home_status)
        self.assertEqual(sshs1.id, sshs2.id)

        sshs1 = generic.add_home_status(home_status, revision=50)
        sshs2 = generic.add_home_status(home_status, revision=50)
        self.assertEqual(sshs1.id, sshs2.id)

        sshs1 = generic.add_home_status(home_status, revision=51, is_test_home=True)
        with self.assertRaises(ValueError):
            sshs2 = generic.add_home_status(home_status, revision=51, is_test_home=False)

    def test_is_full(self):
        """The SampleSet.is_full() method correctly reflects the quantity of items currently in it."""
        empty = SampleSet.objects.get(uuid="empty")
        full = SampleSet.objects.get(uuid="full")
        self.assertLess(empty.samplesethomestatus_set.current().count(), settings.SAMPLING_MAX_SIZE)
        self.assertEqual(empty.is_full(), False)
        self.assertEqual(full.samplesethomestatus_set.current().count(), settings.SAMPLING_MAX_SIZE)
        self.assertEqual(full.is_full(), True)

    def test_get_current_items(self):
        """Return only the samplesethomestatus objects where revision matches the sampleset."""
        sampleset = SampleSet.objects.get(uuid="generic")
        queryset = sampleset.samplesethomestatus_set.current()

        # Independently get these intended items
        current_items = SampleSetHomeStatus.objects.filter(
            sampleset=sampleset, revision=sampleset.revision
        )

        self.assertEqual(set(queryset), set(current_items))

    def test_get_saved_items(self):
        """Return only the samplesethomestatus objects where revision is less than the sampleset."""
        sampleset = SampleSet.objects.get(uuid="multistage")
        queryset = sampleset.samplesethomestatus_set.saved()

        # Independently get these intended items
        saved_items = SampleSetHomeStatus.objects.filter(
            sampleset=sampleset, revision__lt=sampleset.revision
        )

        self.assertEqual(set(queryset), set(saved_items))

    # def test_systems_questions_expansion(self):
    #     """
    #     Questions fetched from a sampleset should be those that match the EEP checklist, unless
    #     there are System objects found for the home, which should have the power to duplicate
    #     certain questions with matching system types.
    #     """
    #
    #     raise NotImplementedError("Need to test systems expansion code.")

    def test_get_source_answers(self):
        """
        Answered found as "source" answers only include items that come from the Home checklist or
        the bulk uploader.
        """
        sampleset = SampleSet.objects.get(uuid="generic")
        sshs = sampleset.samplesethomestatus_set.filter(is_test_home=True)[0]
        queryset = sshs.get_source_answers()

        # Independently fetch the same data.
        # Answers should come from only the test home(s) in the sampleset.
        answers = Answer.objects.filter(home=sshs.home_status.home)
        self.assertEqual(set(queryset), set(answers))

    def test_advance(self):
        """
        SampleSet.advance() should duplicate all current items with a bumped revision, and leave
        behind a copy of new answers from test homes on the sampled homes.
        """
        sampleset = SampleSet.objects.get(uuid="generic")
        num_old_items = sampleset.samplesethomestatus_set.all().count()
        old_revision = sampleset.revision
        test_answers = sampleset.get_current_source_answers()
        self.assertNotEqual(sampleset.samplesethomestatus_set.current().count(), 0)
        self.assertNotEqual(test_answers.count(), 0)

        sampleset.advance()

        # Revision gets bumped
        self.assertEqual(old_revision + 1, sampleset.revision)

        # Ensure new quantity is expected
        num_new_items = sampleset.samplesethomestatus_set.all().count()
        self.assertEqual(num_old_items * 2, num_new_items)

        # Verify individual items being mirrored
        for item in sampleset.samplesethomestatus_set.current():
            old_item = sampleset.samplesethomestatus_set.get(
                home_status=item.home_status, revision=old_revision
            )
            self.assertEqual(old_revision, old_item.revision)
            self.assertEqual(old_revision + 1, item.revision)

            # Answers got pushed to old_item
            if old_item.is_test_home:
                # test homes won't end up receiving pushed answers because they already have a
                # separate reference to that answer.
                self.assertEqual(old_item.answers.count(), 0)
            else:
                self.assertEqual(old_item.answers.count(), test_answers.count())

        # Do it again
        sampleset.advance()

        # Assumptions
        self.assertEqual(old_revision + 2, sampleset.revision)
        num_new_items = sampleset.samplesethomestatus_set.all().count()
        self.assertEqual(num_old_items * 3, num_new_items)

        # This time, the answers were already accounted for and should not have been pushed again
        for item in sampleset.samplesethomestatus_set.current():
            previous_item = sampleset.samplesethomestatus_set.get(
                home_status=item.home_status, revision=old_revision + 1
            )
            self.assertEqual(previous_item.answers.count(), 0)

    def test_discover_builder_org(self):
        """BuilderOrganization can be fetched dynamically from sampleset."""
        from axis.home.models import EEPProgramHomeStatus

        generic = SampleSet.objects.get(uuid="generic")
        builder = generic.discover_builder_org()
        self.assertEqual(
            builder, generic.samplesethomestatus_set.all()[0].home_status.home.get_builder()
        )

        # It should return False if multiple builders are in the sampleset
        home_status = EEPProgramHomeStatus.objects.get(company__name="loose_objects")
        generic.add_home_status(home_status)
        builder = generic.discover_builder_org()
        self.assertEqual(builder, False)

        # It should return None if nothing's in the sampleset
        empty = SampleSet.objects.get(uuid="empty")
        builder = empty.discover_builder_org()
        self.assertEqual(builder, None)

    def test_discover_subdivision(self):
        """Subdivision can be fetched dynamically from sampleset."""
        from axis.home.models import EEPProgramHomeStatus

        generic = SampleSet.objects.get(uuid="generic")
        subdivision = generic.discover_subdivision()
        self.assertEqual(
            subdivision, generic.samplesethomestatus_set.all()[0].home_status.home.subdivision
        )

        # It should return False if multiple subdivisions are in the sampleset
        home_status = EEPProgramHomeStatus.objects.get(company__name="loose_objects")
        generic.add_home_status(home_status)
        subdivision = generic.discover_subdivision()
        self.assertEqual(subdivision, False)

        # It should return None if nothing's in the sampleset
        empty = SampleSet.objects.get(uuid="empty")
        subdivision = empty.discover_subdivision()
        self.assertEqual(subdivision, None)

    def test_discover_eep_program(self):
        """EEPProgram can be fetched dynamically from sampleset."""
        from axis.home.models import EEPProgramHomeStatus

        generic = SampleSet.objects.get(uuid="generic")
        eep_program = generic.discover_eep_program()
        self.assertEqual(
            eep_program, generic.samplesethomestatus_set.all()[0].home_status.eep_program
        )

        # It should return False if multiple programs are in the sampleset
        home_status = EEPProgramHomeStatus.objects.get(company__name="loose_objects")
        generic.add_home_status(home_status)
        eep_program = generic.discover_eep_program()
        self.assertEqual(eep_program, False)

        # It should return None if nothing's in the sampleset
        empty = SampleSet.objects.get(uuid="empty")
        eep_program = empty.discover_eep_program()
        self.assertEqual(eep_program, None)

    def test_discover_is_metro_sampled(self):
        """is_metro_sampled can be fetched dynamically from sampleset."""
        from axis.home.models import EEPProgramHomeStatus

        generic = SampleSet.objects.get(uuid="generic")
        is_metro_sampled = generic.discover_is_metro_sampled()
        self.assertEqual(is_metro_sampled, False)

        # It should return True if multiple metros are in the sampleset
        home_status = EEPProgramHomeStatus.objects.get(company__name="loose_objects")
        generic.add_home_status(home_status)
        is_metro_sampled = generic.discover_is_metro_sampled()
        self.assertEqual(is_metro_sampled, True)


class SampleSetHomeStatusModelTests(SampleSetTestMixin, TestCase, AxisTestCaseUserMixin):
    def test_get_source_answers(self):
        """Returns only answers that have been provided directly to the home (checklist/upload)."""
        generic = SampleSet.objects.get(uuid="generic")
        test_home = generic.samplesethomestatus_set.filter(is_test_home=True)[0]
        sampled_home = generic.samplesethomestatus_set.filter(is_test_home=False)[0]

        queryset = test_home.get_source_answers()
        self.assertNotEqual(queryset.count(), 0)
        self.assertEqual(set(queryset), set(test_home.home_status.home.answer_set.all()))

        queryset = sampled_home.get_source_answers()
        self.assertEqual(queryset.count(), 0)
        self.assertEqual(set(queryset), set(sampled_home.home_status.home.answer_set.all()))

    def test_get_contributed_answers(self):
        """Returns only answers that have been shared previously to the home via sampling."""
        multistage = SampleSet.objects.get(uuid="multistage")
        test_home = multistage.samplesethomestatus_set.current().filter(is_test_home=True)[0]
        sampled_home = multistage.samplesethomestatus_set.current().filter(is_test_home=False)[0]
        contributed_answers = set(Answer.objects.filter(samplesethomestatus__sampleset=multistage))

        queryset = test_home.get_source_answers()
        self.assertNotEqual(queryset.count(), 0)
        self.assertEqual(set(queryset), contributed_answers)

        queryset = sampled_home.get_contributed_answers()
        self.assertNotEqual(queryset.count(), 0)
        self.assertEqual(set(queryset), contributed_answers)

    def test_get_contributed_answers_retrievable_via_unsaved_standin(self):
        """
        Provided a home_status_id value, an unsaved SampleSetHomeStatus instance can still fetch
        contributed answer data, since it is identified by OTHER instances of this homestatus.
        """
        multistage = SampleSet.objects.get(uuid="multistage")
        test_homes = multistage.samplesethomestatus_set
        sampled_home = multistage.samplesethomestatus_set.current().filter(is_test_home=False)[0]
        contributed_answers = set(Answer.objects.filter(samplesethomestatus__sampleset=multistage))

        unsaved = SampleSetHomeStatus()
        unsaved.id = sampled_home.id
        unsaved.home_status_id = sampled_home.home_status.id

        queryset = unsaved.get_contributed_answers()
        self.assertNotEqual(queryset.count(), 0)
        self.assertEqual(set(queryset), contributed_answers)

    def test_find_existing_answers(self):
        """Existing answers are found from checklist/bulk assignment and past samplesets."""
        multistage = SampleSet.objects.get(uuid="multistage")
        test_home = multistage.samplesethomestatus_set.current().filter(is_test_home=True)[0]
        test_home_old = multistage.samplesethomestatus_set.saved().filter(
            home_status=test_home.home_status
        )[0]

        # Make sure there is past data from checklist/bulk.
        self.assertNotEqual(test_home.home_status.home.answer_set.count(), 0)

        # Verify the return value is these two things combined
        queryset = test_home.find_existing_answers()
        answers = test_home.get_source_answers() | test_home.get_contributed_answers()
        self.assertEqual(set(queryset), set(answers))

    def test_find_new_test_answers(self):
        """New answers are found from excluding checklist/bulk assignment and past samplesets."""
        multistage = SampleSet.objects.get(uuid="multistage")
        test_home = multistage.samplesethomestatus_set.current().filter(is_test_home=True)[0]

        # Make sure there is past data from checklist/bulk.
        self.assertNotEqual(test_home.home_status.home.answer_set.count(), 0)

        # Verify the return value is empty, since all answers are already covered.
        queryset = test_home.find_new_test_answers()
        self.assertEqual(set(queryset), set())

    def test_find_unanswered_questions(self):
        """Questions without answers already advanced to them are returned upon request."""
        sampleset = SampleSet.objects.get(uuid="generic")
        sampled_home = sampleset.samplesethomestatus_set.current().filter(is_test_home=False)[0]
        questions = sampled_home.get_questions()
        answered = sampled_home.find_answered_questions()
        unanswered = sampled_home.find_unanswered_questions()

        # Verify assumptions about how these numbers stack up so that our test is worth running.
        self.assertNotEqual(questions.count(), 0)
        self.assertNotEqual(answered.count(), questions.count())
        self.assertNotEqual(unanswered.count(), 0)
        self.assertEqual(unanswered.count() + answered.count(), questions.count())

        # Core of the method's behavior
        self.assertEqual(set(questions) - set(answered), set(unanswered))
        for question in unanswered:
            self.assertEqual(
                question.answer_set.filter(home=sampled_home.home_status.home).count(), 0
            )
        for question in answered:
            self.assertNotEqual(
                question.answer_set.filter(home=sampled_home.home_status.home).count(), 0
            )

    def test_find_uncovered_questions(self):
        """
        Uncovered questions are those that have no advanced answers, and don't appear to be covered
        by the current sampleset if it were to be advanced right now.
        """
        sampleset = SampleSet.objects.get(uuid="multistage_incomplete")
        sampled_home = sampleset.samplesethomestatus_set.current().filter(is_test_home=False)[0]
        questions = sampled_home.get_questions()
        answered = sampled_home.find_answered_questions()
        unanswered = sampled_home.find_unanswered_questions()

        # Verify assumptions about how these numbers stack up so that our test is worth running.
        self.assertNotEqual(questions.count(), 0)
        self.assertNotEqual(answered.count(), questions.count())
        self.assertNotEqual(unanswered.count(), 0)
        self.assertEqual(unanswered.count() + answered.count(), questions.count())

        # Core of the tested behavior
        uncovered = sampled_home.find_uncovered_questions()
        self.assertNotEqual(uncovered.count(), 0)
        self.assertEqual(uncovered.count(), unanswered.count())
        self.assertEqual(uncovered.count(), questions.count() - answered.count())


class SampleSetQueryTests(SampleSetTestMixin, TestCase, AxisTestCaseUserMixin):
    def test_filter_answers_across_programs(self):
        """
        Test homes supply answers reguardless of source program, as long as the question ids match
        (i.e., the question object is re-used in multiple programs).
        """
        sampleset = SampleSet.objects.get(uuid="mixed_programs")

        normal_ssitem = sampleset.samplesethomestatus_set.all()[0]
        mixed_ssitem = sampleset.samplesethomestatus_set.get(
            home_status__eep_program__name="ugly_duckling"
        )

        normal_item = normal_ssitem.home_status
        mixed_item = mixed_ssitem.home_status

        ## Confirm the assumptions about the proper test conditions

        self.assertEqual(normal_ssitem.is_test_home, True)
        self.assertEqual(mixed_ssitem.is_test_home, True)

        # Verify the odd program out is the superset of the other
        normal_questions = normal_item.eep_program.get_checklist_question_set()
        mixed_questions = mixed_item.eep_program.get_checklist_question_set()
        self.assertLess(set(normal_questions), set(mixed_questions))

        # Verify that there is an overlap of question ids
        normal_question_ids = normal_questions.values_list("id", flat=True)
        mixed_question_ids = mixed_questions.values_list("id", flat=True)
        self.assertNotEqual({}, set(mixed_question_ids) & set(normal_question_ids))

        # Verify that there are answers associated to the shared questions (don't care about others)
        normal_answers = normal_item.home.answer_set.filter(question__in=normal_questions)
        mixed_answers = mixed_item.home.answer_set.filter(question__in=mixed_questions)
        self.assertNotEqual(0, normal_answers.count())
        self.assertNotEqual(0, mixed_answers.count())

        ## Actual test

        answers = sampleset.get_current_source_answers()

        # Verify that answers from both test homes are in the queryset
        self.assertNotEqual(0, answers.filter(home=normal_item.home).count())
        self.assertNotEqual(0, answers.filter(home=mixed_item.home).count())
