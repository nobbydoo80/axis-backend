"""client_agreement.py: """

__author__ = "Artem Hruzd"
__date__ = "10/10/2021 11:44 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.apps import apps
from rest_framework import serializers

from axis.company.api_v3.serializers import CompanyInfoSerializer
from axis.company.models import Company
from axis.core.api_v3.serializers import UserInfoSerializer
from axis.customer_hirl.models import BuilderAgreement
from axis.filehandling.api_v3.serializers import CustomerDocumentInfoSerializer
from axis.geocoder.api_v3.serializers import (
    GeocodeInfoSerializer,
    GeocodeBrokeredResponseSerializer,
)
from axis.geocoder.models import Geocode

customer_hirl_app = apps.get_app_config("customer_hirl")


class ClientAgreementDocusignInfoSerializer(serializers.Serializer):
    """
    Nested serializer to represent useful Dosign information from Dosucisign response
    """

    envelope_id = serializers.CharField(read_only=True)
    status = serializers.SerializerMethodField()
    status_message = serializers.SerializerMethodField()
    recipient_email = serializers.SerializerMethodField()
    delivered_time = serializers.SerializerMethodField()

    def get_status(self, data: dict | None):
        if not data or not data.get("latest_result"):
            return None
        return data.get("latest_result", {}).get("status")

    def get_status_message(self, data: dict | None):
        if not data or not data.get("latest_result"):
            return None
        return data.get("latest_result", {}).get("status_message")

    def get_recipient_email(self, data: dict | None):
        if not data or not data.get("latest_result"):
            return None

        email = None
        recipient_form_data = (
            data.get("latest_result", {}).get("source", {}).get("recipientFormData", [])
        )
        if recipient_form_data:
            email = recipient_form_data[0].get("email")
        return email

    def get_delivered_time(self, data: dict | None):
        if not data or not data.get("latest_result"):
            return None

        delivered_time = None
        recipient_form_data = (
            data.get("latest_result", {}).get("source", {}).get("recipientFormData", [])
        )
        if recipient_form_data:
            delivered_time = recipient_form_data[0].get("deliveredTime")
        return delivered_time


class ClientAgreementSerializer(serializers.ModelSerializer):
    company_info = CompanyInfoSerializer(source="company", read_only=True)
    owner_info = CompanyInfoSerializer(source="owner", read_only=True)
    created_by_info = UserInfoSerializer(source="created_by", read_only=True)
    initiator_info = UserInfoSerializer(source="initiator", read_only=True)
    ca_version_to_sign = serializers.ReadOnlyField(source="get_ca_version_to_sign")
    mailing_geocode_info = GeocodeInfoSerializer(source="mailing_geocode", read_only=True)
    mailing_geocode_response_info = GeocodeBrokeredResponseSerializer(
        source="mailing_geocode_response", read_only=True
    )

    shipping_geocode_info = GeocodeInfoSerializer(source="shipping_geocode", read_only=True)
    shipping_geocode_response_info = GeocodeBrokeredResponseSerializer(
        source="shipping_geocode_response", read_only=True
    )
    signed_agreement_info = CustomerDocumentInfoSerializer(
        source="signed_agreement", read_only=True
    )
    certifying_document_info = CustomerDocumentInfoSerializer(
        source="certifying_document", read_only=True
    )
    extension_request_signed_agreement_info = CustomerDocumentInfoSerializer(
        source="extension_request_signed_agreement", read_only=True
    )
    extension_request_certifying_document_info = CustomerDocumentInfoSerializer(
        source="extension_request_certifying_document", read_only=True
    )
    docusign_data = ClientAgreementDocusignInfoSerializer(source="data", read_only=True)

    class Meta:
        model = BuilderAgreement
        fields = (
            "id",
            "company",
            "company_info",
            "owner",
            "owner_info",
            "state",
            "signer_email",
            "signer_name",
            "mailing_geocode",
            "created_by",
            "created_by_info",
            "initiator",
            "initiator_info",
            "date_modified",
            "date_created",
            "website",
            "use_payment_contact_in_ngbs_green_projects",
            "agreement_start_date",
            "agreement_expiration_date",
            "primary_contact_first_name",
            "primary_contact_last_name",
            "primary_contact_title",
            "primary_contact_email_address",
            "primary_contact_phone_number",
            "primary_contact_cell_number",
            "secondary_contact_first_name",
            "secondary_contact_last_name",
            "secondary_contact_title",
            "secondary_contact_email_address",
            "secondary_contact_phone_number",
            "secondary_contact_cell_number",
            "payment_contact_first_name",
            "payment_contact_last_name",
            "payment_contact_title",
            "payment_contact_phone_number",
            "payment_contact_cell_number",
            "payment_contact_email_address",
            "marketing_contact_first_name",
            "marketing_contact_last_name",
            "marketing_contact_title",
            "marketing_contact_phone_number",
            "marketing_contact_cell_number",
            "marketing_contact_email_address",
            "website_contact_first_name",
            "website_contact_last_name",
            "website_contact_title",
            "website_contact_phone_number",
            "website_contact_cell_number",
            "website_contact_email_address",
            # address fields
            "mailing_geocode_info",
            "mailing_geocode_response_info",
            "shipping_geocode_info",
            "shipping_geocode_response_info",
            "mailing_geocode",
            "mailing_geocode_response",
            "shipping_geocode",
            "shipping_geocode_response",
            # files
            "signed_agreement_info",
            "signed_agreement",
            "certifying_document_info",
            "certifying_document",
            # extension request
            "extension_request_state",
            "extension_request_signed_agreement",
            "extension_request_signed_agreement_info",
            "extension_request_certifying_document",
            "extension_request_certifying_document_info",
            "extension_request_reject_reason",
            # computed fields
            "ca_version_to_sign",
            "docusign_data",
        )
        read_only_fields = ("state", "company", "owner")


class CreateClientAgreementWithoutDocuSignSerializer(serializers.ModelSerializer):
    company = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all())

    class Meta:
        model = BuilderAgreement
        fields = ("company",)

    def validate(self, attrs):
        company = attrs["company"]

        agreement_exists = company.customer_hirl_enrolled_agreements.exclude(
            state=BuilderAgreement.EXPIRED
        ).exists()

        if agreement_exists:
            raise serializers.ValidationError(
                {"company": f"{company} already have active Client Agreement"}
            )

        return attrs

    def save(self, **kwargs):
        kwargs["state"] = BuilderAgreement.COUNTERSIGNED
        return super(CreateClientAgreementWithoutDocuSignSerializer, self).save(**kwargs)


class CreateClientAgreementWithoutUserSerializer(serializers.Serializer):
    company = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all())
    signer_email = serializers.EmailField()
    signer_name = serializers.CharField(max_length=100)
    mailing_geocode = serializers.PrimaryKeyRelatedField(queryset=Geocode.objects.all())

    def validate(self, attrs):
        company = attrs["company"]

        agreement_exists = company.customer_hirl_enrolled_agreements.exclude(
            state=BuilderAgreement.EXPIRED
        ).exists()

        if agreement_exists:
            raise serializers.ValidationError(
                {"company": f"{company}  already has an active Client Agreement.  No action taken"}
            )

        return attrs

    def create(self, validated_data):
        client_agreement = BuilderAgreement.objects.create(
            owner=customer_hirl_app.get_customer_hirl_provider_organization(),
            company=validated_data["company"],
            signer_email=validated_data["signer_email"],
            signer_name=validated_data["signer_name"],
            mailing_geocode=validated_data["mailing_geocode"],
            state=BuilderAgreement.NEW,
            initiator=self.context["request"].user,
            created_by=self.context["request"].user,
        )
        return client_agreement

    def update(self, instance, validated_data):
        raise NotImplementedError


class ClientAgreementForceStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BuilderAgreement
        fields = ("state",)
