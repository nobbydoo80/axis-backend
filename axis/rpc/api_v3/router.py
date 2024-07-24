# -*- coding: utf-8 -*-
"""router.py: """

__author__ = "Artem Hruzd"
__date__ = "11/21/2022 15:17"
__copyright__ = "Copyright 2011-2022 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from axis.rpc.api_v3.viewsets import HIRLRPCUpdaterRequestViewSet


class RPCRouter:
    @staticmethod
    def register(router):
        # qa app
        hirl_rpc_updater_request_router = router.register(
            r"hirl_rpc_updater_request", HIRLRPCUpdaterRequestViewSet, "hirl_rpc_updater_request"
        )
