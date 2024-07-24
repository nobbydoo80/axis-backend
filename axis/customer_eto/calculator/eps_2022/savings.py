"""savings.py - Axis"""

__author__ = "Steven K"
__date__ = "3/3/22 08:11"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
import math
from dataclasses import dataclass
from decimal import Decimal
from functools import cached_property

from simulation.enumerations import EnergyUnit
from simulation.utils.conversions import convert_kwh_to, convert_therm_to
from tabulate import tabulate

from axis.customer_eto.enumerations import QualifyingThermostat, Fireplace2020

log = logging.getLogger(__name__)


@dataclass
class HeatingCoolingSavings:
    code_heating_therms: float = 0.0
    code_heating_kwh: float = 0.0
    code_cooling_kwh: float = 0.0
    improved_heating_therms: float = 0.0
    improved_heating_kwh: float = 0.0
    improved_cooling_kwh: float = 0.0
    thermostat: QualifyingThermostat = QualifyingThermostat.NONE

    @cached_property
    def thermostat_heating_adjustment(self) -> float:
        lookup = {
            QualifyingThermostat.DUCTED_ASHP: 0.12,
            QualifyingThermostat.DUCTED_FURNACE: 0.06,
            QualifyingThermostat.NONE: 0.0,
        }
        return lookup[self.thermostat]

    @cached_property
    def thermostat_cooling_adjustment(self) -> float:
        lookup = {
            QualifyingThermostat.DUCTED_ASHP: 0.06,
            QualifyingThermostat.DUCTED_FURNACE: 0.06,
            QualifyingThermostat.NONE: 0.0,
        }
        return lookup[self.thermostat]

    @cached_property
    def thermostat_heating_kwh_savings(self) -> float:
        return self.improved_heating_kwh * self.thermostat_heating_adjustment

    @cached_property
    def thermostat_heating_therm_savings(self) -> float:
        return self.improved_heating_therms * self.thermostat_heating_adjustment

    @cached_property
    def thermostat_cooling_kwh_savings(self) -> float:
        return self.improved_cooling_kwh * self.thermostat_cooling_adjustment

    @cached_property
    def total_heating_kwh_savings(self) -> float:
        value = self.code_heating_kwh
        if self.thermostat != QualifyingThermostat.NONE:
            value -= self.improved_heating_kwh - self.thermostat_heating_kwh_savings
        else:
            value -= self.improved_heating_kwh
        return value

    @cached_property
    def total_heating_therm_savings(self) -> float:
        value = self.code_heating_therms
        if self.thermostat != QualifyingThermostat.NONE:
            value -= self.improved_heating_therms - self.thermostat_heating_therm_savings
        else:
            value -= self.improved_heating_therms
        return value

    @cached_property
    def total_cooling_kwh_savings(self) -> float:
        value = self.code_cooling_kwh
        if self.thermostat != QualifyingThermostat.NONE:
            value -= self.improved_cooling_kwh - self.thermostat_cooling_kwh_savings
        else:
            value -= self.improved_cooling_kwh
        return value

    @cached_property
    def report(self) -> str:
        return tabulate(
            [
                [
                    "Modeled Heating Consumption Baseline (UDRH)",
                    self.code_heating_kwh,
                    self.code_heating_therms,
                ],
                [
                    "Modeled Heating Consumption Proposed",
                    self.improved_heating_kwh,
                    self.improved_heating_therms,
                ],
                [],
                ["Modeled Cooling kWh Consumption Baseline (UDRH)", self.code_cooling_kwh],
                ["Modeled Cooling kWh Consumption Proposed", self.improved_cooling_kwh],
                [],
                ["Heating Smart Thermostat Adjustment", self.thermostat_heating_adjustment],
                ["Cooling Smart Thermostat Adjustment", self.thermostat_cooling_adjustment],
                [],
                [
                    "Heating Smart Thermostat Savings",
                    self.thermostat_heating_kwh_savings,
                    self.thermostat_heating_therm_savings,
                ],
                [
                    "Cooling Smart Thermostat Savings",
                    self.thermostat_cooling_kwh_savings,
                ],
                [],
                [
                    "Total Heating Savings",
                    self.total_heating_kwh_savings,
                    self.total_heating_therm_savings,
                ],
                [
                    "Total Cooling Savings",
                    self.total_cooling_kwh_savings,
                ],
            ],
            headers=["Heating & Cooling", "Electric (kWh)", "Gas (therms)"],
            floatfmt=".2f",
        )


@dataclass
class HotWaterSavings:
    code_hot_water_therms: float = 0.0
    code_hot_water_kwh: float = 0.0
    improved_hot_water_therms: float = 0.0
    improved_hot_water_kwh: float = 0.0

    @cached_property
    def total_hot_water_kwh_savings(self) -> float:
        return self.code_hot_water_kwh - self.improved_hot_water_kwh

    @cached_property
    def total_hot_water_therm_savings(self) -> float:
        return self.code_hot_water_therms - self.improved_hot_water_therms

    @cached_property
    def report(self) -> str:
        return tabulate(
            [
                [
                    "Modeled Water Heating Consumption Baseline (UDRH)",
                    self.code_hot_water_kwh,
                    self.code_hot_water_therms,
                ],
                [
                    "Modeled Water Heating Consumption Proposed",
                    self.improved_hot_water_kwh,
                    self.improved_hot_water_therms,
                ],
                [],
                [
                    "Total Water Heating Savings",
                    self.total_hot_water_kwh_savings,
                    self.total_hot_water_therm_savings,
                ],
            ],
            headers=["Water Heating", "Electric (kWh)", "Gas (therms)"],
            floatfmt=".2f",
        )


@dataclass
class LightsAndApplianceSavings:
    code_lights_and_appliance_therms: float = 0.0
    code_lights_and_appliance_kwh: float = 0.0
    improved_lights_and_appliance_therms: float = 0.0
    improved_lights_and_appliance_kwh: float = 0.0

    @cached_property
    def total_lights_and_appliance_kwh_savings(self) -> float:
        return self.code_lights_and_appliance_kwh - self.improved_lights_and_appliance_kwh

    @cached_property
    def total_lights_and_appliance_therm_savings(self) -> float:
        return self.code_lights_and_appliance_therms - self.improved_lights_and_appliance_therms

    @cached_property
    def report(self) -> str:
        return tabulate(
            [
                [
                    "Modeled Lights and Appliances Consumption Baseline (UDRH)",
                    self.code_lights_and_appliance_kwh,
                    self.code_lights_and_appliance_therms,
                ],
                [
                    "Modeled Lights and Appliances Consumption Proposed",
                    self.improved_lights_and_appliance_kwh,
                    self.improved_lights_and_appliance_therms,
                ],
                [],
                [
                    "Total Lights and Appliances Savings",
                    self.total_lights_and_appliance_kwh_savings,
                    self.total_lights_and_appliance_therm_savings,
                ],
            ],
            headers=["Lights and Appliances", "Electric (kWh)", "Gas (therms)"],
            floatfmt=".2f",
        )


@dataclass
class FireplaceSavings:
    fireplace: Fireplace2020 = Fireplace2020.NONE

    @cached_property
    def code_fireplace_therms(self) -> float:
        lookup = {
            Fireplace2020.NONE: 0.0,
            Fireplace2020.FE_LTE_49: 88.5,
            Fireplace2020.FE_50_59: 88.5,
            Fireplace2020.FE_60_69: 88.5,
            Fireplace2020.FE_GTE_70: 88.5,
        }
        return lookup[self.fireplace]

    @cached_property
    def improved_fireplace_therms(self) -> float:
        lookup = {
            Fireplace2020.NONE: 0.0,
            Fireplace2020.FE_LTE_49: 88.5,
            Fireplace2020.FE_50_59: 88.5,
            Fireplace2020.FE_60_69: 88.5,
            Fireplace2020.FE_GTE_70: 70.2,
        }
        return lookup[self.fireplace]

    @cached_property
    def total_fireplace_therm_savings(self) -> float:
        return self.code_fireplace_therms - self.improved_fireplace_therms

    @cached_property
    def report(self) -> str:
        return tabulate(
            [
                [
                    "Fireplace Consumption Baseline (UDRH)",
                    None,
                    self.code_fireplace_therms,
                ],
                [
                    "Fireplace Consumption Proposed",
                    None,
                    self.improved_fireplace_therms,
                ],
                [],
                [
                    "Total Fireplace Savings",
                    None,
                    self.total_fireplace_therm_savings,
                ],
            ],
            headers=["Fireplace", "Electric (kWh)", "Gas (therms)"],
            floatfmt=".2f",
        )


@dataclass
class SavingsResult:
    baseline: float
    proposed: float
    savings: float
    pct_improvement: float

    @cached_property
    def floored_pct_improvement(self):
        return math.floor(self.pct_improvement * 100.0) / 100.0


@dataclass
class CostResult:
    baseline_consumption: float
    proposed_consumption: float
    savings: float
    rate: Decimal = "0.0"

    @cached_property
    def proposed_monthly(self) -> float:
        try:
            return max([self.proposed_consumption / 12.0, 0])
        except ZeroDivisionError:
            return 0.0

    @cached_property
    def baseline_monthly(self) -> float:
        try:
            return max([self.baseline_consumption / 12.0, 0])
        except ZeroDivisionError:
            return 0.0

    @cached_property
    def monthly_proposed_cost(self) -> float:
        return self.proposed_monthly * float(self.rate)

    @cached_property
    def monthly_baseline_cost(self) -> float:
        return self.baseline_monthly * float(self.rate)

    @cached_property
    def annual_proposed_cost(self) -> float:
        return self.proposed_consumption * float(self.rate)

    @cached_property
    def annual_baseline_cost(self) -> float:
        return self.baseline_consumption * float(self.rate)

    @cached_property
    def annual_savings_cost(self) -> float:
        return self.savings * float(self.rate)


@dataclass
class Savings:
    code_heating_therms: float = 0.0
    code_heating_kwh: float = 0.0
    code_cooling_kwh: float = 0.0
    code_hot_water_therms: float = 0.0
    code_hot_water_kwh: float = 0.0
    code_lights_and_appliance_therms: float = 0.0
    code_lights_and_appliance_kwh: float = 0.0

    improved_heating_therms: float = 0.0
    improved_heating_kwh: float = 0.0
    improved_cooling_kwh: float = 0.0
    improved_hot_water_therms: float = 0.0
    improved_hot_water_kwh: float = 0.0
    improved_lights_and_appliance_therms: float = 0.0
    improved_lights_and_appliance_kwh: float = 0.0
    improved_pv_kwh: float = 0.0

    electric_rate: Decimal = "0.0"
    gas_rate: Decimal = "0.0"

    thermostat: QualifyingThermostat = QualifyingThermostat.NONE
    fireplace: Fireplace2020 = Fireplace2020.NONE

    @cached_property
    def heating_cooling(self) -> HeatingCoolingSavings:
        return HeatingCoolingSavings(
            code_heating_therms=self.code_heating_therms,
            code_heating_kwh=self.code_heating_kwh,
            code_cooling_kwh=self.code_cooling_kwh,
            improved_heating_therms=self.improved_heating_therms,
            improved_heating_kwh=self.improved_heating_kwh,
            improved_cooling_kwh=self.improved_cooling_kwh,
            thermostat=self.thermostat,
        )

    @cached_property
    def hot_water(self) -> HotWaterSavings:
        return HotWaterSavings(
            code_hot_water_therms=self.code_hot_water_therms,
            code_hot_water_kwh=self.code_hot_water_kwh,
            improved_hot_water_therms=self.improved_hot_water_therms,
            improved_hot_water_kwh=self.improved_hot_water_kwh,
        )

    @cached_property
    def lights_and_appliance(self) -> LightsAndApplianceSavings:
        return LightsAndApplianceSavings(
            code_lights_and_appliance_therms=self.code_lights_and_appliance_therms,
            code_lights_and_appliance_kwh=self.code_lights_and_appliance_kwh,
            improved_lights_and_appliance_therms=self.improved_lights_and_appliance_therms,
            improved_lights_and_appliance_kwh=self.improved_lights_and_appliance_kwh,
        )

    @cached_property
    def fireplace_savings(self) -> FireplaceSavings:
        return FireplaceSavings(fireplace=self.fireplace)

    @cached_property
    def therm(self) -> SavingsResult:
        baseline = sum(
            [
                self.code_heating_therms,
                self.code_hot_water_therms,
                self.code_lights_and_appliance_therms,
                self.fireplace_savings.code_fireplace_therms,
            ]
        )
        proposed = sum(
            [
                self.improved_heating_therms
                - self.heating_cooling.thermostat_heating_therm_savings,
                self.improved_hot_water_therms,
                self.improved_lights_and_appliance_therms,
                self.fireplace_savings.improved_fireplace_therms,
            ]
        )
        savings = baseline - proposed
        try:
            pct_improvement = savings / baseline
        except ZeroDivisionError:
            pct_improvement = 0

        return SavingsResult(
            baseline=baseline,
            proposed=proposed,
            savings=savings,
            pct_improvement=pct_improvement,
        )

    @cached_property
    def kwh(self) -> SavingsResult:
        baseline = sum(
            [
                self.code_heating_kwh,
                self.code_cooling_kwh,
                self.code_hot_water_kwh,
                self.code_lights_and_appliance_kwh,
            ]
        )
        proposed = sum(
            [
                self.improved_heating_kwh - self.heating_cooling.thermostat_heating_kwh_savings,
                self.improved_cooling_kwh - self.heating_cooling.thermostat_cooling_kwh_savings,
                self.improved_hot_water_kwh,
                self.improved_lights_and_appliance_kwh,
            ]
        )
        savings = baseline - proposed
        try:
            pct_improvement = savings / baseline
        except ZeroDivisionError:
            pct_improvement = 0

        return SavingsResult(
            baseline=baseline,
            proposed=proposed,
            savings=savings,
            pct_improvement=pct_improvement,
        )

    @cached_property
    def mbtu(self) -> SavingsResult:
        baseline = sum(
            [
                convert_kwh_to(self.kwh.baseline, EnergyUnit.MBTU),
                convert_therm_to(self.therm.baseline, EnergyUnit.MBTU),
            ]
        )
        proposed = sum(
            [
                convert_kwh_to(self.kwh.proposed, EnergyUnit.MBTU),
                convert_therm_to(self.therm.proposed, EnergyUnit.MBTU),
            ]
        )
        savings = baseline - proposed
        try:
            pct_improvement = savings / baseline
        except ZeroDivisionError:
            pct_improvement = 0

        return SavingsResult(
            baseline=baseline,
            proposed=proposed,
            savings=savings,
            pct_improvement=pct_improvement,
        )

    @property
    def savings_report(self) -> str:
        result = tabulate(
            [
                [
                    "Therms",
                    self.therm.baseline,
                    self.therm.proposed,
                    self.therm.savings,
                    f"{self.therm.pct_improvement:.1%}",
                ],
                [
                    "kWh",
                    self.kwh.baseline,
                    self.kwh.proposed,
                    self.kwh.savings,
                    f"{self.kwh.pct_improvement:.1%}",
                ],
                [
                    "MMBtu",
                    self.mbtu.baseline,
                    self.mbtu.proposed,
                    self.mbtu.savings,
                    f"{self.mbtu.pct_improvement:.1%}",
                ],
            ],
            headers=[
                "Energy Consumption and Savings Summary",
                "Baseline",
                "Proposed",
                "Savings",
                "% Improvement",
            ],
            floatfmt=".1f",
        )
        result += "\n\n" + self.heating_cooling.report
        result += "\n\n" + self.hot_water.report
        result += "\n\n" + self.lights_and_appliance.report
        result += "\n\n" + self.fireplace_savings.report
        return result

    @cached_property
    def gas_costing(self) -> CostResult:
        return CostResult(
            baseline_consumption=self.therm.baseline,
            proposed_consumption=self.therm.proposed,
            savings=self.therm.savings,
            rate=self.gas_rate,
        )

    @cached_property
    def electric_costing(self) -> CostResult:
        return CostResult(
            baseline_consumption=self.kwh.baseline,
            proposed_consumption=self.kwh.proposed - self.improved_pv_kwh,
            savings=self.kwh.savings,
            rate=self.electric_rate,
        )

    @cached_property
    def monthly_cost(self) -> float:
        return self.gas_costing.monthly_proposed_cost + self.electric_costing.monthly_proposed_cost

    @cached_property
    def cost_report(self) -> str:
        results = tabulate(
            [
                ["Electric Annual Rate", f"$ {float(self.electric_rate):,.2f}"],
                ["Gas Annual Rate", f"$ {float(self.gas_rate):,.2f}"],
            ],
            floatfmt=".2f",
        )
        baseline_total = (
            self.gas_costing.annual_baseline_cost + self.electric_costing.annual_baseline_cost
        )
        savings_total = (
            self.gas_costing.annual_savings_cost + self.electric_costing.annual_savings_cost
        )
        results += "\n\n" + tabulate(
            [
                ["Annual Consumption - Elec", self.electric_costing.proposed_consumption],
                [
                    "Monthly Consumption - Elec",
                    self.electric_costing.proposed_monthly,
                    f"$ {self.electric_costing.monthly_proposed_cost:,.2f}",
                ],
                ["Annual Consumption - Gas", self.gas_costing.proposed_consumption],
                [
                    "Monthly Consumption - Gas",
                    self.gas_costing.proposed_monthly,
                    f"$ {self.gas_costing.monthly_proposed_cost:,.2f}",
                ],
                ["Estimated Monthly Energy Cost", None, f"$ {self.monthly_cost:,.2f}"],
                [],
                [
                    "Annual Baseling - Elec",
                    self.electric_costing.baseline_consumption,
                    f"$ {self.electric_costing.annual_baseline_cost:,.2f}",
                ],
                [
                    "Annual Baseline - Gas",
                    self.gas_costing.baseline_consumption,
                    f"$ {self.gas_costing.annual_baseline_cost:,.2f}",
                ],
                [
                    "Annual Baseline Total",
                    None,
                    f"$ {baseline_total:,.2f}",
                ],
                [],
                [
                    "Annual Savings - Elec",
                    self.electric_costing.savings,
                    f"$ {self.electric_costing.annual_savings_cost:,.2f}",
                ],
                [
                    "Annual Savings - Gas",
                    self.gas_costing.savings,
                    f"$ {self.gas_costing.annual_savings_cost:,.2f}",
                ],
                [
                    "Annual Savings Total",
                    None,
                    f"$ {savings_total:,.2f}",
                ],
                [
                    "30 year savings",
                    None,
                    f"$ {savings_total * 30.0:,.2f}",
                ],
            ],
            headers=[None, "kWh/Therm", "$"],
            floatfmt=".1f",
        )
        return results
