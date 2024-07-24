"""serializer.py: """

__author__ = "Artem Hruzd"
__date__ = "03/03/2021 22:02"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
    "Naruhito Kaide",
]

from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.utils import timezone
from hashid_field.rest import HashidSerializerCharField
from rest_framework import serializers
from django.conf import settings

from axis.core.api_v3.serializers import UserInfoSerializer
from axis.customer_hirl.api_v3.serializer_fields import HIRLProjectAddressDisplayField
from axis.customer_hirl.models import BuilderAgreement

from axis.home.api_v3.serializers import EEPProgramHomeStatusInfoSerializer
from axis.invoicing.models import Invoice, InvoiceItemGroup
from axis.company.api_v3.serializers import CompanyInfoSerializer

customer_hirl_app = apps.get_app_config("customer_hirl")


class InvoiceMeta:
    model = Invoice
    fields = (
        "id",
        "state",
        "note",
        "invoice_type",
        "customer",
        "customer_info",
        "issuer",
        "issuer_info",
        "total",
        "total_paid",
        "current_balance",
        "created_by",
        "created_by_info",
        "updated_at",
        "created_at",
    )
    read_only_fields = (
        "created_by",
        "invoice_type",
        "updated_at",
        "created_at",
        "total",
        "total_paid",
    )


class InvoiceSerializerMixin(metaclass=serializers.SerializerMetaclass):
    id = HashidSerializerCharField(source_field="invoicing.Invoice.id", read_only=True)

    customer_info = CompanyInfoSerializer(source="customer", read_only=True)
    issuer_info = CompanyInfoSerializer(source="issuer", read_only=True)
    created_by_info = UserInfoSerializer(source="created_by", read_only=True)

    current_balance = serializers.SerializerMethodField()

    def get_current_balance(self, invoice):
        return invoice.current_balance


class BasicInvoiceSerializer(InvoiceSerializerMixin, serializers.ModelSerializer):
    """Basic control of Invoice instance."""

    class Meta(InvoiceMeta):
        read_only_fields = InvoiceMeta.read_only_fields + ("state",)


class InvoiceSerializer(InvoiceSerializerMixin, serializers.ModelSerializer):
    """Allows full control of Invoice instance."""

    class Meta(InvoiceMeta):
        pass


class InvoiceAggregateByStateSerializer(serializers.Serializer):
    new = serializers.IntegerField(default=0)
    paid = serializers.IntegerField(default=0)
    cancelled = serializers.IntegerField(default=0)

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError


class InvoiceItemGroupMeta:
    model = InvoiceItemGroup
    fields = (
        "id",
        "invoice",
        "home_status",
        "home_status_info",
        "total",
        "updated_at",
        "created_at",
    )
    read_only_fields = ("created_at", "updated_at")


class InvoiceItemGroupSerializerMixin(metaclass=serializers.SerializerMetaclass):
    id = HashidSerializerCharField(source_field="invoicing.InvoiceItemGroup.id", read_only=True)
    invoice = serializers.PrimaryKeyRelatedField(
        pk_field=HashidSerializerCharField(source_field="invoicing.Invoice.id"),
        queryset=Invoice.objects.all(),
    )

    home_status_info = EEPProgramHomeStatusInfoSerializer(source="home_status")
    total = serializers.SerializerMethodField()

    def get_total(self, invoice_item_group):
        return invoice_item_group.total


class BasicInvoiceItemGroupSerializer(InvoiceItemGroupSerializerMixin, serializers.ModelSerializer):
    """Basic control of InvoiceItemGroup instance."""

    class Meta(InvoiceItemGroupMeta):
        read_only_fields = InvoiceMeta.read_only_fields + ("state",)


class InvoiceItemGroupSerializer(InvoiceItemGroupSerializerMixin, serializers.ModelSerializer):
    """Allows full control of InvoiceItemGroup instance."""

    class Meta(InvoiceItemGroupMeta):
        pass


class HIRLCreateInvoiceDataSerializer(serializers.Serializer):
    invoice_item_groups = serializers.PrimaryKeyRelatedField(
        pk_field=HashidSerializerCharField(
            salt=f"invoicing.InvoiceItemGroup{settings.HASHID_FIELD_SALT}",
            alphabet=settings.HASHID_FIELD_ALPHABET,
        ),
        queryset=InvoiceItemGroup.objects.all(),
        many=True,
    )
    note = serializers.CharField(required=False, allow_blank=True)

    def validate_invoice_item_groups(self, invoice_item_groups):
        if not invoice_item_groups:
            raise serializers.ValidationError(
                "Specify at least one Invoice Item Group to create Invoice"
            )

        unique_entity_responsible_for_payment = None

        for invoice_item_group in invoice_item_groups:
            if invoice_item_group.current_balance == 0:
                raise serializers.ValidationError("You cannot create invoice with 0 balance items")
            hirl_project = invoice_item_group.home_status.customer_hirl_project
            try:
                entity_responsible_for_payment = (
                    hirl_project.registration.get_company_responsible_for_payment()
                )
            except ObjectDoesNotExist:
                raise serializers.ValidationError(
                    f"Project {hirl_project.id} do not have Entity Responsible For Payment"
                )

            if (
                unique_entity_responsible_for_payment
                and unique_entity_responsible_for_payment != entity_responsible_for_payment
            ):
                raise serializers.ValidationError(
                    "Projects must contain same Entity Responsible for payment"
                )
            else:
                unique_entity_responsible_for_payment = entity_responsible_for_payment

            try:
                project_client = hirl_project.registration.get_project_client_company()
            except ObjectDoesNotExist:
                raise serializers.ValidationError(
                    f"Project {hirl_project.id} do not have Client Company"
                )

            countersigned_ca_exists = project_client.customer_hirl_enrolled_agreements.filter(
                state=BuilderAgreement.COUNTERSIGNED
            ).exists()

            if not countersigned_ca_exists:
                raise serializers.ValidationError(
                    f"Client Company {project_client} for Project {hirl_project.id} "
                    f"does not have a Countersigned Client Agreement"
                )

        return invoice_item_groups

    def create(self, validated_data):
        invoice_item_groups = validated_data["invoice_item_groups"]
        note = validated_data.get("note", "")
        customer_hirl_project = invoice_item_groups[0].home_status.customer_hirl_project
        company_responsible_for_payment = (
            customer_hirl_project.registration.get_company_responsible_for_payment()
        )

        with transaction.atomic():
            invoice = Invoice.objects.create(
                invoice_type=Invoice.HIRL_PROJECT_INVOICE_TYPE,
                issuer=customer_hirl_app.get_customer_hirl_provider_organization(),
                customer=company_responsible_for_payment,
                note=note,
                created_by=self.context["request"].user,
            )
            for invoice_item_group in invoice_item_groups:
                invoice_item_group.invoice = invoice
                invoice_item_group.save()

        # reload invoice to update all annotations
        invoice = Invoice.objects.get(pk=invoice.pk)

        return invoice

    def update(self, instance, validated_data):
        raise NotImplementedError


class CustomerHIRLInvoiceManagementListSerializer(
    InvoiceItemGroupSerializerMixin, serializers.ModelSerializer
):
    home_status_state = serializers.ReadOnlyField(source="home_status.state")
    hirl_project_address = HIRLProjectAddressDisplayField(
        source="home_status.customer_hirl_project"
    )
    home_id = serializers.ReadOnlyField(source="home_status.home.id")
    hirl_project_id = serializers.ReadOnlyField(source="home_status.customer_hirl_project.id")
    hirl_project_registration_id = serializers.ReadOnlyField(
        source="home_status.customer_hirl_project.registration.id"
    )
    eep_program_id = serializers.ReadOnlyField(source="home_status.eep_program.id")
    eep_program_name = serializers.ReadOnlyField(source="home_status.eep_program.name")
    client_ca_status = serializers.ReadOnlyField()
    client = serializers.SerializerMethodField()

    class Meta(InvoiceItemGroupMeta):
        fields = (
            "id",
            "home_status",
            "home_status_state",
            "home_id",
            "eep_program_id",
            "eep_program_name",
            "hirl_project_id",
            "hirl_project_registration_id",
            "hirl_project_address",
            "client",
            "total",
            "client_ca_status",
            "created_at",
        )
        read_only_fields = InvoiceItemGroupMeta.read_only_fields

    def get_client(self, invoice_item_group):
        client = None
        home_status = getattr(invoice_item_group, "home_status", None)
        if home_status:
            customer_hirl_project = getattr(home_status, "customer_hirl_project", None)
            if customer_hirl_project:
                client = customer_hirl_project.registration.get_project_client_company()
        return CompanyInfoSerializer(instance=client).data


class CustomerHIRLInvoiceSerializer(serializers.ModelSerializer):
    id = HashidSerializerCharField(source_field="invoicing.Invoice.id", read_only=True)
    customer_id = serializers.ReadOnlyField(source="customer.id")
    customer_type = serializers.ReadOnlyField(source="customer.company_type")
    customer_name = serializers.SerializerMethodField()
    client_id = serializers.SerializerMethodField()
    client_type = serializers.SerializerMethodField()
    client_name = serializers.SerializerMethodField()
    current_balance = serializers.SerializerMethodField()
    h_numbers = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = (
            "id",
            "customer_id",
            "customer_type",
            "customer_name",
            "client_id",
            "client_type",
            "client_name",
            "total",
            "total_paid",
            "h_numbers",
            "current_balance",
            "created_at",
        )

    def get_customer_name(self, invoice):
        customer = getattr(invoice, "customer", None)
        if not customer:
            return ""
        hirl_company_client = getattr(customer, "hirlcompanyclient", None)
        if not hirl_company_client:
            return ""
        return f"{invoice.customer.name} (NGBS ID: {hirl_company_client.id})"

    def get_client_company(self, invoice):
        invoice_item_group = invoice.invoiceitemgroup_set
        invoice_item = invoice_item_group.first()
        if not invoice_item:
            return ""
        hirl_project = invoice_item.home_status.customer_hirl_project
        client_company = hirl_project.registration.get_project_client_company()
        return client_company

    def get_client_type(self, invoice):
        client_company = self.get_client_company(invoice)
        if not client_company:
            return ""
        return client_company.company_type

    def get_client_id(self, invoice):
        client_company = self.get_client_company(invoice)
        if not client_company:
            return ""
        return client_company.id

    def get_client_name(self, invoice):
        client_company = self.get_client_company(invoice)
        if not client_company:
            return ""
        hirl_company_client = getattr(client_company, "hirlcompanyclient", None)
        if not hirl_company_client:
            return ""
        return f"{client_company.name} (NGBS ID: {hirl_company_client.id})"

    def get_current_balance(self, invoice):
        return invoice.current_balance

    def get_h_numbers(self, invoice):
        return invoice.invoiceitemgroup_set.values_list(
            "home_status__customer_hirl_project__h_number", flat=True
        )
