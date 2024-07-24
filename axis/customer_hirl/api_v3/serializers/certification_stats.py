"""certification_stats.py - Axis"""

__author__ = "Steven K"
__date__ = "12/31/21 11:55"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from django.apps import apps
from django.db.models import QuerySet, Sum, Q, FloatField, Avg
from django.db.models.functions import Coalesce
from rest_framework import serializers

from axis.home.models import EEPProgramHomeStatus

log = logging.getLogger(__name__)
customer_hirl_app = apps.get_app_config("customer_hirl")


class CustomerHirlHomeStatusMetricsSerializer(serializers.Serializer):
    """
    Used to represent nested data in CustomerHirlMetricListSerializer
    """

    program_ids = serializers.ListSerializer(child=serializers.IntegerField())
    certified_buildings = serializers.IntegerField(default=0, help_text="Certified Building")
    certified_units = serializers.IntegerField(default=0, help_text="Certified Units")
    in_progress_buildings = serializers.IntegerField(default=0, help_text="In-Progress Building")
    in_progress_units = serializers.IntegerField(default=0, help_text="In-Progress Units")

    abandoned_buildings = serializers.IntegerField(
        default=0, help_text="Total number of abandoned buildings"
    )
    abandoned_units = serializers.IntegerField(
        default=0, help_text="Total number of abandoned units"
    )

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError


class CertificationMetricSerializer(serializers.Serializer):
    """
    Provides a breakdown of groupings for a given queryset
    """

    single_family = CustomerHirlHomeStatusMetricsSerializer()
    multi_family = CustomerHirlHomeStatusMetricsSerializer()
    multi_family_remodel = CustomerHirlHomeStatusMetricsSerializer()
    land_developments = CustomerHirlHomeStatusMetricsSerializer()
    certified_commercial_space = serializers.FloatField(default=0)
    in_progress_commercial_space = serializers.FloatField(default=0)
    certified_average_units_count = serializers.FloatField(default=0)
    in_progress_average_units_count = serializers.FloatField(default=0)
    certified_hers_score_average_count = serializers.FloatField(default=0)
    in_progress_hers_score_average_count = serializers.FloatField(default=0)

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError

    def _filter_in_progress_qs(self, qs):
        from axis.customer_hirl.models import HIRLProject

        VALID_BILLING_STATES = [
            HIRLProject.NEW_BILLING_STATE,  # Legacy 4 (new)
            HIRLProject.NEW_NOTIFIED_BILLING_STATE,
            HIRLProject.NOTICE_SENT_BILLING_STATE,  # Legacy 6 (Notice Sent)
        ]

        return qs.filter(
            Q(customer_hirl_project__billing_state__in=VALID_BILLING_STATES)
            | Q(customer_hirl_project__manual_billing_state__in=VALID_BILLING_STATES),
        ).exclude(
            state__in=[
                EEPProgramHomeStatus.COMPLETE_STATE,
                EEPProgramHomeStatus.ABANDONED_STATE,
            ]
        )

    def get_hirl_result(self, queryset) -> dict:
        certified = queryset.filter(
            state=EEPProgramHomeStatus.COMPLETE_STATE
        ).annotate_customer_hirl_unit_count()
        abandoned = queryset.filter(
            state=EEPProgramHomeStatus.ABANDONED_STATE
        ).annotate_customer_hirl_unit_count()
        in_progress = self._filter_in_progress_qs(queryset).annotate_customer_hirl_unit_count()

        lookup = {"certified": certified, "abandoned": abandoned, "in_progress": in_progress}
        data = {
            "program_ids": [],
        }

        for key, qs in lookup.items():
            values = qs.values_list("eep_program_id", flat=True)
            data["program_ids"] = list(set(data["program_ids"] + list(values)))
            data[f"{key}_buildings"] = qs.count()
            data[f"{key}_units"] = qs.aggregate(total_units=Coalesce(Sum("unit_count"), 0))[
                "total_units"
            ]
        return data

    def to_representation(self, data):
        """We accept the queryset as the instance so we can properly work with the data"""

        if data and not isinstance(data, QuerySet):
            raise TypeError(f"Expecting a queryset got {type(data)}")

        base_queryset = data.filter(
            eep_program__owner__slug=customer_hirl_app.CUSTOMER_SLUG,
        )

        data = {}

        single_family_qs = base_queryset.filter(eep_program__is_multi_family=False).exclude(
            eep_program__slug__in=customer_hirl_app.GREEN_SUBDIVISION_PROGRAMS
        )
        data["single_family"] = self.get_hirl_result(single_family_qs)

        mf_qs = base_queryset.filter(
            eep_program__is_multi_family=True,
        ).exclude(
            eep_program__slug__in=customer_hirl_app.GREEN_SUBDIVISION_PROGRAMS
            + customer_hirl_app.REMODEL_PROGRAMS
        )
        data["multi_family"] = self.get_hirl_result(mf_qs)

        mfr_qs = base_queryset.filter(
            eep_program__is_multi_family=True,
            eep_program__slug__in=customer_hirl_app.REMODEL_PROGRAMS,
        ).exclude(eep_program__slug__in=customer_hirl_app.GREEN_SUBDIVISION_PROGRAMS)
        data["multi_family_remodel"] = self.get_hirl_result(mfr_qs)

        gs_qs = base_queryset.filter(
            eep_program__slug__in=customer_hirl_app.GREEN_SUBDIVISION_PROGRAMS,
        )
        data["land_developments"] = self.get_hirl_result(gs_qs)

        data["certified_commercial_space"] = base_queryset.filter(
            state=EEPProgramHomeStatus.COMPLETE_STATE
        ).aggregate(
            total=Coalesce(
                Sum("customer_hirl_project__total_commercial_space"), 0, output_field=FloatField()
            )
        )[
            "total"
        ]

        data["in_progress_commercial_space"] = self._filter_in_progress_qs(base_queryset).aggregate(
            total=Coalesce(
                Sum("customer_hirl_project__total_commercial_space"),
                0,
                output_field=FloatField(),
            )
        )["total"]

        data["certified_average_units_count"] = (
            base_queryset.filter(state=EEPProgramHomeStatus.COMPLETE_STATE)
            .annotate_customer_hirl_unit_count()
            .aggregate(
                avg=Coalesce(
                    Avg("unit_count"),
                    0,
                    output_field=FloatField(),
                )
            )["avg"]
        )
        data["in_progress_average_units_count"] = (
            self._filter_in_progress_qs(base_queryset)
            .annotate_customer_hirl_unit_count()
            .aggregate(
                avg=Coalesce(
                    Avg("unit_count"),
                    0,
                    output_field=FloatField(),
                )
            )["avg"]
        )

        data["certified_hers_score_average_count"] = (
            base_queryset.filter(state=EEPProgramHomeStatus.COMPLETE_STATE)
            .annotate_customer_hirl_hers_score()
            .aggregate(
                avg=Coalesce(
                    Avg("hers_score"),
                    0,
                    output_field=FloatField(),
                )
            )["avg"]
        )
        data["in_progress_hers_score_average_count"] = (
            self._filter_in_progress_qs(base_queryset)
            .annotate_customer_hirl_hers_score()
            .aggregate(
                avg=Coalesce(
                    Avg("hers_score"),
                    0,
                    output_field=FloatField(),
                )
            )["avg"]
        )

        return super(CertificationMetricSerializer, self).to_representation(data)
