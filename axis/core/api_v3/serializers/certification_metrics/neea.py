"""certification_metrics.py: """

from rest_framework import serializers
from axis.core.api_v3.serializers.builder_program_metrics import BuilderProgramMetricsMixin


__author__ = "Rajesh Pethe"
__date__ = "08/19/2020 13:11"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Rajesh Pethe",
    "Steven Klass",
]


class NEEACertificationsMetricsSerializer(serializers.Serializer):
    """
    Represents Utility Certification metrics from NEEA
    """

    id = serializers.IntegerField()
    name = serializers.CharField(help_text="Program name")
    total = serializers.IntegerField(default=0, help_text="Total certified homes")
    savings_kwh = serializers.FloatField(default=0.0, help_text="Total energy savings in KWH")
    savings_therms = serializers.FloatField(default=0.0, help_text="Total thermal emission savings")
    approved_payments = serializers.IntegerField(
        default=0, help_text="Number of homes with incentive payments approved"
    )
    pending_payments = serializers.IntegerField(
        default=0, help_text="Number of homes with incentive payments IS pending for approval"
    )
    approved_dollars = serializers.FloatField(
        default=0.0, help_text="Total incentive amount approved in dollars"
    )
    pending_dollars = serializers.FloatField(
        default=0.0, help_text="Incentive amount in dollars that pending aproval"
    )

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError

    def to_internal_value(self, data):
        try:
            data["id"] = data["eep_program__id"]
        except KeyError:
            pass
        try:
            data["name"] = data["eep_program__name"]
        except KeyError:
            pass
        try:
            data["total"] = data["n"]
        except KeyError:
            pass
        try:
            data["savings_kwh"] = data["stats"]["savings_kwh"]
        except KeyError:
            pass
        try:
            data["savings_therms"] = data["stats"]["savings_therms"]
        except KeyError:
            pass
        try:
            data["approved_payments"] = data["stats"]["approved_payments"]
        except KeyError:
            pass
        try:
            data["pending_payments"] = data["stats"]["pending_payments"]
        except KeyError:
            pass
        try:
            data["approved_dollars"] = data["stats"]["approved_dollars"]
        except KeyError:
            pass
        try:
            data["pending_dollars"] = data["stats"]["pending_dollars"]
        except KeyError:
            pass
        return super(NEEACertificationsMetricsSerializer, self).to_internal_value(data)


class NEEACertificationsMetricsListSerializer(serializers.Serializer):
    """
    Represents Utility Certification metrics LIST from NEEA
    """

    data = serializers.ListSerializer(child=NEEACertificationsMetricsSerializer())
    totals = serializers.DictField(default={}, help_text="Totals of relevant items in data.")
    controls = serializers.DictField(default={}, help_text="Filter controls")
    choices = serializers.DictField(
        default={}, help_text="Selectable choices for e.g. utilities, state etc."
    )

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError


class NEEAHomeStatusMetricsSerializer(BuilderProgramMetricsMixin, serializers.Serializer):
    """
    Used to represent nested data in NEEAHomeStatusMetricsListSerializer
    """

    active = serializers.IntegerField(
        default=0,
        help_text="Total number of program certifications with data collection in progress",
    )
    pending_inspection = serializers.IntegerField(
        default=0, help_text="Total number of program certifications pending for inspection"
    )
    inspected = serializers.IntegerField(
        default=0, help_text="Total number of program certifications with data collection completed"
    )
    abandoned = serializers.IntegerField(
        default=0, help_text="Total number of abandoned program certifications"
    )
    qa_pending = serializers.IntegerField(default=0, help_text="For back-end use only")
    totals = serializers.SerializerMethodField(default=None, help_text="Total homes NOT certified")

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError

    def get_totals(self, obj):
        total = 0
        for item in ["active", "pending_inspection", "inspected", "abandoned", "qa_pending"]:
            total += obj[item]
        return total

    def to_internal_value(self, data):
        try:
            data["id"] = data["eep_program__id"]
        except KeyError:
            pass
        try:
            data["name"] = data["eep_program__name"]
        except KeyError:
            pass
        try:
            data["certified_homes"] = data["stats"]["homestatus"]["complete"]
        except KeyError:
            pass
        try:
            data["active"] = data["stats"]["homestatus"]["inspection"]
        except KeyError:
            pass
        try:
            data["pending_inspection"] = data["stats"]["homestatus"]["pending_inspection"]
        except KeyError:
            pass
        try:
            data["inspected"] = data["stats"]["homestatus"]["certification_pending"]
        except KeyError:
            pass
        try:
            data["abandoned"] = data["stats"]["homestatus"]["abandoned"]
        except KeyError:
            pass
        try:
            data["qa_pending"] = data["stats"]["homestatus"]["qa_pending"]
        except KeyError:
            pass

        return super(NEEAHomeStatusMetricsSerializer, self).to_internal_value(data)


class NEEAHomeStatusMetricsListSerializer(serializers.Serializer):
    """
    Used to represent nested data in NEEA Homes NOT Certified Grid
    """

    data = serializers.ListSerializer(child=NEEAHomeStatusMetricsSerializer())
    controls = serializers.DictField(default={}, help_text="Filter controls")
    choices = serializers.DictField(
        default={}, help_text="Selectable choices for e.g. utilities, state etc."
    )

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError

    def to_representation(self, value):
        """Filters out metrics with zero certifications."""
        metrics = value["data"]
        metrics[:] = [i for i in metrics if self.is_valid_metric(i)]

        return super(NEEAHomeStatusMetricsListSerializer, self).to_representation(value)

    def is_valid_metric(self, metric):
        """Retruns True if atleast one home was tried for certification."""
        total = 0
        for item in ["active", "pending_inspection", "inspected", "abandoned", "qa_pending"]:
            total += metric[item]
        if total != 0:
            return True
        return False
