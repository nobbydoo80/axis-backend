"""net_zero.py - Axis"""

__author__ = "Steven K"
__date__ = "12/1/21 16:32"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
from functools import cached_property

from tabulate import tabulate

from axis.customer_eto.calculator.eps_2021.base import (
    HomePath,
    AllocationIncentive,
    FuelAllocationIncentive,
)
from axis.customer_eto.calculator.eps_2021.constants import Constants
from axis.customer_eto.calculator.eps_2021.net_zero import NetZero2020
from axis.customer_eto.eep_programs.fire_rebuild_2021 import FireResilienceBonus
from axis.customer_eto.enumerations import (
    PNWUSStates,
    ElectricUtility,
    PrimaryHeatingEquipment2020,
    SmartThermostatBrands2020,
    GridHarmonization2020,
    AdditionalIncentives2020,
    SolarElements2020,
    HeatType,
    YesNo,
)

log = logging.getLogger(__name__)


class NetZeroFire2021(NetZero2020):
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
        heat_type: HeatType = None,
        fire_rebuild_qualification: YesNo = YesNo.NO,
        fire_resilience_bonus: FireResilienceBonus = FireResilienceBonus.NO,
        home_path: HomePath = None,
        whole_home_incentive: float = None,
    ):
        self.heat_type = heat_type
        self.fire_rebuild_qualification = fire_rebuild_qualification
        self.fire_resilience_bonus = fire_resilience_bonus
        super(NetZeroFire2021, self).__init__(
            total_kwh=total_kwh,
            total_therms=total_therms,
            cooling_kwh=cooling_kwh,
            pv_kwh=pv_kwh,
            percent_improvement=percent_improvement,
            percent_improvement_therms=percent_improvement_therms,
            us_state=us_state,
            constants=constants,
            electric_utility=electric_utility,
            primary_heating_class=primary_heating_class,
            thermostat_brand=thermostat_brand,
            grid_harmonization_elements=grid_harmonization_elements,
            eps_additional_incentives=eps_additional_incentives,
            solar_elements=solar_elements,
            home_path=home_path,
            whole_home_incentive=whole_home_incentive,
        )

    @cached_property
    def has_triple_pane_windows(self) -> bool:
        return any(
            [
                self.fire_resilience_bonus == FireResilienceBonus.TRIPLE_PANE,
                self.fire_resilience_bonus == FireResilienceBonus.TRIPLE_PANE_AND_RIGID_INSULATION,
                self.fire_resilience_bonus == FireResilienceBonus.TRIPLE_PANE_AND_SEALED_ATTIC,
                self.fire_resilience_bonus
                == FireResilienceBonus.TRIPLE_PANE_AND_RIGID_INSULATION_AND_SEALED_ATTIC,
            ]
        )

    @cached_property
    def has_rigid_insulation(self) -> bool:
        return any(
            [
                self.fire_resilience_bonus == FireResilienceBonus.RIGID_INSULATION,
                self.fire_resilience_bonus == FireResilienceBonus.RIGID_INSULATION_AND_SEALED_ATTIC,
                self.fire_resilience_bonus == FireResilienceBonus.TRIPLE_PANE_AND_RIGID_INSULATION,
                self.fire_resilience_bonus
                == FireResilienceBonus.TRIPLE_PANE_AND_RIGID_INSULATION_AND_SEALED_ATTIC,
            ]
        )

    @cached_property
    def has_sealed_attic(self) -> bool:
        return any(
            [
                self.fire_resilience_bonus == FireResilienceBonus.SEALED_ATTIC,
                self.fire_resilience_bonus == FireResilienceBonus.RIGID_INSULATION_AND_SEALED_ATTIC,
                self.fire_resilience_bonus == FireResilienceBonus.TRIPLE_PANE_AND_SEALED_ATTIC,
                self.fire_resilience_bonus
                == FireResilienceBonus.TRIPLE_PANE_AND_RIGID_INSULATION_AND_SEALED_ATTIC,
            ]
        )

    @cached_property
    def input_report(self) -> str:
        """This is a replication of the INPUTS tab"""
        data = super(NetZeroFire2021, self).input_report

        data += "\n\nFire Rebuild Inputs\n"

        data += tabulate(
            [
                ["Fire Rebuild?:", "Yes" if self.fire_rebuild_qualification == YesNo.YES else "No"],
                [
                    "Triple Pane Window?:",
                    "Yes" if self.has_triple_pane_windows else "No",
                ],
                [
                    "Exterior Rigid Insulation?:",
                    "Yes" if self.has_rigid_insulation else "No",
                ],
                [
                    "Sealed Attic?:",
                    "Yes" if self.has_sealed_attic else "No",
                ],
            ]
        )
        return data

    @cached_property
    def triple_pane_window_incentive(self) -> float:
        if self.fire_rebuild_qualification == YesNo.NO:
            return 0.0
        if self.has_triple_pane_windows:
            return 750.00
        return 0.0

    @cached_property
    def rigid_insulation_incentive(self) -> float:
        if self.fire_rebuild_qualification == YesNo.NO:
            return 0.0
        if self.has_rigid_insulation:
            return 750.00
        return 0.0

    @cached_property
    def sealed_attic_incentive(self) -> float:
        if self.fire_rebuild_qualification == YesNo.NO:
            return 0.0
        if self.has_sealed_attic:
            return 400.00
        return 0.0

    @cached_property
    def total_fire_resilience_incentive(self) -> float:
        return (
            self.triple_pane_window_incentive
            + self.rigid_insulation_incentive
            + self.sealed_attic_incentive
        )

    @cached_property
    def total_incentive(self) -> float:
        try:
            return (
                self.whole_home_incentive
                + self.total_nz_and_energy_smart_incentive
                + self.total_fire_resilience_incentive
            )
        except TypeError:
            raise TypeError("Set whole_home_incentive from outside")

    @cached_property
    def incentive_report(self) -> str:
        data = "Incentives\n"
        data += tabulate(
            [
                ["Net Zero", f"$ {self.net_zero_incentive:,.2f}"],
                ["Base Package", f"$ {self.energy_smart_base_package_incentive:,.2f}"],
                ["Storage Ready", f"$ {self.energy_smart_storage_ready_incentive:,.2f}"],
                ["Advanced Wiring", f"$ {self.energy_smart_advanced_wiring_incentive:,.2f}"],
                ["Bonus: Triple Pane Windows", f"$ {self.triple_pane_window_incentive:,.2f}"],
                ["Bonus: Exterior Rigid Insulation", f"$ {self.rigid_insulation_incentive:,.2f}"],
                ["Bonus: Sealed Attic", f"$ {self.sealed_attic_incentive:,.2f}"],
                ["--------------------", "--------"],
                ["NZ + ESH Total", f"$ {self.total_nz_and_energy_smart_incentive:,.2f}"],
                ["Fire Resilience Bonus Total", f"$ {self.total_fire_resilience_incentive:,.2f}"],
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
            return 11028.0 * self.percent_improvement + 3972.0
        elif self.home_path == HomePath.PATH_2:
            return 40206.0 * self.percent_improvement - 1864.0
        elif self.home_path == HomePath.PATH_3:
            return 21562.0 * self.percent_improvement + 3730.0
        elif self.home_path == HomePath.PATH_4:
            return 11276.0
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
            mad_max_str = "30-34.9%"
        elif self.home_path == HomePath.PATH_4:
            mad_max_str = ">=35"
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
    def fire_resilience_allocation(self) -> AllocationIncentive:
        """New one"""
        electric_allocation, electric_incentive = 0.0, 0.0
        gas_allocation, gas_incentive = 0.0, 0.0
        if self.heat_type == HeatType.ELECTRIC:
            allocation = electric_allocation = 1.0
            incentive = electric_incentive = self.total_fire_resilience_incentive
        else:
            allocation = gas_allocation = 1.0
            incentive = gas_incentive = self.total_fire_resilience_incentive

        electric = FuelAllocationIncentive(
            electric_allocation,
            max([0, electric_incentive]),
            "Electric",
            self.electric_utility,
            None,
            None,
        )
        gas = FuelAllocationIncentive(
            gas_allocation,
            max([0, gas_incentive]),
            "Gas",
            None,
            None,
            None,
        )

        return AllocationIncentive(
            electric,
            gas,
            allocation,
            incentive,
            None,
        )

    @cached_property
    def net_zero_allocation_report(self):
        data = "Builder EPS Net Zero Incentive and Allocations for PT"
        data += " " * 30
        data += "Builder EPS ESH Incentive and Allocations for PT\n"

        fire_allocation = self.fire_resilience_allocation.electric
        if self.heat_type == HeatType.GAS:
            fire_allocation = self.fire_resilience_allocation.gas

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
                (),
                (
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    f"{fire_allocation.allocation:.2%}",
                    f"$ {fire_allocation.incentive:,.2f}",
                    fire_allocation.fuel,
                    self.fire_resilience_allocation.electric.utility.value,
                ),
                (
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    "Builder",
                    f"{self.fire_resilience_allocation.allocation:.2%}",
                    f"$ {self.fire_resilience_allocation.incentive:,.2f}",
                    None,
                    None,
                ),
            ]
        )
        return data
