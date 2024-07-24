"""invoice_item.py: """

__author__ = "Artem Hruzd"
__date__ = "03/09/2021 18:43"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from axis.examine import PanelMachinery, TableMachinery
from axis.home.api import HIRLInvoiceItemViewSet
from axis.home.forms import HIRLInvoiceItemForm
from axis.invoicing.models import InvoiceItem


class HIRLInvoiceItemExamineMachinery(TableMachinery):
    model = InvoiceItem
    form_class = HIRLInvoiceItemForm
    api_provider = HIRLInvoiceItemViewSet
    type_name = "hirl_invoice_item"
    can_add_new = False

    regionset_template = "examine/home/hirl_invoice_item_regionset_table.html"
    region_template = "examine/home/hirl_invoice_item_region_tablerow.html"
    detail_template = "examine/home/hirl_invoice_item_detail_tablerow.html"

    def get_region_dependencies(self):
        return {
            "group": [
                {
                    "field_name": "id",
                    "serialize_as": "group",
                }
            ],
        }

    def get_new_region_endpoint(self):
        user = self.context["request"].user
        new_endpoint = super(HIRLInvoiceItemExamineMachinery, self).get_new_region_endpoint()

        if not user or not user.is_authenticated:
            return None

        if user.is_superuser:
            return new_endpoint

        if not user.is_customer_hirl_company_admin_member():
            return None

        return new_endpoint

    def can_edit_object(self, instance, user=None):
        if not user or not user.is_authenticated:
            return False

        if not user.is_customer_hirl_company_member():
            return False

        if instance.protected:
            return False
        has_invoice = getattr(instance, "group", None) and getattr(instance.group, "invoice", None)
        return not has_invoice

    def can_delete_object(self, instance, user=None):
        if not user or not user.is_authenticated:
            return False

        if not user.is_customer_hirl_company_member():
            return False

        if instance.protected:
            return False
        has_invoice = getattr(instance, "group", None) and getattr(instance.group, "invoice", None)
        return not has_invoice
