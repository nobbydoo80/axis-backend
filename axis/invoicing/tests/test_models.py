"""models.py: """

__author__ = "Artem Hruzd"
__date__ = "09/14/2021 11:44 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from unittest import mock

from django.apps import apps
from axis.company.tests.factories import provider_organization_factory
from axis.core.tests.factories import SET_NULL, provider_user_factory
from axis.core.tests.testcases import AxisTestCase
from axis.customer_hirl.models import HIRLProjectRegistration
from axis.customer_hirl.tests.factories import (
    hirl_project_factory,
    hirl_project_registration_factory,
    hirl_green_energy_badge_factory,
)
from axis.invoicing.models import Invoice
from axis.invoicing.tests.factories import (
    invoice_item_factory,
    invoice_factory,
)

customer_hirl_app = apps.get_app_config("customer_hirl")


class TestInvoiceItem(AxisTestCase):
    @mock.patch(
        "axis.invoicing.messages." "invoice_item_group." "HIRLInvoiceItemGroupUpdatedMessage.send"
    )
    def test_customer_hirl_notifications_on_update(self, invoice_update_message):
        hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )
        provider_user_factory(
            first_name="NGBS", last_name="Admin", company=hirl_company, is_company_admin=True
        )
        sf_registration = hirl_project_registration_factory(
            project_type=HIRLProjectRegistration.SINGLE_FAMILY_PROJECT_TYPE,
        )
        sf_project = hirl_project_factory(
            registration=sf_registration, home_status=SET_NULL, home_address_geocode_response=None
        )
        sf_project.create_home_status()
        sf_project.refresh_from_db()

        old_notice_sent = sf_project.most_recent_notice_sent
        self.assertIsNotNone(old_notice_sent)

        hirl_green_energy_badge = hirl_green_energy_badge_factory()

        sf_project.green_energy_badges.add(hirl_green_energy_badge)

        # send update message for CRFP and HI admins
        self.assertEqual(invoice_update_message.call_count, 2)

        invoice_item_group = sf_project.home_status.invoiceitemgroup_set.all().first()
        # create un protected item
        invoice_item_factory(group=invoice_item_group, cost=10)

        sf_project.refresh_from_db()

        # send update message for CRFP and HI admins
        self.assertEqual(invoice_update_message.call_count, 4)
        self.assertNotEqual(sf_project.most_recent_notice_sent, old_notice_sent)

        with self.subTest("Test save item without home_status"):
            invoice_item_factory(cost=20)

            self.assertEqual(invoice_update_message.call_count, 4)

    def test_search_by_case_insensitive_id(self):
        invoice = invoice_factory()
        self.assertEqual(Invoice.objects.count(), 1)
        search_qs = Invoice.objects.all().search_by_case_insensitive_id(
            value=str(invoice.id).upper()
        )
        self.assertEqual(search_qs.count(), 1)

        with self.subTest("With None value"):
            search_qs = Invoice.objects.all().search_by_case_insensitive_id(value=None)
            self.assertEqual(search_qs.count(), 0)

        with self.subTest("With not existing ID"):
            search_qs = Invoice.objects.all().search_by_case_insensitive_id(value="NOT EXISTING ID")
            self.assertEqual(search_qs.count(), 0)
