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


class CustomerHIRLTopVerifierStatsSerializer(serializers.Serializer):
    verifiers_by_project_count = serializers.ListSerializer(child=serializers.ListField())
    verifiers_by_unit_count = serializers.ListSerializer(child=serializers.ListField())

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError

    def to_representation(self, data):
        """We accept the queryset as the instance so we can properly work with the data"""

        if data and not isinstance(data, QuerySet):
            raise TypeError(f"Expecting a queryset got {type(data)}")

        verifiers_by_project_count = (
            data.values_list(
                "customer_hirl_project__registration__registration_user",
                "customer_hirl_project__registration__registration_user__first_name",
                "customer_hirl_project__registration__registration_user__last_name",
            )
            .annotate(projects_count=Count("id"))
            .annotate(
                verifier_first_name=F(
                    "customer_hirl_project__registration__registration_user__first_name"
                ),
                verifier_last_name=F(
                    "customer_hirl_project__registration__registration_user__last_name"
                ),
            )
            .values(
                "verifier_first_name",
                "verifier_last_name",
                "projects_count",
            )
            .order_by("-projects_count")
        )
        result = dict()
        result["verifiers_by_project_count"] = list(verifiers_by_project_count)
        verifiers_by_unit_count = (
            data.values_list(
                "customer_hirl_project__registration__registration_user",
                "customer_hirl_project__registration__registration_user__first_name",
                "customer_hirl_project__registration__registration_user__last_name",
            )
            .annotate(projects_count=Count("id"))
            .annotate(
                verifier_first_name=F(
                    "customer_hirl_project__registration__registration_user__first_name"
                ),
                verifier_last_name=F(
                    "customer_hirl_project__registration__registration_user__last_name"
                ),
                units_count=F("customer_hirl_project__number_of_units"),
            )
            .values(
                "verifier_first_name",
                "verifier_last_name",
            )
            .annotate(total_units=Coalesce(Sum("units_count"), Value(0)) + F("projects_count"))
            .order_by("-total_units")
        )
        result["verifiers_by_unit_count"] = list(verifiers_by_unit_count)
        return result
