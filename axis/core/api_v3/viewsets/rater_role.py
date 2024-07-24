"""viewset.py: """

__author__ = "Artem Hruzd"
__date__ = "05/11/2022 16:53"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

import logging

from django.apps import apps
from django.contrib.auth import get_user_model
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from axis.core.api_v3 import RATER_ROLE_SEARCH_FIELDS, RATER_ROLE_ORDERING_FIELDS
from axis.core.api_v3.filters import (
    AxisSearchFilter,
    AxisOrderingFilter,
    AxisFilterBackend,
    RaterRoleFilter,
)
from axis.core.api_v3.serializers import RaterRoleSerializer
from axis.core.models import RaterRole

User = get_user_model()
log = logging.getLogger(__name__)
customer_hirl_app = apps.get_app_config("customer_hirl")


class RaterRoleViewSet(
    viewsets.mixins.RetrieveModelMixin,
    viewsets.mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = (IsAuthenticated,)
    model = RaterRole
    filterset_class = RaterRoleFilter
    serializer_class = RaterRoleSerializer
    queryset = model.objects.all()
    filter_backends = [AxisFilterBackend, AxisSearchFilter, AxisOrderingFilter]
    search_fields = RATER_ROLE_SEARCH_FIELDS
    ordering_fields = RATER_ROLE_ORDERING_FIELDS
