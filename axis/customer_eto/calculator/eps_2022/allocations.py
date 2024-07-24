"""allocations.py - Axis"""

__author__ = "Steven K"
__date__ = "3/3/22 15:00"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
from dataclasses import dataclass
from functools import cached_property
from typing import Union

from simulation.enumerations import FuelType
from tabulate import tabulate

from axis.customer_eto.calculator.eps_2021.base import (
    HomePath,
    HomeSubType,
    LoadProfile,
    ElectricLoadProfile,
    GasLoadProfile,
)
from axis.customer_eto.calculator.eps_2022.incentives import IncentiveItem
from axis.customer_eto.enumerations import ElectricUtility, GasUtility, HeatType

log = logging.getLogger(__name__)


@dataclass
class FuelAllocationComponent:
    fuel: FuelType
    utility: Union[ElectricUtility, GasUtility]
    load_profile: Union[ElectricLoadProfile, GasLoadProfile]
    allocation: float
    measure_life: float
    builder_incentive: float
    verifier_incentive: float


@dataclass
class ProjectTrackerAllocation:
    slug: str
    label: str
    electric: float = 0.0
    gas: float = 0.0
    sle: float = 0.0

    @property
    def total(self) -> float:
        return self.gas + self.electric + self.sle

    @property
    def total_str(self):
        return f"$ {self.total:.2f}" if self.total != 0 else None

    @property
    def gas_str(self):
        return f"$ {self.gas:.2f}" if self.gas != 0 else None

    @property
    def electric_str(self):
        return f"$ {self.electric:.2f}" if self.electric != 0 else None

    @property
    def sle_str(self):
        return f"$ {self.sle:.2f}" if self.sle != 0 else None


@dataclass
class ProjectTrackerTotal:
    electric_utility: ElectricUtility
    gas_utility: GasUtility
    electric_incentive: float = 0.0
    gas_incentive: float = 0.0
    solar_incentive: float = 0.0

    @property
    def gas_incentive_str(self):
        return f"$ {self.gas_incentive:,.2f}"

    @property
    def electric_incentive_str(self):
        return f"$ {self.electric_incentive:,.2f}"

    @property
    def solar_incentive_str(self):
        return f"$ {self.solar_incentive:,.2f}"

    @property
    def total(self):
        return self.electric_incentive + self.gas_incentive + self.solar_incentive

    @property
    def total_str(self):
        return f"$ {self.total:,.2f}"


@dataclass
class Allocation:
    percent_improvement: float
    heat_type: HeatType
    heating_therms: float = 0.0
    hot_water_therms: float = 0.0
    electric_utility: ElectricUtility = ElectricUtility.NONE
    gas_utility: GasUtility = GasUtility.NONE
    builder_base_incentive: float = 0.0
    builder_additional_incentives: list[IncentiveItem] = None
    verifier_base_incentive: float = 0.0
    verifier_additional_incentives: list[IncentiveItem] = None

    @cached_property
    def home_path(self) -> HomePath:
        """
        =IFS(
        AND(C18>=0.1,C18<0.2),"Path 1",
        AND(C18>=0.2,C18<0.3),"Path 2",
        AND(C18>=0.3,C18<0.35),"Path 3",
        C18>=0.35,"Path 4")
        """

        if 0.2 > self.percent_improvement >= 0.10:
            return HomePath.PATH_1
        elif 0.3 > self.percent_improvement >= 0.20:
            return HomePath.PATH_2
        elif 0.35 > self.percent_improvement >= 0.30:
            return HomePath.PATH_3
        elif self.percent_improvement >= 0.35:
            return HomePath.PATH_4
        return HomePath.UNDEFINED

    @cached_property
    def sub_type(self) -> HomeSubType:
        """Combined them to simplify"""
        if self.heating_therms > 0.0 and self.hot_water_therms > 0.0:
            return HomeSubType.GHGW
        if self.heating_therms == 0.0 and self.hot_water_therms == 0.0:
            return HomeSubType.EHEW
        if self.heating_therms > 0.0 and self.hot_water_therms == 0.0:
            return HomeSubType.GHEW
        if self.heating_therms == 0.0 and self.hot_water_therms > 0.0:
            return HomeSubType.EHGW

    def get_default_load_profile_data(self) -> dict:
        return {
            # Path 1
            (HomePath.PATH_1, HomeSubType.EHEW): LoadProfile(
                ElectricLoadProfile.RESIDENTIAL_ASHP,
                GasLoadProfile.NONE,
                37.0,
                1.0,
                0.0,
            ),
            (HomePath.PATH_1, HomeSubType.EHGW): LoadProfile(
                ElectricLoadProfile.RESIDENTIAL_ASHP,
                GasLoadProfile.HOT_WATER,
                38.0,
                0.940,
                0.060,
            ),
            (HomePath.PATH_1, HomeSubType.GHEW): LoadProfile(
                ElectricLoadProfile.RESIDENTIAL_WATER_HEAT,
                GasLoadProfile.RESIDENTIAL_HEATING,
                35.0,
                0.190,
                0.810,
            ),
            (HomePath.PATH_1, HomeSubType.GHGW): LoadProfile(
                ElectricLoadProfile.RESIDENTIAL_CENTRAL_AC,
                GasLoadProfile.RESIDENTIAL_HEATING,
                36.0,
                0.130,
                0.870,
            ),
            # Path 2
            (HomePath.PATH_2, HomeSubType.EHEW): LoadProfile(
                ElectricLoadProfile.RESIDENTIAL_ASHP,
                GasLoadProfile.NONE,
                30.0,
                1.0,
                0.0,
            ),
            (HomePath.PATH_2, HomeSubType.EHGW): LoadProfile(
                ElectricLoadProfile.RESIDENTIAL_ASHP,
                GasLoadProfile.HOT_WATER,
                34.0,
                0.690,
                0.310,
            ),
            (HomePath.PATH_2, HomeSubType.GHEW): LoadProfile(
                ElectricLoadProfile.RESIDENTIAL_WATER_HEAT,
                GasLoadProfile.RESIDENTIAL_HEATING,
                27.0,
                0.620,
                0.380,
            ),
            (HomePath.PATH_2, HomeSubType.GHGW): LoadProfile(
                ElectricLoadProfile.RESIDENTIAL_CENTRAL_AC,
                GasLoadProfile.RESIDENTIAL_HEATING,
                32.0,
                0.080,
                0.920,
            ),
            # Path 3
            (HomePath.PATH_3, HomeSubType.EHEW): LoadProfile(
                ElectricLoadProfile.RESIDENTIAL_ASHP,
                GasLoadProfile.NONE,
                36.0,
                1.0,
                0.0,
            ),
            (HomePath.PATH_3, HomeSubType.EHGW): LoadProfile(
                ElectricLoadProfile.RESIDENTIAL_ASHP,
                GasLoadProfile.HOT_WATER,
                39.0,
                0.790,
                0.210,
            ),
            (HomePath.PATH_3, HomeSubType.GHEW): LoadProfile(
                ElectricLoadProfile.RESIDENTIAL_WATER_HEAT,
                GasLoadProfile.RESIDENTIAL_HEATING,
                34.0,
                0.410,
                0.590,
            ),
            (HomePath.PATH_3, HomeSubType.GHGW): LoadProfile(
                ElectricLoadProfile.RESIDENTIAL_CENTRAL_AC,
                GasLoadProfile.RESIDENTIAL_HEATING,
                38.0,
                0.040,
                0.960,
            ),
            # Path 4
            (HomePath.PATH_4, HomeSubType.EHEW): LoadProfile(
                ElectricLoadProfile.RESIDENTIAL_ASHP,
                GasLoadProfile.NONE,
                34.0,
                1.0,
                0.0,
            ),
            (HomePath.PATH_4, HomeSubType.EHGW): LoadProfile(
                ElectricLoadProfile.RESIDENTIAL_ASHP,
                GasLoadProfile.HOT_WATER,
                37.0,
                0.800,
                0.200,
            ),
            (HomePath.PATH_4, HomeSubType.GHEW): LoadProfile(
                ElectricLoadProfile.RESIDENTIAL_WATER_HEAT,
                GasLoadProfile.RESIDENTIAL_HEATING,
                35.0,
                0.410,
                0.590,
            ),
            (HomePath.PATH_4, HomeSubType.GHGW): LoadProfile(
                ElectricLoadProfile.RESIDENTIAL_CENTRAL_AC,
                GasLoadProfile.RESIDENTIAL_HEATING,
                38.0,
                0.080,
                0.920,
            ),
        }

    @cached_property
    def partial_territory(self):
        """=IF(C10="Other/None","Partial","Full")"""
        return self.electric_utility == ElectricUtility.NONE

    def get_partial_load_profile_data(self):
        return {
            HomeSubType.GHEW: LoadProfile(
                ElectricLoadProfile.NONE,
                GasLoadProfile.NONE,
                0.0,
                0.450,
                0.550,
            ),
            HomeSubType.GHGW: LoadProfile(
                ElectricLoadProfile.NONE,
                GasLoadProfile.NONE,
                0.0,
                0.110,
                0.890,
            ),
        }

    @cached_property
    def load_profile(self) -> LoadProfile:
        try:
            default = self.get_default_load_profile_data()[self.home_path, self.sub_type]
        except KeyError:
            default = LoadProfile(ElectricLoadProfile.NONE, GasLoadProfile.NONE, 0.0, 0.0, 0.0)
        if self.partial_territory:
            try:
                data = self.get_partial_load_profile_data()[self.sub_type]
                return LoadProfile(
                    default.electric_load_profile,
                    default.gas_load_profile,
                    default.weighted_avg_measure_life,
                    data.electric_allocation,
                    data.gas_allocation,
                )
            except KeyError:
                return LoadProfile(
                    ElectricLoadProfile.NONE,
                    GasLoadProfile.NONE,
                    default.weighted_avg_measure_life,
                    0.0,
                    0.0,
                )
        return default

    @cached_property
    def allocation_data(self) -> list[FuelAllocationComponent]:
        load_profile = self.load_profile
        electric_allocation = load_profile.electric_allocation
        gas_allocation = load_profile.gas_allocation
        return [
            FuelAllocationComponent(
                fuel=FuelType.ELECTRIC,
                utility=self.electric_utility,
                load_profile=load_profile.electric_load_profile,
                allocation=electric_allocation,
                measure_life=load_profile.weighted_avg_measure_life,
                builder_incentive=0.0
                if self.electric_utility == ElectricUtility.NONE
                else self.builder_base_incentive * electric_allocation,
                verifier_incentive=0.0
                if self.partial_territory
                else self.verifier_base_incentive * electric_allocation,
            ),
            FuelAllocationComponent(
                fuel=FuelType.NATURAL_GAS,
                utility=self.gas_utility,
                load_profile=load_profile.gas_load_profile,
                allocation=gas_allocation,
                measure_life=load_profile.weighted_avg_measure_life,
                builder_incentive=0.0
                if self.gas_utility == GasUtility.NONE
                else self.builder_base_incentive * gas_allocation,
                verifier_incentive=self.verifier_base_incentive
                if self.partial_territory
                else self.verifier_base_incentive * gas_allocation,
            ),
        ]

    @cached_property
    def electric(self) -> FuelAllocationComponent:
        return next((x for x in self.allocation_data if x.fuel == FuelType.ELECTRIC))

    @cached_property
    def gas(self) -> FuelAllocationComponent:
        return next((x for x in self.allocation_data if x.fuel == FuelType.NATURAL_GAS))

    @cached_property
    def _bonus_builder_allocation_dict(self) -> dict:
        b_allocation_dict = dict()
        for item in self.builder_additional_incentives:
            b_allocation_dict[item.slug] = item
        return b_allocation_dict

    @cached_property
    def _bonus_verifier_allocation_dict(self) -> dict:
        v_allocation_dict = dict()
        for item in self.verifier_additional_incentives:
            v_allocation_dict[item.slug] = item
        return v_allocation_dict

    @cached_property
    def pt_builder_net_zero_allocation(self) -> ProjectTrackerAllocation:
        value = self._bonus_builder_allocation_dict.get(
            "net_zero", IncentiveItem(reported=False, eligible=False, label="Net Zero")
        )
        return ProjectTrackerAllocation(
            value.slug, value.label, 0.0, 0.0, value.incentive if value.eligible else 0.0
        )

    @cached_property
    def pt_builder_solar_ready_allocation(self) -> ProjectTrackerAllocation:
        value = self._bonus_builder_allocation_dict.get(
            "solar_ready", IncentiveItem(reported=False, eligible=False, label="Solar Ready")
        )
        return ProjectTrackerAllocation(
            value.slug, value.label, 0.0, 0.0, value.incentive if value.eligible else 0.0
        )

    @cached_property
    def pt_verifier_solar_ready_allocation(self) -> ProjectTrackerAllocation:
        value = self._bonus_verifier_allocation_dict.get(
            "solar_ready", IncentiveItem(reported=False, eligible=False, label="Solar Ready")
        )

        return ProjectTrackerAllocation(
            value.slug, value.label, 0.0, 0.0, value.incentive if value.eligible else 0.0
        )

    @cached_property
    def pt_builder_esh_ev_ready_allocation(self) -> ProjectTrackerAllocation:
        value = self._bonus_builder_allocation_dict.get(
            "esh_ev_ready", IncentiveItem(reported=False, eligible=False, label="ESH: EV Ready")
        )

        return ProjectTrackerAllocation(
            value.slug, value.label, value.incentive if value.eligible else 0.0, 0.0, 0.0
        )

    @cached_property
    def pt_builder_esh_solar_storage_allocation(self) -> ProjectTrackerAllocation:
        value = self._bonus_builder_allocation_dict.get(
            "esh_solar_storage",
            IncentiveItem(reported=False, eligible=False, label="ESH: Solar + Storage"),
        )

        return ProjectTrackerAllocation(
            value.slug, value.label, 0.0, 0.0, value.incentive if value.eligible else 0.0
        )

    @cached_property
    def pt_builder_dei_allocation(self) -> ProjectTrackerAllocation:
        value = self._bonus_builder_allocation_dict.get(
            "builder_dei", IncentiveItem(reported=False, eligible=False, label="Builder DEI")
        )

        return ProjectTrackerAllocation(
            value.slug,
            value.label,
            value.incentive if self.heat_type == HeatType.ELECTRIC and value.eligible else 0.0,
            value.incentive if self.heat_type != HeatType.ELECTRIC and value.eligible else 0.0,
            0.0,
        )

    @cached_property
    def pt_verifier_dei_allocation(self) -> ProjectTrackerAllocation:
        value = self._bonus_verifier_allocation_dict.get(
            "verifier_dei", IncentiveItem(reported=False, eligible=False, label="Verifier DEI")
        )

        return ProjectTrackerAllocation(
            value.slug,
            value.label,
            value.incentive if self.heat_type == HeatType.ELECTRIC and value.eligible else 0.0,
            value.incentive if self.heat_type != HeatType.ELECTRIC and value.eligible else 0.0,
            0.0,
        )

    @cached_property
    def pt_builder_heat_pump_water_heater_allocation(self) -> ProjectTrackerAllocation:
        value = self._bonus_builder_allocation_dict.get(
            "heat_pump_water_heater",
            IncentiveItem(reported=False, eligible=False, label="Heat Pump Water Heater"),
        )

        return ProjectTrackerAllocation(
            value.slug,
            value.label,
            value.incentive * self.electric.allocation if value.eligible else 0.0,
            value.incentive * self.gas.allocation if value.eligible else 0.0,
            0.0,
        )

    @cached_property
    def pt_builder_fire_rebuild_triple_pane_windows_allocation(self) -> ProjectTrackerAllocation:
        value = self._bonus_builder_allocation_dict.get(
            "triple_pane_windows",
            IncentiveItem(reported=False, eligible=False, label=" - Triple Pane Windows"),
        )

        return ProjectTrackerAllocation(
            value.slug,
            value.label,
            value.incentive if self.heat_type == HeatType.ELECTRIC and value.eligible else 0.0,
            value.incentive if self.heat_type != HeatType.ELECTRIC and value.eligible else 0.0,
            0.0,
        )

    @cached_property
    def pt_builder_fire_rebuild_exterior_rigid_insulation_allocation(
        self,
    ) -> ProjectTrackerAllocation:
        value = self._bonus_builder_allocation_dict.get(
            "exterior_rigid_insulation",
            IncentiveItem(reported=False, eligible=False, label=" - Exterior Rigid Insulation"),
        )

        return ProjectTrackerAllocation(
            value.slug,
            value.label,
            value.incentive if self.heat_type == HeatType.ELECTRIC and value.eligible else 0.0,
            value.incentive if self.heat_type != HeatType.ELECTRIC and value.eligible else 0.0,
            0.0,
        )

    @cached_property
    def pt_builder_fire_rebuild_sealed_attic_allocation(self) -> ProjectTrackerAllocation:
        #     reported: bool = True
        #     eligible: bool = True
        #     incentive: float = 0.0
        #     budget: str = None
        #     utility_allocation: str = None
        #     label: str = None

        value = self._bonus_builder_allocation_dict.get(
            "sealed_attic", IncentiveItem(reported=False, eligible=False, label=" - Sealed Attic")
        )
        return ProjectTrackerAllocation(
            value.slug,
            value.label,
            value.incentive if self.heat_type == HeatType.ELECTRIC and value.eligible else 0.0,
            value.incentive if self.heat_type != HeatType.ELECTRIC and value.eligible else 0.0,
            0.0,
        )

    @cached_property
    def builder_allocations(self):
        return [
            self.pt_builder_net_zero_allocation,
            self.pt_builder_solar_ready_allocation,
            self.pt_builder_esh_ev_ready_allocation,
            self.pt_builder_esh_solar_storage_allocation,
            self.pt_builder_dei_allocation,
            self.pt_builder_heat_pump_water_heater_allocation,
            self.pt_builder_fire_rebuild_triple_pane_windows_allocation,
            self.pt_builder_fire_rebuild_exterior_rigid_insulation_allocation,
            self.pt_builder_fire_rebuild_sealed_attic_allocation,
        ]

    @cached_property
    def verifier_allocations(self):
        return [
            self.pt_verifier_dei_allocation,
            self.pt_verifier_solar_ready_allocation,
        ]

    @cached_property
    def builder_total_incentive(self) -> ProjectTrackerTotal:
        electric = self.electric.builder_incentive
        gas = self.gas.builder_incentive
        solar = 0.0
        for item in self.builder_allocations:
            electric += item.electric
            gas += item.gas
            solar += item.sle
        return ProjectTrackerTotal(
            electric_utility=self.electric_utility.value,
            gas_utility=self.gas_utility.value,
            electric_incentive=round(electric, 0),
            gas_incentive=round(gas, 0),
            solar_incentive=round(solar, 0),
        )

    @cached_property
    def verifier_total_incentive(self) -> ProjectTrackerTotal:
        electric = self.electric.verifier_incentive
        gas = self.gas.verifier_incentive
        solar = 0.0
        for item in self.verifier_allocations:
            electric += item.electric
            gas += item.gas
            solar += item.sle
        return ProjectTrackerTotal(
            electric_utility=self.electric_utility.value,
            gas_utility=self.gas_utility.value,
            electric_incentive=round(electric, 0),
            gas_incentive=round(gas, 0),
            solar_incentive=round(solar, 0),
        )

    @cached_property
    def allocation_summary(self):
        return tabulate(
            [
                [
                    self.builder_total_incentive.electric_utility,
                    self.builder_total_incentive.electric_incentive_str,
                    self.verifier_total_incentive.electric_incentive_str,
                ],
                [
                    self.builder_total_incentive.gas_utility,
                    self.builder_total_incentive.gas_incentive_str,
                    self.verifier_total_incentive.gas_incentive_str,
                ],
                [
                    "Solar",
                    self.builder_total_incentive.solar_incentive_str,
                    self.verifier_total_incentive.solar_incentive_str,
                ],
                [
                    "Total",
                    self.builder_total_incentive.total_str,
                    self.verifier_total_incentive.total_str,
                ],
            ],
            headers=["Source", "Builder", "Verifier"],
        )

    @cached_property
    def allocation_report(self) -> str:
        report = "Allocation Report \n"
        report += tabulate(
            [
                ["Home Path", self.home_path.value],
                ["Sub Type", self.sub_type.value],
                ["Partial Territory", "Yes" if self.partial_territory else "No"],
            ]
        )
        report += "\n\n"
        report += tabulate(
            [
                [
                    f"{self.home_path.value} {self.sub_type.value}",
                    self.load_profile.electric_load_profile.value,
                    self.load_profile.gas_load_profile.value,
                    self.load_profile.weighted_avg_measure_life,
                    self.load_profile.electric_allocation,
                    self.load_profile.gas_allocation,
                ]
            ],
            headers=[
                "Subtype & Allocation",
                "Electric LP",
                "Gas LP",
                "Measure Life",
                "Electric Allocation",
                "Gas Allocation",
            ],
        )

        report += "\n\nStandard Utility Allocations for PT\n"
        report += tabulate(
            [
                [
                    "Electric",
                    self.electric_utility.value,
                    self.load_profile.electric_load_profile.value,
                    self.load_profile.electric_allocation,
                    self.load_profile.weighted_avg_measure_life,
                ],
                [
                    "Gas",
                    self.gas_utility.value,
                    self.load_profile.gas_load_profile.value,
                    self.load_profile.gas_allocation,
                    self.load_profile.weighted_avg_measure_life,
                ],
            ],
            headers=["Fuel", "Utility", "Load Profile", "Allocation", "WAML"],
        )
        report += "\n\n\n"

        performance_incentives = [
            [
                "Builder Performance Incentives",
                f"$ {self.electric.builder_incentive:.2f}",
                f"$ {self.gas.builder_incentive:.2f}",
                None,
                f"$ {self.electric.builder_incentive + self.gas.builder_incentive:.2f}",
            ],
            [
                "Verifier Performance Incentives",
                f"$ {self.electric.verifier_incentive:.2f}",
                f"$ {self.gas.verifier_incentive:.2f}",
                None,
                f"$ {self.electric.verifier_incentive + self.gas.verifier_incentive:.2f}",
            ],
            [],
            ["Builder Bonus"],
        ]
        for item in self.builder_allocations:
            performance_incentives.append(
                [item.label, item.electric_str, item.gas_str, item.sle_str, item.total_str]
            )

        performance_incentives.append([])
        performance_incentives.append(["Verifier Bonus"])

        for item in self.verifier_allocations:
            performance_incentives.append(
                [item.label, item.electric_str, item.gas_str, item.sle_str, item.total_str]
            )

        report += tabulate(performance_incentives, headers=["", "Electric", "Gas", "SLE", "Total"])
        report += "\n\n"

        report += self.allocation_summary
        return report
