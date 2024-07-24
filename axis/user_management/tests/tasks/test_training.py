"""training.py: """


from django.utils import timezone
from dateutil.relativedelta import relativedelta
from django.test import override_settings

from axis.core.tests.client import AxisClient
from axis.core.tests.testcases import AxisTestCase
from axis.filehandling.models import AsynchronousProcessedDocument
from axis.user_management.models import Training, TrainingStatus
from axis.user_management.tasks import training_report_task, training_status_expire_task
from axis.user_management.states import TrainingStatusStates
from axis.user_management.tests.mixins import TrainingTextMixin

__author__ = "Artem Hruzd"
__date__ = "12/23/2019 22:22"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class TrainingTaskTest(TrainingTextMixin, AxisTestCase):
    client_class = AxisClient

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_training_report_task(self):
        provider_user = self.get_admin_user("provider")
        training = Training.objects.first()

        asynchronous_process_document = AsynchronousProcessedDocument(
            download=True, company=provider_user.company
        )
        asynchronous_process_document.save()

        training_report_task.delay(
            asynchronous_process_document_id=asynchronous_process_document.id,
            user_id=training.trainee.id,
            training_ids=[
                training.id,
            ],
        )
        asynchronous_process_document.refresh_from_db()
        self.assertIsNotNone(asynchronous_process_document.document.file)
        asynchronous_process_document.document.file.close()

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    @override_settings(USER_MANAGEMENT={"TRAINING_CYCLE": relativedelta(years=3)})
    def test_equipment_status_expire_task(self):
        trainings = Training.objects.all()
        approved_statuses_count = TrainingStatus.objects.filter(
            state=TrainingStatusStates.APPROVED
        ).count()
        expired_statuses_count = TrainingStatus.objects.filter(
            state=TrainingStatusStates.EXPIRED
        ).count()

        self.assertNotEqual(approved_statuses_count, 0)

        for training in trainings:
            training.training_date = timezone.now().date() - relativedelta(years=10)
            training.save()

        training_status_expire_task.delay()

        new_approved_status_count = TrainingStatus.objects.filter(
            state=TrainingStatusStates.APPROVED
        ).count()
        new_expired_status_count = TrainingStatus.objects.filter(
            state=TrainingStatusStates.EXPIRED
        ).count()

        self.assertEqual(new_approved_status_count, 0)
        self.assertEqual(new_expired_status_count, approved_statuses_count + expired_statuses_count)
