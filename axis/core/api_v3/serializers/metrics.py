"""metrics.py: """


from rest_framework import serializers


__author__ = "Rajesh Pethe"
__date__ = "09/18/2020 19:21:49"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Rajesh Pethe",
    "Steven Klass",
]


class StatsResponseSerializer(serializers.Serializer):
    body = serializers.ListField(default=[])
    sidebars = serializers.DictField(default={})


class MetricsProgramSuccessSerializer(serializers.Serializer):
    eep_program = serializers.CharField(help_text="EEP Program name")
    eep_program_id = serializers.IntegerField(help_text="EEP Program ID")
    success_rate = serializers.FloatField(
        default=0, help_text="Percentage of homes that completed QA without requiring correction"
    )
    total_qa = serializers.IntegerField(
        default=0, help_text="Total homes that have had QA completed."
    )
    correction_required = serializers.IntegerField(
        default=0, help_text="Homes that DID require correction"
    )
    corrected_percentage = serializers.FloatField(
        default=0.0, help_text="Percentage of QA that needed correction"
    )
    failed_percentage = serializers.FloatField(
        default=0.0, help_text="Percentage of QA that failed"
    )

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError


class MetricProgramFailureByTypeSerializer(serializers.Serializer):
    type_id = serializers.IntegerField(default=0, help_text="QA status observation ID")
    type = serializers.CharField(help_text="QA status observation type")
    count = serializers.IntegerField(default=0, help_text="Total failures under this observation")

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError


class MetricProgramSuccessByRaterSerializer(serializers.Serializer):
    ror_id = serializers.IntegerField(default=0, help_text="Rater of record (user) ID")
    ror_first_name = serializers.CharField(help_text="Rater or record first name")
    ror_last_name = serializers.CharField(help_text="Rater or record last name")
    total_qa = serializers.IntegerField(default=0, help_text="Total QA done by this rater")
    success_rate = serializers.FloatField(
        default=0.0, help_text="Percentage os QA passed without needing corrections."
    )
    correction_required = serializers.IntegerField(
        default=0, help_text="Total Number of corrections required"
    )
    corrected_percentage = serializers.FloatField(
        default=0.0, help_text="Percentage of QA that needed correction"
    )
    failed_percentage = serializers.FloatField(
        default=0.0, help_text="Percentage of QA that failed"
    )

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError


class MetricsProgramListSerializer(serializers.Serializer):
    success_by_program = serializers.ListSerializer(
        child=MetricsProgramSuccessSerializer(),
        help_text="""
            Success metrics, grouped by program.
            Fields `success_rate`, `corrected_percentage` and `failed_percentage`
            can be used to graphically represent success of programs.
        """,
    )
    failures_by_type = serializers.ListSerializer(
        child=MetricProgramFailureByTypeSerializer(), help_text="QA failure metrics"
    )
    success_by_rater_user = serializers.ListSerializer(
        child=MetricProgramSuccessByRaterSerializer(),
        help_text="Success metrics, by individual raters",
    )

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError


class MetricsListSerializer(serializers.Serializer):
    """
    Represents QA Metrics data
    """

    data = serializers.ListSerializer(child=MetricsProgramListSerializer())
    controls = serializers.DictField(default={}, help_text="Filter controls")
    choices = serializers.DictField(
        default={}, help_text="Selectable choices for e.g. utilities, state etc."
    )

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError
