"""green_energy_badge.py: """

__author__ = "Artem Hruzd"
__date__ = "04/22/2021 17:02"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from axis.core.api_v3.filters import AxisSearchFilter, AxisOrderingFilter, AxisFilterBackend
from axis.customer_hirl.api_v3 import (
    HIRL_GREEN_EENERGY_BADGE_SEARCH_FIELDS,
    HIRL_GREEN_EENERGY_BADGE_ORDERING_FIELDS,
)
from axis.customer_hirl.api_v3.filters import HIRLGreenEnergyBadgeFilter
from axis.customer_hirl.api_v3.serializers import HIRLGreenEnergyBadgeSerializer
from axis.customer_hirl.models import HIRLGreenEnergyBadge


class HIRLGreenEnergyBadgeViewSet(viewsets.ReadOnlyModelViewSet):
    model = HIRLGreenEnergyBadge
    permission_classes = (IsAuthenticated,)
    queryset = model.objects.all()
    filter_class = HIRLGreenEnergyBadgeFilter
    serializer_class = HIRLGreenEnergyBadgeSerializer
    filter_backends = [AxisFilterBackend, AxisSearchFilter, AxisOrderingFilter]
    search_fields = HIRL_GREEN_EENERGY_BADGE_SEARCH_FIELDS
    ordering_fields = HIRL_GREEN_EENERGY_BADGE_ORDERING_FIELDS
