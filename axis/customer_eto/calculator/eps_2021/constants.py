"""constants.py - Axis"""

__author__ = "Steven K"
__date__ = "9/10/21 13:08"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
from functools import cached_property

from tabulate import tabulate

from axis.customer_eto.calculator.eps_2021.base import (
    round_value,
    HomePath,
    HomeSubType,
    LoadProfile,
    ElectricLoadProfile,
    GasLoadProfile,
)
from axis.customer_eto.enumerations import (
    ElectricUtility,
    PNWUSStates,
    ClimateLocation,
    QualifyingThermostat,
    HeatType,
)

log = logging.getLogger(__name__)

ELECTRIC_SPACE_HEAT_FUEL_WEIGHT = 3.29
ELECTRIC_HOT_WATER_FUEL_WEIGHT = 1.43
HEAT_PUMP_HEATING_CORRECTION_FACTOR = 1.0
HEAT_PUMP_COOLING_CORRECTION_FACTOR = 1.0
ELECTRIC_CARBON_FACTOR = 1.09
NATURAL_GAS_CARBON_FACTOR = 11.7
FIREPLACE_ADDITION_THERMS = 88.5
FIREPLACE_ADDITION_THERMS_GT70 = 70.2

CARBON_WEIGHTS = {
    ElectricUtility.PACIFIC_POWER: 1.09,
    ElectricUtility.PORTLAND_GENERAL: 1.09,
    ElectricUtility.NONE: 0.067,
}


class Constants:
    electric_space_heat_fuel_weight = ELECTRIC_SPACE_HEAT_FUEL_WEIGHT
    electric_hot_water_fuel_weight = ELECTRIC_HOT_WATER_FUEL_WEIGHT
    heat_pump_heating_correction_factor = HEAT_PUMP_HEATING_CORRECTION_FACTOR
    heat_pump_cooling_correction_factor = HEAT_PUMP_COOLING_CORRECTION_FACTOR
    electric_carbon_factor = ELECTRIC_CARBON_FACTOR
    natural_gas_carbon_factor = NATURAL_GAS_CARBON_FACTOR
    fireplace_addition_therms = FIREPLACE_ADDITION_THERMS
    carbon_weights = CARBON_WEIGHTS

    fireplace_addition_therms_gt70 = FIREPLACE_ADDITION_THERMS_GT70

    def __init__(
        self,
        electric_utility: ElectricUtility,
        us_state: PNWUSStates = PNWUSStates.OR,
        thermostat: QualifyingThermostat = QualifyingThermostat.NONE,
        heat_type: HeatType = None,
    ):
        self.electric_utility = electric_utility
        self.us_state = us_state
        self.thermostat = thermostat
        self.heat_type = heat_type

    @cached_property
    def code_constant_report(self):
        table = [
            ["Electric Space Heat Fuel Weight", self.electric_space_heat_fuel_weight],
            ["Electric DHW Fuel Weight", self.electric_hot_water_fuel_weight],
            ["HP Correction Factor-Heating", self.heat_pump_heating_correction_factor],
            ["HP Correction Factor-Cooling", self.heat_pump_cooling_correction_factor],
            ["Electric Carbon Factor (lbs/kWh)", self.electric_carbon_factor],
            ["Natural Gas Carbon Factor (lbs/therm)", self.natural_gas_carbon_factor],
            ["Fireplace addition for baseline (Therms)", self.fireplace_addition_therms],
        ]
        return tabulate(table, floatfmt=f".{round_value}f")

    @cached_property
    def improved_electric_carbon_factor(self):
        return self.carbon_weights[self.electric_utility]

    @cached_property
    def smart_thermostat_factor_1(self):
        """For Washington this is Gas Specific - Otherwise both"""
        if self.us_state == "WA":
            return 0.06
        if self.thermostat != QualifyingThermostat.NONE:
            if self.heat_type == HeatType.GAS:
                return 0.06
            elif self.heat_type == HeatType.ELECTRIC:
                return 0.12
        return 0.0

    @cached_property
    def smart_thermostat_factor_2(self):
        """For Washington this is Gas Specific - Otherwise both"""
        if self.us_state == "WA":
            return 0.12
        if self.thermostat != QualifyingThermostat.NONE:
            return 0.06
        return 0.0

    @cached_property
    def improved_constant_report(self):
        smart_thermostat_factor_1 = "Smart Thermostat savings %"
        smart_thermostat_factor_2 = "Smart Thermostat Cooling savings %"

        if self.us_state == "WA":
            smart_thermostat_factor_1 = "Gas Smart Tstat Savings Percent"
            smart_thermostat_factor_2 = "Electric Smart Tstats Savings Percent"

        table = [
            ["Electric Space Heat Fuel Weight", self.electric_space_heat_fuel_weight],
            ["Electric DHW Fuel Weight", self.electric_hot_water_fuel_weight],
            ["HP Correction Factor-Heating", self.heat_pump_heating_correction_factor],
            ["HP Correction Factor-Cooling", self.heat_pump_cooling_correction_factor],
            ["Electric Carbon Factor (lbs/kWh)", self.improved_electric_carbon_factor],
            ["Natural Gas Carbon Factor (lbs/therm)", self.natural_gas_carbon_factor],
            [smart_thermostat_factor_1, self.smart_thermostat_factor_1],
            [smart_thermostat_factor_2, self.smart_thermostat_factor_2],
            ["Fireplace addition EF < 69", self.fireplace_addition_therms],
            ["Fireplace addition EF >70", self.fireplace_addition_therms_gt70],
        ]
        return tabulate(table, floatfmt=f".{round_value}f")

    @cached_property
    def carbon_report(self):
        data = "Pounds of Carbon per therm/kWh per ODOE October 2018\n"
        data += tabulate(
            [
                ["Natural Gas", self.natural_gas_carbon_factor, "lbs/therm"],
                [
                    "Pacific Power",
                    self.carbon_weights.get(ElectricUtility.PACIFIC_POWER),
                    "lbs/kWh",
                ],
                [
                    "Portland General",
                    self.carbon_weights.get(ElectricUtility.PORTLAND_GENERAL),
                    "lbs/kWh",
                ],
                ["BPA", self.carbon_weights.get(ElectricUtility.NONE), "lbs/kWh"],
            ],
            floatfmt=f".{round_value}f",
        )
        return data

    def get_wa_load_profile_data(self):
        return {
            # Path 1
            (HomePath.PATH_1, HomeSubType.GHEW): LoadProfile(
                ElectricLoadProfile.RESIDENTIAL_LIGHTING,
                GasLoadProfile.RESIDENTIAL_HEATING,
                45.0,
                0.0,
                1.0,
            ),
            (HomePath.PATH_1, HomeSubType.GHGW): LoadProfile(
                ElectricLoadProfile.RESIDENTIAL_LIGHTING,
                GasLoadProfile.RESIDENTIAL_HEATING,
                44.0,
                0.0,
                1.0,
            ),
            (HomePath.PATH_1, HomeSubType.EHEW): LoadProfile(
                ElectricLoadProfile.RESIDENTIAL_LIGHTING,
                GasLoadProfile.RESIDENTIAL_HEATING,
                45.0,
                0.0,
                1.0,
            ),
            (HomePath.PATH_1, HomeSubType.EHGW): LoadProfile(
                ElectricLoadProfile.RESIDENTIAL_LIGHTING,
                GasLoadProfile.RESIDENTIAL_HEATING,
                44.0,
                0.0,
                1.0,
            ),
            # Path 2
            (HomePath.PATH_2, HomeSubType.GHEW): LoadProfile(
                ElectricLoadProfile.RESIDENTIAL_LIGHTING,
                GasLoadProfile.RESIDENTIAL_HEATING,
                38.0,
                0.0,
                1.0,
            ),
            (HomePath.PATH_2, HomeSubType.GHGW): LoadProfile(
                ElectricLoadProfile.RESIDENTIAL_LIGHTING,
                GasLoadProfile.RESIDENTIAL_HEATING,
                37.0,
                0.0,
                1.0,
            ),
            (HomePath.PATH_2, HomeSubType.EHEW): LoadProfile(
                ElectricLoadProfile.RESIDENTIAL_LIGHTING,
                GasLoadProfile.RESIDENTIAL_HEATING,
                38.0,
                0.0,
                1.0,
            ),
            (HomePath.PATH_2, HomeSubType.EHGW): LoadProfile(
                ElectricLoadProfile.RESIDENTIAL_LIGHTING,
                GasLoadProfile.RESIDENTIAL_HEATING,
                37.0,
                0.0,
                1.0,
            ),
            # Path 3
            (HomePath.PATH_3, HomeSubType.GHEW): LoadProfile(
                ElectricLoadProfile.RESIDENTIAL_LIGHTING,
                GasLoadProfile.RESIDENTIAL_HEATING,
                41.0,
                0.0,
                1.0,
            ),
            (HomePath.PATH_3, HomeSubType.GHGW): LoadProfile(
                ElectricLoadProfile.RESIDENTIAL_LIGHTING,
                GasLoadProfile.RESIDENTIAL_HEATING,
                39.0,
                0.0,
                1.0,
            ),
            (HomePath.PATH_3, HomeSubType.EHEW): LoadProfile(
                ElectricLoadProfile.RESIDENTIAL_LIGHTING,
                GasLoadProfile.RESIDENTIAL_HEATING,
                41.0,
                0.0,
                1.0,
            ),
            (HomePath.PATH_3, HomeSubType.EHGW): LoadProfile(
                ElectricLoadProfile.RESIDENTIAL_LIGHTING,
                GasLoadProfile.RESIDENTIAL_HEATING,
                39.0,
                0.0,
                1.0,
            ),
            # Path 4
            (HomePath.PATH_4, HomeSubType.GHEW): LoadProfile(
                ElectricLoadProfile.RESIDENTIAL_LIGHTING,
                GasLoadProfile.RESIDENTIAL_HEATING,
                41.0,
                0.0,
                1.0,
            ),
            (HomePath.PATH_4, HomeSubType.GHGW): LoadProfile(
                ElectricLoadProfile.RESIDENTIAL_LIGHTING,
                GasLoadProfile.RESIDENTIAL_HEATING,
                41.0,
                0.0,
                1.0,
            ),
            (HomePath.PATH_4, HomeSubType.EHEW): LoadProfile(
                ElectricLoadProfile.RESIDENTIAL_LIGHTING,
                GasLoadProfile.RESIDENTIAL_HEATING,
                41.0,
                0.0,
                1.0,
            ),
            (HomePath.PATH_4, HomeSubType.EHGW): LoadProfile(
                ElectricLoadProfile.RESIDENTIAL_LIGHTING,
                GasLoadProfile.RESIDENTIAL_HEATING,
                41.0,
                0.0,
                1.0,
            ),
        }

    def get_default_load_profile_data(self):
        return {
            # Path 1
            (HomePath.PATH_1, HomeSubType.EHEW): LoadProfile(
                ElectricLoadProfile.RESIDENTIAL_ASHP,
                GasLoadProfile.NONE,
                43.0,
                1.0,
                0.0,
            ),
            (HomePath.PATH_1, HomeSubType.EHGW): LoadProfile(
                ElectricLoadProfile.RESIDENTIAL_ASHP,
                GasLoadProfile.HOT_WATER,
                43.0,
                0.9744819195559840000,
                0.0255180804440162000,
            ),
            (HomePath.PATH_1, HomeSubType.GHEW): LoadProfile(
                ElectricLoadProfile.RESIDENTIAL_SPACE_CONDITIONING,
                GasLoadProfile.RESIDENTIAL_HEATING,
                35.0,
                0.3790606181956560000,
                0.6209393818043440000,
            ),
            (HomePath.PATH_1, HomeSubType.GHGW): LoadProfile(
                ElectricLoadProfile.RESIDENTIAL_SPACE_CONDITIONING,
                GasLoadProfile.RESIDENTIAL_HEATING,
                34.0,
                0.3453554216774470000,
                0.6546445783225530000,
            ),
            # Path 2
            (HomePath.PATH_2, HomeSubType.EHEW): LoadProfile(
                ElectricLoadProfile.RESIDENTIAL_ASHP,
                GasLoadProfile.NONE,
                38.0,
                1.0,
                0.0,
            ),
            (HomePath.PATH_2, HomeSubType.EHGW): LoadProfile(
                ElectricLoadProfile.RESIDENTIAL_ASHP,
                GasLoadProfile.HOT_WATER,
                41.0,
                0.868987663436506000,
                0.1310123365634940000,
            ),
            (HomePath.PATH_2, HomeSubType.GHEW): LoadProfile(
                ElectricLoadProfile.RESIDENTIAL_SPACE_CONDITIONING,
                GasLoadProfile.RESIDENTIAL_HEATING,
                29.0,
                0.7560419843980000000,
                0.2439580156020000000,
            ),
            (HomePath.PATH_2, HomeSubType.GHGW): LoadProfile(
                ElectricLoadProfile.RESIDENTIAL_SPACE_CONDITIONING,
                GasLoadProfile.RESIDENTIAL_HEATING,
                34.0,
                0.1883061089346960000,
                0.8116938910653040000,
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
                0.8458957826709290000,
                0.1541042173290710000,
            ),
            (HomePath.PATH_3, HomeSubType.GHEW): LoadProfile(
                ElectricLoadProfile.RESIDENTIAL_SPACE_CONDITIONING,
                GasLoadProfile.RESIDENTIAL_HEATING,
                33.0,
                0.7547094636691920000,
                0.2452905363308080000,
            ),
            (HomePath.PATH_3, HomeSubType.GHGW): LoadProfile(
                ElectricLoadProfile.RESIDENTIAL_SPACE_CONDITIONING,
                GasLoadProfile.RESIDENTIAL_HEATING,
                38.0,
                0.2263699182253570000,
                0.7736300817746430000,
            ),
            # Path 4
            (HomePath.PATH_4, HomeSubType.EHEW): LoadProfile(
                ElectricLoadProfile.RESIDENTIAL_ASHP,
                GasLoadProfile.NONE,
                37.0,
                1.0,
                0.0,
            ),
            (HomePath.PATH_4, HomeSubType.EHGW): LoadProfile(
                ElectricLoadProfile.RESIDENTIAL_ASHP,
                GasLoadProfile.HOT_WATER,
                40.0,
                0.8855852584722720000,
                0.1144147415277280000,
            ),
            (HomePath.PATH_4, HomeSubType.GHEW): LoadProfile(
                ElectricLoadProfile.RESIDENTIAL_SPACE_CONDITIONING,
                GasLoadProfile.RESIDENTIAL_HEATING,
                36.0,
                0.6532115667028290000,
                0.3467884332971710000,
            ),
            (HomePath.PATH_4, HomeSubType.GHGW): LoadProfile(
                ElectricLoadProfile.RESIDENTIAL_SPACE_CONDITIONING,
                GasLoadProfile.RESIDENTIAL_HEATING,
                40.0,
                0.1661286423177830000,
                0.8338713576822170000,
            ),
        }

    def get_load_profile(self, home_path, sub_type):
        """Gets a full load profile"""
        data = self.get_default_load_profile_data()
        if self.us_state == PNWUSStates.WA:
            data = self.get_wa_load_profile_data()
        try:
            return data[(home_path, sub_type)]
        except KeyError:
            return LoadProfile(ElectricLoadProfile.NONE, GasLoadProfile.NONE, 0.0, 0.0, 0.0)

    def get_partial_territory_load_profile(self, sub_type):
        """Provides the update for a load profile where the gas or electric utility is other/none"""
        data = {
            HomeSubType.GHEW: {"electric_allocation": 0.450000, "gas_allocation": 0.550000},
            HomeSubType.GHGW: {"electric_allocation": 0.080000, "gas_allocation": 0.920000},
            HomeSubType.EHEW: {"electric_allocation": 1.000000, "gas_allocation": 0.000000},
            HomeSubType.EHGW: {"electric_allocation": 0.830000, "gas_allocation": 0.170000},
        }
        return data[sub_type]

    def get_simplified_location(self, climate_location: ClimateLocation):
        data = {
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
        return data.get(climate_location)
