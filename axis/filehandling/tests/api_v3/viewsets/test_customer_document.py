"""customer_document.py: """

__author__ = "Artem Hruzd"
__date__ = "04/27/2020 14:40"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

import io

from django.apps import apps

from hashid_field import Hashid
from rest_framework.reverse import reverse_lazy

from axis.company.strings import COMPANY_TYPES_MAPPING
from axis.company.tests.factories import builder_organization_factory
from axis.company.tests.mixins import CompaniesAndUsersTestMixin
from axis.core.tests.factories import builder_user_factory
from axis.core.tests.testcases import ApiV3Tests
from axis.filehandling.tests.factories import customer_document_factory

filehandling_app = apps.get_app_config("filehandling")


class TestCustomerDocumentViewSet(CompaniesAndUsersTestMixin, ApiV3Tests):
    def test_retrieve(self):
        builder_organization = builder_organization_factory()

        for company_type in COMPANY_TYPES_MAPPING.keys():
            user = self.get_random_user(company_type=company_type)
            customer_document = customer_document_factory(
                company=user.company,
                content_object=builder_organization,
                is_public=False,
            )
            detail_url = reverse_lazy(
                "api_v3:customer_document-detail", args=(customer_document.id,)
            )
            data = self.retrieve(url=detail_url, user=user)
            self.assertEqual(data["id"], customer_document.id)

    def test_update(self):
        builder_organization = builder_organization_factory()

        for company_type in COMPANY_TYPES_MAPPING.keys():
            user = self.get_random_user(company_type=company_type)
            customer_document = customer_document_factory(
                company=user.company,
                content_object=builder_organization,
                is_public=False,
            )
            detail_url = reverse_lazy(
                "api_v3:customer_document-detail", args=(customer_document.id,)
            )
            with io.open(__file__, "rb") as f:
                data = self.update(
                    url=detail_url,
                    user=user,
                    partial=True,
                    data=dict(document=f, description="test description", is_public=True),
                    data_format="multipart",
                )
                self.assertEqual(data["id"], customer_document.id)
                self.assertEqual(data["description"], "test description")
                self.assertTrue(data["is_public"])

    def test_preview(self):
        builder_organization = builder_organization_factory()
        user = builder_user_factory(company=builder_organization)
        customer_document = customer_document_factory(
            company=builder_organization,
            content_object=builder_organization,
            is_public=False,
        )
        preview_url = reverse_lazy("api_v3:customer_document-preview", args=(customer_document.id,))
        self.client.force_authenticate(user=user)
        response = self.client.get(preview_url, format="json")
        # check that our redirect is correct, but do not check target status
        self.assertRedirects(
            response,
            customer_document.document.url,
            target_status_code=404,
            fetch_redirect_response=False,
        )

    def test_login_not_required(self):
        builder_organization = builder_organization_factory()
        customer_document = customer_document_factory(
            company=builder_organization,
            content_object=builder_organization,
            is_public=False,
        )
        self.assertTrue(customer_document.login_required)

        hash_id = Hashid(customer_document.id, salt=filehandling_app.HASHID_FILE_HANDLING_SALT)
        with self.subTest("Passing the ID in lieu of the Hash"):
            public_url = reverse_lazy("api_v3:public_document-detail", args=(customer_document.id,))
            response = self.client.get(public_url)
            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.json(), {"detail": "Not found."})
        with self.subTest("Right ID document requires a login_required=False"):
            public_url = reverse_lazy("api_v3:public_document-detail", args=(hash_id.hashid,))
            response = self.client.get(public_url)
            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.json(), {"detail": "Not found."})

        with self.subTest("Get the document"):
            customer_document.login_required = False
            customer_document.save()

            public_url = reverse_lazy("api_v3:public_document-detail", args=(hash_id.hashid,))
            response = self.client.get(public_url)
            self.assertRedirects(
                response,
                customer_document.document.url,
                target_status_code=404,
                fetch_redirect_response=False,
            )
