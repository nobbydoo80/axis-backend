"""calculator.py - Axis"""

__author__ = "Steven K"
__date__ = "3/1/22 14:39"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
from dataclasses import dataclass
from decimal import Decimal
from functools import cached_property

import math
from tabulate import tabulate

from axis.customer_eto.calculator.eps_2022.allocations import Allocation
from axis.customer_eto.calculator.eps_2022.calculations import Calculations
from axis.customer_eto.calculator.eps_2022.carbon import Carbon
from axis.customer_eto.calculator.eps_2022.incentives import Incentives
from axis.customer_eto.calculator.eps_2022.projected import Projected
from axis.customer_eto.calculator.eps_2022.savings import Savings
from axis.customer_eto.eep_programs.eto_2022 import (
    SmartThermostatBrands2022,
    AdditionalElements2022,
    SolarElements2022,
    CobidRegistered,
    CobidQualification,
)
from axis.customer_eto.eep_programs.fire_rebuild_2021 import FireResilienceBonus
from axis.customer_eto.enumerations import (
    PNWUSStates,
    ClimateLocation,
    ElectricUtility,
    GasUtility,
    Fireplace2020,
    PrimaryHeatingEquipment2020,
    QualifyingThermostat,
    HeatType,
)

log = logging.getLogger(__name__)


@dataclass
class EPS2022Calculator:
    us_state: PNWUSStates
    climate_location: ClimateLocation
    conditioned_area: float
    primary_heating_class: PrimaryHeatingEquipment2020

    electric_utility: ElectricUtility = ElectricUtility.NONE
    gas_utility: GasUtility = GasUtility.NONE

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
    has_heat_pump_water_heater: bool = False

    # From checklist
    improved_pv_kwh: float = 0.0
    thermostat_brand: SmartThermostatBrands2022 = SmartThermostatBrands2022.NONE
    fireplace: Fireplace2020 = Fireplace2020.NONE
    electric_elements: AdditionalElements2022 = AdditionalElements2022.NO
    cobid_registered: CobidRegistered = CobidRegistered.NO
    cobid_type: CobidQualification = CobidQualification.NO
    solar_elements: SolarElements2022 | None = None
    fire_resiliance_bonus: FireResilienceBonus | None = None

    # Misc
    electric_rate: Decimal = "0.0"
    gas_rate: Decimal = "0.0"

    @cached_property
    def input_str(self) -> str:
        input_data_str = "input_data = {"
        input_data_str += f"""
    "us_state": {self.us_state},
    "climate_location": {self.climate_location},
    "primary_heating_class": {self.primary_heating_class},
    "conditioned_area": {self.conditioned_area},
    "electric_utility": {self.electric_utility},
    "gas_utility": {self.gas_utility},
    "fireplace": {self.fireplace},
    "thermostat_brand": {self.thermostat_brand},
    "electric_elements": {self.electric_elements},
    "solar_elements": {self.solar_elements},
    "cobid_registered": {self.cobid_registered},
    "cobid_type": {self.cobid_type},
    "fire_resiliance_bonus": {self.fire_resiliance_bonus},
    "code_heating_therms": {self.code_heating_therms},
    "code_heating_kwh": {self.code_heating_kwh},
    "code_cooling_kwh": {self.code_cooling_kwh},
    "code_hot_water_therms": {self.code_hot_water_therms},
    "code_hot_water_kwh": {self.code_hot_water_kwh},
    "code_lights_and_appliance_therms": {self.code_lights_and_appliance_therms},
    "code_lights_and_appliance_kwh": {self.code_lights_and_appliance_kwh},
    "improved_heating_therms": {self.improved_heating_therms},
    "improved_heating_kwh": {self.improved_heating_kwh},
    "improved_cooling_kwh": {self.improved_cooling_kwh},
    "improved_hot_water_therms": {self.improved_hot_water_therms},
    "improved_hot_water_kwh": {self.improved_hot_water_kwh},
    "improved_lights_and_appliance_therms": {self.improved_lights_and_appliance_therms},
    "improved_lights_and_appliance_kwh": {self.improved_lights_and_appliance_kwh},
    "improved_pv_kwh": {self.improved_pv_kwh},
    "electric_rate": {self.electric_rate},
    "gas_rate": {self.gas_rate},\n"""
        input_data_str += "}\n"
        input_data_str += "calculator = EPS2022Calculator(**input_data)"
        return input_data_str

    @cached_property
    def thermostat(self) -> QualifyingThermostat:
        if self.thermostat_brand in [
            None,
            SmartThermostatBrands2022.OTHER,
            SmartThermostatBrands2022.NONE,
        ]:
            return QualifyingThermostat.NONE

        if self.primary_heating_class == PrimaryHeatingEquipment2020.GAS_FURNACE:
            return QualifyingThermostat.DUCTED_FURNACE
        if self.primary_heating_class in [
            PrimaryHeatingEquipment2020.DFHP,
            PrimaryHeatingEquipment2020.DUCTED_ASHP,
            PrimaryHeatingEquipment2020.MINI_SPLIT_DUCTED,
        ]:
            return QualifyingThermostat.DUCTED_ASHP

        return QualifyingThermostat.NONE

    @cached_property
    def heat_type(self) -> HeatType:
        if self.primary_heating_class in [
            PrimaryHeatingEquipment2020.GAS_FIREPLACE,
            PrimaryHeatingEquipment2020.GAS_UNIT_HEATER,
            PrimaryHeatingEquipment2020.GAS_FURNACE,
            PrimaryHeatingEquipment2020.GAS_BOILER,
            PrimaryHeatingEquipment2020.OTHER_GAS,
        ]:
            return HeatType.GAS
        return HeatType.ELECTRIC

    @cached_property
    def net_zero(self) -> bool:
        return self.solar_elements == SolarElements2022.NET_ZERO

    @cached_property
    def solar_ready(self) -> bool:
        return self.solar_elements == SolarElements2022.SOLAR_READY

    @cached_property
    def solar_production(self) -> float:
        return self.improved_pv_kwh

    @cached_property
    def ev_ready(self) -> bool:
        return self.electric_elements in [
            AdditionalElements2022.ELECTRIC_CAR,
            AdditionalElements2022.SOLAR_AND_ELECTRIC_CAR,
            AdditionalElements2022.ALL,
        ]

    @cached_property
    def storage_ready(self) -> bool:
        return self.electric_elements in [
            AdditionalElements2022.SOLAR_AND_STORAGE,
            AdditionalElements2022.ALL,
        ]

    @cached_property
    def corbid_builder(self) -> bool:
        return any(
            [
                self.cobid_registered in [CobidRegistered.BUILDER, CobidRegistered.BOTH],
                self.cobid_type not in [CobidQualification.NO],
            ]
        )

    @cached_property
    def corbid_verifier(self) -> bool:
        return any(
            [
                self.cobid_registered in [CobidRegistered.VERIFIER, CobidRegistered.BOTH],
                self.cobid_type not in [CobidQualification.NO],
            ]
        )

    @cached_property
    def fire_rebuild(self) -> bool:
        return self.fire_resiliance_bonus in [
            FireResilienceBonus.NO,
            FireResilienceBonus.SEALED_ATTIC,
            FireResilienceBonus.RIGID_INSULATION,
            FireResilienceBonus.TRIPLE_PANE,
            FireResilienceBonus.TRIPLE_PANE_AND_RIGID_INSULATION,
            FireResilienceBonus.TRIPLE_PANE_AND_SEALED_ATTIC,
            FireResilienceBonus.RIGID_INSULATION_AND_SEALED_ATTIC,
            FireResilienceBonus.TRIPLE_PANE_AND_RIGID_INSULATION_AND_SEALED_ATTIC,
        ]

    @cached_property
    def triple_pane_windows(self) -> bool:
        return self.fire_resiliance_bonus in [
            FireResilienceBonus.TRIPLE_PANE,
            FireResilienceBonus.TRIPLE_PANE_AND_RIGID_INSULATION,
            FireResilienceBonus.TRIPLE_PANE_AND_SEALED_ATTIC,
            FireResilienceBonus.TRIPLE_PANE_AND_RIGID_INSULATION_AND_SEALED_ATTIC,
        ]

    @cached_property
    def exterior_rigid_insulation(self) -> bool:
        return self.fire_resiliance_bonus in [
            FireResilienceBonus.RIGID_INSULATION,
            FireResilienceBonus.TRIPLE_PANE_AND_RIGID_INSULATION,
            FireResilienceBonus.RIGID_INSULATION_AND_SEALED_ATTIC,
            FireResilienceBonus.TRIPLE_PANE_AND_RIGID_INSULATION_AND_SEALED_ATTIC,
        ]

    @cached_property
    def sealed_attic(self) -> bool:
        return self.fire_resiliance_bonus in [
            FireResilienceBonus.SEALED_ATTIC,
            FireResilienceBonus.TRIPLE_PANE_AND_SEALED_ATTIC,
            FireResilienceBonus.RIGID_INSULATION_AND_SEALED_ATTIC,
            FireResilienceBonus.TRIPLE_PANE_AND_RIGID_INSULATION_AND_SEALED_ATTIC,
        ]

    @cached_property
    def _input_model_data_report(self) -> str:
        results = "Model Data\n"
        results += tabulate(
            [
                [
                    "Heating Therms",
                    self.code_heating_therms,
                    self.improved_heating_therms,
                ],
                [
                    "Heating kWh",
                    self.code_heating_kwh,
                    self.improved_heating_kwh,
                ],
                [
                    "Cooling kWh",
                    self.code_cooling_kwh,
                    self.improved_cooling_kwh,
                ],
                [
                    "Water Heating Therms",
                    self.code_hot_water_therms,
                    self.improved_hot_water_therms,
                ],
                [
                    "Water Heating kWh",
                    self.code_hot_water_kwh,
                    self.improved_hot_water_kwh,
                ],
                [
                    "Lights & Appliances Therms",
                    self.code_lights_and_appliance_therms,
                    self.improved_lights_and_appliance_therms,
                ],
                [
                    "Lights & Appliances kWh",
                    self.code_lights_and_appliance_kwh,
                    self.improved_lights_and_appliance_kwh,
                ],
                [
                    "PV kWh",
                    None,
                    self.improved_pv_kwh,
                ],
            ],
            headers=["", "Code", "Improvement"],
            floatfmt=".3f",
        )
        return results

    @cached_property
    def _input_savings_data_report(self) -> str:
        results = "Axis Data for Modeled Savings Tab\n"
        results += tabulate(
            [
                ["Heat Type", self.heat_type.value],
                ["Smart Thermostat", self.thermostat.value],
                ["Fireplace EF", self.fireplace.value],
            ],
        )
        return results

    @cached_property
    def _input_incentive_data_report(self) -> str:
        results = "Axis Data for Modeled Savings Tab\n"
        results += tabulate(
            [
                ["Electric Utility", self.electric_utility.value],
                ["Gas Utility", self.gas_utility.value],
                [],
                ["Solar Production", f"{self.solar_production:.1f}"],
                [],
                ["Additional Incentives"],
                ["Net Zero", "Yes" if self.net_zero else "No"],
                ["ESH: EV Ready", "Yes" if self.ev_ready else "No"],
                ["ESH: Solar & Storage", "Yes" if self.storage_ready else "No"],
                ["Solar Ready", "Yes" if self.solar_ready else "No"],
                ["Builder DEI", "Yes" if self.corbid_builder else "No"],
                ["Verifier DEI", "Yes" if self.corbid_verifier else "No"],
                ["Heat Pump Water Heater", "Yes" if self.has_heat_pump_water_heater else "No"],
                [],
                ["Fire Rebuild Only"],
                ["Fire Rebuild", "Yes" if self.fire_rebuild else "No"],
                ["Triple Pane Windows", "Yes" if self.triple_pane_windows else "No"],
                ["Exterior Rigid Insulation", "Yes" if self.exterior_rigid_insulation else "No"],
                ["Sealed Attic", "Yes" if self.sealed_attic else "No"],
            ]
        )
        return results

    @cached_property
    def percent_generation_kwh(self):
        try:
            pv_generation_pct = self.improved_pv_kwh / self.savings.kwh.proposed
            return max([min([math.floor(pv_generation_pct * 100.0) / 100.0, 1.0]), 0])
        except (TypeError, ZeroDivisionError):
            return 0.0

    @cached_property
    def _input_eps_data_report(self):
        results = "Axis data for EPS Sheet / XML Outputs\n"
        results += tabulate(
            [
                ["Climate Location", self.climate_location.value],
                ["Home Square Footage", self.conditioned_area],
                [],
                [
                    "Electric Annual Cost",
                    f"$ {self.savings.electric_costing.annual_proposed_cost:,.2f}",
                ],
                ["Gas Annual Cost", f"$ {self.savings.gas_costing.annual_proposed_cost:,.2f}"],
                [],
                ["PV Electric Offset %", f"{self.percent_generation_kwh:.1%}"],
            ]
        )
        return results

    @cached_property
    def input_report(self) -> str:
        results = self._input_model_data_report + 2 * "\n"
        results += self._input_savings_data_report + 2 * "\n"
        results += self._input_incentive_data_report + 2 * "\n"
        results += self._input_eps_data_report + 2 * "\n"
        return results

    @cached_property
    def calculations(self) -> Calculations:
        return Calculations(
            heat_type=self.heat_type,
            code_heating_therms=self.code_heating_therms,
            code_heating_kwh=self.code_heating_kwh,
            code_cooling_kwh=self.code_cooling_kwh,
            code_hot_water_therms=self.code_hot_water_therms,
            code_hot_water_kwh=self.code_hot_water_kwh,
            code_lights_and_appliance_therms=self.code_lights_and_appliance_therms,
            code_lights_and_appliance_kwh=self.code_lights_and_appliance_kwh,
            improved_heating_therms=self.improved_heating_therms,
            improved_heating_kwh=self.improved_heating_kwh,
            improved_cooling_kwh=self.improved_cooling_kwh,
            improved_hot_water_therms=self.improved_hot_water_therms,
            improved_hot_water_kwh=self.improved_hot_water_kwh,
            improved_lights_and_appliance_therms=self.improved_lights_and_appliance_therms,
            improved_lights_and_appliance_kwh=self.improved_lights_and_appliance_kwh,
            improved_pv_kwh=self.improved_pv_kwh,
            code_fireplace_savings_therms=self.savings.fireplace_savings.code_fireplace_therms,
            improved_fireplace_savings_therms=self.savings.fireplace_savings.improved_fireplace_therms,
            thermostat_heating_kwh_savings=self.savings.heating_cooling.thermostat_heating_kwh_savings,
            thermostat_heating_therm_savings=self.savings.heating_cooling.thermostat_heating_therm_savings,
            thermostat_cooling_kwh_savings=self.savings.heating_cooling.thermostat_cooling_kwh_savings,
        )

    @cached_property
    def savings(self) -> Savings:
        return Savings(
            code_heating_therms=self.code_heating_therms,
            code_heating_kwh=self.code_heating_kwh,
            code_cooling_kwh=self.code_cooling_kwh,
            code_hot_water_therms=self.code_hot_water_therms,
            code_hot_water_kwh=self.code_hot_water_kwh,
            code_lights_and_appliance_therms=self.code_lights_and_appliance_therms,
            code_lights_and_appliance_kwh=self.code_lights_and_appliance_kwh,
            improved_heating_therms=self.improved_heating_therms,
            improved_heating_kwh=self.improved_heating_kwh,
            improved_cooling_kwh=self.improved_cooling_kwh,
            improved_hot_water_therms=self.improved_hot_water_therms,
            improved_hot_water_kwh=self.improved_hot_water_kwh,
            improved_lights_and_appliance_therms=self.improved_lights_and_appliance_therms,
            improved_lights_and_appliance_kwh=self.improved_lights_and_appliance_kwh,
            improved_pv_kwh=self.improved_pv_kwh,
            thermostat=self.thermostat,
            fireplace=self.fireplace,
            electric_rate=self.electric_rate,
            gas_rate=self.gas_rate,
        )

    @cached_property
    def incentives(self) -> Incentives:
        solar_production = self.solar_production
        if self.solar_elements == [SolarElements2022.SOLAR_READY, SolarElements2022.NON_ETO_SOLAR]:
            solar_production = 0.0

        return Incentives(
            percent_improvement=self.savings.mbtu.pct_improvement,
            therm_percent_improvement=self.savings.therm.pct_improvement,
            solar_production=solar_production,
            improved_total_kwh=self.savings.kwh.proposed,
            improved_total_therms=self.savings.therm.proposed,
            fire_rebuild=self.fire_rebuild,
            net_zero=self.net_zero,
            solar_ready=self.solar_ready,
            storage_ready=self.storage_ready,
            ev_ready=self.ev_ready,
            corbid_builder=self.corbid_builder,
            corbid_verifier=self.corbid_verifier,
            has_heat_pump_water_heater=self.has_heat_pump_water_heater,
            triple_pane_windows=self.triple_pane_windows,
            exterior_rigid_insulation=self.exterior_rigid_insulation,
            sealed_attic=self.sealed_attic,
            heat_type=self.heat_type,
            electric_utility=self.electric_utility,
            gas_utility=self.gas_utility,
        )

    @cached_property
    def allocations(self) -> Allocation:
        return Allocation(
            percent_improvement=self.savings.mbtu.pct_improvement,
            heating_therms=self.improved_heating_therms,
            hot_water_therms=self.improved_hot_water_therms,
            electric_utility=self.electric_utility,
            gas_utility=self.gas_utility,
            builder_base_incentive=self.incentives.baseline_builder_incentive,
            builder_additional_incentives=self.incentives.builder_additional_incentives,
            verifier_base_incentive=self.incentives.baseline_verifier_incentive,
            verifier_additional_incentives=self.incentives.verifier_additional_incentives,
            heat_type=self.heat_type,
        )

    @cached_property
    def projected(self) -> Projected:
        return Projected(
            climate_location=self.climate_location,
            heat_type=self.heat_type,
            conditioned_area=self.conditioned_area,
            electric_utility=self.electric_utility,
            gas_utility=self.gas_utility,
        )

    @cached_property
    def carbon(self) -> Carbon:
        return Carbon(
            climate_location=self.climate_location,
            heat_type=self.heat_type,
            conditioned_area=self.conditioned_area,
            electric_utility=self.electric_utility,
            code_total_kwh=self.savings.kwh.baseline,
            improved_total_kwh=self.savings.kwh.proposed,
            code_total_therms=self.savings.therm.baseline,
            improved_total_therms=self.savings.therm.proposed,
        )

    @cached_property
    def improved_electric_cost(self):
        return max([0, self.savings.electric_costing.annual_proposed_cost])

    @cached_property
    def improved_gas_cost(self):
        return max([0, self.savings.gas_costing.annual_proposed_cost])

    @cached_property
    def annual_cost(self):
        return round(self.improved_electric_cost + self.improved_gas_cost, 2)

    @cached_property
    def monthly_cost(self):
        return 0 if self.annual_cost == 0.0 else self.annual_cost / 12.0

    @cached_property
    def annual_cost_code(self):
        return round(
            self.savings.gas_costing.annual_baseline_cost
            + self.savings.electric_costing.annual_baseline_cost,
            2,
        )

    @cached_property
    def monthly_cost_code(self):
        return 0 if self.annual_cost_code == 0.0 else self.annual_cost_code / 12.0
