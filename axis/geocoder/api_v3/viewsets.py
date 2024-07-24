"""viewsets.py: """
import json

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from axis.geocoder.api_v3.serializers import (
    GeocodeSerializer,
    GeocodeMatchesSerializer,
    GeocodeCityMatchesSerializer,
    GeocodeCitySerializer,
)
from axis.geocoder.models import Geocode

__author__ = "Artem Hruzd"
__date__ = "04/09/2020 16:22"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class GeocodeViewSet(viewsets.GenericViewSet):
    """
    Perform a address or city geocode using our internal geocoders
    """

    model = Geocode
    queryset = model.objects.all()

    def get_serializer_class(self):
        if self.action == "matches":
            return GeocodeSerializer
        elif self.action == "city_matches":
            return GeocodeCitySerializer

    @swagger_auto_schema(
        request_body=GeocodeMatchesSerializer,
        responses={"201": GeocodeSerializer, "200": GeocodeSerializer},
    )
    @action(
        detail=False,
        methods=[
            "post",
        ],
    )
    def matches(self, request, **kwargs):
        """Preforms a project (street_level) geocode"""
        data_serializer = GeocodeMatchesSerializer(data=request.data)
        data_serializer.is_valid(raise_exception=True)
        geocode, created = data_serializer.save(**kwargs)
        serializer = self.get_serializer_class()
        return Response(
            serializer(instance=geocode).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    @swagger_auto_schema(
        request_body=GeocodeCityMatchesSerializer,
        responses={"201": GeocodeCitySerializer, "200": GeocodeCitySerializer},
    )
    @action(
        detail=False,
        methods=[
            "post",
        ],
    )
    def city_matches(self, request, **kwargs):
        """Preforms a city geocode based on a name / county"""
        data_serializer = GeocodeCityMatchesSerializer(data=request.data)
        data_serializer.is_valid(raise_exception=True)
        geocode, created = data_serializer.save(**kwargs)
        serializer = self.get_serializer_class()
        return Response(
            serializer(instance=geocode).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )
