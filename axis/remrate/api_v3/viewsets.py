__author__ = "Rajesh Pethe"
__date__ = "07/10/2020 20:07"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = ["Steven Klass", "Rajesh Pethe", "Artem Hruzd"]

import logging

import django_auto_prefetching
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from rest_framework_extensions.mixins import NestedViewSetMixin

from axis.remrate.models import RemRateUser
from axis.remrate.api_v3.serializers import RemrateUserSerializer, NestedRemrateUserSerializer
from axis.remrate.utils import RemrateUserAccountsManager
from axis.company.api_v3.permissions import (
    RaterCompanyMemberPermission,
    ProviderCompanyMemberPermission,
)
from axis.core.api_v3.permissions import IsAdminUserOrSuperUserPermission
from .filters import RemRateUserFilter
from axis.core.api_v3.filters import AxisSearchFilter, AxisOrderingFilter, AxisFilterBackend
from axis.remrate.api_v3 import REMRATE_USER_ORDERING_FIELDS, REMRATE_USER_SEARCH_FIELDS

log = logging.getLogger(__name__)


class RemRateUserViewSet(
    viewsets.GenericViewSet,
    viewsets.mixins.RetrieveModelMixin,
    viewsets.mixins.UpdateModelMixin,
    viewsets.mixins.DestroyModelMixin,
):
    """
    retrieve:
        Get remrate user by ID


        Returns remrate user
    partial_update:
        Update one or more fields on an existing remrate user


        returns updated remrate user
    update:
        Update remrate user


        returns updated remrate user
    delete:
        Delete remrate user


        Delete remrate user
    """

    model = RemRateUser
    queryset = model.objects.all()
    permission_classes = (
        IsAdminUserOrSuperUserPermission
        | RaterCompanyMemberPermission
        | ProviderCompanyMemberPermission,
    )
    filterset_class = RemRateUserFilter
    serializer_class = RemrateUserSerializer
    filter_backends = [AxisFilterBackend, AxisSearchFilter, AxisOrderingFilter]
    search_fields = REMRATE_USER_SEARCH_FIELDS
    ordering_fields = REMRATE_USER_ORDERING_FIELDS

    def get_queryset(self):
        queryset = super(RemRateUserViewSet, self).get_queryset()
        queryset = queryset.filter_by_user(user=self.request.user)
        return django_auto_prefetching.prefetch(queryset, self.get_serializer_class())

    def perform_update(self, serializer):
        with transaction.atomic():
            serializer.save()

        self.update_db_user(serializer)
        return Response(status=status.HTTP_200_OK)

    def update_db_user(self, serializer):
        with RemrateUserAccountsManager() as manager:
            validated_data = serializer.validated_data
            username = validated_data.get("username")
            password = validated_data.get("password")
            manager.update_user_password(username, password)

    def perform_destroy(self, instance):
        instance = self.get_object()

        with transaction.atomic():
            instance.delete()

        self.delete_db_user(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def delete_db_user(self, instance):
        with RemrateUserAccountsManager() as manager:
            username = instance.username
            manager.delete_user(username)


class NestedRemRateUserViewSet(
    NestedViewSetMixin,
    viewsets.GenericViewSet,
    viewsets.mixins.CreateModelMixin,
    viewsets.mixins.ListModelMixin,
):
    """
    Nested remrate users endpoint
    list:
        Get all remrate users


        Returns all remrate users
    create:
        Create remrate users

        Create remrate user for company
    """

    model = RemRateUser
    queryset = model.objects.all()
    permission_classes = (
        IsAdminUserOrSuperUserPermission
        | RaterCompanyMemberPermission
        | ProviderCompanyMemberPermission,
    )
    filterset_class = RemRateUserFilter
    serializer_class = NestedRemrateUserSerializer
    filter_backends = [AxisFilterBackend, AxisSearchFilter, AxisOrderingFilter]
    search_fields = REMRATE_USER_SEARCH_FIELDS
    ordering_fields = REMRATE_USER_ORDERING_FIELDS

    def get_queryset(self):
        queryset = super(NestedRemRateUserViewSet, self).get_queryset()
        queryset = queryset.filter_by_user(user=self.request.user)
        return queryset

    def perform_create(self, serializer):
        company_id = self.get_parents_query_dict().get("company_id")
        r_data = self.request.data.copy()
        r_data["company"] = company_id
        serializer = self.get_serializer(data=r_data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            serializer.save()

        self.create_db_user(serializer)
        return Response(status=status.HTTP_201_CREATED)

    def create_db_user(self, serializer):
        with RemrateUserAccountsManager() as manager:
            validated_data = serializer.validated_data
            username = validated_data.get("username")
            password = validated_data.get("password")
            manager.create_new_user(username, password)
