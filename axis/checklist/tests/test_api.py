from django.urls import reverse
from rest_framework.test import APIClient
from axis.checklist.models import Question, Answer
from axis.core.tests.testcases import AxisTestCase
from django.contrib.auth import get_user_model

from axis.geographic.tests.factories import real_city_factory
from axis.home.models import Home


__author__ = "Steven Klass"
__date__ = "1/20/12 1:28 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

User = get_user_model()


class AnswerSerializationApiTest(AxisTestCase):
    client_class = APIClient

    base64_image = (
        """data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"""
    )

    @classmethod
    def setUpTestData(cls):
        from axis.checklist.tests.factories import question_factory, answer_factory
        from axis.core.tests.factories import general_admin_factory
        from axis.home.tests.factories import custom_home_factory

        city = real_city_factory("Gilbert", "AZ")
        home = custom_home_factory(street_line1="256 W Oxford ln", zipcode="85233", city=city)
        question_factory()
        question = question_factory()
        user = general_admin_factory()
        answer_factory(
            home=home, question=question, user=user, system_no=None, is_considered_failure=False
        )

    def setUp(self):
        super(AnswerSerializationApiTest, self).setUp()
        self.user = self.admin_user
        self.assertTrue(
            self.client.login(username=self.user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (self.user.username, self.user.pk),
        )

    def test_custom_keys_exist(self):
        """Verifies that certain custom keys exist in an Answer dict."""
        answer = Answer.objects.all()[0]

        check_for_keys = [
            "company",
            "first_name",
            "last_name",
            "full_name",
            "lot_number",
            "delete_url",
        ]

        kwargs = {"pk": answer.id}
        url = reverse("apiv2:answer-detail", kwargs=kwargs)
        response = self.client.get(url)

        # good response
        self.assertEqual(response.status_code, 200)

        # all the keys are in the dict
        for key in check_for_keys:
            self.assertIn(
                key, response.data, "{} not found in AnswerSerialization Response".format(key)
            )

        # delete url should be the same as get/post url
        self.assertEqual(str(response.data["delete_url"]), url)

    def test_create_answer_with_images(self):
        """Verifies that base64 images get created correctly when creating an answer."""
        home = Home.objects.all()[0]
        question = Question.objects.filter(answer__isnull=True)[0]

        kwargs = {"pk": home.id, "question_id": question.id}
        url = reverse("apiv2:answer", kwargs=kwargs)

        answer = {
            "home": home.id,
            "question": question.id,
            "user": self.user.id,
            "answer": "testing images",
            "comment": "Test comment",
            "answerimage_set": [{"photo_raw": self.base64_image, "photo_raw_name": "__file__"}],
        }

        response = self.client.post(url, answer, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertIn("answer", response.data)
        self.assertIn("customer_documents", response.data["answer"])

    def test_create_answer_with_documents(self):
        """Verifies that base64 documents get created correctly when creating an answer."""
        home = Home.objects.all()[0]
        question = Question.objects.filter(answer__isnull=True)[0]

        kwargs = {"pk": home.id, "question_id": question.id}
        url = reverse("apiv2:answer", kwargs=kwargs)

        answer = {
            "home": home.id,
            "question": question.id,
            "user": self.user.id,
            "answer": "testing documents",
            "comment": "Test comment",
            "answerdocument_set": [
                {"document_raw": self.base64_image, "document_raw_name": "__file__"}
            ],
        }

        response = self.client.post(url, answer, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertIn("answer", response.data)
        self.assertIn("customer_documents", response.data["answer"])
