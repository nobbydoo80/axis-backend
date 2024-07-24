"""rater_metrics.py: """

from rest_framework import serializers
from axis.core.utils import get_dict_totals


__author__ = "Rajesh Pethe"
__date__ = "09/18/2020 19:11:17"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Rajesh Pethe",
    "Steven Klass",
]


class QAMetricsSerializerMixin(metaclass=serializers.SerializerMetaclass):
    """
    Describing data returned by stats-rater_file_mertics
    {
        "homes_count": 9,
        "in_progress_count": 0,
        "completed_first_time_count": 2,
        "completed_first_time_percentage": "40.00%",
        "completed_required_corrections_count": 3,
        "completed_required_corrections_percentage": "60.00%",
        "completed_total_count": 5,
        "completed_total_percentage": "55.56%",
        "grouped_id": 1044,
        "grouped_name": "Central Electric Cooperative",
        "pending_qa_homes_count": 7
    }
    """

    id = serializers.IntegerField()
    name = serializers.CharField()
    homes_count = serializers.IntegerField(
        default=0, help_text="Total homes certified in specified date range"
    )
    completed_first_time_count = serializers.IntegerField(
        default=0, help_text="Homes that completed QA without requiring correction"
    )
    completed_first_time_percentage = serializers.CharField(
        default=0, help_text="Percentage of homes that completed QA without requiring correction"
    )
    completed_required_corrections_count = serializers.IntegerField(
        default=0, help_text="Homes that completed QA but DID require correction"
    )
    completed_required_corrections_percentage = serializers.CharField(
        default=0, help_text="Percentage of homes that completed QA but DID require correction"
    )
    completed_total_count = serializers.IntegerField(
        default=0, help_text="Total homes that have had QA completed."
    )
    completed_total_percentage = serializers.CharField(
        default=0, help_text="QA Percentage of homes for the specified date range"
    )

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError

    def to_internal_value(self, data):
        try:
            data["id"] = data["grouped_id"]
        except KeyError:
            pass
        try:
            data["name"] = data["grouped_name"]
        except KeyError:
            pass
        return super(QAMetricsSerializerMixin, self).to_internal_value(data)


class FileAndFieldMetricsSerializer(QAMetricsSerializerMixin, serializers.Serializer):
    """
    File and Field metrics, a member of QAMetricsListSerializer.
    Represent File and Field QA Metrics.
    """

    pending_qa_homes_count = serializers.IntegerField(
        default=0, help_text="Homes that entered QA in the specified date range"
    )

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError


class QAMetricsListSerializer(serializers.Serializer):
    data = serializers.ListSerializer(child=FileAndFieldMetricsSerializer())
    totals = serializers.SerializerMethodField(
        default={}, help_text="Dictionary representing totals of relevant items in data."
    )
    controls = serializers.DictField(default={}, help_text="Filter controls")
    choices = serializers.DictField(
        default={}, help_text="Selectable choices for e.g. utilities, state etc."
    )

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError

    def get_totals(self, obj):
        return get_dict_totals(obj)


class NeeaFileAndFieldMetricsSerializer(QAMetricsSerializerMixin, serializers.Serializer):
    """
    NEEA File and Field serializer, represents data in NeeaFileAndFieldMetricsListSerializer
    """

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError


class NeeaFileAndFieldMetricsListSerializer(serializers.Serializer):
    """
    Represents File Metrics summary data
    """

    data = serializers.ListSerializer(child=NeeaFileAndFieldMetricsSerializer())
    totals = serializers.SerializerMethodField(
        default={}, help_text="Dictionary representing totals of relevant items in data."
    )
    controls = serializers.DictField(default={}, help_text="Filter controls")
    choices = serializers.DictField(
        default={}, help_text="Selectable choices for e.g. utilities, state etc."
    )

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError

    def get_totals(self, obj):
        return get_dict_totals(obj)

    def get_style_parameter(self):
        return "rater"
