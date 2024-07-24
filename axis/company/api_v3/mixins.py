"""mixins.py: """

__author__ = "Artem Hruzd"
__date__ = "04/07/2020 16:55"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.db.models import Count, Q
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.response import Response

from axis.company.api_v3.serializers import (
    CompanyAggregatedCountyByStateSerializer,
    CompanyUpdateCountiesByStateSerializer,
)
from axis.core.api_v3.serializers.common import BulkSelectByIdSerializer
from axis.geographic.api_v3.serializers.county import CountySerializer
from axis.geographic.models import County


class CompanyCountiesMixin(object):
    counties_serializer = CountySerializer

    @swagger_auto_schema(methods=["patch"], request_body=BulkSelectByIdSerializer)
    @action(detail=True, methods=["get", "patch"])
    def counties(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.method == "PATCH":
            serializer = BulkSelectByIdSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            counties = County.objects.filter(id__in=serializer.data["ids"])
            instance.counties.set(counties)

        serializer = self.counties_serializer(instance.counties, many=True)
        return Response(serializer.data)

    @action(
        detail=True,
        methods=[
            "get",
        ],
    )
    def aggregated_counties_by_state(self, request, *args, **kwargs):
        instance = self.get_object()
        counties_ids = instance.counties.values_list("id")

        aggregated_counties = (
            County.objects.values("state")
            .annotate(
                counties=Count("id"),
                selected_counties=Count("id", filter=Q(id__in=counties_ids)),
            )
            .order_by("state")
        )
        serializer = CompanyAggregatedCountyByStateSerializer(aggregated_counties, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(methods=["patch"], request_body=BulkSelectByIdSerializer)
    @action(
        detail=True,
        methods=[
            "patch",
        ],
    )
    def update_counties_for_state(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = CompanyUpdateCountiesByStateSerializer(instance=instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        serializer = self.counties_serializer(instance.counties, many=True)
        return Response(serializer.data)
