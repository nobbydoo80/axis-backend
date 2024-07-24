"""calculations.py - Axis"""

__author__ = "Steven K"
__date__ = "3/4/22 12:01"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
from dataclasses import dataclass
from functools import cached_property
from typing import Union

from simulation.enumerations import EnergyUnit
from simulation.utils.conversions import convert_kwh_to, convert_therm_to
from tabulate import tabulate

from axis.customer_eto.enumerations import HeatType

log = logging.getLogger(__name__)


ELECTRIC_HEATING_FUEL_WEIGHT = 3.67
ELECTRIC_HOT_WATER_FUEL_WEIGHT = 3.18


@dataclass
class BaseCalculation:
    in_heating_therms: float = 0.0
    in_heating_kwh: float = 0.0
    in_cooling_kwh: float = 0.0
    in_hot_water_therms: float = 0.0
    in_hot_water_kwh: float = 0.0
    in_lights_and_appliance_therms: float = 0.0
    in_lights_and_appliance_kwh: float = 0.0
    in_pv_kwh: float = 0.0
    in_fireplace_therms: float = 0.0
    thermostat_heating_therms: float = 0.0
    thermostat_heating_kwh: float = 0.0
    thermostat_cooling_kwh: float = 0.0

    @cached_property
    def heating_therms(self) -> float:
        return self.in_heating_therms - self.thermostat_heating_therms

    @cached_property
    def heating_kwh(self) -> float:
        return self.in_heating_kwh - self.thermostat_heating_kwh

    @cached_property
    def cooling_kwh(self) -> float:
        return self.in_cooling_kwh - self.thermostat_cooling_kwh

    @cached_property
    def hot_water_therms(self) -> float:
        return self.in_hot_water_therms

    @cached_property
    def hot_water_kwh(self) -> float:
        return self.in_hot_water_kwh

    @cached_property
    def lights_and_appliance_therms(self) -> float:
        return self.in_lights_and_appliance_therms

    @cached_property
    def lights_and_appliance_kwh(self) -> float:
        return self.in_lights_and_appliance_kwh

    @cached_property
    def pv_kwh(self) -> float:
        return self.in_pv_kwh

    @cached_property
    def fireplace_therms(self) -> float:
        return self.in_fireplace_therms

    @cached_property
    def total_kwh(self) -> float:
        return sum(
            [
                self.heating_kwh,
                self.cooling_kwh,
                self.hot_water_kwh,
                self.in_lights_and_appliance_kwh,
                -self.pv_kwh,
            ]
        )

    @cached_property
    def total_therms(self) -> float:
        return sum(
            [
                self.heating_therms,
                self.hot_water_therms,
                self.lights_and_appliance_therms,
                self.fireplace_therms,
            ]
        )

    @cached_property
    def total_mbtu(self) -> float:
        return sum(
            [
                convert_kwh_to(self.total_kwh, EnergyUnit.MBTU),
                convert_therm_to(self.total_therms, EnergyUnit.MBTU),
            ]
        )


@dataclass
class GasHeatCalculation(BaseCalculation):
    @cached_property
    def hot_water_kwh(self) -> float:
        return self.in_hot_water_kwh * ELECTRIC_HOT_WATER_FUEL_WEIGHT


@dataclass
class ElectricHeatCalculation(GasHeatCalculation):
    @cached_property
    def heating_kwh(self) -> float:
        return self.in_heating_kwh * ELECTRIC_HEATING_FUEL_WEIGHT


@dataclass
class ImprovedElectricHeatCalculation(GasHeatCalculation):
    @cached_property
    def heating_kwh(self) -> float:
        return max([0, (self.in_heating_kwh - self.pv_kwh) * ELECTRIC_HEATING_FUEL_WEIGHT])


@dataclass
class ConsumptionAdjustment:
    unadjusted: BaseCalculation
    gas_heat: GasHeatCalculation
    electric_heat: Union[ElectricHeatCalculation, ImprovedElectricHeatCalculation]


@dataclass
class Calculations:
    heat_type: HeatType
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

    code_fireplace_savings_therms: float = 0.0
    improved_fireplace_savings_therms: float = 0.0

    thermostat_heating_kwh_savings: float = 0.0
    thermostat_heating_therm_savings: float = 0.0
    thermostat_cooling_kwh_savings: float = 0.0

    @cached_property
    def code_consumption(self) -> ConsumptionAdjustment:
        kw = dict(
            in_heating_therms=self.code_heating_therms,
            in_heating_kwh=self.code_heating_kwh,
            in_cooling_kwh=self.code_cooling_kwh,
            in_hot_water_therms=self.code_hot_water_therms,
            in_hot_water_kwh=self.code_hot_water_kwh,
            in_lights_and_appliance_therms=self.code_lights_and_appliance_therms,
            in_lights_and_appliance_kwh=self.code_lights_and_appliance_kwh,
            in_fireplace_therms=self.code_fireplace_savings_therms,
        )
        return ConsumptionAdjustment(
            unadjusted=BaseCalculation(**kw),
            gas_heat=GasHeatCalculation(**kw),
            electric_heat=ElectricHeatCalculation(**kw),
        )

    def get_consumption_report(self, consumption: ConsumptionAdjustment, include_pv=True):
        vars = {
            "heating_therms": "Heating Therms",
            "heating_kwh": "Heating kWh",
            "cooling_kwh": "Cooling kWh",
            "hot_water_therms": "Water Heating Therms",
            "hot_water_kwh": "Water Heating kWh",
            "lights_and_appliance_therms": "Lights & Appliances Therms",
            "lights_and_appliance_kwh": "Lights & Appliances kWh",
            "pv_kwh": "PV kWh",
            "fireplace_therms": "Fireplace",
            None: None,
            "total_therms": "Total Therms",
            "total_kwh": "Total kWh",
            "total_mbtu": "Total MMBTU (EPS)",
        }
        table = []
        for attr, label in vars.items():
            if attr == "pv_kwh" and include_pv is False:
                continue
            if attr is None:
                table.append([])
                continue
            table.append(
                (
                    label,
                    getattr(consumption.unadjusted, attr),
                    getattr(consumption.gas_heat, attr),
                    getattr(consumption.electric_heat, attr),
                )
            )
        return tabulate(
            table, headers=["", "Unadjusted", "Gas Heat", "Electric Heat"], floatfmt=".2f"
        )

    @cached_property
    def improved_consumption(self) -> ConsumptionAdjustment:
        kw = dict(
            in_heating_therms=self.improved_heating_therms,
            in_heating_kwh=self.improved_heating_kwh,
            in_cooling_kwh=self.improved_cooling_kwh,
            in_hot_water_therms=self.improved_hot_water_therms,
            in_hot_water_kwh=self.improved_hot_water_kwh,
            in_lights_and_appliance_therms=self.improved_lights_and_appliance_therms,
            in_lights_and_appliance_kwh=self.improved_lights_and_appliance_kwh,
            in_pv_kwh=self.improved_pv_kwh,
            in_fireplace_therms=self.improved_fireplace_savings_therms,
            thermostat_heating_therms=self.thermostat_heating_therm_savings,
            thermostat_heating_kwh=self.thermostat_heating_kwh_savings,
            thermostat_cooling_kwh=self.thermostat_cooling_kwh_savings,
        )
        return ConsumptionAdjustment(
            unadjusted=BaseCalculation(**kw),
            gas_heat=GasHeatCalculation(**kw),
            electric_heat=ImprovedElectricHeatCalculation(**kw),
        )

    @cached_property
    def consumption_report(self) -> str:
        result = "Baseline Consumption Adjustment (for EPS)\n"
        result += self.get_consumption_report(self.code_consumption, False)
        result += "\n\nImproved Consumption Adjustment (for EPS)\n"
        result += self.get_consumption_report(self.improved_consumption)
        result += "\n\n"
        result += tabulate(
            [
                ['"Standard Newly Built Home" EPS', self.code_eps_score],
                ['"Your Home" EPS', self.eps_score],
            ]
        )

        return result

    @cached_property
    def eps_score(self) -> int:
        value = self.improved_consumption.electric_heat.total_mbtu
        if self.heat_type == HeatType.GAS:
            value = self.improved_consumption.gas_heat.total_mbtu
        return int(round(max([0, value]), 0))

    @cached_property
    def code_eps_score(self) -> int:
        value = self.code_consumption.electric_heat.total_mbtu
        if self.heat_type == HeatType.GAS:
            value = self.code_consumption.gas_heat.total_mbtu
        return int(round(max([0, value]), 0))
