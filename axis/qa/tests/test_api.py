from django.urls import reverse
from django.utils import timezone

from axis.core.tests.client import AxisClient
from axis.core.tests.testcases import AxisTestCase
from axis.eep_program.models import EEPProgram
from axis.home.models import EEPProgramHomeStatus
from axis.qa.models import QARequirement, QAStatus
from .mixins import QAManagerTestMixin

__author__ = "Artem Hruzd"
__date__ = "6/5/2019 1:29 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
]


class QAStatusAPITest(QAManagerTestMixin, AxisTestCase):
    client_class = AxisClient

    def test_list(self):
        user = self.nonadmin_user
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )
        total_count = QAStatus.objects.count()
        url = reverse("apiv2:qa_status-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], total_count)

    def test_rater_file_metrics(self):
        user = self.get_nonadmin_user(company_type="rater")
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )
        eep_program = EEPProgram.objects.first()
        file_qa = QARequirement.objects.get(eep_program=eep_program, type="file")
        # expect 2 QAStatuses from our fixturecompiler
        qa_statuses = QAStatus.objects.filter(requirement=file_qa)
        self.assertEqual(len(qa_statuses), 2)

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

        qa_status.make_transition("in_progress_to_complete", user=user)

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

        url = reverse("apiv2:qa_status-rater-file-metrics")
        with self.subTest("Rater of Record"):
            response = self.client.get(url, data={"style": "rater_of_record"})
            self.assertEqual(response.status_code, 200)

            self.assertEqual(response.json()["sums"]["completed_first_time_count"], 1)
            self.assertEqual(response.json()["sums"]["in_progress_count"], 0)
            self.assertEqual(response.json()["data"][0]["completed_total_percentage"], "100.00%")
            self.assertEqual(
                response.json()["data"][0]["completed_required_corrections_percentage"], "50.00%"
            )

        with self.subTest("Rater"):
            response = self.client.get(url, data={"style": "rater"})
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn("sums", data)
            self.assertIn("data", data)
            self.assertIn("in_progress_count", data["sums"])
            self.assertIn("completed_required_corrections_count", data["sums"])

            self.assertEqual(data["sums"]["completed_first_time_count"], 1)
            self.assertEqual(data["sums"]["in_progress_count"], 0)
            self.assertEqual(data["data"][0]["completed_total_percentage"], "100.00%")
            self.assertEqual(data["data"][0]["completed_required_corrections_percentage"], "50.00%")

        with self.subTest("Utility"):
            response = self.client.get(url, data={"style": "utility"})
            self.assertEqual(response.status_code, 200)

            # self.assertEqual(response.json()['sums']['completed_first_time_count'], 1)
            # self.assertEqual(response.json()['sums']['in_progress_count'], 0)
            # self.assertEqual(response.json()['data'][0]['completed_total_percentage'], '100.00%')
            # self.assertEqual(
            #     response.json()['data'][0]['completed_required_corrections_percentage'], '50.00%')

    def test_rater_field_metrics(self):
        user = self.get_nonadmin_user(company_type="rater")

        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        eep_program = EEPProgram.objects.first()
        field_qa = QARequirement.objects.get(eep_program=eep_program, type="field")
        # expect 2 QAStatuses from our fixturecompiler
        qa_statuses = QAStatus.objects.filter(requirement=field_qa)
        self.assertEqual(len(qa_statuses), 2)

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
        url = reverse("apiv2:qa_status-rater-field-metrics")

        with self.subTest("Rater of Record"):
            response = self.client.get(url, data={"style": "rater_of_record"})
            self.assertEqual(response.status_code, 200)

            data = response.json()

            self.assertIn("sums", data)
            self.assertIn("in_progress_count", data["sums"])
            self.assertIn("completed_required_corrections_count", data["sums"])

            self.assertEqual(data["sums"]["in_progress_count"], 1)
            self.assertEqual(data["sums"]["completed_required_corrections_count"], 1)

        with self.subTest("Rater"):
            response = self.client.get(url, data={"style": "rater"})
            self.assertEqual(response.status_code, 200)
            data = response.json()

            self.assertIn("sums", data)
            self.assertIn("in_progress_count", data["sums"])
            self.assertIn("completed_required_corrections_count", data["sums"])

            self.assertEqual(data["sums"]["in_progress_count"], 1)
            self.assertEqual(data["sums"]["completed_required_corrections_count"], 1)

        with self.subTest("Utility"):
            response = self.client.get(url, data={"style": "utility"})
            self.assertEqual(response.status_code, 200)

            # self.assertEqual(response.json()['sums']['in_progress_count'], 1)
            # self.assertEqual(response.json()['sums']['completed_required_corrections_count'], 1)
