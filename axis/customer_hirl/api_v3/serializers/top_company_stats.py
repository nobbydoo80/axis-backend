__author__ = "Naruhito Kaide"
__date__ = "01/10/2022 13:45"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = ["Naruhito Kaide"]

import itertools
import logging

from django.apps import apps
from django.db.models import QuerySet, Q, Count, F, Sum, Value
from django.db.models.functions import Coalesce
from rest_framework import serializers

log = logging.getLogger(__name__)
customer_hirl_app = apps.get_app_config("customer_hirl")


class CustomerHIRLTopCompanyStatsSerializer(serializers.Serializer):
    companies_by_project_count = serializers.ListSerializer(child=serializers.ListField())
    companies_by_unit_count = serializers.ListSerializer(child=serializers.ListField())

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError

    def to_representation(self, data):
        """We accept the queryset as the instance so we can properly work with the data"""

        if data and not isinstance(data, QuerySet):
            raise TypeError(f"Expecting a queryset got {type(data)}")

        companies_by_project_count = (
            data.values_list(
                "customer_hirl_project__registration__registration_user__company",
                "customer_hirl_project__registration__registration_user__company__name",
            )
            .annotate(projects_count=Count("id"))
            .annotate(
                company_name=F(
                    "customer_hirl_project__registration__registration_user__company__name"
                ),
            )
            .values(
                "company_name",
                "projects_count",
            )
            .order_by("-projects_count")
        )
        result = dict()
        result["companies_by_project_count"] = list(companies_by_project_count)
        companies_by_unit_count = (
            data.annotate_customer_hirl_unit_count()
            .values_list(
                "customer_hirl_project__registration__registration_user__company",
                "customer_hirl_project__registration__registration_user__company__name",
            )
            .annotate(projects_count=Count("id"))
            .annotate(
                company_name=F(
                    "customer_hirl_project__registration__registration_user__company__name"
                ),
                units_count=F("customer_hirl_project__number_of_units"),
            )
            .values("company_name")
            .annotate(total_units=Coalesce(Sum("units_count"), 0) + F("projects_count"))
            .order_by("-total_units")
        )
        result["companies_by_unit_count"] = list(companies_by_unit_count)
        return result
