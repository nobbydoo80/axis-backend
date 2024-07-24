"""factories.py: """

__author__ = "Artem Hruzd"
__date__ = "03/16/2021 20:13"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

import re

from axis.core.utils import random_sequence
from axis.invoicing.models import Invoice, InvoiceItemGroup, InvoiceItem, InvoiceItemTransaction


def invoice_item_transaction_factory(**kwargs):
    invoice_item = kwargs.pop("invoice_item", None)

    if invoice_item is None:
        _kwrgs = {}
        for k, v in list(kwargs.items()):
            if k.startswith("invoice_item__"):
                _kwrgs[re.sub(r"invoice_item__", "", k)] = kwargs.pop(k)
        invoice_item = invoice_item_group_factory(**_kwrgs)

    kwrgs = {
        "created_by": None,
        "note": "",
        "amount": 0,
        "item": invoice_item,
    }
    kwrgs.update(kwargs)
    invoice_item_transaction = InvoiceItemTransaction.objects.create(**kwrgs)
    return invoice_item_transaction


def invoice_item_factory(**kwargs):
    invoice_item_group = kwargs.pop("group", None)

    if invoice_item_group is None:
        _kwrgs = {}
        for k, v in list(kwargs.items()):
            if k.startswith("group__"):
                _kwrgs[re.sub(r"group__", "", k)] = kwargs.pop(k)
        invoice_item_group = invoice_item_group_factory(**_kwrgs)

    kwrgs = {
        "name": random_sequence(4),
        "cost": 0,
        "protected": False,
        "group": invoice_item_group,
    }
    kwrgs.update(kwargs)
    invoice_item = InvoiceItem.objects.create(**kwrgs)
    return invoice_item


def invoice_item_group_factory(**kwargs):
    kwrgs = {
        "invoice": None,
        "home_status": None,
        "created_by": None,
    }
    kwrgs.update(kwargs)
    invoice_item_group = InvoiceItemGroup.objects.create(**kwrgs)
    return invoice_item_group


def invoice_factory(**kwargs):
    invoice_item_groups = kwargs.pop("invoice_item_groups", [])

    kwrgs = {"invoice_number": "", "issuer": None, "customer": None, "total": 0, "total_paid": 0}
    kwrgs.update(kwargs)
    invoice = Invoice.objects.create(**kwrgs)

    for invoice_groups in invoice_item_groups:
        invoice_groups.invoice = invoice
        invoice_groups.save()

    return Invoice.objects.get(pk=invoice.pk)
