__author__ = "Artem Hruzd"
__date__ = "03/03/2021 17:16"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

import itertools
import operator
from functools import reduce

from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django_fsm import FSMField, transition
from hashid_field import HashidAutoField
from simple_history.models import HistoricalRecords

from axis.company.models import Company
from axis.core.checks import register_reportlab_fonts
from .invoice_item import InvoiceItemGroup
from axis.invoicing.messages import HIRLInvoicePaidMessage, HIRLInvoiceCancelledMessage
from axis.core.utils import get_frontend_url

User = get_user_model()
frontend_app = apps.get_app_config("frontend")
register_reportlab_fonts()


class InvoiceQuerySet(models.QuerySet):
    def filter_by_user(self, user):
        if not user.is_authenticated or not user.company:
            return self.none()

        if user.is_superuser:
            return self

        invoice_ids = []

        if user.company.company_type == Company.RATER_COMPANY_TYPE:
            # allow Verifier access for Invoice object created for HIRLProject
            invoice_ids = (
                InvoiceItemGroup.objects.filter(
                    invoice__isnull=False,
                    home_status__customer_hirl_project__registration__registration_user__company=user.company,
                )
                .values_list("invoice__id")
                .distinct()
            )

        return self.filter(
            Q(issuer=user.company)
            | Q(customer=user.company)
            | Q(id__in=invoice_ids)
            | Q(created_by=user)
        ).distinct()

    def search_by_case_insensitive_id(self, value):
        """
        Allows searching with case-insensitive ID string
        :param value: string search term
        :return: queryset
        """
        invoice_ids = []
        if value and value.startswith("INV"):
            # remove INV prefix to increase performance
            term = value[3:]
            # find all upper, lower and mixed case combinations of a string
            invoice_all_possible_id_terms = map(
                "".join, itertools.product(*zip(term.upper(), term.lower()))
            )
            invoice_all_possible_id_terms = set([f"INV{t}" for t in invoice_all_possible_id_terms])
            invoice_ids = (
                self.model.objects.filter(
                    reduce(
                        operator.or_,
                        [Q(**{"id__icontains": term}) for term in invoice_all_possible_id_terms],
                    )
                )
                .values_list("id", flat=True)
                .distinct()
            )
        return self.filter(id__in=invoice_ids)


class InvoiceManager(models.Manager.from_queryset(InvoiceQuerySet)):
    pass


class Invoice(models.Model):
    """
    Invoice model aggregates all information about payment and represent it
    based on invoice type
    """

    NEW_STATE = "new"
    PAID_STATE = "paid"
    CANCELLED_STATE = "cancelled"

    STATE_CHOICES = (
        (NEW_STATE, "New"),
        (PAID_STATE, "Paid"),
        (CANCELLED_STATE, "Canceled"),
    )

    DEFAULT_INVOICE_TYPE = "default"
    HIRL_PROJECT_INVOICE_TYPE = "hirl_project"

    INVOICE_TYPE_CHOICES = (
        (DEFAULT_INVOICE_TYPE, "Default"),
        (HIRL_PROJECT_INVOICE_TYPE, "Customer HIRL Project"),
    )

    id = HashidAutoField(
        primary_key=True, salt=f"invoicing.Invoice{settings.HASHID_FIELD_SALT}", prefix="INV"
    )

    invoice_type = models.CharField(
        max_length=30, choices=INVOICE_TYPE_CHOICES, default=DEFAULT_INVOICE_TYPE
    )

    state = FSMField(choices=STATE_CHOICES, default=NEW_STATE)
    state_changed_at = models.DateTimeField(auto_now_add=True)

    invoice_number = models.CharField(
        max_length=255, blank=True, help_text="Unique ID for external systems"
    )

    total = models.DecimalField(
        decimal_places=2,
        default=0,
        max_digits=16,
        help_text="Field automatically updating based on InvoiceItem sum cost",
    )
    total_paid = models.DecimalField(
        decimal_places=2,
        default=0,
        max_digits=16,
        help_text="Field automatically updating based on InvoiceItemTransaction sum amount",
    )

    note = models.TextField(blank=True)
    created_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        related_name="%(app_label)s_created_invoices",
        on_delete=models.SET_NULL,
        help_text="If None this means that Invoice has been created automatically",
    )

    issuer = models.ForeignKey(
        "company.Company",
        null=True,
        blank=True,
        related_name="%(app_label)s_issued_invoices",
        on_delete=models.SET_NULL,
    )

    customer = models.ForeignKey(
        "company.Company",
        null=True,
        blank=True,
        related_name="%(app_label)s_invoices",
        on_delete=models.SET_NULL,
        help_text="Company who will pay Invoice",
    )

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = InvoiceManager()
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Invoice"
        ordering = [
            "-updated_at",
        ]

    def __str__(self):
        return f"Invoice ID: {self.id} Type: {self.get_invoice_type_display()}"

    @classmethod
    def from_db(cls, db, field_names, values):
        instance = super(Invoice, cls).from_db(db, field_names, values)
        # customization to store the original field values on the instance
        instance._loaded_values = dict(zip(field_names, values))
        return instance

    def get_absolute_url(self):
        if self.invoice_type == self.HIRL_PROJECT_INVOICE_TYPE:
            return get_frontend_url("hi", "invoices", self.id)
        return ""

    def save(self, **kwargs):
        original = dict()
        if hasattr(self, "_loaded_values"):
            original = self._loaded_values

        if original.get("state") != self.state:
            self.state_changed_at = timezone.now()

        return super(Invoice, self).save(**kwargs)

    @property
    def current_balance(self):
        return self.total - self.total_paid

    def can_pay(self):
        """
        Condition for PAID state transition.

        Customer HIRL invoices can be PAID only if current_balance is < 1.

        :return: Boolean
        """
        if self.total == 0 and self.total_paid == 0:
            return False

        if self.current_balance > 0:
            return False
        return True

    @transition(
        field=state,
        source=NEW_STATE,
        target=PAID_STATE,
        conditions=[
            can_pay,
        ],
    )
    def pay(self):
        url = self.get_absolute_url()

        if self.invoice_type == self.HIRL_PROJECT_INVOICE_TYPE:
            invoice_paid_context = {
                "invoice_detail_url": url,
                "customer": self.customer,
                "customer_url": self.customer.get_absolute_url(),
                "invoice_item_groups": self.invoiceitemgroup_set.all(),
                "invoice_id": self.id,
            }

            HIRLInvoicePaidMessage(url=url).send(company=self.issuer, context=invoice_paid_context)
            HIRLInvoicePaidMessage(url=url).send(
                company=self.customer,
                context=invoice_paid_context,
            )

    @transition(field=state, source=NEW_STATE, target=CANCELLED_STATE)
    def cancel(self):
        url = self.get_absolute_url()

        if self.invoice_type == self.HIRL_PROJECT_INVOICE_TYPE:
            invoice_cancelled_context = {
                "invoice_detail_url": url,
                "customer": self.customer,
                "customer_url": self.customer.get_absolute_url(),
                "invoice_item_groups": self.invoiceitemgroup_set.all(),
                "invoice_id": self.id,
            }

            HIRLInvoiceCancelledMessage(url=url).send(
                company=self.issuer, context=invoice_cancelled_context
            )
            HIRLInvoiceCancelledMessage(url=url).send(
                company=self.customer,
                context=invoice_cancelled_context,
            )
