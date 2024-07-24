"""serializers.py: """
__author__ = "Artem Hruzd"
__date__ = "07/16/2020 20:48"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from rest_framework import serializers

from axis.annotation.api_v3.serializers import AnnotationInfoSerializer
from axis.company.api_v3.serializers import CompanyInfoSerializer
from axis.core.api_v3.serializers import UserInfoSerializer
from axis.eep_program.api_v3.serializers import EEPProgramInfoSerializer
from axis.home.api_v3.serializers import EEPProgramHomeStatusInfoSerializer, HomeInfoSerializer
from axis.home.api_v3.serializers.eep_program_home_status import EEPProgramHomeStatusMeta
from axis.home.models import EEPProgramHomeStatus
from axis.qa.models import QAStatus, Observation, ObservationType, QARequirement, QANote

User = get_user_model()


class QARequirementInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = QARequirement
        fields = ("id", "type", "qa_company")


class QAEEPProgramHomeStatusInfoSerializer(EEPProgramHomeStatusInfoSerializer):
    class Meta(EEPProgramHomeStatusMeta):
        pass


class QAStatusSerializerMixin(metaclass=serializers.SerializerMetaclass):
    home_status_info = QAEEPProgramHomeStatusInfoSerializer(source="home_status", read_only=True)
    requirement_info = QARequirementInfoSerializer(source="requirement", read_only=True)


class QAStatusMeta:
    """
    Base Meta model for QAStatus with common fields
    """

    model = QAStatus
    fields = ("id", "home_status", "home_status_info", "requirement", "requirement_info")


class QAStatusInfoSerializer(QAStatusSerializerMixin, serializers.ModelSerializer):
    class Meta(QAStatusMeta):
        pass


class BasicQAStatusSerializer(QAStatusSerializerMixin, serializers.ModelSerializer):
    """Basic control of EEPProgramHomeStatus instance."""

    class Meta(QAStatusMeta):
        pass


class QAStatusSerializer(QAStatusSerializerMixin, serializers.ModelSerializer):
    """Allows full control of QAStatus instance."""

    class Meta(QAStatusMeta):
        pass


class HIRLQAStatusListEEPProgramHomeStatusInfoSerializer(serializers.ModelSerializer):
    eep_program_info = EEPProgramInfoSerializer(source="eep_program")
    home_info = HomeInfoSerializer(source="home")

    class Meta:
        model = EEPProgramHomeStatus
        fields = (
            "id",
            "state",
            "eep_program",
            "eep_program_info",
            "home",
            "home_info",
        )


class HIRLQAStatusListSerializer(serializers.ModelSerializer):
    """
    Optimized list for customer_hirl_list endpoint
    """

    home_status_info = HIRLQAStatusListEEPProgramHomeStatusInfoSerializer(
        source="home_status", read_only=True
    )
    requirement_info = QARequirementInfoSerializer(source="requirement", read_only=True)
    verifier_id = serializers.ReadOnlyField()
    verifier_name = serializers.ReadOnlyField()
    state_cycle_time_total_duration = serializers.SerializerMethodField()
    home_status_notes = serializers.SerializerMethodField()

    class Meta:
        model = QAStatus
        fields = (
            "id",
            "state",
            "home_status",
            "home_status_info",
            "requirement",
            "requirement_info",
            "verifier_id",
            "verifier_name",
            "state_cycle_time_total_duration",
            "home_status_notes",
        )

    def get_state_cycle_time_total_duration(self, qa_status: QAStatus) -> float:
        return qa_status.state_cycle_time_duration

    def get_home_status_notes(self, qa_status: QAStatus):
        annotations = qa_status.home_status.annotations.all()
        return AnnotationInfoSerializer(annotations, many=True).data


class HIRLQAStatusUserFilterBadgesCountSerializer(serializers.Serializer):
    all_projects = serializers.IntegerField(default=0)
    my_projects = serializers.IntegerField(default=0)
    rough_qa_projects = serializers.IntegerField(default=0)
    final_qa_projects = serializers.IntegerField(default=0)
    desktop_audit_projects = serializers.IntegerField(default=0)
    qa_correction_received_projects = serializers.IntegerField(default=0)
    qa_correction_required_projects = serializers.IntegerField(default=0)

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError


class ObservationTypeInfoSerializer(serializers.ModelSerializer):
    company_info = CompanyInfoSerializer(source="company", read_only=True)

    class Meta:
        model = ObservationType
        fields = ("id", "name", "company", "company_info", "last_update", "created_on")


class ObservationSerializerMixin(metaclass=serializers.SerializerMetaclass):
    qa_status_info = QAStatusInfoSerializer(source="qa_status", read_only=True)
    user_info = UserInfoSerializer(source="user", read_only=True)
    observation_type_info = ObservationTypeInfoSerializer(source="observation_type", read_only=True)


class ObservationMeta:
    model = Observation
    fields = (
        "qa_status",
        "qa_status_info",
        "observation_type",
        "observation_type_info",
        "qa_note",
        "user",
        "user_info",
        "last_update",
        "created_on",
    )


class ObservationSerializer(ObservationSerializerMixin, serializers.ModelSerializer):
    class Meta(ObservationMeta):
        pass


class QANoteSerializer(serializers.ModelSerializer):
    user_info = UserInfoSerializer(source="user", read_only=True)
    qa_status_info = QAStatusInfoSerializer(source="qa_status", read_only=True)

    class Meta:
        model = QANote
        fields = (
            "id",
            "user",
            "user_info",
            "qa_status",
            "qa_status_info",
            "note",
            "last_update",
            "created_on",
        )


class QANoteListSerializer(serializers.ModelSerializer):
    user_name = serializers.ReadOnlyField(source="user.get_full_name")
    observation_names = serializers.SerializerMethodField()

    class Meta:
        model = QANote
        fields = (
            "id",
            "user_name",
            "note",
            "observation_names",
            "last_update",
        )

    def get_observation_names(self, qa_note):
        return qa_note.observation_set.all().values_list("observation_type__name", flat=True)


class CreateQANoteForMultipleQAStatusesSerializer(serializers.Serializer):
    qa_statuses = serializers.PrimaryKeyRelatedField(queryset=QAStatus.objects.all(), many=True)
    note = serializers.CharField(required=True)

    def create(self, validated_data):
        notes = []
        qa_content_type = ContentType.objects.get_for_model(QAStatus)
        with transaction.atomic():
            for qa_status in validated_data["qa_statuses"]:
                note = QANote.objects.create(
                    qa_status=qa_status,
                    user=self.context["request"].user,
                    note=validated_data["note"],
                    content_type=qa_content_type,
                    object_id=qa_status.id,
                )
                notes.append(note)
        return notes

    def update(self, instance, validated_data):
        raise NotImplementedError
