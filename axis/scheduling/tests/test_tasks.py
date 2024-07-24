"""test_tasks.py: """

from django.test import override_settings

from axis.core.tests.testcases import ApiV3Tests
from axis.filehandling.models import AsynchronousProcessedDocument
from axis.scheduling.models import Task
from axis.scheduling.tasks import scheduling_task_report_task
from axis.scheduling.tests.mixins import SchedulingTaskMixin

__author__ = "Artem Hruzd"
__date__ = "02/03/2020 20:48"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class SchedulingTaskTest(SchedulingTaskMixin, ApiV3Tests):
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_scheduling_task_report_task(self):
        task = Task.objects.first()

        asynchronous_process_document = AsynchronousProcessedDocument(
            download=True, company=task.assigner.company
        )
        asynchronous_process_document.save()

        scheduling_task_report_task.delay(
            asynchronous_process_document_id=asynchronous_process_document.id,
            user_id=task.assigner.id,
            task_ids=[
                task.id,
            ],
        )
        asynchronous_process_document.refresh_from_db()
        self.assertIsNotNone(asynchronous_process_document.document.file)
        asynchronous_process_document.document.file.close()
