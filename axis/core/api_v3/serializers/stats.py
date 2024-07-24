"""stats.py: """

from rest_framework import serializers


__author__ = "Rajesh Pethe"
__date__ = "08/19/2020 13:11"
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
        default=0,
        help_text="Percentage of homes that completed QA without requiring correction",
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
        default=0,
        help_text="Completed field QA percentage for the specified date range",
    )
    field_qa_count = serializers.IntegerField(
        default=0,
        help_text="Total that have had field QA completed for the specified date range",
    )
    field_qa_percentage = serializers.CharField(
        default=0,
        help_text="Completed field QA percentage for the specified date range",
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
    totals = serializers.DictField(default={}, help_text="Agregates of relevant elements in data.")
    controls = serializers.DictField(default={}, help_text="Filter controls")
    choices = serializers.DictField(
        default={}, help_text="Selectable choices for e.g. utilities, state etc."
    )

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError


class RaterMetricsSerializer(serializers.Serializer):
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
        default=0,
        help_text="Percentage of homes that completed QA without requiring correction",
    )
    completed_required_corrections_count = serializers.IntegerField(
        default=0, help_text="Homes that completed QA but DID require correction"
    )
    completed_required_corrections_percentage = serializers.CharField(
        default=0,
        help_text="Percentage of homes that completed QA but DID require correction",
    )
    completed_total_count = serializers.IntegerField(
        default=0, help_text="Total homes that have had QA completed."
    )
    completed_total_percentage = serializers.CharField(
        default=0, help_text="QA Percentage of homes for the specified date range"
    )
    pending_qa_homes_count = serializers.IntegerField(
        default=0, help_text="Total homes that have had QA pending."
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
        return super(RaterMetricsSerializer, self).to_internal_value(data)


class RaterMetricsTotals(serializers.Serializer):
    """ """

    homes_count = serializers.IntegerField(
        default=0, help_text="Total homes certified in specified date range"
    )
    in_progress_count = serializers.IntegerField(default=0, help_text="Total homes QA in progress")
    completed_first_time_count = serializers.IntegerField(
        default=0,
        help_text="Total Homes that completed QA without requiring correction",
    )
    completed_required_corrections_count = serializers.IntegerField(
        default=0, help_text="Total Homes that completed QA but DID require correction"
    )
    completed_total_count = serializers.IntegerField(
        default=0, help_text="Total homes that have had QA completed."
    )
    pending_qa_homes_count = serializers.IntegerField(
        default=0, help_text="Total homes that have had QA pending."
    )


class RaterMetricsListSerializer(serializers.Serializer):
    """
    Represents File Metrics summary data
    """

    data = serializers.ListSerializer(child=RaterMetricsSerializer())
    totals = RaterMetricsTotals()
    controls = serializers.DictField(default={}, help_text="Filter controls")
    choices = serializers.DictField(
        default={}, help_text="Selectable choices for e.g. utilities, state etc."
    )

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError


class RaterFieldMetricsListSerializer(serializers.Serializer):
    """
    Represents File Metrics summary data
    """

    data = serializers.ListSerializer(child=RaterMetricsSerializer())
    totals = RaterMetricsTotals()
    controls = serializers.DictField(default={}, help_text="Filter controls")
    choices = serializers.DictField(
        default={}, help_text="Selectable choices for e.g. utilities, state etc."
    )

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError


class MetricsProgramSuccessSerializer(serializers.Serializer):
    eep_program = serializers.CharField(help_text="EEP Program name")
    eep_program_id = serializers.IntegerField(help_text="EEP Program ID")
    success_rate = serializers.FloatField(
        default=0,
        help_text="Percentage of homes that completed QA without requiring correction",
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
    totals = serializers.DictField(default={}, help_text="Agregates of relevant elements in data.")
    controls = serializers.DictField(default={}, help_text="Filter controls")
    choices = serializers.DictField(
        default={}, help_text="Selectable choices for e.g. utilities, state etc."
    )

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError


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
        default=0,
        help_text="Number of homes with incentive payments IS pending for approval",
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
