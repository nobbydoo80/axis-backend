"""certification_stats.py - Axis"""

__author__ = "Steven K"
__date__ = "12/31/21 11:55"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from django.apps import apps
from django.db.models import QuerySet, Sum, FloatField, Avg, IntegerField
from django.db.models.functions import Coalesce
from rest_framework import serializers
from axis.customer_hirl.models.project_registration import HIRLProjectRegistration

log = logging.getLogger(__name__)
customer_hirl_app = apps.get_app_config("customer_hirl")


class HIRLAggregateDashboardSerializer(serializers.Serializer):
    buildings_count = serializers.IntegerField(default=0)
    unit_count_and_project_count = serializers.IntegerField(default=0)
    total_commercial_space = serializers.FloatField(default=0)
    average_units = serializers.FloatField(default=0)
    hers_score_is_not_null_count = serializers.IntegerField(default=0)
    average_hers_score = serializers.FloatField(default=0)

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError

    def to_representation(self, queryset):
        if queryset and not isinstance(queryset, QuerySet):
            raise TypeError(f"Expecting a queryset got {type(queryset)}")

        data = {}
        data["buildings_count"] = queryset.count()
        sf_buildings_count = queryset.filter(
            customer_hirl_project__registration__project_type=HIRLProjectRegistration.SINGLE_FAMILY_PROJECT_TYPE
        ).count()
        data["unit_count_and_project_count"] = (
            queryset.aggregate(total=Coalesce(Sum("unit_count"), 0, output_field=IntegerField()))[
                "total"
            ]
            + sf_buildings_count
        )
        data["total_commercial_space"] = queryset.aggregate(
            total=Coalesce(
                Sum("customer_hirl_project__total_commercial_space"), 0, output_field=FloatField()
            )
        )["total"]

        data["average_units"] = queryset.aggregate(
            avg=Coalesce(
                Avg("unit_count"),
                0,
                output_field=FloatField(),
            )
        )["avg"]

        return super(HIRLAggregateDashboardSerializer, self).to_representation(data)
