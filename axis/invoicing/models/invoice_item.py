"""invoice_item.py: """

__author__ = "Artem Hruzd"
__date__ = "03/03/2021 18:03"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

import waffle
from django.apps import apps
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Sum, F, Subquery, OuterRef, DecimalField, Case, When
from django.db.models.functions import Coalesce
from django.utils import timezone
from hashid_field import HashidAutoField
from django.conf import settings
from simple_history.models import HistoricalRecords

from axis.company.models import Company

from axis.core.managers.utils import queryset_user_is_authenticated
from axis.invoicing.messages import HIRLInvoiceItemGroupUpdatedMessage

User = get_user_model()
customer_hirl_app = apps.get_app_config("customer_hirl")


class InvoiceItemGroupQuerySet(models.QuerySet):
    @queryset_user_is_authenticated
    def filter_by_user(self, user):
        if user.is_customer_hirl_company_member():
            return self.filter(home_status__customer_hirl_project__isnull=False)

        if user.is_company_type_member(Company.RATER_COMPANY_TYPE):
            return self.filter(
                home_status__customer_hirl_project__registration__registration_user__company=user.company
            )

        if user.is_company_type_member(Company.BUILDER_COMPANY_TYPE):
            return self.filter(
                home_status__customer_hirl_project__registration__builder_organization=user.company
            )

        if user.is_company_type_member(Company.DEVELOPER_COMPANY_TYPE):
            return self.filter(
                home_status__customer_hirl_project__registration__developer_organization=user.company
            )

        if user.is_company_type_member(Company.COMMUNITY_OWNER_COMPANY_TYPE):
            return self.filter(
                home_status__customer_hirl_project__registration__community_owner_organization=user.company
            )

        if user.is_company_type_member(Company.ARCHITECT_COMPANY_TYPE):
            return self.filter(
                home_status__customer_hirl_project__registration__achitect_organization=user.company
            )
        return self.none()

    def annotate_client_ca_status(self):
        """
        Customer HIRL specific: Annotate current ERFP Client Agreement status
        By default use Builder Organization CA state

        This query is really heavy because of a lot of different sub queries
        :return: Queryset
        """
        from axis.customer_hirl.models import HIRLProjectRegistration
        from axis.customer_hirl.models import BuilderAgreement

        builder_client_agreements = BuilderAgreement.objects.filter(
            company=OuterRef(
                "home_status__customer_hirl_project__registration__builder_organization"
            )
        ).order_by("-date_created")
        architect_client_agreements = BuilderAgreement.objects.filter(
            company=OuterRef(
                "home_status__customer_hirl_project__registration__architect_organization"
            )
        ).order_by("-date_created")
        developer_client_agreements = BuilderAgreement.objects.filter(
            company=OuterRef(
                "home_status__customer_hirl_project__registration__developer_organization"
            )
        ).order_by("-date_created")
        community_owner_client_agreements = BuilderAgreement.objects.filter(
            company=OuterRef(
                "home_status__customer_hirl_project__registration__community_owner_organization"
            )
        ).order_by("-date_created")
        return self.annotate(
            client_ca_status=Case(
                When(
                    home_status__customer_hirl_project__registration__project_client=HIRLProjectRegistration.PROJECT_CLIENT_BUILDER,
                    then=builder_client_agreements.values("state")[:1],
                ),
                When(
                    home_status__customer_hirl_project__registration__project_client=HIRLProjectRegistration.PROJECT_CLIENT_ARCHITECT,
                    then=architect_client_agreements.values("state")[:1],
                ),
                When(
                    home_status__customer_hirl_project__registration__project_client=HIRLProjectRegistration.PROJECT_CLIENT_DEVELOPER,
                    then=developer_client_agreements.values("state")[:1],
                ),
                When(
                    home_status__customer_hirl_project__registration__project_client=HIRLProjectRegistration.PROJECT_CLIENT_OWNER,
                    then=community_owner_client_agreements.values("state")[:1],
                ),
                default=builder_client_agreements.values("state")[:1],
            )
        )


class InvoiceItemGroupManager(models.Manager.from_queryset(InvoiceItemGroupQuerySet)):
    def get_queryset(self):
        # https://stackoverflow.com/a/45803258/1786016
        return (
            super(InvoiceItemGroupManager, self)
            .get_queryset()
            .annotate(
                total=Coalesce(
                    Subquery(
                        InvoiceItem.objects.filter(group=OuterRef("pk"))
                        .values("group")
                        .order_by("group")
                        .annotate(
                            total=Sum("cost"),
                        )
                        .values("total")[:1]
                    ),
                    0,
                    output_field=DecimalField(),
                ),
                total_paid=Coalesce(
                    Subquery(
                        InvoiceItemTransaction.objects.filter(item__group=OuterRef("pk"))
                        .values("item__group")
                        .order_by("item__group")
                        .annotate(
                            total_paid=Sum("amount"),
                        )
                        .values("total_paid")[:1]
                    ),
                    0,
                    output_field=DecimalField(),
                ),
                current_balance=Coalesce(
                    F("total") - F("total_paid"), 0, output_field=DecimalField()
                ),
            )
        )


class InvoiceItemGroup(models.Model):
    ANY_CATEGORY = ""
    APPEALS_FEE_CATEGORY = "appeals_fees"
    CATEGORY_CHOICES = (
        (ANY_CATEGORY, "Any"),
        (APPEALS_FEE_CATEGORY, "Appeals Fees"),
    )

    id = HashidAutoField(
        primary_key=True, salt=f"invoicing.InvoiceItemGroup{settings.HASHID_FIELD_SALT}"
    )
    created_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        related_name="%(app_label)s_invoice_item_groups",
        on_delete=models.CASCADE,
        help_text="If None this means that Invoice Item Group has been created automatically",
    )

    invoice = models.ForeignKey("Invoice", null=True, blank=True, on_delete=models.SET_NULL)
    home_status = models.ForeignKey(
        "home.EEPProgramHomeStatus", null=True, blank=True, on_delete=models.SET_NULL
    )
    category = models.CharField(
        max_length=255, choices=CATEGORY_CHOICES, default=ANY_CATEGORY, blank=True
    )

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = InvoiceItemGroupManager()
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Invoice Group"
        ordering = [
            "-updated_at",
        ]

    def __str__(self):
        return f"Invoice Item Group ID: {self.id} Home Status ID: {self.home_status_id}"


class InvoiceItemQuerySet(models.QuerySet):
    @queryset_user_is_authenticated
    def filter_by_user(self, user):
        return self


class InvoiceItemManager(models.Manager.from_queryset(InvoiceItemQuerySet)):
    def get_queryset(self):
        # https://stackoverflow.com/a/45803258/1786016
        return (
            super(InvoiceItemManager, self)
            .get_queryset()
            .annotate(
                total_paid=Coalesce(
                    Subquery(
                        InvoiceItemTransaction.objects.filter(item=OuterRef("pk"))
                        .values("item")
                        .order_by("item")
                        .annotate(
                            total_paid=Sum("amount"),
                        )
                        .values("total_paid")[:1]
                    ),
                    0,
                    output_field=DecimalField(),
                ),
                current_balance=Coalesce(
                    F("cost") - F("total_paid"), 0, output_field=DecimalField()
                ),
            )
        )


class InvoiceItem(models.Model):
    id = HashidAutoField(
        primary_key=True, salt=f"invoicing.InvoiceItem{settings.HASHID_FIELD_SALT}"
    )
    group = models.ForeignKey("InvoiceItemGroup", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    cost = models.DecimalField(default=0.00, max_digits=9, decimal_places=2)
    protected = models.BooleanField(
        default=False, help_text="Item can not be edited by User after creation"
    )

    created_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        related_name="%(app_label)s_invoice_items",
        on_delete=models.CASCADE,
        help_text="If None this means that Invoice Item has been created automatically",
    )

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = InvoiceItemManager()
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Invoice Item"
        ordering = [
            "-updated_at",
        ]

    def __str__(self):
        return f"{self.name} {self.cost}"

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super(InvoiceItem, self).save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )

        invoice_item_group = getattr(self, "group", None)
        home_status = None
        hirl_project = None
        company_responsible_for_payment = None

        if invoice_item_group:
            home_status = getattr(invoice_item_group, "home_status", None)
            if home_status:
                hirl_project = getattr(home_status, "customer_hirl_project", None)
                if hirl_project:
                    registration = hirl_project.registration
                    try:
                        company_responsible_for_payment = (
                            registration.get_company_responsible_for_payment()
                        )
                    except ObjectDoesNotExist:
                        pass

        if hirl_project:
            # do not trigger any signals for HIRLProject
            from axis.customer_hirl.models import HIRLProject

            HIRLProject.objects.filter(id=hirl_project.id).select_for_update().update(
                most_recent_notice_sent=timezone.now()
            )

            # ignore protected items.
            # Most of protected Items created programmatically
            # and have own notifications
            if not self.protected:
                message_context = {
                    "url": f"{home_status.home.get_absolute_url()}#/tabs/invoicing",
                    "home_url": f"{home_status.home.get_absolute_url()}" f"#/tabs/invoicing",
                    "home_address": home_status.home,
                    "invoice_item_groups_url": "/app/hi/invoice_item_groups/",
                }

                if company_responsible_for_payment:
                    HIRLInvoiceItemGroupUpdatedMessage(
                        url=f"{home_status.home.get_absolute_url()}#/tabs/invoicing"
                    ).send(
                        company=company_responsible_for_payment,
                        context=message_context,
                    )

                hirl_company = customer_hirl_app.get_customer_hirl_provider_organization()
                company_admins = hirl_company.users.filter(is_company_admin=True)

                if company_admins:
                    HIRLInvoiceItemGroupUpdatedMessage(
                        url=f"{home_status.home.get_absolute_url()}#/tabs/invoicing"
                    ).send(
                        users=company_admins,
                        context=message_context,
                    )


class InvoiceItemTransaction(models.Model):
    """
    Adding support for partially paid Invoices
    """

    id = HashidAutoField(
        primary_key=True, salt=f"invoicing.InvoiceItemTransaction{settings.HASHID_FIELD_SALT}"
    )
    item = models.ForeignKey(
        "InvoiceItem", related_name="transactions", null=True, on_delete=models.SET_NULL
    )
    amount = models.DecimalField(default=0.00, max_digits=9, decimal_places=2)
    note = models.TextField(blank=True)
    created_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        related_name="%(app_label)s_invoice_item_transactions",
        on_delete=models.CASCADE,
        help_text="If None this means that Invoice Transaction has been created automatically",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Invoice Item Transaction"
        ordering = [
            "-created_at",
        ]

    def __str__(self):
        return f"Transaction for Item({self.item}) - Amount: {self.amount}"
