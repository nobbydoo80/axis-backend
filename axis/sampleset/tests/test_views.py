"""tests.py: Django sampleset.tests"""


from django.db.models import Count
from django.urls import reverse

from axis.company.models import Company
from axis.core.tests.client import AxisClient
from axis.core.tests.testcases import ApiV3Tests
from axis.eep_program.models import EEPProgram
from axis.home.models import EEPProgramHomeStatus
from axis.subdivision.models import Subdivision
from .mixins import SampleSetTestMixin
from ..models import SampleSet, SampleSetHomeStatus

__author__ = "Artem Hruzd"
__date__ = "6/12/19 1:29 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
]


class SampleSetListViewTests(SampleSetTestMixin, ApiV3Tests):
    client_class = AxisClient

    def test_permissions(self):
        url = reverse("sampleset:list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(url, response["Location"], msg=url)
        self.assertIn(reverse("auth:login"), response["Location"])

        user = self.noperms_user

        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        self.assertFalse(user.has_perm("sampleset.view_sampleset"), True)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_output(self):
        user = self.user_model.objects.exclude(company__isnull=True).first()
        url = reverse("sampleset:list")
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            url, content_type="application/json", HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["recordsTotal"], SampleSet.objects.count())

        # filter list by subdivision
        subdivision = Subdivision.objects.first()
        url = reverse("sampleset:list", kwargs={"subdivision_id": subdivision.pk})
        response = self.client.get(
            url, content_type="application/json", HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(response.status_code, 200)
        sample_set_count = (
            SampleSet.objects.filter(home_statuses__home__subdivision_id=subdivision.pk)
            .distinct()
            .count()
        )
        self.assertEqual(response.json()["recordsTotal"], sample_set_count)


class SampleSetUIViewTests(SampleSetTestMixin, ApiV3Tests):
    client_class = AxisClient

    def test_permissions(self):
        url = reverse("sampleset:control_center")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(url, response["Location"], msg=url)
        self.assertIn(reverse("auth:login"), response["Location"])

        user = self.noperms_user

        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        self.assertFalse(user.has_perm("sampleset.view_samplesethomestatus"), True)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def _apply_filters_and_compare_count_in_results(self, user, count, filters=None):
        url = reverse("sampleset:control_center")
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        response = self.client.get(
            url,
            data=filters,
            content_type="application/json",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.json()["recordsTotal"], count)

    def test_non_json_request(self):
        user = self.user_model.objects.exclude(company__isnull=True).first()
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )
        url = reverse("sampleset:control_center")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_output_without_filters(self):
        user = self.user_model.objects.exclude(company__isnull=True).first()
        queryset = EEPProgramHomeStatus.objects.filter_by_user(user)
        queryset = queryset.filter(
            eep_program__allow_sampling=True, eep_program__required_checklists__isnull=False
        ).distinct()

        self._apply_filters_and_compare_count_in_results(user=user, count=queryset.count())

    def test_output_with_has_sampleset_filter(self):
        user = self.user_model.objects.exclude(company__isnull=True).first()

        # prepare data for filtering
        SampleSetHomeStatus.objects.update(is_active=False)

        queryset = EEPProgramHomeStatus.objects.filter_by_user(user)
        queryset = queryset.filter(
            eep_program__allow_sampling=True, eep_program__required_checklists__isnull=False
        )

        count = queryset.filter(samplesethomestatus__is_active=False).distinct().count()

        self._apply_filters_and_compare_count_in_results(
            user=user,
            filters={
                "has_sampleset": "0",
            },
            count=count,
        )

        count = queryset.filter(samplesethomestatus__is_active=True).distinct().count()

        self._apply_filters_and_compare_count_in_results(
            user=user,
            filters={
                "has_sampleset": "1",
            },
            count=count,
        )

    def test_output_with_has_answers_filter(self):
        user = self.user_model.objects.exclude(company__isnull=True).first()

        # prepare data for filtering
        SampleSetHomeStatus.objects.update(is_active=False)

        queryset = EEPProgramHomeStatus.objects.filter_by_user(user)
        queryset = queryset.filter(
            eep_program__allow_sampling=True, eep_program__required_checklists__isnull=False
        ).annotate(num_answers=Count("home__answer__id"))

        count = queryset.filter(num_answers=0).distinct().count()

        self._apply_filters_and_compare_count_in_results(
            user=user,
            filters={
                "has_answers": "0",
            },
            count=count,
        )

        count = queryset.filter(num_answers__gt=0).distinct().count()

        self._apply_filters_and_compare_count_in_results(
            user=user,
            filters={
                "has_answers": "1",
            },
            count=count,
        )

    def test_output_with_uuid_filter(self):
        user = self.user_model.objects.exclude(company__isnull=True).order_by("id").first()

        # prepare object that we want to search
        # change uuid name
        sample_set = (
            SampleSet.objects.filter(
                home_statuses__in=EEPProgramHomeStatus.objects.filter_by_user(user)
            )
            .annotate(num_home_statuses=Count("samplesethomestatus__id"))
            .filter(num_home_statuses__gt=0)
            .first()
        )

        sample_set.uuid = "nametosearch"
        sample_set.save()

        count = sample_set.home_statuses.count()

        self._apply_filters_and_compare_count_in_results(
            user=user,
            filters={
                "name": "nametosear",
            },
            count=count,
        )

        # test alt_name field to search too
        sample_set.uuid = "no"
        sample_set.alt_name = "nametosearch"
        sample_set.save()

        self._apply_filters_and_compare_count_in_results(
            user=user,
            filters={
                "name": "nametosear",
            },
            count=count,
        )

    def test_output_with_start_date_filter(self):
        user = self.user_model.objects.exclude(company__isnull=True).order_by("id").first()

        sample_set = (
            SampleSet.objects.filter(
                home_statuses__in=EEPProgramHomeStatus.objects.filter_by_user(user)
            )
            .annotate(num_home_statuses=Count("samplesethomestatus__id"))
            .filter(num_home_statuses__gt=0)
            .first()
        )

        count = sample_set.home_statuses.count()

        self._apply_filters_and_compare_count_in_results(
            user=user,
            filters={
                "start_date": sample_set.start_date,
            },
            count=count,
        )

    def test_output_with_eep_program_filter(self):
        user = self.user_model.objects.exclude(company__isnull=True).first()

        eep_program = EEPProgram.objects.first()

        queryset = EEPProgramHomeStatus.objects.filter_by_user(user)
        queryset = queryset.filter(
            eep_program__allow_sampling=True,
            eep_program__required_checklists__isnull=False,
            eep_program=eep_program,
        )

        count = queryset.distinct().count()

        self._apply_filters_and_compare_count_in_results(
            user=user,
            filters={
                "eep_program": eep_program.pk,
            },
            count=count,
        )

        self._apply_filters_and_compare_count_in_results(
            user=user,
            filters={
                "eep_program": [
                    eep_program.pk,
                ],
            },
            count=count,
        )

    def test_output_with_builder_filter(self):
        user = self.user_model.objects.exclude(company__isnull=True).first()

        queryset = EEPProgramHomeStatus.objects.filter_by_user(user)
        company = Company.objects.first()
        queryset = queryset.filter(
            home__relationships__company__company_type="builder",
            home__relationships__company__in=[
                company,
            ],
        )

        count = queryset.distinct().count()

        self._apply_filters_and_compare_count_in_results(
            user=user,
            filters={
                "builder": company.pk,
            },
            count=count,
        )

        self._apply_filters_and_compare_count_in_results(
            user=user,
            filters={
                "builder": [
                    company.pk,
                ],
            },
            count=count,
        )

    def test_output_with_subdivision_filter(self):
        user = self.user_model.objects.exclude(company__isnull=True).first()

        queryset = EEPProgramHomeStatus.objects.filter_by_user(user)
        subdivision = Subdivision.objects.first()
        queryset = queryset.filter(
            home__subdivision_id__in=[
                subdivision,
            ]
        )

        count = queryset.distinct().count()

        self._apply_filters_and_compare_count_in_results(
            user=user,
            filters={
                "subdivision": subdivision.pk,
            },
            count=count,
        )

        self._apply_filters_and_compare_count_in_results(
            user=user,
            filters={
                "subdivision": [
                    subdivision.pk,
                ],
            },
            count=count,
        )

    def test_output_with_homestatus_state_filter(self):
        user = self.user_model.objects.exclude(company__isnull=True).first()

        queryset = (
            EEPProgramHomeStatus.objects.filter_by_user(user)
            .filter(certification_date=None)
            .exclude(state="complete")
        )

        count = queryset.distinct().count()

        self._apply_filters_and_compare_count_in_results(
            user=user,
            filters={
                "homestatus_state": "uncertified",
            },
            count=count,
        )

        queryset = queryset.filter(state="certification_pending")
        count = queryset.distinct().count()

        self._apply_filters_and_compare_count_in_results(
            user=user,
            filters={
                "homestatus_state": "certification_pending",
            },
            count=count,
        )

    def test_output_with_owner_filter(self):
        company = Company.objects.exclude(pk=self.admin_user.company.pk).first()
        queryset = EEPProgramHomeStatus.objects.filter_by_user(self.admin_user).filter(
            company_id__in=[
                company,
            ]
        )

        count = queryset.distinct().count()

        self._apply_filters_and_compare_count_in_results(
            user=self.admin_user,
            filters={
                "owner": company.pk,
            },
            count=count,
        )


class SampleSetDetailViewTests(SampleSetTestMixin, ApiV3Tests):
    client_class = AxisClient

    def test_permissions(self):
        sample_set = SampleSet.objects.first()

        url = reverse("sampleset:view", kwargs={"uuid": sample_set.uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(url, response["Location"], msg=url)
        self.assertIn(reverse("auth:login"), response["Location"])

        user = self.noperms_user

        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        self.assertFalse(user.has_perm("sampleset.view_sampleset"), True)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_output(self):
        user = self.user_model.objects.exclude(company__isnull=True).first()
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )
        sample_set = SampleSet.objects.first()
        sample_set.owner = user.company
        sample_set.save()

        url = reverse("sampleset:view", kwargs={"uuid": sample_set.uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, sample_set.owner.name)
        self.assertContains(response, sample_set.revision)


class SampleSetAjaxHomeProviderTests(SampleSetTestMixin, ApiV3Tests):
    client_class = AxisClient

    def test_permissions(self):
        sample_set = SampleSet.objects.first()

        url = reverse("sampleset:homes", kwargs={"uuid": sample_set.uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(url, response["Location"], msg=url)
        self.assertIn(reverse("auth:login"), response["Location"])

        user = self.noperms_user

        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        self.assertFalse(user.has_perm("sampleset.view_sampleset"), True)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_output(self):
        user = self.user_model.objects.exclude(company__isnull=True).first()
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        sample_set = SampleSet.objects.first()

        url = reverse("sampleset:homes", kwargs={"uuid": sample_set.uuid})
        response = self.client.get(
            url, content_type="application/json", HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(response.status_code, 200)

        count = (
            SampleSetHomeStatus.objects.filter(sampleset__uuid=sample_set.uuid)
            .current()
            .distinct()
            .count()
        )
        self.assertEqual(response.json()["recordsTotal"], count)


class SampleSetAjaxAnswersTests(SampleSetTestMixin, ApiV3Tests):
    client_class = AxisClient

    def test_permissions(self):
        sample_set = SampleSet.objects.first()

        url = reverse("sampleset:answers", kwargs={"uuid": sample_set.uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(url, response["Location"], msg=url)
        self.assertIn(reverse("auth:login"), response["Location"])

        user = self.noperms_user

        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        self.assertFalse(user.has_perm("sampleset.view_sampleset"), True)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_output(self):
        user = self.user_model.objects.exclude(company__isnull=True).first()
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        sample_set = SampleSet.objects.first()

        url = reverse("sampleset:answers", kwargs={"uuid": sample_set.uuid})
        response = self.client.get(
            url, content_type="application/json", HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(response.status_code, 200)

        count = sample_set.get_test_answers().count()
        self.assertEqual(response.json()["recordsTotal"], count)
