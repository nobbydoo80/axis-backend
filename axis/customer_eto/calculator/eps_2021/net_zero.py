"""net_zero.py - Axis"""

__author__ = "Steven K"
__date__ = "9/17/21 07:30"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
from functools import cached_property

from tabulate import tabulate

from ...enumerations import (
    GridHarmonization2020,
    AdditionalIncentives2020,
    SolarElements2020,
    ElectricUtility,
    PrimaryHeatingEquipment2020,
    SmartThermostatBrands2020,
    PNWUSStates,
)
from .constants import Constants
from .base import HomePath, FuelAllocationIncentive, AllocationIncentive

log = logging.getLogger(__name__)


class NetZero2020:
    def __init__(
        self,
        total_kwh: float,
        total_therms: float,
        cooling_kwh: float,
        pv_kwh: float,
        percent_improvement: float,
        percent_improvement_therms: float,
        us_state: PNWUSStates,
        constants: Constants,
        electric_utility: ElectricUtility,
        primary_heating_class: PrimaryHeatingEquipment2020,
        thermostat_brand: SmartThermostatBrands2020 = SmartThermostatBrands2020.NONE,
        grid_harmonization_elements: GridHarmonization2020 = GridHarmonization2020.NONE,
        eps_additional_incentives: AdditionalIncentives2020 = AdditionalIncentives2020.NO,
        solar_elements: SolarElements2020 = SolarElements2020.NONE,
        home_path: HomePath = None,
        whole_home_incentive: float = None,
    ):
        self.total_kwh = total_kwh
        self.total_therms = total_therms
        self.cooling_kwh = cooling_kwh
        self.pv_kwh = pv_kwh
        self.percent_improvement = percent_improvement
        self.percent_improvement_therms = percent_improvement_therms
        self.electric_utility = electric_utility
        self.primary_heating_class = primary_heating_class
        self.thermostat_brand = thermostat_brand
        self.grid_harmonization_elements = grid_harmonization_elements
        self.eps_additional_incentives = eps_additional_incentives
        self.solar_elements = solar_elements
        self.us_state = us_state
        self.constants = constants
        # These will need to be set up
        self.home_path = home_path
        self.whole_home_incentive = whole_home_incentive

    @cached_property
    def qualifies_for_net_zero(self) -> bool:
        return all(self._net_zero_elements.values())

    @cached_property
    def _net_zero_elements(self) -> dict:
        valid_utilities = [ElectricUtility.PACIFIC_POWER, ElectricUtility.PORTLAND_GENERAL]
        return {
            "Qualifying State": self.us_state != PNWUSStates.WA,
            "Valid Utility": self.electric_utility in valid_utilities,
            "Overall % Improvement": self.percent_improvement >= 0.2,
            "Acceptable Therms": self.total_therms == 0.0 or self.percent_improvement_therms >= 0.2,
            "PV Generation": self.pv_kwh >= self.total_kwh,
            "Valid Solar Elements": self.solar_elements == SolarElements2020.SOLAR_PV,
        }

    @cached_property
    def smart_thermostat_requirement_met(self) -> bool:
        return any(
            [
                self.thermostat_brand == SmartThermostatBrands2020.ECOBEE3,
                self.thermostat_brand == SmartThermostatBrands2020.ECOBEE4,
                self.thermostat_brand == SmartThermostatBrands2020.ECOBEE_VOICE,
                self.thermostat_brand == SmartThermostatBrands2020.NEST_E,
                self.thermostat_brand == SmartThermostatBrands2020.NEST_LEARNING,
            ]
        )

    @cached_property
    def solar_exempt(self) -> bool:
        return any(
            [
                self.eps_additional_incentives == AdditionalIncentives2020.ENERGY_SMART,
                self.eps_additional_incentives
                == AdditionalIncentives2020.AFFORDABLE_HOUSING_AND_ENERGY_SMART,
            ]
        )

    @cached_property
    def mini_split(self) -> bool:
        return any(
            [
                self.primary_heating_class == PrimaryHeatingEquipment2020.MINI_SPLIT_MIXED,
                self.primary_heating_class == PrimaryHeatingEquipment2020.MINI_SPLIT_DUCTED,
                self.primary_heating_class == PrimaryHeatingEquipment2020.MINI_SPLIT_NON_DUCTED,
            ]
        )

    @cached_property
    def _esh_base_elements(self) -> dict:
        valid_utilities = [ElectricUtility.PACIFIC_POWER, ElectricUtility.PORTLAND_GENERAL]
        return {
            "Qualifying State": self.us_state != PNWUSStates.WA,
            "Valid Utility": self.electric_utility in valid_utilities,
            "Valid Thermostat w/cooling": self.smart_thermostat_requirement_met
            and self.cooling_kwh > 0.0,
            "Mini-Split": self.mini_split,
        }

    @cached_property
    def qualifies_for_esh_base(self) -> bool:
        data = self._esh_base_elements
        return all(
            [
                data["Qualifying State"],
                data["Valid Utility"],
                any([data["Valid Thermostat w/cooling"], data["Mini-Split"]]),
            ]
        )

    @cached_property
    def input_report(self) -> str:
        data = "Net Zero & Energy Smart Home Inputs\n"
        esh_base = ", ".join([k for k, v in self._esh_base_elements.items() if not v])
        data += tabulate(
            [
                [
                    "Net Zero",
                    "Net Zero" if self.qualifies_for_net_zero else "No",
                    ", ".join([k for k, v in self._net_zero_elements.items() if not v]),
                ],
                [
                    "Checklist ESH",
                    self.grid_harmonization_elements.value,
                    "",
                ],
                [
                    "ESH Smart Thermostat",
                    "Yes" if self.smart_thermostat_requirement_met else "No",
                    "" if self.smart_thermostat_requirement_met else self.thermostat_brand.value,
                ],
                [
                    "Solar Exempt",
                    "Yes" if self.solar_exempt else "No",
                    "" if self.solar_exempt else self.eps_additional_incentives.value,
                ],
                [
                    "Mini Split",
                    "Yes" if self.mini_split else "No",
                    "" if self.mini_split else self.primary_heating_class.value,
                ],
                [
                    "Qualifies for ESH Base",
                    "Yes" if self.qualifies_for_esh_base else "No",
                    "" if self.qualifies_for_esh_base else esh_base,
                ],
            ],
            headers=["Label", "Status", "Inputs / Missing"],
        )

        return data

    @cached_property
    def net_zero_incentive(self) -> float:
        "C3"
        if self.qualifies_for_net_zero:
            return 750.00
        return 0.0

    @cached_property
    def energy_smart_base_package_incentive(self):
        value = 0.0
        if (
            self.qualifies_for_esh_base
            and self.grid_harmonization_elements != GridHarmonization2020.NONE
        ):
            value = 200.00
        return value

    @cached_property
    def energy_smart_storage_ready_incentive(self):
        value = 0.0
        if self.energy_smart_base_package_incentive:
            if not self.solar_exempt and self.grid_harmonization_elements in [
                GridHarmonization2020.STORAGE,
                GridHarmonization2020.ALL,
            ]:
                value += 150.00
        return value

    @cached_property
    def energy_smart_advanced_wiring_incentive(self):
        value = 0.0
        if self.energy_smart_base_package_incentive:
            if self.grid_harmonization_elements in [
                GridHarmonization2020.WIRING,
                GridHarmonization2020.ALL,
            ]:
                value += 150.00
        return value

    @cached_property
    def energy_smart_incentive(self) -> float:
        "C4"
        return (
            self.energy_smart_base_package_incentive
            + self.energy_smart_storage_ready_incentive
            + self.energy_smart_advanced_wiring_incentive
        )

    @cached_property
    def total_nz_and_energy_smart_incentive(self) -> float:
        return self.net_zero_incentive + self.energy_smart_incentive

    @cached_property
    def total_incentive(self) -> float:
        try:
            return self.whole_home_incentive + self.total_nz_and_energy_smart_incentive
        except TypeError:
            raise TypeError("Set whole_home_incentive from outside")

    @cached_property
    def incentive_report(self) -> str:
        data = "Incentives\n"
        data += tabulate(
            [
                ["Net Zero", f"$ {self.net_zero_incentive:,.2f}"],
                ["Energy Smart Homes", f"$ {self.energy_smart_incentive:,.2f}"],
                ["--------------------", "--------"],
                ["NZ + ESH Total", f"$ {self.total_nz_and_energy_smart_incentive:,.2f}"],
                ["Whole Home Incentive", f"$ {self.whole_home_incentive:,.2f}"],
                ["--------------------", "--------"],
                ["TOTAL INCENTIVE", f"$ {self.total_incentive:,.2f}"],
            ]
        )
        return data

    @cached_property
    def home_max_incentive(self) -> float:
        """Provide a home path and a builder incentive this will crank out the max builder
        incentive"""
        if self.home_path == HomePath.PATH_1:
            return 13310.0 * self.percent_improvement + 255.0
        elif self.home_path == HomePath.PATH_2:
            return 5920.0 * self.percent_improvement + 1733.0
        elif self.home_path == HomePath.PATH_3:
            return 23020.0 * self.percent_improvement + -3397.0
        elif self.home_path == HomePath.PATH_4:
            return 5811.0
        return 0.0

    @cached_property
    def mad_max_report(self) -> str:
        data = "MAD Max Incentive\n"
        mad_max_str = "--"
        if self.home_path == HomePath.PATH_1:
            mad_max_str = "10-19.9%"
        elif self.home_path == HomePath.PATH_2:
            mad_max_str = "20-29.9%"
        elif self.home_path == HomePath.PATH_3:
            mad_max_str = "30-39.9%"
        elif self.home_path == HomePath.PATH_4:
            mad_max_str = ">=40"
        elif self.home_path is None:
            mad_max_str = f"ERROR {self.percent_improvement:.1%} improvement!"
        data += tabulate(
            [
                [mad_max_str, f"$ {self.home_max_incentive:,.2f}"],
                ["This home's max incentive", f"$ {self.home_max_incentive:,.2f}"],
            ]
        )
        return data

    @cached_property
    def solar_allocation(self) -> float:
        return max([0, self.total_incentive - self.home_max_incentive])

    @cached_property
    def eps_allocation(self) -> float:
        return self.total_nz_and_energy_smart_incentive - self.solar_allocation

    @cached_property
    def incentive_allocation_report(self) -> str:
        data = "Incentive Allocations (EPS vs Solar)\n"
        data += tabulate(
            [
                ["EPS (PGE/PAC)", f"$ {self.eps_allocation:,.2f}"],
                ["Solar", f"$ {self.solar_allocation:,.2f}"],
            ]
        )
        return data

    @cached_property
    def net_zero_eps_builder_allocation(self) -> AllocationIncentive:
        """Top Left"""
        electric_allocation = 0.0
        if self.net_zero_incentive:
            electric_allocation = 1.0

        try:
            electric_incentive = (
                self.net_zero_incentive
                / self.total_nz_and_energy_smart_incentive
                * self.eps_allocation
            )
        except ZeroDivisionError:
            electric_incentive = 0.0

        electric = FuelAllocationIncentive(
            electric_allocation,
            max([0, electric_incentive]),
            "Electric",
            self.electric_utility,
            None,
            None,
        )
        gas = FuelAllocationIncentive(
            0,
            0,
            "Gas",
            None,
            None,
            None,
        )
        return AllocationIncentive(
            electric,
            gas,
            electric_allocation,
            electric_incentive,
            None,
        )

    @cached_property
    def net_zero_energy_smart_homes_builder_eps_allocation(self) -> AllocationIncentive:
        """Top Right"""
        electric_allocation = 0.0
        if self.energy_smart_incentive:
            electric_allocation = 1.0

        try:
            electric_incentive = (
                self.energy_smart_incentive
                / self.total_nz_and_energy_smart_incentive
                * self.eps_allocation
            )
        except ZeroDivisionError:
            electric_incentive = 0.0

        electric = FuelAllocationIncentive(
            electric_allocation,
            max([0, electric_incentive]),
            "Electric",
            self.electric_utility,
            None,
            None,
        )
        gas = FuelAllocationIncentive(
            0,
            0,
            "Gas",
            None,
            None,
            None,
        )
        return AllocationIncentive(
            electric,
            gas,
            electric_allocation,
            electric_incentive,
            None,
        )

    @cached_property
    def net_zero_solar_builder_allocation(self) -> AllocationIncentive:
        """Bottom Left"""
        electric_allocation = 0.0
        if self.net_zero_incentive:
            electric_allocation = 1.0

        try:
            electric_incentive = (
                self.net_zero_incentive
                / self.total_nz_and_energy_smart_incentive
                * self.solar_allocation
            )
        except ZeroDivisionError:
            electric_incentive = 0.0

        electric = FuelAllocationIncentive(
            electric_allocation,
            max([0, electric_incentive]),
            "Electric",
            self.electric_utility,
            None,
            None,
        )
        gas = FuelAllocationIncentive(
            0,
            0,
            "Gas",
            None,
            None,
            None,
        )
        return AllocationIncentive(
            electric,
            gas,
            electric_allocation,
            electric_incentive,
            None,
        )

    @cached_property
    def net_zero_energy_smart_homes_builder_solar_allocation(self) -> AllocationIncentive:
        """Bottom Right"""
        electric_allocation = 0.0
        if self.energy_smart_incentive:
            electric_allocation = 1.0

        try:
            electric_incentive = (
                self.energy_smart_incentive
                / self.total_nz_and_energy_smart_incentive
                * self.solar_allocation
            )
        except ZeroDivisionError:
            electric_incentive = 0.0

        electric = FuelAllocationIncentive(
            electric_allocation,
            max([0, electric_incentive]),
            "Electric",
            self.electric_utility,
            None,
            None,
        )
        gas = FuelAllocationIncentive(
            0,
            0,
            "Gas",
            None,
            None,
            None,
        )
        return AllocationIncentive(
            electric,
            gas,
            electric_allocation,
            electric_incentive,
            None,
        )

    @cached_property
    def net_zero_allocation_report(self):
        data = "Builder EPS Net Zero Incentive and Allocations for PT"
        data += " " * 40
        data += "Builder EPS ESH Incentive and Allocations for PT\n"
        data += tabulate(
            [
                (
                    None,
                    f"{self.net_zero_eps_builder_allocation.electric.allocation:.2%}",
                    f"$ {self.net_zero_eps_builder_allocation.electric.incentive:,.2f}",
                    self.net_zero_eps_builder_allocation.electric.fuel,
                    self.net_zero_eps_builder_allocation.electric.utility.value,
                    " " * 5,
                    None,
                    f"{self.net_zero_energy_smart_homes_builder_eps_allocation.electric.allocation:.2%}",
                    f"$ {self.net_zero_energy_smart_homes_builder_eps_allocation.electric.incentive:,.2f}",
                    self.net_zero_energy_smart_homes_builder_eps_allocation.electric.fuel,
                    self.net_zero_energy_smart_homes_builder_eps_allocation.electric.utility.value,
                ),
                (
                    "Builder",
                    f"{self.net_zero_eps_builder_allocation.allocation:.2%}",
                    f"$ {self.net_zero_eps_builder_allocation.incentive:,.2f}",
                    None,
                    None,
                    None,
                    "Builder",
                    f"{self.net_zero_energy_smart_homes_builder_eps_allocation.allocation:.2%}",
                    f"$ {self.net_zero_energy_smart_homes_builder_eps_allocation.incentive:,.2f}",
                    None,
                    None,
                ),
                (),
                (
                    None,
                    f"{self.net_zero_solar_builder_allocation.electric.allocation:.2%}",
                    f"$ {self.net_zero_solar_builder_allocation.electric.incentive:,.2f}",
                    self.net_zero_solar_builder_allocation.electric.fuel,
                    self.net_zero_solar_builder_allocation.electric.utility.value,
                    None,
                    None,
                    f"{self.net_zero_energy_smart_homes_builder_solar_allocation.electric.allocation:.2%}",
                    f"$ {self.net_zero_energy_smart_homes_builder_solar_allocation.electric.incentive:,.2f}",
                    self.net_zero_energy_smart_homes_builder_solar_allocation.electric.fuel,
                    self.net_zero_energy_smart_homes_builder_solar_allocation.electric.utility.value,
                ),
                (
                    "Builder",
                    f"{self.net_zero_solar_builder_allocation.allocation:.2%}",
                    f"$ {self.net_zero_solar_builder_allocation.incentive:,.2f}",
                    None,
                    None,
                    None,
                    "Builder",
                    f"{self.net_zero_energy_smart_homes_builder_solar_allocation.allocation:.2%}",
                    f"$ {self.net_zero_energy_smart_homes_builder_solar_allocation.incentive:,.2f}",
                    None,
                    None,
                ),
            ]
        )
        return data
