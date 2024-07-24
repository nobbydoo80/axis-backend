"""projected.py - Axis"""

__author__ = "Steven K"
__date__ = "9/15/21 16:23"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
from functools import cached_property
from tabulate import tabulate

from axis.customer_eto.calculator.eps_2021.base import Projected, round_value, CarbonData
from axis.customer_eto.calculator.eps_2021.constants import Constants
from axis.customer_eto.enumerations import HeatType, ClimateLocation, ElectricUtility, GasUtility
from simulation.enumerations import EnergyUnit
from simulation.utils.conversions import convert_kwh_to, convert_therm_to

log = logging.getLogger(__name__)


class Projected2021:
    def __init__(
        self,
        climate_location: ClimateLocation,
        heat_type: HeatType,
        conditioned_area: float,
        electric_utility: ElectricUtility,
        gas_utility: GasUtility,
        constants: Constants,
    ):
        self.climate_location = climate_location
        self.heat_type = heat_type
        self.conditioned_area = conditioned_area
        self.electric_utility = electric_utility
        self.gas_utility = gas_utility
        self.constants = constants

    @cached_property
    def projected_energy_consumption(self) -> Projected:
        location = self.constants.get_simplified_location(self.climate_location)

        electric_home_kwh = 0.0
        gas_home_kwh = 0.0
        gas_home_therms = 0.0
        if location == ClimateLocation.PORTLAND:
            if self.heat_type != HeatType.GAS:
                electric_home_kwh = 23520.0 + (5.54 * self.conditioned_area)
            if self.heat_type == HeatType.GAS:
                gas_home_kwh = 4700.0 + (2.39 * self.conditioned_area)
                gas_home_therms = 271.0 + (0.23 * self.conditioned_area)
        elif location == ClimateLocation.MEDFORD:
            if self.heat_type != HeatType.GAS:
                electric_home_kwh = 20806.0 + (7.74 * self.conditioned_area)
            if self.heat_type == HeatType.GAS:
                gas_home_kwh = 4700.0 + (2.39 * self.conditioned_area)
                gas_home_therms = 271.0 + (0.23 * self.conditioned_area)
        elif location == ClimateLocation.REDMOND:
            if self.heat_type != HeatType.GAS:
                electric_home_kwh = 19320.00 + (9.96 * self.conditioned_area)
            if self.heat_type == HeatType.GAS:
                gas_home_kwh = 2397.00 + (3.29 * self.conditioned_area)
                gas_home_therms = 192.0 + (0.3 * self.conditioned_area)

        return Projected(location, electric_home_kwh, gas_home_kwh, gas_home_therms)

    @cached_property
    def projected_energy_consumption_mbtu(self) -> Projected:
        projected = self.projected_energy_consumption
        return Projected(
            projected.location,
            convert_kwh_to(projected.electric_home_kwh, EnergyUnit.MBTU),
            convert_kwh_to(projected.gas_home_kwh, EnergyUnit.MBTU),
            convert_therm_to(projected.gas_home_therms, EnergyUnit.MBTU),
        )

    @cached_property
    def similar_size_eps(self) -> float:
        projected = self.projected_energy_consumption_mbtu
        return sum(
            [
                projected.electric_home_kwh,
                projected.gas_home_kwh,
                projected.gas_home_therms,
            ]
        )

    @cached_property
    def projected_carbon_consumption(self) -> Projected:
        location = self.constants.get_simplified_location(self.climate_location)

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

        return Projected(location, electric_home_kwh, gas_home_kwh, gas_home_therms)

    @cached_property
    def similar_size_carbon_data(self) -> CarbonData:
        projected = self.projected_carbon_consumption

        electric_score, gas_score = 0.0, 0.0
        if projected.location and self.electric_utility:
            electric_score = projected.electric_home_kwh + projected.gas_home_kwh
            electric_score *= self.constants.improved_electric_carbon_factor
            electric_score /= 2000.00
        if projected.location and self.gas_utility:
            gas_score = projected.gas_home_therms * self.constants.natural_gas_carbon_factor
            gas_score /= 2000.00
        return CarbonData(
            projected.location, self.electric_utility, electric_score, self.gas_utility, gas_score
        )

    @cached_property
    def similar_size_carbon(self) -> float:
        data = self.similar_size_carbon_data
        return sum([data.electric_score, data.gas_score])

    @cached_property
    def projected_consumption_report(self) -> str:
        data = "\nFactors for EPS\n\n"
        data += tabulate(
            [
                [
                    self.conditioned_area,
                    self.climate_location.value,
                    self.heat_type.value,
                    self.electric_utility.value,
                    self.gas_utility.value,
                ],
            ],
            headers=["Square Ft", "Location", "Heating", "Electric", "Gas"],
            floatfmt=f".{round_value}f",
        )

        data += f"\n\nProjected Energy Consumption ({self.climate_location.value})\n\n"
        data += tabulate(
            [
                [
                    self.projected_energy_consumption.electric_home_kwh,
                    self.projected_energy_consumption.gas_home_kwh,
                    self.projected_energy_consumption.gas_home_therms,
                ],
            ],
            headers=["Electric kWh", "Gas kWh", "Gas Therms"],
            floatfmt=f".{round_value}f",
        )

        data += f"\n\nProjected Energy Consumption in MBtu ({self.climate_location.value})\n\n"
        data += tabulate(
            [
                [
                    self.projected_energy_consumption_mbtu.electric_home_kwh,
                    self.projected_energy_consumption_mbtu.gas_home_kwh,
                    self.projected_energy_consumption_mbtu.gas_home_therms,
                ],
            ],
            headers=["Location", "Electric kWh", "Gas kWh", "Gas Therms"],
            floatfmt=f".{round_value}f",
        )

        data += f"\n\n\tSimilar Size OR EPS Home:\t{self.similar_size_eps:.{round_value}f}\n"

        data += f"\n\nProjected Energy Consumption CARBON ({self.climate_location.value})\n\n"
        data += tabulate(
            [
                [
                    self.projected_carbon_consumption.electric_home_kwh,
                    self.projected_carbon_consumption.gas_home_kwh,
                    self.projected_carbon_consumption.gas_home_therms,
                ],
            ],
            headers=["Electric kWh", "Gas kWh", "Gas Therms"],
            floatfmt=f".{round_value}f",
        )

        data += f"\n\nProjected Carbon Score ({self.climate_location.value})\n\n"
        data += tabulate(
            [
                [
                    self.similar_size_carbon_data.electric_score,
                    self.similar_size_carbon_data.gas_score,
                ],
            ],
            headers=[
                f"{self.similar_size_carbon_data.electric_utility.value}",
                f"{self.similar_size_carbon_data.gas_utility.value}",
            ],
            floatfmt=f".{round_value}f",
        )

        data += f"\n\n\tSimilar Size OR Home Carbon:\t{self.similar_size_carbon:.{round_value}f}\n"

        return data
