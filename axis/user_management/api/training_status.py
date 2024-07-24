"""control_center_base_list.py: """


from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from axis.user_management.models import TrainingStatus
from axis.user_management.serializers import (
    TrainingStatusSerializer,
    TrainingStatusChangeStateSerializer,
)

__author__ = "Artem Hruzd"
__date__ = "10/31/2019 20:23"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class TrainingStatusViewSet(viewsets.ModelViewSet):
    queryset = TrainingStatus.objects.all()
    serializer_class = TrainingStatusSerializer

    @action(detail=False, methods=["post"])
    def change_state(self, request):
        serializer = TrainingStatusChangeStateSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
