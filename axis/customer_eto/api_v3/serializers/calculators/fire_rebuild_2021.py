"""fire_rebuild_2021.py - Axis"""

__author__ = "Steven K"
__date__ = "12/1/21 15:12"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from rest_framework import serializers

from axis.customer_eto.api_v3.serializers.calculators.eps_base import (
    CalculatorBaseSerializer,
    CalculatorSerializer,
)
from axis.customer_eto.api_v3.serializers.fields import EnumField
from axis.customer_eto.calculator.eps_fire_2021.calculator import EPSFire2021Calculator
from axis.customer_eto.enumerations import (
    YesNo,
    SmartThermostatBrands2020,
    Fireplace2020,
    GridHarmonization2020,
    AdditionalIncentives2020,
    SolarElements2020,
)
from axis.customer_eto.eep_programs.fire_rebuild_2021 import FireResilienceBonus
from axis.customer_eto.models import FastTrackSubmission
from axis.home.models import EEPProgramHomeStatus

log = logging.getLogger(__name__)


class EPSFire2021CalculatorBaseSerializer(CalculatorBaseSerializer):
    fire_resilience_bonus = EnumField(choices=FireResilienceBonus, default=FireResilienceBonus.NO)
    fire_rebuild_qualification = EnumField(choices=YesNo, default=YesNo.NO)

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
            "fire_resilience_bonus",
            "fire_rebuild_qualification",
        )

    def get_calculator_class(self):
        return EPSFire2021Calculator


class EPSFire2021CalculatorSerializer(CalculatorSerializer):
    """This is main calculator for ETO"""

    home_status = serializers.PrimaryKeyRelatedField(
        queryset=EEPProgramHomeStatus.objects.filter(eep_program__slug="eto-fire-2021")
    )

    def get_simulation_serializer(self):
        from .simulation import EPSSimulation2022Serializer

        return EPSSimulation2022Serializer

    def get_calculator_serializer(self):
        return EPSFire2021CalculatorBaseSerializer

    def get_calculator_checklist_inputs(self, home_status: EEPProgramHomeStatus) -> dict:
        result = {}
        answers = home_status.get_input_values(user_role="rater")
        if not answers.get("primary-heating-equipment-type"):
            result["errors"] = ["Missing question Primary Heat Type needed to compute EPS"]
        else:
            result["primary_heating_class"] = answers["primary-heating-equipment-type"]
            result["thermostat_brand"] = answers.get(
                "smart-thermostat-brand", SmartThermostatBrands2020.NONE
            )
            result["fireplace"] = answers.get("has-gas-fireplace", Fireplace2020.NONE)
            result["grid_harmonization_elements"] = answers.get(
                "grid-harmonization-elements", GridHarmonization2020.NONE
            )
            result["eps_additional_incentives"] = answers.get(
                "eto-additional-incentives", AdditionalIncentives2020.NO
            )
            result["solar_elements"] = answers.get("solar-elements", SolarElements2020.NONE)
            result["improved_pv_kwh"] = answers.get("ets-annual-etsa-kwh", 0.0)
            result["fire_resilience_bonus"] = answers.get(
                "fire-resilience-bonus", FireResilienceBonus.NO
            )
            result["fire_rebuild_qualification"] = answers.get(
                "fire-rebuild-qualification", YesNo.NO
            )
        return result

    def get_calculator_return_data(self, home_status: EEPProgramHomeStatus) -> dict:
        return {
            "home_status": home_status.pk,
            "eps_score": self.calculator.improved_calculations.eps_score,
            "eps_score_built_to_code_score": self.calculator.code_calculations.code_eps_score,
            "percent_improvement": round(
                self.calculator.improvement_data.floored_improvement_breakout.mbtu, 2
            ),
            "percent_improvement_kwh": round(
                self.calculator.improvement_data.floored_improvement_breakout.kwh, 2
            ),
            "percent_improvement_therms": round(
                self.calculator.improvement_data.floored_improvement_breakout.therms, 2
            ),
            "builder_incentive": self.calculator.incentives.builder_incentive,
            "rater_incentive": self.calculator.incentives.verifier_incentive,
            "carbon_score": round(self.calculator.improved_calculations.carbon_score, 1),
            "carbon_built_to_code_score": round(
                self.calculator.code_calculations.code_carbon_score, 1
            ),
            "estimated_annual_energy_costs": round(self.calculator.annual_cost, 2),
            "estimated_monthly_energy_costs": round(self.calculator.monthly_cost, 2),
            "similar_size_eps_score": round(self.calculator.projected.similar_size_eps, 0),
            "similar_size_carbon_score": round(self.calculator.projected.similar_size_carbon, 1),
            "builder_gas_incentive": round(self.calculator.incentives.builder_gas_incentive, 2),
            "builder_electric_incentive": round(
                self.calculator.incentives.builder_electric_incentive, 2
            ),
            "rater_gas_incentive": round(self.calculator.incentives.verifier_gas_incentive, 2),
            "rater_electric_incentive": round(
                self.calculator.incentives.verifier_electric_incentive, 2
            ),
            "therm_savings": round(self.calculator.improvement_data.savings.therms, 2),
            "kwh_savings": round(self.calculator.improvement_data.savings.kwh, 2),
            "mbtu_savings": round(self.calculator.improvement_data.savings.mbtu, 2),
            "eps_calculator_version": "2021-10-01",
            "net_zero_eps_incentive": round(
                self.calculator.net_zero.net_zero_eps_builder_allocation.incentive, 2
            ),
            "energy_smart_homes_eps_incentive": round(
                self.calculator.net_zero.net_zero_energy_smart_homes_builder_eps_allocation.incentive,
                2,
            ),
            "net_zero_solar_incentive": round(
                self.calculator.net_zero.net_zero_solar_builder_allocation.incentive, 2
            ),
            "energy_smart_homes_solar_incentive": round(
                self.calculator.net_zero.net_zero_energy_smart_homes_builder_solar_allocation.incentive,
                2,
            ),
            # EPS Reporting Fields
            "electric_cost_per_month": round(self.calculator.improved.electric_cost / 12.0, 2),
            "natural_gas_cost_per_month": round(self.calculator.improved.gas_cost / 12.0, 2),
            "improved_total_kwh": self.calculator.improved.total_kwh,
            "improved_total_therms": self.calculator.improved.total_therms,
            "solar_hot_water_kwh": self.calculator.improved.solar_hot_water_kwh,
            "solar_hot_water_therms": self.calculator.improved.solar_hot_water_therms,
            "pv_kwh": self.calculator.improved.pv_kwh,
            "projected_carbon_consumption_electric": self.calculator.projected.projected_carbon_consumption.electric_home_kwh
            + self.calculator.projected.projected_carbon_consumption.gas_home_kwh,
            "projected_carbon_consumption_natural_gas": self.calculator.projected.projected_carbon_consumption.gas_home_therms,
            "triple_pane_window_incentive": round(
                self.calculator.net_zero.triple_pane_window_incentive, 2
            ),
            "rigid_insulation_incentive": round(
                self.calculator.net_zero.rigid_insulation_incentive, 2
            ),
            "sealed_attic_incentive": round(self.calculator.net_zero.sealed_attic_incentive, 2),
        }
