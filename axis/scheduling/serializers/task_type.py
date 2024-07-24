"""task_type.py: """


from rest_framework import serializers

from axis.scheduling.models import TaskType
from django.contrib.contenttypes.models import ContentType

__author__ = "Artem Hruzd"
__date__ = "01/13/2020 12:49"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class TaskTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskType
        fields = ("name", "company", "content_type", "updated_at", "created_at")
        read_only_fields = ("created_at", "updated_at", "company", "content_type")

    def create(self, validated_data):
        model = self.context["request"].query_params["content_type"]
        validated_data["company"] = self.context["request"].user.company
        validated_data["content_type"] = ContentType.objects.get(model=model)
        return super(TaskTypeSerializer, self).create(validated_data=validated_data)
