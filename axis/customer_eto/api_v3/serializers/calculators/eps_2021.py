"""eps_2021.py - Axis"""

__author__ = "Steven K"
__date__ = "9/8/21 13:40"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from axis.home.models import EEPProgramHomeStatus
from .eps_base import CalculatorBaseSerializer, CalculatorSerializer
from ....calculator.eps_2021.calculator import EPS2021Calculator
from ....enumerations import (
    SmartThermostatBrands2020,
    Fireplace2020,
    GridHarmonization2020,
    AdditionalIncentives2020,
    SolarElements2020,
)

log = logging.getLogger(__name__)


class EPS2021CalculatorBaseSerializer(CalculatorBaseSerializer):
    def get_calculator_class(self):
        return EPS2021Calculator


class EPS2021CalculatorSerializer(CalculatorSerializer):
    """This is main calculator for ETO"""

    def get_simulation_serializer(self):
        from .simulation import EPSSimulation2021Serializer

        return EPSSimulation2021Serializer

    def get_calculator_serializer(self):
        return EPS2021CalculatorBaseSerializer

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
            "estimated_annual_energy_costs_code": round(self.calculator.annual_cost_code, 2),
            "estimated_monthly_energy_costs_code": round(self.calculator.monthly_cost_code, 2),
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
            "improved_total_kwh": self.calculator.improvement_data.improved.kwh,
            "improved_total_therms": self.calculator.improvement_data.improved.therms,
            "solar_hot_water_kwh": self.calculator.improved.solar_hot_water_kwh,
            "solar_hot_water_therms": self.calculator.improved.solar_hot_water_therms,
            "pv_kwh": self.calculator.improved.pv_kwh,
            "projected_carbon_consumption_electric": self.calculator.projected.projected_carbon_consumption.electric_home_kwh
            + self.calculator.projected.projected_carbon_consumption.gas_home_kwh,
            "projected_carbon_consumption_natural_gas": self.calculator.projected.projected_carbon_consumption.gas_home_therms,
        }
