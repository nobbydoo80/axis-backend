__author__ = "Artem Hruzd"
__date__ = "04/03/2020 19:44"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.db import transaction
from django.apps import apps
from rest_framework import serializers
from axis.company.api_v3.serializers import CompanyInfoSerializer
from axis.company.models import Company
from axis.core.api_v3.serializers import UserInfoSerializer
from axis.eep_program.models import EEPProgram
from .equipment_sponsor_status import EquipmentSponsorStatusInfoSerializer
from axis.equipment.models import Equipment, EquipmentSponsorStatus

equipment_app = apps.get_app_config("equipment")


class EquipmentSerializer(serializers.ModelSerializer):
    """Basic control of Equipment instance."""

    owner_company_info = CompanyInfoSerializer(read_only=True, source="owner_company")
    assignees_info = UserInfoSerializer(read_only=True, many=True, source="assignees")
    equipment_sponsor_statuses_info = EquipmentSponsorStatusInfoSerializer(
        read_only=True, many=True, source="equipmentsponsorstatus_set"
    )

    class Meta:
        model = Equipment
        fields = (
            "id",
            "owner_company",
            "owner_company_info",
            "equipment_type",
            "brand",
            "equipment_model",
            "serial",
            "description",
            "calibration_date",
            "calibration_cycle",
            "calibration_company",
            "assignees",
            "assignees_info",
            "notes",
            "expired_equipment",
            "equipment_sponsor_statuses_info",
            "calibration_documentation",
            "updated_at",
            "created_at",
        )
        read_only_fields = ("expired_equipment",)
        extra_kwargs = {"assignees": {"allow_empty": True}}

    @transaction.atomic
    def create(self, validated_data):
        instance = super(EquipmentSerializer, self).create(validated_data)
        owner_company = instance.owner_company
        user = self.context["request"].user

        for (
            applicable_company_slug,
            applicable_programs,
        ) in equipment_app.EQUIPMENT_APPLICABLE_REQUIREMENTS.items():
            program = (
                EEPProgram.objects.filter_by_company(owner_company)
                .filter(slug__in=applicable_programs)
                .first()
            )
            if program:
                equipment_sponsor_status = EquipmentSponsorStatus(
                    equipment=instance, company=Company.objects.get(slug=applicable_company_slug)
                )
                equipment_sponsor_status.save()

                if user and (
                    user.company.company_type == Company.PROVIDER_COMPANY_TYPE
                    or user.company == program.owner
                ):
                    equipment_sponsor_status.active(user=user)
                    equipment_sponsor_status.save()

        return instance
