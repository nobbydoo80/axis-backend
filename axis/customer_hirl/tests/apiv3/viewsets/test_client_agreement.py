__author__ = "Artem Hruzd"
__date__ = "10/11/2021 12:05 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from unittest import mock
from unittest.mock import patch

from django.apps import apps
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.utils import timezone
from rest_framework import status

from axis.annotation.models import Annotation
from axis.annotation.tests.factories import type_factory
from axis.company.tests.factories import provider_organization_factory, builder_organization_factory
from axis.core.tests.factories import provider_user_factory, builder_admin_factory
from axis.core.tests.testcases import ApiV3Tests
from axis.customer_hirl.models import BuilderAgreement
from axis.customer_hirl.tests.factories import builder_agreement_factory
from axis.filehandling.docusign import DocuSignObject
from axis.filehandling.tests.docusign_mocks import DocusignMock
from axis.geocoder.models import Geocode
from axis.geographic.tests.factories import real_city_factory
from axis.geographic.utils.legacy import format_geographic_input

User = get_user_model()
customer_hirl_app = apps.get_app_config("customer_hirl")


class TestClientAgreementViewSet(ApiV3Tests):
    def test_create_without_docusign_as_hirl_user(self):
        hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )
        hirl_user = provider_user_factory(
            first_name="NGBS", last_name="Admin", company=hirl_company, is_company_admin=True
        )

        builder_organization = builder_organization_factory()

        create_without_docusign_url = reverse_lazy(
            "api_v3:client_agreements-create-without-docusign"
        )

        self.client.force_authenticate(user=hirl_user)
        response = self.client.post(
            create_without_docusign_url, data={"company": builder_organization.id}, format="json"
        )

        builder_agreement = BuilderAgreement.objects.get()
        self.assertEqual(response.data["id"], builder_agreement.id)
        self.assertEqual(response.data["state"], BuilderAgreement.COUNTERSIGNED)
        self.assertEqual(response.data["owner"], hirl_company.id)
        self.assertEqual(response.data["company"], builder_organization.id)

        with self.subTest("Try to create CA with existing"):
            response = self.client.post(
                create_without_docusign_url,
                data={"company": builder_organization.id},
                format="json",
            )
            self.assertEqual(response.status_code, 400)

    @mock.patch("axis.customer_hirl.tasks.post_agreement_for_builder_signing_task.delay")
    def test_create_without_user_as_hirl_user(self, mock_post_agreement_for_builder_signing_task):
        hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )
        hirl_user = provider_user_factory(
            first_name="NGBS", last_name="Admin", company=hirl_company, is_company_admin=False
        )

        builder_organization = builder_organization_factory()

        street_line1 = "479 Washington St"
        street_line2 = ""
        city = real_city_factory("Providence", "RI")
        zipcode = "34342"

        raw_address, raw_parts, entity_type = format_geographic_input(
            street_line1=street_line1, street_line2=street_line2, city=city, zipcode=zipcode
        )

        geocode, _created = Geocode.objects.get_or_create(
            raw_address=raw_address,
            entity_type=entity_type,
            defaults=dict(immediate=True, **raw_parts),
        )

        create_without_user_url = reverse_lazy("api_v3:client_agreements-create-without-user")

        self.client.force_authenticate(user=hirl_user)

        request_data = {
            "company": builder_organization.id,
            "signer_email": "a@a.com",
            "signer_name": "Test Name",
            "mailing_geocode": geocode.id,
        }

        response = self.client.post(
            create_without_user_url,
            data=request_data,
            format="json",
        )

        builder_agreement = BuilderAgreement.objects.get()
        self.assertEqual(response.data["id"], builder_agreement.id)
        self.assertEqual(response.data["state"], BuilderAgreement.NEW)
        self.assertEqual(response.data["owner"], hirl_company.id)
        self.assertEqual(response.data["company"], builder_organization.id)
        self.assertEqual(response.data["signer_email"], "a@a.com")
        self.assertEqual(response.data["signer_name"], "Test Name")
        self.assertEqual(response.data["mailing_geocode"], geocode.id)
        self.assertEqual(builder_agreement.initiator, hirl_user)
        self.assertEqual(builder_agreement.created_by, hirl_user)

        mock_post_agreement_for_builder_signing_task.assert_called_once()

        with self.subTest("Try to create CA with existing"):
            response = self.client.post(
                create_without_user_url,
                data=request_data,
                format="json",
            )
            self.assertEqual(response.status_code, 400)

    @mock.patch("axis.filehandling.docusign.backend.BaseDocuSignObject.check_token")
    @mock.patch("axis.filehandling.docusign.backend.BaseDocuSignObject.session_rest_get")
    @mock.patch("axis.filehandling.docusign.backend.BaseDocuSignObject.session_rest_put")
    def test_resend_docusign_email(self, session_rest_put, session_rest_get, check_token):
        hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )
        hirl_user = provider_user_factory(
            first_name="NGBS", last_name="Admin", company=hirl_company, is_company_admin=True
        )

        builder_organization = builder_organization_factory()

        ca = BuilderAgreement.objects.create(
            owner=hirl_company,
            company=builder_organization,
            data={},
        )

        url = reverse_lazy("api_v3:client_agreements-resend-docusign-email", kwargs={"pk": ca.pk})
        self.client.force_authenticate(user=hirl_user)

        with self.subTest("Test with empty VA"):
            response = self.client.post(url, data=None, format="json")
            data = response.json()
            self.assertEqual(data, False)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        with self.subTest("Test with sent for Builder"):
            session_rest_get().json.return_value = {
                "signers": [{"name": "test name", "email": "test email"}]
            }
            session_rest_put().status_code = status.HTTP_200_OK
            ca.data = {
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
            ca.save()
            response = self.client.post(url, data=None, format="json")
            data = response.json()
            self.assertEqual(data, True)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        with self.subTest("Test with complete for state"):
            session_rest_get().json.return_value = {
                "signers": [{"name": "test name", "email": "test email"}]
            }
            session_rest_put().status_code = status.HTTP_200_OK
            ca.data = {
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
            ca.save()
            response = self.client.post(url, data=None, format="json")
            data = response.json()
            self.assertEqual(data, False)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_note_annotation(self):
        hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )
        hirl_user = provider_user_factory(
            first_name="NGBS", last_name="Admin", company=hirl_company, is_company_admin=True
        )
        builder_organization = builder_organization_factory()

        client_agreement = builder_agreement_factory(
            owner=hirl_company, company=builder_organization
        )

        note_type = type_factory(
            slug="notes",
            applicable_content_types=[
                BuilderAgreement,
            ],
        )

        with self.subTest("Create Note annotation"):
            url = reverse_lazy(
                "api_v3:client_agreements-annotations-list",
                args=(client_agreement.id,),
            )
            response = self.create(
                url=url, user=hirl_user, data={"content": "Test", "type": note_type.id}
            )

            self.assertEqual(response["type"], note_type.id)
            self.assertEqual(response["content"], "Test")
            self.assertEqual(response["user"], hirl_user.id)
            self.assertEqual(response["is_public"], True)
            self.assertEqual(response["field_name"], "")

        with self.subTest("Retrieve Note annotation"):
            annotation = Annotation.objects.get()
            url = reverse_lazy(
                "api_v3:client_agreements-annotations-detail",
                args=(client_agreement.id, annotation.id),
            )
            response = self.retrieve(url=url, user=hirl_user)

            self.assertEqual(response["id"], annotation.id)

        with self.subTest("Update Note annotation"):
            annotation = Annotation.objects.get()
            url = reverse_lazy(
                "api_v3:client_agreements-annotations-detail",
                args=(client_agreement.id, annotation.id),
            )
            response = self.update(
                url=url, user=hirl_user, partial=True, data={"content": "New content"}
            )

            self.assertEqual(response["content"], "New content")

        with self.subTest("Delete Note annotation"):
            annotation = Annotation.objects.get()
            url = reverse_lazy(
                "api_v3:client_agreements-annotations-detail",
                args=(client_agreement.id, annotation.id),
            )
            self.delete(url=url, user=hirl_user)

            self.assertEqual(Annotation.objects.all().count(), 0)

    def test_force_state(self):
        hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )
        hirl_user = provider_user_factory(
            first_name="NGBS", last_name="Admin", company=hirl_company, is_company_admin=True
        )
        client = builder_admin_factory()
        client_agreement = builder_agreement_factory(
            owner=hirl_company, company=client.company, state=BuilderAgreement.NEW
        )
        self.assertEqual(client_agreement.state, BuilderAgreement.NEW)

        url = reverse_lazy(
            "api_v3:client_agreements-force-state", kwargs={"pk": client_agreement.pk}
        )

        with self.subTest("Test force change state by client"):
            self.update(
                url=url,
                user=client,
                data={"state": BuilderAgreement.COUNTERSIGNED},
                partial=True,
                expected_status=status.HTTP_403_FORBIDDEN,
            )

        with self.subTest("Test force change state by NGBS user"):
            self.update(
                url=url,
                user=hirl_user,
                data={"state": BuilderAgreement.COUNTERSIGNED},
                partial=True,
            )

    @patch.object(DocuSignObject, "create_envelope")
    @patch.object(DocuSignObject, "get_envelope_statuses")
    @patch.object(DocuSignObject, "get_envelope_form_data")
    @patch.object(DocuSignObject, "get_completed_documents")
    def test_full_client_agreement_workflow(
        self, _get_docs, _env_form_data, _env_status, _env_create
    ):
        _env_create.return_value = DocusignMock().create_envelope
        _env_status.return_value = DocusignMock().envelope_statuses
        _env_form_data.return_value = DocusignMock().envelope_form_data
        _get_docs.return_value = DocusignMock().get_completed_documents()

        hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )
        hirl_user = provider_user_factory(
            first_name="NGBS",
            last_name="Admin",
            company=hirl_company,
            is_company_admin=True,
            username=customer_hirl_app.BUILDER_AGREEMENT_COUNTER_SIGNING_USERNAME,
        )
        client = builder_admin_factory()

        street_line1 = "479 Washington St"
        city = real_city_factory("Providence", "RI")
        zipcode = "34342"
        geocode_response = Geocode.objects.get_matches(
            street_line1=street_line1, street_line2="", city=city, zipcode=zipcode
        ).first()

        valid_client_agreement_data = {
            "mailing_geocode": geocode_response.geocode.pk,
            "mailing_geocode_response": geocode_response.pk,
            "shipping_geocode": geocode_response.geocode.pk,
            "shipping_geocode_response": geocode_response.pk,
            "primary_contact_first_name": "primary_contact_first_name",
            "primary_contact_last_name": "primary_contact_last_name",
            "primary_contact_title": "primary_contact_title",
            "primary_contact_phone_number": "primary_contact_phone_number",
            "primary_contact_cell_number": "primary_contact_cell_number",
            "primary_contact_email_address": "primary_contact_email_address",
            "secondary_contact_first_name": "secondary_contact_first_name",
            "secondary_contact_last_name": "secondary_contact_last_name",
            "secondary_contact_title": "secondary_contact_title",
            "secondary_contact_phone_number": "secondary_contact_phone_number",
            "secondary_contact_cell_number": "secondary_contact_cell_number",
            "secondary_contact_email_address": "secondary_contact_email_address",
            "payment_contact_first_name": "payment_contact_first_name",
            "payment_contact_last_name": "payment_contact_last_name",
            "payment_contact_title": "payment_contact_title",
            "payment_contact_phone_number": "payment_contact_phone_number",
            "payment_contact_cell_number": "payment_contact_cell_number",
            "payment_contact_email_address": "payment_contact_email_address",
            "use_payment_contact_in_ngbs_green_projects": True,
            "marketing_contact_first_name": "marketing_contact_first_name",
            "marketing_contact_last_name": "marketing_contact_last_name",
            "marketing_contact_title": "marketing_contact_title",
            "marketing_contact_phone_number": "marketing_contact_phone_number",
            "marketing_contact_cell_number": "marketing_contact_cell_number",
            "marketing_contact_email_address": "marketing_contact_email_address",
            "website_contact_first_name": "website_contact_first_name",
            "website_contact_last_name": "website_contact_last_name",
            "website_contact_title": "website_contact_title",
            "website_contact_phone_number": "website_contact_phone_number",
            "website_contact_cell_number": "website_contact_cell_number",
            "website_contact_email_address": "website_contact_email_address",
            "website": "https://homeinnovation.pivotalenergy.net/",
        }

        with self.subTest("Create CA as client"):
            with patch(
                "axis.customer_hirl.builder_agreements.messages.builder."
                "LegalAgreementReadyForSigningMessage.send"
            ) as legal_agreement_ready_send_message:
                url = reverse_lazy("api_v3:client_agreements-list")
                self.create(url=url, user=client, data=valid_client_agreement_data)
                legal_agreement_ready_send_message.assert_called_once()
            agreement = BuilderAgreement.objects.get()
            self.assertEqual(
                agreement.data,
                {
                    "envelope_id": DocusignMock().create_envelope["envelopeId"],
                    "unsigned_upload_result": DocusignMock().create_envelope,
                    "signed_upload_result": None,
                    "latest_result": None,
                },
            )
            self.assertEqual(agreement.state, agreement.NEW)

            # check that data that we send saved in a model
            for k, v in valid_client_agreement_data.items():
                if k in [
                    "mailing_geocode",
                    "mailing_geocode_response",
                    "shipping_geocode",
                    "shipping_geocode_response",
                ]:
                    # handle FK keys
                    self.assertEqual(getattr(agreement, f"{k}_id"), v)
                else:
                    self.assertEqual(getattr(agreement, k), v)

        with self.subTest("Approve CA as NGBS"):
            agreement = BuilderAgreement.objects.get()
            url = reverse_lazy("api_v3:client_agreements-approve", kwargs={"pk": agreement.pk})
            self.create(url=url, user=hirl_user, expected_status=status.HTTP_200_OK)
            agreement.refresh_from_db()

            self.assertEqual(agreement.state, agreement.APPROVED)

        with self.subTest("NGBS Admin set dates"):
            agreement = BuilderAgreement.objects.get()
            self.assertIsNone(agreement.agreement_start_date)
            self.assertIsNone(agreement.agreement_expiration_date)
            url = reverse_lazy("api_v3:client_agreements-detail", kwargs={"pk": agreement.pk})
            self.update(
                url=url,
                user=hirl_user,
                data={
                    "agreement_start_date": "2018-05-20",
                    "agreement_expiration_date": "2050-05-20",
                },
                partial=True,
            )

            agreement.refresh_from_db()
            self.assertIsNotNone(agreement.agreement_start_date)
            self.assertIsNotNone(agreement.agreement_expiration_date)

        with self.subTest("Client sign Document and we update status"):
            agreement = BuilderAgreement.objects.get()
            self.assertIsNone(agreement.signed_agreement_id)
            self.assertIsNone(agreement.certifying_document)
            envelope_statuses = DocusignMock().envelope_statuses
            envelope_statuses["envelopes"][0]["status"] = "completed"

            _env_status.return_value = envelope_statuses
            url = reverse_lazy(
                "api_v3:client_agreements-update-docusign-status", kwargs={"pk": agreement.pk}
            )
            self.create(url=url, user=hirl_user, expected_status=status.HTTP_200_OK)

            agreement.refresh_from_db()
            self.assertIsNotNone(agreement.signed_agreement_id)
            self.assertIsNotNone(agreement.certifying_document)

        with self.subTest("NGBS send document for countersign"):
            with patch(
                "axis.customer_hirl.builder_agreements.messages.owner."
                "LegalAgreementReadyForCountersigningMessage.send"
            ) as legal_agreement_ready_send_message:
                agreement = BuilderAgreement.objects.get()
                url = reverse_lazy("api_v3:client_agreements-verify", kwargs={"pk": agreement.pk})
                self.create(url=url, user=hirl_user, expected_status=status.HTTP_200_OK)
                agreement.refresh_from_db()

                self.assertEqual(agreement.state, agreement.VERIFIED)
                legal_agreement_ready_send_message.assert_called_once()

        with self.subTest("NGBS sign Document and we update status"):
            old_signed_agreement_id = agreement.signed_agreement_id
            old_certifying_document_id = agreement.certifying_document_id

            envelope_statuses = DocusignMock().envelope_statuses
            envelope_statuses["envelopes"][0]["status"] = "completed"

            _env_status.return_value = envelope_statuses

            client.company.street_line1 = None
            client.company.street_line2 = None
            client.company.city = None
            client.company.zipcode = None
            client.company.shipping_geocode = None
            client.company.save()

            with patch(
                "axis.customer_hirl.builder_agreements.messages.builder."
                "EnrollmentCompleteMessage.send"
            ) as complete_send_message:
                agreement = BuilderAgreement.objects.get()
                url = reverse_lazy(
                    "api_v3:client_agreements-update-docusign-status", kwargs={"pk": agreement.pk}
                )
                self.create(url=url, user=hirl_user, expected_status=status.HTTP_200_OK)

                agreement.refresh_from_db()
                self.assertNotEqual(agreement.signed_agreement_id, old_signed_agreement_id)
                self.assertNotEqual(agreement.certifying_document_id, old_certifying_document_id)

                self.assertEqual(agreement.state, agreement.COUNTERSIGNED)
                complete_send_message.assert_called_once()

                client.refresh_from_db()

                self.assertEqual(
                    client.company.street_line1, agreement.mailing_geocode.raw_street_line1
                )
                self.assertEqual(
                    client.company.street_line2, agreement.mailing_geocode.raw_street_line2
                )
                self.assertEqual(client.company.city, agreement.mailing_geocode.raw_city)
                self.assertEqual(client.company.zipcode, agreement.mailing_geocode.raw_zipcode)

                self.assertEqual(client.company.shipping_geocode, agreement.shipping_geocode)

    @patch.object(DocuSignObject, "create_envelope")
    @patch.object(DocuSignObject, "get_envelope_statuses")
    @patch.object(DocuSignObject, "get_envelope_form_data")
    @patch.object(DocuSignObject, "get_completed_documents")
    def test_extension_request_client_agreement_workflow(
        self, _get_docs, _env_form_data, _env_status, _env_create
    ):
        self.test_full_client_agreement_workflow()

        _env_create.return_value = DocusignMock().create_envelope
        _env_status.return_value = DocusignMock().envelope_statuses
        _env_form_data.return_value = DocusignMock().envelope_form_data
        _get_docs.return_value = DocusignMock().get_completed_documents()

        hirl_user = User.objects.get(
            username=customer_hirl_app.BUILDER_AGREEMENT_COUNTER_SIGNING_USERNAME
        )
        agreement = BuilderAgreement.objects.get()
        client = agreement.company.users.first()

        with self.subTest("Initiate Extension Request"):
            self.assertEqual(
                agreement.extension_request_state, BuilderAgreement.EXTENSION_REQUEST_NOT_SENT
            )

            with patch(
                "axis.customer_hirl.builder_agreements.messages.owner."
                "NewExtensionRequestMessage.send"
            ) as initiate_send_message:
                url = reverse_lazy(
                    "api_v3:client_agreements-initiate-extension-request",
                    kwargs={"pk": agreement.pk},
                )
                self.create(url=url, user=client, expected_status=status.HTTP_200_OK)

                agreement.refresh_from_db()
                initiate_send_message.assert_called_once()
                self.assertEqual(
                    agreement.extension_request_state, BuilderAgreement.EXTENSION_REQUEST_INITIATED
                )

        with self.subTest("Approve Client Agreement Extension Request"):
            agreement = BuilderAgreement.objects.get()

            with patch(
                "axis.customer_hirl.builder_agreements.messages.builder."
                "ExtensionRequestApprovedMessage.send"
            ) as approve_send_message:
                url = reverse_lazy(
                    "api_v3:client_agreements-approve-extension-request",
                    kwargs={"pk": agreement.pk},
                )
                self.create(
                    url=url,
                    user=hirl_user,
                    expected_status=status.HTTP_200_OK,
                )

                agreement.refresh_from_db()

                self.assertEqual(
                    agreement.extension_request_state,
                    BuilderAgreement.EXTENSION_REQUEST_SENT_TO_CLIENT,
                )
                approve_send_message.assert_called_once()

        with self.subTest("Client sign Extension Request and we update status"):
            self.assertIsNone(agreement.extension_request_data.get("countersigning_upload_result"))
            self.assertIsNone(agreement.extension_request_signed_agreement_id)
            self.assertIsNone(agreement.extension_request_certifying_document_id)
            self.assertEqual(
                agreement.extension_request_state,
                BuilderAgreement.EXTENSION_REQUEST_SENT_TO_CLIENT,
            )
            envelope_statuses = DocusignMock().envelope_statuses
            envelope_statuses["envelopes"][0]["status"] = "completed"

            _env_status.return_value = envelope_statuses

            with patch(
                "axis.customer_hirl.builder_agreements.messages.owner."
                "ExtensionRequestAgreementReadyForCountersigningMessage.send"
            ) as ready_for_countersign_send_message:
                envelope_statuses = DocusignMock().envelope_statuses
                envelope_statuses["envelopes"][0]["status"] = "completed"

                _env_status.return_value = envelope_statuses
                url = reverse_lazy(
                    "api_v3:client_agreements-update-docusign-status", kwargs={"pk": agreement.pk}
                )
                # mock update_countersigned_extension_request inside update_docusign_status
                # to do not trigger it for our already mocked docusign response
                # envelope_statuses["envelopes"][0]["status"] = "completed",
                # that makes agreement countersigned
                with patch(
                    "axis.customer_hirl.api_v3.viewsets.client_agreement."
                    "update_countersigned_extension_request_agreement_status_from_docusign_task"
                ) as update_countersigned_extension_request_mock:
                    self.create(url=url, user=hirl_user, expected_status=status.HTTP_200_OK)

                    agreement.refresh_from_db()
                    self.assertIsNotNone(agreement.extension_request_signed_agreement_id)
                    self.assertIsNotNone(agreement.extension_request_certifying_document_id)

                    self.assertEqual(
                        agreement.extension_request_state,
                        BuilderAgreement.EXTENSION_REQUEST_SENT_FOR_COUNTERSIGN,
                    )
                    self.assertIsNotNone(
                        agreement.extension_request_data["countersigning_upload_result"]
                    )
                    ready_for_countersign_send_message.assert_called_once()
                    update_countersigned_extension_request_mock.assert_called_once()

        with self.subTest("NGBS sign Extension Request and we update status"):
            old_signed_agreement_id = agreement.extension_request_signed_agreement_id
            old_certifying_document_id = agreement.extension_request_certifying_document_id

            envelope_statuses = DocusignMock().envelope_statuses
            envelope_statuses["envelopes"][0]["status"] = "completed"

            _env_status.return_value = envelope_statuses

            self.assertEqual(
                agreement.extension_request_state,
                BuilderAgreement.EXTENSION_REQUEST_SENT_FOR_COUNTERSIGN,
            )

            with patch(
                "axis.customer_hirl.builder_agreements.messages.builder."
                "ExtensionRequestCompleteMessage.send"
            ) as complete_send_message:
                self.assertIsNotNone(agreement.agreement_expiration_date)
                old_expiration_date = agreement.agreement_expiration_date
                url = reverse_lazy(
                    "api_v3:client_agreements-update-docusign-status", kwargs={"pk": agreement.pk}
                )
                self.create(url=url, user=hirl_user, expected_status=status.HTTP_200_OK)

                agreement.refresh_from_db()
                self.assertNotEqual(
                    agreement.extension_request_signed_agreement_id, old_signed_agreement_id
                )
                self.assertNotEqual(
                    agreement.extension_request_certifying_document_id, old_certifying_document_id
                )

                self.assertEqual(agreement.extension_request_state, agreement.COUNTERSIGNED)
                complete_send_message.assert_called_once()
                self.assertEqual(
                    agreement.agreement_expiration_date,
                    old_expiration_date
                    + timezone.timedelta(days=BuilderAgreement.EXTENSION_REQUEST_DAYS_TO_EXTEND),
                )

    @patch.object(DocuSignObject, "create_envelope")
    @patch.object(DocuSignObject, "get_envelope_statuses")
    @patch.object(DocuSignObject, "get_envelope_form_data")
    @patch.object(DocuSignObject, "get_completed_documents")
    def test_reject_extension_request_client_agreement_workflow(
        self, _get_docs, _env_form_data, _env_status, _env_create
    ):
        self.test_full_client_agreement_workflow()

        _env_create.return_value = DocusignMock().create_envelope
        _env_status.return_value = DocusignMock().envelope_statuses
        _env_form_data.return_value = DocusignMock().envelope_form_data
        _get_docs.return_value = DocusignMock().get_completed_documents()

        hirl_user = User.objects.get(
            username=customer_hirl_app.BUILDER_AGREEMENT_COUNTER_SIGNING_USERNAME
        )
        agreement = BuilderAgreement.objects.get()
        client = agreement.company.users.first()

        with self.subTest("Initiate Extension Request"):
            self.assertEqual(
                agreement.extension_request_state, BuilderAgreement.EXTENSION_REQUEST_NOT_SENT
            )

            with patch(
                "axis.customer_hirl.builder_agreements.messages.owner."
                "NewExtensionRequestMessage.send"
            ) as initiate_send_message:
                url = reverse_lazy(
                    "api_v3:client_agreements-initiate-extension-request",
                    kwargs={"pk": agreement.pk},
                )
                self.create(url=url, user=client, expected_status=status.HTTP_200_OK)

                agreement.refresh_from_db()
                initiate_send_message.assert_called_once()
                self.assertEqual(
                    agreement.extension_request_state, BuilderAgreement.EXTENSION_REQUEST_INITIATED
                )

        with self.subTest("Reject Client Agreement Extension Request"):
            agreement = BuilderAgreement.objects.get()

            with patch(
                "axis.customer_hirl.builder_agreements.messages.builder."
                "ExtensionRequestRejectedMessage.send"
            ) as reject_send_message:
                url = reverse_lazy(
                    "api_v3:client_agreements-reject-extension-request",
                    kwargs={"pk": agreement.pk},
                )
                self.create(
                    url=url,
                    user=hirl_user,
                    data={"reason": "Test reason"},
                    expected_status=status.HTTP_200_OK,
                )

                agreement.refresh_from_db()

                self.assertEqual(agreement.extension_request_reject_reason, "Test reason")
                self.assertEqual(
                    agreement.extension_request_state, BuilderAgreement.EXTENSION_REQUEST_REJECTED
                )
                reject_send_message.assert_called_once()
