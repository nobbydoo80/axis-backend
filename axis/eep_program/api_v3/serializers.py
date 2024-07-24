"""serializers.py: """

from rest_framework import serializers

from axis.company.api_v3.serializers import CompanyInfoSerializer
from axis.eep_program.models import EEPProgram

__author__ = "Artem Hruzd"
__date__ = "07/07/2020 13:11"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class EEPProgramInfoSerializer(serializers.ModelSerializer):
    """
    Contains only basic information about program
    """

    owner_info = CompanyInfoSerializer(source="owner", read_only=True)

    class Meta:
        model = EEPProgram
        fields = (
            "id",
            "name",
            "owner",
            "owner_info",
            "slug",
            "is_active",
            "is_legacy",
            "is_public",
            "program_start_date",
            "program_close_date",
            "program_submit_date",
            "program_end_date",
            "is_multi_family",
            "comment",
        )


class EEPProgramSerializerMixin(metaclass=serializers.SerializerMetaclass):
    owner_info = CompanyInfoSerializer(source="owner", read_only=True)


class EEPProgramMeta:
    """
    Base Meta model for EEPProgram with common fields
    """

    model = EEPProgram
    fields = (
        "id",
        "name",
        "owner",
        "owner_info",
        "slug",
        "is_active",
        "is_legacy",
        "is_public",
        "program_start_date",
        "program_close_date",
        "program_submit_date",
        "program_end_date",
        "is_multi_family",
        "comment",
        "enable_standard_disclosure",
        "require_floorplan_approval",
        "require_input_data",
        "require_rem_data",
        "require_model_file",
        "require_ekotrope_data",
        "manual_transition_on_certify",
        "require_rater_of_record",
        "require_energy_modeler",
        "require_field_inspector",
        "require_builder_relationship",
        "require_builder_assigned_to_home",
        "require_hvac_relationship",
        "require_hvac_assigned_to_home",
        "require_utility_relationship",
        "require_utility_assigned_to_home",
        "require_rater_relationship",
        "require_rater_assigned_to_home",
        "require_provider_relationship",
        "require_provider_assigned_to_home",
        "require_qa_relationship",
        "require_qa_assigned_to_home",
        "allow_sampling",
        "allow_metro_sampling",
        "require_resnet_sampling_provider",
    )
    read_only_fields = ("slug",)


class BasicEEPProgramSerializer(EEPProgramSerializerMixin, serializers.ModelSerializer):
    """Basic control of EEPProgramMeta instance"""

    class Meta(EEPProgramMeta):
        pass


class EEPProgramSerializer(EEPProgramSerializerMixin, serializers.ModelSerializer):
    """Allows full control of EEPProgramMeta instance"""

    class Meta(EEPProgramMeta):
        pass
