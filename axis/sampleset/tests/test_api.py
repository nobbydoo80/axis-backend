"""test_api.py: Sampleset app """


from django.test.utils import override_settings
from django.urls import reverse

from axis.core.tests.client import AxisClient
from axis.core.tests.testcases import ApiV3Tests
from axis.home.models import EEPProgramHomeStatus
from .mixins import SampleSetTestMixin
from ..models import SampleSet

__author__ = "Artem Hruzd"
__date__ = "11/16/18 1:38 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
]


class SampleSetViewSetTests(SampleSetTestMixin, ApiV3Tests):
    client_class = AxisClient

    def test_summary(self):
        user = self.user_model.objects.exclude(company__isnull=True).first()
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )
        sample_set = SampleSet.objects.first()
        url = reverse("apiv2:sampleset-summary", kwargs={"pk": sample_set.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], str(sample_set.pk))
        self.assertEqual(response.data["name"], sample_set.uuid)

    def test_uuid(self):
        user = self.user_model.objects.exclude(company__isnull=True).first()
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )
        url = reverse("apiv2:sampleset-uuid")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.data.get("uuid"))

    def test_analyze(self):
        eep_program_home_statuses = EEPProgramHomeStatus.objects.order_by("?").values_list(
            "id", flat=True
        )[:4]

        user = self.user_model.objects.exclude(company__isnull=True).first()
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )
        url = reverse("apiv2:sampleset-analyze")
        response = self.client.get(
            url,
            data={
                "test": list(eep_program_home_statuses)[:2],
                "sampled": list(eep_program_home_statuses)[2:],
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["added"], set(eep_program_home_statuses))
        self.assertTrue(response.data["is_metro_sampled"])
        self.assertEqual(
            response.data["messages"],
            [
                {
                    "message": "Sample set uses more than one builder.",
                    "code": "mismatched_builders",
                    "level": "ERROR",
                }
            ],
        )

    @override_settings(SAMPLING_MAX_SIZE=-1)
    def test_commit_sampling_oversize(self):
        eep_program_home_statuses = EEPProgramHomeStatus.objects.order_by("?").values_list(
            "id", flat=True
        )[:4]

        user = self.user_model.objects.exclude(company__isnull=True).first()
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )
        url = reverse("apiv2:sampleset-commit")

        response = self.client.post(
            url,
            data={
                "uuid": "testobj",
                "alt_name": "testobj",
                "test": list(eep_program_home_statuses)[:2],
                "sampled": list(eep_program_home_statuses)[2:],
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "New configuration has too many items")

    @override_settings(SAMPLING_MAX_SIZE=4)
    def test_commit(self):
        eep_program_home_statuses = EEPProgramHomeStatus.objects.order_by("pk").values_list(
            "id", flat=True
        )[:4]

        user = self.user_model.objects.exclude(company__isnull=True).first()
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )
        url = reverse("apiv2:sampleset-commit")
        response = self.client.post(
            url,
            data={
                "uuid": "testobj",
                "alt_name": "testobj",
                "test": list(eep_program_home_statuses)[:2],
                "sampled": list(eep_program_home_statuses)[2:],
            },
        )
        self.assertEqual(response.status_code, 200)
        created_sample_set = SampleSet.objects.filter(alt_name="testobj").first()
        try:
            self.assertIsNotNone(created_sample_set)
        except AssertionError:
            print("Response data: %r" % response.__dict__)
            print("Response data: %r" % response.__dict__)
            print("Samplesets: %r" % SampleSet.objects.all().values_list("uuid", flat=True))
            print("Statuses: %r" % eep_program_home_statuses.all().values_list("pk", flat=True))
            raise

        response = self.client.post(
            url,
            data={
                "sampleset": created_sample_set.pk,
                "test": list(eep_program_home_statuses)[:2],
                "sampled": list(eep_program_home_statuses)[2:],
            },
        )
        self.assertEqual(response.status_code, 200)

    def test_advance(self):
        user = self.user_model.objects.exclude(company__isnull=True).first()
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )
        sample_set = SampleSet.objects.first()
        url = reverse("apiv2:sampleset-advance", kwargs={"pk": sample_set.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)


class SampleSetHomeStatusViewSetTests(SampleSetTestMixin, ApiV3Tests):
    client_class = AxisClient

    def test_list(self):
        user = self.user_model.objects.exclude(company__isnull=True).first()
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )
        url = reverse("apiv2:samplesethomestatus-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
