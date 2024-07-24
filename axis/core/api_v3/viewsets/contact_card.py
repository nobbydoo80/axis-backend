__author__ = "Artem Hruzd"
__date__ = "05/11/2021 23:15"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

import logging

import django_auto_prefetching
from django.contrib.auth import get_user_model
from rest_framework import viewsets
from rest_framework_extensions.mixins import NestedViewSetMixin

from axis.core.api_v3.filters import (
    ContactCardFilter,
    AxisFilterBackend,
    AxisSearchFilter,
    AxisOrderingFilter,
)
from axis.core.api_v3.serializers import ContactCardSerializer
from axis.core.models import ContactCard

User = get_user_model()
log = logging.getLogger(__name__)

CONTACT_CARD_SEARCH_FIELDS = ["first_name", "last_name", "title", "phones__phone", "emails__email"]


class ContactCardViewSet(viewsets.ModelViewSet):
    model = ContactCard
    queryset = ContactCard.objects.all()
    serializer_class = ContactCardSerializer
    filterset_class = ContactCardFilter
    filter_backends = [AxisFilterBackend, AxisSearchFilter, AxisOrderingFilter]
    search_fields = CONTACT_CARD_SEARCH_FIELDS

    def get_queryset(self):
        queryset = super(ContactCardViewSet, self).get_queryset()
        queryset = queryset.prefetch_related("emails", "phones")
        return django_auto_prefetching.prefetch(queryset, self.get_serializer_class())


class NestedCompanyContactCardViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    model = ContactCard
    queryset = ContactCard.objects.all()
    serializer_class = ContactCardSerializer
    filterset_class = ContactCardFilter
    filter_backends = [AxisFilterBackend, AxisSearchFilter, AxisOrderingFilter]
    search_fields = CONTACT_CARD_SEARCH_FIELDS

    def perform_create(self, serializer):
        serializer.save(company_id=self.get_parents_query_dict().get("company_id"))
