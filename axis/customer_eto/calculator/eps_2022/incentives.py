"""incentives.py - Axis"""

__author__ = "Steven K"
__date__ = "3/3/22 10:59"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
import reprlib
from collections import defaultdict
from dataclasses import dataclass
from functools import cached_property

from tabulate import tabulate

from axis.customer_eto.enumerations import ElectricUtility, GasUtility, HeatType

log = logging.getLogger(__name__)


@dataclass
class IncentiveItem:
    reported: bool = True
    eligible: bool = True
    incentive: float = 0.0
    budget: str = None
    utility_allocation: str = None
    label: str = None

    @property
    def reported_str(self) -> str:
        return "Yes" if self.reported else "No"

    @property
    def eligible_str(self) -> str:
        return "Yes" if self.eligible else "No"

    @property
    def incentive_str(self) -> str:
        return f"$ {self.incentive:.2f}"

    @property
    def slug(self):
        slug = self.label.replace(" - ", "").replace(" + ", " ").replace(":", "").replace(" ", "_")
        return slug.lower()


@dataclass
class Incentives:
    percent_improvement: float
    heat_type: HeatType
    therm_percent_improvement: float = 0.0
    solar_production: float = 0.0
    improved_total_kwh: float = 0.0
    improved_total_therms: float = 0.0
    fire_rebuild: bool = False
    net_zero: bool = False
    solar_ready: bool = False
    storage_ready: bool = False
    ev_ready: bool = False
    corbid_builder: bool = False
    corbid_verifier: bool = False
    has_heat_pump_water_heater: bool = False
    triple_pane_windows: bool = False
    exterior_rigid_insulation: bool = False
    sealed_attic: bool = False
    electric_utility: ElectricUtility = ElectricUtility.NONE
    gas_utility: GasUtility = GasUtility.NONE

    @cached_property
    def partial_territory(self) -> bool:
        """
        =IF(C10="Other/None","Partial","Full")
        """
        return self.electric_utility == ElectricUtility.NONE

    @cached_property
    def baseline_builder_incentive(self) -> float:
        """
        =IF(
            AND(
                C12="Partial",
                Inputs!C15="Electric Heat"),
            "0",
            IF(
                C14="Yes",
                2*MIN(4085,IF(C18>=0.1,36354*C18^2-4510.2*C18+1210.5,0)),
                MIN(4085,IF(C18>=0.1,36354*C18^2-4510.2*C18+1210.5,0)))
            )
        """
        if self.percent_improvement < 0.10:
            return 0.0
        if self.partial_territory and self.heat_type == HeatType.ELECTRIC:
            return 0.0
        value = 36354.0 * self.percent_improvement * self.percent_improvement
        value += -4510.2 * self.percent_improvement + 1210.5
        value = min([4085.0, value])
        return value * 2 if self.fire_rebuild else value

    @cached_property
    def baseline_verifier_incentive(self) -> float:
        """
        =IF(C14="No",
            IFS(AND(C18>=0.1,C18<0.2),300,C18>=0.2,0.2*C19),
            IFS(AND(C18>=0.1,C18<0.2),300,C18>=0.2,0.2*C19/2)
        )
        """
        if self.percent_improvement < 0.10:
            return 0.0
        elif 0.2 > self.percent_improvement >= 0.10:
            return 300.00
        if self.fire_rebuild:
            return 0.2 * (self.baseline_builder_incentive / 2.0)
        return 0.2 * self.baseline_builder_incentive

    @cached_property
    def net_zero_builder_incentive(self) -> IncentiveItem:
        """
        =IFERROR(
            IF(
                AND(
                    OR(C10="Portland General",C10="Pacific Power"),
                    C26="Yes",
                    'Modeled Savings'!F17>=0.2,
                    OR('Modeled Savings'!D15=0,'Modeled Savings'!F15>=0.1),
                    'Incentives & Allocations'!C14>=(0.95*'Modeled Savings'!D16)
                ),"Yes","No"),
        "No")

        References:
            C10 - electric_utility
            C26 - net_zero
            F17 - percent_improvement
            D15 - improved_total_therms
            F15 - therm_percent_improvement
            C14 - solar_production
            D16 - improved_total_kwh

        Project Tracker this maps to:  EPSNZ
        """
        eligible = all(
            [
                self.electric_utility != ElectricUtility.NONE,
                self.net_zero,
                self.percent_improvement >= 0.2,
                any([self.improved_total_therms == 0.0, self.therm_percent_improvement >= 0.1]),
                self.solar_production >= 0.95 * self.improved_total_kwh,
                self.baseline_builder_incentive > 0,
            ]
        )
        return IncentiveItem(
            self.net_zero, eligible, 1000.00 if eligible else 0.0, "SLE", "SLE", "Net Zero"
        )

    @cached_property
    def solar_ready_builder_incentive(self) -> IncentiveItem:
        """=IF(
        AND(
            OR(C10="Portland General",C10="Pacific Power"),
            C26="Yes"),
            "Yes",
            "No")

        Project Tracker - SOLRDYCON
        """
        eligible = all(
            [
                self.electric_utility != ElectricUtility.NONE,
                self.solar_ready,
                self.baseline_builder_incentive > 0,
            ]
        )
        return IncentiveItem(
            self.solar_ready, eligible, 200.00 if eligible else 0.0, "SLE", "SLE", "Solar Ready"
        )

    @cached_property
    def solar_ready_verifier_incentive(self) -> IncentiveItem:
        """=IF(AND(OR(C10="Portland General",C10="Pacific Power"),C40="Yes"),"Yes","No")
        Project Tracker N/A
        """
        eligible = all(
            [
                self.electric_utility != ElectricUtility.NONE,
                self.solar_ready,
                self.baseline_builder_incentive > 0,
            ]
        )
        return IncentiveItem(
            self.solar_ready, eligible, 50.00 if eligible else 0.0, "SLE", "SLE", "Solar Ready"
        )

    @cached_property
    def ev_ready_builder_incentive(self) -> IncentiveItem:
        """=IF(
            AND(
                OR(C10="Portland General",C10="Pacific Power"),
                C28="Yes"),
                "Yes","No")


        Project Tracker EPSESH Reused"""
        eligible = all(
            [
                self.ev_ready,
                self.electric_utility != ElectricUtility.NONE,
                self.baseline_builder_incentive > 0,
            ]
        )
        return IncentiveItem(
            self.ev_ready,
            eligible,
            200.00 if eligible else 0.0,
            "ENH",
            "Ele",
            "ESH: EV Ready",
        )

    @cached_property
    def solar_storage_builder_incentive(self) -> IncentiveItem:
        """=IF(
        AND(
            OR(C10="Portland General",C10="Pacific Power"),
            C28="Yes"),
            "Yes","No")

        Project Tracker EPSESH Reused"""
        eligible = all(
            [
                self.electric_utility != ElectricUtility.NONE,
                self.storage_ready,
                self.baseline_builder_incentive > 0,
            ]
        )

        return IncentiveItem(
            self.storage_ready,
            eligible,
            200.00 if eligible else 0.0,
            "SLE",
            "SLE",
            "ESH: Solar + Storage",
        )

    @cached_property
    def cobid_builder_incentive(self) -> IncentiveItem:
        """=IF(C29="Yes","Yes","")

        Project Tracker DEIBONUSBUILDER"""

        eligible = all(
            [
                self.corbid_builder,
                self.baseline_builder_incentive > 0,
            ]
        )

        return IncentiveItem(
            self.corbid_builder,
            eligible,
            500.00 if eligible else 0.0,
            "ENH",
            "Ele" if self.heat_type == HeatType.ELECTRIC else "Gas",
            "Builder DEI",
        )

    @cached_property
    def cobid_verifier_incentive(self) -> IncentiveItem:
        """=IF(C29="Yes","Yes","")

        Project Tracker DEIBONUSVERIFIER"""

        eligible = all(
            [
                self.corbid_verifier,
                self.baseline_builder_incentive > 0,
            ]
        )

        return IncentiveItem(
            self.corbid_verifier,
            eligible,
            250.00 if eligible else 0.0,
            "ENH",
            "Ele" if self.heat_type == HeatType.ELECTRIC else "Gas",
            "Verifier DEI",
        )

    @cached_property
    def heat_pump_water_heater_incentive(self) -> IncentiveItem:
        eligible = all(
            [
                not self.partial_territory,
                self.has_heat_pump_water_heater,
                self.baseline_builder_incentive > 0,
            ]
        )
        return IncentiveItem(
            self.has_heat_pump_water_heater,
            eligible,
            -250.00 if eligible else 0.0,
            "ENH",
            "Allocation",
            "Heat Pump Water Heater",
        )

    @cached_property
    def fire_rebuild_incentive(self) -> IncentiveItem:
        eligible = all([self.fire_rebuild, self.baseline_builder_incentive > 0])
        return IncentiveItem(
            self.fire_rebuild,
            eligible,
            0.0,
            None,
            None,
            "Fire Rebuild",
        )

    @cached_property
    def fire_rebuild_triple_pane_incentive(self) -> IncentiveItem:
        """Project Tracker EPSFRFRTW"""
        eligible = all(
            [self.fire_rebuild, self.triple_pane_windows, self.baseline_builder_incentive > 0]
        )
        return IncentiveItem(
            self.triple_pane_windows,
            eligible,
            750.00 if eligible else 0.0,
            "ENH",
            "Ele" if self.heat_type == HeatType.ELECTRIC else "Gas",
            " - Triple Pane Windows",
        )

    @cached_property
    def fire_rebuild_insulation_incentive(self) -> IncentiveItem:
        """Project Tracker EPSFRFREI"""
        eligible = all(
            [self.fire_rebuild, self.exterior_rigid_insulation, self.baseline_builder_incentive > 0]
        )
        return IncentiveItem(
            self.exterior_rigid_insulation,
            eligible,
            750.00 if eligible else 0.0,
            "ENH",
            "Ele" if self.heat_type == HeatType.ELECTRIC else "Gas",
            " - Exterior Rigid Insulation",
        )

    @cached_property
    def fire_rebuild_sealed_attic_incentive(self) -> IncentiveItem:
        """Project Tracker EPSFRFRSA"""
        eligible = all([self.fire_rebuild, self.sealed_attic, self.baseline_builder_incentive > 0])
        return IncentiveItem(
            self.sealed_attic,
            eligible,
            400.00 if eligible else 0.0,
            "ENH",
            "Ele" if self.heat_type == HeatType.ELECTRIC else "Gas",
            " - Sealed Attic",
        )

    @cached_property
    def builder_additional_incentives(self) -> list[IncentiveItem]:
        return [
            self.net_zero_builder_incentive,
            self.solar_ready_builder_incentive,
            self.ev_ready_builder_incentive,
            self.solar_storage_builder_incentive,
            self.cobid_builder_incentive,
            self.heat_pump_water_heater_incentive,
            self.fire_rebuild_incentive,
            self.fire_rebuild_triple_pane_incentive,
            self.fire_rebuild_insulation_incentive,
            self.fire_rebuild_sealed_attic_incentive,
        ]

    @cached_property
    def total_builder_additional_incentives(self) -> dict:
        results = defaultdict(int)
        total = 0
        for item in self.builder_additional_incentives:
            if item.budget is None:
                continue
            results[item.budget] += item.incentive
            total += item.incentive
        results["total"] = max([0, total])
        return results

    @cached_property
    def verifier_additional_incentives(self) -> list[IncentiveItem]:
        return [self.cobid_verifier_incentive, self.solar_ready_verifier_incentive]

    @cached_property
    def total_verifier_additional_incentives(self) -> dict:
        results = defaultdict(int)
        total = 0
        for item in self.verifier_additional_incentives:
            if item.budget is None:
                continue
            results[item.budget] += item.incentive
            total += item.incentive
        results["total"] = max([0, total])
        return results

    @cached_property
    def total_builder_incentive(self) -> float:
        return self.baseline_builder_incentive + self.total_builder_additional_incentives["total"]

    @cached_property
    def builder_incentive(self) -> float:
        return round(self.total_builder_incentive, 0)

    @cached_property
    def total_verifier_incentive(self) -> float:
        return self.baseline_verifier_incentive + self.total_verifier_additional_incentives["total"]

    @cached_property
    def verifier_incentive(self) -> float:
        return round(self.total_verifier_incentive, 0)

    @cached_property
    def incentive_report(self) -> str:
        result = "Builder & Verifier Performance Incentive (before additional incentives)\n\n"
        result += tabulate(
            [
                ["Incentive Improvement", f"{self.percent_improvement:.1%}"],
                ["Builder Performance Incentive", f"$ {self.baseline_builder_incentive:,.2f}"],
                ["Verifier Performance Incentive", f"$ {self.baseline_verifier_incentive:,.2f}"],
            ],
        )
        result += "\n\nAdditional Incentives\n\n"

        additional = []
        for item in self.builder_additional_incentives:
            additional.append(
                [
                    item.label,
                    item.reported_str,
                    item.eligible_str,
                    item.incentive_str,
                    item.budget,
                    item.utility_allocation,
                ]
            )
        for budget, total in self.total_builder_additional_incentives.items():
            label = f"{budget} Total" if len(budget) == 3 else f"Grand {budget}"
            bucket = budget if len(budget) == 3 else None
            additional.append([None, None, label, f"$ {total:,.2f}", bucket])
        additional.append([])
        for item in self.verifier_additional_incentives:
            additional.append(
                [
                    item.label,
                    item.reported_str,
                    item.eligible_str,
                    item.incentive_str,
                    item.budget,
                    item.utility_allocation,
                ]
            )
        for budget, total in self.total_verifier_additional_incentives.items():
            label = f"{budget} Total" if len(budget) == 3 else f"Grand {budget}"
            bucket = budget if len(budget) == 3 else None
            additional.append([None, None, label, f"$ {total:,.2f}", bucket])

        result += tabulate(
            additional,
            headers=[
                "Builder Incentive",
                "Reported",
                "Eligible",
                "Incentive",
                "Budget",
                "Utility Budget",
            ],
        )

        return result
