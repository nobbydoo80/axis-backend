"""test_washington_code_credit_upload.py - Axis"""

__author__ = "Steven K"
__date__ = "10/26/21 12:19"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import io
import logging
import os.path
import shutil
import tempfile

from django.urls import reverse_lazy
from django_celery_results.models import TaskResult

from axis.core.tests.client import AxisClient
from axis.customer_eto.tests.program_checks.test_washington_code_credit import (
    WashingtonCodeCreditProgramBase,
)
from axis.filehandling.models import AsynchronousProcessedDocument

log = logging.getLogger(__name__)


class WashingtonCodeCreditDataTests(WashingtonCodeCreditProgramBase):
    client_class = AxisClient

    @classmethod
    def setUpTestData(cls):
        super(WashingtonCodeCreditDataTests, cls).setUpTestData()
        from axis.core.tests.factories import rater_user_factory

        cls.user = rater_user_factory(company=cls.rater_company)
        cls.rater_company.update_permissions()

    def test_program_no_data_downloads(self):
        """Verify that we can do the various downloads"""

        self.assertTrue(
            self.client.login(username=self.user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (self.user.username, self.user.pk),
        )

        with self.subTest(f"{self.eep_program} Single Program"):
            url = reverse_lazy(
                "home:download_single_program", kwargs={"eep_program": self.eep_program.pk}
            )
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response["content-type"],
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            self.assertEqual(
                response["content-disposition"],
                f"attachment; filename=Axis-Program-{self.eep_program.slug}.xlsx",
            )

        with self.subTest(f"{self.eep_program} Single Home"):
            url = reverse_lazy("home:download_single_home", kwargs={"home": self.home.pk})
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response["content-type"],
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            self.assertEqual(
                response["content-disposition"],
                f"attachment; filename=Axis-Home-{self.home.pk}.xlsx",
            )

        with self.subTest(f"{self.eep_program} Single Home Status"):
            url = reverse_lazy(
                "home:download_single_homestatus", kwargs={"home_status": self.home_status.pk}
            )
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response["content-type"],
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            self.assertEqual(
                response["content-disposition"],
                f"attachment; filename=Axis-Home-{self.home.pk}.xlsx",
            )

        with self.subTest(f"{self.eep_program} Bulk Download"):
            url = reverse_lazy(
                "checklist:bulk_checklist_download", kwargs={"pk": self.eep_program.pk}
            )
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response["content-type"],
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            self.assertEqual(
                response["content-disposition"],
                f"attachment; filename=energy-trust-washington-code-credits-2021.xlsx",
            )


class WashingtonCodeCreditUploadViewTests(WashingtonCodeCreditProgramBase):
    client_class = AxisClient

    @classmethod
    def setUpTestData(cls):
        super(WashingtonCodeCreditUploadViewTests, cls).setUpTestData()
        from axis.core.tests.factories import rater_admin_factory

        cls.user = rater_admin_factory(company=cls.rater_company)
        cls.rater_company.update_permissions()

        document = os.path.join(
            os.path.dirname(__file__), "../../static/templates/washington_code_credit.xlsm"
        )
        temp_dir = tempfile.mkdtemp()
        cls.document = os.path.join(temp_dir, os.path.basename(document))
        shutil.copy2(document, cls.document)

    def test_upload_view(self):
        """This will verify the view and upload handlers"""
        self.assertEqual(AsynchronousProcessedDocument.objects.count(), 0)
        self.client.force_login(self.user)
        # Make sure user can upload
        self.assertIn("home.add_home", self.user.get_all_permissions())
        upload_url = reverse_lazy("eto:wcc-upload")

        # Verify we get to the page
        response = self.client.get(upload_url)
        self.assertEqual(response.status_code, 200)

        # Verify we get upload
        self.assertTrue(os.path.isfile(self.document))
        self.assertTrue(os.path.exists(self.document))

        # # Need to figure this out.  I need to replicate locally and I cant?
        with io.open(self.document, "rb") as fp:
            data = {"company": self.rater_company.id, "document": fp}
            response = self.client.post(upload_url, data=data, format="multipart")
            self.assertEqual(AsynchronousProcessedDocument.objects.count(), 1)
            document = AsynchronousProcessedDocument.objects.last()
            self.assertRedirects(response, document.get_absolute_url())

        self.assertIsInstance(document.result, dict)
        self.assertEqual(document.filename().lower(), os.path.basename(self.document).lower())
        self.assertNotEqual(document.document.name, os.path.basename(self.document))
        self.assertIsNotNone(document.task_name)
        self.assertEqual(
            document.task_name,
            "axis.customer_eto.tasks.washington_code_credit.WashingtonCodeCreditUploadTask",
        )
        self.assertNotEqual(document.created_date, document.modified_date)
        self.assertGreater(document.modified_date, document.created_date)

        response = self.client.get(
            reverse_lazy("async_document_detail", kwargs={"pk": document.id}),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(response.status_code, 200)
        document.refresh_from_db()
        self.assertTrue(document.final_status)
