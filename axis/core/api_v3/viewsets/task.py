"""task.py - axis"""

__author__ = "Steven K"
__date__ = "3/14/23 10:58"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from axis.core.api_v3.serializers import CeleryAsyncResultSerializer

log = logging.getLogger(__name__)


class CeleryTaskViewSet(viewsets.GenericViewSet):
    """
    API V3 Generic Celery Task Result
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = CeleryAsyncResultSerializer
    lookup_field = "uuid"

    def get_serializer_class(self):
        if self.action in ["status"]:
            return CeleryAsyncResultSerializer
        return None

    @action(detail=True, methods=["get"])
    def status(self, request, *args, **kwargs):
        serializer = self.get_serializer(data={"task_id": kwargs.get("uuid")})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
