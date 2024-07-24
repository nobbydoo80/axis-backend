""" eps_2022.py - Axis"""

__author__ = "Steven K"
__date__ = "3/1/22 14:40"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
import typing
from enum import Enum

from rest_framework import serializers

from axis.customer_eto.api_v3.serializers.calculators.eps_base import CalculatorSerializer
from axis.customer_eto.api_v3.serializers.fields import EnumField
from axis.customer_eto.calculator.eps_2022.calculator import EPS2022Calculator
from axis.customer_eto.eep_programs.eto_2022 import (
    SmartThermostatBrands2022,
    SolarElements2022,
    AdditionalElements2022,
    CobidRegistered,
    CobidQualification,
)
from axis.customer_eto.eep_programs.fire_rebuild_2021 import FireResilienceBonus
from axis.customer_eto.enumerations import (
    PNWUSStates,
    ClimateLocation,
    PrimaryHeatingEquipment2020,
    ElectricUtility,
    GasUtility,
    Fireplace2020,
    GridHarmonization2020,
    AdditionalIncentives2020,
    SolarElements2020,
    SmartThermostatBrands2020,
)
from axis.home.models import EEPProgramHomeStatus
from .eps_2021 import EPS2021CalculatorSerializer

log = logging.getLogger(__name__)


class EPS2022CalculatorBaseSerializer(serializers.Serializer):
    us_state = EnumField(choices=PNWUSStates)
    climate_location = EnumField(choices=ClimateLocation)
    conditioned_area = serializers.IntegerField(min_value=50, max_value=6000)
    electric_utility = EnumField(choices=ElectricUtility, default=ElectricUtility.NONE)
    gas_utility = EnumField(choices=GasUtility, default=GasUtility.NONE)

    code_heating_therms = serializers.FloatField(default=0.0)
    code_heating_kwh = serializers.FloatField(default=0.0)
    code_cooling_kwh = serializers.FloatField(default=0.0)
    code_hot_water_therms = serializers.FloatField(default=0.0)
    code_hot_water_kwh = serializers.FloatField(default=0.0)
    code_lights_and_appliance_therms = serializers.FloatField(default=0.0)
    code_lights_and_appliance_kwh = serializers.FloatField(default=0.0)

    improved_heating_therms = serializers.FloatField(default=0.0)
    improved_heating_kwh = serializers.FloatField(default=0.0)
    improved_cooling_kwh = serializers.FloatField(default=0.0)
    improved_hot_water_therms = serializers.FloatField(default=0.0)
    improved_hot_water_kwh = serializers.FloatField(default=0.0)
    improved_lights_and_appliance_therms = serializers.FloatField(default=0.0)
    improved_lights_and_appliance_kwh = serializers.FloatField(default=0.0)
    electric_rate = serializers.FloatField(default=0.0)
    gas_rate = serializers.FloatField(default=0.0)

    has_heat_pump_water_heater = serializers.BooleanField(default=False)

    # From checklist
    improved_pv_kwh = serializers.FloatField(default=0.0)
    primary_heating_class = EnumField(choices=PrimaryHeatingEquipment2020)

    thermostat_brand = EnumField(
        choices=SmartThermostatBrands2022, default=SmartThermostatBrands2022.NONE
    )
    fireplace = EnumField(choices=Fireplace2020, default=Fireplace2020.NONE)
    electric_elements = EnumField(choices=AdditionalElements2022, default=AdditionalElements2022.NO)
    solar_elements = EnumField(choices=SolarElements2022, allow_null=True, default=None)
    fire_resiliance_bonus = EnumField(
        choices=FireResilienceBonus, allow_null=True, default=FireResilienceBonus.NO
    )
    cobid_registered = EnumField(choices=CobidRegistered, default=CobidRegistered.NO)
    cobid_type = EnumField(choices=CobidQualification, default=CobidQualification.NO)

    class Meta:
        fields = (
            "us_state",
            "climate_location",
            "conditioned_area",
            "electric_utility",
            "gas_utility",
            # Simulation Code
            "code_heating_therms",
            "code_heating_kwh",
            "code_cooling_kwh",
            "code_hot_water_therms",
            "code_hot_water_kwh",
            "code_lights_and_appliance_therms",
            "code_lights_and_appliance_kwh",
            # Simulation Improved
            "improved_heating_therms",
            "improved_heating_kwh",
            "improved_cooling_kwh",
            "improved_hot_water_therms",
            "improved_hot_water_kwh",
            "improved_lights_and_appliance_therms",
            "improved_lights_and_appliance_kwh",
            "has_heat_pump_water_heater",
            "improved_pv_kwh",
            "electric_rate",
            "gas_rate",
            # Checklist
            "primary_heating_class",
            "fireplace",
            "thermostat_brand",
            "grid_harmonization_elements",
            "eps_additional_incentives",
            "solar_elements",
            "cobid_type",
            "cobid_registered",
        )

    def get_calculator_class(self):
        return EPS2022Calculator

    def get_input(self, data):
        """Swaps out the Enum internal for the actual value"""
        result = {}
        for k, v in data.items():
            if isinstance(v, Enum):
                v = v.value
            result[k] = v
        return result

    def to_internal_value(self, data):
        internal = super(EPS2022CalculatorBaseSerializer, self).to_internal_value(data)
        calculator_class = self.get_calculator_class()
        self.calculator = calculator_class(**internal)

        result = {
            "input": self.get_input(internal),
        }
        return result


class EPS2022CalculatorSerializer(CalculatorSerializer):
    """This is main calculator for ETO"""

    home_status = serializers.PrimaryKeyRelatedField(
        queryset=EEPProgramHomeStatus.objects.filter(eep_program__slug="eto-2022")
    )
    is_locked = serializers.SerializerMethodField(read_only=True)
    pretty_percent_improvement = serializers.SerializerMethodField(read_only=True)
    pretty_percent_improvement_kwh = serializers.SerializerMethodField(read_only=True)
    pretty_percent_improvement_therms = serializers.SerializerMethodField(read_only=True)
    pretty_percent_generation_kwh = serializers.SerializerMethodField(read_only=True)
    us_state = serializers.SerializerMethodField(read_only=True)
    reports = serializers.SerializerMethodField(read_only=True)

    class Meta(CalculatorSerializer.Meta):
        """Meta Options"""

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
            "ev_ready_builder_incentive",
            "solar_storage_builder_incentive",
            "solar_ready_builder_incentive",
            "solar_ready_verifier_incentive",
            "heat_pump_water_heater_incentive",
            "eps_calculator_version",
            # EPS Fields
            "electric_cost_per_month",
            "natural_gas_cost_per_month",
            "improved_total_kwh",
            "improved_total_therms",
            "solar_hot_water_kwh",
            "solar_hot_water_therms",
            "pv_kwh",
            "percent_generation_kwh",
            "projected_carbon_consumption_electric",
            "projected_carbon_consumption_natural_gas",
            # Extra
            "pretty_percent_improvement",
            "pretty_percent_improvement_kwh",
            "pretty_percent_improvement_therms",
            "pretty_percent_generation_kwh",
            "us_state",
            "reports",
            "is_locked",
        )

    def get_calculator_serializer(self) -> typing.Type[serializers.Serializer]:
        return EPS2022CalculatorBaseSerializer

    def get_simulation_serializer(self) -> typing.Type[serializers.Serializer]:
        from .simulation import EPSSimulation2023Serializer

        return EPSSimulation2023Serializer

    def get_calculator_checklist_inputs(self, home_status: EEPProgramHomeStatus) -> dict:
        result = {}
        answers = home_status.get_input_values(user_role="rater")
        if home_status.home.state != "OR":
            if "errors" not in result:
                result["errors"] = []
            result["errors"].append("ETO-2022 only applies to OR only.")
        if not answers.get("primary-heating-equipment-type"):
            if "errors" not in result:
                result["errors"] = []
            result["errors"].append("Missing question Primary Heat Type needed to compute EPS")
        if "errors" not in result:
            result["primary_heating_class"] = answers["primary-heating-equipment-type"]
            result["thermostat_brand"] = answers.get(
                "smart-thermostat-brand", SmartThermostatBrands2022.NONE
            )
            result["fireplace"] = answers.get("has-gas-fireplace", Fireplace2020.NONE)
            result["electric_elements"] = answers.get(
                "eto-electric-elements", AdditionalElements2022.NO
            )
            result["cobid_registered"] = answers.get("cobid-registered", CobidRegistered.NO)
            result["cobid_type"] = answers.get("cobid-type", CobidQualification.NO)

            result["fire_resiliance_bonus"] = None
            fire_rebuild = answers.get("fire-rebuild-qualification")
            if fire_rebuild and fire_rebuild.lower() == "yes":
                result["fire_resiliance_bonus"] = answers.get("fire-resilience-bonus")

            result["solar_elements"] = answers.get("solar-elements")
            result["improved_pv_kwh"] = answers.get(
                "ets-annual-etsa-kwh", answers.get("non-ets-annual-pv-watts", 0.0)
            )
        return result

    def get_calculator_return_data(self, home_status: EEPProgramHomeStatus) -> dict:
        return {
            "home_status": home_status.pk,
            "eps_score": self.calculator.calculations.eps_score,
            "eps_score_built_to_code_score": self.calculator.calculations.code_eps_score,
            "percent_improvement": round(self.calculator.savings.mbtu.floored_pct_improvement, 2),
            "percent_improvement_kwh": round(
                self.calculator.savings.kwh.floored_pct_improvement, 2
            ),
            "percent_improvement_therms": round(
                self.calculator.savings.therm.floored_pct_improvement, 2
            ),
            "builder_incentive": round(
                self.calculator.allocations.builder_total_incentive.total, 2
            ),
            "rater_incentive": round(self.calculator.allocations.verifier_total_incentive.total, 2),
            "carbon_score": round(self.calculator.carbon.carbon_score.total, 1),
            "carbon_built_to_code_score": round(self.calculator.carbon.code_carbon_score.total, 1),
            "estimated_annual_energy_costs": round(self.calculator.annual_cost, 2),
            "estimated_monthly_energy_costs": round(self.calculator.monthly_cost, 2),
            "estimated_annual_energy_costs_code": round(self.calculator.annual_cost_code, 2),
            "estimated_monthly_energy_costs_code": round(self.calculator.monthly_cost_code, 2),
            "similar_size_eps_score": round(self.calculator.projected.similar_size_eps, 0),
            "similar_size_carbon_score": round(
                self.calculator.carbon.similar_size_carbon_score.total, 1
            ),
            "builder_gas_incentive": round(
                self.calculator.allocations.builder_total_incentive.gas_incentive, 2
            ),
            "builder_electric_incentive": round(
                self.calculator.allocations.builder_total_incentive.electric_incentive, 2
            ),
            "rater_gas_incentive": round(
                self.calculator.allocations.verifier_total_incentive.gas_incentive, 2
            ),
            "rater_electric_incentive": round(
                self.calculator.allocations.verifier_total_incentive.electric_incentive, 2
            ),
            "therm_savings": round(self.calculator.savings.therm.savings, 2),
            "kwh_savings": round(self.calculator.savings.kwh.savings, 2),
            "mbtu_savings": round(self.calculator.savings.mbtu.savings, 2),
            "eps_calculator_version": "2022-03-24",
            # Reused - Net Zero Solar
            "net_zero_solar_incentive": self.calculator.incentives.net_zero_builder_incentive.incentive,
            "triple_pane_window_incentive": self.calculator.incentives.fire_rebuild_triple_pane_incentive.incentive,
            "rigid_insulation_incentive": self.calculator.incentives.fire_rebuild_insulation_incentive.incentive,
            "sealed_attic_incentive": self.calculator.incentives.fire_rebuild_sealed_attic_incentive.incentive,
            # New for 2022
            "solar_ready_builder_incentive": self.calculator.incentives.solar_ready_builder_incentive.incentive,
            "solar_ready_verifier_incentive": self.calculator.incentives.solar_ready_verifier_incentive.incentive,
            "ev_ready_builder_incentive": self.calculator.incentives.ev_ready_builder_incentive.incentive,
            "solar_storage_builder_incentive": self.calculator.incentives.solar_storage_builder_incentive.incentive,
            "cobid_builder_incentive": self.calculator.incentives.cobid_builder_incentive.incentive,
            "cobid_verifier_incentive": self.calculator.incentives.cobid_verifier_incentive.incentive,
            "heat_pump_water_heater_incentive": self.calculator.incentives.heat_pump_water_heater_incentive.incentive,
            # EPS Reporting Fields
            "electric_cost_per_month": round(
                self.calculator.savings.electric_costing.monthly_proposed_cost, 2
            ),
            "natural_gas_cost_per_month": round(
                self.calculator.savings.gas_costing.monthly_proposed_cost, 2
            ),
            "improved_total_kwh": self.calculator.savings.kwh.proposed,
            "improved_total_therms": self.calculator.savings.therm.proposed,
            "solar_hot_water_kwh": 0.0,
            "solar_hot_water_therms": 0.0,
            "pv_kwh": self.calculator.improved_pv_kwh,
            "percent_generation_kwh": self.calculator.percent_generation_kwh,
            "projected_carbon_consumption_electric": self.calculator.carbon.similar_size_carbon_score.electric,
            "projected_carbon_consumption_natural_gas": self.calculator.carbon.similar_size_carbon_score.gas,
        }

    def get_reports(self, instance):
        if instance and hasattr(self, "calculator"):
            return {
                "inputs": self.calculator.input_report,
                "input_dump": self.calculator.input_str,
                "modeled_savings": self.calculator.savings.savings_report,
                "incentives": self.calculator.incentives.incentive_report
                + "\n\n Allocations \n\n"
                + self.calculator.allocations.allocation_report,
                "eps_sheet": self.calculator.projected.projected_report
                + "\n\n"
                + self.calculator.calculations.consumption_report
                + "\n\n"
                + self.calculator.savings.cost_report,
                "carbon": self.calculator.carbon.report,
            }
        return {
            "inputs": None,
            "input_dump": None,
            "code_calculations": None,
            "modeled_savings": None,
            "eps_sheet": None,
            "improved_calculations": None,
            "improvements": None,
            "incentives": None,
            "projected": None,
            "carbon": None,
        }


class EPS2022WACalculatorSerializer(EPS2021CalculatorSerializer):
    def get_simulation_serializer(self):
        from .simulation import EPSSimulation2022Serializer

        return EPSSimulation2022Serializer

    def get_calculator_checklist_inputs(self, home_status: EEPProgramHomeStatus) -> dict:
        result = {}
        answers = home_status.get_input_values(user_role="rater")
        if not answers.get("primary-heating-equipment-type"):
            result["errors"] = ["Missing question Primary Heat Type needed to compute EPS"]
        else:
            result["primary_heating_class"] = answers["primary-heating-equipment-type"]

            smart_tstat = answers.get("smart-thermostat-brand", SmartThermostatBrands2020.NONE)
            if smart_tstat in [
                "Nest Thermostat",
                SmartThermostatBrands2022.NEST,
                SmartThermostatBrands2022.NEST.value,
            ]:
                smart_tstat = SmartThermostatBrands2022.NEST_LEARNING.value
            result["thermostat_brand"] = smart_tstat
            result["fireplace"] = answers.get("has-gas-fireplace", Fireplace2020.NONE)

            # None of this applies to Washington homes.
            result["grid_harmonization_elements"] = GridHarmonization2020.NONE
            result["eps_additional_incentives"] = AdditionalIncentives2020.NO
            result["solar_elements"] = SolarElements2020.NONE
        return result
