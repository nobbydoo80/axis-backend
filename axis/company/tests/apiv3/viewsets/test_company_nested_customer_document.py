__author__ = "Artem Hruzd"
__date__ = "04/27/2020 11:38"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

import io
import zipfile

from django.contrib.auth import get_user_model
from django.urls import reverse_lazy

from axis.company.tests.factories import builder_organization_factory
from axis.company.tests.mixins import CompaniesAndUsersTestMixin
from axis.core.tests.factories import builder_user_factory
from axis.core.tests.testcases import ApiV3Tests

from axis.core.utils import unrandomize_filename

from axis.filehandling.models import AsynchronousProcessedDocument
from axis.filehandling.tests.factories import customer_document_factory

User = get_user_model()


class TestCompanyNestedCustomerDocumentViewSet(CompaniesAndUsersTestMixin, ApiV3Tests):
    include_company_types = ["builder"]
    include_unrelated = False
    include_noperms = False

    def test_list(self):
        user = User.objects.filter(is_superuser=False, company__company_type="builder").first()
        list_url = reverse_lazy("api_v3:company-documents-list", args=(user.company.pk,))
        data = self.list(user=user, url=list_url)
        self.assertEqual(len(data), user.company.customer_documents.count())

    def test_create_as_company_admin_member(self):
        """
        Create customer document as Company Admin member of this company
        """
        builder_company_admin = self.get_admin_user(company_type="builder")
        create_url = reverse_lazy(
            "api_v3:company-documents-list", args=(builder_company_admin.company.id,)
        )

        obj = self.create(
            user=builder_company_admin,
            url=create_url,
            data=dict(
                document=io.open(__file__, "rb"), description="test description", is_public=False
            ),
            data_format="multipart",
        )
        self.assertTrue(bool(obj["document"]))
        self.assertEqual(obj["description"], "test description")
        self.assertFalse(obj["is_public"])

    def test_download_all(self):
        builder_company = builder_organization_factory()
        builder_user = builder_user_factory(company=builder_company)

        cd1 = customer_document_factory(company=builder_company)
        cd2 = customer_document_factory(company=builder_company)

        download_all_url = reverse_lazy(
            "api_v3:company-documents-download-all", args=(builder_company.id,)
        )

        self.client.force_authenticate(user=builder_user)
        response = self.client.get(
            download_all_url,
        )

        async_document = AsynchronousProcessedDocument.objects.get(id=response.data["id"])

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
