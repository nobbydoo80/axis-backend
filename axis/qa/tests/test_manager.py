from datetime import timezone

from axis.core.tests.testcases import AxisTestCase
from axis.home.models import EEPProgramHomeStatus
from axis.qa.models import QAStatus
from .mixins import QAManagerTestMixin

__author__ = "Michael Jeffrey"
__date__ = "10/22/15 9:23 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Michael Jeffrey",
]


class QAManagerTests(QAManagerTestMixin, AxisTestCase):
    def setUp(self):
        from axis.company.models import Company

        qa = Company.objects.get(company_type="qa")
        qa.update_permissions("qa")

        qa_status_1, qa_status_2, qa_status_3, qa_status_4 = QAStatus.objects.all()

        qa_status_1.make_transition("in_progress_to_correction_required")
        qa_status_1.make_transition("correction_required_to_correction_received")
        qa_status_1.make_transition("correction_received_to_correction_required")
        qa_status_1.make_transition("correction_required_to_correction_received")
        qa_status_1.make_transition("correction_received_to_correction_required")
        qa_status_1.make_transition("correction_required_to_correction_received")
        qa_status_1.make_transition("correction_received_to_correction_required")
        qa_status_1.make_transition("correction_required_to_correction_received")
        qa_status_1.make_transition("correction_received_to_complete")

        qa_status_2.make_transition("in_progress_to_correction_required")
        qa_status_2.make_transition("correction_required_to_correction_received")
        qa_status_2.make_transition("correction_received_to_correction_required")
        qa_status_2.make_transition("correction_required_to_correction_received")
        qa_status_2.make_transition("correction_received_to_correction_required")
        qa_status_2.make_transition("correction_required_to_correction_received")
        qa_status_2.make_transition("correction_received_to_complete")

        qa_status_3.make_transition("in_progress_to_correction_required")
        qa_status_3.make_transition("correction_required_to_correction_received")
        qa_status_3.make_transition("correction_received_to_correction_required")
        qa_status_3.make_transition("correction_required_to_correction_received")
        qa_status_3.make_transition("correction_received_to_correction_required")
        qa_status_3.make_transition("correction_required_to_correction_received")
        qa_status_3.make_transition("correction_received_to_correction_required")
        qa_status_3.make_transition("correction_required_to_correction_received")
        qa_status_3.make_transition("correction_received_to_complete")

        qa_status_4.make_transition("in_progress_to_correction_required")
        qa_status_4.make_transition("correction_required_to_correction_received")
        qa_status_4.make_transition("correction_received_to_correction_required")
        qa_status_4.make_transition("correction_required_to_correction_received")
        qa_status_4.make_transition("correction_received_to_correction_required")
        qa_status_4.make_transition("correction_required_to_correction_received")
        qa_status_4.make_transition("correction_received_to_complete")

        stats_and_offsets = [
            (qa_status_1, 12),
            (qa_status_2, 13),
            (qa_status_3, 14),
            (qa_status_4, 15),
        ]

        from datetime import timedelta, datetime

        qa_status_1.state_history.update(start_time=datetime.now(timezone.utc))
        qa_status_2.state_history.update(start_time=datetime.now(timezone.utc))
        qa_status_3.state_history.update(start_time=datetime.now(timezone.utc))
        qa_status_4.state_history.update(start_time=datetime.now(timezone.utc))

        # Store the offsets so we don't hardcode expected order.
        self.expected_offsets = {}
        for qa_stat, offset in stats_and_offsets:
            self.expected_offsets[(qa_stat.home_status.id, qa_stat.requirement.type)] = offset
            for i, state_log in enumerate(qa_stat.state_history.all(), 1):
                state_log.start_time += timedelta(minutes=offset * i)
                state_log.save()

    def test_single_qa_status_transition_durations_calculations(self):
        home_status_id = list(EEPProgramHomeStatus.objects.values_list("id", flat=True))[0]
        metrics = QAStatus.objects.get_qa_metrics_for_home_statuses([home_status_id])

        expected_duration = self.expected_offsets[(home_status_id, "field")]

        for _, _, end_time, duration, _, _, _ in metrics[home_status_id]["transitions"]["field"]:
            if not end_time:
                continue

            minutes = duration.seconds // 60
            self.assertEqual(minutes, expected_duration)

    def test_multiple_qa_status_transition_durations_calculations(self):
        home_status_ids = list(EEPProgramHomeStatus.objects.values_list("id", flat=True))
        metrics = QAStatus.objects.get_qa_metrics_for_home_statuses(home_status_ids)

        for (id_lookup, qa_type), expected_offset in self.expected_offsets.items():
            for _, _, end_time, duration, _, _, _ in metrics[id_lookup]["transitions"][qa_type]:
                if not end_time:
                    continue
                minutes = duration.seconds // 60
                self.assertEqual(minutes, expected_offset)

    def test_single_qa_status_durations_calculations_by_state(self):
        home_status_id = list(EEPProgramHomeStatus.objects.values_list("id", flat=True))[0]
        metrics = QAStatus.objects.get_qa_metrics_for_home_statuses([home_status_id])

        expected_offset = self.expected_offsets[(home_status_id, "field")]

        for state, duration in metrics[home_status_id]["durations"]["field"].items():
            minutes = duration.seconds // 60
            self.assertEqual(
                minutes, metrics[home_status_id]["counts"][state]["field"] * expected_offset
            )

    def test_multiple_qa_status_durations_calculations_by_state(self):
        home_status_ids = list(EEPProgramHomeStatus.objects.values_list("id", flat=True))
        metrics = QAStatus.objects.get_qa_metrics_for_home_statuses(home_status_ids)

        for (id_lookup, qa_type), expected_offset in self.expected_offsets.items():
            for state, duration in metrics[id_lookup]["durations"][qa_type].items():
                minutes = duration.seconds // 60
                count = metrics[id_lookup]["counts"][state][qa_type]
                self.assertEqual(minutes, count * expected_offset)
