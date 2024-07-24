"""signals.py: """

__author__ = "Artem Hruzd"
__date__ = "04/09/2021 15:44"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.apps import apps

from axis.core.tests.testcases import AxisTestCase
from axis.invoicing.models import Invoice
from axis.invoicing.tests.factories import (
    invoice_item_factory,
    invoice_item_transaction_factory,
    invoice_factory,
    invoice_item_group_factory,
)

customer_hirl_app = apps.get_app_config("customer_hirl")


class TestInvoiceItemTransactionSignals(AxisTestCase):
    def test_invoice_move_to_paid_state(self):
        """
        When we have an invoice and we receive new transaction we need to update it's state to PAID
        if all requirements are met
        """
        invoice = invoice_factory()
        invoice_item_group = invoice_item_group_factory()
        invoice_item = invoice_item_factory(group=invoice_item_group, cost=10)

        invoice_item_group.invoice = invoice
        invoice_item_group.save()

        invoice_item_transaction_factory(invoice_item=invoice_item, amount=0)

        invoice.refresh_from_db()
        self.assertEqual(invoice.state, Invoice.NEW_STATE)

        invoice_item_transaction_factory(invoice_item=invoice_item, amount=10)

        invoice.refresh_from_db()
        self.assertEqual(invoice.state, Invoice.PAID_STATE)

    def test_update_invoice_totals(self):
        invoice = invoice_factory()
        invoice_item_group = invoice_item_group_factory()
        invoice_item = invoice_item_factory(group=invoice_item_group, cost=10)
        invoice_item_transaction = invoice_item_transaction_factory(
            invoice_item=invoice_item, amount=10
        )

        invoice_item_group.invoice = invoice
        invoice_item_group.save()

        self.assertEqual(invoice.total, 10)
        self.assertEqual(invoice.total_paid, 10)

        invoice_item.cost = 20
        invoice_item.save()

        invoice_item_transaction2 = invoice_item_transaction_factory(
            invoice_item=invoice_item, amount=10
        )

        self.assertEqual(invoice.total, 20)
        self.assertEqual(invoice.total_paid, 20)

        invoice_item_transaction.delete()

        self.assertEqual(invoice.total, 20)
        self.assertEqual(invoice.total_paid, 10)

        invoice_item_transaction2.delete()

        self.assertEqual(invoice.total, 20)
        self.assertEqual(invoice.total_paid, 0)


class TestInvoiceItemSignals(AxisTestCase):
    def test_update_invoice_totals(self):
        invoice = invoice_factory()
        invoice_item_group = invoice_item_group_factory()
        invoice_item = invoice_item_factory(group=invoice_item_group, cost=10)

        invoice_item_group.invoice = invoice
        invoice_item_group.save()

        self.assertEqual(invoice.total, 10)
        self.assertEqual(invoice.total_paid, 0)

        invoice_item.cost = 20
        invoice_item.save()

        self.assertEqual(invoice.total, 20)
        self.assertEqual(invoice.total_paid, 0)

        invoice_item.delete()

        self.assertEqual(invoice.total, 0)
        self.assertEqual(invoice.total_paid, 0)


class TestInvoiceItemGroupSignals(AxisTestCase):
    def test_invoice_move_to_paid_state(self):
        """
        When we attach invoice group that already have transactions
        to Invoice we must mark it as PAID
        """
        invoice = invoice_factory()
        self.assertEqual(invoice.state, Invoice.NEW_STATE)

        invoice_item_group = invoice_item_group_factory()
        invoice_item = invoice_item_factory(group=invoice_item_group, cost=10)
        invoice_item_transaction_factory(invoice_item=invoice_item, amount=2)
        invoice_item_transaction_factory(invoice_item=invoice_item, amount=2)
        invoice_item_transaction_factory(invoice_item=invoice_item, amount=2)
        invoice_item_transaction_factory(invoice_item=invoice_item, amount=2)
        invoice_item_transaction_factory(invoice_item=invoice_item, amount=2)

        invoice_item_group.invoice = invoice
        invoice_item_group.save()

        invoice.refresh_from_db()
        self.assertEqual(invoice.state, Invoice.PAID_STATE)

    def test_update_invoice_totals(self):
        invoice = invoice_factory()
        invoice_item_group = invoice_item_group_factory()
        invoice_item_factory(group=invoice_item_group, cost=10)

        invoice_item_group.invoice = invoice
        invoice_item_group.save()

        self.assertEqual(invoice.total, 10)
        self.assertEqual(invoice.total_paid, 0)

        invoice_item_group.delete()

        self.assertEqual(invoice.total, 0)
        self.assertEqual(invoice.total_paid, 0)
