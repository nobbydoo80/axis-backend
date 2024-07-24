"""inspection_grade.py: """


__author__ = "Artem Hruzd"
__date__ = "12/25/2019 18:36"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

import random
from unittest import mock

from django.urls import reverse

from axis.core.tests.client import AxisClient
from axis.core.tests.testcases import AxisTestCase
from axis.user_management.models import InspectionGrade
from axis.user_management.tests.mixins import InspectionGradeTestMixin


class UserInspectionGradeViewSetTest(InspectionGradeTestMixin, AxisTestCase):
    client_class = AxisClient

    @mock.patch("axis.messaging.messages.ModernMessage.send")
    def test_create_inspection_grade_with_provider(self, send_message):
        provider_user = self.get_admin_user("provider")
        rater_user = self.get_admin_user("rater")
        self.assertTrue(
            self.client.login(username=provider_user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login"
            % (provider_user.username, provider_user.pk),
        )
        inspection_grade_data = {
            "user_id": rater_user.id,  # specify trainee_id as region dependency
            "graded_date": "1993-11-29",
            "letter_grade": random.choice(InspectionGrade.LETTER_GRADE_CHOICES)[0],
            "notes": "test",
        }

        url = "{}?machinery=UserInspectionGradeExamineMachinery".format(
            reverse("apiv2:user_inspection_grade-list")
        )

        response = self.client.post(url, data=inspection_grade_data)
        self.assertEqual(response.status_code, 201)

        created_inspection_grade = InspectionGrade.objects.order_by("-id").first()
        self.assertEqual(created_inspection_grade.user.id, inspection_grade_data["user_id"])
        self.assertEqual(created_inspection_grade.approver, provider_user)
        self.assertEqual(
            created_inspection_grade.letter_grade, inspection_grade_data["letter_grade"]
        )
        self.assertEqual(created_inspection_grade.notes, inspection_grade_data["notes"])

        send_message.assert_called_once()
