__author__ = "Artem Hruzd"
__date__ = "03/16/2020 23:41"
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

from axis.core.api_v3.filters import AxisSearchFilter, AxisOrderingFilter, AxisFilterBackend
from axis.customer_eto.api_v3.filters import ETOAccountFilter
from axis.customer_eto.api_v3.serializers import ETOAccountSerializer
from axis.customer_eto.models import ETOAccount

log = logging.getLogger(__name__)
User = get_user_model()
customer_hirl_app = apps.get_app_config("customer_hirl")
customer_eto_app = apps.get_app_config("customer_eto")


class ETOAccountViewSet(viewsets.ModelViewSet):
    model = ETOAccount
    queryset = model.objects.all()
    filterset_class = ETOAccountFilter
    serializer_class = ETOAccountSerializer
    filter_backends = [AxisFilterBackend, AxisSearchFilter, AxisOrderingFilter]
    search_fields = [
        "company__id",
        "company__name",
        "account_number",
        "ccb_number",
    ]
    ordering_fields = ["id", "company__id", "account_number", "ccb_number"]

    @property
    def permission_classes(self):
        return (IsAuthenticated,)

    def get_queryset(self):
        qs = super(ETOAccountViewSet, self).get_queryset()
        return qs.filter_by_user(user=self.request.user)
