"""invoice_item_group_machinery.py: """

__author__ = "Artem Hruzd"
__date__ = "03/09/2021 18:43"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

import pytz
from django.db.models import Sum, DecimalField
from django.db.models.functions import Coalesce

from axis.customer_hirl.models import HIRLProject
from axis.examine import PanelMachinery
from axis.home.api import HIRLInvoiceItemGroupViewSet, HomeStatusViewSet
from axis.home.forms import HIRLInvoiceItemGroupForm, HomeStatusForm
from .invoice_item import HIRLInvoiceItemExamineMachinery
from axis.invoicing.models import InvoiceItemGroup, InvoiceItem, InvoiceItemTransaction
from axis.home.models import EEPProgramHomeStatus


class InvoiceHomeStatusExamineMachinery(PanelMachinery):
    """Home Status Machinery"""

    model = EEPProgramHomeStatus
    form_class = HomeStatusForm
    type_name = "invoice_home_status"
    api_provider = HomeStatusViewSet

    template_set = "accordion"
    region_template = "examine/home/invoice_homestatus_region.html"
    detail_template = "examine/home/invoice_homestatus_detail.html"
    form_template = "examine/home/invoice_homestatus_form.html"

    can_add_new = False

    def get_form_kwargs(self, instance):
        return {
            "user": self.context["request"].user,
        }

    def get_object_name(self, instance):
        if instance.pk:
            return instance.eep_program.name
        return super(InvoiceHomeStatusExamineMachinery, self).get_object_name(instance)

    def can_edit_object(self, instance, user=None):
        return False

    def can_delete_object(self, instance, user=None):
        return False

    def get_helpers(self, instance):
        helpers = super(InvoiceHomeStatusExamineMachinery, self).get_helpers(instance)
        protected_total_fees = InvoiceItem.objects.filter(
            group__home_status=instance, protected=True
        ).aggregate(total_fees=Coalesce(Sum("cost"), 0, output_field=DecimalField()))["total_fees"]

        hirl_project = (
            HIRLProject.objects.filter(id=instance.customer_hirl_project.id)
            .annotate_billing_info()
            .first()
        )

        helpers["total_fees"] = protected_total_fees
        helpers["total_fees_charged"] = hirl_project.fee_total
        helpers["balance_owed"] = hirl_project.fee_current_balance

        helpers["customer_hirl_project_id"] = hirl_project.id
        helpers["h_number"] = hirl_project.h_number
        helpers["jamis_milestoned"] = hirl_project.is_jamis_milestoned
        helpers[
            "hirlcompanyclient_id"
        ] = hirl_project.registration.get_project_client_company().hirlcompanyclient.id
        helpers[
            "hirlcompanyinvoicee_id"
        ] = hirl_project.registration.get_company_responsible_for_payment().hirlcompanyclient.id
        helpers["billing_state"] = hirl_project.billing_state

        most_recent_payment_received = hirl_project.most_recent_payment_received
        if most_recent_payment_received:
            most_recent_payment_received = hirl_project.most_recent_payment_received.astimezone(
                pytz.timezone("US/Eastern")
            )
            most_recent_payment_received = most_recent_payment_received.strftime("%m/%d/%Y")
        helpers["most_recent_payment_received"] = most_recent_payment_received
        helpers["most_recent_notice_sent"] = hirl_project.most_recent_notice_sent
        helpers["initial_invoice_date"] = hirl_project.initial_invoice_date
        helpers["certification_date"] = instance.certification_date

        return helpers


class HIRLInvoiceItemGroupExamineMachinery(PanelMachinery):
    model = InvoiceItemGroup
    form_class = HIRLInvoiceItemGroupForm
    api_provider = HIRLInvoiceItemGroupViewSet
    type_name = "hirl_invoice_item_group"

    regionset_template = "examine/home/hirl_invoice_item_group_regionset.html"
    region_template = "examine/home/hirl_invoice_item_group_region.html"
    detail_template = "examine/home/hirl_invoice_item_group_detail.html"

    def get_region_dependencies(self):
        return {
            "home_status": [
                {
                    "field_name": "id",
                    "serialize_as": "home_status",
                }
            ],
        }

    def get_new_region_endpoint(self):
        user = self.context["request"].user
        new_endpoint = super(HIRLInvoiceItemGroupExamineMachinery, self).get_new_region_endpoint()

        if not user or not user.is_authenticated:
            return None

        if user.is_superuser:
            return new_endpoint

        if not user.is_customer_hirl_company_admin_member():
            return None

        return new_endpoint

    def can_edit_object(self, instance, user=None):
        return False

    def can_delete_object(self, instance, user=None):
        return False

    def get_helpers(self, instance):
        helpers = super(HIRLInvoiceItemGroupExamineMachinery, self).get_helpers(instance)

        helpers["machinery"] = {}

        has_invoice = getattr(self.instance, "invoice", None)
        objects = []
        if instance.pk:
            objects = instance.invoiceitem_set.all()
        invoice_item_group_machinery = HIRLInvoiceItemExamineMachinery(
            objects=objects, context={"request": self.context["request"]}
        )
        invoice_item_group_machinery.can_add_new = not has_invoice

        helpers["machinery"]["invoice_item_machinery"] = invoice_item_group_machinery.get_summary()
        return helpers
