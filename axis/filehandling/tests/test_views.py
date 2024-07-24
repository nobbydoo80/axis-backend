"""test_views.py: Django filehandling.tests"""


__author__ = "Steven Klass"
__date__ = "1/10/12 3:27 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

import logging
import os
import io

from django.urls import reverse

from axis.core.tests.client import AxisClient
from axis.core.tests.testcases import AxisTestCase
from axis.company.tests.mixins import CompaniesAndUsersTestMixin
from ..models import AsynchronousProcessedDocument


log = logging.getLogger(__name__)


class AsynchronousProcessedDocumentBaseTestHandler(object):
    def _handle_uploading(self, user_id, file_obj, url, password="password"):
        """This will do a basic push to ensure it all works.."""

        user = self.user_model.objects.get(id=user_id)
        self.assertEqual(self.client.login(username=user.username, password=password), True)
        self.assertEqual(user.has_perm("filehandling.add_asynchronousprocesseddocument"), True)
        current_document_count = AsynchronousProcessedDocument.objects.count()
        self.assertEqual(os.path.isfile(file_obj), True)

        with io.open(file_obj, "rb") as f:
            form = {"company": user.company.id, "document": f}

            upload_url = reverse(url)
            response = self.client.get(upload_url)
            self.assertEqual(response.status_code, 200)

            response = self.client.post(upload_url, data=form)
            self.assertEqual(
                AsynchronousProcessedDocument.objects.count(),
                current_document_count + 1,
            )
            document = AsynchronousProcessedDocument.objects.last()

            self.assertRedirects(response, document.get_absolute_url())
            self.assertIsNotNone(document.task_id)

            # Wait for this to finish
            while True:
                # This will update the status if something happened.
                response = self.client.get(
                    reverse("async_document_detail", kwargs={"pk": document.id}),
                    HTTP_X_REQUESTED_WITH="XMLHttpRequest",
                )
                self.assertEqual(response.status_code, 200)
                document = AsynchronousProcessedDocument.objects.get(id=document.id)
                if document.final_status:
                    break

            self.assertIsInstance(document.result, dict)
            self.assertEqual(document.filename().lower(), os.path.basename(file_obj).lower())
            self.assertNotEqual(document.document.name, os.path.basename(file_obj))
            self.assertIsNotNone(document.task_name)
            self.assertNotEqual(document.created_date, document.modified_date)
            self.assertGreater(document.modified_date, document.created_date)
            return document


class FileHandlingViewTests(
    CompaniesAndUsersTestMixin,
    AxisTestCase,
    AsynchronousProcessedDocumentBaseTestHandler,
):
    """Test out filehandling application"""

    include_company_types = ["builder", "rater", "provider"]
    client_class = AxisClient

    def test_success_test_document_upload(self):
        """Test basic ability to upload and parse a document"""
        file_obj = __file__ if __file__.endswith("py") else __file__[:-1]
        user = self.get_admin_user("provider")
        document = self._handle_uploading(
            user_id=user.id, file_obj=file_obj, url="async_document_test"
        )

        self.assertEqual(document.final_status, "SUCCESS")

        self.assertEqual(document.download, False)

        results = document.result
        keys = ["info", "errors", "warnings", "traceback", "result", "debug", "latest"]
        self.assertEqual(sorted(results.keys()), sorted(keys))
        self.assertGreater(len(results["info"]), 0)
        self.assertEqual(len(results["errors"]), 0)
        self.assertGreater(len(results["warnings"]), 0)
        self.assertGreater(len(results["result"]), 0)
        self.assertGreater(len(results["latest"]), 0)
        self.assertIsNone(results["traceback"])
        self.assertEqual(
            results["result"],
            "Completed processing {} for {}".format(document.filename(), user.company),
        )

    def test_failed_test_document_upload(self):
        """Test basic ability to upload and parse a bad document"""

        file_obj = os.path.join(os.path.dirname(__file__), "bad_file.c")
        document = self._handle_uploading(
            user_id=self.get_admin_user("rater").id,
            file_obj=file_obj,
            url="async_document_test",
        )

        # TODO: FIX ME??
        # self.assertEqual(document.final_status, "FAILURE")
        self.assertEqual(document.download, False)

        results = document.result
        keys = ["info", "errors", "warnings", "traceback", "result", "debug", "latest"]
        self.assertEqual(sorted(results.keys()), sorted(keys))
        self.assertRaises(TypeError, results["traceback"])
        self.assertRaises(TypeError, results["result"])
