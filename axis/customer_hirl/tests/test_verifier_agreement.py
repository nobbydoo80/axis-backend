"""verifier_agreement.py: """
import datetime
import unittest
from unittest import mock
from unittest.mock import patch

from django.apps import apps
from django.urls import reverse
from django.utils import timezone

from axis.company.models import SponsorPreferences
from axis.company.tests.factories import provider_organization_factory, rater_organization_factory
from axis.core.tests.factories import rater_user_factory, provider_user_factory
from axis.core.tests.testcases import AxisTestCase
from axis.customer_hirl.models import VerifierAgreement
from axis.customer_hirl.tasks import (
    verifier_agreement_expire_notification_warning_task,
    verifier_agreement_expire_task,
)
from axis.customer_hirl.tests.factories import verifier_agreement_factory
from axis.customer_hirl.verifier_agreements.states import VerifierAgreementStates

__author__ = "Artem Hruzd"
__date__ = "10/09/2020 10:41"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from axis.filehandling.docusign import DocuSignObject

customer_hirl_app = apps.get_app_config("customer_hirl")


VERIFIER_AGREEMENT_CREATE_DATA = {
    "mailing_geocode_street_line1": "mailing_address_street_line1",
    "mailing_geocode_street_line2": "mailing_address_street_line2",
    "mailing_geocode_city": "1",
    "mailing_geocode_zipcode": "123456",
    "shipping_geocode_street_line1": "shipping_address_street_line1",
    "shipping_geocode_street_line2": "shipping_address_street_line2",
    "shipping_geocode_city": 1,
    "shipping_geocode_zipcode": "123456",
    "website": "website",
    "applicant_first_name": "first",
    "applicant_last_name": "last",
    "applicant_title": "title",
    "applicant_phone_number": "99999999",
    "applicant_cell_number": "",
    "applicant_email": "applicant@gmail.com",
    "administrative_contact_first_name": "first_name",
    "administrative_contact_last_name": "last_name",
    "administrative_contact_phone_number": "phone_number",
    "administrative_contact_email": "administrative@gmail.com",
    "company_with_multiple_verifiers": True,
    "company_officer_first_name": "first_name",
    "company_officer_last_name": "last_name",
    "company_officer_title": "title",
    "company_officer_phone_number": "99999999",
    "company_officer_email": "officer@gmail.com",
}


class VerifierAgreementModelTests(AxisTestCase):
    hirl_company = None
    rater_company = None
    rater_user = None

    @classmethod
    def setUpTestData(cls):
        cls.hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )
        cls.rater_company = rater_organization_factory()
        cls.rater_user = rater_user_factory(company=cls.rater_company)
        cls.verifier_agreement = verifier_agreement_factory(
            verifier=cls.rater_user,
            owner=cls.hirl_company,
        )
        # set va_version_to_sign to 1 by default
        cls.verifier_agreement.date_created = datetime.datetime(year=2019, month=5, day=1).replace(
            tzinfo=datetime.timezone.utc
        )
        cls.verifier_agreement.save()

    @patch.object(DocuSignObject, "update_envelope")
    def test_verifier_agreement_delete_docusign_envelope(self, update_envelope):
        verifier_agreement = VerifierAgreement.objects.get()
        verifier_agreement.verifier_agreement_docusign_data = {"envelope_id": "123-test"}
        verifier_agreement.officer_agreement_docusign_data = {"envelope_id": "123-test"}
        verifier_agreement.hirl_agreement_docusign_data = {"envelope_id": "123-test"}
        verifier_agreement.save()
        verifier_agreement.delete()
        update_envelope.assert_called_with(
            envelope_id="123-test",
            data={
                "status": "voided",
                "voidedReason": f"Automatically set state to Voided, "
                f"because Verifier Agreement on AXIS has been deleted",
            },
        )
        self.assertEqual(update_envelope.call_count, 3)

    def test_get_va_version_to_sign(self):
        verifier_agreement = VerifierAgreement.objects.get()
        self.assertEqual(verifier_agreement.get_va_version_to_sign(), 1)

        verifier_agreement.date_created = datetime.datetime(year=2022, month=9, day=19).replace(
            tzinfo=datetime.timezone.utc
        )
        verifier_agreement.save()
        self.assertEqual(verifier_agreement.get_va_version_to_sign(), 2)


class VerifierAgreementEnrolleeTests(AxisTestCase):
    """Enrollees see menu item and have perms for access the views behind it."""

    @classmethod
    def setUpTestData(cls):
        """Fixture populate method"""
        hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )
        provider_user_factory(
            first_name="NGBS",
            last_name="Admin",
            company=hirl_company,
            is_company_admin=True,
            username=customer_hirl_app.VERIFIER_AGREEMENT_COUNTER_SIGNING_USERNAME,
        )

        rater_org = rater_organization_factory()
        company_admin_rater_user = rater_user_factory(is_company_admin=True, company=rater_org)

        SponsorPreferences.objects.create(sponsor=hirl_company, sponsored_company=rater_org)

        company_admin_rater_user.company.update_permissions()

    def test_has_enrollment_perms(self):
        """Enrollees can 'add', 'change', and 'view'."""
        rater_user = self.get_admin_user(company_type="rater")
        rater_user.company.update_permissions()
        self.assertEqual(rater_user.has_perm("customer_hirl.add_verifieragreement"), True)
        self.assertEqual(rater_user.has_perm("customer_hirl.view_verifieragreement"), True)
        self.assertEqual(rater_user.has_perm("customer_hirl.change_verifieragreement"), True)
        self.assertEqual(rater_user.has_perm("customer_hirl.delete_verifieragreement"), False)

    @unittest.skipIf(
        not customer_hirl_app.VERIFIER_AGREEMENT_ENROLLMENT_ENABLED,
        "Extension is has been disabled",
    )
    def test_sees_enrollment_menu_item(self):
        """Enrollees see the enrollment menu item."""

        rater_user = self.get_admin_user(company_type="rater")
        self.client.force_login(rater_user)

        response = self.client.get("/")
        menu = next(
            (
                x
                for x in response.context["menu"][2].children
                if x.path == reverse("hirl:verifier_agreements:enroll")
            ),
            None,
        )
        self.assertEqual(menu.has_perms, True)

    def test_enroll_menu_redirects_to_new_without_instance(self):
        """Menu item takes users without an enrollment to the creation view."""

        rater_user = self.get_admin_user(company_type="rater")
        rater_user.company.update_permissions()
        self.client.force_login(rater_user)

        self.assertEqual(rater_user.customer_hirl_enrolled_verifier_agreements.count(), 0)
        self.assertRedirects(
            self.client.get(reverse("hirl:verifier_agreements:enroll")),
            reverse("hirl:verifier_agreements:add"),
        )

    def test_enroll_menu_redirects_to_existing_instance(self):
        """Menu item takes users with an enrollment to that enrollment view."""

        rater_user = self.get_admin_user(company_type="rater")
        rater_user.company.update_permissions()
        self.client.force_login(rater_user)
        instance = rater_user.customer_hirl_enrolled_verifier_agreements.create(
            owner=customer_hirl_app.get_customer_company(), verifier=rater_user
        )
        self.assertRedirects(
            self.client.get(reverse("hirl:verifier_agreements:enroll")),
            reverse("hirl:verifier_agreements:examine", kwargs={"pk": instance.pk}),
        )

    def test_initiate_new(self):
        rater_user = self.get_admin_user(company_type="rater")
        rater_user.company.update_permissions()
        self.client.force_login(rater_user)
        va = rater_user.customer_hirl_enrolled_verifier_agreements.create(
            owner=customer_hirl_app.get_customer_company(), verifier=rater_user
        )
        va.state = VerifierAgreementStates.COUNTERSIGNED
        va.save()

        response = self.client.get(reverse("hirl:verifier_agreements:initiate_new"))
        self.assertRedirects(
            response,
            reverse("hirl:verifier_agreements:add"),
        )

        va.refresh_from_db()

        self.assertEqual(va.state, VerifierAgreementStates.EXPIRED)

    # def test_examine_enroll_basic(self):
    #     """Verify that the examine enrollment api can create `BuilderAgreement`s."""
    #
    #     rater_user = self.get_admin_user(company_type='rater')
    #     rater_user.company.update_permissions()
    #     self.client.force_login(rater_user)
    #     city = City.objects.first()
    #
    #     driver = MachineryDriver(
    #         VerifierAgreementEnrollmentMachinery,
    #         create_new=True,
    #         request_user=rater_user)
    #     data = VERIFIER_AGREEMENT_CREATE_DATA.copy()
    #     data['mailing_geocode_city'] = city.pk
    #     data['shipping_geocode_city'] = city.pk
    #     driver.bind(data)
    #
    #     client_object = driver.get_client_object()
    #     response = driver.submit(self.client, method='post')
    #     self.assertEqual(response.status_code, 201)
    #
    #     response_object = driver.get_response_object()
    #
    #     agreement = VerifierAgreement.objects.get(id=response_object['id'])
    #     self.assertEqual(agreement.state, 'new')
    #     self.assertEqual(agreement.agreement_start_date, None)
    #     self.assertEqual(agreement.agreement_expiration_date, None)
    #     self.assertEqual(agreement.mailing_geocode.raw_city, city)


class VerifierAgreementsTasksTests(AxisTestCase):
    @mock.patch(
        "axis.customer_hirl."
        "verifier_agreements.messages.owner."
        "VerifierAgreementExpirationWarningMessage.send"
    )
    def test_verifier_agreement_expire_notification_warning_task(self, warning_send_message):
        hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )
        provider_user_factory(company=hirl_company, is_company_admin=True)
        verifier = rater_user_factory()
        VerifierAgreement.objects.create(
            owner=hirl_company,
            verifier=verifier,
            agreement_expiration_date=timezone.now() + timezone.timedelta(days=60),
        )
        verifier_agreement_expire_notification_warning_task(days_before_expire=60)

        # message for admin and for verifier
        self.assertEqual(warning_send_message.call_count, 2)

    @mock.patch(
        "axis.customer_hirl."
        "verifier_agreements.messages.verifier."
        "ExpiredVerifierAgreementMessage.send"
    )
    @mock.patch(
        "axis.customer_hirl."
        "verifier_agreements.messages.owner."
        "ExpiredOwnerVerifierAgreementMessage.send"
    )
    def test_verifier_agreement_expire_task(self, verifier_send_message, owner_send_message):
        hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )
        provider_user_factory(company=hirl_company, is_company_admin=True)
        verifier = rater_user_factory()
        verifier_agreement = VerifierAgreement.objects.create(
            owner=hirl_company,
            verifier=verifier,
            agreement_expiration_date=timezone.now().date() - timezone.timedelta(days=1),
        )
        self.assertEqual(verifier_agreement.state, VerifierAgreementStates.NEW)
        verifier_agreement_expire_task()
        verifier_send_message.assert_called_once()
        owner_send_message.assert_called_once()
        verifier_agreement.refresh_from_db()
        self.assertEqual(verifier_agreement.state, VerifierAgreementStates.EXPIRED)
