"""test_api.py: Django incentive_payment"""


import json
import logging
import os

from django.contrib.auth.models import Permission
from django.urls import reverse

from rest_framework.test import APITestCase

from django.contrib.auth import get_user_model
from axis.company.models import Company
from .factories import fasttracksubmission_factory
from ..models import ETOAccount

__author__ = "Steven Klass"
__date__ = "12/19/13 3:42 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)
User = get_user_model()


class FastTrackApiTests(APITestCase):
    fixtures = [os.path.join("scheduling", "initial_seed.json")]

    def setUp(self):
        company = Company.objects.create(name="20th Century Ltd")
        user = User.objects.create(
            username="user", email="moo@aol.com", is_superuser=True, company=company
        )
        self.client.force_authenticate(user=user)

    def test_get_list(self):
        submission = fasttracksubmission_factory(create_distribution=False)
        url = reverse("apiv2:fasttrack-list")

        # Get the object list from the API
        user = submission.home_status.company.users.all()[0]
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Verify that only the one submitted item is in the response
        objects = json.loads(response.content)["results"]
        self.assertEqual(1, len(objects))
        self.assertEqual(str(objects[0]["project_id"]), str(submission.project_id))

    def test_get_detail(self):
        submission = fasttracksubmission_factory(create_distribution=False)
        url = reverse("apiv2:fasttrack-detail", kwargs={"project_id": submission.project_id})

        # Get the object detail from the API
        user = submission.home_status.company.users.all()[0]

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_eto_submission_to_us(self):
        submission = fasttracksubmission_factory(create_distribution=False)
        home_status = submission.home_status
        url = reverse("apiv2:fasttrack-detail", kwargs={"project_id": submission.project_id})

        user = home_status.company.users.all()[0]

        eto_company_account = ETOAccount.objects.create(
            company=home_status.company, account_number="1234"
        )

        data = {
            "status": "Paid",
            "account_number": eto_company_account.account_number,
            "paid_date": "2014-01-01",
            "project_id": submission.project_id,
            # Optional
            "check_number": "90210",
        }

        response = self.client.put(url, data=data)
        self.assertEqual(response.status_code, 200)

        # Verify that an IPPItem was created with the individual cost amount
        ipp_items = home_status.ippitem_set.all()
        self.assertEqual(1, ipp_items.count())

        ipp_item = ipp_items.get()
        distribution = ipp_items.get().incentive_distribution
        self.assertEqual(submission.rater_incentive, ipp_item.cost)
        self.assertEqual(submission.rater_incentive, distribution.total)
        self.assertEqual(distribution.status, 2)
