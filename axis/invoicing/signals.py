"""signals.py: """

__author__ = "Artem Hruzd"
__date__ = "04/09/2021 15:25"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

import django_fsm
from django.apps import apps
from django.db.models import Sum
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone

from axis.invoicing.models import InvoiceItemTransaction, InvoiceItemGroup, Invoice, InvoiceItem

customer_hirl_app = apps.get_app_config("customer_hirl")


@receiver(post_save, sender=InvoiceItemTransaction)
def invoice_item_transaction_post_save(sender, instance, created, **kwargs):
    """
    When we have an invoice and we receive new transaction we need to update it's totals
    """
    item = getattr(instance, "item", None)
    if item:
        group = getattr(item, "group", None)
        if group:
            invoice = getattr(group, "invoice", None)
            if invoice:
                __update_invoice_totals(invoice)


@receiver(post_delete, sender=InvoiceItemTransaction)
def invoice_item_transaction_post_delete(sender, instance, **kwargs):
    item = getattr(instance, "item", None)
    if item:
        group = getattr(item, "group", None)
        if group:
            invoice = getattr(group, "invoice", None)
            if invoice:
                __update_invoice_totals(invoice)


@receiver(post_save, sender=InvoiceItem)
def invoice_item_post_save(sender, instance, created, **kwargs):
    """
    When we have an invoice and we update InvoiceItem we need to update it's totals
    """
    group = getattr(instance, "group", None)
    if group:
        invoice = getattr(group, "invoice", None)
        if invoice:
            __update_invoice_totals(invoice)


@receiver(post_delete, sender=InvoiceItem)
def invoice_item_post_delete(sender, instance, **kwargs):
    group = getattr(instance, "group", None)
    if group:
        invoice = getattr(group, "invoice", None)
        if invoice:
            __update_invoice_totals(invoice)


@receiver(post_save, sender=InvoiceItemGroup)
def invoice_item_group_post_save(sender, instance, created, **kwargs):
    """
    When we attach invoice group that already have transactions to Invoice we must mark it as PAID
    """
    from axis.customer_hirl.models import HIRLProject

    invoice = getattr(instance, "invoice", None)
    home_status = getattr(instance, "home_status", None)
    customer_hirl_project = None

    if home_status:
        customer_hirl_project = getattr(home_status, "customer_hirl_project", None)

    if invoice:
        __update_invoice_totals(invoice)
        # Set once when first non Appeals Invoice was created
        if instance.category != InvoiceItemGroup.APPEALS_FEE_CATEGORY and customer_hirl_project:
            HIRLProject.objects.filter(
                id=customer_hirl_project.id, initial_invoice_date__isnull=True
            ).select_for_update().update(initial_invoice_date=invoice.created_at)
    # update billing state for HIRLProject
    if not kwargs.get("raw"):
        if customer_hirl_project:
            __update_billing_state_for_customer_hirl_project(customer_hirl_project)


@receiver(post_delete, sender=InvoiceItemGroup)
def invoice_item_group_post_delete(sender, instance, **kwargs):
    invoice = getattr(instance, "invoice", None)
    if invoice:
        __update_invoice_totals(invoice)


@receiver(post_save, sender=Invoice)
def invoice_post_save(sender, instance, created, **kwargs):
    # Trying to make Invoice as Paid if possible
    if instance.state == Invoice.NEW_STATE:
        try:
            instance.pay()
            instance.save()
        except django_fsm.TransitionNotAllowed:
            pass


def __update_invoice_totals(invoice: Invoice):
    """
    Update invoice total and total_paid fields
    :param invoice: Invoice object
    :return: Invoice
    """
    total = InvoiceItem.objects.filter(group__invoice=invoice).aggregate(total=Sum("cost"))["total"]
    total_paid = InvoiceItemTransaction.objects.filter(item__group__invoice=invoice).aggregate(
        total_paid=Sum("amount")
    )["total_paid"]
    invoice.total = total or 0
    invoice.total_paid = total_paid or 0
    invoice.save()
    return invoice


def __update_billing_state_for_customer_hirl_project(customer_hirl_project):
    if customer_hirl_project:
        customer_hirl_project.calculate_billing_state()
