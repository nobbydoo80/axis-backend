__author__ = "Artem Hruzd"
__date__ = "04/19/2023 00:17"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


from django.apps import apps
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy

from axis.core.tests.factories import (
    provider_user_factory,
    rater_user_factory,
)
from axis.core.tests.testcases import ApiV3Tests
from axis.customer_hirl.models import COIDocument
from axis.customer_hirl.tests.factories import coi_document_factory

User = get_user_model()
customer_hirl_app = apps.get_app_config("customer_hirl")


class TestCOIDocumentViewSet(ApiV3Tests):
    def test_list(self):
        list_url = reverse_lazy("api_v3:coi_documents-list")
        provider_user = provider_user_factory(company__slug=customer_hirl_app.CUSTOMER_SLUG)
        rater_user = rater_user_factory()

        provider_coi_document = coi_document_factory(company=provider_user.company)
        rater_coi_document = coi_document_factory(company=rater_user.company)

        coi_documents = COIDocument.objects.all()
        self.assertEqual(coi_documents.count(), 2)

        data = self.list(url=list_url, user=provider_user)

        self.assertEqual(len(data), coi_documents.count())

        data = self.list(url=list_url, user=rater_user)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["id"], rater_coi_document.id)

    def test_create(self):
        provider_user = provider_user_factory(company__slug=customer_hirl_app.CUSTOMER_SLUG)
        rater_user = rater_user_factory()

        valid_data = dict(
            description="Description test",
            policy_number="Policy Number test",
            start_date="2023-04-30",
            expiration_date="2023-04-27",
        )

        create_url = reverse_lazy(
            "api_v3:company-coi_documents-list", args=(rater_user.company.id,)
        )

        with self.subTest("Create with rater_user and try to set readonly fields"):
            data = self.create(url=create_url, user=rater_user, data=valid_data)

            self.assertEqual(data["start_date"], None)
            self.assertEqual(data["expiration_date"], None)
            self.assertEqual(data["description"], valid_data["description"])

        with self.subTest("Create as HIRL user"):
            data = self.create(
                url=create_url,
                user=provider_user,
                data=valid_data,
            )

            self.assertEqual(data["start_date"], valid_data["start_date"])
            self.assertEqual(data["expiration_date"], valid_data["expiration_date"])
            self.assertEqual(data["description"], valid_data["description"])
