"""test_project_tracker.py - axis"""

__author__ = "Steven K"
__date__ = "3/22/23 08:29"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import json
import logging
from django.test import RequestFactory, TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework.test import APITestCase
from rest_framework.test import force_authenticate
from axis.customer_eto.api_v3.serializers.project_tracker import ProjectTrackerSerializer
from axis.customer_eto.enumerations import ProjectTrackerSubmissionStatus
from .test_eto_2022 import TestProjectTracker2022Mixin
from axis.customer_eto.models import FastTrackSubmission
from axis.customer_eto.api_v3.viewsets.project_tracker import ProjectTrackerViewSet
from axis.customer_eto.tests.factories import fasttracksubmission_factory

User = get_user_model()
log = logging.getLogger(__name__)


class TestProjectTrackerSerializer(TestProjectTracker2022Mixin, APITestCase):
    def test_no_applicable_types_serializer(self):
        self.assertIn("ENH", self.project_tracker.get_project_types())
        self.assertIn("SLE", self.project_tracker.get_project_types())

        with self.subTest("Empty Test"):
            serializer = ProjectTrackerSerializer(instance=self.project_tracker)
            # print(json.dumps(serializer.data, indent=4))
            data = serializer.data
            self.assertEqual(data["address"], "854 West 27th Avenue, Eugene, OR, 97405")
            self.assertEqual(data["project_id"], "")
            self.assertEqual(data["solar_project_id"], "")
            self.assertEqual(data["submit_user"], None)
            self.assertEqual(data["submit_status"], None)
            self.assertEqual(data["solar_submit_status"], None)
            self.assertEqual(
                data["overall_submission_status"], "ENH: Not Submitted, SLE: Not Submitted"
            )

        with self.subTest("Both"):
            self.project_tracker.project_id = "FOO"
            self.project_tracker.solar_project_id = "BAR"
            self.project_tracker.submit_status = ProjectTrackerSubmissionStatus.SUCCESS
            self.project_tracker.solar_submit_status = ProjectTrackerSubmissionStatus.SUCCESS
            self.project_tracker.save()

            serializer = ProjectTrackerSerializer(instance=self.project_tracker)
            data = serializer.data
            self.assertEqual(data["project_id"], "FOO")
            self.assertEqual(data["solar_project_id"], "BAR")
            self.assertEqual(data["overall_submission_status"], "ENH: Success, SLE: Success")

        with self.subTest("ENH Ony"):
            self.project_tracker.project_id = "FOO"
            self.project_tracker.solar_project_id = None
            self.project_tracker.submit_status = ProjectTrackerSubmissionStatus.SUCCESS
            self.project_tracker.solar_submit_status = None
            self.project_tracker.net_zero_solar_incentive = 0.0
            self.project_tracker.solar_storage_builder_incentive = 0.0
            self.project_tracker.solar_ready_builder_incentive = 0.0
            self.project_tracker.solar_ready_verifier_incentive = 0.0
            self.project_tracker.save()
            self.project_tracker.refresh_from_db()

            self.assertNotIn("SLE", self.project_tracker.get_project_types())

            serializer = ProjectTrackerSerializer(instance=self.project_tracker)
            data = serializer.data
            self.assertEqual(data["project_id"], "FOO")
            self.assertEqual(data["solar_project_id"], "N/A")
            self.assertEqual(data["overall_submission_status"], "Success")


class ProjectTrackerViewSetTestCase(TestProjectTracker2022Mixin, APITestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.view = ProjectTrackerViewSet.as_view({"get": "list"})
        self.user = User.objects.create(username="testuser")
        self.anonymous_user = AnonymousUser()
        self.fast_track_submission = fasttracksubmission_factory(create_distribution=False)

    def test_anonymous_user(self):
        request = self.factory.get("/")
        force_authenticate(request, user=self.anonymous_user)
        response = self.view(request)
        self.assertEqual(response.status_code, 403)
