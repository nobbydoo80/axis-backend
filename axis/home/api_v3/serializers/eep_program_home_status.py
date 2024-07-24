"""eep_program_home_status.py - Axis"""

__author__ = "Steven K"
__date__ = "7/16/21 12:33"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from django.contrib.sites.shortcuts import get_current_site
from hashid_field.rest import HashidSerializerCharField
from rest_framework import serializers
from hashid_field import Hashid
from django.conf import settings
from django.urls import reverse_lazy
from axis.company.api_v3.serializers import CompanyInfoSerializer
from axis.core.api_v3.serializers import UserInfoSerializer
from axis.customer_hirl.models import HIRLProjectRegistration, HIRLProject
from axis.eep_program.api_v3.serializers import EEPProgramInfoSerializer
from axis.qa.models import QAStatus, QARequirement
from axis.floorplan.api_v3.serializers import FloorplanInfoSerializer
from axis.geocoder.api_v3.serializers import (
    GeocodeInfoSerializer,
    GeocodeBrokeredResponseSerializer,
)
from axis.home.models import EEPProgramHomeStatus
from .home import HomeInfoSerializer

log = logging.getLogger(__name__)


class EEPProgramHomeStatusSerializerMixin(metaclass=serializers.SerializerMetaclass):
    eep_program_info = EEPProgramInfoSerializer(source="eep_program")
    company_info = CompanyInfoSerializer(source="company")
    rater_of_record_info = UserInfoSerializer(source="rater_of_record")
    energy_modeler_info = UserInfoSerializer(source="energy_modeler")
    floorplan_info = FloorplanInfoSerializer(source="floorplan")
    home_info = HomeInfoSerializer(source="home")


class EEPProgramHomeStatusMeta:
    """
    Base Meta model for EEPProgramHomeStatus with common fields
    """

    model = EEPProgramHomeStatus
    fields = (
        "id",
        "state",
        "eep_program",
        "eep_program_info",
        "company",
        "company_info",
        "rater_of_record",
        "rater_of_record_info",
        "energy_modeler",
        "energy_modeler_info",
        "field_inspectors",
        "floorplan",
        "floorplan_info",
        "floorplans",
        "certification_date",
        "home",
        "home_info",
        "customer_hirl_project",
        # Accounting
        "pct_complete",
        "is_billable",
        "modified_date",
        "created_date",
    )


class EEPProgramHomeStatusHIRLProjectRegistrationInfoSerializer(serializers.ModelSerializer):
    id = HashidSerializerCharField(
        source_field="customer_hirl.HIRLProjectRegistration.id", read_only=True
    )
    registration_user_info = UserInfoSerializer(source="registration_user", read_only=True)
    eep_program_info = EEPProgramInfoSerializer(source="eep_program", read_only=True)
    builder_organization_info = CompanyInfoSerializer(source="builder_organization", read_only=True)
    architect_organization_info = CompanyInfoSerializer(
        source="architect_organization", read_only=True
    )
    developer_organization_info = CompanyInfoSerializer(
        source="developer_organization", read_only=True
    )
    community_owner_organization_info = CompanyInfoSerializer(
        source="community_owner_organization", read_only=True
    )

    class Meta:
        model = HIRLProjectRegistration
        fields = (
            "id",
            "project_type",
            "state",
            "state_changed_at",
            "state_change_reason",
            "registration_user",
            "registration_user_info",
            "eep_program",
            "eep_program_info",
            "builder_organization",
            "builder_organization_info",
            "architect_organization",
            "architect_organization_info",
            "developer_organization",
            "developer_organization_info",
            "community_owner_organization",
            "community_owner_organization_info",
        )


class EEPProgramHomeStatusHIRLProjectInfoSerializer(serializers.ModelSerializer):
    """
    Special serializer for EEPProgramHomeStatus that is not contain Home Status data to
    avoid circular import
    """

    id = HashidSerializerCharField(source_field="customer_hirl.HIRLProject.id", read_only=True)
    registration = serializers.PrimaryKeyRelatedField(
        pk_field=HashidSerializerCharField(source_field="customer_hirl.HIRLProjectRegistration.id"),
        queryset=HIRLProjectRegistration.objects.all(),
    )
    home_address_geocode_info = GeocodeInfoSerializer(source="home_address_geocode", read_only=True)
    home_address_geocode_response_info = GeocodeBrokeredResponseSerializer(
        source="home_address_geocode_response", read_only=True
    )
    registration_info = EEPProgramHomeStatusHIRLProjectRegistrationInfoSerializer(
        source="registration"
    )

    class Meta:
        model = HIRLProject
        fields = (
            "id",
            "registration",
            "registration_info",
            "home_address_geocode",
            "home_address_geocode_info",
            "home_address_geocode_response",
            "home_address_geocode_response_info",
            "is_accessory_structure",
            "accessory_structure_description",
            "h_number",
            "created_at",
        )


class EEPProgramHomeStatusInfoSerializer(
    EEPProgramHomeStatusSerializerMixin, serializers.ModelSerializer
):
    customer_hirl_project = serializers.PrimaryKeyRelatedField(
        pk_field=HashidSerializerCharField(source_field="customer_hirl.HIRLProject.id"),
        queryset=HIRLProject.objects.all(),
        allow_null=True,
    )
    customer_hirl_project_info = EEPProgramHomeStatusHIRLProjectInfoSerializer(
        source="customer_hirl_project"
    )

    class Meta(EEPProgramHomeStatusMeta):
        fields = (
            "id",
            "state",
            "eep_program",
            "eep_program_info",
            "company",
            "company_info",
            "rater_of_record",
            "rater_of_record_info",
            "energy_modeler",
            "energy_modeler_info",
            "field_inspectors",
            "floorplan",
            "floorplan_info",
            "floorplans",
            "certification_date",
            "home",
            "home_info",
            "customer_hirl_project",
            "customer_hirl_project_info",
            # Accounting
            "pct_complete",
            "is_billable",
            "modified_date",
            "created_date",
        )


class BasicEEPProgramHomeStatusSerializer(
    EEPProgramHomeStatusSerializerMixin, serializers.ModelSerializer
):
    """Basic control of EEPProgramHomeStatus instance."""

    class Meta(EEPProgramHomeStatusMeta):
        pass


class EEPProgramHomeStatusSerializer(
    EEPProgramHomeStatusSerializerMixin, serializers.ModelSerializer
):
    """Allows full control of EEPProgramHomeStatus instance."""

    class Meta(EEPProgramHomeStatusMeta):
        pass


class CustomerHIRLCertifiedProjectsByMonthMetricsSerializer(serializers.Serializer):
    certification_date_month = serializers.DateField()
    home_status_count = serializers.IntegerField(default=0)

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError


class CustomerHIRLCertifiedUnitsByMonthMetricsSerializer(serializers.Serializer):
    certification_date_month = serializers.DateField()
    units_count = serializers.IntegerField(default=0)

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError


class CustomerHIRLBulkCertificateEEPProgramHomeStatusList(serializers.ModelSerializer):
    eep_program_info = EEPProgramInfoSerializer(source="eep_program")
    company_info = CompanyInfoSerializer(source="company")
    home_info = HomeInfoSerializer(source="home")
    customer_hirl_legacy_id = serializers.ReadOnlyField(source="hirl_legacy_project_id")
    subdivision_name = serializers.ReadOnlyField(source="home.subdivision.name")
    certification_link = serializers.SerializerMethodField(source="id", read_only=True)

    class Meta:
        model = EEPProgramHomeStatus
        fields = (
            "id",
            "state",
            "eep_program",
            "eep_program_info",
            "company",
            "company_info",
            "home",
            "home_info",
            "customer_hirl_project",
            "customer_hirl_legacy_id",
            "certification_date",
            "subdivision_name",
            "modified_date",
            "created_date",
            "certification_link",
        )

    def get_certification_link(self, obj):
        user_id_hash = self.context["request"].user.id
        current_site = get_current_site(self.context["request"])
        full_url = obj.get_certification_link(user_id_hash, current_site)
        return full_url


class CustomerHIRLCertificateLookupListSerializer(serializers.ModelSerializer):
    address = serializers.SerializerMethodField()
    company_info = CompanyInfoSerializer(source="company")
    subdivision_name = serializers.ReadOnlyField(source="home.subdivision.name")
    certification_path = serializers.ReadOnlyField(source="eep_program.name")
    client_name = serializers.SerializerMethodField()
    certification_link = serializers.SerializerMethodField(source="id", read_only=True)
    certification_level = serializers.SerializerMethodField()

    class Meta:
        model = EEPProgramHomeStatus
        fields = (
            "id",
            "address",
            "company",
            "company_info",
            "client_name",
            "certification_path",
            "certification_date",
            "subdivision_name",
            "certification_level",
            "certification_link",
        )

    def get_client_name(self, obj) -> str:
        client_name = ""
        client_comany = obj.customer_hirl_project.registration.get_project_client_company()
        client_name = client_comany.name
        return client_name

    def get_address(self, obj) -> str:
        address = obj.home.get_home_address_display(
            include_city_state_zip=True, raw=True, include_lot_number=False
        )
        return address

    def get_certification_level(self, obj):
        certification_level = ""
        if obj.pk:
            try:
                certification_level = obj.qastatus_set.get(
                    requirement__type=QARequirement.FINAL_INSPECTION_QA_REQUIREMENT_TYPE
                ).get_hirl_certification_level_awarded_display()
            except QAStatus.DoesNotExist:
                certification_level = ""

        return certification_level

    def get_certification_link(self, obj):
        current_site = get_current_site(self.context["request"])
        user_id_hash = obj.customer_hirl_project.registration.registration_user.id
        full_url = obj.get_certification_link(user_id_hash, current_site)
        return full_url
