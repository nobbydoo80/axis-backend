"""eto_2022.py - Axis"""

__author__ = "Steven K"
__date__ = "3/7/22 12:32"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from rest_framework.permissions import IsAuthenticated

from drf_yasg.utils import swagger_auto_schema

from axis.customer_eto.api_v3.serializers.calculators.eps_2022 import (
    EPS2022CalculatorBaseSerializer,
    EPS2022CalculatorSerializer,
    EPS2022WACalculatorSerializer,
)
from axis.customer_eto.models import FastTrackSubmission
from axis.home.models import EEPProgramHomeStatus

log = logging.getLogger(__name__)


class ETO2022CalculatorViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)
    http_method_names = ["post", "options", "trace"]

    @swagger_auto_schema(request_body=EPS2022CalculatorBaseSerializer)
    @action(methods=["post"], detail=False, permission_classes=[IsAuthenticated])
    def calculator(self, request):
        """This is the raw calculator input"""
        serializer = EPS2022CalculatorBaseSerializer(data=request.data)

        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_201_CREATED)

        return Response(
            {
                "status": "Bad Request",
                "message": serializer.is_valid(),
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    @swagger_auto_schema(request_body=EPS2022CalculatorSerializer)
    @action(methods=["post"], detail=True, permission_classes=[IsAuthenticated])
    def generate(self, request, pk):
        """This will take a home status pk and return out the data"""
        instance = FastTrackSubmission.objects.filter(home_status_id=pk).first()

        serializer = EPS2022CalculatorSerializer(
            instance=instance,
            data={"home_status": pk},
        )

        home_status = EEPProgramHomeStatus.objects.filter(id=pk).first()
        if home_status and home_status.home.state == "WA":
            serializer = EPS2022WACalculatorSerializer(
                instance=instance,
                data={"home_status": pk},
            )

        _status = status.HTTP_201_CREATED if instance is None else status.HTTP_202_ACCEPTED

        if serializer.is_valid(raise_exception=False):
            serializer.save()
            return Response(serializer.data, status=_status)

        msg = []
        if len(serializer.errors.get("simulation", [])):
            _err = len(serializer.errors.get("simulation", []))
            msg.append(f"{_err} Simulation errors")
        if len(serializer.errors.get("checklist_questions", [])):
            _err = len(serializer.errors.get("checklist_questions", []))
            msg.append(f"{_err} checklist response errors")
        keys = [x for x in serializer.errors if x not in ["simulation", "checklist_questions"]]
        if keys:
            msg.append(f"{len(keys)} other calculator items")

        return Response(
            {
                "status": "Input Error: " + "; ".join(msg),
                "message": serializer.is_valid(),
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
