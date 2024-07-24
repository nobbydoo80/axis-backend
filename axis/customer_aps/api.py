"""api.py: customer aps"""


from rest_framework import viewsets

from axis.examine.api.restframework import ExamineViewSetAPIMixin
from axis.subdivision.models import Subdivision
from .serializers import APSHomeSerializer, APSSmartThermostatSerializer
from .models import APSHome

__author__ = "Autumn Valenta"
__date__ = "1/08/15 10:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]


class APSHomeViewSet(ExamineViewSetAPIMixin, viewsets.ModelViewSet):
    model = APSHome
    queryset = model.objects.all()
    serializer_class = APSHomeSerializer

    def get_examine_machinery_class(self, raise_exception=True):
        from axis.home.views.machineries import APSHomeExamineMachinery

        return APSHomeExamineMachinery


class APSSmartThermostatOptionViewSet(ExamineViewSetAPIMixin, viewsets.ModelViewSet):
    """APS Smart Thermostat Option API"""

    model = Subdivision
    queryset = model.objects.all()
    serializer_class = APSSmartThermostatSerializer

    def get_examine_machinery_class(self, raise_exception=True):
        """Get Machinery Class"""
        from axis.customer_aps.views.examine import APSSmartThermostatOptionsMachinery

        return APSSmartThermostatOptionsMachinery
