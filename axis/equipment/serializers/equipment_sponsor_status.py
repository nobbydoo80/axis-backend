"""equipment_sponsor_status.py: """


from django.db import transaction
from rest_framework import serializers
from ..models import EquipmentSponsorStatus, Equipment
from ..states import EquipmentSponsorStatusStates
from django_fsm import can_proceed
from axis.company.models import Company

__author__ = "Artem Hruzd"
__date__ = "10/31/2019 20:35"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class EquipmentSponsorStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = EquipmentSponsorStatus
        fields = "__all__"


class EquipmentSponsorStatusChangeStateSerializer(serializers.Serializer):
    equipment_ids = serializers.ListField(child=serializers.IntegerField())
    new_state = serializers.ChoiceField(choices=EquipmentSponsorStatusStates.choices)
    state_notes = serializers.CharField(allow_blank=True)
    company_id = serializers.IntegerField(required=False)

    @transaction.atomic
    def create(self, validated_data):
        equipments = Equipment.objects.filter(id__in=validated_data["equipment_ids"])
        user = self.context["request"].user
        if user.is_superuser:
            company = Company.objects.filter(id=validated_data.get("company_id")).first()
            if not company:
                raise serializers.ValidationError("company_id is required for superusers")
        else:
            company = user.company

        state_methods_map = {
            EquipmentSponsorStatusStates.ACTIVE: "active",
            EquipmentSponsorStatusStates.NEW: "new",
            EquipmentSponsorStatusStates.REJECTED: "reject",
            EquipmentSponsorStatusStates.EXPIRED: "expire",
        }
        for equipment in equipments:
            equipment_sponsor_status = EquipmentSponsorStatus.objects.filter(
                equipment=equipment, company=company
            ).first()

            if not equipment_sponsor_status:
                raise serializers.ValidationError(
                    "You do not have permission to change status for {}".format(equipment)
                )

            try:
                state_method_str = state_methods_map[validated_data["new_state"]]
                state_method = getattr(equipment_sponsor_status, state_method_str)
                if not can_proceed(state_method):
                    raise AttributeError
            except AttributeError:
                raise serializers.ValidationError(
                    "Change state from {from_state} "
                    "to {to_state} for object {equipment} "
                    "is not allowed".format(
                        from_state=equipment_sponsor_status.state,
                        to_state=validated_data["new_state"],
                        equipment=equipment,
                    )
                )

            state_method(user=user, state_notes=validated_data["state_notes"])
            equipment_sponsor_status.save()

        return {
            "equipment_ids": validated_data["equipment_ids"],
            "new_state": validated_data["new_state"],
            "state_notes": validated_data["state_notes"],
        }

    def update(self, instance, validated_data):
        raise NotImplementedError
