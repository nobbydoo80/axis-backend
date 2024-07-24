"""frontend_logger.py"""

from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from axis.core.api_v3.serializers import FrontendLogSerializer

__author__ = "Rajesh Pethe"
__date__ = "30/06/2020 15:17"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = ["Rajesh Pethe", "Steven Klass"]


class FrontendLoggerViewSet(viewsets.GenericViewSet, viewsets.mixins.CreateModelMixin):
    """
    Using to logging critical and unexpected behaviour

    create:
        Log unexpected behaviour or exception


        Create log record and notify all developers
    """

    permission_classes = [
        AllowAny,
    ]
    serializer_class = FrontendLogSerializer
