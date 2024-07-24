"""program_metrics.py: """

from rest_framework import serializers

__author__ = "Rajesh Pethe"
__date__ = "09/18/2020 19:14:15"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Rajesh Pethe",
    "Steven Klass",
]


class ProgramMetricsSerializer(serializers.Serializer):
    """
    Using for represent nested data in EEPProgramHomeStatusProgramMetricsSerializer
    """

    id = serializers.IntegerField()
    name = serializers.CharField()
    total = serializers.IntegerField(
        default=0, help_text="Total number of homes certified in specified date range"
    )
    file_first_time_count = serializers.IntegerField(
        default=0, help_text="Homes that completed QA without requiring correction"
    )
    file_first_time_percentage = serializers.CharField(
        default=0, help_text="Percentage of homes that completed QA without requiring correction"
    )
    file_qa_count = serializers.IntegerField(
        default=0, help_text="Total that have had QA completed the specified date range"
    )
    file_qa_percentage = serializers.CharField(
        default=0, help_text="Completed QA percentage for the specified date range"
    )
    field_first_time_count = serializers.IntegerField(
        default=0, help_text="Completed field QA without requiring correction"
    )
    field_first_time_percentage = serializers.CharField(
        default=0, help_text="Completed field QA percentage for the specified date range"
    )
    field_qa_count = serializers.IntegerField(
        default=0, help_text="Total that have had field QA completed for the specified date range"
    )
    field_qa_percentage = serializers.CharField(
        default=0, help_text="Completed field QA percentage for the specified date range"
    )

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError

    def to_internal_value(self, data):
        try:
            data["id"] = data["eep_program_id"]
        except KeyError:
            pass
        try:
            data["name"] = data["eep_program_name"]
        except KeyError:
            pass
        try:
            data["total"] = data["total_count"]
        except KeyError:
            pass
        return super(ProgramMetricsSerializer, self).to_internal_value(data)


class ProgramMetricsListSerializer(serializers.Serializer):
    """
    Represents Builder Program Metrics summary data
    """

    data = serializers.ListSerializer(child=ProgramMetricsSerializer())
    controls = serializers.DictField(default={}, help_text="Filter controls")
    choices = serializers.DictField(
        default={}, help_text="Selectable choices for e.g. utilities, state etc."
    )

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError
