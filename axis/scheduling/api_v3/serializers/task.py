"""task.py: """

__author__ = "Artem Hruzd"
__date__ = "10/10/2022 20:01"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from typing import List

from django.apps import apps
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from django_fsm import can_proceed
from rest_framework import serializers
from axis.scheduling.messages import (
    TaskCreatedMessage,
    TaskRejectedMessage,
    TaskChangedStatusMessage,
)

from axis.core.api_v3.serializers import UserInfoSerializer
from axis.home.api_v3.serializers import HomeInfoSerializer
from axis.scheduling.messages import TaskApprovedMessage
from axis.scheduling.models import Task

frontend_app = apps.get_app_config("frontend")

User = get_user_model()


class TaskSerializer(serializers.ModelSerializer):
    assignees_info = UserInfoSerializer(source="assignees", many=True, read_only=True)
    assigner_info = UserInfoSerializer(source="assigner", read_only=True)
    home_info = HomeInfoSerializer(source="home", read_only=True)

    class Meta:
        model = Task
        fields = (
            "id",
            "assignees",
            "assignees_info",
            "note",
            "approval_state",
            "datetime",
            "status",
            "home_info",
            "assigner_info",
            "created_at",
        )

    def create(self, validated_data):
        task = super(TaskSerializer, self).create(validated_data)
        # because we are using this serializer in api v2
        # send notifications here, instead of viewset perform_create method to DRY
        url = f"/{frontend_app.DEPLOY_URL}scheduling/tasks"
        users = (
            User.objects.filter(
                company__id__in=task.assignees.values_list("company_id"),
                is_company_admin=True,
            )
            | task.assignees.all()
        ).distinct()
        TaskCreatedMessage(url=url).send(
            users=users,
            context={
                "dashboard_url": url,
                "url": task.get_task_list_url(),
                "task_id": task.id,
                "assigner_profile_url": task.assigner.get_absolute_url(),
                "assigner": task.assigner,
            },
        )
        return task


class TaskFlatListSerializer(serializers.ModelSerializer):
    assignees_info = UserInfoSerializer(source="assignees", many=True, read_only=True)
    task_type_name = serializers.ReadOnlyField(source="task_type.name")
    assigner_info = UserInfoSerializer(source="assigner", read_only=True)
    approver_info = UserInfoSerializer(source="approver", read_only=True)
    status_approver_info = UserInfoSerializer(source="status_approver", read_only=True)
    home_info = HomeInfoSerializer(source="home", read_only=True)

    class Meta:
        model = Task
        fields = (
            "id",
            "assignees",
            "assignees_info",
            "task_type_name",
            "note",
            "approver_info",
            "approval_state",
            "approval_annotation",
            "approval_state_changed_at",
            "datetime",
            "status",
            "status_approver",
            "status_approver_info",
            "status_changed_at",
            "status_annotation",
            "home_info",
            "assigner",
            "assigner_info",
            "created_at",
        )


class TaskChangeStateSerializer(serializers.Serializer):
    task_ids = serializers.ListField(child=serializers.IntegerField(), default=[])
    new_state = serializers.ChoiceField(choices=Task.APPROVAL_STATE_CHOICES)
    approval_annotation = serializers.CharField(allow_blank=True)

    def get_tasks(self, task_ids: List[int]):
        tasks = Task.objects.filter(id__in=task_ids)
        user = self.context["request"].user
        if not user.is_superuser:
            if user.is_company_admin:
                tasks = tasks.filter(assignees__company=user.company)
            else:
                tasks = tasks.filter(assignees=user)
        return tasks

    def validate(self, attrs):
        tasks = self.get_tasks(task_ids=attrs["task_ids"])

        for task in tasks:
            try:
                state_method_str = Task.STATE_METHODS_MAP[attrs["new_state"]]
                state_method = getattr(task, state_method_str)
                if not can_proceed(state_method):
                    raise AttributeError
            except AttributeError:
                raise serializers.ValidationError(
                    {
                        "state": "Change state from {from_state} "
                        "to {to_state} for {task} "
                        "is not allowed".format(
                            from_state=task.approval_state,
                            to_state=attrs["new_state"],
                            task=task,
                        )
                    }
                )
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        tasks = self.get_tasks(task_ids=validated_data["task_ids"])

        for task in tasks:
            state_method_str = Task.STATE_METHODS_MAP[validated_data["new_state"]]
            state_method = getattr(task, state_method_str)
            state_method(
                user=self.context["request"].user,
                approval_annotation=validated_data["approval_annotation"],
            )
            task.save()
            url = f"/{frontend_app.DEPLOY_URL}scheduling/tasks"

            users = (
                User.objects.filter(
                    Q(
                        company__id__in=task.assignees.values_list("company_id"),
                        is_company_admin=True,
                    )
                    | Q(id=task.assigner_id)
                    | Q(id=task.approver_id)
                )
                | task.assignees.all()
            ).distinct()
            base_context = {
                "url": url,
                "task_id": task.id,
                "approver_user": task.approver,
                "approver_user_profile_url": task.approver.get_absolute_url(),
                "assignee_links_list": ", ".join(
                    [
                        f'<a href="{assignee.get_absolute_url()}">{assignee}</a>'
                        for assignee in task.assignees.all()
                    ]
                ),
            }

            if validated_data["new_state"] == Task.APPROVAL_STATE_APPROVED:
                TaskApprovedMessage(url=url).send(
                    users=users,
                    context=base_context,
                )

            if validated_data["new_state"] == Task.APPROVAL_STATE_REJECTED:
                context = dict(base_context)
                context["reason"] = task.approval_annotation

                TaskRejectedMessage(url=url).send(
                    users=users,
                    context=context,
                )

        return {
            "task_ids": validated_data["task_ids"],
            "new_state": validated_data["new_state"],
            "approval_annotation": validated_data["approval_annotation"],
        }

    def update(self, instance, validated_data):
        raise NotImplementedError


class TaskChangeStatusSerializer(serializers.Serializer):
    task_ids = serializers.ListField(child=serializers.IntegerField())
    new_status = serializers.ChoiceField(choices=Task.TASK_STATUS_CHOICES)
    status_annotation = serializers.CharField(required=False, allow_blank=True)

    def get_tasks(self, task_ids: List[int]):
        tasks = Task.objects.filter(id__in=task_ids)
        user = self.context["request"].user
        if not user.is_superuser:
            if user.is_company_admin:
                tasks = tasks.filter(
                    Q(assignees__company=user.company) | Q(assigner__company=user.company)
                )
            else:
                tasks = tasks.filter(assignees=user | Q(assigner__company=user.company))
        return tasks

    def validate(self, attrs):
        tasks = self.get_tasks(task_ids=attrs["task_ids"])

        for task in tasks:
            if task.approval_state == Task.APPROVAL_STATE_NEW:
                raise serializers.ValidationError(
                    {"status": f"Change status for {task} with New state is not allowed"}
                )
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        tasks = self.get_tasks(task_ids=validated_data["task_ids"])
        user = self.context["request"].user
        status_annotation = validated_data.get("status_annotation", "")

        for task in tasks:
            task.status = validated_data["new_status"]
            task.status_approver = user
            task.status_annotation = status_annotation
            task.status_changed_at = timezone.now()
            task.save()

            url = f"/{frontend_app.DEPLOY_URL}scheduling/tasks"

            users = (
                User.objects.filter(
                    Q(
                        company__id__in=task.assignees.values_list("company_id"),
                        is_company_admin=True,
                    )
                    | Q(id=task.assigner_id)
                    | Q(id=task.approver_id)
                )
                | task.assignees.all()
            ).distinct()
            base_context = {
                "url": url,
                "task_id": task.id,
                "new_status": task.get_status_display(),
                "status_approver_user": task.approver,
                "status_approver_user_profile_url": task.approver.get_absolute_url(),
                "assignee_links_list": ", ".join(
                    [
                        f'<a href="{assignee.get_absolute_url()}">{assignee}</a>'
                        for assignee in task.assignees.all()
                    ]
                ),
            }

            TaskChangedStatusMessage(url=url).send(
                users=users,
                context=base_context,
            )

        return {
            "task_ids": validated_data["task_ids"],
            "new_status": validated_data["new_status"],
            "status_annotation": status_annotation,
        }

    def update(self, instance, validated_data):
        raise NotImplementedError


class TaskExportToCalSerializer(serializers.Serializer):
    task_ids = serializers.ListField(child=serializers.IntegerField())

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError
