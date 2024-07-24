"""calculations.py - Axis"""

__author__ = "Steven K"
__date__ = "9/10/21 12:38"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
from functools import cached_property

from tabulate import tabulate
from simulation.enumerations import EnergyUnit
from simulation.utils.conversions import convert_kwh_to, convert_therm_to

from .base import (
    round_value,
    CodeData,
    ConsumptionCalculationData,
    CarbonCalculationData,
    EPSCalculationData,
    ImprovedData,
)
from .constants import Constants
from ...enumerations import Fireplace2020, QualifyingThermostat, HeatType, PNWUSStates

log = logging.getLogger(__name__)


class CodeCalculation:
    def __init__(
        self,
        heating_therms: float,
        heating_kwh: float,
        cooling_kwh: float,
        hot_water_therms: float,
        hot_water_kwh: float,
        lights_and_appliance_therms: float,
        lights_and_appliance_kwh: float,
        fireplace: Fireplace2020,
        heat_type: HeatType,
        constants: Constants,
    ):
        self.heat_type = heat_type
        self.constants = constants

        fireplace_therms = 0
        if fireplace != Fireplace2020.NONE:
            fireplace_therms = self.constants.fireplace_addition_therms

        self.unadjusted = CodeData(
            heating_therms,
            heating_kwh,
            cooling_kwh,
            hot_water_therms,
            hot_water_kwh,
            lights_and_appliance_therms,
            lights_and_appliance_kwh,
            fireplace_therms,
        )

    @cached_property
    def unadjusted_carbon(self) -> CarbonCalculationData:
        therms = (
            sum(
                [
                    self.unadjusted.heating_therms,
                    self.unadjusted.hot_water_therms,
                    self.unadjusted.lights_and_appliance_therms,
                    self.unadjusted.fireplace_therms,
                ]
            )
            * self.constants.natural_gas_carbon_factor
            / 2000.00
        )
        kwh = (
            sum(
                [
                    self.unadjusted.heating_kwh,
                    self.unadjusted.cooling_kwh,
                    self.unadjusted.hot_water_kwh,
                    self.unadjusted.lights_and_appliance_kwh,
                ]
            )
            * self.constants.electric_carbon_factor
            / 2000.00
        )
        return CarbonCalculationData(therms, kwh, therms + kwh)

    @cached_property
    def unadjusted_consumption(self) -> ConsumptionCalculationData:
        therms = sum(
            [
                self.unadjusted.heating_therms,
                self.unadjusted.hot_water_therms,
                self.unadjusted.lights_and_appliance_therms,
                self.unadjusted.fireplace_therms,
            ]
        )
        kwh = sum(
            [
                self.unadjusted.heating_kwh,
                self.unadjusted.cooling_kwh,
                self.unadjusted.hot_water_kwh,
                self.unadjusted.lights_and_appliance_kwh,
            ]
        )
        mbtu = convert_kwh_to(kwh, EnergyUnit.MBTU) + convert_therm_to(therms, EnergyUnit.MBTU)
        return ConsumptionCalculationData(therms, kwh, mbtu)

    @cached_property
    def gas_fuel_weight(self) -> CodeData:
        return CodeData(
            self.unadjusted.heating_therms,
            self.unadjusted.heating_kwh,
            self.unadjusted.cooling_kwh,
            self.unadjusted.hot_water_therms,
            self.unadjusted.hot_water_kwh * self.constants.electric_hot_water_fuel_weight,
            self.unadjusted.lights_and_appliance_therms,
            self.unadjusted.lights_and_appliance_kwh,
            self.unadjusted.fireplace_therms,
        )

    @cached_property
    def gas_fuel_weight_eps(self) -> EPSCalculationData:
        therms = sum(
            [
                self.gas_fuel_weight.heating_therms,
                self.gas_fuel_weight.hot_water_therms,
                self.gas_fuel_weight.lights_and_appliance_therms,
                self.gas_fuel_weight.fireplace_therms,
            ]
        )
        kwh = sum(
            [
                self.gas_fuel_weight.heating_kwh,
                self.gas_fuel_weight.cooling_kwh,
                self.gas_fuel_weight.hot_water_kwh,
                self.gas_fuel_weight.lights_and_appliance_kwh,
            ]
        )
        mbtu = convert_kwh_to(kwh, EnergyUnit.MBTU) + convert_therm_to(therms, EnergyUnit.MBTU)
        return EPSCalculationData(therms, kwh, mbtu)

    @cached_property
    def hp_correction(self) -> CodeData:
        return CodeData(
            self.unadjusted.heating_therms,
            self.unadjusted.heating_kwh * self.constants.heat_pump_heating_correction_factor,
            self.unadjusted.cooling_kwh * self.constants.heat_pump_cooling_correction_factor,
            self.unadjusted.hot_water_therms,
            self.unadjusted.hot_water_kwh,
            self.unadjusted.lights_and_appliance_therms,
            self.unadjusted.lights_and_appliance_kwh,
            self.unadjusted.fireplace_therms,
        )

    @cached_property
    def hp_correction_carbon(self) -> CarbonCalculationData:
        therms = (
            sum(
                [
                    self.hp_correction.heating_therms,
                    self.hp_correction.hot_water_therms,
                    self.hp_correction.lights_and_appliance_therms,
                    self.hp_correction.fireplace_therms,
                ]
            )
            * self.constants.natural_gas_carbon_factor
            / 2000.00
        )
        kwh = (
            sum(
                [
                    self.hp_correction.heating_kwh,
                    self.hp_correction.cooling_kwh,
                    self.hp_correction.hot_water_kwh,
                    self.hp_correction.lights_and_appliance_kwh,
                ]
            )
            * self.constants.electric_carbon_factor
            / 2000.00
        )
        return CarbonCalculationData(therms, kwh, therms + kwh)

    @cached_property
    def hp_correction_consumption(self) -> ConsumptionCalculationData:
        therms = sum(
            [
                self.hp_correction.heating_therms,
                self.hp_correction.hot_water_therms,
                self.hp_correction.lights_and_appliance_therms,
                self.hp_correction.fireplace_therms,
            ]
        )
        kwh = sum(
            [
                self.hp_correction.heating_kwh,
                self.hp_correction.cooling_kwh,
                self.hp_correction.hot_water_kwh,
                self.hp_correction.lights_and_appliance_kwh,
            ]
        )
        mbtu = convert_kwh_to(kwh, EnergyUnit.MBTU) + convert_therm_to(therms, EnergyUnit.MBTU)
        return ConsumptionCalculationData(therms, kwh, mbtu)

    @cached_property
    def hp_fuel_weight(self) -> CodeData:
        return CodeData(
            self.hp_correction.heating_therms,
            self.hp_correction.heating_kwh * self.constants.electric_space_heat_fuel_weight,
            self.hp_correction.cooling_kwh,
            self.hp_correction.hot_water_therms,
            self.hp_correction.hot_water_kwh * self.constants.electric_hot_water_fuel_weight,
            self.hp_correction.lights_and_appliance_therms,
            self.hp_correction.lights_and_appliance_kwh,
            self.hp_correction.fireplace_therms,
        )

    @cached_property
    def hp_fuel_weight_eps(self) -> EPSCalculationData:
        therms = sum(
            [
                self.hp_fuel_weight.heating_therms,
                self.hp_fuel_weight.hot_water_therms,
                self.hp_fuel_weight.lights_and_appliance_therms,
                self.hp_fuel_weight.fireplace_therms,
            ]
        )
        kwh = sum(
            [
                self.hp_fuel_weight.heating_kwh,
                self.hp_fuel_weight.cooling_kwh,
                self.hp_fuel_weight.hot_water_kwh,
                self.hp_fuel_weight.lights_and_appliance_kwh,
            ]
        )
        mbtu = convert_kwh_to(kwh, EnergyUnit.MBTU) + convert_therm_to(therms, EnergyUnit.MBTU)
        return EPSCalculationData(therms, kwh, mbtu)

    @cached_property
    def code_eps_score(self) -> float:
        if self.heat_type == HeatType.GAS:
            return max([0, round(self.gas_fuel_weight_eps.total_mbtu, 0)])
        return max([0, round(self.hp_fuel_weight_eps.total_mbtu, 0)])

    @cached_property
    def code_carbon_score(self) -> float:
        if self.heat_type == HeatType.GAS:
            return max([0, self.unadjusted_carbon.carbon_score])
        return max([0, self.hp_correction_carbon.carbon_score])

    @cached_property
    def calculation_report(self) -> str:
        table = [
            [
                "Heating Therms",
                self.unadjusted.heating_therms,
                self.gas_fuel_weight.heating_therms,
                self.hp_correction.heating_therms,
                self.hp_fuel_weight.heating_therms,
            ],
            [
                "Heating kWh",
                self.unadjusted.heating_kwh,
                self.gas_fuel_weight.heating_kwh,
                self.hp_correction.heating_kwh,
                self.hp_fuel_weight.heating_kwh,
            ],
            [
                "Cooling kWh",
                self.unadjusted.cooling_kwh,
                self.gas_fuel_weight.cooling_kwh,
                self.hp_correction.cooling_kwh,
                self.hp_fuel_weight.cooling_kwh,
            ],
            [
                "Water Heating Therms",
                self.unadjusted.hot_water_therms,
                self.gas_fuel_weight.hot_water_therms,
                self.hp_correction.hot_water_therms,
                self.hp_fuel_weight.hot_water_therms,
            ],
            [
                "Water Heating kWh",
                self.unadjusted.hot_water_kwh,
                self.gas_fuel_weight.hot_water_kwh,
                self.hp_correction.hot_water_kwh,
                self.hp_fuel_weight.hot_water_kwh,
            ],
            [
                "Lights & Appliance Therms",
                self.unadjusted.lights_and_appliance_therms,
                self.gas_fuel_weight.lights_and_appliance_therms,
                self.hp_correction.lights_and_appliance_therms,
                self.hp_correction.lights_and_appliance_therms,
            ],
            [
                "Lights & Appliance kWH",
                self.unadjusted.lights_and_appliance_kwh,
                self.gas_fuel_weight.lights_and_appliance_kwh,
                self.hp_correction.lights_and_appliance_kwh,
                self.hp_correction.lights_and_appliance_kwh,
            ],
            [
                "Fireplace Therms",
                self.unadjusted.fireplace_therms,
                self.gas_fuel_weight.fireplace_therms,
                self.hp_correction.fireplace_therms,
                self.hp_correction.fireplace_therms,
            ],
            ["Solar HW kWh"],
            ["Solar WH kWh"],
            ["PV kWh"],
            #
            [],  # EPS
            #
            [
                "Total Therms",
                None,
                self.gas_fuel_weight_eps.total_therms,
                None,
                self.hp_fuel_weight_eps.total_therms,
            ],
            [
                "Total kWh",
                None,
                self.gas_fuel_weight_eps.total_kwh,
                None,
                self.hp_fuel_weight_eps.total_kwh,
            ],
            [
                "Total MBtu",
                None,
                self.gas_fuel_weight_eps.total_mbtu,
                None,
                self.hp_fuel_weight_eps.total_mbtu,
            ],
            #
            [],  # Carbon
            #
            [
                "Total Therms",
                self.unadjusted_carbon.total_therms,
                None,
                self.hp_correction_carbon.total_therms,
            ],
            [
                "Total kWh",
                self.unadjusted_carbon.total_kwh,
                None,
                self.hp_correction_carbon.total_kwh,
            ],
            [
                "Total MBtu",
                self.unadjusted_carbon.carbon_score,
                None,
                self.hp_correction_carbon.carbon_score,
            ],
            #
            [],  # Total Consumption
            #
            [
                "Total Therms",
                self.unadjusted_consumption.total_therms,
                None,
                self.hp_correction_consumption.total_therms,
            ],
            [
                "Total kWh",
                self.unadjusted_consumption.total_kwh,
                None,
                self.hp_correction_consumption.total_kwh,
            ],
        ]
        return tabulate(
            table,
            headers=[
                "CODE HOME CALCULATIONS",
                "Unadj Values",
                "Gas Fuel Weight",
                "HP Correction",
                "HP Fuel Weight",
            ],
            floatfmt=f".{round_value}f",
            # missingval="-",
        )


class ImprovedCalculation:
    def __init__(
        self,
        heating_therms: float,
        heating_kwh: float,
        cooling_kwh: float,
        hot_water_therms: float,
        hot_water_kwh: float,
        lights_and_appliance_therms: float,
        lights_and_appliance_kwh: float,
        solar_hot_water_therms: float,
        solar_hot_water_kwh: float,
        pv_kwh: float,
        fireplace: Fireplace2020,
        thermostat: QualifyingThermostat,
        heat_type: HeatType,
        constants: Constants,
        us_state: PNWUSStates = PNWUSStates.OR,
    ):
        self.heat_type = heat_type
        self.constants = constants
        self.fireplace = fireplace
        self.thermostat = thermostat
        self.us_state = us_state
        self.input_data = ImprovedData(
            heating_therms,
            None,
            heating_kwh,
            None,
            cooling_kwh,
            None,
            hot_water_therms,
            hot_water_kwh,
            lights_and_appliance_therms,
            lights_and_appliance_kwh,
            None,
            solar_hot_water_therms,
            solar_hot_water_kwh,
            pv_kwh,
        )

    @cached_property
    def unadjusted(self) -> ImprovedData:
        gas_tstat = 0
        electric_tstat = 0
        cooling_tstat = 0
        if self.us_state == PNWUSStates.WA:
            if self.thermostat == QualifyingThermostat.DUCTED_FURNACE:
                gas_tstat = (
                    self.input_data.heating_therms * self.constants.smart_thermostat_factor_1
                )
            elif (
                self.input_data.heating_therms == 0.0
                and self.thermostat == QualifyingThermostat.DUCTED_ASHP
            ):
                electric_tstat = (
                    self.input_data.heating_kwh * self.constants.smart_thermostat_factor_2
                )
        else:
            gas_tstat = self.input_data.heating_therms * self.constants.smart_thermostat_factor_1
            electric_tstat = self.input_data.heating_kwh * self.constants.smart_thermostat_factor_1
            cooling_tstat = self.input_data.cooling_kwh * self.constants.smart_thermostat_factor_2

        fireplace = 0
        if self.fireplace != Fireplace2020.NONE:
            fireplace = self.constants.fireplace_addition_therms
        if self.fireplace == Fireplace2020.FE_GTE_70:
            fireplace = self.constants.fireplace_addition_therms_gt70

        return ImprovedData(
            self.input_data.heating_therms,
            gas_tstat,
            self.input_data.heating_kwh,
            electric_tstat,
            self.input_data.cooling_kwh,
            cooling_tstat,
            self.input_data.hot_water_therms,
            self.input_data.hot_water_kwh,
            self.input_data.lights_and_appliance_therms,
            self.input_data.lights_and_appliance_kwh,
            fireplace,
            self.input_data.solar_hot_water_therms,
            self.input_data.solar_hot_water_kwh,
            self.input_data.pv_kwh,
        )

    @cached_property
    def unadjusted_carbon(self) -> CarbonCalculationData:
        therms = sum(
            [
                self.gas_fuel_weight.heating_therms,
                self.gas_fuel_weight.hot_water_therms,
                self.gas_fuel_weight.lights_and_appliance_therms,
                self.gas_fuel_weight.fireplace_therms,
            ]
        )
        if self.unadjusted.solar_hot_water_therms:
            therms = sum(
                [
                    self.gas_fuel_weight.heating_therms,
                    self.gas_fuel_weight.solar_hot_water_therms,
                    self.gas_fuel_weight.lights_and_appliance_therms,
                    self.gas_fuel_weight.fireplace_therms,
                ]
            )
        therms = therms * self.constants.natural_gas_carbon_factor / 2000.00

        kwh = sum(
            [
                self.gas_fuel_weight.heating_kwh,
                self.gas_fuel_weight.cooling_kwh,
                self.gas_fuel_weight.hot_water_kwh,
                self.gas_fuel_weight.lights_and_appliance_kwh,
                -self.gas_fuel_weight.pv_kwh,
            ]
        )
        if self.unadjusted.solar_hot_water_kwh:
            kwh = sum(
                [
                    self.gas_fuel_weight.heating_kwh,
                    self.gas_fuel_weight.cooling_kwh,
                    self.gas_fuel_weight.solar_hot_water_kwh,
                    self.gas_fuel_weight.lights_and_appliance_kwh,
                    -self.gas_fuel_weight.pv_kwh,
                ]
            )
        kwh = kwh * self.constants.improved_electric_carbon_factor / 2000.00
        return CarbonCalculationData(therms, kwh, therms + kwh)

    @cached_property
    def unadjusted_consumption(self) -> ConsumptionCalculationData:
        therms = sum(
            [
                self.gas_fuel_weight.heating_therms,
                self.unadjusted.hot_water_therms,
                self.gas_fuel_weight.lights_and_appliance_therms,
                self.unadjusted.fireplace_therms,
            ]
        )
        kwh = sum(
            [
                self.gas_fuel_weight.heating_kwh,
                self.gas_fuel_weight.cooling_kwh,
                self.unadjusted.hot_water_kwh,
                self.gas_fuel_weight.lights_and_appliance_kwh,
            ]
        )
        mbtu = convert_kwh_to(kwh, EnergyUnit.MBTU) + convert_therm_to(therms, EnergyUnit.MBTU)
        return ConsumptionCalculationData(therms, kwh, mbtu)

    @cached_property
    def gas_fuel_weight(self) -> ImprovedData:
        hot_water_therms = self.unadjusted.hot_water_therms
        if self.unadjusted.solar_hot_water_therms > 0:
            hot_water_therms = 0

        water_heater_kwh = self.unadjusted.hot_water_kwh
        if self.unadjusted.solar_hot_water_kwh > 0:
            water_heater_kwh = 0
        elif self.unadjusted.pv_kwh > 0:
            water_heater_kwh -= self.unadjusted.pv_kwh

        solar_hot_water_kwh = self.unadjusted.solar_hot_water_kwh
        if self.unadjusted.pv_kwh > 0:
            solar_hot_water_kwh -= self.unadjusted.pv_kwh

        pv_kwh = self.unadjusted.pv_kwh - self.unadjusted.hot_water_kwh
        if self.unadjusted.solar_hot_water_kwh > 0:
            pv_kwh = self.unadjusted.pv_kwh - self.unadjusted.solar_hot_water_kwh

        return ImprovedData(
            self.unadjusted.heating_therms - self.unadjusted.gas_thermostat_savings,
            None,
            self.unadjusted.heating_kwh - self.unadjusted.electric_thermostat_savings,
            None,
            self.unadjusted.cooling_kwh - self.unadjusted.cooling_thermostat_savings,
            None,
            hot_water_therms,
            max([0, water_heater_kwh]),
            self.unadjusted.lights_and_appliance_therms,
            self.unadjusted.lights_and_appliance_kwh,
            self.unadjusted.fireplace_therms,
            self.unadjusted.solar_hot_water_therms,
            max([0, solar_hot_water_kwh]),
            max([0, pv_kwh]),
        )

    @cached_property
    def gas_fuel_weight_eps(self) -> EPSCalculationData:
        therms = sum(
            [
                self.gas_fuel_weight.heating_therms,
                self.gas_fuel_weight.hot_water_therms,
                self.gas_fuel_weight.lights_and_appliance_therms,
                self.gas_fuel_weight.fireplace_therms,
                self.gas_fuel_weight.solar_hot_water_therms,
            ]
        )
        kwh = sum(
            [
                self.gas_fuel_weight.heating_kwh,
                self.gas_fuel_weight.cooling_kwh,
                self.gas_fuel_weight.hot_water_kwh * self.constants.electric_hot_water_fuel_weight,
                self.gas_fuel_weight.lights_and_appliance_kwh,
                self.gas_fuel_weight.solar_hot_water_kwh
                * self.constants.electric_hot_water_fuel_weight,
                -self.gas_fuel_weight.pv_kwh,
            ]
        )
        mbtu = convert_kwh_to(kwh, EnergyUnit.MBTU) + convert_therm_to(therms, EnergyUnit.MBTU)
        return EPSCalculationData(therms, kwh, mbtu)

    @cached_property
    def hp_correction(self) -> ImprovedData:
        return ImprovedData(
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        )

    @cached_property
    def hp_correction_carbon(self) -> CarbonCalculationData:
        therms = sum(
            [
                self.hp_fuel_weight.heating_therms,
                self.hp_fuel_weight.hot_water_therms,
                self.hp_fuel_weight.lights_and_appliance_therms,
                self.hp_fuel_weight.fireplace_therms,
            ]
        )
        if self.unadjusted.solar_hot_water_therms:
            therms = sum(
                [
                    self.hp_fuel_weight.heating_therms,
                    self.hp_fuel_weight.solar_hot_water_therms,
                    self.hp_fuel_weight.lights_and_appliance_therms,
                    self.hp_fuel_weight.fireplace_therms,
                ]
            )
        therms = therms * self.constants.natural_gas_carbon_factor / 2000.00

        kwh = sum(
            [
                self.hp_fuel_weight.heating_kwh,
                self.hp_fuel_weight.cooling_kwh,
                self.hp_fuel_weight.hot_water_kwh,
                self.hp_fuel_weight.lights_and_appliance_kwh,
                -self.hp_fuel_weight.pv_kwh,
            ]
        )
        if self.unadjusted.solar_hot_water_kwh:
            kwh = sum(
                [
                    self.hp_fuel_weight.heating_kwh,
                    self.hp_fuel_weight.cooling_kwh,
                    self.hp_fuel_weight.solar_hot_water_kwh,
                    self.hp_fuel_weight.lights_and_appliance_kwh,
                    -self.hp_fuel_weight.pv_kwh,
                ]
            )
        kwh = kwh * self.constants.improved_electric_carbon_factor / 2000.00
        return CarbonCalculationData(therms, kwh, therms + kwh)

    @cached_property
    def hp_fuel_weight(self) -> ImprovedData:
        heating_kwh = self.unadjusted.heating_kwh - self.unadjusted.electric_thermostat_savings
        if self.unadjusted.pv_kwh:
            heating_kwh = heating_kwh - self.unadjusted.pv_kwh

        hot_water_therms = self.unadjusted.hot_water_therms
        if self.unadjusted.solar_hot_water_therms > 0:
            hot_water_therms = 0

        hot_water_kwh = self.unadjusted.hot_water_kwh
        if self.unadjusted.solar_hot_water_kwh > 0:
            hot_water_kwh = 0
        elif self.unadjusted.pv_kwh > self.unadjusted.heating_kwh:
            hot_water_kwh -= self.unadjusted.pv_kwh - self.unadjusted.heating_kwh

        solar_hot_water_kwh = self.unadjusted.solar_hot_water_kwh
        if self.unadjusted.pv_kwh > self.unadjusted.heating_kwh:
            solar_hot_water_kwh -= self.unadjusted.pv_kwh - self.unadjusted.heating_kwh

        pv_kwh = (
            self.unadjusted.pv_kwh - self.unadjusted.heating_kwh - self.unadjusted.hot_water_kwh
        )
        if self.unadjusted.solar_hot_water_kwh > 0:
            pv_kwh = (
                self.unadjusted.pv_kwh
                - self.unadjusted.heating_kwh
                - self.unadjusted.solar_hot_water_kwh
            )

        return ImprovedData(
            self.unadjusted.heating_therms,
            None,
            max([0, heating_kwh]),
            heating_kwh * self.constants.electric_space_heat_fuel_weight,
            self.unadjusted.cooling_kwh - self.unadjusted.cooling_thermostat_savings,
            None,
            hot_water_therms,
            max([0, hot_water_kwh]),
            self.unadjusted.lights_and_appliance_therms,
            self.unadjusted.lights_and_appliance_kwh,
            self.unadjusted.fireplace_therms,
            self.unadjusted.solar_hot_water_therms,
            max([0, solar_hot_water_kwh]),
            max([0, pv_kwh]),
        )

    @cached_property
    def hp_fuel_weight_eps(self) -> EPSCalculationData:
        therms = sum(
            [
                self.hp_fuel_weight.heating_therms,
                self.hp_fuel_weight.hot_water_therms,
                self.hp_fuel_weight.lights_and_appliance_therms,
                self.hp_fuel_weight.fireplace_therms,
                self.hp_fuel_weight.solar_hot_water_therms,
            ]
        )
        kwh = sum(
            [
                self.hp_fuel_weight.heating_kwh * self.constants.electric_space_heat_fuel_weight,
                self.hp_fuel_weight.cooling_kwh,
                self.hp_fuel_weight.hot_water_kwh * self.constants.electric_hot_water_fuel_weight,
                self.hp_fuel_weight.lights_and_appliance_kwh,
                self.hp_fuel_weight.solar_hot_water_kwh
                * self.constants.electric_hot_water_fuel_weight,
                -self.hp_fuel_weight.pv_kwh,
            ]
        )
        mbtu = convert_kwh_to(kwh, EnergyUnit.MBTU) + convert_therm_to(therms, EnergyUnit.MBTU)
        return EPSCalculationData(therms, kwh, mbtu)

    @cached_property
    def hp_correction_consumption(self) -> ConsumptionCalculationData:
        therms = sum(
            [
                self.hp_fuel_weight.heating_therms,
                self.unadjusted.hot_water_therms,
                self.hp_fuel_weight.lights_and_appliance_therms,
                self.hp_fuel_weight.fireplace_therms,
            ]
        )
        kwh = sum(
            [
                self.unadjusted.heating_kwh - self.unadjusted.electric_thermostat_savings,
                self.unadjusted.cooling_kwh - self.unadjusted.cooling_thermostat_savings,
                self.unadjusted.hot_water_kwh,
                self.hp_fuel_weight.lights_and_appliance_kwh,
            ]
        )
        mbtu = convert_kwh_to(kwh, EnergyUnit.MBTU) + convert_therm_to(therms, EnergyUnit.MBTU)
        return ConsumptionCalculationData(therms, kwh, mbtu)

    @cached_property
    def eps_score(self) -> float:
        if self.heat_type == HeatType.GAS:
            return max([0, round(self.gas_fuel_weight_eps.total_mbtu, 0)])
        return max([0, round(self.hp_fuel_weight_eps.total_mbtu, 0)])

    @cached_property
    def carbon_score(self) -> float:
        if self.heat_type == HeatType.GAS:
            return max([0, self.unadjusted_carbon.carbon_score])
        return max([0, self.hp_correction_carbon.carbon_score])

    @cached_property
    def electric_carbon_score(self) -> float:
        if self.heat_type == HeatType.GAS:
            return max([0, self.unadjusted_carbon.total_kwh])
        return max([0, self.hp_correction_carbon.total_kwh])

    @cached_property
    def gas_carbon_score(self) -> float:
        if self.heat_type == HeatType.GAS:
            return self.unadjusted_carbon.total_therms
        return self.hp_correction_carbon.total_therms

    @cached_property
    def calculation_report(self) -> str:
        table = [
            [
                "Heating Therms",
                self.unadjusted.heating_therms,
                self.gas_fuel_weight.heating_therms,
                self.hp_correction.heating_therms,
                self.hp_fuel_weight.heating_therms,
            ],
            [
                "Gas Tstat Savings",
                self.unadjusted.gas_thermostat_savings,
            ],
            [
                "Heating kWh",
                self.unadjusted.heating_kwh,
                self.gas_fuel_weight.heating_kwh,
                self.hp_correction.heating_kwh,
                self.hp_fuel_weight.heating_kwh,
            ],
            [
                "Electric Tstat Savings",
                self.unadjusted.electric_thermostat_savings,
            ],
            [
                "Cooling kWh",
                self.unadjusted.cooling_kwh,
                self.gas_fuel_weight.cooling_kwh,
                self.hp_correction.cooling_kwh,
                self.hp_fuel_weight.cooling_kwh,
            ],
            [
                "Cooling Tstat Savings",
                self.unadjusted.cooling_thermostat_savings,
                self.gas_fuel_weight.cooling_thermostat_savings,
                self.hp_correction.cooling_thermostat_savings,
                self.hp_fuel_weight.cooling_thermostat_savings,
            ],
            [
                "Water Heating Therms",
                self.unadjusted.hot_water_therms,
                self.gas_fuel_weight.hot_water_therms,
                self.hp_correction.hot_water_therms,
                self.hp_fuel_weight.hot_water_therms,
            ],
            [
                "Water Heating kWh",
                self.unadjusted.hot_water_kwh,
                self.gas_fuel_weight.hot_water_kwh,
                self.hp_correction.hot_water_kwh,
                self.hp_fuel_weight.hot_water_kwh,
            ],
            [
                "Lights & Appliance Therms",
                self.unadjusted.lights_and_appliance_therms,
                self.gas_fuel_weight.lights_and_appliance_therms,
                self.hp_correction.lights_and_appliance_therms,
                self.hp_fuel_weight.lights_and_appliance_therms,
            ],
            [
                "Lights & Appliance kWH",
                self.unadjusted.lights_and_appliance_kwh,
                self.gas_fuel_weight.lights_and_appliance_kwh,
                self.hp_correction.lights_and_appliance_kwh,
                self.hp_fuel_weight.lights_and_appliance_kwh,
            ],
            [
                "Fireplace Therms",
                self.unadjusted.fireplace_therms,
                self.gas_fuel_weight.fireplace_therms,
                self.hp_correction.fireplace_therms,
                self.hp_fuel_weight.fireplace_therms,
            ],
            [
                "Solar HW Therms",
                self.unadjusted.solar_hot_water_therms,
                self.gas_fuel_weight.solar_hot_water_therms,
                self.hp_correction.solar_hot_water_therms,
                self.hp_fuel_weight.solar_hot_water_therms,
            ],
            [
                "Solar WH kWh",
                self.unadjusted.solar_hot_water_kwh,
                self.gas_fuel_weight.solar_hot_water_kwh,
                self.hp_correction.solar_hot_water_kwh,
                self.hp_fuel_weight.solar_hot_water_kwh,
            ],
            [
                "PV kWh",
                self.unadjusted.pv_kwh,
                self.gas_fuel_weight.pv_kwh,
                self.hp_correction.pv_kwh,
                self.hp_fuel_weight.pv_kwh,
            ],
            #
            [],  # EPS
            #
            [
                "Total Therms",
                None,
                self.gas_fuel_weight_eps.total_therms,
                None,
                self.hp_fuel_weight_eps.total_therms,
            ],
            [
                "Total kWh",
                None,
                self.gas_fuel_weight_eps.total_kwh,
                None,
                self.hp_fuel_weight_eps.total_kwh,
            ],
            [
                "Total MBtu",
                None,
                self.gas_fuel_weight_eps.total_mbtu,
                None,
                self.hp_fuel_weight_eps.total_mbtu,
            ],
            #
            [],  # Carbon
            #
            [
                "Total Therms",
                self.unadjusted_carbon.total_therms,
                None,
                self.hp_correction_carbon.total_therms,
            ],
            [
                "Total kWh",
                self.unadjusted_carbon.total_kwh,
                None,
                self.hp_correction_carbon.total_kwh,
            ],
            [
                "Total MBtu",
                self.unadjusted_carbon.carbon_score,
                None,
                self.hp_correction_carbon.carbon_score,
            ],
            #
            [],  # Total Consumption
            #
            [
                "Total Therms",
                self.unadjusted_consumption.total_therms,
                None,
                self.hp_correction_consumption.total_therms,
            ],
            [
                "Total kWh",
                self.unadjusted_consumption.total_kwh,
                None,
                self.hp_correction_consumption.total_kwh,
            ],
        ]
        return tabulate(
            table,
            headers=[
                "IMPROVED HOME CALCULATIONS",
                "Unadj Values",
                "Gas Fuel Weight",
                "HP Correction",
                "HP Fuel Weight",
            ],
            floatfmt=f".{round_value}f",
        )
