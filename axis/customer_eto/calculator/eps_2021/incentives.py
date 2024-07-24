"""incentives.py - Axis"""

__author__ = "Steven K"
__date__ = "9/14/21 11:58"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
from tabulate import tabulate

from functools import cached_property

from axis.customer_eto.calculator.eps_2021.base import (
    HomePath,
    HomeSubType,
    LoadProfile,
    round_value,
    FuelAllocationIncentive,
    AllocationIncentive,
)
from axis.customer_eto.calculator.eps_2021.constants import Constants
from axis.customer_eto.calculator.eps_2021.net_zero import NetZero2020
from axis.customer_eto.enumerations import GasUtility, ElectricUtility

log = logging.getLogger(__name__)


class Incentives2020:
    def __init__(
        self,
        percent_improvement: float,
        electric_utility: ElectricUtility,
        gas_utility: GasUtility,
        heating_therms: float,
        hot_water_therms: float,
        hot_water_kwh: float,
        constants: Constants,
        net_zero: NetZero2020 = None,
        has_heat_pump_water_heater: bool = False,
    ):
        self.percent_improvement = percent_improvement
        self.heating_therms = heating_therms
        self.hot_water_therms = hot_water_therms
        self.hot_water_kwh = hot_water_kwh
        self.electric_utility = electric_utility
        self.gas_utility = gas_utility
        self.constants = constants
        self.net_zero = net_zero
        self.has_heat_pump_water_heater = has_heat_pump_water_heater

        if self.net_zero is not None:
            # We need to set these so we can recalculate incentives
            self.net_zero.home_path = self.home_path
            self.net_zero.whole_home_incentive = self.builder_whole_home_incentive

    @property
    def labels(self):
        return {
            "percent_improvement": "Percent Improvement",
            "full_territory_incentive": "2021 Full Territory Incentive",
        }

    @cached_property
    def full_territory_builder_incentive(self) -> float:
        """
        =MIN(5223,IF($D$6>=0.1,(36354*($D$6^2))-(4510.2*$D$6)+1210.5))

        :return:
        """

        if self.percent_improvement < 0.10:
            return 0.0

        value = 36354.0 * self.percent_improvement * self.percent_improvement
        value += -4510.2 * self.percent_improvement + 1210.5
        return min([5223.0, value])

    @cached_property
    def home_path(self) -> HomePath:
        """
        =IF(
            AND(D6>=E10,D6<E11),D10,
            IF(AND(D6>=E11,D6<E12),D11,
            IF(AND(D6>=E12,D6<E13),D12,IF(AND(ISNUMBER(D6),D6>=E13),D13,"-"))))


        :return:
        """

        if 0.2 > self.percent_improvement >= 0.10:
            return HomePath.PATH_1
        elif 0.3 > self.percent_improvement >= 0.20:
            return HomePath.PATH_2
        elif 0.4 > self.percent_improvement >= 0.30:
            return HomePath.PATH_3
        elif self.percent_improvement >= 0.40:
            return HomePath.PATH_4

    @cached_property
    def sub_type(self) -> HomeSubType:
        """
        =IF(
            AND('Input-2020'!C21>1,'Input-2020'!F21>1),"GH+GW",
            IF(
                AND('Input-2020'!C21<1,'Input-2020'!G21>1),"EH+EW",
                IF(
                    AND('Input-2020'!C21>1,'Input-2020'!G21>1),"GH+EW",
                    IF(
                        AND('Input-2020'!C21<1,'Input-2020'!F21>1),"EH+GW",
                        "other"))))

        :return:
        """
        if self.heating_therms > 1.0 and self.hot_water_therms > 1:
            return HomeSubType.GHGW
        if self.heating_therms < 1.0 and self.hot_water_kwh > 1:
            return HomeSubType.EHEW
        if self.heating_therms > 1.0 and self.hot_water_kwh > 1:
            return HomeSubType.GHEW
        if self.heating_therms < 1.0 and self.hot_water_therms > 1:
            return HomeSubType.EHGW
        return HomeSubType.OTHER

    @cached_property
    def load_profile(self) -> LoadProfile:
        profile = self.constants.get_load_profile(self.home_path, self.sub_type)._asdict()
        if self.gas_utility == GasUtility.NONE or self.electric_utility == ElectricUtility.NONE:
            profile.update(self.constants.get_partial_territory_load_profile(self.sub_type))
        return LoadProfile(**profile)

    @cached_property
    def builder_electric_incentive(self):
        load_profile = self.load_profile
        if self.electric_utility != ElectricUtility.NONE:
            value = load_profile.electric_allocation * self.full_territory_builder_incentive
            if self.has_heat_pump_water_heater:
                value -= 250.00
            return value
        return 0.0

    @cached_property
    def builder_gas_incentive(self):
        load_profile = self.load_profile
        if self.gas_utility != GasUtility.NONE:
            return load_profile.gas_allocation * self.full_territory_builder_incentive
        return 0.0

    @cached_property
    def builder_whole_home_incentive(self):
        return self.builder_electric_incentive + self.builder_gas_incentive

    @cached_property
    def total_builder_incentive(self):
        """This is the total with net zero.."""
        if self.net_zero is not None:
            return self.net_zero.total_incentive
        return self.builder_whole_home_incentive

    @cached_property
    def builder_incentive(self):
        return round(self.total_builder_incentive, 0)

    @cached_property
    def builder_allocation_data(self) -> AllocationIncentive:
        load_profile = self.load_profile
        electric = FuelAllocationIncentive(
            load_profile.electric_allocation,
            self.builder_electric_incentive,
            "Electric",
            self.electric_utility,
            load_profile.electric_load_profile,
            load_profile.weighted_avg_measure_life,
        )
        gas = FuelAllocationIncentive(
            load_profile.gas_allocation,
            self.builder_gas_incentive,
            "Gas",
            self.gas_utility,
            load_profile.gas_load_profile,
            load_profile.weighted_avg_measure_life,
        )
        return AllocationIncentive(
            electric,
            gas,
            load_profile.electric_allocation + load_profile.gas_allocation,
            self.builder_whole_home_incentive,
            load_profile.weighted_avg_measure_life,
        )

    @cached_property
    def initial_verifier_incentive(self) -> float:
        if self.percent_improvement < 0.10:
            return 0.0
        value = self.full_territory_builder_incentive - 500.0
        value *= min([0.4, self.percent_improvement])
        return max([300.00, value])

    @cached_property
    def verifier_electric_allocation(self):
        load_profile = self.load_profile
        electric_allocation = 0.0
        if self.electric_utility != ElectricUtility.NONE and self.gas_utility != GasUtility.NONE:
            electric_allocation = load_profile.electric_allocation
        elif self.electric_utility != ElectricUtility.NONE and self.gas_utility == GasUtility.NONE:
            electric_allocation = 1.0
        return electric_allocation

    @cached_property
    def verifier_electric_incentive(self):
        return self.verifier_electric_allocation * self.initial_verifier_incentive

    @cached_property
    def verifier_gas_allocation(self):
        load_profile = self.load_profile
        gas_allocation = 0.0
        if self.electric_utility != ElectricUtility.NONE and self.gas_utility != GasUtility.NONE:
            gas_allocation = load_profile.gas_allocation
        elif self.gas_utility != GasUtility.NONE and self.electric_utility == ElectricUtility.NONE:
            gas_allocation = 1.0
        return gas_allocation

    @cached_property
    def verifier_gas_incentive(self):
        if self.gas_utility != GasUtility.NONE:
            return self.verifier_gas_allocation * self.initial_verifier_incentive
        return 0.0

    @cached_property
    def verifier_whole_home_incentive(self):
        return self.verifier_gas_incentive + self.verifier_electric_incentive

    @cached_property
    def verifier_incentive(self):
        return round(max([0, self.verifier_whole_home_incentive]), 0)

    @cached_property
    def verifier_allocation_data(self) -> AllocationIncentive:
        load_profile = self.load_profile

        """
        =IF(AND('Input-2020'!C12 <> 'Input-2020'!X7, 'Input-2020'!C13 <> 'Input-2020'!Y8), D51,
        IF( 'Input-2020'!C12 = 'Input-2020'!X7, 0,
        IF( AND('Input-2020'!C12 <> 'Input-2020'!X7, 'Input-2020'!C13 = 'Input-2020'!Y8), 1,)))
        if gas != None and electric != None:
            allocation =   load_profile.electric_allocation

        """
        electric = FuelAllocationIncentive(
            self.verifier_electric_allocation,
            self.verifier_electric_incentive,
            "Electric",
            self.electric_utility,
            load_profile.electric_load_profile,
            load_profile.weighted_avg_measure_life,
        )

        gas = FuelAllocationIncentive(
            self.verifier_gas_allocation,
            self.verifier_gas_incentive,
            "Gas",
            self.gas_utility,
            load_profile.gas_load_profile,
            load_profile.weighted_avg_measure_life,
        )
        return AllocationIncentive(
            electric,
            gas,
            load_profile.electric_allocation + load_profile.gas_allocation,
            self.verifier_whole_home_incentive,
            load_profile.weighted_avg_measure_life,
        )

    @cached_property
    def incentive_report(self) -> str:
        data = ""
        data += tabulate(
            [
                [
                    self.home_path.value if self.home_path else "ERROR",
                    self.sub_type.value,
                ],
            ],
            headers=["Home Path", "Home SubType"],
        )
        data += "\n\nBuilder Incentive and Allocations\n"
        data += tabulate(
            [
                [
                    f"{self.percent_improvement:.2%}",
                    f"$ {self.full_territory_builder_incentive:,.2f}",
                ],
            ],
            headers=[self.labels["percent_improvement"], self.labels["full_territory_incentive"]],
        )
        data += "\n\n"
        data += tabulate(
            [
                [
                    None,
                    f"{self.builder_allocation_data.electric.allocation:.2%}",
                    f"$ {self.builder_allocation_data.electric.incentive:,.2f}",
                    self.builder_allocation_data.electric.fuel,
                    self.builder_allocation_data.electric.utility.value,
                    self.builder_allocation_data.electric.load_profile.value,
                    None,
                ],
                [
                    None,
                    f"{self.builder_allocation_data.gas.allocation:.2%}",
                    f"$ {self.builder_allocation_data.gas.incentive:,.2f}",
                    self.builder_allocation_data.gas.fuel,
                    self.builder_allocation_data.gas.utility.value,
                    self.builder_allocation_data.gas.load_profile.value,
                    None,
                ],
                [
                    "Builder",
                    f"{self.builder_allocation_data.allocation:.2%}",
                    f"$ {self.builder_allocation_data.incentive:,.2f}",
                    None,
                    None,
                    None,
                    self.builder_allocation_data.waml,
                ],
            ],
            headers=(
                "",
                "Allocation",
                "Incentive",
                "Fuel",
                "Utility",
                "Load Profile",
                "WAML - Whole Home",
            ),
            floatfmt=f".{round_value}f",
        )
        if self.has_heat_pump_water_heater:
            data += (
                f"\n\n** Note: HPWH Deduction applied onto Builder Electric Incentive ("
                f"${self.builder_allocation_data.electric.incentive + 250.0:,.2f}) **\n"
            )

        data += "\n\nVerifier Incentive and Allocations\n"
        data += tabulate(
            [
                [
                    f"{self.percent_improvement:.2%}",
                    f"$ {self.initial_verifier_incentive:,.2f}",
                ],
            ],
            headers=[self.labels["percent_improvement"], "Initial Verifier Incentive"],
        )
        data += "\n\n"
        data += tabulate(
            [
                [
                    None,
                    f"{self.verifier_allocation_data.electric.allocation:.2%}",
                    f"$ {self.verifier_allocation_data.electric.incentive:,.2f}",
                    self.verifier_allocation_data.electric.fuel,
                    self.verifier_allocation_data.electric.utility.value,
                    self.verifier_allocation_data.electric.load_profile.value,
                    None,
                ],
                [
                    None,
                    f"{self.verifier_allocation_data.gas.allocation:.2%}",
                    f"$ {self.verifier_allocation_data.gas.incentive:,.2f}",
                    self.verifier_allocation_data.gas.fuel,
                    self.verifier_allocation_data.gas.utility.value,
                    self.verifier_allocation_data.gas.load_profile.value,
                    None,
                ],
                [
                    "Verifier",
                    f"{self.verifier_allocation_data.allocation:.2%}",
                    f"$ {self.verifier_allocation_data.incentive:,.2f}",
                    None,
                    None,
                    None,
                    self.verifier_allocation_data.waml,
                ],
            ],
            headers=(
                "",
                "Allocation",
                "Incentive",
                "Fuel",
                "Utility",
                "Load Profile",
                "WAML - Whole Home",
            ),
            floatfmt=f".{round_value}f",
        )

        return data


class Incentives2021WA(Incentives2020):
    @property
    def labels(self):
        return {
            "percent_improvement": "Gas Percent Improvement",
            "full_territory_incentive": "2021 Builder Incentive",
        }

    @cached_property
    def full_territory_builder_incentive(self) -> float:
        """
        =@IFS(
            AND(
                'Input-2021'!C13="NW Natural",    # Gas Utility
                'Input-2021'!E21>0,               # Code DHW Therms
                'Incentives-2021'!D10>0.05),      # Therm Heating PCT Improvement
                MIN(2150,9000*'Incentives-2021'!D10+350),
            AND(
                'Input-2021'!C13="NW Natural",
                'Input-2021'!F21>0,
                'Incentives-2021'!D10>0.05),
                MIN(1920,8800*'Incentives-2021'!D10+160)
        :return:
        """
        if self.percent_improvement <= 0.05 or self.gas_utility != GasUtility.NW_NATURAL:
            return 0.0

        if self.hot_water_therms > 0.0:
            return min([2150.0, 9000.0 * self.percent_improvement + 350])
        elif self.hot_water_kwh > 0.0:
            return min([1920.0, 8800.0 * self.percent_improvement + 160])
        return 0.0

    @cached_property
    def home_path(self) -> HomePath:
        if 0.1 > self.percent_improvement >= 0.05:
            return HomePath.PATH_1
        elif 0.15 > self.percent_improvement >= 0.10:
            return HomePath.PATH_2
        elif 0.2 > self.percent_improvement >= 0.15:
            return HomePath.PATH_3
        elif self.percent_improvement >= 0.20:
            return HomePath.PATH_4

    @cached_property
    def load_profile(self) -> LoadProfile:
        return self.constants.get_load_profile(self.home_path, self.sub_type)

    @cached_property
    def initial_verifier_incentive(self) -> float:
        if self.percent_improvement < 0.05 or self.gas_utility != GasUtility.NW_NATURAL:
            return 0.0
        return 100.00

    @cached_property
    def verifier_allocation_data(self) -> AllocationIncentive:
        load_profile = self.load_profile
        electric_allocation = 0.0
        electric_incentive = electric_allocation * self.initial_verifier_incentive
        electric = FuelAllocationIncentive(
            electric_allocation,
            electric_incentive,
            "Electric",
            self.electric_utility,
            load_profile.electric_load_profile,
            load_profile.weighted_avg_measure_life,
        )

        gas_allocation = 1.0
        gas_incentive = gas_allocation * self.initial_verifier_incentive
        gas = FuelAllocationIncentive(
            gas_allocation,
            gas_incentive,
            "Gas",
            self.gas_utility,
            load_profile.gas_load_profile,
            load_profile.weighted_avg_measure_life,
        )
        return AllocationIncentive(
            electric,
            gas,
            electric_allocation + gas_allocation,
            electric_incentive + gas_incentive,
            load_profile.weighted_avg_measure_life,
        )
