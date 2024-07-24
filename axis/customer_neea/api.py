"""api.py: Django customer_neea"""


# pylint: disable=abstract-method
import logging

from rest_framework import viewsets

from .models import LegacyNEEAHome

__author__ = "Steven Klass"
__date__ = "10/25/13 7:55 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


log = logging.getLogger(__name__)


class LegacyNEEAViewSet(viewsets.ReadOnlyModelViewSet):
    """Legacy NEEA View Set"""

    model = LegacyNEEAHome
    queryset = model.objects.all()

    def filter_queryset(self, request, queryset):
        """Filter for the user"""
        return queryset.filter_by_user(request.user)
