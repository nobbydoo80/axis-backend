"""task.py: """
__author__ = "Artem Hruzd"
__date__ = "01/13/2020 12:48"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import serializers

from axis.core.utils import make_safe_field
from axis.scheduling.api_v3.serializers import TaskSerializer as TaskSerializerAPIV3
from axis.scheduling.models import Task

User = get_user_model()


class TaskHomeSerializer(TaskSerializerAPIV3):
    """
    Deprecated API V2 serializer
    """

    task_type_display = serializers.StringRelatedField(source="task_type", read_only=True)
    assignees_display = make_safe_field(serializers.SerializerMethodField)()
    status_display = make_safe_field(serializers.CharField)(
        source="get_status_display", read_only=True
    )
    assigner_display = serializers.SerializerMethodField()
    task_list_url = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = (
            "id",
            "task_type",
            "assignees",
            "status",
            "datetime",
            "note",
            "is_public",
            "created_at",
            "updated_at",
            "approval_state",
            "home",
            # virtual fields
            "task_type_display",
            "assignees_display",
            "status_display",
            "assigner_display",
            "task_list_url",
        )
        read_only_fields = (
            "created_at",
            "updated_at",
            "assigner",
            "approval_state",
        )

    def get_assignees_display(self, obj):
        names = [
            '<a href="{}">{}</a>'.format(
                reverse("profile:detail", kwargs={"pk": user.pk}), user.get_full_name()
            )
            for user in obj.assignees.all()
        ]
        return ", ".join(names)

    def get_assigner_display(self, obj):
        if hasattr(obj, "assigner"):
            return "{}".format(obj.assigner)
        return ""

    def get_task_list_url(self, obj):
        if obj:
            return obj.get_task_list_url()
        return ""


class TaskUserSerializer(TaskSerializerAPIV3):
    """
    Deprecated API V2 serializer
    """

    task_type_display = serializers.StringRelatedField(source="task_type", read_only=True)
    assignees_display = make_safe_field(serializers.SerializerMethodField)()
    status_display = make_safe_field(serializers.CharField)(
        source="get_status_display", read_only=True
    )
    assigner_display = serializers.SerializerMethodField()
    task_list_url = serializers.SerializerMethodField()
    # because we can't pre-popualte MTM array field on frontend
    region_assignee = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True
    )

    class Meta:
        model = Task
        fields = (
            "id",
            "task_type",
            "status",
            "datetime",
            "note",
            "is_public",
            "created_at",
            "updated_at",
            "approval_state",
            # virtual fields
            "task_type_display",
            "assignees_display",
            "status_display",
            "assigner_display",
            "task_list_url",
            "region_assignee",
        )
        read_only_fields = (
            "created_at",
            "updated_at",
            "assigner",
            "approval_state",
        )

    def get_assignees_display(self, obj):
        names = [
            '<a href="{}">{}</a>'.format(
                reverse("profile:detail", kwargs={"pk": user.pk}), user.get_full_name()
            )
            for user in obj.assignees.all()
        ]
        return ", ".join(names)

    def get_assigner_display(self, obj):
        if hasattr(obj, "assigner"):
            return "{}".format(obj.assigner)
        return ""

    def get_task_list_url(self, obj):
        if obj:
            return obj.get_task_list_url()
        return ""

    def validate(self, attrs):
        region_assignee = attrs.pop("region_assignee")
        attrs["assignees"] = [
            region_assignee,
        ]
        return attrs
