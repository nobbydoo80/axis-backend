"""zendesk.py: """

__author__ = "Artem Hruzd"
__date__ = "05/21/2021 12:11 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from axis.core.api_v3.serializers import ZendeskCreateRequestSerializer
from axis.core.api_v3.serializers.zendesk import ZendeskCreateRequestResponseSerializer


class ZendeskViewSet(viewsets.GenericViewSet):
    """
    API V3 Zendesk Support
    """

    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.action in ["request_create"]:
            return ZendeskCreateRequestSerializer
        return None

    @action(detail=False, methods=["post"])
    def request_create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        zendesk_request = serializer.create(validated_data=serializer.validated_data)

        response_serializer = ZendeskCreateRequestResponseSerializer(
            data={
                "api_url": zendesk_request["request"]["url"],
                "url": f'{settings.ZENDESK_URL}/requests/{zendesk_request["request"]["id"]}',
            }
        )
        response_serializer.is_valid(raise_exception=True)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
