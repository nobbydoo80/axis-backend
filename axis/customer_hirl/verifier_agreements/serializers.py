"""serializers.py: """

__author__ = "Artem Hruzd"
__date__ = "04/16/2020 17:07"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.apps import apps
from django.core.exceptions import ValidationError
from django.urls import reverse
from rest_framework import serializers

from axis.core.utils import make_safe_field
from axis.customer_hirl.models import VerifierAgreement, COIDocument
from axis.geographic.models import City
from . import MANAGEMENT_FIELDS, MANAGEMENT_LABELS, ENROLLMENT_LABELS, ENROLLMENT_FIELDS
from .messages.owner import NewVerifierAgreementEnrollmentMessage
from axis.geocoder.api_v3.serializers import GeocodeMatchesSerializer

app = apps.get_app_config("customer_hirl")


# Existing VerifierAgreement management
class VerifierAgreementManagementSerializer(serializers.ModelSerializer):
    """Owner serializer for BuilderAgreement model."""

    company_display = serializers.SerializerMethodField()
    company_url = serializers.ReadOnlyField(source="verifier.company.get_absolute_url")
    verifier_name_display = serializers.ReadOnlyField(source="verifier.get_full_name")
    verifier_company_cois = serializers.SerializerMethodField()
    state_display = serializers.CharField(
        source="get_state_display", label="Status", read_only=True
    )
    va_version_to_sign = serializers.ReadOnlyField(source="get_va_version_to_sign")

    class Meta:
        model = VerifierAgreement
        fields = MANAGEMENT_FIELDS + (
            "id",
            "state",
            "owner",
            "state_display",
            "company_display",
            "verifier_name_display",
            "verifier_company_cois",
            "company_url",
            "va_version_to_sign",
        )
        read_only_fields = ("state", "owner")
        labels = MANAGEMENT_LABELS

    def get_verifier_company_cois(self, instance):
        return COIDocumentSerializer(
            instance.verifier.company.coi_documents.active(), many=True
        ).data

    def get_company_display(self, instance=None):
        """Return enrollee display string."""
        company = self.context["request"].user.company
        if self.instance and self.instance.pk:
            company = self.instance.verifier.company

        return f"<a href='{company.get_absolute_url()}'>{company}</a>"


# New or existing VerifierAgreement
class VerifierAgreementEnrollmentSerializer(serializers.ModelSerializer):
    """Enrollee serializer for VerifierAgreement model."""

    company_display = serializers.SerializerMethodField()
    verifier_name_display = serializers.SerializerMethodField()
    verifier_company_url = serializers.SerializerMethodField()
    state_display = serializers.CharField(
        source="get_state_display", label="Status", read_only=True
    )

    applicant_first_name = serializers.CharField(max_length=30, label="First Name", required=True)
    applicant_last_name = serializers.CharField(max_length=30, label="Last Name", required=True)
    applicant_title = serializers.CharField(max_length=100, label="Title", required=True)
    applicant_phone_number = serializers.CharField(
        max_length=30, label="Phone Number", required=True
    )
    applicant_email = serializers.CharField(max_length=30, label="Email", required=True)

    mailing_geocode_street_line1 = serializers.CharField(
        source="mailing_geocode.raw_street_line1", max_length=100, allow_null=True
    )
    mailing_geocode_street_line2 = serializers.CharField(
        source="mailing_geocode.raw_street_line2", max_length=100, allow_blank=True, allow_null=True
    )
    mailing_geocode_zipcode = serializers.CharField(
        source="mailing_geocode.raw_zipcode", max_length=15, allow_null=True
    )
    mailing_geocode_city = serializers.PrimaryKeyRelatedField(
        source="mailing_geocode.raw_city",
        required=True,
        queryset=City.objects.all(),
        allow_null=True,
    )
    mailing_geocode_city_display = serializers.ReadOnlyField(source="mailing_geocode.raw_city.name")

    shipping_geocode_street_line1 = serializers.CharField(
        source="shipping_geocode.raw_street_line1", max_length=100, required=False, allow_blank=True
    )
    shipping_geocode_street_line2 = serializers.CharField(
        source="shipping_geocode.raw_street_line2", max_length=100, required=False, allow_blank=True
    )
    shipping_geocode_zipcode = serializers.CharField(
        source="shipping_geocode.raw_zipcode", max_length=15, required=False, allow_blank=True
    )
    shipping_geocode_city = serializers.PrimaryKeyRelatedField(
        source="shipping_geocode.raw_city",
        required=False,
        allow_null=True,
        queryset=City.objects.all(),
    )
    shipping_geocode_city_display = serializers.ReadOnlyField(
        source="shipping_geocode.raw_city.name"
    )

    company_with_multiple_verifiers = serializers.BooleanField(write_only=True)

    company_url = serializers.ReadOnlyField(source="verifier.company.get_absolute_url")
    us_states_display = serializers.SerializerMethodField()
    provided_services_display = serializers.SerializerMethodField()
    verifier_company_cois = serializers.SerializerMethodField()

    class Meta:
        model = VerifierAgreement
        fields = ENROLLMENT_FIELDS + (
            "id",
            "state",
            "verifier",
            "state_display",
            "company_display",
            "verifier_name_display",
            "verifier_company_url",
            "mailing_geocode_street_line1",
            "mailing_geocode_street_line2",
            "mailing_geocode_zipcode",
            "mailing_geocode_city",
            "mailing_geocode_city_display",
            "shipping_geocode_street_line1",
            "shipping_geocode_street_line2",
            "shipping_geocode_zipcode",
            "shipping_geocode_city",
            "shipping_geocode_city_display",
            "company_with_multiple_verifiers",
            "provided_services_display",
            "us_states_display",
            "verifier_company_cois",
            "company_url",
            "agreement_start_date",
            "agreement_expiration_date",
        )
        read_only_fields = (
            "state",
            "verifier",
            "agreement_start_date",
            "agreement_expiration_date",
        )

        extra_kwargs = {}
        for name in ENROLLMENT_FIELDS:
            extra_kwargs.setdefault(name, {})["label"] = ENROLLMENT_LABELS.get(name)

    @property
    def verifier(self):
        if self.instance and self.instance.pk:
            return self.instance.verifier
        return self.context["request"].user

    @property
    def company(self):
        """Return the enrollee company instance."""
        return self.verifier.company

    def validate(self, data):
        data["mailing_geocode"][
            "raw_address"
        ] = "{raw_street_line1} {raw_street_line2} " "{raw_zipcode} {raw_city}".format(
            **data["mailing_geocode"]
        )

        # check if we have all shipping_geocode then address will be different than mailing
        # in other case remove shipping_geocode to make it None in db
        if data.get("shipping_geocode"):
            shipping_geocode = {
                "raw_street_line1": data["shipping_geocode"].get("raw_street_line1", ""),
                "raw_street_line2": data["shipping_geocode"].get("raw_street_line2", ""),
                "raw_zipcode": data["shipping_geocode"].get("raw_zipcode", ""),
                "raw_city": data["shipping_geocode"].get("raw_city", None),
            }
            if all(
                [
                    shipping_geocode["raw_street_line1"],
                    shipping_geocode["raw_zipcode"],
                    shipping_geocode["raw_city"],
                ]
            ):
                shipping_geocode[
                    "raw_address"
                ] = "{raw_street_line1} {raw_street_line2} " "{raw_zipcode} {raw_city}".format(
                    **shipping_geocode
                )
                data["shipping_geocode"] = shipping_geocode
            else:
                if (
                    shipping_geocode["raw_street_line1"]
                    or shipping_geocode["raw_city"]
                    or shipping_geocode["raw_zipcode"]
                ):
                    raise ValidationError("Different shipping address is required")
                data.pop("shipping_geocode", None)

        administrative_contact_fields = [
            "administrative_contact_first_name",
            "administrative_contact_last_name",
            "administrative_contact_phone_number",
            "administrative_contact_email",
        ]
        administrative_contact_data = [data.get(field) for field in administrative_contact_fields]
        if any(administrative_contact_data) and not all(administrative_contact_data):
            administrative_contact_fields_errors = {}
            for field in administrative_contact_fields:
                if not data.get(field):
                    administrative_contact_fields_errors[field] = ["This field is required"]
            raise serializers.ValidationError(administrative_contact_fields_errors)

        company_officer_fields = [
            "company_officer_first_name",
            "company_officer_last_name",
            "company_officer_phone_number",
            "company_officer_title",
            "company_officer_email",
        ]

        if data.get("company_with_multiple_verifiers"):
            if not all(data.get(officer_field) for officer_field in company_officer_fields):
                raise ValidationError("Company officer fields are required")
        else:
            for officer_field in company_officer_fields:
                data.pop(officer_field, None)

        return data

    def save(self, **kwargs):
        """Save a BuilderAgreement with static fields locked to the customer and the builder."""

        instance = super(VerifierAgreementEnrollmentSerializer, self).save(
            owner=app.get_customer_company(), verifier=self.verifier, **kwargs
        )

        return instance

    def create(self, validated_data):
        """Create then issue message about creation to owner."""
        mailing_geocode_data = validated_data.pop("mailing_geocode")

        data_serializer = GeocodeMatchesSerializer(
            data={
                "street_line1": mailing_geocode_data["raw_street_line1"],
                "street_line2": mailing_geocode_data["raw_street_line2"],
                "city": mailing_geocode_data["raw_city"].id,
                "zipcode": mailing_geocode_data["raw_zipcode"],
            }
        )
        data_serializer.is_valid(raise_exception=True)
        mailing_geocode, create = data_serializer.save()
        validated_data["mailing_geocode"] = mailing_geocode

        shipping_geocode_data = validated_data.pop("shipping_geocode", None)
        if shipping_geocode_data:
            data_serializer = GeocodeMatchesSerializer(
                data={
                    "street_line1": shipping_geocode_data["raw_street_line1"],
                    "street_line2": shipping_geocode_data["raw_street_line2"],
                    "city": shipping_geocode_data["raw_city"].id,
                    "zipcode": shipping_geocode_data["raw_zipcode"],
                }
            )
            data_serializer.is_valid(raise_exception=True)
            shipping_geocode, create = data_serializer.save()
            validated_data["shipping_geocode"] = shipping_geocode

        instance = super(VerifierAgreementEnrollmentSerializer, self).create(validated_data)

        url = instance.get_absolute_url()
        NewVerifierAgreementEnrollmentMessage(url=url).send(
            company=instance.owner,
            context={
                "verifier": instance.verifier,
                "url": url,
                "list_url": reverse("hirl:verifier_agreements:list"),
            },
        )
        return instance

    def update(self, instance, validated_data):
        mailing_geocode_data = validated_data.pop("mailing_geocode")

        data_serializer = GeocodeMatchesSerializer(
            data={
                "street_line1": mailing_geocode_data["raw_street_line1"],
                "street_line2": mailing_geocode_data["raw_street_line2"],
                "city": mailing_geocode_data["raw_city"].id,
                "zipcode": mailing_geocode_data["raw_zipcode"],
            }
        )
        data_serializer.is_valid(raise_exception=True)
        mailing_geocode, create = data_serializer.save()
        validated_data["mailing_geocode"] = mailing_geocode

        shipping_geocode_data = validated_data.pop("shipping_geocode", None)
        if shipping_geocode_data:
            data_serializer = GeocodeMatchesSerializer(
                data={
                    "street_line1": shipping_geocode_data["raw_street_line1"],
                    "street_line2": shipping_geocode_data["raw_street_line2"],
                    "city": shipping_geocode_data["raw_city"].id,
                    "zipcode": shipping_geocode_data["raw_zipcode"],
                }
            )
            data_serializer.is_valid(raise_exception=True)
            shipping_geocode, create = data_serializer.save()
            validated_data["shipping_geocode"] = shipping_geocode
        return super(VerifierAgreementEnrollmentSerializer, self).update(instance, validated_data)

    # Field getters
    def get_company_display(self, instance=None):
        """Return enrollee display string."""

        return f"<a href='{self.verifier.company.get_absolute_url()}'>{self.verifier.company}</a>"

    def get_verifier_name_display(self, instance):
        return "{}".format(self.verifier.get_full_name())

    def get_verifier_company_url(self, obj):
        if obj.id and obj.verifier:
            company_type = obj.verifier.company.company_type
            company_pk = obj.verifier.company.pk
        else:
            company_type = self.context["request"].user.company.company_type
            company_pk = self.context["request"].user.company.pk
        return reverse("company:view", kwargs={"type": company_type, "pk": company_pk})

    def get_us_states_display(self, instance):
        if not instance.pk:
            return ""
        return ", ".join(instance.us_states.values_list("name", flat=True))

    def get_provided_services_display(self, instance):
        if not instance.pk:
            return ""
        return ", ".join(instance.provided_services.values_list("name", flat=True))

    def get_verifier_company_cois(self, instance):
        if not instance.id:
            return []
        return COIDocumentSerializer(
            instance.verifier.company.coi_documents.active(), many=True
        ).data


class COIDocumentSerializer(serializers.ModelSerializer):
    url = make_safe_field(serializers.CharField)(source="document.url", read_only=True)
    document_raw = serializers.CharField(required=False, write_only=True)
    document_raw_name = serializers.CharField(required=False, write_only=True)

    class Meta:
        model = COIDocument

        # "document" is readonly while we are the only ones using the api... we only send
        # document_raw.  This serializer should be updated to transition "raw" base64 the way the
        # HomeDocumentForm does.
        fields = (
            "id",
            "company",
            "document",
            "document_raw",
            "document_raw_name",
            "policy_number",
            "start_date",
            "expiration_date",
            "description",
            "created_at",
            "last_update",
            "url",
        )
        read_only_fields = ("id", "document", "created_at", "last_update")

    def validate(self, attrs):
        # do this hack to require document when we create it
        # but also allow send patch requests without document
        document_raw = attrs.pop("document_raw", None)
        document_raw_name = attrs.pop("document_raw_name", None)
        if not self.instance and (not document_raw or not document_raw_name):
            raise serializers.ValidationError({"document": "This field is required"})
        return attrs


class BasicCOIDocumentSerializer(COIDocumentSerializer):
    """
    Serializer for raters and providers that allow only upload file
    """

    class Meta:
        model = COIDocument
        fields = (
            "id",
            "company",
            "document",
            "document_raw",
            "document_raw_name",
            "policy_number",
            "start_date",
            "expiration_date",
            "description",
            "created_at",
            "last_update",
            "url",
        )
        read_only_fields = (
            "id",
            "document",
            "created_at",
            "last_update",
            "policy_number",
            "start_date",
            "expiration_date",
        )
