"""top_states_stats.py: """

__author__ = "Artem Hruzd"
__date__ = "01/10/2022 13:45"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

import itertools
import logging

from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.db.models import QuerySet, Q, Count, Subquery, OuterRef
from rest_framework import serializers

from axis.company.models import Company
from axis.home.models import Home

log = logging.getLogger(__name__)
customer_hirl_app = apps.get_app_config("customer_hirl")


class CustomerHIRLTopBuilderStatsSerializer(serializers.Serializer):
    builders_for_mf_grouped_by_unit_count = serializers.ListSerializer(
        child=serializers.ListField()
    )
    builders_for_sf_grouped_by_count = serializers.ListSerializer(child=serializers.ListField())

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError

    def to_representation(self, data):
        """We accept the queryset as the instance so we can properly work with the data"""

        if data and not isinstance(data, QuerySet):
            raise TypeError(f"Expecting a queryset got {type(data)}")

        base_queryset = data.filter(
            eep_program__owner__slug=customer_hirl_app.CUSTOMER_SLUG,
        )

        home_ct = ContentType.objects.get_for_model(Home)

        data = dict()
        # multi family
        builder_subquery = Company.objects.filter(company_type="builder").filter(
            relationships__content_type=home_ct, relationships__object_id=OuterRef("home__pk")
        )

        mf_home_statuses = (
            base_queryset.filter(eep_program__is_multi_family=True)
            .annotate_customer_hirl_unit_count()
            .annotate(
                builder_id=Subquery(builder_subquery.values("id")[:1]),
                builder_name=Subquery(builder_subquery.values("name")[:1]),
            )
            .filter(builder_id__isnull=False, builder_name__isnull=False)
            .values("id", "builder_id", "builder_name", "unit_count")
            .order_by("builder_id")
        )

        grouped_mf_builders = []

        for k, g in itertools.groupby(mf_home_statuses, lambda c: c["builder_id"]):
            t = list(g)
            total = sum([tmp["unit_count"] for tmp in t])
            if total > 0:
                grouped_mf_builders.append((t[0]["builder_name"], total))

        data["builders_for_mf_grouped_by_unit_count"] = sorted(
            grouped_mf_builders, key=lambda d: d[1], reverse=True
        )

        # single family
        home_ids = base_queryset.filter(eep_program__is_multi_family=False).values_list("home_id")

        grouped_sf_builders = (
            Company.objects.filter(company_type="builder")
            .values_list("name")
            .order_by("name")
            .annotate(
                builders_count=Count(
                    "relationships",
                    filter=Q(
                        relationships__content_type=home_ct,
                        relationships__object_id__in=home_ids,
                    ),
                )
            )
            .order_by("-builders_count")[:100]
        )
        data["builders_for_sf_grouped_by_count"] = grouped_sf_builders

        return data
