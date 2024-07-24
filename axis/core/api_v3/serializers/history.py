"""history.py: """


from rest_framework import serializers
from axis.core.api_v3.serializers import UserInfoSerializer

__author__ = "Artem Hruzd"
__date__ = "03/19/2020 18:20"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class HistoryChangesDiffSerializer(serializers.Serializer):
    field_name = serializers.CharField()
    old = serializers.CharField()
    new = serializers.CharField()

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError


class HistorySerializer(serializers.Serializer):
    history_id = serializers.IntegerField()
    history_datetime = serializers.DateTimeField()
    history_type = serializers.CharField()
    history_user = serializers.IntegerField(allow_null=True)
    history_user_info = UserInfoSerializer(allow_null=True)
    changes = HistoryChangesDiffSerializer(many=True)

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError
