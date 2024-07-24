"""carbon.py - Axis"""

__author__ = "Steven K"
__date__ = "3/15/22 09:57"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
from dataclasses import dataclass
from functools import cached_property

from tabulate import tabulate

from axis.customer_eto.calculator.eps_2022.projected import (
    simplified_location_data_map,
    ProjectedData,
)
from axis.customer_eto.enumerations import ClimateLocation, HeatType, ElectricUtility

NATURAL_GAS_CARBON_FACTOR = 11.7
ELECTRIC_CARBON_FACTOR = 1.09
OTHER_ELECTRIC_CARBON_FACTOR = 0.067

log = logging.getLogger(__name__)


@dataclass
class CarbonScore:
    electric: float = 0.0
    gas: float = 0.0
    total: float = 0.0


@dataclass
class Carbon:
    climate_location: ClimateLocation
    heat_type: HeatType
    conditioned_area: float = 0.0
    electric_utility: ElectricUtility = ElectricUtility.NONE
    code_total_kwh: float = 0.0
    improved_total_kwh: float = 0.0
    code_total_therms: float = 0.0
    improved_total_therms: float = 0.0

    @cached_property
    def simplified_location(self):
        return simplified_location_data_map[self.climate_location]

    @cached_property
    def energy_consumption(self) -> ProjectedData:
        location = self.simplified_location
        electric_home_kwh = 0.0
        gas_home_kwh = 0.0
        gas_home_therms = 0.0
        if location == ClimateLocation.PORTLAND:
            if self.heat_type != HeatType.GAS:
                electric_home_kwh = 11874.0 + (3.52 * self.conditioned_area)
            if self.heat_type == HeatType.GAS:
                gas_home_kwh = 4700.0 + (2.39 * self.conditioned_area)
                gas_home_therms = 271.0 + (0.23 * self.conditioned_area)
        elif location == ClimateLocation.MEDFORD:
            if self.heat_type != HeatType.GAS:
                electric_home_kwh = 11141.0 + (5.08 * self.conditioned_area)
            if self.heat_type == HeatType.GAS:
                gas_home_kwh = 4700.0 + (2.39 * self.conditioned_area)
                gas_home_therms = 271.0 + (0.23 * self.conditioned_area)
        elif location == ClimateLocation.REDMOND:
            if self.heat_type != HeatType.GAS:
                electric_home_kwh = 9978.00 + (5.45 * self.conditioned_area)
            if self.heat_type == HeatType.GAS:
                gas_home_kwh = 2397.00 + (3.29 * self.conditioned_area)
                gas_home_therms = 192.0 + (0.3 * self.conditioned_area)

        return ProjectedData(location, electric_home_kwh, gas_home_kwh, gas_home_therms)

    @cached_property
    def similar_size_carbon_score(self) -> CarbonScore:
        projected = self.energy_consumption
        e_value = (
            projected.electric_home_kwh
            if self.heat_type != HeatType.GAS
            else projected.gas_home_kwh
        )

        try:
            ele_value = e_value * self.electric_factor / 2000.0
        except ZeroDivisionError:
            ele_value = 0.0

        try:
            gas_value = projected.gas_home_therms * NATURAL_GAS_CARBON_FACTOR / 2000.0
        except ZeroDivisionError:
            gas_value = 0.0

        return CarbonScore(
            electric=max([0, ele_value]),
            gas=max([0, gas_value]),
            total=max([0, ele_value + gas_value]),
        )

    @cached_property
    def electric_factor(self):
        return (
            OTHER_ELECTRIC_CARBON_FACTOR
            if self.electric_utility == ElectricUtility.NONE
            else ELECTRIC_CARBON_FACTOR
        )

    @cached_property
    def carbon_score(self) -> CarbonScore:
        electric_factor = ELECTRIC_CARBON_FACTOR  # self.electric_factor  # TODO REPORT ME

        try:
            ele_value = self.improved_total_kwh * electric_factor / 2000.0
        except ZeroDivisionError:
            ele_value = 0.0

        try:
            gas_value = self.improved_total_therms * NATURAL_GAS_CARBON_FACTOR / 2000.0
        except ZeroDivisionError:
            gas_value = 0.0

        return CarbonScore(
            electric=max([0, ele_value]),
            gas=max([0, gas_value]),
            total=max([0, ele_value + gas_value]),
        )

    @cached_property
    def code_carbon_score(self) -> CarbonScore:
        electric_factor = ELECTRIC_CARBON_FACTOR  # self.electric_factor  # TODO REPORT ME
        try:
            ele_value = self.code_total_kwh * electric_factor / 2000.0
        except ZeroDivisionError:
            ele_value = 0.0

        try:
            gas_value = self.code_total_therms * NATURAL_GAS_CARBON_FACTOR / 2000.0
        except ZeroDivisionError:
            gas_value = 0.0

        return CarbonScore(
            electric=max([0, ele_value]),
            gas=max([0, gas_value]),
            total=max([0, ele_value + gas_value]),
        )

    @cached_property
    def report(self):
        portland = (
            self.similar_size_carbon_score.electric
            if self.electric_utility == ElectricUtility.PORTLAND_GENERAL
            else None
        )
        pac = (
            self.similar_size_carbon_score.electric
            if self.electric_utility == ElectricUtility.PACIFIC_POWER
            else None
        )
        other = (
            self.similar_size_carbon_score.electric
            if self.electric_utility == ElectricUtility.NONE
            else None
        )

        data = tabulate(
            [
                ["Portland General", portland],
                ["Pacific", pac],
                ["Other/None (BPA)", other],
                ["Natural Gas", self.similar_size_carbon_score.gas],
            ],
            headers=["Projected Carbon Score", self.energy_consumption.location.value],
            floatfmt=".1f",
        )

        portland_code = (
            self.code_carbon_score.electric
            if self.electric_utility == ElectricUtility.PORTLAND_GENERAL
            else None
        )
        pac_code = (
            self.code_carbon_score.electric
            if self.electric_utility == ElectricUtility.PACIFIC_POWER
            else None
        )
        other_code = (
            self.code_carbon_score.electric
            if self.electric_utility == ElectricUtility.NONE
            else None
        )

        portland_proposed = (
            self.carbon_score.electric
            if self.electric_utility == ElectricUtility.PORTLAND_GENERAL
            else None
        )
        pac_proposed = (
            self.carbon_score.electric
            if self.electric_utility == ElectricUtility.PACIFIC_POWER
            else None
        )
        other_proposed = (
            self.carbon_score.electric if self.electric_utility == ElectricUtility.NONE else None
        )

        data += "\n\n" + tabulate(
            [
                ["Portland General", portland_code, portland_proposed],
                ["Pacific", pac_code, pac_proposed],
                ["Other/None (BPA)", other_code, other_proposed],
                ["Natural Gas", self.code_carbon_score.gas, self.carbon_score.gas],
            ],
            headers=["Carbon Score in Short tons", "Code", "Proposed"],
            floatfmt=".1f",
        )

        data += "\n\n" + tabulate(
            [
                ["Carbon Score", self.carbon_score.total],
                ["Code Carbon Score", self.code_carbon_score.total],
                ["Similar Size Carbon Score", self.similar_size_carbon_score.total],
            ],
            floatfmt=".1f",
        )
        return data
