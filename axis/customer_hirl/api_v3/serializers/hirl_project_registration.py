"""hirl_project_registration.py: """

__author__ = "Artem Hruzd"
__date__ = "04/16/2021 17:21"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from hashid_field.rest import HashidSerializerCharField
from rest_framework import serializers

from axis.company.api_v3.serializers import CompanyInfoSerializer
from axis.core.api_v3.serializers import UserInfoSerializer, ContactCardSerializer
from axis.customer_hirl.models import HIRLProject, HIRLProjectRegistration
from axis.customer_hirl.utils import (
    hirl_project_address_is_unique,
    get_hirl_project_address_components,
)
from axis.eep_program.api_v3.serializers import EEPProgramInfoSerializer
from axis.subdivision.api_v3.serializers import SubdivisionInfoSerializer


class HIRLProjectRegistrationInfoSerializer(serializers.ModelSerializer):
    id = HashidSerializerCharField(
        source_field="customer_hirl.HIRLProjectRegistration.id", read_only=True
    )
    registration_user_info = UserInfoSerializer(source="registration_user", read_only=True)
    eep_program_info = EEPProgramInfoSerializer(source="eep_program", read_only=True)
    subdivision_info = SubdivisionInfoSerializer(source="subdivision", read_only=True)

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
            "subdivision",
            "subdivision_info",
            "project_name",
        )


class HIRLProjectRegistrationSerializerMixin(metaclass=serializers.SerializerMetaclass):
    """
    Only support update. To create HIRLProjectRegistration use appropriate methods
    """

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
    subdivision_info = SubdivisionInfoSerializer(source="subdivision", read_only=True)

    builder_organization_contact_info = ContactCardSerializer(
        source="builder_organization_contact", read_only=True
    )
    developer_organization_contact_info = ContactCardSerializer(
        source="developer_organization_contact", read_only=True
    )
    community_owner_organization_contact_info = ContactCardSerializer(
        source="community_owner_organization_contact", read_only=True
    )
    architect_organization_contact_info = ContactCardSerializer(
        source="architect_organization_contact", read_only=True
    )
    projects_count = serializers.IntegerField(read_only=True)

    def validate(self, attrs):
        registration = getattr(self, "instance")
        is_build_to_rent = attrs.get("is_build_to_rent", registration.is_build_to_rent)

        if registration.project_type == HIRLProjectRegistration.SINGLE_FAMILY_PROJECT_TYPE:
            required_fields = ["builder_organization"]
            if is_build_to_rent:
                required_fields.append("developer_organization")
                required_fields.append("developer_organization_contact")

        elif registration.project_type == HIRLProjectRegistration.MULTI_FAMILY_PROJECT_TYPE:
            required_fields = [
                "project_name",
                "project_client",
                "estimated_completion_date",
                "application_packet_completion",
                "party_named_on_certificate",
                "project_contact_first_name",
                "project_contact_last_name",
                "project_contact_email",
                "project_contact_phone_number",
            ]
        elif registration.project_type == HIRLProjectRegistration.LAND_DEVELOPMENT_PROJECT_TYPE:
            required_fields = [
                "project_name",
                "estimated_completion_date",
                "developer_organization",
                "developer_organization_contact",
            ]
        else:
            raise serializers.ValidationError({"project_type": "Project Type field is required"})

        for required_field_name in required_fields:
            if required_field_name in attrs.keys() and not attrs[required_field_name]:
                raise serializers.ValidationError(
                    {
                        required_field_name: [
                            "This field is required",
                        ]
                    }
                )
        return attrs

    def update(self, instance, validated_data):
        is_build_to_rent = validated_data.get("is_build_to_rent", instance.is_build_to_rent)
        if instance.project_type == HIRLProjectRegistration.SINGLE_FAMILY_PROJECT_TYPE:
            if is_build_to_rent:
                validated_data["project_client"] = HIRLProjectRegistration.PROJECT_CLIENT_DEVELOPER
                validated_data[
                    "entity_responsible_for_payment"
                ] = HIRLProjectRegistration.DEVELOPER_RESPONSIBLE_ENTITY
            else:
                validated_data["developer_organization"] = None
                validated_data["developer_organization_contact"] = None
                validated_data["project_client"] = HIRLProjectRegistration.PROJECT_CLIENT_BUILDER
                validated_data[
                    "entity_responsible_for_payment"
                ] = HIRLProjectRegistration.BUILDER_RESPONSIBLE_ENTITY

        return super(HIRLProjectRegistrationSerializerMixin, self).update(instance, validated_data)


class HIRLProjectRegistrationMeta:
    """
    Base Meta model for HIRLProjectRegistration with common fields
    """

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
        "subdivision",
        "subdivision_info",
        "builder_organization",
        "builder_organization_info",
        "builder_organization_contact",
        "builder_organization_contact_info",
        # single family specific
        "is_build_to_rent",
        # multi family specific
        "project_name",
        "project_client",
        "community_named_on_certificate",
        "project_contact_first_name",
        "project_contact_last_name",
        "project_contact_email",
        "project_contact_phone_number",
        "application_packet_completion",
        "party_named_on_certificate",
        "project_description",
        "estimated_completion_date",
        "project_website_url",
        "building_will_include_non_residential_space",
        "seeking_hud_mortgage_insurance_premium_reduction",
        "seeking_fannie_mae_green_financing",
        "seeking_freddie_mac_green_financing",
        "intended_to_be_affordable_housing",
        "developer_organization",
        "developer_organization_info",
        "developer_organization_contact",
        "developer_organization_contact_info",
        "community_owner_organization",
        "community_owner_organization_info",
        "community_owner_organization_contact",
        "community_owner_organization_contact_info",
        "architect_organization",
        "architect_organization_info",
        "architect_organization_contact",
        "architect_organization_contact_info",
        "marketing_first_name",
        "marketing_last_name",
        "marketing_email",
        "marketing_phone",
        "sales_phone",
        "sales_email",
        "sales_website_url",
        "entity_responsible_for_payment",
        "billing_first_name",
        "billing_last_name",
        "billing_email",
        "billing_phone",
        "sampling",
        # land development specific
        "ld_workflow",
        # annotations
        "projects_count",
    )


class HIRLProjectRegistrationSerializer(
    HIRLProjectRegistrationSerializerMixin, serializers.ModelSerializer
):
    """
    Full information about Project Registration
    """

    class Meta(HIRLProjectRegistrationMeta):
        pass


class BasicHIRLProjectRegistrationSerializer(
    HIRLProjectRegistrationSerializerMixin, serializers.ModelSerializer
):
    """
    Base Project Registration fields available for Common users
    """

    class Meta(HIRLProjectRegistrationMeta):
        pass


class HIRLProjectRegistrationListSerializer(serializers.ModelSerializer):
    id = HashidSerializerCharField(
        source_field="customer_hirl.HIRLProjectRegistration.id", read_only=True
    )
    registration_user_info = UserInfoSerializer(source="registration_user", read_only=True)
    eep_program_info = EEPProgramInfoSerializer(source="eep_program", read_only=True)
    subdivision_info = SubdivisionInfoSerializer(source="subdivision", read_only=True)
    projects_count = serializers.IntegerField(read_only=True)

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
            "subdivision",
            "subdivision_info",
            "project_name",
            "project_client",
            # annotations
            "projects_count",
        )


class CreateSFHIRLProjectSerializer(serializers.ModelSerializer):
    """
    Serializer is using to create nested projects on Project Registration
    """

    class Meta:
        model = HIRLProject
        fields = (
            "is_accessory_structure",
            "accessory_structure_description",
            "is_accessory_dwelling_unit",
            "accessory_dwelling_unit_description",
            "lot_number",
            "home_address_geocode",
            "home_address_geocode_response",
            "hud_disaster_case_number",
            "green_energy_badges",
            "is_require_water_sense_certification",
            "is_require_rough_inspection",
            "is_require_wri_certification",
            "is_appeals_project",
        )

    def validate(self, attrs):
        is_accessory_structure = attrs.get("is_accessory_structure")

        if is_accessory_structure:
            if not attrs.get("accessory_structure_description"):
                raise serializers.ValidationError(
                    {"accessory_structure_description": "Description is required"}
                )
        else:
            attrs["accessory_structure_description"] = ""

        is_accessory_dwelling_unit = attrs.get("is_accessory_dwelling_unit")
        if is_accessory_dwelling_unit:
            if not attrs.get("accessory_dwelling_unit_description"):
                raise serializers.ValidationError(
                    {"accessory_dwelling_unit_description": "Description is required"}
                )
        else:
            attrs["accessory_dwelling_unit_description"] = ""

        if is_accessory_structure and is_accessory_dwelling_unit:
            raise serializers.ValidationError(
                {
                    "is_accessory_dwelling_unit": "Project can be only Accessory Structure "
                    "or Accessory Dwelling Unit. Not both"
                }
            )
        return attrs


class CreateSFHIRLProjectRegistrationSerializer(serializers.ModelSerializer):
    projects = CreateSFHIRLProjectSerializer(many=True)

    class Meta:
        model = HIRLProjectRegistration
        fields = (
            "eep_program",
            "builder_organization",
            "builder_organization_contact",
            "subdivision",
            "is_build_to_rent",
            "developer_organization",
            "developer_organization_contact",
            "projects",
            "building_will_include_non_residential_space",
            "seeking_hud_mortgage_insurance_premium_reduction",
            "seeking_fannie_mae_green_financing",
            "seeking_freddie_mac_green_financing",
            "intended_to_be_affordable_housing",
            "sampling",
        )
        extra_kwargs = {
            "eep_program": {"required": True},
            "builder_organization": {"required": True},
            "builder_organization_contact": {"required": True},
        }

    def validate_projects(self, value):
        if len(value) == 0:
            raise serializers.ValidationError(
                {"projects": "Provide at least one project to create Single Family Registration"}
            )
        return value

    def validate(self, attrs):
        is_build_to_rent = attrs.get("is_build_to_rent")

        developer_organization = attrs.get("developer_organization")
        developer_organization_contact = attrs.get("developer_organization_contact")

        if is_build_to_rent and not developer_organization:
            raise serializers.ValidationError(
                {"developer_organization": "Developer Organization is required"}
            )

        if is_build_to_rent and not developer_organization_contact:
            raise serializers.ValidationError(
                {"developer_organization_contact": "Developer Organization Contact is required"}
            )

        # validate for unique address between projects
        seen_addresses = []

        for project_attrs in attrs["projects"]:
            home_address_geocode_response = project_attrs.get("home_address_geocode_response")
            address_components = get_hirl_project_address_components(
                home_address_geocode=project_attrs.get("home_address_geocode"),
                home_address_geocode_response=home_address_geocode_response,
            )
            if not address_components:
                raise serializers.ValidationError({"non_field_error": "Provide project address"})
            address = (
                f'{address_components["street_line1"]}'
                f'{address_components["street_line2"]}'
                f'{address_components["city"]}'
                f'{address_components["zipcode"]}'
            )

            if address in seen_addresses:
                raise serializers.ValidationError(
                    {"non_field_error": f"Project Address: {address} is not Unique"}
                )
            else:
                seen_addresses.append(address)

            is_unique = hirl_project_address_is_unique(
                street_line1=address_components["street_line1"],
                street_line2=address_components["street_line2"],
                city=address_components["city"],
                zipcode=address_components["zipcode"],
                project_type=HIRLProjectRegistration.SINGLE_FAMILY_PROJECT_TYPE,
                project=None,
                geocode_response=home_address_geocode_response,
            )

            if not is_unique:
                raise serializers.ValidationError(
                    {"non_field_error": f"Project Address: {address} is not Unique"}
                )

            builder_organization = attrs.get("builder_organization")
            subdivision = attrs.get("subdivision")

            if subdivision:
                if subdivision.builder_org_id != builder_organization.id:
                    raise serializers.ValidationError(
                        {
                            "builder_organization": "Builder Organization must be the same as for selected Subdivision"
                        }
                    )

        return attrs

    def create(self, validated_data):
        projects_data = validated_data.pop("projects")
        is_build_to_rent = validated_data.get("is_build_to_rent", False)
        if is_build_to_rent:
            validated_data["project_client"] = HIRLProjectRegistration.PROJECT_CLIENT_DEVELOPER
            validated_data[
                "entity_responsible_for_payment"
            ] = HIRLProjectRegistration.DEVELOPER_RESPONSIBLE_ENTITY
        else:
            validated_data["developer_organization"] = None
            validated_data["project_client"] = HIRLProjectRegistration.PROJECT_CLIENT_BUILDER
            validated_data[
                "entity_responsible_for_payment"
            ] = HIRLProjectRegistration.BUILDER_RESPONSIBLE_ENTITY

        registration = HIRLProjectRegistration.objects.create(**validated_data)
        for project_data in projects_data:
            green_energy_badges = project_data.pop("green_energy_badges", [])
            project = HIRLProject.objects.create(registration=registration, **project_data)
            project.green_energy_badges.add(*green_energy_badges)
        return registration


class CreateLandDevelopmentHIRLProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = HIRLProject
        fields = (
            "lot_number",
            "home_address_geocode",
            "home_address_geocode_response",
            "number_of_lots",
            "land_development_project_type",
            "are_all_homes_in_ld_seeking_certification",
            "land_development_phase_number",
        )
        extra_kwargs = {
            "number_of_lots": {"required": False},
            "land_development_project_type": {"required": True},
            "home_address_geocode": {"required": True},
        }

    def validate(self, attrs):
        land_development_project_type = attrs["land_development_project_type"]
        number_of_lots = attrs.get("number_of_lots")

        if land_development_project_type == HIRLProject.LD_PROJECT_TYPE_PHASE_PROJECT:
            if not number_of_lots:
                raise serializers.ValidationError({"number_of_lots": "This field is required"})

        return attrs


class CreateLandDevelopmentHIRLProjectRegistrationSerializer(serializers.ModelSerializer):
    projects = CreateLandDevelopmentHIRLProjectSerializer(many=True)

    class Meta:
        model = HIRLProjectRegistration
        fields = (
            "eep_program",
            "developer_organization",
            "developer_organization_contact",
            "estimated_completion_date",
            "project_name",
            "project_description",
            "project_website_url",
            "ld_workflow",
            "projects",
        )
        extra_kwargs = {
            "eep_program": {"required": True},
            "developer_organization": {"required": True},
            "developer_organization_contact": {"required": True},
            "estimated_completion_date": {"required": True},
            "project_description": {"required": True},
            "project_website_url": {"required": True},
        }

    def validate_projects(self, value):
        if len(value) == 0:
            raise serializers.ValidationError(
                {"projects": "Provide at least one project to create Land Development Registration"}
            )
        return value

    def validate(self, attrs):
        # validate for unique address between projects
        seen_addresses = []

        for project_attrs in attrs["projects"]:
            home_address_geocode_response = project_attrs.get("home_address_geocode_response")
            address_components = get_hirl_project_address_components(
                home_address_geocode=project_attrs.get("home_address_geocode"),
                home_address_geocode_response=home_address_geocode_response,
            )
            if not address_components:
                raise serializers.ValidationError({"non_field_error": "Provide project address"})
            address = (
                f'{address_components["street_line1"]}'
                f'{address_components["street_line2"]}'
                f'{address_components["city"]}'
                f'{address_components["zipcode"]}'
            )

            if address in seen_addresses:
                raise serializers.ValidationError(
                    {"non_field_error": f"Project Address: {address} is not Unique"}
                )
            else:
                seen_addresses.append(address)

            is_unique = hirl_project_address_is_unique(
                street_line1=address_components["street_line1"],
                street_line2=address_components["street_line2"],
                city=address_components["city"],
                zipcode=address_components["zipcode"],
                project_type=HIRLProjectRegistration.SINGLE_FAMILY_PROJECT_TYPE,
                project=None,
                geocode_response=home_address_geocode_response,
            )

            if not is_unique:
                raise serializers.ValidationError(
                    {"non_field_error": f"Project Address: {address} is not Unique"}
                )

        return attrs

    def create(self, validated_data):
        projects_data = validated_data.pop("projects")

        registration = HIRLProjectRegistration.objects.create(**validated_data)
        for project_data in projects_data:
            _ = HIRLProject.objects.create(
                registration=registration,
                is_require_rough_inspection=False,
                **project_data,
            )

        return registration


class CreateCommercialSpaceProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = HIRLProject
        fields = (
            "is_accessory_structure",
            "accessory_structure_description",
            "lot_number",
            "home_address_geocode",
            "home_address_geocode_response",
            "hud_disaster_case_number",
            "green_energy_badges",
            "building_number",
            "is_include_commercial_space",
            "commercial_space_type",
            "total_commercial_space",
            "is_appeals_project",
        )

    def validate(self, attrs):
        attrs["number_of_units"] = 1
        attrs["story_count"] = 1
        return attrs


class CreateMFHIRLProjectSerializer(serializers.ModelSerializer):
    """
    Serializer is using to create nested projects on Project Registration
    """

    commercial_space_parent = serializers.PrimaryKeyRelatedField(
        pk_field=HashidSerializerCharField(source_field="customer_hirl.HIRLProject.id"),
        queryset=HIRLProject.objects.all(),
        required=False,
    )
    commercial_spaces = CreateCommercialSpaceProjectSerializer(many=True, required=False)

    class Meta:
        model = HIRLProject
        fields = (
            "is_accessory_structure",
            "accessory_structure_description",
            "is_accessory_dwelling_unit",
            "accessory_dwelling_unit_description",
            "lot_number",
            "home_address_geocode",
            "home_address_geocode_response",
            "hud_disaster_case_number",
            "green_energy_badges",
            "number_of_units",
            "story_count",
            "building_number",
            "is_include_commercial_space",
            "commercial_space_type",
            "total_commercial_space",
            "commercial_spaces",
            "is_require_water_sense_certification",
            "is_require_rough_inspection",
            "is_require_wri_certification",
            "commercial_space_parent",
            "is_appeals_project",
        )
        extra_kwargs = {"number_of_units": {"default": 1}, "story_count": {"default": 1}}

    def validate(self, attrs):
        is_accessory_structure = attrs.get("is_accessory_structure")

        if is_accessory_structure:
            if not attrs.get("accessory_structure_description"):
                raise serializers.ValidationError(
                    {"accessory_structure_description": "Description is required"}
                )
        else:
            attrs["accessory_structure_description"] = ""

        is_accessory_dwelling_unit = attrs.get("is_accessory_dwelling_unit")
        if is_accessory_dwelling_unit:
            if not attrs.get("accessory_dwelling_unit_description"):
                raise serializers.ValidationError(
                    {"accessory_dwelling_unit_description": "Description is required"}
                )
        else:
            attrs["accessory_dwelling_unit_description"] = ""

        if is_accessory_structure and is_accessory_dwelling_unit:
            raise serializers.ValidationError(
                {
                    "is_accessory_dwelling_unit": "Project can be only Accessory Structure "
                    "or Accessory Dwelling Unit. Not both"
                }
            )

        is_include_commercial_space = attrs.get("is_include_commercial_space")

        if is_include_commercial_space:
            if not attrs.get("commercial_space_type"):
                raise serializers.ValidationError(
                    {"commercial_space_type": "This field is required"}
                )
            if not attrs.get("total_commercial_space"):
                raise serializers.ValidationError(
                    {"total_commercial_space": "This field is required"}
                )
        else:
            attrs["commercial_space_type"] = None
            attrs["total_commercial_space"] = None

        return attrs


class CreateMFHIRLProjectRegistrationSerializer(serializers.ModelSerializer):
    """
    Project Registration creation process include creating of new projects too
    """

    projects = CreateMFHIRLProjectSerializer(many=True)

    class Meta:
        model = HIRLProjectRegistration
        fields = (
            "eep_program",
            "project_name",
            "project_client",
            "community_named_on_certificate",
            "project_contact_first_name",
            "project_contact_last_name",
            "project_contact_email",
            "project_contact_phone_number",
            "application_packet_completion",
            "party_named_on_certificate",
            "project_description",
            "estimated_completion_date",
            "project_website_url",
            "building_will_include_non_residential_space",
            "seeking_hud_mortgage_insurance_premium_reduction",
            "seeking_fannie_mae_green_financing",
            "seeking_freddie_mac_green_financing",
            "intended_to_be_affordable_housing",
            "builder_organization",
            "builder_organization_contact",
            "developer_organization",
            "developer_organization_contact",
            "community_owner_organization",
            "community_owner_organization_contact",
            "architect_organization",
            "architect_organization_contact",
            "marketing_first_name",
            "marketing_last_name",
            "marketing_email",
            "marketing_phone",
            "sales_phone",
            "sales_email",
            "sales_website_url",
            "entity_responsible_for_payment",
            "billing_first_name",
            "billing_last_name",
            "billing_email",
            "billing_phone",
            "sampling",
            "projects",
        )

        extra_kwargs = {
            "eep_program": {"required": True},
            "project_client": {"required": True},
            "entity_responsible_for_payment": {"required": True},
            "party_named_on_certificate": {"required": True},
            "builder_organization": {"required": True},
            "builder_organization_contact": {"required": True},
        }

    def validate(self, attrs):
        entity_responsible_for_payment = attrs.get("entity_responsible_for_payment")
        builder_organization = attrs.get("builder_organization")
        developer_organization = attrs.get("developer_organization")
        architect_organization = attrs.get("architect_organization")
        community_owner_organization = attrs.get("community_owner_organization")

        if entity_responsible_for_payment == HIRLProjectRegistration.BUILDER_RESPONSIBLE_ENTITY:
            if not builder_organization:
                raise serializers.ValidationError(
                    {
                        "builder_organization": "This field is required, because you "
                        "specify Builder as Entity Responsible For Payment"
                    }
                )

        if entity_responsible_for_payment == HIRLProjectRegistration.DEVELOPER_RESPONSIBLE_ENTITY:
            if not developer_organization:
                raise serializers.ValidationError(
                    {
                        "builder_organization": "This field is required, because you "
                        "specify Developer as Entity Responsible For Payment"
                    }
                )

        if entity_responsible_for_payment == HIRLProjectRegistration.ARCHITECT_RESPONSIBLE_ENTITY:
            if not architect_organization:
                raise serializers.ValidationError(
                    {
                        "architect_organization": "This field is required, because you "
                        "specify Architect as Entity Responsible For Payment"
                    }
                )

        if (
            entity_responsible_for_payment
            == HIRLProjectRegistration.COMMUNITY_OWNER_RESPONSIBLE_ENTITY
        ):
            if not community_owner_organization:
                raise serializers.ValidationError(
                    {
                        "community_owner_organization": "This field is required, because you "
                        "specify Owner as Entity "
                        "Responsible For Payment"
                    }
                )

        # validate for unique address between projects
        seen_addresses = []

        # flatten projects to check all nested addresses for uniqueness
        projects = attrs.get("projects", [])
        flatten_projects = []
        for project in projects:
            commercial_space_projects = project.get("commercial_spaces", [])
            flatten_projects += commercial_space_projects

        flatten_projects += projects

        for project_attrs in flatten_projects:
            home_address_geocode_response = project_attrs.get("home_address_geocode_response")
            address_components = get_hirl_project_address_components(
                home_address_geocode=project_attrs.get("home_address_geocode"),
                home_address_geocode_response=home_address_geocode_response,
            )
            if not address_components:
                raise serializers.ValidationError({"non_field_error": "Provide project address"})
            address = (
                f'{address_components["street_line1"]}'
                f'{address_components["street_line2"]}'
                f'{address_components["city"]}'
                f'{address_components["zipcode"]}'
            )

            if address in seen_addresses:
                raise serializers.ValidationError(
                    {"non_field_error": f"Project Address: {address} is not Unique"}
                )
            else:
                seen_addresses.append(address)

            is_unique = hirl_project_address_is_unique(
                street_line1=address_components["street_line1"],
                street_line2=address_components["street_line2"],
                city=address_components["city"],
                zipcode=address_components["zipcode"],
                project_type=HIRLProjectRegistration.MULTI_FAMILY_PROJECT_TYPE,
                project=None,
                geocode_response=home_address_geocode_response,
            )

            if not is_unique:
                raise serializers.ValidationError(
                    {"non_field_error": f"Project Address: {address} is not Unique"}
                )

        return attrs

    def create(self, validated_data):
        projects_data = validated_data.pop("projects")
        registration = HIRLProjectRegistration.objects.create(**validated_data)
        for project_data in projects_data:
            commercial_spaces = project_data.pop("commercial_spaces", [])
            green_energy_badges = project_data.pop("green_energy_badges", [])
            project = HIRLProject.objects.create(registration=registration, **project_data)
            project.green_energy_badges.add(*green_energy_badges)

            for commercial_space_data in commercial_spaces:
                green_energy_badges = commercial_space_data.pop("green_energy_badges", [])
                commercial_space_project = HIRLProject.objects.create(
                    registration=registration,
                    commercial_space_parent=project,
                    **commercial_space_data,
                )
                commercial_space_project.green_energy_badges.add(*green_energy_badges)
        return registration


class HIRLProjectAddMFSerializer(
    CreateMFHIRLProjectRegistrationSerializer, serializers.ModelSerializer
):
    """
    Using the same logic as CreateMFHIRLProjectRegistrationSerializer,
    but accepts only existing registration id
    """

    projects = CreateMFHIRLProjectSerializer(many=True, write_only=True)

    class Meta:
        model = HIRLProject
        fields = ("projects",)

    def validate_projects(self, value):
        if len(value) == 0:
            raise serializers.ValidationError({"projects": "Provide at least one project to add"})
        return value

    def create(self, attrs):
        projects_data = attrs.pop("projects")
        projects = []
        registration = attrs["registration"]
        if registration.state in [
            HIRLProjectRegistration.REJECTED_STATE,
            HIRLProjectRegistration.ABANDONED_STATE,
        ]:
            raise serializers.ValidationError(
                {
                    "registration": f"Cannot create Project for Registration "
                    f"with {registration.get_state_display()} state"
                }
            )
        for project_data in projects_data:
            commercial_spaces = project_data.pop("commercial_spaces", [])
            green_energy_badges = project_data.pop("green_energy_badges", [])
            project = HIRLProject.objects.create(registration=registration, **project_data)
            project.green_energy_badges.add(*green_energy_badges)

            if registration.state != HIRLProjectRegistration.NEW_STATE:
                project.create_home_status()
            project.save()
            projects.append(project)

            for commercial_space_data in commercial_spaces:
                green_energy_badges = commercial_space_data.pop("green_energy_badges", [])
                commercial_space_project = HIRLProject.objects.create(
                    registration=registration,
                    commercial_space_parent=project,
                    **commercial_space_data,
                )
                commercial_space_project.green_energy_badges.add(*green_energy_badges)
                if registration.state != HIRLProjectRegistration.NEW_STATE:
                    commercial_space_project.create_home_status()

                commercial_space_project.save()
                projects.append(commercial_space_project)
        return projects


class HIRLProjectAddSFSerializer(
    CreateMFHIRLProjectRegistrationSerializer, serializers.ModelSerializer
):
    """
    Using the same logic as CreateMFHIRLProjectRegistrationSerializer,
    but accepts only existing registration id
    """

    projects = CreateSFHIRLProjectSerializer(many=True, write_only=True)

    class Meta:
        model = HIRLProject
        fields = ("projects",)

    def validate_projects(self, value):
        if len(value) == 0:
            raise serializers.ValidationError({"projects": "Provide at least one project to add"})
        return value

    def create(self, attrs):
        projects_data = attrs.pop("projects")
        projects = []
        registration = attrs["registration"]
        if registration.state in [
            HIRLProjectRegistration.REJECTED_STATE,
            HIRLProjectRegistration.ABANDONED_STATE,
        ]:
            raise serializers.ValidationError(
                {
                    "registration": f"Cannot create Project for Registration "
                    f"with {registration.get_state_display()} state"
                }
            )
        for project_data in projects_data:
            green_energy_badges = project_data.pop("green_energy_badges", [])
            project = HIRLProject.objects.create(registration=registration, **project_data)
            project.green_energy_badges.add(*green_energy_badges)

            if registration.state != HIRLProjectRegistration.NEW_STATE:
                project.create_home_status()
            project.save()
            projects.append(project)

        return projects


class AbandonHIRLProjectRegistrationSerializer(serializers.Serializer):
    reason = serializers.CharField(allow_blank=True)
    billing_state = serializers.ChoiceField(
        choices=[HIRLProject.VOID_BILLING_STATE, HIRLProject.NOT_PURSUING_BILLING_STATE],
        help_text="Set Billing state for all projects that do not have Invoice",
        default=HIRLProject.VOID_BILLING_STATE,
    )

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError

    def validate(self, attrs):
        # allowed EEPProgramHomeStatus transitions
        from_states = [
            "pending_inspection",
            "inspection",
            "qa_pending",
            "certification_pending",
            "customer_hirl_pending_project_data",
            "customer_hirl_pending_rough_qa",
            "customer_hirl_pending_final_qa",
        ]
        project = self.instance.projects.exclude(home_status__state__in=from_states).first()
        if project:
            raise serializers.ValidationError(
                {
                    "project": f"We cannot move Project {project.id} from state "
                    f"{project.home_status.get_state_display()} to state Abandoned"
                }
            )
        return attrs
