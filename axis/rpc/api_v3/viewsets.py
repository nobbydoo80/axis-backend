# -*- coding: utf-8 -*-
"""viewsets.py: """

__author__ = "Artem Hruzd"
__date__ = "11/21/2022 15:17"
__copyright__ = "Copyright 2011-2022 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

import django_auto_prefetching
from rest_framework import viewsets, status
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from axis.core.api_v3.filters import AxisFilterBackend, AxisSearchFilter, AxisOrderingFilter
from axis.rpc.api_v3 import (
    RPC_SESSION_SEARCH_FIELDS,
    RPC_SESSION_ORDERING_FIELDS,
    HIRL_RPC_UPDATER_REQUEST_FILTER_FIELDS,
    HIRL_RPC_UPDATER_REQUEST_SEARCH_FIELDS,
)
from axis.rpc.api_v3.filters import RPCSessionFilter, HIRLRPCUpdaterRequestFilter
from axis.rpc.api_v3.serializers import (
    RPCSessionSerializer,
    HIRLRPCUpdaterRequestSerializer,
    HIRLRPCUpdaterRequestCreateSerializer,
)
from axis.rpc.models import RPCSession, HIRLRPCUpdaterRequest


class RPCSessionViewSet(viewsets.ModelViewSet):
    model = RPCSession
    queryset = model.objects.all()
    filterset_class = RPCSessionFilter
    serializer_class = RPCSessionSerializer
    filter_backends = [AxisFilterBackend, AxisSearchFilter, AxisOrderingFilter]
    search_fields = RPC_SESSION_SEARCH_FIELDS
    ordering_fields = RPC_SESSION_ORDERING_FIELDS

    @property
    def permission_classes(self):
        return (IsAuthenticated,)

    def get_queryset(self):
        queryset = super(RPCSessionViewSet, self).get_queryset()
        queryset = queryset.filter_by_user(user=self.request.user)
        return django_auto_prefetching.prefetch(queryset, self.get_serializer_class())


class HIRLRPCUpdaterRequestViewSet(viewsets.ModelViewSet):
    parser_classes = (MultiPartParser,)
    model = HIRLRPCUpdaterRequest
    queryset = model.objects.all()
    filterset_class = HIRLRPCUpdaterRequestFilter
    serializer_class = HIRLRPCUpdaterRequestSerializer
    filter_backends = [AxisFilterBackend, AxisSearchFilter, AxisOrderingFilter]
    search_fields = HIRL_RPC_UPDATER_REQUEST_SEARCH_FIELDS
    ordering_fields = HIRL_RPC_UPDATER_REQUEST_FILTER_FIELDS

    @property
    def permission_classes(self):
        return (IsAuthenticated,)

    def get_serializer_class(self):
        return HIRLRPCUpdaterRequestSerializer

    def get_queryset(self):
        queryset = super(HIRLRPCUpdaterRequestViewSet, self).get_queryset()
        queryset = queryset.filter_by_user(user=self.request.user)
        return django_auto_prefetching.prefetch(queryset, self.get_serializer_class())

    def create(self, request, *args, **kwargs):
        serializer = HIRLRPCUpdaterRequestCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        serializer = self.get_serializer(instance=serializer.instance)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
