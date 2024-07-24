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
from django.db.models import QuerySet, Q, Count
from rest_framework import serializers

from axis.geographic.models import County

log = logging.getLogger(__name__)
customer_hirl_app = apps.get_app_config("customer_hirl")


class CustomerHIRLTopStatesStatsSerializer(serializers.Serializer):
    states_for_mf_grouped_by_unit_count = serializers.ListSerializer(child=serializers.ListField())
    states_for_sf_grouped_by_count = serializers.ListSerializer(child=serializers.ListField())

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

        data = dict()

        mf_counties = (
            base_queryset.filter(eep_program__is_multi_family=True)
            .annotate_customer_hirl_unit_count()
            .values("id", "home__city__county__state", "unit_count")
            .order_by("home__city__county__state")
        )

        grouped_mf_counties = []

        for k, g in itertools.groupby(mf_counties, lambda c: c["home__city__county__state"]):
            t = list(g)
            total = sum([tmp["unit_count"] for tmp in t])

            grouped_mf_counties.append((k, total))

        data["states_for_mf_grouped_by_unit_count"] = sorted(
            grouped_mf_counties, key=lambda d: d[1], reverse=True
        )

        grouped_sf_counties = list(
            County.objects.all()
            .values_list("state")
            .order_by("state")
            .annotate(
                home_status_count=Count(
                    "home__homestatuses",
                    filter=Q(
                        home__homestatuses__id__in=base_queryset.filter(
                            eep_program__is_multi_family=False
                        ),
                    ),
                )
            )
            .order_by("-home_status_count", "state")
        )
        data["states_for_sf_grouped_by_count"] = grouped_sf_counties

        return data
