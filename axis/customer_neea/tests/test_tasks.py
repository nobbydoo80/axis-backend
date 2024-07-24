"""test_tasks.py: """


from unittest import mock

from django.urls import reverse
from django.utils import timezone

from axis.company.models import Company
from axis.core.tests.client import AxisClient
from axis.core.tests.testcases import AxisTestCase
from axis.customer_neea.tasks import (
    issue_monthly_bpa_utility_report_to_company_task,
    issue_monthly_bpa_utility_reports_to_bpa_utilities_task,
    export_home_data_raw_task,
    export_home_data_custom_task,
    export_home_data_bpa_task,
)
from axis.eep_program.models import EEPProgram
from axis.filehandling.models import AsynchronousProcessedDocument
from axis.home.models import EEPProgramHomeStatus
from axis.relationship.utils import create_or_update_spanning_relationships

__author__ = "Artem Hruzd"
__date__ = "07/12/2019 15:41"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from .mixins import NEEAV2ProgramTestMixin


class CustomerNEEATaskTest(NEEAV2ProgramTestMixin, AxisTestCase):
    client_class = AxisClient
    program_slug = "neea-bpa"

    @mock.patch(
        "axis.customer_neea.tasks.messages.NeeaHomeUtilityStatusRawExportCompletedMessage.send"
    )
    @mock.patch("axis.home.export_data.BaseHomeStatusDataDump.update_task_progress")
    def test_export_home_data_raw_task(self, update_task_progress, send_message):
        company = Company.objects.first()
        user = company.users.first()
        result_object = AsynchronousProcessedDocument.objects.create(company=company)
        export_home_data_raw_task(result_object_id=result_object.pk, user_id=user.pk)
        update_task_progress.assert_called()

        send_message.assert_called_once_with(user=user)

    @mock.patch(
        "axis.customer_neea.tasks.messages.NeeaHomeUtilityStatusCustomExportCompletedMessage.send"
    )
    @mock.patch("axis.home.export_data.BaseHomeStatusDataDump.update_task_progress")
    def test_export_home_data_custom_task(self, update_task_progress, send_message):
        company = Company.objects.first()
        user = company.users.first()
        result_object = AsynchronousProcessedDocument.objects.create(company=company)
        export_home_data_custom_task(result_object_id=result_object.pk, user_id=user.pk)
        update_task_progress.assert_called()

        send_message.assert_called_once_with(user=user)

    @mock.patch(
        "axis.customer_neea.tasks.messages.NeeaHomeUtilityStatusBPAExportCompletedMessage.send"
    )
    @mock.patch("axis.home.export_data.BaseHomeStatusDataDump.update_task_progress")
    def test_export_home_data_bpa_task(self, update_task_progress, send_message):
        company = Company.objects.first()
        user = company.users.first()
        result_object = AsynchronousProcessedDocument.objects.create(company=company)
        export_home_data_bpa_task(result_object_id=result_object.pk, user_id=user.pk)
        update_task_progress.assert_called()
        send_message.assert_called_once_with(user=user)

    @mock.patch("axis.customer_neea.tasks.issue_monthly_bpa_utility_report_to_company_task.delay")
    def test_issue_monthly_bpa_utility_reports_to_bpa_utilities_task(
        self, mock_utility_report_task
    ):
        bpa_utilities_count = (
            Company.objects.filter(
                sponsors__slug="bpa",
                company_type="utility",
                is_active=True,
                users__is_company_admin=True,
                users__is_active=True,
            )
            .distinct()
            .count()
        )

        issue_monthly_bpa_utility_reports_to_bpa_utilities_task()
        self.assertEqual(mock_utility_report_task.call_count, bpa_utilities_count)

    @mock.patch(
        "axis.customer_neea.tasks.messages.NeeaMonthlyHomeUtilityStatusBPAExportAvailableMessage.send"
    )
    @mock.patch("axis.home.export_data.BaseHomeStatusDataDump.update_task_progress")
    def test_issue_monthly_bpa_utility_report_to_company_task(
        self, update_task_progress, send_message
    ):
        utility_company = Company.objects.filter(
            sponsors__slug="bpa",
            company_type="utility",
            is_active=True,
            users__is_company_admin=True,
            users__is_active=True,
        ).first()
        issue_monthly_bpa_utility_report_to_company_task(utility_id=utility_company.pk)
        update_task_progress.assert_called()

        last_day_in_period = timezone.now().replace(day=1) - timezone.timedelta(days=1)
        result_object = AsynchronousProcessedDocument.objects.first()
        download_url = reverse("async_document_download", kwargs={"pk": result_object.pk})

        send_message.assert_called_once_with(
            company=utility_company,
            context={
                "year": last_day_in_period.year,
                "month": last_day_in_period.strftime("%B"),
                "url": download_url,
            },
        )

    def test_download_single_program(self):
        """Make sure that we can download the checklist"""
        user = self.get_user(is_company_admin=True, company__slug="ber")
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        program = EEPProgram.objects.get(slug=self.program_slug)

        url = reverse("home:download_single_program", kwargs={"eep_program": program.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response["content-type"],
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        self.assertEqual(
            response["content-disposition"], "attachment; filename=Axis-Program-neea-bpa.xlsx"
        )

    def test_download_bulk_checklist(self):
        """Make sure that we can download the checklist"""
        user = self.get_user(is_company_admin=True, company__slug="ber")
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        program = EEPProgram.objects.get(slug=self.program_slug)
        url = reverse("checklist:bulk_checklist_download", kwargs={"pk": program.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response["content-type"],
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        self.assertEqual(
            response["content-disposition"],
            "attachment; " "filename=utility-incentive-v2-single-family-performance-path.xlsx",
        )

    def test_download_single_homestatus(self):
        """Make sure that we can download the checklist"""
        user = self.get_user(is_company_admin=True, company__slug="ber")
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        home_status = EEPProgramHomeStatus.objects.get(eep_program__slug=self.program_slug)
        url = reverse("home:download_single_homestatus", kwargs={"home_status": home_status.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response["content-type"],
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        self.assertEqual(
            response["content-disposition"],
            f"attachment; filename=Axis-Home-" f"{home_status.home.pk}.xlsx",
        )

    def test_download_single_home(self):
        """Make sure that we can download the checklist"""
        user = self.get_user(is_company_admin=True, company__slug="ber")
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        home_status = EEPProgramHomeStatus.objects.get(eep_program__slug=self.program_slug)
        url = reverse("home:download_single_home", kwargs={"home": home_status.home.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response["content-type"],
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        self.assertEqual(
            response["content-disposition"],
            f"attachment; filename=Axis-Home-{home_status.home.pk}.xlsx",
        )


class CustomerNEEABPAQATests(NEEAV2ProgramTestMixin, AxisTestCase):
    client_class = AxisClient
    program_slug = "neea-bpa"

    def test_calculator_bad_api_endpoint(self):
        """Make sure we return 400 if we have an error."""
        user = self.get_user(is_company_admin=True, company__slug="ber")
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        from axis.customer_neea.models import PNWZone

        PNWZone.objects.all().delete()

        home_status = EEPProgramHomeStatus.objects.get(eep_program__slug=self.program_slug)
        url = reverse("apiv2:home_status-rtf-calculator", kwargs={"pk": home_status.pk})
        response = self.client.get(url)
        data = response.json()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["message"], "Standard Protocol Calculator Input Error:")
        self.assertEqual(len(data["errors"]), 1)

    def test_calculator_good_api_endpoint(self):
        """Right by default we do not have 2 things."""
        user = self.get_user(is_company_admin=True, company__slug="ber")
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )
        home_status = EEPProgramHomeStatus.objects.get(eep_program__slug=self.program_slug)
        url = reverse("apiv2:home_status-rtf-calculator", kwargs={"pk": home_status.pk})
        response = self.client.get(url)
        data = response.json()

        self.assertEqual(response.status_code, 200)

    def test_qa_relationships_api_endpoint_incentive_payer(self):
        """Right by default we do not have 2 things."""
        user = self.get_user(is_company_admin=True, company__slug="ber")
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        from axis.customer_neea.models import StandardProtocolCalculator

        self.assertEqual(StandardProtocolCalculator.objects.count(), 0)

        # Nothing should change here.
        home_status = EEPProgramHomeStatus.objects.get(eep_program__slug=self.program_slug)
        base_home_rels = list(
            home_status.home.relationships.all().values_list("company__slug", flat=True)
        )

        create_or_update_spanning_relationships(None, home_status)

        home_status = EEPProgramHomeStatus.objects.get(eep_program__slug=self.program_slug)
        home_rels = list(
            home_status.home.relationships.all().values_list("company__slug", flat=True)
        )
        self.assertEqual(set(base_home_rels), set(home_rels))

        url = reverse("apiv2:home_status-rtf-calculator", kwargs={"pk": home_status.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(StandardProtocolCalculator.objects.count(), 1)

        data = response.json()
        self.assertEqual(data["incentive_paying_organization"], "pacific-power")

        home_status = EEPProgramHomeStatus.objects.get(eep_program__slug=self.program_slug)
        home_rels = list(
            home_status.home.relationships.all().values_list("company__slug", flat=True)
        )
        self.assertEqual(set(base_home_rels + ["qa-pacific-power-qa-wa"]), set(home_rels))

    def test_qa_relationships_api_endpoint_default(self):
        """Right by default we do not have 2 things."""
        user = self.get_user(is_company_admin=True, company__slug="ber")
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        from axis.customer_neea.models import StandardProtocolCalculator

        self.assertEqual(StandardProtocolCalculator.objects.count(), 0)

        from axis.company.tests.factories import utility_organization_factory

        home_status = EEPProgramHomeStatus.objects.get(eep_program__slug=self.program_slug)
        utility = utility_organization_factory(
            name="foobar", slug="foobar", city=home_status.home.city
        )
        home_status.home.relationships.filter(company__slug="pacific-power").update(company=utility)

        base_home_rels = list(
            home_status.home.relationships.all().values_list("company__slug", flat=True)
        )
        self.assertNotIn("pacific-power", base_home_rels)

        create_or_update_spanning_relationships(None, home_status)

        home_status = EEPProgramHomeStatus.objects.get(eep_program__slug=self.program_slug)
        home_rels = list(
            home_status.home.relationships.all().values_list("company__slug", flat=True)
        )
        self.assertEqual(set(base_home_rels), set(home_rels))

        url = reverse("apiv2:home_status-rtf-calculator", kwargs={"pk": home_status.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(StandardProtocolCalculator.objects.count(), 1)

        data = response.json()
        self.assertEqual(data["incentive_paying_organization"], None)

        home_status = EEPProgramHomeStatus.objects.get(eep_program__slug=self.program_slug)
        home_rels = list(
            home_status.home.relationships.all().values_list("company__slug", flat=True)
        )
        self.assertEqual(set(base_home_rels + ["clearesult-qa"]), set(home_rels))
