"""company_tests.py: Django company.tests"""

__author__ = "Steven Klass"
__date__ = "12/3/11 10:08 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

import logging

from django.contrib.auth import get_user_model
from django.core.files import File

from axis.company.models import Company
from axis.company.tests.mixins import CompaniesAndUsersTestMixin
from axis.core.tests.client import AxisClient
from axis.core.tests.testcases import AxisTestCase
from axis.filehandling.models import CustomerDocument

log = logging.getLogger(__name__)


User = get_user_model()


class CompanyViewTests(CompaniesAndUsersTestMixin, AxisTestCase):
    """Test out company application"""

    include_company_types = ["rater", "builder"]
    include_unrelated_companies = False

    client_class = AxisClient

    def test_shared_supplement_docs(self):
        """Test the document sharing capability for both one-way and bi-directional relationships"""

        user = self.user_model.objects.first()
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )
        target = Company.objects.filter_by_company(user.company, show_attached=True).first()

        # Ensure we are bi-directional friends
        self.assertIn(user.company, target.relationships.get_companies())
        self.assertIn(target, user.company.relationships.get_companies())

        self.assertEqual(target.customer_documents.count(), 0)

        # Create a public document
        with open(__file__) as current_file:
            f = File(current_file, name="test.txt")
            CustomerDocument.objects.create(
                document=f,
                description="First Description",
                is_public=True,
                company=user.company,
                content_object=target,
            )
            self.assertEqual(target.customer_documents.count(), 1)
            self.assertEqual(target.customer_documents.all()[0].is_public, True)
