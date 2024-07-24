"""washington_code_credit.py - Axis"""

__author__ = "Steven K"
__date__ = "8/10/21 08:23"
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

from axis.customer_eto.models import FastTrackSubmission
from ...serializers.calculators.washington_code_credit import (
    WashingtonCodeCreditCalculatorBaseSerializer,
    WashingtonCodeCreditCalculatorSerializer,
)

log = logging.getLogger(__name__)


class WashingtonCodeCreditCalculatorViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)
    http_method_names = ["post", "options", "trace"]

    @swagger_auto_schema(request_body=WashingtonCodeCreditCalculatorBaseSerializer)
    @action(methods=["post"], detail=False, permission_classes=[IsAuthenticated])
    def calculator(self, request):
        """This is the raw calculator input"""
        serializer = WashingtonCodeCreditCalculatorBaseSerializer(data=request.data)

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

    @swagger_auto_schema(request_body=WashingtonCodeCreditCalculatorSerializer)
    @action(methods=["post"], detail=True, permission_classes=[IsAuthenticated])
    def generate(self, request, pk):
        """This will take a home status pk and return out the data"""
        instance = FastTrackSubmission.objects.filter(home_status_id=pk).first()

        serializer = WashingtonCodeCreditCalculatorSerializer(
            instance=instance,
            data={"home_status": pk},
        )

        _status = status.HTTP_201_CREATED if instance is None else status.HTTP_202_ACCEPTED

        if serializer.is_valid(raise_exception=False):
            serializer.save()
            return Response(serializer.data, status=_status)

        msg = []
        if len(serializer.errors.get("annotations", [])):
            _err = len(serializer.errors.get("annotations", []))
            msg.append(f"{_err} annotation errors")
        if len(serializer.errors.get("checklist_questions", [])):
            _err = len(serializer.errors.get("checklist_questions", []))
            msg.append(f"{_err} checklist response errors")
        keys = [x for x in serializer.errors if x not in ["annotations", "checklist_questions"]]
        if keys:
            msg.append(f"{len(keys)} other items")

        return Response(
            {
                "status": "Input Error: " + "; ".join(msg),
                "message": serializer.is_valid(),
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
