"""simulation.py: """

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from simulation.models import Simulation
from rest_framework.decorators import action
from rest_framework.response import Response
from axis.company.api_v3.permissions import UsersCompanyOwnsObjectPermission
from drf_yasg.utils import swagger_auto_schema
from simulation.serializers.simulation.qa import SimulationSerializer

__author__ = "Rajesh Pethe"
__date__ = "12/18/2020 17:11:44"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Rajesh Pethe",
    "Steven Klass",
]


class SimulationViewSet(viewsets.GenericViewSet):
    model = Simulation
    queryset = Simulation.objects.all()
    permission_classes = (UsersCompanyOwnsObjectPermission,)

    def get_queryset(self):
        return self.queryset

    @property
    def serializer_class(self):
        return SimulationSerializer

    @swagger_auto_schema()
    @action(detail=True)
    def analyze(self, request, pk=None):
        simulation = self.get_object()
        serializer = SimulationSerializer(data={"id": simulation.id})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.to_representation(instance=simulation))
