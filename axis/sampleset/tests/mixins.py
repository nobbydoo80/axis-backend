""" SampleSet fixture compilers for tests. """


__author__ = "Autumn Valenta"
__date__ = "07-11-14 11:55 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


import logging

from django.conf import settings

from axis.checklist.tests.factories import answer_factory
from axis.core.tests.factories import rater_user_factory, basic_user_factory
from axis.home.tests.factories import (
    eep_program_home_status_factory,
    eep_program_checklist_home_status_factory,
)
from axis.geographic.tests.factories import real_city_factory
from .factories import empty_sampleset_factory, sampleset_with_subdivision_homes_factory

log = logging.getLogger(__name__)


class SampleSetTestMixin:
    @classmethod
    def setUpTestData(cls):
        cls.city = real_city_factory("Skowhegan", "ME")

        basic_user_factory(username="noperm_user")
        checklist_user = rater_user_factory(username="checklist_answerer", company__city=cls.city)

        empty_sampleset_factory(uuid="empty")
        sampleset_with_subdivision_homes_factory(
            uuid="generic",
            subdivision__city=cls.city,
            subdivision__builder_org__name="builder1",
            eep_program__question_count=10,
            pct_complete=76,
        )
        sampleset_with_subdivision_homes_factory(
            uuid="full",
            subdivision__city=cls.city,
            subdivision__builder_org__name="builder2",
            num_homes=settings.SAMPLING_MAX_SIZE,
        )
        sampleset_with_subdivision_homes_factory(
            uuid="multistage",
            revision=3,
            subdivision__city=cls.city,
            subdivision__builder_org__name="builder3",
            pct_complete=100,
            eep_program__question_count=10,
        )
        sampleset_with_subdivision_homes_factory(
            uuid="multistage_incomplete",
            revision=3,
            subdivision__city=cls.city,
            subdivision__builder_org__name="builder4",
            pct_complete=90,
            eep_program__question_count=10,
        )
        sampleset_with_subdivision_homes_factory(
            subdivision__city=cls.city,
            subdivision__builder_org__name="builder5",
            eep_program__question_count=10,
            uuid="accurate",
            pct_complete=76,
            num_test_homes=2,
            num_homes=settings.SAMPLING_MAX_SIZE,
        )

        # Build a sampleset that contains multiple programs, where the mismatched program has some
        # overlapping question ids with the rest of the group.  Move some of the answers from a
        # normal item over to the mismatched item.
        ss_mixed = sampleset_with_subdivision_homes_factory(
            uuid="mixed_programs", eepprogramhomestatus__company=checklist_user.company
        )

        other_homestatus = eep_program_checklist_home_status_factory(
            eep_program__name="ugly_duckling",
            eep_program__no_close_dates=True,
            company=checklist_user.company,
        )

        shared_questions = ss_mixed.home_statuses.all()[0].eep_program.get_checklist_question_set()

        other_homestatus.eep_program.required_checklists.all()[0].questions.add(*shared_questions)

        test_status = ss_mixed.samplesethomestatus_set.filter(is_test_home=True)[0]

        other_status = ss_mixed.add_home_status(
            other_homestatus, is_test_home=True, revision=ss_mixed.revision
        )

        for i, question in enumerate(shared_questions):
            # Drop half the answers on the normal item, half on the mismatched item.
            if i % 2:
                target = test_status
            else:
                target = other_status
            answer_factory(question, target.home_status.home, checklist_user)

        # Add a loose object for tests to use without confusion of pre-existing membership in the
        # sampleset.
        eep_program_home_status_factory(
            company__name="loose_objects", eep_program__no_close_dates=True
        )
