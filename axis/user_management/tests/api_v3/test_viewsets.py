"""viewsets.py: """

__author__ = "Artem Hruzd"
__date__ = "12/13/2021 19:31"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

import os
from unittest import mock

from django.apps import apps
from django.conf import settings
from django.test import override_settings
from django.urls import reverse_lazy, reverse
from freezegun import freeze_time

from axis.company.models import SponsorPreferences
from axis.company.tests.factories import provider_organization_factory, rater_organization_factory
from axis.core.tests.factories import provider_user_factory, rater_user_factory
from axis.core.tests.testcases import ApiV3Tests
from axis.filehandling.models import AsynchronousProcessedDocument
from axis.user_management.models import Accreditation
from axis.user_management.models import InspectionGrade
from axis.user_management.tests.factories import accreditation_factory
from axis.user_management.tests.factories import inspection_grade_factory

customer_hirl_app = apps.get_app_config("customer_hirl")


class TestAccreditationViewSet(ApiV3Tests):
    def _customer_hirl_certificate_test(self, accreditation_name):
        hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )
        hirl_user = provider_user_factory(
            first_name="NGBS", last_name="Admin", company=hirl_company, is_company_admin=True
        )
        verifier_user = rater_user_factory()

        accreditation = accreditation_factory(
            trainee=verifier_user, approver=hirl_user, name=accreditation_name
        )

        url = reverse_lazy(
            "api_v3:accreditations-generate-certificate", kwargs={"pk": accreditation.pk}
        )
        self.client.force_authenticate(user=verifier_user)
        response = self.client.get(url, content_type="application/pdf")

        self.assertEqual(response.status_code, 200)

        with self.subTest("Test access with ngbs user"):
            self.client.force_authenticate(user=hirl_user)
            response = self.client.get(url, content_type="application/pdf")

            self.assertEqual(response.status_code, 200)

    def test_generate_master_verifier_certificate(self):
        self._customer_hirl_certificate_test(accreditation_name=Accreditation.MASTER_VERIFIER_NAME)

    def test_generate_2020_ngbs_certificate(self):
        self._customer_hirl_certificate_test(accreditation_name=Accreditation.NGBS_2020_NAME)

    def test_generate_2015_ngbs_certificate(self):
        self._customer_hirl_certificate_test(accreditation_name=Accreditation.NGBS_2015_NAME)

    def test_generate_2012_ngbs_certificate(self):
        self._customer_hirl_certificate_test(accreditation_name=Accreditation.NGBS_2012_NAME)

    def test_generate_wri_verifier_ngbs_certificate(self):
        self._customer_hirl_certificate_test(
            accreditation_name=Accreditation.NGBS_WRI_VERIFIER_NAME
        )

    def test_generate_green_field_rep_ngbs_certificate(self):
        self._customer_hirl_certificate_test(
            accreditation_name=Accreditation.NGBS_GREEN_FIELD_REP_NAME
        )


class TestInspectionGradeViewSet(ApiV3Tests):
    def test_customer_hirl_list(self):
        hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )
        hirl_user = provider_user_factory(
            first_name="NGBS", last_name="Admin", company=hirl_company, is_company_admin=True
        )
        verifier_user = rater_user_factory()
        SponsorPreferences.objects.create(
            sponsor=hirl_company, sponsored_company=verifier_user.company
        )
        verifier_user.company.update_permissions()
        inspection_grade = inspection_grade_factory(user=verifier_user)

        list_url = reverse_lazy("api_v3:inspection_grades-customer-hirl-list")
        data = self.list(url=list_url, user=hirl_user)

        self.assertEqual(data[0]["id"], inspection_grade.id)
        self.assertEqual(len(data), 1)

    @mock.patch("axis.user_management.tasks.inspection_grade_report_task.delay")
    def test_create_approver_report(self, inspection_grade_report_task):
        hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )
        hirl_user = provider_user_factory(
            first_name="NGBS", last_name="Admin", company=hirl_company, is_company_admin=True
        )
        verifier_user = rater_user_factory()
        SponsorPreferences.objects.create(
            sponsor=hirl_company, sponsored_company=verifier_user.company
        )
        verifier_user.company.update_permissions()
        inspection_grade_factory(user=verifier_user)
        inspection_grade_factory(user=verifier_user)

        self.assertTrue(
            self.client.login(username=hirl_user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (hirl_user.username, hirl_user.pk),
        )

        inspection_grade_ids = list(InspectionGrade.objects.values_list("pk", flat=True))
        url = reverse("api_v3:inspection_grades-create-approver-report")
        response = self.client.get(url)

        asynchronous_process_document = AsynchronousProcessedDocument.objects.first()

        self.assertEqual(
            response.json()["id"],
            asynchronous_process_document.id,
        )
        self.assertEqual(
            response.json()["company"],
            hirl_company.id,
        )

        inspection_grade_report_task.assert_called_once_with(
            asynchronous_process_document_id=asynchronous_process_document.id,
            inspection_grade_ids=inspection_grade_ids,
            user_id=hirl_user.id,
        )

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    @freeze_time("2015-4-15")
    @mock.patch(
        "axis.user_management.tasks.inspection_grade_tasks.InspectionGradeCustomerHIRLQuarterReportMessage"
    )
    def test_customer_hirl_inspection_grade_quarter_report(self, quarter_message):
        hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )
        hirl_user = provider_user_factory(
            first_name="NGBS", last_name="Admin", company=hirl_company, is_company_admin=True
        )

        verifier_company1 = rater_organization_factory(name="Verifier company 1")
        verifier_user1 = rater_user_factory(first_name="Verifier1", company=verifier_company1)
        SponsorPreferences.objects.get_or_create(
            sponsor=hirl_user.company, sponsored_company=verifier_user1.company
        )
        verifier_user1.company.update_permissions()

        self.client.force_authenticate(user=hirl_user)
        url = reverse("api_v3:inspection_grades-customer-hirl-inspection-grade-quarter-report")

        with self.subTest("verifier average A - B grades"):
            verifier_user1_grade1 = inspection_grade_factory(
                user=verifier_user1, letter_grade=InspectionGrade.A_GRADE
            )
            verifier_user1_grade2 = inspection_grade_factory(
                user=verifier_user1, letter_grade=InspectionGrade.B_GRADE
            )

            _ = self.client.get(url, content_type="application/pdf")

            quarter_message().send.assert_called_once()
            self.assertEqual(
                quarter_message().content,
                "Congratulations! Throughout {from_date} to {to_date}, you consistently earned high "
                "performance marks from the NGBS Green Review team. Great job! <a href='{url}' "
                "target='_blank'>View your current NGBS Green 6-month grade average</a>",
            )
            quarter_message().email_content = os.path.join(
                settings.SITE_ROOT,
                "axis",
                "user_management",
                "templates",
                "inspection_grade",
                "customer_hirl_inspection_grade_quarter_report_email.html",
            )

        with self.subTest("verifier average grade C"):
            verifier_user1_grade1.letter_grade = InspectionGrade.C_GRADE
            verifier_user1_grade1.save()
            verifier_user1_grade2.letter_grade = InspectionGrade.C_GRADE
            verifier_user1_grade2.save()

            quarter_message().send.call_count = 0

            _ = self.client.get(url, content_type="application/pdf")

            quarter_message().send.assert_called_once()
            self.assertEqual(
                quarter_message().content,
                "<a href='{url}' target='_blank'>View your current NGBS Green 6-month grade average</a>",
            )
            quarter_message().email_content = os.path.join(
                settings.SITE_ROOT,
                "axis",
                "user_management",
                "templates",
                "inspection_grade",
                "customer_hirl_inspection_grade_quarter_report_for_c_grade_email.html",
            )

        with self.subTest("verifier average grade D F"):
            verifier_user1_grade1.letter_grade = InspectionGrade.D_GRADE
            verifier_user1_grade1.save()
            verifier_user1_grade2.letter_grade = InspectionGrade.F_GRADE
            verifier_user1_grade2.save()

            quarter_message().send.call_count = 0

            _ = self.client.get(url, content_type="application/pdf")

            quarter_message().send.assert_called_once()
            self.assertEqual(
                quarter_message().content,
                "<a href='{url}' target='_blank'>View your current NGBS Green 6-month grade average</a>",
            )
            quarter_message().email_content = os.path.join(
                settings.SITE_ROOT,
                "axis",
                "user_management",
                "templates",
                "inspection_grade",
                "customer_hirl_inspection_grade_quarter_report_for_f_grade_email.html",
            )
