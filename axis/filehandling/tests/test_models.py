"""test_views.py: Django filehandling.tests"""


import logging
import os

from django.core.files import File

from axis.core.tests.testcases import AxisTestCase
from ..models import CustomerDocument

__author__ = "Steven Klass"
__date__ = "1/10/12 3:27 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

from ...company.tests.mixins import CompaniesAndUsersTestMixin

log = logging.getLogger(__name__)


class CustomerDocumentQuerySetTests(CompaniesAndUsersTestMixin, AxisTestCase):
    include_company_types = ["rater", "provider"]
    include_unrelated_companies = False

    def test_public_documents_not_included_by_default(self):
        user_1 = self.get_nonadmin_user(company_type="rater")
        user_2 = self.get_nonadmin_user(company_type="provider")
        with open(__file__) as fh:
            CustomerDocument.objects.create(
                content_object=user_1.company,
                company=user_1.company,
                document=File(fh, name="test.txt"),
                is_public=True,
            )

        # Sanity check that the document exists
        documents = user_1.company.customer_documents.filter_by_user(user_1)
        self.assertEqual(len(documents), 1)

        # Confirm that the public documents are not automatically published to the queryset
        documents = user_1.company.customer_documents.filter_by_user(user_2)
        self.assertEqual(len(documents), 0)

    def test_public_documents_included_upon_request(self):
        user_1 = self.get_nonadmin_user(company_type="rater")
        user_2 = self.get_nonadmin_user(company_type="provider")
        with open(__file__) as fh:
            CustomerDocument.objects.create(
                content_object=user_1.company,
                company=user_1.company,
                document=File(fh, name="test.txt"),
                is_public=True,
            )

        # Sanity check that the document exists
        documents = user_1.company.customer_documents.filter_by_user(user_1)
        self.assertEqual(len(documents), 1)

        # Confirm that the public documents are made available in the queryset when asked
        documents = user_1.company.customer_documents.filter_by_user(user_2, include_public=True)
        self.assertEqual(len(documents), 1)

    def test_shared_public_document_is_not_publicly_editable(self):
        user_1 = self.get_nonadmin_user(company_type="rater")
        user_2 = self.get_nonadmin_user(company_type="provider")
        with open(__file__) as fh:
            document = CustomerDocument.objects.create(
                content_object=user_1.company,
                company=user_1.company,
                document=File(fh, name="test.txt"),
                is_public=True,
            )

        self.assertEqual(document.can_be_edited(user_2), False)
