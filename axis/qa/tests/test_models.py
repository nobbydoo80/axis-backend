"""test_models.py: Django qa"""

__author__ = "Steven Klass"
__date__ = "1/20/14 12:55 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

import logging
import random
from unittest.mock import patch

from django.apps import apps
from django.contrib.auth import get_user_model
from django.utils import timezone
from freezegun import freeze_time

from axis.company.tests.factories import provider_organization_factory
from axis.core.tests.factories import provider_user_factory, rater_user_factory
from axis.core.tests.testcases import AxisTestCase
from axis.eep_program.tests.factories import basic_eep_program_factory
from axis.home.models import EEPProgramHomeStatus
from axis.messaging.models import Message
from .factories import qa_requirement_factory, qa_status_factory
from .mixins import QATestMixin
from ..models import QARequirement, QAStatus

User = get_user_model()

log = logging.getLogger(__name__)


customer_hirl_app = apps.get_app_config("customer_hirl")


class QAModelTests(QATestMixin, AxisTestCase):
    """Test out homes app"""

    def test_only_stores_states_that_have_been_transitioned_to(self):
        requirement, qa_status = self._get_requirement_and_qa_status()

        qa_status.make_transition("received_to_in_progress", user=self.qa)
        qa_status.make_transition("in_progress_to_correction_required", user=self.qa)
        temp = QAStatus.objects.get_qa_metrics_for_home_statuses([self.home_status.id])
        self.assertEqual(len(temp["transitions"]), 2)
        self.assertEqual(len(temp["to_states"]), 2)

    def test_adds_count_on_to_state_for_transition(self):
        requirement, qa_status = self._get_requirement_and_qa_status()

        qa_status.make_transition("received_to_in_progress", user=self.qa)
        qa_status.make_transition("in_progress_to_correction_required", user=self.qa)
        qa_status.make_transition("correction_required_to_correction_received")
        qa_status.make_transition("correction_received_to_correction_required", user=self.qa)
        qa_status.make_transition("correction_required_to_correction_received")
        qa_status.make_transition("correction_received_to_correction_required", user=self.qa)

        temp = QAStatus.objects.get_qa_metrics_for_home_statuses([self.home_status.id])
        counts = temp[self.home_status.id]["counts"]["file"]

        self.assertEqual(counts["in_progress"], 2)
        self.assertEqual(counts["correction_required"], 3)
        self.assertEqual(counts["correction_received"], 2)
        self.assertEqual(
            len(temp[self.home_status.id]["transitions"]["file"]), 7, "Did not get all transitions."
        )

    def test_rater_receives_message_when_corrections_are_required(self):
        requirement, qa_status = self._get_requirement_and_qa_status(qa_status_state="in_progress")

        self.assertEqual(Message.objects.count(), 0)
        qa_status.make_transition("in_progress_to_correction_required")
        self.assertEqual(Message.objects.first().user.company, self.home_status.company)

    def test_qa_company_receives_message_when_corrections_have_been_received(self):
        requirement, qa_status = self._get_requirement_and_qa_status(
            qa_status_state="correction_required"
        )

        self.assertEqual(Message.objects.count(), 0)
        qa_status.make_transition("correction_required_to_correction_received")
        self.assertEqual(Message.objects.first().user.company, qa_status.owner)

    def test_provider_receives_message_when_gating_qa_is_complete(self):
        requirement, qa_status = self._get_requirement_and_qa_status(
            qa_status_state="in_progress", requirement_gate_certification=True
        )
        provider_company = self.home_status.get_provider()

        self.assertEqual(Message.objects.count(), 0)
        qa_status.make_transition("in_progress_to_complete")
        self.assertEqual(
            Message.objects.filter(user__company=provider_company).count(),
            provider_company.users.count(),
        )

    def test_rater_receives_message_when_gating_qa_is_complete(self):
        requirement, qa_status = self._get_requirement_and_qa_status(
            qa_status_state="in_progress", requirement_gate_certification=True
        )
        rater_company = self.home_status.company

        self.assertEqual(Message.objects.count(), 0)
        qa_status.make_transition("in_progress_to_complete")
        self.assertEqual(
            Message.objects.filter(user__company=rater_company).count(), rater_company.users.count()
        )

    def test_adding_field_qa_creates_home_status_with_qa_program(self):
        self.assertEqual(
            EEPProgramHomeStatus.objects.filter(eep_program=self.qa_eep_program).count(), 0
        )
        self._get_requirement_and_qa_status(requirement_type="field")
        self.assertEqual(
            EEPProgramHomeStatus.objects.filter(eep_program=self.qa_eep_program).count(), 1
        )

    def test_deleting_field_qa_deletes_home_status_with_qa_program(self):
        requirement, qa_status = self._get_requirement_and_qa_status(requirement_type="field")

        self.assertEqual(
            EEPProgramHomeStatus.objects.filter(eep_program=self.qa_eep_program).count(), 1
        )
        qa_status.delete()
        self.assertEqual(
            EEPProgramHomeStatus.objects.filter(eep_program=self.qa_eep_program).count(), 0
        )

    def test_qastatus_requires_homestatus_or_subdivision_fk_not_both(self):
        requirement, qa_status = self._get_requirement_and_qa_status(requirement_type="file")
        subdivision = self.home_status.home.subdivision
        self.assertIsNotNone(subdivision)
        qa_status.subdivision = subdivision
        with self.assertRaisesMessage(
            ValueError, "Only allowed to have one of: home_status, subdivision"
        ):
            qa_status.save()
        qa_status.home_status = None
        qa_status.save()

    def test_subdivision_qastatus_type_limited_to_file(self):
        requirement, qa_status = self._get_requirement_and_qa_status(requirement_type="field")
        subdivision = self.home_status.home.subdivision
        self.assertIsNotNone(subdivision)

        qa_status.home_status = None
        qa_status.subdivision = subdivision
        with self.assertRaisesMessage(ValueError, "Unsupported QA type for Subdivision: field"):
            qa_status.save()

    @patch("axis.qa.models.CustomerHIRLQADesigneeAssigneeMessage.send")
    @patch("axis.qa.models.QADesigneeAssigneeMessage.send")
    def test_qa_designee_change_notification(
        self, send_qa_designee_message, customer_hirl_send_qa_designee_message
    ):
        requirement = QARequirement.objects.create(
            qa_company=self.qa.company,
            eep_program=self.eep_program,
            type=QARequirement.FILE_QA_REQUIREMENT_TYPE,
            gate_certification=True,
        )
        qa_status = QAStatus.objects.create(
            owner=self.qa.company,
            state="received",
            requirement=requirement,
            home_status=self.home_status,
            qa_designee=self.rater,
        )

        send_qa_designee_message.assert_called_once()
        self.assertEqual(customer_hirl_send_qa_designee_message.call_count, 0)

        with self.subTest("Customer HIRL QA Designee assigned"):
            hirl_company = provider_organization_factory(
                name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
            )
            hirl_user = provider_user_factory(
                first_name="NGBS", last_name="Admin", company=hirl_company, is_company_admin=True
            )
            qa_status.qa_designee = hirl_user
            qa_status.save()

            send_qa_designee_message.assert_called_once()
            customer_hirl_send_qa_designee_message.assert_called_once()

    @patch("axis.qa.state_machine.CustomerHIRLQaCorrectionReceivedMessage.send")
    def test_customer_hirl_qa_correction_received(self, send_correction_received_message):
        hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )
        hirl_user = provider_user_factory(
            first_name="NGBS", last_name="Admin", company=hirl_company, is_company_admin=True
        )
        verifier = rater_user_factory(first_name="Kent", last_name="Mitchell")
        eep_program = basic_eep_program_factory(
            slug=random.choice(customer_hirl_app.HIRL_PROJECT_EEP_PROGRAM_SLUGS)
        )
        requirement = qa_requirement_factory(
            eep_program=eep_program,
            qa_company=hirl_company,
            type=QARequirement.ROUGH_INSPECTION_QA_REQUIREMENT_TYPE,
        )

        qa_status = qa_status_factory(
            requirement=requirement,
            state="correction_required",
            qa_designee=hirl_user,
            home_status__eep_program=eep_program,
            home_status__customer_hirl_rough_verifier=verifier,
        )

        qa_status.make_transition("correction_required_to_correction_received")
        send_correction_received_message.assert_called_once()

    def test_annotate_state_cycle_time_duration(self):
        hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )
        hirl_user = provider_user_factory(
            first_name="NGBS", last_name="Admin", company=hirl_company, is_company_admin=True
        )
        verifier = rater_user_factory(first_name="Kent", last_name="Mitchell")
        eep_program = basic_eep_program_factory(
            slug=random.choice(customer_hirl_app.HIRL_PROJECT_EEP_PROGRAM_SLUGS)
        )
        requirement = qa_requirement_factory(
            eep_program=eep_program,
            qa_company=hirl_company,
            type=QARequirement.ROUGH_INSPECTION_QA_REQUIREMENT_TYPE,
        )

        initial_datetime = timezone.datetime(
            year=2014, month=7, day=12, hour=15, minute=6, second=3
        )
        with freeze_time(initial_datetime) as frozen_datetime:
            with self.subTest("Check duration if we do not have state_history"):
                created_on = timezone.now() - timezone.timedelta(days=1)

                qa_status = qa_status_factory(
                    requirement=requirement,
                    state="correction_required",
                    qa_designee=hirl_user,
                    home_status__eep_program=eep_program,
                    home_status__customer_hirl_rough_verifier=verifier,
                )
                qa_status.created_on = created_on
                qa_status.save()

                self.assertEqual(qa_status.created_on, created_on)
                # Make sure we do not have state history
                self.assertEqual(qa_status.state_history.count(), 0)

                qa_status = (
                    QAStatus.objects.filter(id=qa_status.id)
                    .annotate_last_state_cycle_time_duration()
                    .first()
                )

                self.assertEqual(
                    qa_status.state_cycle_time_duration, timezone.now() - qa_status.created_on
                )

            with self.subTest("Check duration if we have state_history"):
                frozen_datetime.tick()
                qa_status.make_transition("correction_required_to_correction_received")
                self.assertEqual(qa_status.state_history.count(), 1)

                qa_status = (
                    QAStatus.objects.filter(id=qa_status.id)
                    .annotate_last_state_cycle_time_duration()
                    .first()
                )

                self.assertEqual(
                    qa_status.state_cycle_time_duration,
                    timezone.now() - qa_status.state_history.first().start_time,
                )

    def test_annotate_customer_hirl_verifier(self):
        hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )
        hirl_user = provider_user_factory(
            first_name="NGBS", last_name="Admin", company=hirl_company, is_company_admin=True
        )
        verifier = rater_user_factory(first_name="Kent", last_name="Mitchell")
        eep_program = basic_eep_program_factory(
            slug=random.choice(customer_hirl_app.HIRL_PROJECT_EEP_PROGRAM_SLUGS)
        )

        with self.subTest("Check Rough Verifier"):
            requirement = qa_requirement_factory(
                eep_program=eep_program,
                qa_company=hirl_company,
                type=QARequirement.ROUGH_INSPECTION_QA_REQUIREMENT_TYPE,
            )

            qa_status = qa_status_factory(
                requirement=requirement,
                state="correction_required",
                qa_designee=hirl_user,
                home_status__eep_program=eep_program,
                home_status__customer_hirl_rough_verifier=verifier,
            )
            qa_status.save()

            qa_status = (
                QAStatus.objects.filter(id=qa_status.id).annotate_customer_hirl_verifier().first()
            )

            self.assertEqual(qa_status.verifier_id, verifier.id)
            self.assertEqual(qa_status.verifier_name, verifier.get_full_name())

        with self.subTest("Check Desktop Audit Verifier"):
            requirement = qa_requirement_factory(
                eep_program=eep_program,
                qa_company=hirl_company,
                type=QARequirement.DESKTOP_AUDIT_REQUIREMENT_TYPE,
            )

            qa_status = qa_status_factory(
                requirement=requirement,
                state="correction_required",
                qa_designee=hirl_user,
                home_status__eep_program=eep_program,
                home_status__customer_hirl_rough_verifier=verifier,
            )
            qa_status.save()

            qa_status = (
                QAStatus.objects.filter(id=qa_status.id).annotate_customer_hirl_verifier().first()
            )

            self.assertEqual(qa_status.verifier_id, verifier.id)
            self.assertEqual(qa_status.verifier_name, verifier.get_full_name())

        with self.subTest("Check Final Verifier"):
            requirement = qa_requirement_factory(
                eep_program=eep_program,
                qa_company=hirl_company,
                type=QARequirement.FINAL_INSPECTION_QA_REQUIREMENT_TYPE,
            )

            qa_status = qa_status_factory(
                requirement=requirement,
                state="correction_required",
                qa_designee=hirl_user,
                home_status__eep_program=eep_program,
                home_status__customer_hirl_final_verifier=verifier,
            )
            qa_status.save()

            qa_status = (
                QAStatus.objects.filter(id=qa_status.id).annotate_customer_hirl_verifier().first()
            )

            self.assertEqual(qa_status.verifier_id, verifier.id)
            self.assertEqual(qa_status.verifier_name, verifier.get_full_name())

    def test_get_customer_hirl_grading_verifier(self):
        hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )
        hirl_user = provider_user_factory(
            first_name="NGBS", last_name="Admin", company=hirl_company, is_company_admin=True
        )
        verifier = rater_user_factory(first_name="Kent", last_name="Mitchell")
        verifier2 = rater_user_factory(first_name="Mike", last_name="Russel")
        eep_program = basic_eep_program_factory(
            slug=random.choice(customer_hirl_app.HIRL_PROJECT_EEP_PROGRAM_SLUGS)
        )

        requirement = qa_requirement_factory(
            eep_program=eep_program,
            qa_company=hirl_company,
            type=QARequirement.FINAL_INSPECTION_QA_REQUIREMENT_TYPE,
        )

        qa_status = qa_status_factory(
            requirement=requirement,
            state="correction_required",
            qa_designee=hirl_user,
            home_status__eep_program=eep_program,
            home_status__customer_hirl_rough_verifier=None,
            home_status__customer_hirl_final_verifier=None,
        )
        qa_status.save()

        self.assertIsNone(qa_status.get_customer_hirl_grading_verifier())

        requirement.type = QARequirement.ROUGH_INSPECTION_QA_REQUIREMENT_TYPE
        requirement.save()
        qa_status.home_status.customer_hirl_rough_verifier = verifier
        qa_status.home_status.save()
        qa_status.refresh_from_db()
        self.assertEqual(qa_status.get_customer_hirl_grading_verifier(), verifier)

        requirement.type = QARequirement.FINAL_INSPECTION_QA_REQUIREMENT_TYPE
        requirement.save()
        qa_status.home_status.customer_hirl_final_verifier = verifier2
        qa_status.home_status.save()
        qa_status.refresh_from_db()
        self.assertEqual(qa_status.get_customer_hirl_grading_verifier(), verifier2)
