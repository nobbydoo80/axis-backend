"""serializers.py: """

__author__ = "Artem Hruzd"
__date__ = "11/21/2022 15:17"
__copyright__ = "Copyright 2011-2022 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.contrib.auth import get_user_model
from rest_framework import serializers

from axis.core.api_v3.serializers import UserInfoSerializer
from axis.rpc.models import RPCSession, HIRLRPCUpdaterRequest
from axis.rpc.tasks import customer_hirl_updater_rpc_session_task

User = get_user_model()


class RPCSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RPCSession
        fields = ("id",)


class HIRLRPCUpdaterRequestSerializer(serializers.ModelSerializer):
    user_info = UserInfoSerializer(source="user", read_only=True)
    result = serializers.JSONField(read_only=True)

    class Meta:
        model = HIRLRPCUpdaterRequest
        fields = (
            "id",
            "state",
            "user",
            "user_info",
            "rpc_session",
            "document",
            "result_document",
            "scoring_path",
            "project_type",
            "task_id",
            "result",
            "created_at",
        )


class HIRLRPCUpdaterRequestCreateSerializer(serializers.Serializer):
    report_file = serializers.FileField(required=True)
    scoring_path = serializers.ChoiceField(choices=HIRLRPCUpdaterRequest.SCORING_PATH_CHOICES)
    project_type = serializers.ChoiceField(choices=HIRLRPCUpdaterRequest.PROJECT_TYPE_CHOICES)

    def create(self, validated_data):
        user = validated_data["user"]
        hirl_rpc_updater_request = HIRLRPCUpdaterRequest.objects.create(
            user=user,
            document=validated_data["report_file"],
            scoring_path=validated_data["scoring_path"],
            project_type=validated_data["project_type"],
        )
        customer_hirl_updater_rpc_session_task.delay(
            hirl_rpc_updater_request_id=hirl_rpc_updater_request.id
        )
        return hirl_rpc_updater_request

    def update(self, instance, validated_data):
        pass
