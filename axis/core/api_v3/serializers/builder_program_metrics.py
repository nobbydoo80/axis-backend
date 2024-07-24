"""builder_program_metrics.py: """

from rest_framework import serializers
from collections import OrderedDict, defaultdict


__author__ = "Rajesh Pethe"
__date__ = "09/18/2020 19:52:14"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Rajesh Pethe",
    "Steven Klass",
]


class BuilderProgramMetricsMixin(metaclass=serializers.SerializerMetaclass):
    id = serializers.IntegerField()
    name = serializers.CharField(help_text="Program Name")
    certified_homes = serializers.IntegerField(default=0, help_text="Certified Homes")


class BuilderProgramMetricsSerializer(BuilderProgramMetricsMixin, serializers.Serializer):
    """
    Using for represent nested data in
    BuilderProgramMetricsListSerializer
    """

    incentives_paid = serializers.DecimalField(
        decimal_places=2, default=0, max_digits=16, help_text="Incentives Paid"
    )
    estimated_incentive = serializers.DecimalField(
        decimal_places=2, default=0, max_digits=16, help_text="Estimated Incentive"
    )
    energy_savings = serializers.DecimalField(
        decimal_places=2, default=0, max_digits=16, help_text="Energy Savings"
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
            data["incentives_paid"] = data["incentives_paid_raw"]
        except KeyError:
            pass
        try:
            data["estimated_incentive"] = data["stats"]["homestatus"]["outstanding_payment"]
        except KeyError:
            pass
        try:
            data["energy_savings"] = data["energy_savings_raw"]
        except KeyError:
            pass
        try:
            data["certified_homes"] = data["certifications"]
        except KeyError:
            pass

        return super(BuilderProgramMetricsSerializer, self).to_internal_value(data)


def get_dict_totals(obj):
    totals = defaultdict(int)
    try:
        for metric in obj["data"]:
            for key in metric:
                if key.endswith("_id") or key == "id":
                    continue
                try:
                    0 + metric[key]
                except:
                    continue
                totals[key] += metric[key]
    except KeyError:
        pass
    return dict(totals)


class BuilderProgramMetricsListSerializer(serializers.Serializer):
    """
    Represents Builder Program Metrics summary data
    """

    data = serializers.ListSerializer(child=BuilderProgramMetricsSerializer())
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


class HomeStatusMetricsSerializer(BuilderProgramMetricsMixin, serializers.Serializer):
    """
    Used to represent nested data in HomeStatusMetricsListSerializer
    """

    active = serializers.IntegerField(
        default=0,
        help_text="Total number of program certifications with data collection in progress",
    )
    pending_qa = serializers.IntegerField(
        default=0,
        help_text='Total homes pending for QA. Represents "Not Certified - Pending" in the grid.',
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
    totals = serializers.SerializerMethodField(default=None, help_text="Total homes NOT certified")

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError

    def get_totals(self, obj):
        total = 0
        for item in ["active", "pending_qa", "pending_inspection", "inspected", "abandoned"]:
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
            data["pending_qa"] = data["stats"]["qastatus"]["not_complete"]
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

        return super(HomeStatusMetricsSerializer, self).to_internal_value(data)


class HomeStatusMetricsListSerializer(serializers.Serializer):
    """
    Represents Builder Home Status Metrics summary data
    """

    data = serializers.ListSerializer(child=HomeStatusMetricsSerializer())
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


class PaymentStatusMetricsSerializer(BuilderProgramMetricsMixin, serializers.Serializer):
    """
    Used to represent nested data in PaymentStatusMetricsListSerializer
    """

    paid = serializers.IntegerField(default=0, help_text="")
    received = serializers.IntegerField(default=0, help_text="")
    # FIXME: Map this to correct field in data.
    correction_rquired = serializers.IntegerField(default=0, help_text="")
    correction_received = serializers.IntegerField(default=0, help_text="")
    approved_payment = serializers.IntegerField(default=0, help_text="")
    # FIXME: Map this to correct field in data.
    payment_pending = serializers.IntegerField(default=0, help_text="")
    totals = serializers.SerializerMethodField(default=None, help_text="Total of NOT paid homes")
    outstanding_payment = serializers.FloatField(
        default=0, help_text="Outstanding incentive payment"
    )

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError

    def get_totals(self, obj):
        total = 0
        for item in [
            "received",
            "correction_rquired",
            "correction_received",
            "approved_payment",
            "payment_pending",
        ]:
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
            data["paid"] = data["stats"]["incentivepaymentstatus"]["complete"]
        except KeyError:
            pass
        try:
            data["received"] = data["stats"]["incentivepaymentstatus"]["start"]
        except KeyError:
            pass
        try:
            data["correction_received"] = data["stats"]["incentivepaymentstatus"][
                "ipp_failed_restart"
            ]
        except KeyError:
            pass
        try:
            data["approved_payment"] = data["stats"]["incentivepaymentstatus"][
                "ipp_payment_automatic_requirements"
            ]
        except KeyError:
            pass
        try:
            data["outstanding_payment"] = data["stats"]["incentivepaymentstatus"][
                "outstanding_payment"
            ]
        except KeyError:
            pass

        return super(PaymentStatusMetricsSerializer, self).to_internal_value(data)


class PaymentStatusMetricsListSerializer(serializers.Serializer):
    """
    Represents Payment Status Metrics summary data
    """

    data = serializers.ListSerializer(child=PaymentStatusMetricsSerializer())
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
