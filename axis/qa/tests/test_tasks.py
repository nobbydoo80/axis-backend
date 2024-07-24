"""test_tasks.py - Axis"""
import datetime
import logging

from django.contrib.auth import get_user_model
from django.core import mail

from axis.core.tests.testcases import AxisTestCase
from axis.home.models import EEPProgramHomeStatus
from axis.messaging.models import Message, MessagingPreference
from axis.qa.models import QARequirement, QAStatus
from axis.qa.tasks import (
    update_notify_opportunities,
    update_qa_states,
    correction_required_daily_email,
    qa_review_fail_daily_email,
)
from axis.relationship.models import Relationship
from .mixins import QATestMixin
from ..messages import QaRecommendedMessage
from ...core.tests.factories import qa_admin_factory

log = logging.getLogger(__name__)

User = get_user_model()

__author__ = "Steven K"
__date__ = "4/13/21 10:12"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]


class QATaskTests(QATestMixin, AxisTestCase):
    """Test out homes tasks"""

    def test_non_gating_qa_states(self):
        """Verifies that a non-gating QA Program will not"""
        from axis.home.tasks import update_home_states

        requirement = QARequirement.objects.create(
            qa_company=self.qa.company, gate_certification=False, eep_program=self.eep_program
        )

        qa_status = QAStatus.objects.create(
            owner=self.qa.company, requirement=requirement, home_status=self.home_status
        )
        self.assertEqual(qa_status.state, "received")

        update_home_states(eepprogramhomestatus_id=self.home_status.id)
        update_qa_states(qa_status_id=qa_status.id)

        self.assertEqual(
            EEPProgramHomeStatus.objects.get(id=self.home_status.id).state, "certification_pending"
        )
        self.assertEqual(QAStatus.objects.get(id=qa_status.id).state, "in_progress")

    def test_gating_qa_states(self):
        """Verifies that a gating QA Program will Gate Certification"""
        from axis.home.tasks import update_home_states

        requirement = QARequirement.objects.create(
            qa_company=self.qa.company,
            gate_certification=True,
            eep_program=self.eep_program,
            coverage_pct=0.51,
        )

        qa_status = QAStatus.objects.create(
            owner=self.qa.company, requirement=requirement, home_status=self.home_status
        )
        self.assertEqual(qa_status.state, "received")

        update_home_states(eepprogramhomestatus_id=self.home_status.id)
        self.assertTrue(self.home_status.is_eligible_for_certification())
        update_qa_states(qa_status_id=qa_status.id)

        self.assertEqual(
            EEPProgramHomeStatus.objects.get(id=self.home_status.id).state, "qa_pending"
        )
        self.assertEqual(QAStatus.objects.get(id=qa_status.id).state, "in_progress")

        # Complete the QA
        qa_status = QAStatus.objects.get(id=qa_status.id)
        qa_status.state = "complete"
        qa_status.result = "pass"
        qa_status.save()

        update_qa_states(qa_status_id=qa_status.id)
        self.assertEqual(QAStatus.objects.get(id=qa_status.id).state, "complete")

        update_home_states(eepprogramhomestatus_id=self.home_status.id)
        stat = EEPProgramHomeStatus.objects.get(id=self.home_status.id)
        self.assertEqual(stat.state, "certification_pending")

    def test_pct_qa_requirements(self):
        from axis.home.tasks import update_home_states
        from axis.home.tests.factories import custom_home_factory

        Message.objects.all().delete()
        self.assertEqual(Message.objects.all().count(), 0)

        requirement, create = QARequirement.objects.get_or_create(
            qa_company=self.qa.company,
            gate_certification=False,
            eep_program=self.eep_program,
            coverage_pct=0.51,
        )

        # Verify we send a message..
        update_notify_opportunities(home_status_id=self.home_status.id)
        self.assertGreaterEqual(Message.objects.all().count(), 1)
        messages = Message.objects.all().count()

        # Add QA verify we don't send another message..
        qa_status = QAStatus.objects.create(
            owner=self.qa.company, requirement=requirement, home_status=self.home_status
        )

        update_notify_opportunities(home_status_id=self.home_status.id)
        self.assertEqual(Message.objects.all().count(), messages)

        self.assertEqual(qa_status.requirement, requirement)

        req = QARequirement.objects.get(id=requirement.id)
        self.assertEqual(req.get_active_coverage_pct(), 1)

        # Add another home which will not put us over the threshold (50%)
        home = custom_home_factory(builder_org=self.builder.company)
        # TODO We may need to look at this as it requires a relationship to the home to be
        # considered..
        Relationship.objects.validate_or_create_relations_to_entity(home, self.qa.company)
        home_status = EEPProgramHomeStatus.objects.create(
            eep_program=self.eep_program, company=self.rater.company, home=home
        )
        update_home_states(eepprogramhomestatus_id=home_status.id)
        update_notify_opportunities(home_status_id=home_status.id)

        # No real Change..
        req = QARequirement.objects.get(id=requirement.id)
        self.assertEqual(req.get_active_coverage_pct(), 0.5)
        self.assertEqual(Message.objects.all().count(), messages + 2)  # Notified of opportunity

        # And one more the bounce the message..
        home = custom_home_factory(builder_org=self.builder.company)
        Relationship.objects.validate_or_create_relations_to_entity(home, self.qa.company)
        home_status = EEPProgramHomeStatus.objects.create(
            eep_program=self.eep_program, company=self.rater.company, home=home
        )
        update_home_states(eepprogramhomestatus_id=home_status.id)
        update_notify_opportunities(home_status_id=home_status.id)

        # No real Change..
        req = QARequirement.objects.get(id=requirement.id)
        self.assertEqual(req.get_active_coverage_pct(), float(1) / float(3))
        self.assertGreater(Message.objects.all().count(), messages)
        messages = Message.objects.all().count()

        # Multiple saves should not increase messages.
        update_notify_opportunities(home_status_id=home_status.id)
        self.assertEqual(Message.objects.all().count(), messages)

    def test_correction_emails(self):
        requirement, qa_status = self._get_requirement_and_qa_status()

        self.assertEqual(qa_status.state, "received")
        correction_required_daily_email(ignore_dates=True)
        self.assertEqual(len(mail.outbox), 0)

        qa_status.make_transition("received_to_in_progress", user=self.qa)
        self.assertEqual(qa_status.state, "in_progress")
        correction_required_daily_email(ignore_dates=True)
        self.assertEqual(len(mail.outbox), 0)

        qa_status.make_transition("in_progress_to_correction_required", user=self.qa)
        self.assertEqual(qa_status.state, "correction_required")
        correction_required_daily_email()
        self.assertEqual(len(mail.outbox), 0)

        correction_required_daily_email(ignore_dates=True, user=self.qa)
        self.assertEqual(len(mail.outbox), 1)

        # Verify that the subject of the first message is correct.
        self.assertEqual(
            mail.outbox[0].subject,
            "Daily QA Report - 1 outstanding project(s) have QA corrections requested",
        )
        self.assertIn("1 project(s) require outstanding corrections", mail.outbox[0].body)

        self.assertEqual(len(mail.outbox[0].alternatives), 1)
        self.assertEqual(mail.outbox[0].alternatives[0][1], "text/html")

        text = '<a href="https://pivotalenergy.net/home/{home_id}/">{home}'.format(
            home_id=self.home_status.home.id, home=str(self.home_status.home)
        )
        self.assertIn(text, mail.outbox[0].alternatives[0][0])

        # No further emails go out.
        qa_status.make_transition("correction_required_to_correction_received", user=self.rater)
        self.assertEqual(qa_status.state, "correction_received")
        correction_required_daily_email(ignore_dates=True)
        self.assertEqual(len(mail.outbox), 1)

        qa_status.make_transition("correction_received_to_complete", user=self.qa)
        self.assertEqual(qa_status.state, "complete")
        correction_required_daily_email(ignore_dates=True)
        self.assertEqual(len(mail.outbox), 1)

    def test_qa_review_fail_daily_email(self):
        requirement, qa_status = self._get_requirement_and_qa_status()
        qa_status.make_transition("received_to_in_progress", user=self.qa)
        qa_status.make_transition("in_progress_to_complete", user=self.qa)
        qa_status.status = "pass"
        qa_status.has_failed = False
        qa_status.save()

        qa_review_fail_daily_email(ignore_dates=True)
        self.assertEqual(len(mail.outbox), 0)

        qa_status.state = "complete"
        qa_status.result = "fail"
        qa_status.has_failed = True
        qa_status.save()

        qa_review_fail_daily_email(ignore_dates=True)
        # rater and utility companies receive notification
        self.assertGreater(len(mail.outbox), 0)

        self.assertIn("1 Failed QA in Axis", mail.outbox[0].subject)
        self.assertIn("1 project(s) have Failed QA in Axis", mail.outbox[0].body)

        self.assertEqual(len(mail.outbox[0].alternatives), 1)
        self.assertEqual(mail.outbox[0].alternatives[0][1], "text/html")
        self.assertIn(qa_status.home_status.home.get_addr(), mail.outbox[0].alternatives[0][0])

    # def test_pct_qa_requirements_multiple_emails(self):
    #     """Prevent multiple emails from going on the same task."""
    #     Message.objects.all().delete()
    #
    #     # Make sure we get this email
    #     modern_message = QaRecommendedMessage()
    #     MessagingPreference.objects.create(
    #         message_name="QaRecommendedMessage",
    #         user=self.qa,
    #         category=modern_message.category,
    #         receive_email=True,
    #         receive_notification=True,
    #     )
    #
    #     self.assertEqual(Message.objects.all().count(), 0)
    #     self.assertEqual(len(mail.outbox), 0)
    #
    #     QARequirement.objects.get_or_create(
    #         qa_company=self.qa.company,
    #         gate_certification=False,
    #         eep_program=self.eep_program,
    #         coverage_pct=0.51,
    #     )
    #
    #     # Verify we send a message
    #     update_notify_opportunities(home_status_id=self.home_status.id)
    #     self.assertEqual(Message.objects.filter(user=self.qa).count(), 1)
    #     self.assertEqual(len(mail.outbox), 1)
    #
    #     # Ensure we don't get caught in debounce
    #     debounce_time = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=1)
    #     Message.objects.all().update(date_created=debounce_time)
    #
    #     self.home_status.save()
    #
    #     update_notify_opportunities(home_status_id=self.home_status.id)
    #     self.assertEqual(Message.objects.filter(user=self.qa).count(), 1)
    #     self.assertEqual(len(mail.outbox), 1)
    #
    #     Message.objects.all().update(date_created=debounce_time)
    #     self.home_status.save()
    #
    #     # Note this changed b/c it's unique only.
    #     update_notify_opportunities(home_status_id=self.home_status.id)
    #     self.assertEqual(Message.objects.filter(user=self.qa).count(), 1)
    #     self.assertEqual(len(mail.outbox), 1)

    def test_pct_qa_requirements_not_attached(self):
        """If you have multiple QA Companies send Recommended if you are attached"""
        Message.objects.all().delete()

        self.assertEqual(Message.objects.all().count(), 0)

        # This is not attached to this home.  They should not get a notice.
        alt_qa = qa_admin_factory()
        Relationship.objects.create_mutual_relationships(self.home_status.company, alt_qa.company)

        QARequirement.objects.get_or_create(
            qa_company=alt_qa.company,
            gate_certification=False,
            eep_program=self.eep_program,
            coverage_pct=0.99,
        )
        # We are not attached.
        self.assertNotIn(
            alt_qa.company.id,
            list(self.home_status.home.relationships.values_list("company", flat=True)),
        )
        self.assertEqual(QARequirement.objects.filter_for_home_status(self.home_status).count(), 0)
        update_notify_opportunities(home_status_id=self.home_status.id)
        self.assertEqual(Message.objects.all().count(), 0)
