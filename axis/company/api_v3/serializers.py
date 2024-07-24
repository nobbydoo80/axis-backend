"""Slim serializers for object references on other models."""

__author__ = "Artem Hruzd"
__date__ = "01/06/2020 20:55"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from localflavor.us.us_states import USPS_CHOICES
from rest_framework import serializers

from axis.company.api_v3 import COMPANY_COMMON_SERIALIZER_FIELDS
from axis.company.models import AltName, SponsorPreferences, Company
from axis.company.models import CompanyAccess, CompanyRole
from axis.customer_eto.api_v3.serializers.eto_account import ETOAccountInfoSerializer
from axis.customer_eto.models import ETOAccount
from axis.customer_hirl.models import BuilderAgreement, COIDocument
from axis.customer_hirl.serializers.client import HIRLCompanyClientSerializer
from axis.geocoder.api_v3.serializers import (
    GeocodeInfoSerializer,
    GeocodeBrokeredResponseSerializer,
)
from axis.geographic.api_v3.serializers import CitySerializer
from axis.geographic.models import County
from axis.relationship.models import Relationship

User = get_user_model()


class SponsorSlugsField(serializers.RelatedField):
    def to_internal_value(self, data):
        return super(SponsorSlugsField, self).to_internal_value(data)

    def to_representation(self, value):
        return value.slug


class CompanyTypeSerializerMixin(metaclass=serializers.SerializerMetaclass):
    """
    Using as a parent class for all company types serializer
    """

    city_info = CitySerializer(read_only=True, source="city")
    total_users = serializers.IntegerField(read_only=True)
    total_company_admin_users = serializers.IntegerField(read_only=True)
    shipping_geocode_info = GeocodeInfoSerializer(source="shipping_geocode", read_only=True)
    shipping_geocode_response_info = GeocodeBrokeredResponseSerializer(
        source="shipping_geocode_response", read_only=True
    )
    active_customer_hirl_builder_agreements_count = serializers.IntegerField(
        read_only=True, help_text="CounterSigned Builder Agreements by HI customer"
    )
    active_coi_document_count = serializers.IntegerField(
        read_only=True, help_text="Number of non expired COI for Company"
    )
    sponsor_slugs = SponsorSlugsField(source="sponsors", many=True, read_only=True)
    hirlcompanyclient = HIRLCompanyClientSerializer(
        help_text="HI additional company information", read_only=True
    )
    eto_account_info = ETOAccountInfoSerializer(source="eto_account", read_only=True)
    eto_account = serializers.PrimaryKeyRelatedField(
        queryset=ETOAccount.objects.all(), allow_null=True, required=False
    )

    def validate_company_type(self, value):
        """
        Do not allow to create Company of the same type of User company_type
        :param value: company_type
        :return: company_type
        """
        request = self.context.get("request")
        company = None
        if request:
            if request.user.is_superuser:
                return value
            else:
                company = getattr(request.user, "company", None)

        if company and company.company_type == value:
            raise serializers.ValidationError("Cannot create company for this type")
        return value

    def create(self, validated_data):
        company = super(CompanyTypeSerializerMixin, self).create(validated_data)
        Relationship.objects.validate_or_create_relations_to_entity(
            entity=company, direct_relation=self.context["request"].user.company
        )
        return company


class CompanyInfoSerializer(serializers.ModelSerializer):
    """Contains only basic information about company."""

    sponsor_slugs = SponsorSlugsField(source="sponsors", many=True, read_only=True)
    hirlcompanyclient = HIRLCompanyClientSerializer(
        help_text="HI additional company information", read_only=True
    )
    city_info = CitySerializer(read_only=True, source="city")
    shipping_geocode_info = GeocodeInfoSerializer(source="shipping_geocode", read_only=True)
    shipping_geocode_response_info = GeocodeBrokeredResponseSerializer(
        source="shipping_geocode_response", read_only=True
    )

    class Meta:
        model = Company
        fields = (
            "id",
            "name",
            "slug",
            "company_type",
            "sponsors",
            "sponsor_slugs",
            "hirlcompanyclient",
            # Place fields
            "street_line1",
            "street_line2",
            "state",
            "metro",
            "latitude",
            "longitude",
            "zipcode",
            "city",
            "city_info",
            "confirmed_address",
            "address_override",
            "geocode_response",
            "shipping_geocode",
            "shipping_geocode_info",
            "shipping_geocode_response",
            "shipping_geocode_response_info",
        )
        read_only_fields = (
            "id",
            "name",
            "slug",
            "company_type",
            "sponsors",
            "hirlcompanyclient",
        )


class CompanySerializer(CompanyTypeSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = COMPANY_COMMON_SERIALIZER_FIELDS
        ref_name = "AxisCompanySerializer"


class AltNameSerializer(serializers.ModelSerializer):
    company_info = CompanyInfoSerializer(source="company", read_only=True)

    class Meta:
        model = AltName
        fields = ("id", "name", "company_info")


class NestedAltNameSerializer(serializers.ModelSerializer):
    """
    Allow user not specify company_id in data params
    """

    company_info = CompanyInfoSerializer(source="company", read_only=True)

    class Meta:
        model = AltName
        fields = ("id", "name", "company_info")


class AffiliationPreferencesSerializer(serializers.ModelSerializer):
    """
    Affiliation preference serializer
    """

    sponsor_info = CompanyInfoSerializer(source="sponsor", read_only=True)

    class Meta:
        model = SponsorPreferences
        fields = (
            "id",
            "sponsor",
            "sponsor_info",
            "can_edit_profile",
            "can_edit_identity_fields",
            "notify_sponsor_on_update",
        )


class SponsoringPreferencesMeta:
    model = SponsorPreferences
    fields = (
        "id",
        "sponsored_company",
        "sponsored_company_info",
        "can_edit_profile",
        "can_edit_identity_fields",
        "notify_sponsor_on_update",
    )


class SponsoringPreferencesSerializer(serializers.ModelSerializer):
    """
    Sponsoring preference serializer
    """

    sponsored_company_info = CompanyInfoSerializer(source="sponsored_company", read_only=True)

    class Meta(SponsoringPreferencesMeta):
        pass


class UpdateSponsoringPreferencesSerializer(SponsoringPreferencesSerializer):
    """
    Do not allow to modify sponsored company on update
    """

    class Meta(SponsoringPreferencesMeta):
        read_only_fields = ("sponsored_company",)


class SponsorPreferencesSerializer(serializers.ModelSerializer):
    """
    Contains full information about SponsorPreferences object
    """

    sponsor_info = CompanyInfoSerializer(source="sponsor", read_only=True)
    sponsored_company_info = CompanyInfoSerializer(source="sponsored_company", read_only=True)

    class Meta:
        model = SponsorPreferences
        fields = (
            "id",
            "sponsor",
            "sponsor_info",
            "sponsored_company",
            "sponsored_company_info",
            "can_edit_profile",
            "can_edit_identity_fields",
            "notify_sponsor_on_update",
        )

    def validate(self, attrs):
        sponsor = attrs.get("sponsor")
        sponsored_company = attrs.get("sponsored_company")

        if SponsorPreferences.objects.filter(
            sponsor=sponsor, sponsored_company=sponsored_company
        ).exists():
            raise serializers.ValidationError(
                {
                    "sponsored_company": f"Sponsor Preferences for {sponsored_company} by {sponsor} already exists"
                }
            )
        return attrs


class CompanyAggregatedCountyByStateSerializer(serializers.Serializer):
    state = serializers.CharField()
    state_name = serializers.SerializerMethodField()
    counties = serializers.IntegerField()
    selected_counties = serializers.IntegerField()

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError

    def get_state_name(self, data):
        return dict(USPS_CHOICES).get(data["state"])


class CompanyUpdateCountiesByStateSerializer(serializers.Serializer):
    state = serializers.ChoiceField(choices=USPS_CHOICES)
    counties = serializers.ListField(child=serializers.IntegerField())

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        counties_ids = validated_data["counties"]
        state = validated_data["state"]
        state_counties = County.objects.filter(id__in=counties_ids, state=state)
        instance_counties = instance.counties.filter(state=state)

        instance.counties.remove(*instance_counties)
        instance.counties.add(*state_counties)
        return instance


class CopyResourcesToOtherCompanySerializer(serializers.Serializer):
    company_from = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all())
    companies_to = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all(), many=True)
    copy_client_agreement = serializers.BooleanField(default=False)
    copy_coi = serializers.BooleanField(default=False)
    move_client_agreement = serializers.BooleanField(default=False)
    move_coi = serializers.BooleanField(default=False)

    def validate_companies_to(self, value):
        if len(value) == 0:
            raise serializers.ValidationError("Provide at least one company to copy data")
        return value

    def create(self, validated_data):
        company_from = validated_data.pop("company_from")
        companies_to = validated_data.pop("companies_to")
        copy_client_agreement = validated_data.pop("copy_client_agreement")
        move_client_agreement = validated_data.pop("move_client_agreement")
        copy_coi = validated_data.pop("copy_coi")
        move_coi = validated_data.pop("move_coi")

        if copy_client_agreement and move_client_agreement:
            raise serializers.ValidationError(
                {
                    "non_field_errors": "Cannot perform move and copy Client Agreement in the same time"
                }
            )

        if copy_coi and move_coi:
            raise serializers.ValidationError(
                {
                    "non_field_errors": "Cannot perform move and copy Certificate Of Insurances in the same time"
                }
            )

        data = {"client_agreements": [], "cois": []}
        if copy_client_agreement:
            client_agreement = company_from.customer_hirl_enrolled_agreements.exclude(
                state=BuilderAgreement.EXPIRED
            ).first()
            if client_agreement:
                for company_to in companies_to:
                    company_to.customer_hirl_enrolled_agreements.all().update(
                        state=BuilderAgreement.EXPIRED
                    )
                    # created date is not copy automatically
                    date_created = client_agreement.date_created
                    client_agreement.id = None
                    client_agreement.company = company_to
                    client_agreement.save()

                    client_agreement.date_created = date_created
                    client_agreement.save()

                    data["client_agreements"].append(client_agreement.id)

        if move_client_agreement:
            client_agreements = company_from.customer_hirl_enrolled_agreements.all()
            for company_to in companies_to:
                for client_agreement in client_agreements:
                    client_agreement.company = company_to
                    client_agreement.save()
                    data["client_agreements"].append(client_agreement.id)

        if copy_coi:
            cois = company_from.coi_documents.all()
            for company_to in companies_to:
                company_to.coi_documents.all().delete()
                for coi in cois:
                    # created date is not copy automatically
                    created_at = coi.created_at
                    coi.id = None
                    coi.company = company_to
                    coi.save()

                    coi.created_at = created_at
                    coi.save()

                    data["cois"].append(coi.id)

        if move_coi:
            cois = company_from.coi_documents.all()
            for company_to in companies_to:
                for coi in cois:
                    coi.company = company_to
                    coi.save()
                    data["cois"].append(coi.id)

        return data

    def update(self, instance, validated_data):
        raise NotImplementedError


class CopiedResourcesToOtherCompanyResponseSerializer(serializers.Serializer):
    client_agreements = serializers.PrimaryKeyRelatedField(
        queryset=BuilderAgreement.objects.all(), many=True
    )
    cois = serializers.PrimaryKeyRelatedField(queryset=COIDocument.objects.all(), many=True)

    def create(self, validated_data):
        return NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError


class CompanyFlatListSerializer(serializers.ModelSerializer):
    """
    Flat optimized list of companies to display
    """

    address = serializers.SerializerMethodField()
    eto_account = serializers.SerializerMethodField()
    hirlcompanyclient_id = serializers.ReadOnlyField(source="hirlcompanyclient.id", read_only=True)
    state = serializers.SerializerMethodField()
    total_users = serializers.IntegerField(read_only=True)
    total_company_admin_users = serializers.IntegerField(read_only=True)

    class Meta:
        model = Company
        fields = (
            "id",
            "name",
            "company_type",
            "address",
            "state",
            "zipcode",
            "office_phone",
            "eto_account",
            "total_users",
            "total_company_admin_users",
            "hirlcompanyclient_id",
        )

    def get_address(self, company):
        address_line = company.street_line1
        if company.street_line2:
            address_line += f" {company.street_line2}"
        return address_line

    def get_eto_account(self, company):
        try:
            return company.eto_account.account_number
        except ObjectDoesNotExist:
            return ""

    def get_state(self, company):
        if getattr(company, "city", None):
            if getattr(company.city, "county", None):
                return company.city.county.state
        return ""


class CompanyRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyRole
        fields = (
            "id",
            "slug",
            "name",
        )


class CompanyAccessSerializer(serializers.ModelSerializer):
    from axis.core.api_v3.serializers.fields import FilterByUserPrimaryKeyRelatedField

    user = FilterByUserPrimaryKeyRelatedField(queryset=User.objects.all(), required=True)
    company = FilterByUserPrimaryKeyRelatedField(queryset=Company.objects.all(), required=True)
    company_info = CompanyInfoSerializer(source="company", read_only=True)
    roles_info = CompanyRoleSerializer(source="roles", many=True, read_only=True)
    user_info = serializers.SerializerMethodField()

    class Meta:
        model = CompanyAccess
        fields = ("id", "user", "user_info", "company", "company_info", "roles", "roles_info")

    def get_user_info(self, company_access: CompanyAccess):
        """
        Avoid circular import by using SerializerMethodField
        :param company_access: CompanyAccess instance
        :return: UserInfoSerializer().data
        """
        from axis.core.api_v3.serializers import UserInfoSerializer

        return UserInfoSerializer(company_access.user, read_only=True).data

    def get_validators(self):
        """
        Override DRF get_validators method to remove check for unique_together.
        We do not need it because we use `update_or_create` in create method
        """
        # If the validators have been declared explicitly then use that.
        validators = getattr(getattr(self, "Meta", None), "validators", None)
        if validators is not None:
            return list(validators)

        # Otherwise use the default set of validators.
        return self.get_unique_for_date_validators()

    def create(self, validated_data):
        user = validated_data["user"]
        company = validated_data["company"]
        roles = validated_data["roles"]

        company_access, created = CompanyAccess.objects.update_or_create(
            user=user, company=company, defaults={}
        )
        company_access.roles.set(roles)
        return company_access

    def update(self, instance, validated_data):
        validated_data.pop("user", None)
        validated_data.pop("company", None)
        return super(CompanyAccessSerializer, self).update(instance, validated_data)


class ChangeCompanySerializer(serializers.Serializer):
    from axis.core.api_v3.serializers.fields import FilterByUserPrimaryKeyRelatedField

    company_access = FilterByUserPrimaryKeyRelatedField(
        queryset=CompanyAccess.objects.all(), required=True
    )

    def create(self, validated_data):
        company_access = validated_data["company_access"]
        company = company_access.company
        request = self.context.get("request", None)
        if request:
            user = request.user
            user.company = company_access.company
            user.save()

        return company

    def update(self, instance, validated_data):
        raise NotImplementedError
