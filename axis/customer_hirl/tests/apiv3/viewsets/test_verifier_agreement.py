"""test_verifier_agreement.py: """

__author__ = "Artem Hruzd"
__date__ = "04/19/2022 18:42"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


from unittest import mock

from django.apps import apps
from django.urls import reverse_lazy
from django.utils import timezone
from rest_framework.status import HTTP_200_OK

from axis.company.models import SponsorPreferences
from axis.company.tests.factories import (
    provider_organization_factory,
    rater_organization_factory,
)
from axis.core.tests.factories import provider_user_factory, rater_user_factory
from axis.core.tests.testcases import ApiV3Tests
from axis.customer_hirl.models import VerifierAgreement

customer_hirl_app = apps.get_app_config("customer_hirl")


class TestVerifierAgreementViewSet(ApiV3Tests):
    hirl_company = None
    hirl_user = None

    @classmethod
    def setUpTestData(cls):
        cls.hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )
        cls.hirl_user = provider_user_factory(
            first_name="NGBS",
            last_name="Admin",
            company=cls.hirl_company,
            is_company_admin=True,
            username=customer_hirl_app.VERIFIER_AGREEMENT_COUNTER_SIGNING_USERNAME,
        )

        rater_org = rater_organization_factory()
        company_admin_rater_user = rater_user_factory(is_company_admin=True, company=rater_org)

        SponsorPreferences.objects.create(sponsor=cls.hirl_company, sponsored_company=rater_org)

        company_admin_rater_user.company.update_permissions()

    @mock.patch("axis.filehandling.docusign.backend.BaseDocuSignObject.check_token")
    @mock.patch("axis.filehandling.docusign.backend.BaseDocuSignObject.session_rest_get")
    @mock.patch("axis.filehandling.docusign.backend.BaseDocuSignObject.session_rest_put")
    def test_resend_docusign_email(self, session_rest_put, session_rest_get, check_token):
        verifier = self.get_admin_user(company_type="rater")
        va = VerifierAgreement.objects.create(
            owner=self.hirl_company,
            verifier=verifier,
            agreement_expiration_date=timezone.now() + timezone.timedelta(days=60),
            verifier_agreement_docusign_data={},
            officer_agreement_docusign_data={},
            hirl_agreement_docusign_data={},
        )

        url = reverse_lazy("api_v3:verifier_agreements-resend-docusign-email", kwargs={"pk": va.pk})
        self.client.force_authenticate(user=self.hirl_user)

        with self.subTest("Test with empty VA"):
            response = self.client.post(url, data=None, format="json")
            data = response.json()
            self.assertEqual(data, False)
            self.assertEqual(response.status_code, HTTP_200_OK)

        with self.subTest("Test with sent for Verifier"):
            session_rest_get().json.return_value = {
                "signers": [{"name": "test name", "email": "test email"}]
            }
            session_rest_put().status_code = HTTP_200_OK
            va.verifier_agreement_docusign_data = {
                "envelope_id": "bc9a19cc-3521-40f8-b2d5-4124f95cc0dc",
                "latest_result": None,
                "signed_upload_result": None,
                "unsigned_upload_result": {
                    "uri": "/envelopes/bc9a19cc-3521-40f8-b2d5-4124f95cc0dc",
                    "status": "sent",
                    "envelopeId": "bc9a19cc-3521-40f8-b2d5-4124f95cc0dc",
                    "statusDateTime": "2022-04-19T14:31:55.9170000Z",
                },
            }
            va.save()
            response = self.client.post(url, data=None, format="json")
            data = response.json()
            self.assertEqual(data, True)
            self.assertEqual(response.status_code, HTTP_200_OK)

        with self.subTest("Test with complete for Verifier"):
            session_rest_get().json.return_value = {
                "signers": [{"name": "test name", "email": "test email"}]
            }
            session_rest_put().status_code = HTTP_200_OK
            va.verifier_agreement_docusign_data = {
                "envelope_id": "bc9a19cc-3521-40f8-b2d5-4124f95cc0dc",
                "latest_result": {"source": {"status": "completed"}},
                "signed_upload_result": None,
                "unsigned_upload_result": {
                    "uri": "/envelopes/bc9a19cc-3521-40f8-b2d5-4124f95cc0dc",
                    "status": "sent",
                    "envelopeId": "bc9a19cc-3521-40f8-b2d5-4124f95cc0dc",
                    "statusDateTime": "2022-04-19T14:31:55.9170000Z",
                },
            }
            va.save()
            response = self.client.post(url, data=None, format="json")
            data = response.json()
            self.assertEqual(data, False)
            self.assertEqual(response.status_code, HTTP_200_OK)

        with self.subTest("Test with sent for Officer"):
            session_rest_get().json.return_value = {
                "signers": [{"name": "test name", "email": "test email"}]
            }
            session_rest_put().status_code = HTTP_200_OK
            va.verifier_agreement_docusign_data = {
                "envelope_id": "bc9a19cc-3521-40f8-b2d5-4124f95cc0dc",
                "latest_result": {"source": {"status": "completed"}},
                "signed_upload_result": None,
                "unsigned_upload_result": {
                    "uri": "/envelopes/bc9a19cc-3521-40f8-b2d5-4124f95cc0dc",
                    "status": "sent",
                    "envelopeId": "bc9a19cc-3521-40f8-b2d5-4124f95cc0dc",
                    "statusDateTime": "2022-04-19T14:31:55.9170000Z",
                },
            }
            va.officer_agreement_docusign_data = {
                "envelope_id": "bc9a19cc-3521-40f8-b2d5-4124f95cc0dc",
                "latest_result": {"source": {"status": "sent"}},
                "signed_upload_result": None,
                "unsigned_upload_result": {
                    "uri": "/envelopes/bc9a19cc-3521-40f8-b2d5-4124f95cc0dc",
                    "status": "sent",
                    "envelopeId": "bc9a19cc-3521-40f8-b2d5-4124f95cc0dc",
                    "statusDateTime": "2022-04-19T14:31:55.9170000Z",
                },
            }
            va.save()
            response = self.client.post(url, data=None, format="json")
            data = response.json()
            self.assertEqual(data, True)
            self.assertEqual(response.status_code, HTTP_200_OK)

        with self.subTest("Test with sent for NGBS"):
            session_rest_get().json.return_value = {
                "signers": [{"name": "test name", "email": "test email"}]
            }
            session_rest_put().status_code = HTTP_200_OK
            va.verifier_agreement_docusign_data = {
                "envelope_id": "bc9a19cc-3521-40f8-b2d5-4124f95cc0dc",
                "latest_result": {"source": {"status": "completed"}},
                "signed_upload_result": None,
                "unsigned_upload_result": {
                    "uri": "/envelopes/bc9a19cc-3521-40f8-b2d5-4124f95cc0dc",
                    "status": "sent",
                    "envelopeId": "bc9a19cc-3521-40f8-b2d5-4124f95cc0dc",
                    "statusDateTime": "2022-04-19T14:31:55.9170000Z",
                },
            }
            va.officer_agreement_docusign_data = {
                "envelope_id": "bc9a19cc-3521-40f8-b2d5-4124f95cc0dc",
                "latest_result": {"source": {"status": "completed"}},
                "signed_upload_result": None,
                "unsigned_upload_result": {
                    "uri": "/envelopes/bc9a19cc-3521-40f8-b2d5-4124f95cc0dc",
                    "status": "sent",
                    "envelopeId": "bc9a19cc-3521-40f8-b2d5-4124f95cc0dc",
                    "statusDateTime": "2022-04-19T14:31:55.9170000Z",
                },
            }
            va.hirl_agreement_docusign_data = {
                "envelope_id": "bc9a19cc-3521-40f8-b2d5-4124f95cc0dc",
                "latest_result": {"source": {"status": "sent"}},
                "signed_upload_result": None,
                "unsigned_upload_result": {
                    "uri": "/envelopes/bc9a19cc-3521-40f8-b2d5-4124f95cc0dc",
                    "status": "sent",
                    "envelopeId": "bc9a19cc-3521-40f8-b2d5-4124f95cc0dc",
                    "statusDateTime": "2022-04-19T14:31:55.9170000Z",
                },
            }
            va.save()
            response = self.client.post(url, data=None, format="json")
            data = response.json()
            self.assertEqual(data, True)
            self.assertEqual(response.status_code, HTTP_200_OK)
