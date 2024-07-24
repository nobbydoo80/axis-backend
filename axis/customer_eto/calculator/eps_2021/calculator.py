"""calculator.py - Axis"""

__author__ = "Steven K"
__date__ = "9/8/21 13:13"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
from functools import cached_property

import math
from tabulate import tabulate

from .base import (
    SimData,
    round_value,
    ImprovementData,
    ImprovementSummmaryData,
)
from .calculations import CodeCalculation, ImprovedCalculation
from .constants import Constants
from .incentives import Incentives2021WA, Incentives2020
from .net_zero import NetZero2020
from .projected import Projected2021
from ...enumerations import (
    HeatType,
    PNWUSStates,
    ElectricUtility,
    GasUtility,
    ClimateLocation,
    Fireplace2020,
    QualifyingThermostat,
    GridHarmonization2020,
    AdditionalIncentives2020,
    SolarElements2020,
    PrimaryHeatingEquipment2020,
    SmartThermostatBrands2020,
)

log = logging.getLogger(__name__)


class EPS2021Calculator:
    def __init__(
        self,
        us_state: PNWUSStates,
        climate_location: ClimateLocation,
        conditioned_area: float,
        electric_utility: ElectricUtility,
        gas_utility: GasUtility,
        primary_heating_class: PrimaryHeatingEquipment2020,
        thermostat_brand: SmartThermostatBrands2020,
        fireplace: Fireplace2020 = Fireplace2020.NONE,
        grid_harmonization_elements: GridHarmonization2020 = GridHarmonization2020.NONE,
        eps_additional_incentives: AdditionalIncentives2020 = AdditionalIncentives2020.NO,
        solar_elements: SolarElements2020 = SolarElements2020.NONE,
        code_heating_therms: float = 0,
        code_heating_kwh: float = 0,
        code_cooling_kwh: float = 0,
        code_hot_water_therms: float = 0,
        code_hot_water_kwh: float = 0,
        code_lights_and_appliance_therms: float = 0,
        code_lights_and_appliance_kwh: float = 0,
        code_electric_cost: float = 0,
        code_gas_cost: float = 0,
        improved_heating_therms: float = 0,
        improved_heating_kwh: float = 0,
        improved_cooling_kwh: float = 0,
        improved_hot_water_therms: float = 0,
        improved_hot_water_kwh: float = 0,
        improved_lights_and_appliance_therms: float = 0,
        improved_lights_and_appliance_kwh: float = 0,
        improved_pv_kwh: float = 0,
        improved_solar_hot_water_therms: float = 0,
        improved_solar_hot_water_kwh: float = 0,
        improved_electric_cost: float = 0,
        improved_gas_cost: float = 0,
        has_heat_pump_water_heater: bool = False,
    ):
        self.us_state = us_state
        self.climate_location = climate_location
        self.conditioned_area = conditioned_area
        self.electric_utility = electric_utility
        self.gas_utility = gas_utility
        self.primary_heating_class = primary_heating_class
        self.thermostat_brand = thermostat_brand
        self.fireplace = fireplace
        self.grid_harmonization_elements = grid_harmonization_elements
        self.eps_additional_incentives = eps_additional_incentives
        self.solar_elements = solar_elements
        self.has_heat_pump_water_heater = has_heat_pump_water_heater

        total_kwh = (
            code_heating_kwh + code_cooling_kwh + code_hot_water_kwh + code_lights_and_appliance_kwh
        )
        total_therms = (
            code_heating_therms + code_hot_water_therms + code_lights_and_appliance_therms
        )

        self.code = SimData(
            code_heating_therms,
            code_heating_kwh,
            code_cooling_kwh,
            code_hot_water_therms,
            code_hot_water_kwh,
            0,
            0,
            code_lights_and_appliance_therms,
            code_lights_and_appliance_kwh,
            0,
            total_therms,
            total_kwh,
            code_electric_cost,
            code_gas_cost,
        )

        total_kwh = (
            improved_heating_kwh
            + improved_cooling_kwh
            + improved_hot_water_kwh
            + improved_lights_and_appliance_kwh
            - improved_pv_kwh
        )
        if improved_solar_hot_water_kwh:
            total_kwh -= improved_hot_water_kwh
            total_kwh += improved_solar_hot_water_kwh

        total_therms = (
            improved_heating_therms
            + improved_hot_water_therms
            + improved_lights_and_appliance_therms
        )
        if improved_solar_hot_water_therms:
            total_therms -= improved_hot_water_therms
            total_therms += improved_solar_hot_water_therms

        self.improved = SimData(
            improved_heating_therms,
            improved_heating_kwh,
            improved_cooling_kwh,
            improved_hot_water_therms,
            improved_hot_water_kwh,
            improved_solar_hot_water_therms,
            improved_solar_hot_water_kwh,
            improved_lights_and_appliance_therms,
            improved_lights_and_appliance_kwh,
            improved_pv_kwh,
            total_therms,
            total_kwh,
            improved_electric_cost,
            improved_gas_cost,
        )
        self.input_data = {
            "us_state": us_state,
            "climate_location": climate_location,
            "primary_heating_class": primary_heating_class,
            "conditioned_area": conditioned_area,
            "electric_utility": electric_utility,
            "gas_utility": gas_utility,
            "fireplace": fireplace,
            "thermostat_brand": self.thermostat_brand,
            "grid_harmonization_elements": self.grid_harmonization_elements,
            "eps_additional_incentives": self.eps_additional_incentives,
            "solar_elements": self.solar_elements,
            "code_heating_therms": code_heating_therms,
            "code_heating_kwh": code_heating_kwh,
            "code_cooling_kwh": code_cooling_kwh,
            "code_hot_water_therms": code_hot_water_therms,
            "code_hot_water_kwh": code_hot_water_kwh,
            "code_lights_and_appliance_therms": code_lights_and_appliance_therms,
            "code_lights_and_appliance_kwh": code_lights_and_appliance_kwh,
            "code_electric_cost": code_electric_cost,
            "code_gas_cost": code_gas_cost,
            "improved_heating_therms": improved_heating_therms,
            "improved_heating_kwh": improved_heating_kwh,
            "improved_cooling_kwh": improved_cooling_kwh,
            "improved_hot_water_therms": improved_hot_water_therms,
            "improved_hot_water_kwh": improved_hot_water_kwh,
            "improved_lights_and_appliance_therms": improved_lights_and_appliance_therms,
            "improved_lights_and_appliance_kwh": improved_lights_and_appliance_kwh,
            "improved_pv_kwh": improved_pv_kwh,
            "improved_solar_hot_water_therms": improved_solar_hot_water_therms,
            "improved_solar_hot_water_kwh": improved_solar_hot_water_kwh,
            "improved_electric_cost": improved_electric_cost,
            "improved_gas_cost": improved_gas_cost,
            "has_heat_pump_water_heater": has_heat_pump_water_heater,
        }

    @cached_property
    def input_str(self) -> str:
        data = self.input_data
        input_data_str = "input_data = {"
        input_data_str += f"""
    "us_state": {data.get('us_state')},
    "climate_location": {data.get('climate_location')},
    "primary_heating_class": {data.get('primary_heating_class')},
    "conditioned_area": {data.get('conditioned_area')},
    "electric_utility": {data.get('electric_utility')},
    "gas_utility": {data.get('gas_utility')},
    "fireplace": {data.get('fireplace')},
    "thermostat_brand": {data.get('thermostat_brand')},
    "grid_harmonization_elements": {data.get('grid_harmonization_elements')},
    "eps_additional_incentives": {data.get('eps_additional_incentives')},
    "solar_elements": {data.get('solar_elements')},
    "code_heating_therms": {data.get('code_heating_therms')},
    "code_heating_kwh": {data.get('code_heating_kwh')},
    "code_cooling_kwh": {data.get('code_cooling_kwh')},
    "code_hot_water_therms": {data.get('code_hot_water_therms')},
    "code_hot_water_kwh": {data.get('code_hot_water_kwh')},
    "code_lights_and_appliance_therms": {data.get('code_lights_and_appliance_therms')},
    "code_lights_and_appliance_kwh": {data.get('code_lights_and_appliance_kwh')},
    "code_electric_cost": {data.get('code_electric_cost')},
    "code_gas_cost": {data.get('code_gas_cost')},
    "improved_heating_therms": {data.get('improved_heating_therms')},
    "improved_heating_kwh": {data.get('improved_heating_kwh')},
    "improved_cooling_kwh": {data.get('improved_cooling_kwh')},
    "improved_hot_water_therms": {data.get('improved_hot_water_therms')},
    "improved_hot_water_kwh": {data.get('improved_hot_water_kwh')},
    "improved_lights_and_appliance_therms": {data.get('improved_lights_and_appliance_therms')},
    "improved_lights_and_appliance_kwh": {data.get('improved_lights_and_appliance_kwh')},
    "improved_pv_kwh": {data.get('improved_pv_kwh')},
    "improved_solar_hot_water_therms": {data.get('improved_solar_hot_water_therms')},
    "improved_solar_hot_water_kwh": {data.get('improved_solar_hot_water_kwh')},
    "improved_electric_cost": {data.get('improved_electric_cost')},
    "improved_gas_cost": {data.get('improved_gas_cost')},\n"""
        input_data_str += "}\n"
        input_data_str += "calculator = EPS2021Calculator(**input_data)"
        return input_data_str

    @cached_property
    def constants(self):
        return Constants(self.electric_utility, self.us_state, self.thermostat, self.heat_type)

    @cached_property
    def thermostat(self) -> QualifyingThermostat:
        if self.thermostat_brand in [None, "", SmartThermostatBrands2020.NONE]:
            return QualifyingThermostat.NONE

        if self.primary_heating_class in [
            PrimaryHeatingEquipment2020.GAS_FIREPLACE,
            PrimaryHeatingEquipment2020.GAS_UNIT_HEATER,
            PrimaryHeatingEquipment2020.GAS_FURNACE,
            PrimaryHeatingEquipment2020.GAS_BOILER,
            PrimaryHeatingEquipment2020.OTHER_GAS,
        ]:
            return QualifyingThermostat.DUCTED_FURNACE
        if self.primary_heating_class in [
            PrimaryHeatingEquipment2020.ELECTRIC_RESISTANCE,
            PrimaryHeatingEquipment2020.DUCTED_ASHP,
            PrimaryHeatingEquipment2020.GSHP,
            PrimaryHeatingEquipment2020.OTHER_ELECTRIC,
        ]:
            return QualifyingThermostat.DUCTED_ASHP
        return QualifyingThermostat.NONE

    @cached_property
    def heat_type(self):
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
    def input_report(self) -> str:
        def get_value(obj):
            if obj is None:
                return None
            try:
                return obj.value
            except AttributeError:
                return obj

        table = [
            ("Climate Location", get_value(self.input_data["climate_location"])),
            ("Heat Type", self.heat_type.value),
            ("Performace", "Percentage Improvement"),
            ("Conditioned Area", self.conditioned_area),
            ("Electric Utility", self.electric_utility.value),
            ("Gas Utility", self.gas_utility.value),
            ("Qualifying Thermostat", self.thermostat.value),
            ("Fireplace EF", self.fireplace.value),
            (None, None),
            ("HPWH Present", self.has_heat_pump_water_heater),
            (None, None),
            (
                "Grid harmonization elements",
                get_value(self.input_data["grid_harmonization_elements"]),
            ),
            (
                "EPS additional incentives",
                get_value(self.input_data["eps_additional_incentives"]),
            ),
            (
                "Solar Elements",
                get_value(self.input_data["solar_elements"]),
            ),
        ]
        data = tabulate(table, headers=["Input", "Value"])
        data += "\n\n"

        table = [
            [
                "Code:",
                self.code.heating_therms,
                self.code.heating_kwh,
                self.code.cooling_kwh,
                self.code.hot_water_therms,
                self.code.hot_water_kwh,
                self.code.lights_and_appliance_therms,
                self.code.lights_and_appliance_kwh,
                self.code.pv_kwh,
                self.code.total_therms,
                self.code.total_kwh,
                self.code.electric_cost,
                self.code.gas_cost,
            ],
            [
                "Improved:",
                self.improved.heating_therms,
                self.improved.heating_kwh,
                self.improved.cooling_kwh,
                self.improved.hot_water_therms,
                self.improved.hot_water_kwh,
                self.improved.lights_and_appliance_therms,
                self.improved.lights_and_appliance_kwh,
                self.improved.pv_kwh,
                self.improved.total_therms,
                self.improved.total_kwh,
                self.improved.electric_cost,
                self.improved.gas_cost,
            ],
            [],
            [
                None,
                None,
                None,
                "Water w/Solar"
                if self.improved.solar_hot_water_therms or self.improved.solar_hot_water_kwh
                else None,
                self.improved.solar_hot_water_therms
                if self.improved.solar_hot_water_therms or self.improved.solar_hot_water_kwh
                else None,
                self.improved.solar_hot_water_kwh
                if self.improved.solar_hot_water_therms or self.improved.solar_hot_water_kwh
                else None,
            ],
        ]
        data += tabulate(
            table,
            headers=[
                "Data Type",
                "Heating Therms",
                "Heating kWh",
                "Cooling kWh",
                "Hot water Therms",
                "Hot water kWh",
                "L & A Therms",
                "L & A kWh",
                "PV kWH",
                "Total Therms",
                "Total kWH",
                "Electric Cost",
                "Gas Cost",
            ],
            floatfmt=f".{round_value}f",
        )
        # data += "Excel Input\n"
        # data += ",".join(map(str, table[0][1:])) + "\n"
        # data += ",".join(map(str, table[1][1:])) + "\n"
        return data

    @cached_property
    def code_calculations(self):
        return CodeCalculation(
            self.code.heating_therms,
            self.code.heating_kwh,
            self.code.cooling_kwh,
            self.code.hot_water_therms,
            self.code.hot_water_kwh,
            self.code.lights_and_appliance_therms,
            self.code.lights_and_appliance_kwh,
            self.fireplace,
            self.heat_type,
            self.constants,
        )

    @cached_property
    def improved_calculations(self):
        return ImprovedCalculation(
            self.improved.heating_therms,
            self.improved.heating_kwh,
            self.improved.cooling_kwh,
            self.improved.hot_water_therms,
            self.improved.hot_water_kwh,
            self.improved.lights_and_appliance_therms,
            self.improved.lights_and_appliance_kwh,
            self.improved.solar_hot_water_therms,
            self.improved.solar_hot_water_kwh,
            self.improved.pv_kwh,
            self.fireplace,
            self.thermostat,
            self.heat_type,
            self.constants,
            self.us_state,
        )

    @cached_property
    def improvement_data(self) -> ImprovementSummmaryData:
        code = ImprovementData(*self.code_calculations.unadjusted_consumption)
        improved = ImprovementData(*self.improved_calculations.unadjusted_consumption)
        if self.heat_type == HeatType.ELECTRIC:
            code = ImprovementData(*self.code_calculations.hp_correction_consumption)
            improved = ImprovementData(*self.improved_calculations.hp_correction_consumption)

        savings = ImprovementData(
            code.therms - improved.therms, code.kwh - improved.kwh, code.mbtu - improved.mbtu
        )

        try:
            therm_improvement = savings.therms / code.therms
        except ZeroDivisionError:
            therm_improvement = 0.0

        percent_improvement_breakout = ImprovementData(
            therm_improvement,
            savings.kwh / code.kwh,
            savings.mbtu / code.mbtu,
        )
        floored_percent_improvement = ImprovementData(
            math.floor(therm_improvement * 100.0) / 100.0,
            math.floor((savings.kwh / code.kwh) * 100.0) / 100.0,
            math.floor((savings.mbtu / code.mbtu) * 100.0) / 100.0,
        )
        return ImprovementSummmaryData(
            code,
            improved,
            savings,
            percent_improvement_breakout,
            floored_percent_improvement,
            percent_improvement_breakout.mbtu,
        )

    @cached_property
    def improvement_report(self) -> str:
        improvement_data = self.improvement_data
        return tabulate(
            [
                [
                    "Total Therms",
                    improvement_data.code.therms,
                    improvement_data.improved.therms,
                    improvement_data.savings.therms,
                    improvement_data.percent_improvement_breakout.therms * 100.0,
                ],
                [
                    "Total kWh",
                    improvement_data.code.kwh,
                    improvement_data.improved.kwh,
                    improvement_data.savings.kwh,
                    improvement_data.percent_improvement_breakout.kwh * 100.0,
                ],
                [
                    "Total mBtu",
                    improvement_data.code.mbtu,
                    improvement_data.improved.mbtu,
                    improvement_data.savings.mbtu,
                    None,
                ],
                [
                    "% Better than code",
                    None,
                    None,
                    None,
                    improvement_data.percent_improvement * 100.0,
                ],
            ],
            headers=["", "Code", "Improvement", "Savings", "% Better"],
            floatfmt=f".{round_value}f",
        )

    @cached_property
    def incentives(self):
        if self.us_state == PNWUSStates.WA:
            return Incentives2021WA(
                self.improvement_data.percent_improvement_breakout.therms,
                self.electric_utility,
                self.gas_utility,
                self.improved.heating_therms,
                self.improved.hot_water_therms,  # TODO BUG REPORT
                self.improved.hot_water_kwh,
                self.constants,
                self.net_zero,
            )
        return Incentives2020(
            self.improvement_data.percent_improvement,
            self.electric_utility,
            self.gas_utility,
            self.improved.heating_therms,
            self.improved.hot_water_therms,
            self.improved.hot_water_kwh,
            self.constants,
            self.net_zero,
            self.has_heat_pump_water_heater,
        )

    @cached_property
    def projected(self):
        return Projected2021(
            self.constants.get_simplified_location(self.climate_location),
            self.heat_type,
            self.conditioned_area,
            self.electric_utility,
            self.gas_utility,
            self.constants,
        )

    @cached_property
    def net_zero(self):
        return NetZero2020(
            self.improved.total_kwh,
            self.improved.total_therms,
            self.improved.cooling_kwh,
            self.improved.pv_kwh,
            self.improvement_data.percent_improvement,
            self.improvement_data.percent_improvement_breakout.therms,
            self.us_state,
            self.constants,
            self.electric_utility,
            self.primary_heating_class,
            self.thermostat_brand,
            self.grid_harmonization_elements,
            self.eps_additional_incentives,
            self.solar_elements,
        )

    @cached_property
    def annual_cost(self):
        return max([0, self.improved.gas_cost + self.improved.electric_cost])

    @cached_property
    def monthly_cost(self):
        return 0 if self.annual_cost == 0.0 else self.annual_cost / 12.0

    @cached_property
    def annual_cost_code(self):
        return max([0, self.code.gas_cost + self.code.electric_cost])

    @cached_property
    def monthly_cost_code(self):
        return 0 if self.annual_cost_code == 0.0 else self.annual_cost_code / 12.0

    @cached_property
    def as_built_report(self) -> str:
        data = "Home as built\n"

        pct_string = "Percent Improvement:"
        pct_improvement = self.improvement_data.floored_improvement_breakout.mbtu
        if self.us_state == PNWUSStates.WA:
            pct_string = "Gas Percent Improvement:"
            pct_improvement = self.improvement_data.floored_improvement_breakout.therms

        data += tabulate(
            [
                ["EPS:", self.improved_calculations.eps_score, "MBtu"],
                ["EPS (Code):", self.code_calculations.code_eps_score, "MBtu"],
                [
                    pct_string,
                    f"{pct_improvement:.0%}",
                    "MBtu",
                ],
                [
                    "Builder Incentive:",
                    f"$ {self.incentives.builder_incentive:,.0f}",
                    "2021 Incentive",
                ],
                [
                    "Verifier Incentive:",
                    f"$ {self.incentives.verifier_incentive:,.0f}",
                    "2021 Incentive",
                ],
                [
                    "Carbon Score:",
                    f"{self.improved_calculations.carbon_score:.1f}",
                    "Tons CO2/year",
                ],
                [
                    "Code Carbon Score:",
                    f"{self.code_calculations.code_carbon_score:.1f}",
                    "Tons CO2/year",
                ],
                [
                    "Annual Energy Costs:",
                    f"$ {self.annual_cost:,.0f}",
                    "$ per year",
                ],
                [
                    "Monthly Energy Costs:",
                    f"$ {self.monthly_cost:,.0f}",
                    "$ per month",
                ],
                [
                    "Similar Size OR Home Score:",
                    f"{self.projected.similar_size_eps:.0f}",
                    "MBtu",
                ],
                [
                    "Similar Size OR Home Carbon Score:",
                    f"{self.projected.similar_size_carbon:.1f}",
                    "Tons CO2/year",
                ],
            ]
        )
        return data
