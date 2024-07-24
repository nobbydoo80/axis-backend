"""user_training.py: """


__author__ = "Artem Hruzd"
__date__ = "12/23/2019 21:48"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


import random
from unittest.mock import patch, Mock

from django.urls import reverse

from axis.core.tests.client import AxisClient
from axis.core.tests.testcases import AxisTestCase
from axis.user_management.models import Training, TrainingStatus
from axis.user_management.states import TrainingStatusStates
from axis.user_management.tests.mixins import TrainingTextMixin


class UserTrainingViewSetTest(TrainingTextMixin, AxisTestCase):
    client_class = AxisClient

    @patch("axis.messaging.messages.ModernMessage.send")
    @patch(
        "axis.core.serializers.user_management_app",
        Mock(
            TRAINING_APPLICABLE_REQUIREMENTS={
                "aps": ["aps-2019"],
                "neea": [
                    "wa-code-study",
                ],
            }
        ),
    )
    @patch(
        "axis.core.serializers.user_management_app",
        Mock(ACCREDITATION_APPLICABLE_COMPANIES_SLUGS=["aps", "neea"]),
    )
    @patch(
        "axis.core.serializers.user_management_app",
        Mock(TRAINING_APPLICABLE_PROGRAMS=["aps-2019", "wa-code-study"]),
    )
    def test_create_training(self, send_message):
        rater_user = self.get_admin_user("rater")
        provider_user = self.get_admin_user("provider")
        self.assertTrue(
            self.client.login(username=rater_user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (rater_user.username, rater_user.pk),
        )
        training_data = {
            "owner_company": rater_user.company.id,
            "trainee_id": rater_user.id,  # specify trainee_id as region dependency
            "name": "Some name",
            "address": "Random address",
            "training_type": random.choice(Training.TRAINING_TYPE_CHOICES)[0],
            "attendance_type": random.choice(Training.ATTENDANCE_TYPE_CHOICES)[0],
            "credit_hours": random.randint(0, 10),
            "training_date": "1993-11-27",
            "notes": "test",
        }

        url = "{}?machinery=UserTrainingExamineMachinery".format(
            reverse("apiv2:user_training-list")
        )

        response = self.client.post(url, data=training_data)
        self.assertEqual(response.status_code, 201)

        created_training = Training.objects.order_by("-id").first()
        self.assertEqual(created_training.trainee.id, training_data["trainee_id"])
        self.assertEqual(created_training.training_type, training_data["training_type"])
        self.assertEqual(created_training.notes, training_data["notes"])

        send_message.assert_called_once()

        training_status = TrainingStatus.objects.filter(
            training=created_training, company=provider_user.company, state=TrainingStatusStates.NEW
        ).first()
        self.assertIsNotNone(training_status)

    @patch("axis.messaging.messages.ModernMessage.send")
    @patch(
        "axis.core.serializers.user_management_app",
        Mock(
            TRAINING_APPLICABLE_REQUIREMENTS={
                "aps": ["aps-2019"],
                "neea": [
                    "wa-code-study",
                ],
            }
        ),
    )
    @patch(
        "axis.core.serializers.user_management_app",
        Mock(ACCREDITATION_APPLICABLE_COMPANIES_SLUGS=["aps", "neea"]),
    )
    @patch(
        "axis.core.serializers.user_management_app",
        Mock(TRAINING_APPLICABLE_PROGRAMS=["aps-2019", "wa-code-study"]),
    )
    def test_create_training_with_provider(self, send_message):
        rater_user = self.get_admin_user("rater")
        provider_user = self.get_admin_user("provider")
        self.assertTrue(
            self.client.login(username=provider_user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (provider_user.username, rater_user.pk),
        )
        training_data = {
            "owner_company": rater_user.company.id,
            "trainee_id": rater_user.id,  # specify trainee_id as region dependency
            "name": "Some name",
            "address": "Random address",
            "training_type": random.choice(Training.TRAINING_TYPE_CHOICES)[0],
            "attendance_type": random.choice(Training.ATTENDANCE_TYPE_CHOICES)[0],
            "credit_hours": random.randint(0, 10),
            "training_date": "1993-11-27",
            "notes": "test",
        }

        url = "{}?machinery=UserTrainingExamineMachinery".format(
            reverse("apiv2:user_training-list")
        )

        response = self.client.post(url, data=training_data)
        self.assertEqual(response.status_code, 201)

        created_training = Training.objects.order_by("-id").first()

        self.assertEqual(send_message.call_count, 2)

        training_status = TrainingStatus.objects.filter(
            training=created_training,
            company=provider_user.company,
            state=TrainingStatusStates.APPROVED,
        ).first()
        self.assertIsNotNone(training_status)
