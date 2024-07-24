__author__ = "Naruhito Kaide"
__date__ = "04/17/2023 08:33"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Naruhito Kaide" "Steven K",
]

import logging

from django.apps import apps
from django.contrib.auth import get_user_model
from axis.company.models import Company
from axis.core.tests.testcases import AxisTestCase

from .factories import fasttracksubmission_factory
from axis.customer_eto.managers import FastTrackSubmissionManager
from axis.customer_eto.models import FastTrackSubmission

log = logging.getLogger(__name__)
app = apps.get_app_config("customer_eto")
User = get_user_model()


class FastTrackSubmissionManagerTestCase(AxisTestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Company 1")
        self.user = User.objects.create(
            username="testuser", email="testuser@example.com", company=self.company
        )
        self.other_company = Company.objects.create(name="Company 2")
        self.other_user = User.objects.create(
            username="othertestuser", email="othertestuser@example.com", company=self.other_company
        )
        self.fasttrack = fasttracksubmission_factory(create_distribution=False)
        self.fasttrack.home_status.company = self.company
        self.fasttrack.home_status.save()
        self.fasttrack.save()

    def test_filter_by_company(self):
        qs = FastTrackSubmission.objects.filter_by_company(self.company)
        self.assertEqual(qs.count(), 1)
        self.assertIn(self.fasttrack, qs)

    def test_filter_by_user(self):
        # Non-authenticated user
        qs = FastTrackSubmission.objects.filter_by_user(None)
        self.assertEqual(qs.count(), 0)

        # Superuser
        self.user.is_superuser = True
        self.user.save()
        qs = FastTrackSubmission.objects.filter_by_user(self.user)
        self.assertEqual(qs.count(), 1)

        # User with matching company slug
        qs = FastTrackSubmission.objects.filter_by_user(self.user)
        self.assertEqual(qs.count(), 1)

        # User without matching company slug
        qs = FastTrackSubmission.objects.filter_by_user(self.other_user)
        self.assertEqual(qs.count(), 0)

        self.user.is_superuser = False
        self.user.save()
        # Test the "otherwise" clause
        self.user.company.slug = "eto"
        self.user.save()
        qs = FastTrackSubmission.objects.filter_by_user(self.user)
        self.assertEqual(qs.count(), 1)

        # Test the "otherwise" clause
        self.user.company.slug = "peci"
        self.user.save()
        qs = FastTrackSubmission.objects.filter_by_user(self.user)
        self.assertEqual(qs.count(), 1)

        # Test the "otherwise" clause
        self.user.company.slug = "other"
        self.user.save()
        qs = FastTrackSubmission.objects.filter_by_user(self.user)
        self.assertEqual(qs.count(), 1)
