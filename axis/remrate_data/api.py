"""api.py: remrate data"""


from rest_framework.viewsets import ModelViewSet

from .models import Simulation, DESIGN_MODELS

__author__ = "Autumn Valenta"
__date__ = "5/27/13 10:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]


class SimulationViewSet(ModelViewSet):
    model = Simulation
    queryset = model.objects.all()

    def filter_queryset(self, queryset):
        return queryset.filter_by_user(self.request.user)


class UnattachedSimulationViewSet(SimulationViewSet):
    def filter_queryset(self, queryset):
        queryset = queryset.filter_by_user(self.request.user)
        return queryset.filter(
            floorplan__isnull=True, export_type__in=[1] + DESIGN_MODELS
        ).order_by("-id")
