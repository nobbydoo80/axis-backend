"""frontend_log.py: """

import logging

from rest_framework import serializers

logger = logging.getLogger(__name__)

__author__ = "Artem Hruzd"
__date__ = "11/23/2020 13:04"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class FrontendLogSerializer(serializers.Serializer):
    level = serializers.ChoiceField(choices=logging._nameToLevel)
    msg = serializers.CharField(allow_blank=True)
    extra = serializers.DictField()

    def create(self, validated_data):
        request = self.context["request"]
        user = None
        msg = validated_data["msg"]
        extra = validated_data["extra"]
        if request and hasattr(request, "user"):
            user = request.user

        logger.log(
            level=logging._nameToLevel[validated_data["level"]],
            msg=f"Frontend message: User {user} Message: {msg} Extra: {extra}",
        )
        return validated_data

    def update(self, instance, validated_data):
        raise NotImplementedError
