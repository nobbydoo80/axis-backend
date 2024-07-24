"""eps_base.py - Axis"""

__author__ = "Steven K"
__date__ = "12/1/21 15:00"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
from collections import defaultdict
from enum import Enum

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from axis.customer_eto.api_v3.serializers.fields import EnumField
from axis.customer_eto.enumerations import (
    PNWUSStates,
    ClimateLocation,
    PrimaryHeatingEquipment2020,
    ElectricUtility,
    GasUtility,
    Fireplace2020,
    GridHarmonization2020,
    AdditionalIncentives2020,
    SmartThermostatBrands2020,
    SolarElements2020,
)
from axis.customer_eto.models import FastTrackSubmission
from axis.home.models import EEPProgramHomeStatus

log = logging.getLogger(__name__)


class CalculatorBaseSerializer(serializers.Serializer):
    """This is main calculator for ETO"""

    # Regular Stuff
    us_state = EnumField(choices=PNWUSStates)
    climate_location = EnumField(choices=ClimateLocation)
    primary_heating_class = EnumField(choices=PrimaryHeatingEquipment2020)

    conditioned_area = serializers.IntegerField(min_value=50, max_value=15000)

    electric_utility = EnumField(choices=ElectricUtility, default=ElectricUtility.NONE)
    gas_utility = EnumField(choices=GasUtility, default=GasUtility.NONE)

    thermostat_brand = EnumField(
        choices=SmartThermostatBrands2020, default=SmartThermostatBrands2020.NONE
    )
    fireplace = EnumField(choices=Fireplace2020, default=Fireplace2020.NONE)
    grid_harmonization_elements = EnumField(
        choices=GridHarmonization2020, default=GridHarmonization2020.NONE
    )
    eps_additional_incentives = EnumField(
        choices=AdditionalIncentives2020, default=AdditionalIncentives2020.NO
    )
    solar_elements = EnumField(choices=SolarElements2020, default=SolarElements2020.NONE)
    code_heating_therms = serializers.FloatField(default=0.0)
    code_heating_kwh = serializers.FloatField(default=0.0)
    code_cooling_kwh = serializers.FloatField(default=0.0)
    code_hot_water_therms = serializers.FloatField(default=0.0)
    code_hot_water_kwh = serializers.FloatField(default=0.0)
    code_lights_and_appliance_therms = serializers.FloatField(default=0.0)
    code_lights_and_appliance_kwh = serializers.FloatField(default=0.0)
    code_electric_cost = serializers.FloatField(default=0.0)
    code_gas_cost = serializers.FloatField(default=0.0)
    improved_heating_therms = serializers.FloatField(default=0.0)
    improved_heating_kwh = serializers.FloatField(default=0.0)
    improved_cooling_kwh = serializers.FloatField(default=0.0)
    improved_hot_water_therms = serializers.FloatField(default=0.0)
    improved_hot_water_kwh = serializers.FloatField(default=0.0)
    improved_lights_and_appliance_therms = serializers.FloatField(default=0.0)
    improved_lights_and_appliance_kwh = serializers.FloatField(default=0.0)
    improved_pv_kwh = serializers.FloatField(default=0.0)
    improved_solar_hot_water_therms = serializers.FloatField(default=0.0)
    improved_solar_hot_water_kwh = serializers.FloatField(default=0.0)
    improved_electric_cost = serializers.FloatField(default=0.0)
    improved_gas_cost = serializers.FloatField(default=0.0)
    has_heat_pump_water_heater = serializers.BooleanField(default=False)

    class Meta:
        fields = (
            "climate_location",
            "primary_heating_class",
            "conditioned_area",
            "electric_utility",
            "gas_utility",
            "fireplace",
            "thermostat_brand",
            "grid_harmonization_elements",
            "eps_additional_incentives",
            "solar_elements",
            "code_heating_therms",
            "code_heating_kwh",
            "code_cooling_kwh",
            "code_hot_water_therms",
            "code_hot_water_kwh",
            "code_lights_and_appliance_therms",
            "code_lights_and_appliance_kwh",
            "code_electric_cost",
            "code_gas_cost",
            "improved_heating_therms",
            "improved_heating_kwh",
            "improved_cooling_kwh",
            "improved_hot_water_therms",
            "improved_hot_water_kwh",
            "improved_lights_and_appliance_therms",
            "improved_lights_and_appliance_kwh",
            "improved_pv_kwh",
            "improved_solar_hot_water_therms",
            "improved_solar_hot_water_kwh",
            "improved_electric_cost",
            "improved_gas_cost",
            "has_heat_pump_water_heater",
        )

    def get_input(self, data):
        """Swaps out the Enum internal for the actual value"""
        result = {}
        for k, v in data.items():
            if isinstance(v, Enum):
                v = v.value
            result[k] = v
        return result

    def get_calculator_class(self):
        raise NotImplementedError

    def to_internal_value(self, data):
        internal = super(CalculatorBaseSerializer, self).to_internal_value(data)
        calculator_class = self.get_calculator_class()
        self.calculator = calculator_class(**internal)

        result = {
            "input": self.get_input(internal),
        }
        return result


class CalculatorSerializer(serializers.ModelSerializer):
    """This is main calculator for ETO"""

    home_status = serializers.PrimaryKeyRelatedField(
        queryset=EEPProgramHomeStatus.objects.filter(eep_program__slug__in=["eto-2021", "eto-2022"])
    )
    is_locked = serializers.SerializerMethodField(read_only=True)
    pretty_percent_improvement = serializers.SerializerMethodField(read_only=True)
    pretty_percent_improvement_kwh = serializers.SerializerMethodField(read_only=True)
    pretty_percent_improvement_therms = serializers.SerializerMethodField(read_only=True)
    us_state = serializers.SerializerMethodField(read_only=True)
    reports = serializers.SerializerMethodField(read_only=True)

    class Meta:
        """Meta Options"""

        model = FastTrackSubmission
        fields = (
            "id",
            "home_status",
            "project_id",
            "solar_project_id",
            "eps_score",
            "eps_score_built_to_code_score",
            "percent_improvement",
            "percent_improvement_kwh",
            "percent_improvement_therms",
            "builder_incentive",
            "rater_incentive",
            "carbon_score",
            "carbon_built_to_code_score",
            "estimated_annual_energy_costs",
            "estimated_monthly_energy_costs",
            "estimated_annual_energy_costs_code",
            "estimated_monthly_energy_costs_code",
            "similar_size_eps_score",
            "similar_size_carbon_score",
            "builder_gas_incentive",
            "builder_electric_incentive",
            "rater_gas_incentive",
            "rater_electric_incentive",
            "therm_savings",
            "kwh_savings",
            "mbtu_savings",
            "eps_calculator_version",
            "net_zero_eps_incentive",
            "energy_smart_homes_eps_incentive",
            "net_zero_solar_incentive",
            "energy_smart_homes_solar_incentive",
            "triple_pane_window_incentive",
            "rigid_insulation_incentive",
            "sealed_attic_incentive",
            "cobid_builder_incentive",
            "cobid_verifier_incentive",
            "eps_calculator_version",
            # EPS Fields
            "electric_cost_per_month",
            "natural_gas_cost_per_month",
            "improved_total_kwh",
            "improved_total_therms",
            "solar_hot_water_kwh",
            "solar_hot_water_therms",
            "pv_kwh",
            "projected_carbon_consumption_electric",
            "projected_carbon_consumption_natural_gas",
            # Extra
            "pretty_percent_improvement",
            "pretty_percent_improvement_kwh",
            "pretty_percent_improvement_therms",
            "us_state",
            "reports",
            "is_locked",
        )
        read_only_fields = (
            "project_id",
            "solar_project_id",
        )

    @classmethod
    def get_electric_utility(cls, company):
        data = {
            "pacific-power": ElectricUtility.PACIFIC_POWER,
            "portland-electric": ElectricUtility.PORTLAND_GENERAL,
        }
        slug = company.slug if company else None
        return data.get(slug, ElectricUtility.NONE)

    @classmethod
    def get_gas_utility(cls, company):
        data = {
            "nw-natural-gas": GasUtility.NW_NATURAL,
            "cascade-gas": GasUtility.CASCADE,
            "avista": GasUtility.AVISTA,
        }
        slug = company.slug if company else None
        return data.get(slug, GasUtility.NONE)

    def get_simulation_serializer(self):
        raise NotImplementedError

    def get_calculator_serializer(self):
        raise NotImplementedError

    def get_calculator_checklist_inputs(self, home_status: EEPProgramHomeStatus) -> dict:
        """Checklist answers"""
        return {}

    def get_calculator_kwargs(self, home_status: EEPProgramHomeStatus) -> dict:
        """Anything else needed"""
        return {}

    def get_calculator_return_data(self, home_status: EEPProgramHomeStatus) -> dict:
        """Stuff that will get saved back to the FastTrack model"""
        return {"home_status": home_status.pk}

    def to_internal_value(self, data):
        internal = {}
        errors = defaultdict(list)
        home_status = EEPProgramHomeStatus.objects.get(id=data["home_status"])
        if home_status.floorplan is None or home_status.floorplan.simulation is None:
            errors["simulation"] = ["Missing simulation data needed to compute EPS"]
        else:
            serializer_class = self.get_simulation_serializer()
            try:
                serializer = serializer_class(instance=home_status.floorplan.simulation)
                internal.update(serializer.to_representation(home_status.floorplan.simulation))
            except ValidationError as err:
                errors["simulation"] = [value for _key, value in err.detail.items()]

        internal.update(self.get_calculator_checklist_inputs(home_status))
        if "errors" in internal:
            clist_errors = internal.pop("errors")
            clist_errors = [clist_errors] if isinstance(clist_errors, dict) else clist_errors
            errors["checklist_questions"] += clist_errors

        if errors:
            raise ValidationError(errors)

        internal["electric_utility"] = self.get_electric_utility(
            home_status.home.get_electric_company()
        )
        internal["gas_utility"] = self.get_gas_utility(home_status.home.get_gas_company())
        internal["us_state"] = home_status.home.state

        internal.update(self.get_calculator_kwargs(home_status))

        calculator_serializer_class = self.get_calculator_serializer()
        calculator_serializer = calculator_serializer_class(data=internal)
        calculator_serializer.is_valid(raise_exception=True)

        self.calculator = calculator_serializer.calculator

        _internal = self.get_calculator_return_data(home_status=home_status)
        internal = {f: _internal[f] for f in self.fields if _internal.get(f) is not None}
        return super(CalculatorSerializer, self).to_internal_value(internal)

    def update(self, instance, validated_data, override=False):
        """Respect is_locked and don't do shit if it is."""

        if instance and instance.is_locked() and not override:
            return instance

        return super(CalculatorSerializer, self).update(
            instance=instance, validated_data=validated_data
        )

    def create(self, validated_data):
        instance = self.Meta.model.objects.filter(home_status=validated_data["home_status"]).first()
        if instance:
            validated_data.pop("home_status")
            return self.update(instance, validated_data)
        return super(CalculatorSerializer, self).create(validated_data)

    def get_is_locked(self, instance):
        if isinstance(instance, dict):
            return None
        return instance.is_locked()

    def get_pretty_percent_improvement(self, instance):
        return f"{instance.percent_improvement:.0%}"

    def get_pretty_percent_improvement_kwh(self, instance):
        return f"{instance.percent_improvement_kwh:.0%}"

    def get_pretty_percent_improvement_therms(self, instance):
        return f"{instance.percent_improvement_therms:.0%}"

    def get_pretty_percent_generation_kwh(self, instance):
        return f"{instance.percent_generation_kwh:.0%}"

    def get_us_state(self, instance):
        return instance.home_status.home.state

    def get_reports(self, instance):
        if instance and hasattr(self, "calculator"):
            return {
                "inputs": self.calculator.input_report,
                "input_dump": self.calculator.input_str,
                "summary": self.calculator.as_built_report,
                "code_calculations": self.calculator.code_calculations.calculation_report,
                "improved_calculations": self.calculator.improved_calculations.calculation_report,
                "improvements": self.calculator.improvement_report,
                "incentives": self.calculator.incentives.incentive_report,
                "projected": self.calculator.projected.projected_consumption_report,
                "net_zero": self.calculator.net_zero.incentive_report
                + "\n\n"
                + self.calculator.net_zero.mad_max_report
                + "\n\n"
                + self.calculator.net_zero.incentive_allocation_report
                + "\n\n"
                + self.calculator.net_zero.net_zero_allocation_report,
            }
        return {
            "inputs": None,
            "input_dump": None,
            "code_calculations": None,
            "improved_calculations": None,
            "improvements": None,
            "incentives": None,
            "projected": None,
        }
