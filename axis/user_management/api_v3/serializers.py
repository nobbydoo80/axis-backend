"""serializers.py: """

__author__ = "Artem Hruzd"
__date__ = "11/19/2021 7:31 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from rest_framework import serializers

from axis.core.api_v3.serializers import (
    UserInfoSerializer,
    ContentTypeRelatedField,
    ContentTypeInfoSerializer,
)
from axis.qa.api_v3.serializers import QAStatusInfoSerializer
from axis.user_management.models import Accreditation, InspectionGrade


class AccreditationSerializerMixin(metaclass=serializers.SerializerMetaclass):
    trainee_info = UserInfoSerializer(source="trainee", read_only=True)
    approver_info = UserInfoSerializer(source="approver", read_only=True)


class AccreditationSerializer(AccreditationSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Accreditation
        fields = (
            "id",
            "trainee",
            "trainee_info",
            "name",
            "accreditation_id",
            "role",
            "state",
            "state_changed_at",
            "approver",
            "approver_info",
            "accreditation_cycle",
            "date_initial",
            "date_last",
            "manual_expiration_date",
            "updated_at",
            "created_at",
        )


class AccreditationInfoSerializer(AccreditationSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Accreditation
        fields = (
            "id",
            "name",
            "accreditation_id",
            "role",
            "state",
            "state_changed_at",
            "updated_at",
            "created_at",
        )


class InspectionGradeSerializerMixin(metaclass=serializers.SerializerMetaclass):
    user_info = UserInfoSerializer(source="user", read_only=True)
    approver_info = UserInfoSerializer(source="approver", read_only=True)
    qa_status_info = QAStatusInfoSerializer(source="qa_status", read_only=True)


class InspectionGradeMeta:
    model = InspectionGrade
    fields = (
        "id",
        "user",
        "user_info",
        "approver",
        "approver_info",
        "graded_date",
        "numeric_grade",
        "letter_grade",
        "qa_status",
        "qa_status_info",
        "notes",
        "qa_status",
        "updated_at",
        "created_at",
    )


class CustomerHIRLInspectionGradeListSerializer(serializers.ModelSerializer):
    user_fullname = serializers.SerializerMethodField()
    user_company = serializers.ReadOnlyField(source="user.company.id")
    user_company_name = serializers.ReadOnlyField(source="user.company.name")
    user_company_type = serializers.ReadOnlyField(source="user.company.company_type")
    qa_type = serializers.ReadOnlyField(source="qa_status.requirement.type")
    eep_program_name = serializers.ReadOnlyField(source="qa_status.home_status.eep_program.name")
    home_id = serializers.ReadOnlyField(source="qa_status.home_status.home.id")
    home_address = serializers.SerializerMethodField()

    class Meta:
        model = InspectionGrade
        fields = (
            "id",
            "user",
            "user_fullname",
            "user_company",
            "user_company_name",
            "user_company_type",
            "qa_type",
            "eep_program_name",
            "graded_date",
            "numeric_grade",
            "letter_grade",
            "home_id",
            "home_address",
            "notes",
            "qa_status",
            "updated_at",
            "created_at",
        )

    def get_user_fullname(self, inspection_grade):
        return f"{inspection_grade.user.first_name} {inspection_grade.user.last_name}"

    def get_home_address(self, inspection_grade):
        qa_status = getattr(inspection_grade, "qa_status", None)
        if qa_status:
            home_status = getattr(qa_status, "home_status", None)
            if home_status:
                return home_status.home.get_home_address_display()
        return ""


class InspectionGradeSerializer(InspectionGradeSerializerMixin, serializers.ModelSerializer):
    class Meta(InspectionGradeMeta):
        pass


class InspectionGradeAggregateByLetterGradeSerializer(serializers.Serializer):
    a_grade = serializers.IntegerField(default=0)
    b_grade = serializers.IntegerField(default=0)
    c_grade = serializers.IntegerField(default=0)
    d_grade = serializers.IntegerField(default=0)
    f_grade = serializers.IntegerField(default=0)

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError
