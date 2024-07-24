"""washington_code_credit.py - Axis"""

__author__ = "Steven K"
__date__ = "8/5/21 13:19"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import json
import logging
from enum import Enum

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from axis.home.models import EEPProgramHomeStatus
from ..fields import EnumField
from ....calculator.washington_code_credit.calculator import WashingtonCodeCreditCalculator
from ....eep_programs.washington_code_credit import (
    BuildingEnvelope,
    HighEfficiencyHVAC,
    HighEfficiencyHVACDistribution,
    EfficientWaterHeating,
    DWHR,
    RenewableEnergy,
    Appliances,
    WACCFuelType,
    ThermostatType,
    FramingType,
    FireplaceType,
    VentilationType,
    FurnaceLocation,
    DuctLocation,
    AirLeakageControl,
    WashingtonCodeCreditProgram,
)
from ....enumerations import YesNo
from ....models import FastTrackSubmission

log = logging.getLogger(__name__)


class WashingtonCodeCreditCalculatorBaseSerializer(serializers.Serializer):
    """This is the main calculator for the Washington Code Credit"""

    # Annotations
    envelope_option = EnumField(choices=BuildingEnvelope)
    air_leakage_option = EnumField(choices=AirLeakageControl)
    hvac_option = EnumField(choices=HighEfficiencyHVAC)
    hvac_distribution_option = EnumField(choices=HighEfficiencyHVACDistribution)
    dwhr_option = EnumField(choices=DWHR)
    water_heating_option = EnumField(choices=EfficientWaterHeating)
    renewable_electric_option = EnumField(choices=RenewableEnergy)
    appliance_option = EnumField(choices=Appliances)

    # Home Data
    conditioned_floor_area = serializers.IntegerField(min_value=500, max_value=6000)
    water_heating_fuel = EnumField(choices=WACCFuelType)
    thermostat_type = EnumField(choices=ThermostatType)
    fireplace_efficiency = EnumField(choices=FireplaceType)

    # Efficient Building Envelope Options
    wall_cavity_r_value = serializers.IntegerField(min_value=0, max_value=50)
    wall_continuous_r_value = serializers.IntegerField(min_value=0, max_value=50)
    framing_type = EnumField(choices=FramingType)

    window_u_value = serializers.FloatField(min_value=0, max_value=1)
    window_shgc = serializers.FloatField(min_value=0, max_value=1, required=False)
    floor_cavity_r_value = serializers.IntegerField(default=0, min_value=0, max_value=60)
    slab_perimeter_r_value = serializers.IntegerField(default=0, min_value=0, max_value=50)
    under_slab_r_value = serializers.IntegerField(default=0, min_value=0, max_value=50)
    ceiling_r_value = serializers.IntegerField(min_value=0, max_value=80)
    raised_heel = EnumField(choices=YesNo)
    total_ua_alternative = serializers.FloatField(min_value=0, max_value=100, required=False)

    # Air Leakage Control & Efficient Ventilation Options
    air_leakage_ach = serializers.FloatField(min_value=0, max_value=10)
    ventilation_type = EnumField(choices=VentilationType)
    ventilation_brand = serializers.CharField(
        max_length=32, allow_null=True, allow_blank=True, default=None
    )
    ventilation_model = serializers.CharField(
        max_length=32,
        allow_null=True,
        allow_blank=True,
        default=None,
    )
    hrv_asre = serializers.FloatField(min_value=0, max_value=100, required=False)

    # High Efficiency HVAC Equipment Options
    furnace_brand = serializers.CharField(
        max_length=32, allow_null=True, allow_blank=True, default=None
    )
    furnace_model = serializers.CharField(
        max_length=32, allow_null=True, allow_blank=True, default=None
    )
    furnace_afue = serializers.IntegerField(min_value=10, max_value=100)

    furnace_location = EnumField(choices=FurnaceLocation)
    duct_location = EnumField(choices=DuctLocation)
    duct_leakage = serializers.IntegerField(min_value=0, max_value=100)

    # Efficient Water Heating
    dwhr_installed = EnumField(choices=YesNo)
    water_heater_brand = serializers.CharField(
        max_length=32, allow_null=True, allow_blank=True, default=None
    )
    water_heater_model = serializers.CharField(
        max_length=32, allow_null=True, allow_blank=True, default=None
    )
    gas_water_heater_uef = serializers.FloatField(min_value=0, max_value=1, required=False)
    electric_water_heater_uef = serializers.FloatField(min_value=0, max_value=5, required=False)

    # Outputs

    class Meta:
        fields = (
            # Annotations
            "envelope_option",
            "air_leakage_option",
            "hvac_option",
            "hvac_distribution_option",
            "dwhr_option",
            "water_heating_option",
            "renewable_electric_option",
            "appliance_option"
            # Checklist questions
            "conditioned_floor_area",
            "water_heating_fuel",
            "thermostat_type",
            "fireplace_efficiency",
            "wall_cavity_r_value",
            "wall_continuous_r_value",
            "framing_type",
            "window_u_value",
            "window_shgc",
            "floor_cavity_r_value",
            "slab_perimeter_r_value",
            "under_slab_r_value",
            "ceiling_r_value",
            "raised_heel",
            "total_ua_alternative",
            "air_leakage_ach",
            "ventilation_type",
            "ventilation_brand",
            "ventilation_model",
            "hrv_asre",
            "furnace_brand",
            "furnace_model",
            "furnace_afue",
            "furnace_location",
            "duct_location",
            "duct_leakage",
            "dwhr_installed",
            "water_heater_brand",
            "water_heater_model",
            "gas_water_heater_uef",
            "electric_water_heater_uef",
        )

    def get_input(self, data):
        """Swaps out the Enum internal for the actual value"""
        result = {}
        for k, v in data.items():
            if isinstance(v, Enum):
                v = v.value
            result[k] = v
        return result

    def to_internal_value(self, data):
        internal = super(WashingtonCodeCreditCalculatorBaseSerializer, self).to_internal_value(data)
        self.calculator = WashingtonCodeCreditCalculator(**internal)

        if (
            data["water_heating_fuel"] == WACCFuelType.ELECTRIC
            and data.get("electric_water_heater_uef") is None
        ):
            raise ValidationError(
                "Water Heating Fuel of {data['water_heating_fuel']} requires Electric Heater UEF"
            )
        if (
            data["water_heating_fuel"] == WACCFuelType.GAS
            and data.get("gas_water_heater_uef") is None
        ):
            raise ValidationError(
                f"Water Heating Fuel of {data['water_heating_fuel']} requires Gas Heater UEF"
            )

        result = {
            "input": self.get_input(internal),
            "summary_data": self.calculator.summary_data,
            "incentive_data": self.calculator.incentive_data,
            "incentive_report": self.calculator.incentive_report,
            "savings_data": self.calculator.savings_data,
            "specification_data": self.calculator.specification_data,
        }
        return result


class WashingtonCodeCreditCalculatorSerializer(serializers.ModelSerializer):
    """The primary method for interacting with the calculator from a home status"""

    home_status = serializers.PrimaryKeyRelatedField(queryset=EEPProgramHomeStatus.objects.all())
    reports = serializers.SerializerMethodField(read_only=True)
    is_locked = serializers.SerializerMethodField(read_only=True)
    summary = serializers.SerializerMethodField(read_only=True)

    class Meta:
        """Meta Options"""

        model = FastTrackSubmission
        fields = (
            "id",
            "home_status",
            "required_credits_to_meet_code",
            "achieved_total_credits",
            "eligible_gas_points",
            "therm_savings",
            "code_credit_incentive",
            "thermostat_incentive",
            "fireplace_incentive",
            "builder_incentive",
            "rater_incentive",
            "reports",
            "is_locked",
            "summary",
        )

    def to_internal_value(self, data):
        """Take a home status and move it to what we need on the Calculator"""

        home_status = EEPProgramHomeStatus.objects.get(id=data["home_status"])
        data = dict(home_status.annotations.all().values_list("type__slug", "content"))
        data = {k.replace("", ""): v for k, v in data.items()}
        data = {k.replace("-", "_"): v for k, v in data.items()}
        data = {k.replace("wcc_", ""): v for k, v in data.items()}

        answers = home_status.get_input_values(user_role="rater")
        collected_responses = {k.replace("wcc-", ""): value for k, value in answers.items()}

        data.update(collected_responses)
        calculator_serializer = WashingtonCodeCreditCalculatorBaseSerializer(data=data)
        calculator_serializer.is_valid(raise_exception=True)

        self.calculator = calculator_serializer.calculator
        calculator_data = calculator_serializer.validated_data["summary_data"]

        _internal = {
            "home_status": home_status.pk,
            "required_credits_to_meet_code": calculator_data["required_credits_to_meet_code"],
            "achieved_total_credits": calculator_data["achieved_total_credits"],
            "eligible_gas_points": calculator_data["eligible_gas_points"],
            "therm_savings": calculator_data["total_therm_savings"],
            "code_credit_incentive": calculator_data["code_credit_incentive"],
            "thermostat_incentive": calculator_data["thermostat_incentive"],
            "fireplace_incentive": calculator_data["fireplace_incentive"],
            "builder_incentive": calculator_data["total_builder_incentive"],
            "rater_incentive": calculator_data["verifier_incentive"],
        }
        internal = {f: _internal[f] for f in self.fields if _internal.get(f) is not None}
        return super(WashingtonCodeCreditCalculatorSerializer, self).to_internal_value(internal)

    @property
    def errors(self):
        """Represent these as the original checklist questions / annotations"""
        initial_errors = super(WashingtonCodeCreditCalculatorSerializer, self).errors
        # Transform these back to annotations / checklist questions
        expected_annotations = WashingtonCodeCreditProgram().annotations.keys()
        expected_annotations = [k.replace("-", "_") for k in expected_annotations]
        expected_annotations = [k.replace("wcc_", "") for k in expected_annotations]

        expected_measures = WashingtonCodeCreditProgram().texts["rater"].keys()
        expected_measures = [k.replace("wcc-", "") for k in expected_measures]

        errors = {}
        for k, v in initial_errors.items():
            if k in expected_annotations:
                if "annotations" not in errors:
                    errors["annotations"] = {}
                errors["annotations"][k] = v
            elif k in expected_measures:
                if "checklist_questions" not in errors:
                    errors["checklist_questions"] = {}
                errors["checklist_questions"][k] = v
            else:
                errors[k] = v
        return errors

    def update(self, instance, validated_data):
        """Respect is_locked and don't do shit if it is."""
        if instance and instance.is_locked():
            return instance

        return super(WashingtonCodeCreditCalculatorSerializer, self).update(
            instance=instance, validated_data=validated_data
        )

    def create(self, validated_data):
        instance = self.Meta.model.objects.filter(home_status=validated_data["home_status"]).first()
        if instance:
            validated_data.pop("home_status")
            return self.update(instance, validated_data)
        return super(WashingtonCodeCreditCalculatorSerializer, self).create(validated_data)

    def get_is_locked(self, instance):
        if isinstance(instance, dict):
            return None
        return instance.is_locked()

    def get_summary(self, instance):
        return self.calculator.summary_data

    def get_reports(self, instance):
        if instance and hasattr(self, "calculator"):
            return {
                "inputs": self.calculator.input_report,
                "incentives": self.calculator.incentive_report,
                "savings": self.calculator.savings_report,
                "credits": self.calculator.credit_report,
                "specifications": self.calculator.spec_report,
                "summary": self.calculator.summary_report,
                "input_dump": self.calculator.get_input_data_string(),
            }
        return {
            "inputs": None,
            "incentive": None,
            "savings": None,
            "credits": None,
            "specs": None,
            "summary": None,
            "input_dump": None,
        }
