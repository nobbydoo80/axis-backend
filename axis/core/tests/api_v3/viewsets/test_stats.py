"""stats.py: Tests for landing page Metrics"""


from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.utils import timezone

from axis.core.tests.client import AxisClient
from axis.core.tests.testcases import ApiV3Tests
from axis.home.models import EEPProgramHomeStatus
from axis.qa.models import QAStatus
from axis.qa.tests.mixins import QAManagerTestMixin

__author__ = "Rajesh Pethe"
__date__ = "08/07/2020 17:05:05"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Rajesh Pethe",
    "Steven Klass",
]


User = get_user_model()


class MetricsRaterTests(QAManagerTestMixin, ApiV3Tests):
    client_class = AxisClient

    def test_rater_file_metrics(self):
        user = self.get_nonadmin_user(company_type="rater")
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        # expect 4 QAStatuses from our fixturecompiler
        qa_statuses = QAStatus.objects.all()
        self.assertEqual(len(qa_statuses), 4)

        qa_status = qa_statuses[2]
        qa_status.owner = user.company
        qa_status.save()

        # expect 2 EEPProgramHomeStatus from our fixturecompiler
        eep_program_home_statuses = EEPProgramHomeStatus.objects.filter_by_user(user)
        self.assertEqual(len(eep_program_home_statuses), 2)

        eep_program_home_status = eep_program_home_statuses[0]
        eep_program_home_status.make_transition(transition="completion_transition", user=user)
        eep_program_home_status.certification_date = timezone.now()
        eep_program_home_status.rater_of_record = user
        eep_program_home_status.save()
        user.company = eep_program_home_status.company
        user.company.company_type = "utility"
        user.save()

        qa_status.make_transition("in_progress_to_complete", user=user)

        # prepare QAStatus object from our fixturecompiler
        # this will represent QAStatus after corrections
        qa_status = qa_statuses[3]
        qa_status.owner = user.company
        qa_status.save()

        eep_program_home_status = eep_program_home_statuses[1]
        eep_program_home_status.make_transition(transition="completion_transition", user=user)
        eep_program_home_status.certification_date = timezone.now()
        eep_program_home_status.rater_of_record = user
        eep_program_home_status.company.owner = user
        eep_program_home_status.save()
        user.company = eep_program_home_status.company
        user.company.company_type = "utility"
        user.save()

        qa_status.make_transition(transition="in_progress_to_correction_required", user=user)
        qa_status.make_transition(
            transition="correction_required_to_correction_received", user=user
        )
        qa_status.make_transition(transition="correction_received_to_complete", user=user)

        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        url = reverse_lazy("api_v3:stats-rater-file-metrics")
        response = self.client.get(url, data={"style": "rater"})

        response = self.client.get(url, data={"style": "rater"})
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.json()["totals"]["completed_first_time_count"], 1)
        self.assertEqual(response.json()["data"][0]["completed_total_percentage"], "100.00%")
        self.assertEqual(
            response.json()["data"][0]["completed_required_corrections_percentage"], "50.00%"
        )

        response = self.client.get(url, data={"style": "rater"})
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.json()["totals"]["completed_first_time_count"], 1)
        self.assertEqual(response.json()["data"][0]["completed_total_percentage"], "100.00%")
        self.assertEqual(
            response.json()["data"][0]["completed_required_corrections_percentage"], "50.00%"
        )

        response = self.client.get(url, data={"style": "rater"})
        self.assertEqual(response.status_code, 200)

    def test_rater_field_metrics(self):
        user = self.get_nonadmin_user(company_type="rater")

        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        # expect 4 QAStatuses from our fixturecompiler
        qa_statuses = QAStatus.objects.all()
        self.assertEqual(len(qa_statuses), 4)

        qa_status = qa_statuses[0]
        qa_status.owner = user.company
        qa_status.save()

        # expect 2 EEPProgramHomeStatus from our fixturecompiler
        eep_program_home_statuses = EEPProgramHomeStatus.objects.filter_by_user(user)
        self.assertEqual(len(eep_program_home_statuses), 2)

        eep_program_home_status = eep_program_home_statuses[0]
        eep_program_home_status.make_transition(transition="completion_transition", user=user)
        eep_program_home_status.certification_date = timezone.now()
        eep_program_home_status.rater_of_record = user
        eep_program_home_status.save()
        user.company = eep_program_home_status.company
        user.company.company_type = "utility"
        user.save()

        # prepare QAStatus object from our fixturecompiler
        # this will represent QAStatus after corrections
        qa_status = qa_statuses[1]
        qa_status.owner = user.company
        qa_status.save()

        eep_program_home_status = eep_program_home_statuses[1]
        eep_program_home_status.make_transition(transition="completion_transition", user=user)
        eep_program_home_status.certification_date = timezone.now()
        eep_program_home_status.rater_of_record = user
        eep_program_home_status.company.owner = user
        eep_program_home_status.save()
        user.company = eep_program_home_status.company
        user.company.company_type = "utility"
        user.save()

        qa_status.make_transition(transition="in_progress_to_correction_required", user=user)
        qa_status.make_transition(
            transition="correction_required_to_correction_received", user=user
        )
        qa_status.make_transition(transition="correction_received_to_complete", user=user)

        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        url = reverse_lazy("api_v3:stats-rater-field-metrics")
        response = self.client.get(url, data={"style": "rater"})
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.json()["totals"]["completed_required_corrections_count"], 1)

        response = self.client.get(url, data={"style": "rater"})
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.json()["totals"]["completed_required_corrections_count"], 1)

        response = self.client.get(url, data={"style": "utility"})
        self.assertEqual(response.status_code, 200)
