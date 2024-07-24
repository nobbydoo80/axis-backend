"""builder_agreement.py: """

__author__ = "Artem Hruzd"
__date__ = "10/09/2020 10:41"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

import datetime
import unittest
from unittest import mock
from unittest.mock import patch

from django.apps import apps
from django.urls import reverse
from django.utils import timezone
from django_fsm import can_proceed, has_transition_perm

from axis.company.tests.factories import builder_organization_factory
from axis.company.tests.factories import provider_organization_factory
from axis.core.tests.testcases import AxisTestCase
from axis.core.utils import get_frontend_url
from axis.customer_hirl.models import BuilderAgreement
from axis.customer_hirl.tasks import (
    builder_agreement_expire_notification_warning_task,
    builder_agreement_expire_task,
)
from axis.customer_hirl.tasks import (
    post_agreement_for_builder_signing_task,
    update_signed_status_from_docusign_task,
    post_agreement_for_owner_countersigning_task,
    update_countersigned_status_from_docusign_task,
)
from axis.customer_hirl.tests.factories import builder_agreement_factory, coi_document_factory
from axis.customer_hirl.tests.mixins import BuilderAgreementHIRLMixin
from axis.filehandling.docusign import DocuSignObject
from axis.filehandling.models import CustomerDocument
from axis.filehandling.tests.docusign_mocks import DocusignMock
from axis.filehandling.tests.factories import customer_document_factory
from axis.geographic.models import County

customer_hirl_app = apps.get_app_config("customer_hirl")


AGREEMENT_CREATE_DATA = {
    "mailing_geocode_street_line1": "mailing_address_street_line1",
    "mailing_geocode_street_line2": "mailing_address_street_line2",
    "mailing_geocode_city": "1",
    "mailing_geocode_zipcode": "123456",
    "shipping_geocode_street_line1": "shipping_address_street_line1",
    "shipping_geocode_street_line2": "shipping_address_street_line2",
    "shipping_geocode_city": 1,
    "shipping_geocode_zipcode": "123456",
    "website": "website",
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
}


class BuilderAgreementModelTests(AxisTestCase):
    hirl_company = None
    builder_company = None

    @classmethod
    def setUpTestData(cls):
        cls.hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )
        cls.builder_company = builder_organization_factory()

    def test_get_ca_version_to_sign(self):
        builder_agreement = builder_agreement_factory(
            owner=self.hirl_company,
        )
        # set ca_version_to_sign to 1 by default
        builder_agreement.date_created = datetime.datetime(
            year=2019, month=5, day=1, tzinfo=datetime.timezone.utc
        )
        builder_agreement.save()

        self.assertEqual(builder_agreement.get_ca_version_to_sign(), 1)

        builder_agreement.date_created = datetime.datetime(
            year=2022, month=7, day=1, tzinfo=datetime.timezone.utc
        )
        builder_agreement.save()
        self.assertEqual(builder_agreement.get_ca_version_to_sign(), 2)

        builder_agreement.date_created = datetime.datetime(
            year=2023, month=4, day=22, tzinfo=datetime.timezone.utc
        )
        builder_agreement.save()
        self.assertEqual(builder_agreement.get_ca_version_to_sign(), 3)

        builder_agreement.date_created = datetime.datetime(
            year=2033, month=5, day=1, tzinfo=datetime.timezone.utc
        )
        builder_agreement.save()
        self.assertEqual(builder_agreement.get_ca_version_to_sign(), 4)

    @patch.object(DocuSignObject, "update_envelope")
    def test_client_agreement_delete_docusign_envelope(self, update_envelope):
        builder_agreement = builder_agreement_factory(
            owner=self.hirl_company, data={"envelope_id": "123-test"}
        )
        builder_agreement.delete()
        update_envelope.assert_called_once_with(
            envelope_id="123-test",
            data={
                "status": "voided",
                "voidedReason": f"Automatically set state to Voided, because Client Agreement on AXIS has been deleted",
            },
        )


class BuilderAgreementEnrolleeTests(BuilderAgreementHIRLMixin, AxisTestCase):
    """Enrollees see menu item and have perms for access the views behind it."""

    def test_has_enrollment_perms(self):
        """Enrollees can 'add', 'change', and 'view'."""

        builder_user = self.get_admin_user(company_type="builder")
        builder_user.company.update_permissions()

        self.assertEqual(builder_user.has_perm("customer_hirl.add_builderagreement"), True)
        self.assertEqual(builder_user.has_perm("customer_hirl.view_builderagreement"), True)
        self.assertEqual(builder_user.has_perm("customer_hirl.change_builderagreement"), True)
        self.assertEqual(builder_user.has_perm("customer_hirl.delete_builderagreement"), False)

    @unittest.skipIf(not customer_hirl_app.ENROLLMENT_ENABLED, "Extension is has been disabled")
    def test_sees_enrollment_menu_item(self):
        """Enrollees see the enrollment menu item."""

        builder_user = self.get_admin_user(company_type="builder")
        builder_user.company.update_permissions()
        self.client.force_login(builder_user)

        response = self.client.get("/")
        menu = next(
            (x for x in response.context["menu"][2].children if x.path == reverse("hirl:enroll")),
            None,
        )
        self.assertEqual(menu.has_perms, True)

    @unittest.skipIf(not customer_hirl_app.ENROLLMENT_ENABLED, "Extension is has been disabled")
    def test_lacks_agreements_list(self):
        """Enrollees cannot see the owner's menu item."""

        builder_user = self.get_admin_user(company_type="builder")
        builder_user.company.update_permissions()
        self.client.force_login(builder_user)

        response = self.client.get("/")
        for menu_item in response.context["menu"]:
            menu = next(
                (x for x in menu_item.children if x.path == reverse("hirl:agreements:list")), None
            )
            self.assertEqual(menu, None)

    def test_enroll_menu_redirects_to_new_without_instance(self):
        """Menu item takes users without an enrollment to the creation view."""

        builder_user = self.get_admin_user(company_type="builder")
        builder_user.company.update_permissions()
        self.client.force_login(builder_user)

        self.assertEqual(builder_user.company.customer_hirl_enrolled_agreements.count(), 0)
        self.assertRedirects(
            self.client.get(reverse("hirl:enroll")),
            get_frontend_url("hi", "client_agreements", "create"),
        )

    def test_enroll_menu_redirects_to_existing_instance(self):
        """Menu item takes users with an enrollment to that enrollment view."""

        builder_user = self.get_admin_user(company_type="builder")
        builder_user.company.update_permissions()
        self.client.force_login(builder_user)

        instance = builder_user.company.customer_hirl_enrolled_agreements.create(
            owner=customer_hirl_app.get_customer_company(), company=builder_user.company
        )
        self.assertRedirects(
            self.client.get(reverse("hirl:enroll")),
            instance.get_absolute_url(),
        )


class BuilderAgreementOwnerTests(BuilderAgreementHIRLMixin, AxisTestCase):
    """Owners see menu item for enrollment management and have perms for list and detail views."""

    def test_has_management_perms(self):
        """Owners can 'change', and 'view', but NOT 'add'."""

        hirl_user = self.get_admin_user(company_type="provider")
        self.client.force_login(hirl_user)

        self.assertEqual(hirl_user.has_perm("customer_hirl.add_builderagreement"), False)
        self.assertEqual(hirl_user.has_perm("customer_hirl.view_builderagreement"), True)
        self.assertEqual(hirl_user.has_perm("customer_hirl.change_builderagreement"), True)
        self.assertEqual(hirl_user.has_perm("customer_hirl.delete_builderagreement"), False)

    def test_lacks_enrollment_menu_item(self):
        """Owner cannot see the enrollees' menu item."""

        hirl_user = self.get_admin_user(company_type="provider")
        self.client.force_login(hirl_user)

        response = self.client.get("/", follow=True)
        for menu_item in response.context["menu"]:
            menu = next((x for x in menu_item.children if x.path == reverse("hirl:enroll")), None)
            self.assertEqual(menu, None)

    @unittest.skipIf(not customer_hirl_app.ENROLLMENT_ENABLED, "Extension is has been disabled")
    def test_sees_agreements_list(self):
        """Owner see the management menu item."""

        hirl_user = self.get_admin_user(company_type="provider")
        self.client.force_login(hirl_user)

        response = self.client.get("/", follow=True)
        menu = next(
            (
                x
                for x in response.context["menu"][2].children
                if x.path == reverse("hirl:agreements:list")
            ),
            None,
        )
        self.assertEqual(menu.has_perms, True)


class BuilderAgreementTransitionTests(BuilderAgreementHIRLMixin, AxisTestCase):
    """Test state machine transition permissions and conditions."""

    def test_NEW_can_only_approve(self):
        """Verify customer can `approve()` only when state is `NEW`."""
        hirl_user = self.get_admin_user(company_type="provider")
        builder_user = self.get_admin_user(company_type="builder")
        agreement = builder_agreement_factory(owner=hirl_user.company, company=builder_user.company)

        self.assertEqual(agreement.state, BuilderAgreement.NEW)

        self.assertEqual(has_transition_perm(agreement.approve, builder_user), False)
        self.assertEqual(has_transition_perm(agreement.verify, builder_user), False)
        self.assertEqual(has_transition_perm(agreement.expire, builder_user), True)

        self.assertEqual(can_proceed(agreement.approve), True)

    @patch.object(DocuSignObject, "create_envelope")
    @patch.object(DocuSignObject, "get_envelope_statuses")
    @patch.object(DocuSignObject, "get_envelope_form_data")
    @patch.object(DocuSignObject, "get_completed_documents")
    def test_countersigning_process(self, _get_docs, _env_form_data, _env_status, _env_create):
        """Test that we can transition over to signed"""
        _env_create.return_value = DocusignMock().create_envelope
        _env_status.return_value = DocusignMock().envelope_statuses_complete
        _env_form_data.return_value = DocusignMock().envelope_form_data_complete
        _get_docs.return_value = DocusignMock().get_completed_documents()

        hirl_user = self.get_admin_user(company_type="provider")
        builder_user = self.get_admin_user(company_type="builder")
        agreement = builder_agreement_factory(
            owner=hirl_user.company,
            company=builder_user.company,
            agreement_start_date=timezone.now(),
            agreement_expiration_date=timezone.now() + timezone.timedelta(days=1),
        )

        customer_document = agreement.generate_unsigned_customer_document()
        post_agreement_for_builder_signing_task(
            agreement_id=agreement.id, customer_document_id=customer_document.id
        )

        self.assertEqual(agreement.state, BuilderAgreement.NEW)
        self.assertEqual(can_proceed(agreement.approve), True)

        agreement.approve()

        self.assertEqual(agreement.state, BuilderAgreement.APPROVED)
        agreement.save(update_fields=["state"])  # This is due to async behavior
        self.assertIsNone(agreement.certifying_document)
        self.assertIsNone(agreement.signed_agreement)

        update_signed_status_from_docusign_task()
        agreement = BuilderAgreement.objects.get(pk=agreement.pk)
        self.assertIsNotNone(agreement.certifying_document)
        self.assertIsNotNone(agreement.signed_agreement)

        coi_document_factory(
            company=agreement.company, expiration_date=timezone.now() + timezone.timedelta(days=100)
        )

        agreement.verify()
        agreement.save()
        agreement.refresh_from_db()
        self.assertEqual(agreement.state, BuilderAgreement.VERIFIED)
        agreement.save(update_fields=["state"])

        with patch(
            "axis.customer_hirl.builder_agreements."
            "messages.owner.LegalAgreementReadyForCountersigningMessage.send"
        ) as legal_agreement_ready_send_message:
            post_agreement_for_owner_countersigning_task(
                agreement_id=agreement.id, customer_document_id=customer_document.id
            )
            legal_agreement_ready_send_message.assert_called_once()

        with patch(
            "axis.customer_hirl.builder_agreements."
            "messages.builder.EnrollmentCompleteMessage.send"
        ) as enrollment_complete_send_message:
            update_countersigned_status_from_docusign_task()
            enrollment_complete_send_message.assert_called_once()

        agreement = BuilderAgreement.objects.get(pk=agreement.pk)
        self.assertEqual(agreement.state, BuilderAgreement.COUNTERSIGNED)


class BuilderAgreementTaskTests(BuilderAgreementHIRLMixin, AxisTestCase):
    """Test out the task for builder agreement"""

    @patch.object(DocuSignObject, "create_envelope")
    def test_post_agreement_for_builder_signing_task(self, _env_create):
        """Test out the post agreement flow"""
        _env_create.return_value = DocusignMock().create_envelope
        hirl_user = self.get_admin_user(company_type="provider")
        builder_user = self.get_admin_user(company_type="builder")
        agreement = builder_agreement_factory(owner=hirl_user.company, company=builder_user.company)
        customer_doc = customer_document_factory(company=agreement.owner, content_object=agreement)

        output = post_agreement_for_builder_signing_task(agreement.pk, customer_doc.pk)
        self.assertIn("has been posted to DocuSign", output)
        self.agreement = BuilderAgreement.objects.get(id=agreement.pk)
        self.assertEqual(self.agreement.data["signed_upload_result"], None)
        self.assertEqual(self.agreement.data["latest_result"], None)
        self.assertIsNotNone(self.agreement.data["unsigned_upload_result"])
        self.assertEqual(self.agreement.data["envelope_id"], "44040055-4fa6-4aed-a1a4-9ed69fab8cc3")

    @patch.object(DocuSignObject, "create_envelope")
    def test_update_status_from_docusign_no_docs(self, _env_create):
        """Test getting the status of the envelope when there aren't any in the queue"""
        _env_create.return_value = DocusignMock().create_envelope
        results = update_signed_status_from_docusign_task()
        self.assertEqual(results["status_message"], "No envelope id found")

    @patch.object(DocuSignObject, "create_envelope")
    @patch.object(DocuSignObject, "get_envelope_statuses")
    @patch.object(DocuSignObject, "get_envelope_form_data")
    def test_update_status_from_docusign_not_ready(self, _env_form_data, _env_status, _env_create):
        """Test getting the status of the envelope when it is not ready.  3 urls will be hit"""
        _env_create.return_value = DocusignMock().create_envelope
        _env_status.return_value = DocusignMock().envelope_statuses
        _env_form_data.return_value = DocusignMock().envelope_form_data

        hirl_user = self.get_admin_user(company_type="provider")
        builder_user = self.get_admin_user(company_type="builder")
        agreement = builder_agreement_factory(owner=hirl_user.company, company=builder_user.company)

        customer_document = agreement.generate_unsigned_customer_document()
        post_agreement_for_builder_signing_task(
            agreement_id=agreement.id, customer_document_id=customer_document.id
        )

        agreement.approve()
        self.assertEqual(agreement.state, BuilderAgreement.APPROVED)
        agreement.save(update_fields=["state"])  # This is due to async behavior

        agreement = BuilderAgreement.objects.get(pk=agreement.pk)
        self.assertEqual(agreement.data["latest_result"], None)

        update_signed_status_from_docusign_task()
        agreement = BuilderAgreement.objects.get(pk=agreement.pk)

        latest_result = agreement.data["latest_result"]
        self.assertEqual(latest_result.get("waiting_on"), "NGBS Admin")
        self.assertEqual(latest_result.get("remaining_signers"), ["NGBS Admin"])

        self.assertEqual(agreement.state, BuilderAgreement.APPROVED)

    @patch.object(DocuSignObject, "create_envelope")
    @patch.object(DocuSignObject, "get_envelope_statuses")
    @patch.object(DocuSignObject, "get_envelope_form_data")
    @patch.object(DocuSignObject, "get_completed_documents")
    def test_update_status_from_docusign_complete_from_approved(
        self, _get_docs, _env_form_data, _env_status, _env_create
    ):
        """Verifies that when we are approved and get the signed docs we move to signed"""
        _env_create.return_value = DocusignMock().create_envelope
        _env_status.return_value = DocusignMock().envelope_statuses_complete
        _env_form_data.return_value = DocusignMock().envelope_form_data_complete
        _get_docs.return_value = DocusignMock().get_completed_documents()

        hirl_user = self.get_admin_user(company_type="provider")
        builder_user = self.get_admin_user(company_type="builder")
        agreement = builder_agreement_factory(owner=hirl_user.company, company=builder_user.company)

        customer_document = agreement.generate_unsigned_customer_document()
        post_agreement_for_builder_signing_task(
            agreement_id=agreement.id, customer_document_id=customer_document.id
        )

        agreement.approve()
        self.assertEqual(agreement.state, BuilderAgreement.APPROVED)
        agreement.save(update_fields=["state"])  # This is due to async behavior

        agreement = BuilderAgreement.objects.get(pk=agreement.pk)
        self.assertEqual(agreement.data["latest_result"], None)

        update_signed_status_from_docusign_task()
        agreement = BuilderAgreement.objects.get(pk=agreement.pk)

        latest_result = agreement.data["latest_result"]
        self.assertEqual(latest_result.get("waiting_on"), None)
        self.assertEqual(latest_result.get("remaining_signers"), [])

        self.assertIsNotNone(agreement.signed_agreement)
        self.assertIsNotNone(agreement.certifying_document)
        self.assertIsNotNone(agreement.data["signed_upload_result"])

    @mock.patch(
        "axis.customer_hirl."
        "builder_agreements.messages.owner."
        "AgreementExpirationWarningMessage.send"
    )
    @mock.patch(
        "axis.customer_hirl."
        "builder_agreements.messages.builder."
        "BuilderAgreementExpirationWarningMessage.send"
    )
    def test_builder_agreement_expire_notification_warning_task(
        self,
        builder_warning_send_message,
        agreement_warning_send_message,
    ):
        hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )
        builder_organization = builder_organization_factory()
        builder_agreement = BuilderAgreement.objects.create(
            owner=hirl_company,
            company=builder_organization,
            state=BuilderAgreement.COUNTERSIGNED,
        )
        builder_agreement_expire_notification_warning_task(days_before_expire=60)
        builder_agreement.refresh_from_db()

        builder_agreement.agreement_expiration_date = timezone.now() + timezone.timedelta(days=60)
        builder_agreement.save()

        builder_agreement_expire_notification_warning_task(days_before_expire=60)

        agreement_warning_send_message.assert_called_once()

        # make sure builder company receive message
        builder_warning_send_message.assert_called_once()

    def test_builder_agreement_expire_notification_warning_without_message_patch_task(self):
        """
        Do not mock message classes to make sure that we are passing arguments correctly
        """
        hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )
        builder_organization = builder_organization_factory()
        BuilderAgreement.objects.create(
            owner=hirl_company,
            company=builder_organization,
            agreement_expiration_date=timezone.now() + timezone.timedelta(days=60),
        )
        builder_agreement_expire_notification_warning_task(days_before_expire=60)

    @mock.patch(
        "axis.customer_hirl."
        "builder_agreements.messages.builder."
        "ExpiredBuilderAgreementMessage.send"
    )
    @mock.patch(
        "axis.customer_hirl."
        "builder_agreements.messages.owner."
        "ExpiredOwnerAgreementMessage.send"
    )
    def test_builder_agreement_expire_task(
        self,
        owner_send_message,
        builder_send_message,
    ):
        hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )
        builder_organization = builder_organization_factory()
        builder_agreement = BuilderAgreement.objects.create(
            owner=hirl_company,
            company=builder_organization,
            agreement_expiration_date=(timezone.now() - timezone.timedelta(days=1)).date(),
        )
        BuilderAgreement.objects.update(state=BuilderAgreement.COUNTERSIGNED)

        builder_agreement.refresh_from_db()
        self.assertEqual(builder_agreement.state, BuilderAgreement.COUNTERSIGNED)

        builder_agreement_expire_task()

        owner_send_message.assert_called_once()
        builder_send_message.assert_called_once()

        builder_agreement.refresh_from_db()

        self.assertEqual(builder_agreement.state, BuilderAgreement.EXPIRED)

    def test_builder_agreement_expire_without_message_patch_task(self):
        """
        Do not mock message classes to make sure that we are passing arguments correctly
        """
        hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )
        builder_organization = builder_organization_factory()
        builder_agreement = BuilderAgreement.objects.create(
            owner=hirl_company,
            company=builder_organization,
            agreement_expiration_date=timezone.now().date() - timezone.timedelta(days=1),
        )
        self.assertEqual(builder_agreement.state, BuilderAgreement.NEW)
        builder_agreement_expire_task()

    def test_builder_agreement_countersign_update_company_address_task(self):
        hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )

        # our builder organization do not have address information
        builder_organization = builder_organization_factory(
            street_line1="", street_line2="", zipcode=""
        )
        builder_organization.counties.clear()

        # prepare CA for Countersigned state
        builder_agreement = builder_agreement_factory(
            owner=hirl_company, company=builder_organization, state=BuilderAgreement.VERIFIED
        )

        self.assertEqual(builder_agreement.state, BuilderAgreement.VERIFIED)
        self.assertIsNotNone(builder_agreement.shipping_geocode)
        self.assertGreater(County.objects.all().count(), 0)
        self.assertEqual(builder_organization.counties.count(), 0)

        # do countersign and check that our Builder address has been populated
        with open(__file__) as fh:
            data = fh.read()
            builder_agreement.countersign(
                countersigned_document=data,
                certifying_document=data,
            )

        builder_organization.refresh_from_db()

        self.assertEqual(
            builder_organization.street_line1, builder_agreement.mailing_geocode.raw_street_line1
        )
        self.assertEqual(
            builder_organization.street_line2, builder_agreement.mailing_geocode.raw_street_line2
        )
        self.assertEqual(builder_organization.city, builder_agreement.mailing_geocode.raw_city)
        self.assertEqual(
            builder_organization.zipcode, builder_agreement.mailing_geocode.raw_zipcode
        )
        self.assertEqual(builder_organization.shipping_geocode, builder_agreement.shipping_geocode)
        self.assertEqual(builder_organization.counties.count(), County.objects.all().count())

        with self.subTest("Test if company have address we do not change anything"):
            builder_agreement.delete()
            builder_agreement = builder_agreement_factory(
                owner=hirl_company,
                company=builder_organization,
                state=BuilderAgreement.VERIFIED,
                street_line1="477 Washington St",
            )
            with open(__file__) as fh:
                data = fh.read()
                builder_agreement.countersign(
                    countersigned_document=data,
                    certifying_document=data,
                )

                builder_organization.refresh_from_db()
                self.assertNotEqual(
                    builder_organization.street_line1,
                    builder_agreement.mailing_geocode.raw_street_line1,
                )
