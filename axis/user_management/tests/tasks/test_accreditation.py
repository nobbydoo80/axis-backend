"""accreditation.py: """


import datetime
from unittest import mock
from unittest import skipIf

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.test import override_settings
from django.utils import timezone

from axis.core.tests.client import AxisClient
from axis.core.tests.testcases import AxisTestCase
from axis.filehandling.models import AsynchronousProcessedDocument
from axis.user_management.models import Accreditation
from axis.user_management.tasks import (
    accreditation_report_task,
    accreditation_status_expire_task,
    accreditation_status_expire_notification_warning_task,
)
from axis.user_management.tests.mixins import AccreditationTestMixin

__author__ = "Artem Hruzd"
__date__ = "12/23/2019 22:22"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class AccreditationTaskTest(AccreditationTestMixin, AxisTestCase):
    client_class = AxisClient

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_accreditation_report_task(self):
        accreditation = Accreditation.objects.first()

        asynchronous_process_document = AsynchronousProcessedDocument(
            download=True, company=accreditation.approver.company
        )
        asynchronous_process_document.save()

        accreditation_report_task.delay(
            asynchronous_process_document_id=asynchronous_process_document.id,
            user_id=accreditation.trainee.id,
            accreditation_ids=[
                accreditation.id,
            ],
        )
        asynchronous_process_document.refresh_from_db()
        self.assertIsNotNone(asynchronous_process_document.document.file)
        asynchronous_process_document.document.file.close()

    @skipIf(
        settings.DATABASES["default"]["ENGINE"] != "django.db.backends.mysql",
        "Only can be run on MYSQL Engine",
    )
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_accreditation_status_expire_task(self):
        """
        This task only works with MYSQL db
        """
        accreditations = Accreditation.objects.all()

        for accreditation in accreditations:
            accreditation.date_last = timezone.now().date() - relativedelta(years=3)
            accreditation.accreditation_cycle = Accreditation.EVERY_2_YEARS_ACCREDITATION_CYCLE
            accreditation.state = Accreditation.ACTIVE_STATE
            accreditation.save()
        accreditation_status_expire_task.delay()

        inactive_accreditations = Accreditation.objects.filter(state=Accreditation.INACTIVE_STATE)
        self.assertEqual(inactive_accreditations.count(), accreditations.count())

    @skipIf(
        settings.DATABASES["default"]["ENGINE"] != "django.db.backends.mysql",
        "Only can be run on MYSQL Engine",
    )
    @mock.patch.object(timezone, "now")
    @mock.patch("axis.user_management.messages.AccreditationExpireWarningMessage.send")
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_accreditation_status_expire_notification_warning_task(
        self, send_message, mock_timezone
    ):
        mock_timezone.return_value = datetime.datetime(
            2015, 1, 8, 11, 00, tzinfo=datetime.timezone.utc
        )

        accreditations = Accreditation.objects.all()

        for accreditation in accreditations:
            accreditation.date_last = (
                timezone.now().date() + timezone.timedelta(days=10)
            ) - relativedelta(years=2)
            accreditation.accreditation_cycle = Accreditation.EVERY_2_YEARS_ACCREDITATION_CYCLE
            accreditation.state = Accreditation.ACTIVE_STATE
            accreditation.save()

        # make sure that we set the same amount of days to be notified by task
        accreditation_status_expire_notification_warning_task.delay(days_before_expire=10)

        self.assertEqual(send_message.call_count, accreditations.count())
