"""projected.py - Axis"""

__author__ = "Steven K"
__date__ = "3/4/22 11:17"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
from dataclasses import dataclass
from functools import cached_property

from tabulate import tabulate

from simulation.enumerations import EnergyUnit
from simulation.utils.conversions import convert_kwh_to, convert_therm_to

from axis.customer_eto.enumerations import (
    ClimateLocation,
    HeatType,
    ElectricUtility,
    GasUtility,
)

log = logging.getLogger(__name__)


@dataclass
class ProjectedData:
    location: ClimateLocation
    electric_home_kwh: float = (0.0,)
    gas_home_kwh: float = (0.0,)
    gas_home_therms: float = (0.0,)


simplified_location_data_map = {
    ClimateLocation.ASTORIA: ClimateLocation.PORTLAND,
    ClimateLocation.BURNS: ClimateLocation.REDMOND,
    ClimateLocation.EUGENE: ClimateLocation.PORTLAND,
    ClimateLocation.MEDFORD: ClimateLocation.MEDFORD,
    ClimateLocation.NORTH_BEND: ClimateLocation.PORTLAND,
    ClimateLocation.PENDLETON: ClimateLocation.REDMOND,
    ClimateLocation.PORTLAND: ClimateLocation.PORTLAND,
    ClimateLocation.REDMOND: ClimateLocation.REDMOND,
    ClimateLocation.SALEM: ClimateLocation.PORTLAND,
}


@dataclass
class Projected:
    climate_location: ClimateLocation
    heat_type: HeatType
    conditioned_area: float = 0.0
    electric_utility: ElectricUtility = ElectricUtility.NONE
    gas_utility: GasUtility = GasUtility.NONE

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

        return ProjectedData(location, electric_home_kwh, gas_home_kwh, gas_home_therms)

    @cached_property
    def similar_size_eps(self) -> float:
        projected = self.energy_consumption
        if self.heat_type == HeatType.GAS:
            return int(
                round(
                    sum(
                        [
                            convert_kwh_to(projected.gas_home_kwh, EnergyUnit.MBTU),
                            convert_therm_to(projected.gas_home_therms, EnergyUnit.MBTU),
                        ]
                    ),
                    0,
                )
            )
        return int(round(convert_kwh_to(projected.electric_home_kwh, EnergyUnit.MBTU), 0))

    @cached_property
    def projected_report(self) -> str:
        return tabulate(
            [
                ["Electric Home - kWh", self.energy_consumption.electric_home_kwh],
                ["Gas Home - kWh", self.energy_consumption.gas_home_kwh],
                ["Gas Home - therms", self.energy_consumption.gas_home_therms],
                [],
                ['"Similar Size Existing Home" EPS', self.similar_size_eps],
            ],
            headers=["", self.energy_consumption.location.value],
            floatfmt=".0f",
        )
