"""admin.py: """

__author__ = "Artem Hruzd"
__date__ = "03/03/2021 17:12"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.contrib import admin
from django.contrib.admin.decorators import register
from django.urls import reverse
from django.utils.html import format_html

from axis.invoicing.models import InvoiceItem, Invoice, InvoiceItemGroup, InvoiceItemTransaction


class InvoiceItemTabularInline(admin.TabularInline):
    model = InvoiceItem
    extra = 0
    raw_id_fields = ("created_by",)


@register(InvoiceItemTransaction)
class InvoiceItemTransactionAdmin(admin.ModelAdmin):
    search_fields = (
        "id",
        "item__name",
        "item__group__home_status__id",
        "item__group__home_status__customer_hirl_project__id",
        "item__group__invoice__id",
    )
    list_display = ("id", "amount", "note", "created_at", "created_by")
    raw_id_fields = (
        "item",
        "created_by",
    )


@register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    search_fields = (
        "id",
        "name",
        "group__home_status__id",
        "group__home_status__customer_hirl_project__id",
        "group__invoice__id",
    )
    list_filter = ("protected",)
    list_display = ("id", "name", "cost", "protected", "group", "updated_at")
    raw_id_fields = (
        "group",
        "created_by",
    )


@register(InvoiceItemGroup)
class InvoiceItemGroupAdmin(admin.ModelAdmin):
    search_fields = (
        "id",
        "created_by__first_name",
        "created_by__last_name",
        "home_status__eep_program__name",
        "home_status__id",
        "home_status__customer_hirl_project__id",
        "category",
    )
    list_display = ("id", "invoice", "home_status", "category")
    raw_id_fields = (
        "home_status",
        "created_by",
        "invoice",
    )
    inlines = (InvoiceItemTabularInline,)


class InvoiceItemGroupTabularInline(admin.TabularInline):
    model = InvoiceItemGroup
    extra = 0
    readonly_fields = ("get_total", "edit_link")
    raw_id_fields = (
        "created_by",
        "home_status",
    )

    def get_total(self, instance):
        return instance.total

    def edit_link(self, instance):
        url = reverse(
            "admin:%s_%s_change" % (instance._meta.app_label, instance._meta.model_name),
            args=(instance.id,),
        )
        return format_html(f'<a href="{url}">Edit</a>')


@register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    search_fields = (
        "id",
        "issuer__name",
        "customer__name",
        "created_by__first_name",
        "created_by__last_name",
        "invoiceitemgroup__home_status__id",
        "invoiceitemgroup__home_status__customer_hirl_project__id",
    )
    list_display = ("id", "state", "issuer", "customer", "total", "get_current_balance")
    list_select_related = (
        "issuer",
        "customer",
    )
    raw_id_fields = ("created_by", "issuer", "customer")
    readonly_fields = ("total", "total_paid")
    inlines = (InvoiceItemGroupTabularInline,)

    def get_current_balance(self, obj):
        return obj.current_balance
