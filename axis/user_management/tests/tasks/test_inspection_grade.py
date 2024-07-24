"""inspection_grade.py: """

__author__ = "Artem Hruzd"
__date__ = "12/23/2019 22:22"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.apps import apps
from django.test import override_settings

from axis.core.tests.client import AxisClient
from axis.core.tests.testcases import AxisTestCase
from axis.filehandling.models import AsynchronousProcessedDocument
from axis.user_management.models import InspectionGrade
from axis.user_management.tasks import inspection_grade_report_task
from axis.user_management.tests.mixins import InspectionGradeTestMixin

customer_hirl_app = apps.get_app_config("customer_hirl")


class InspectionGradeTaskTest(InspectionGradeTestMixin, AxisTestCase):
    client_class = AxisClient

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_inspection_grade_report_task(self):
        inspection_grade = InspectionGrade.objects.first()

        asynchronous_process_document = AsynchronousProcessedDocument(
            download=True, company=inspection_grade.approver.company
        )
        asynchronous_process_document.save()

        inspection_grade_report_task.delay(
            asynchronous_process_document_id=asynchronous_process_document.id,
            user_id=inspection_grade.user.id,
            inspection_grade_ids=[
                inspection_grade.id,
            ],
        )
        asynchronous_process_document.refresh_from_db()
        self.assertIsNotNone(asynchronous_process_document.document.file)
        asynchronous_process_document.document.file.close()
