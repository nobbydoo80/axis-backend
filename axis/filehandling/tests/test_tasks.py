# -*- coding: utf-8 -*-
"""test_tasks.py: """

__author__ = "Artem Hruzd"
__date__ = "09/12/2022 23:44"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

import zipfile

from axis.company.tests.factories import rater_organization_factory
from axis.core.tests.testcases import AxisTestCase
from axis.core.utils import unrandomize_filename
from axis.filehandling.models import AsynchronousProcessedDocument
from axis.filehandling.tasks import download_multiple_customer_documents_task
from axis.filehandling.tests.factories import customer_document_factory


class CustomerDocumentTasksTests(AxisTestCase):
    def test_download_multiple_customer_documents_task(self):
        rater_company = rater_organization_factory()
        cd1 = customer_document_factory(company=rater_company)
        cd2 = customer_document_factory(company=rater_company)

        async_document = AsynchronousProcessedDocument.objects.create(
            company=rater_company,
            document=None,
            task_name=download_multiple_customer_documents_task.name,
            task_id="",
            download=True,
        )

        download_multiple_customer_documents_task.delay(
            result_object_id=async_document.id, customer_documents_ids=[cd1.id, cd2.id]
        )

        async_document.refresh_from_db()

        self.assertIsNotNone(async_document.document)
        zf = zipfile.ZipFile(async_document.document.file)

        unrandomize_file_list = [unrandomize_filename(fn) for fn in zf.namelist()]
        self.assertEqual(
            unrandomize_file_list,
            [
                "all_documents/",
                f"all_documents/{cd1.filename}",
                f"all_documents/{cd2.filename}",
            ],
        )
