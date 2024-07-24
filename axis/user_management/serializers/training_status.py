"""equipment_sponsor_status.py: """


from django.db import transaction
from rest_framework import serializers
from axis.user_management.models import TrainingStatus, Training
from axis.user_management.states import TrainingStatusStates
from django_fsm import can_proceed
from axis.company.models import Company

__author__ = "Artem Hruzd"
__date__ = "10/31/2019 20:35"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class TrainingStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingStatus
        fields = "__all__"


class TrainingStatusChangeStateSerializer(serializers.Serializer):
    training_ids = serializers.ListField(child=serializers.IntegerField())
    new_state = serializers.ChoiceField(choices=TrainingStatusStates.choices)
    state_notes = serializers.CharField(allow_blank=True)
    company_id = serializers.IntegerField(required=False)

    @transaction.atomic
    def create(self, validated_data):
        trainings = Training.objects.filter(id__in=validated_data["training_ids"])
        user = self.context["request"].user
        if user.is_superuser:
            company = Company.objects.filter(id=validated_data.get("company_id")).first()
            if not company:
                raise serializers.ValidationError("company_id is required for superusers")
        else:
            company = user.company

        state_methods_map = {
            TrainingStatusStates.APPROVED: "approve",
            TrainingStatusStates.NEW: "new",
            TrainingStatusStates.REJECTED: "reject",
        }
        for training in trainings:
            training_status = TrainingStatus.objects.filter(
                training=training, company=company
            ).first()

            if not training_status:
                raise serializers.ValidationError(
                    "You do not have permission to change status for {}".format(company)
                )

            try:
                state_method_str = state_methods_map[validated_data["new_state"]]
                state_method = getattr(training_status, state_method_str)
                if not can_proceed(state_method):
                    raise AttributeError
            except AttributeError:
                raise serializers.ValidationError(
                    "Change state from {from_state} "
                    "to {to_state} for object {training_status} "
                    "is not allowed".format(
                        from_state=training_status.state,
                        to_state=validated_data["new_state"],
                        training_status=training_status,
                    )
                )

            state_method(user=user, state_notes=validated_data["state_notes"])
            training_status.save()

        return {
            "training_ids": validated_data["training_ids"],
            "new_state": validated_data["new_state"],
            "state_notes": validated_data["state_notes"],
        }

    def update(self, instance, validated_data):
        raise NotImplementedError
