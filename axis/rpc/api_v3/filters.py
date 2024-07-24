# -*- coding: utf-8 -*-
"""filters.py: """

__author__ = "Artem Hruzd"
__date__ = "11/21/2022 15:25"
__copyright__ = "Copyright 2011-2022 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from axis.rpc.api_v3 import RPC_SESSION_FILTER_FIELDS, HIRL_RPC_UPDATER_REQUEST_FILTER_FIELDS
from axis.rpc.models import RPCSession, HIRLRPCUpdaterRequest
from django_filters import rest_framework as filters


class RPCSessionFilter(filters.FilterSet):
    class Meta:
        model = RPCSession
        fields = RPC_SESSION_FILTER_FIELDS


class HIRLRPCUpdaterRequestFilter(filters.FilterSet):
    class Meta:
        model = HIRLRPCUpdaterRequest
        fields = HIRL_RPC_UPDATER_REQUEST_FILTER_FIELDS
