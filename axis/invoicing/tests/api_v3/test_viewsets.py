"""viewsets.py: """

__author__ = "Artem Hruzd"
__date__ = "03/17/2021 21:19"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from unittest import mock

from django.apps import apps
from django.urls import reverse_lazy
from rest_framework import status

from axis.company.models import SponsorPreferences
from axis.company.tests.factories import (
    provider_organization_factory,
    builder_organization_factory,
    rater_organization_factory,
    developer_organization_factory,
)
from axis.core.tests.factories import (
    provider_user_factory,
    rater_user_factory,
    builder_user_factory,
    SET_NULL,
)
from axis.core.tests.testcases import ApiV3Tests
from axis.customer_hirl.models import HIRLProjectRegistration, BuilderAgreement
from axis.customer_hirl.tests.factories import (
    hirl_project_factory,
    hirl_project_registration_factory,
    builder_agreement_factory,
)
from axis.eep_program.tests.factories import basic_eep_program_factory
from axis.invoicing.models import InvoiceItemGroup, Invoice
from axis.invoicing.tests.factories import (
    invoice_factory,
    invoice_item_group_factory,
)
from axis.relationship.models import Relationship
from axis.home.models import EEPProgramHomeStatus

customer_hirl_app = apps.get_app_config("customer_hirl")


class TestHIRLInvoiceViewSet(ApiV3Tests):
    def test_customer_hirl_list(self):
        hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )
        hirl_user = provider_user_factory(
            first_name="NGBS", last_name="Admin", company=hirl_company, is_company_admin=True
        )

        builder_organization = builder_organization_factory(name="PUG Builder")

        registration = hirl_project_registration_factory(
            project_type=HIRLProjectRegistration.SINGLE_FAMILY_PROJECT_TYPE,
            builder_organization=builder_organization,
        )
        hirl_project = hirl_project_factory(
            registration=registration, home_status=SET_NULL, home_address_geocode_response=None
        )
        hirl_project.create_home_status()
        hirl_project.save()
        registration.active()
        registration.save()
        hirl_project.refresh_from_db()

        invoice = invoice_factory(
            issuer=hirl_company, customer=builder_organization, created_by=hirl_user
        )
        for invoice_item_group in hirl_project.home_status.invoiceitemgroup_set.all():
            invoice_item_group.invoice = invoice
            invoice_item_group.save()

        list_url = reverse_lazy("api_v3:invoices-customer-hirl-list")
        data = self.list(url=list_url, user=hirl_user)

        self.assertEqual(data[0]["id"], invoice.id)
        self.assertEqual(data[0]["customer_name"], "PUG Builder (NGBS ID: 1)")
        self.assertEqual(data[0]["client_type"], "builder")
        self.assertEqual(data[0]["client_id"], builder_organization.id)
        self.assertEqual(data[0]["client_name"], "PUG Builder (NGBS ID: 1)")
        self.assertEqual(len(data), 1)

    def test_search_with_case_insensitive_id(self):
        hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )
        hirl_user = provider_user_factory(
            first_name="NGBS", last_name="Admin", company=hirl_company, is_company_admin=True
        )
        invoice = invoice_factory(created_by=hirl_user)
        list_url = reverse_lazy("api_v3:invoices-list")
        data = self.list(url=list_url, user=hirl_user)

        self.assertEqual(data[0]["id"], invoice.id)
        self.assertEqual(len(data), 1)

        with self.subTest("Search by case incentive ID"):
            data = self.list(url=f"{list_url}?search={str(invoice.id).upper()}", user=hirl_user)

            self.assertEqual(data[0]["id"], invoice.id)
            self.assertEqual(len(data), 1)

        with self.subTest("Search non existing ID"):
            data = self.list(url=f"{list_url}?search={str(invoice.id).lower()}NOT", user=hirl_user)
            self.assertEqual(len(data), 0)

    @mock.patch("axis.invoicing.messages." "InvoiceCreatedNotificationMessage.send")
    def test_hirl_create_invoice_for_sf_project_as_builder(
        self, invoice_created_notification_message
    ):
        hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )
        provider_user_factory(
            first_name="NGBS", last_name="Admin", company=hirl_company, is_company_admin=True
        )

        provider_user_factory(
            first_name="Non", last_name="admin", company=hirl_company, is_company_admin=False
        )
        builder_organization = builder_organization_factory(name="PUG Builder")
        builder_agreement_factory(
            owner=hirl_company, company=builder_organization, state=BuilderAgreement.COUNTERSIGNED
        )
        builder_user = builder_user_factory(is_company_admin=True, company=builder_organization)

        Relationship.objects.create_mutual_relationships(builder_organization, hirl_company)
        SponsorPreferences.objects.create(
            sponsor=hirl_company, sponsored_company=builder_organization
        )
        builder_organization.update_permissions()

        rater_organization = rater_organization_factory()
        company_admin_rater_user = rater_user_factory(
            is_company_admin=True, company=rater_organization
        )

        eep_program = basic_eep_program_factory(
            name="SF New Construction 2020",
            slug="ngbs-sf-new-construction-2020-new",
            customer_hirl_certification_fee=300,
        )

        sf_registration = hirl_project_registration_factory(
            project_type=HIRLProjectRegistration.SINGLE_FAMILY_PROJECT_TYPE,
            builder_organization=builder_organization,
            eep_program=eep_program,
        )
        sf_project = hirl_project_factory(
            registration=sf_registration, home_address_geocode_response=None
        )

        sf_registration.active()
        sf_project.create_home_status()

        sf_project.refresh_from_db()
        most_recent_notice_sent = sf_project.most_recent_notice_sent
        self.assertIsNotNone(most_recent_notice_sent)

        # expect Invoice Item Group created after create home
        self.assertEqual(InvoiceItemGroup.objects.filter(invoice__isnull=True).count(), 1)

        create_url = reverse_lazy("api_v3:invoices-hirl-create-invoice")

        kwargs = dict(
            url=create_url,
            user=builder_user,
            data=dict(
                issuer=hirl_company.id,
                customer=builder_organization.id,
                invoice_item_groups=list(
                    map(
                        lambda hash_id: str(hash_id),
                        InvoiceItemGroup.objects.values_list("id", flat=True),
                    )
                ),
            ),
        )
        response = self.create(**kwargs)

        sf_project.refresh_from_db()

        self.assertEqual(response["invoice_type"], Invoice.HIRL_PROJECT_INVOICE_TYPE)
        self.assertEqual(response["issuer"], hirl_company.id)
        self.assertEqual(response["customer"], builder_organization.id)
        self.assertEqual(response["created_by"], builder_user.id)
        self.assertEqual(InvoiceItemGroup.objects.filter(invoice__isnull=True).count(), 0)

        sf_project.refresh_from_db()
        self.assertNotEqual(sf_project.most_recent_notice_sent, most_recent_notice_sent)

        invoice_created_notification_message.assert_called_once()

        with self.subTest("Add item group with 0 balance"):
            invoice_item_group = InvoiceItemGroup.objects.create(home_status=sf_project.home_status)
            kwargs = dict(
                url=create_url,
                user=builder_user,
                data=dict(
                    issuer=hirl_company.id,
                    customer=builder_organization.id,
                    invoice_item_groups=[
                        str(invoice_item_group.id),
                    ],
                ),
            )
            self.create(expected_status=status.HTTP_400_BAD_REQUEST, **kwargs)

    def test_customer_hirl_pdf_invoice_report(self):
        hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )
        hirl_user = provider_user_factory(
            first_name="NGBS", last_name="Admin", company=hirl_company, is_company_admin=True
        )

        provider_user_factory(
            first_name="Non", last_name="admin", company=hirl_company, is_company_admin=False
        )
        builder_organization = builder_organization_factory(name="PUG Builder")

        developer_organization = developer_organization_factory()

        registration = hirl_project_registration_factory(
            project_type=HIRLProjectRegistration.SINGLE_FAMILY_PROJECT_TYPE,
            builder_organization=builder_organization,
            developer_organization=developer_organization,
        )
        hirl_project = hirl_project_factory(
            registration=registration, home_status=SET_NULL, home_address_geocode_response=None
        )
        hirl_project.create_home_status()
        hirl_project.save()
        registration.active()
        registration.save()
        hirl_project.refresh_from_db()

        invoice_without_customer = invoice_factory(issuer=hirl_company)
        invoice_with_customer_without_ngbs_id = invoice_factory(
            issuer=hirl_company, customer=developer_organization
        )
        invoice_with_ngbs_id = invoice_factory(issuer=hirl_company, customer=builder_organization)
        for invoice_item_group in hirl_project.home_status.invoiceitemgroup_set.all():
            invoice_item_group.invoice = invoice_with_ngbs_id
            invoice_item_group.save()

        with self.subTest("Builder with NGBS ID"):
            report_url = reverse_lazy(
                "api_v3:invoices-customer-hirl-pdf-invoice-report",
                kwargs={"pk": invoice_with_ngbs_id.id},
            )
            self.client.force_authenticate(user=hirl_user)
            response = self.client.get(report_url)
            self.assertEqual(response.status_code, 200)

        with self.subTest("Developer without NGBS ID"):
            report_url = reverse_lazy(
                "api_v3:invoices-customer-hirl-pdf-invoice-report",
                kwargs={"pk": invoice_with_customer_without_ngbs_id.id},
            )
            self.client.force_authenticate(user=hirl_user)
            response = self.client.get(report_url)
            self.assertEqual(response.status_code, 200)

        with self.subTest("Invoice without customer"):
            report_url = reverse_lazy(
                "api_v3:invoices-customer-hirl-pdf-invoice-report",
                kwargs={"pk": invoice_without_customer.id},
            )
            self.client.force_authenticate(user=hirl_user)
            response = self.client.get(report_url)
            self.assertEqual(response.status_code, 200)
