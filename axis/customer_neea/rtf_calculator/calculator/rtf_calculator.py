"""rtf_calculator.py: Django RTF Calculator"""


import logging
from collections import OrderedDict

from simulation.enumerations import FuelType

from .rtf_base import RTFBaseCalculator
from ..base import RTFBase
from ..data_models import (
    RTFRemModeledInput,
    RTFSimulatedInput,
    RTFSimModeledInput,
)
from ..incentives import BPAIncentivesCalculator

__author__ = "Steven K"
__date__ = "08/20/2019 07:50"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

log = logging.getLogger(__name__)


class RTFCalculator(RTFBaseCalculator, RTFBase):  # pylint: disable=too-many-public-methods
    """RTF implementation of the calculator"""

    def __init__(self, **kwargs):
        super(RTFCalculator, self).__init__(**kwargs)

        self.input_heat_pump_water_heater_tier = kwargs.get("heat_pump_water_heater_tier")
        self.heat_pump_water_heater_tier = self.normalize_input_heat_pump_water_heater_tier(
            self.input_heat_pump_water_heater_tier
        )

        self.input_estar_std_refrigerators_installed = kwargs.get(
            "estar_std_refrigerators_installed", 0
        )
        self.estar_std_refrigerators_installed = self.normalize_integer(
            self.input_estar_std_refrigerators_installed
        )

        self.input_estar_compact_refrigerators_installed = kwargs.get(
            "estar_compact_refrigerators_installed", 0
        )
        self.estar_compact_refrigerators_installed = self.normalize_integer(
            self.input_estar_compact_refrigerators_installed
        )

        self.input_clothes_dryer_type = kwargs.get("clothes_dryer_type")
        self.clothes_dryer_type = self.normalize_clothes_dryer_type(self.input_clothes_dryer_type)

        self.input_clothes_dryer_ucef = kwargs.get("clothes_dryer_ucef", 3.0)
        self.clothes_dryer_ucef = self.normalize_float(self.input_clothes_dryer_ucef, 3.0, 8.0)

        self.input_efficient_clothes_dryers_installed = kwargs.get(
            "efficient_clothes_dryers_installed", 0
        )
        self.efficient_clothes_dryers_installed = self.normalize_integer(
            self.input_efficient_clothes_dryers_installed
        )

    @property
    def program(self):
        return None

    def normalize_input_heat_pump_water_heater_tier(self, input_name):
        """Normalize out heat pump water heater tier"""

        if input_name is None:
            return self.append_issue("Missing Heat Pump Water Heater Tier")

        input_name = input_name.lower().replace(" ", "")

        lower_list = [x.lower() for x in self.constants.HEAT_PUMP_WATER_HEATER_TIERS]
        if input_name.lower() in lower_list:
            _idx = lower_list.index(input_name.lower())
            input_name = self.constants.HEAT_PUMP_WATER_HEATER_TIERS[_idx]

        if input_name not in self.constants.HEAT_PUMP_WATER_HEATER_TIERS:
            msg = "Invalid Heat Pump Water Heater Tier identified '%s' must be one of %s"
            return self.append_issue(
                msg, input_name, ", ".join(self.constants.HEAT_PUMP_WATER_HEATER_TIERS)
            )

        return input_name

    def normalize_clothes_dryer_type(self, input_name):
        """Normalize out clothes dryer type"""

        if input_name is None:
            return "ventless"

        lower_list = [x.lower() for x in self.constants.CLOTHES_DRYER_TYPES]
        if input_name.lower() in lower_list:
            input_name = self.constants.CLOTHES_DRYER_TYPES[lower_list.index(input_name.lower())]

        if input_name not in self.constants.CLOTHES_DRYER_TYPES:
            msg = "Invalid Clothes Dryer Type identified '%s' must be one of%s}"
            return self.append_issue(msg, input_name, ", ".join(self.constants.CLOTHES_DRYER_TYPES))

        return input_name

    def get_sim_modeled_input(self):
        """Simulation based input"""
        return RTFSimModeledInput

    def get_rem_modeled_input(self):
        """Modeled Input"""
        return RTFRemModeledInput

    def get_simulated_input(self):
        """Simulated Input"""
        return RTFSimulatedInput

    @property
    def improved_data_heating_kwh(self):
        """Improved heating kWh"""
        return self.improved_data.heating_kwh

    @property
    def improved_data_heating_therms(self):
        """Improved heating therms"""
        return self.improved_data.heating_therms

    @property
    def improved_data_cooling_kwh(self):
        """Improved cooling kWh"""
        return self.improved_data.cooling_kwh

    @property
    def code_data_heating_kwh(self):
        """Code heating kWh"""
        return self.code_data.heating_kwh

    @property
    def code_data_heating_therms(self):
        """Code heating therms"""
        return self.code_data.heating_therms

    @property
    def code_data_cooling_kwh(self):
        """Code cooling kWh"""
        return self.code_data.cooling_kwh

    @property
    def code_data_total_consumption_kwh(self):
        """Code total kWh consumption"""
        return self.code_data.total_consumption_kwh

    @property
    def code_data_total_consumption_therms(self):
        """Code total therms consumption"""
        return self.code_data.total_consumption_therms

    @property
    def code_data_total_consumption_mmbtu(self):
        """Code total mBtu consumption"""
        return self.therms_to_mbtu(self.code_data_total_consumption_therms) + self.kwh_to_mbtu(
            self.code_data_total_consumption_kwh
        )

    @property
    def improved_data_total_consumption_kwh(self):
        """Improved total kWh consumption"""
        return self.improved_data.total_consumption_kwh

    @property
    def improved_data_total_consumption_therms(self):
        """Improved total therm consumption"""
        return self.improved_data.total_consumption_therms

    @property
    def improved_data_total_consumption_mmbtu(self):
        """Improved total mBtu consumption"""
        return self.therms_to_mbtu(self.improved_data_total_consumption_therms) + self.kwh_to_mbtu(
            self.improved_data_total_consumption_kwh
        )

    @property
    def heating_kwh_savings(self):
        """Heating kWh savings"""
        return (
            self.code_data_heating_kwh - self.improved_data_heating_kwh
        ) * self.electricity_adjustment_factor

    @property
    def heating_therm_savings(self):
        """Heating therm savings"""
        return (
            self.code_data_heating_therms - self.improved_data_heating_therms
        ) * self.gas_adjustment_factor

    @property
    def cooling_kwh_savings(self):
        """Cooling kWh savings"""
        return (
            self.code_data_cooling_kwh - self.improved_data_cooling_kwh
        ) * self.electricity_adjustment_factor

    @property
    def cooling_therm_savings(self):
        """Cooling therm savings"""
        return 0.0

    def heating_cooling_report(self):
        """Report"""
        data = []
        data.append("\n--- Heating and Cooling Energy Savings Calculations: ----")
        msg = "{:<60} {:<10}{:5}{:^10}{:<10}{:<5}"
        data.append(msg.format("", "Electricity", "", "", "Gas", ""))
        data.append(
            msg.format(
                "Simulation Heating Energy Consumption Project",
                self.round4__improved_data_heating_kwh,
                "kWh",
                "",
                self.round4__improved_data_heating_therms,
                "Therms",
            )
        )
        data.append(
            msg.format(
                "Simulation Heating Energy Consumption Baseline (UDRH)",
                self.round4__code_data_heating_kwh,
                "kWh",
                "",
                self.round4__code_data_heating_therms,
                "Therms",
            )
        )
        data.append("")
        data.append(
            msg.format(
                "Simulation Cooling Energy Consumption Project",
                self.round4__improved_data_cooling_kwh,
                "kWh",
                "",
                "",
                "",
            )
        )
        data.append(
            msg.format(
                "Simulation Cooling Energy Consumption Baseline (UDRH)",
                self.round4__code_data_cooling_kwh,
                "kWh",
                "",
                "",
                "",
            )
        )
        data.append("")
        data.append(
            msg.format(
                "Adjustment Factor",
                self.electricity_adjustment_factor,
                "",
                "",
                self.gas_adjustment_factor,
                "",
            )
        )
        data.append("")

        data.append(
            msg.format(
                "Heating Energy Savings",
                self.round4__heating_kwh_savings,
                "kWh",
                "",
                self.round4__heating_therm_savings,
                "Therms",
            )
        )
        data.append(
            msg.format(
                "Cooling Energy Savings",
                self.round4__cooling_kwh_savings,
                "kWh",
                "",
                self.round4__cooling_therm_savings,
                "Therms",
            )
        )

        return "\n".join(data)

    @property
    def qty_heat_pump_water_heaters(self):
        """Qty of heat pump water heaters"""
        return self.improved_data.qty_heat_pump_water_heaters

    improved_data_qty_heat_pump_water_heaters = qty_heat_pump_water_heaters

    @property
    def baseline_hotwater_consumption(self):
        """Baseline hot water consumption"""
        data = dict(self.constants.HEAT_PUMP_WATER_HEATER_BASELINE_CONSUMPTION_RATES)
        return data.get(
            (self.us_state, self.heating_system_config, self.home_size, self.heating_zone), 0.0
        )

    @property
    def heat_pump_water_heater_kwh(self):
        """Heat pump hot water kWh consumption"""
        data = dict(self.constants.HEAT_PUMP_WATER_HEATER_KWH)
        return data.get((self.heat_pump_water_heater_tier, self.heating_zone), 0.0)

    @property
    def heat_pump_water_heater_kwh_savings(self):
        """Heat pump hot water kWh savings"""
        return self.baseline_hotwater_consumption - self.heat_pump_water_heater_kwh

    def hot_water_report(self):
        """Report"""
        data = []
        data.append("\n--- Water Heating Energy Savings Calculations ----")
        msg = "{:<60} {:<10}{:<5}"
        data.append(msg.format("# Heat Pump Water Heater", self.qty_heat_pump_water_heaters, ""))
        data.append(msg.format("Baseline Consumption", self.baseline_hotwater_consumption, "kWh"))
        data.append(msg.format("Heat Pump Water Heater Tier", self.heat_pump_water_heater_tier, ""))
        data.append(
            msg.format("Heat Pump Water Heater kWh", self.heat_pump_water_heater_kwh, "kWh")
        )
        data.append(
            msg.format(
                "Annual Non Interactive Energy Savings",
                self.heat_pump_water_heater_kwh_savings,
                "kWh",
            )
        )
        return "\n".join(data)

    @property
    def baseline_lighting_efficacy(self):
        """Baseline lighting efficacy"""
        data = dict(self.constants.BASELINE_PCT_LIGHTING_EFFICACY)
        return data.get((self.us_state, self.heating_system_config, self.home_size), 0)

    @property
    def total_lamps_over_baseline(self):
        """Total lamps over baseline"""
        total = (
            self.cfl_installed
            + self.led_installed
            - self.total_installed_lamps * self.baseline_lighting_efficacy
        )
        return max(0, total)

    @property
    def total_cfl_over_baseline(self):
        """Total CFL Lamps over baseline"""
        try:
            total = self.total_lamps_over_baseline * (
                self.cfl_installed / (float(self.cfl_installed + self.led_installed))
            )
        except ZeroDivisionError:
            total = 0.0
        return max(0, total)

    @property
    def total_led_over_baseline(self):
        """Total LED Lamps over baseline"""
        total = self.total_lamps_over_baseline - self.total_cfl_over_baseline
        return max(0, total)

    @property
    def weighted_average_hou(self):
        """Weighted average HOU"""
        return self.constants.WEIGHTED_AVERAGE_HOU

    @property
    def weighted_inefficient_wattage(self):
        """Weighted inefficient wattage"""
        return self.constants.WEIGHTED_AVERAGE_INEFFICIENT_WATTAGE

    @property
    def weighted_led_wattage(self):
        """Weighted LED wattage"""
        return self.constants.WEIGHTED_AVERAGE_LED_WATTAGE

    @property
    def weighted_cfl_wattage(self):
        """Weighted CFL wattage"""
        return self.constants.WEIGHTED_AVERAGE_CFL_WATTAGE

    @property
    def lighting_kwh_savings(self):
        """Lighting kWh savings"""
        total = (
            self.weighted_inefficient_wattage - self.weighted_cfl_wattage
        ) * self.total_cfl_over_baseline
        total += (
            self.weighted_inefficient_wattage - self.weighted_led_wattage
        ) * self.total_led_over_baseline
        total *= self.weighted_average_hou * 365
        total /= 1000.0
        return total

    @property
    def lighting_therm_savings(self):
        """Lighting therm savings"""
        return 0.0

    def lighting_report(self):
        """Report"""
        data = []
        data.append("\n--- Lighting Energy Savings Calculations: ----")
        msg = "{:<60} {:<10}{:<5}"
        data.append(msg.format("# CFL Installed", self.cfl_installed, ""))
        data.append(msg.format("# LED Installed", self.led_installed, ""))
        data.append(msg.format("# Total Installed Lamps", self.total_installed_lamps, ""))
        data.append(msg.format("Baseline High Efficacy Lamps", self.baseline_lighting_efficacy, ""))
        data.append(
            msg.format("Total Lamps over baseline", self.round1__total_lamps_over_baseline, "")
        )
        data.append(msg.format("Total CFL over baseline", self.round1__total_cfl_over_baseline, ""))
        data.append(
            msg.format("Total LED Lamps over baseline", self.round1__total_led_over_baseline, "")
        )
        data.append(msg.format("Weighted Average HOU", self.round2__weighted_average_hou, ""))
        data.append(
            msg.format(
                "Weighted Average Inefficient Wattage",
                self.round2__weighted_inefficient_wattage,
                "Watts",
            )
        )
        data.append(
            msg.format("Weighted Average CFL Wattage", self.round2__weighted_cfl_wattage, "Watts")
        )
        data.append(
            msg.format("Weighted Average LED Wattage", self.round2__weighted_led_wattage, "Watts")
        )
        data.append(
            msg.format(
                "Annual Non Interactive Energy Savings", self.round2__lighting_kwh_savings, "kWh"
            )
        )
        return "\n".join(data)

    @property
    def refrigerator_annual_savings(self):
        """Refrigerator annual savings"""
        total = (
            self.estar_std_refrigerators_installed
            * self.constants.STANDARD_REFRIGERATOR_ENERGY_SAVINGS_EUL
        )
        total += (
            self.estar_compact_refrigerators_installed
            * self.constants.COMPACT_REFRIGERATOR_ENERGY_SAVINGS_EUL
        )
        return total

    def get_annual_savings_data(self):  # pylint: disable=inconsistent-return-statements
        """Annual Savings Data"""
        data = dict(self.constants.CLOTHES_DRYER_ANNUAL_SAVINGS)
        for (lower, upper, vtype), value in data.items():
            if lower <= self.clothes_dryer_ucef < upper and vtype == self.clothes_dryer_type:
                return value

    @property
    def clothes_dryer_ucef_range(self):
        """Clothes dryer UCEF range"""
        return self.get_annual_savings_data()["label"]

    @property
    def clothes_dryer_annual_savings(self):
        """Clothes dryer annual savings"""
        return self.get_annual_savings_data()["annual_savings"]

    @property
    def appliance_kwh_savings(self):
        """Appliance kWh savings"""
        return self.clothes_dryer_annual_savings + self.refrigerator_annual_savings

    @property
    def appliance_therm_savings(self):
        """Appliance therm savings"""
        return 0.0

    def appliance_report(self):
        """Report"""
        data = []
        data.append("\n--- Appliance Energy Savings Calculations: ----")
        msg = "{:<60} {:<10}{:<5}"
        data.append(
            msg.format(
                "# standard size ENERGY STAR Refrigerators",
                self.estar_std_refrigerators_installed,
                "",
            )
        )
        data.append(
            msg.format(
                "# compact size ENERGY STAR Refrigerators",
                self.estar_compact_refrigerators_installed,
                "",
            )
        )
        data.append(msg.format("Annual Energy Savings", self.refrigerator_annual_savings, "kWh"))
        data.append(msg.format("", "", ""))
        data.append(msg.format("Clothes Dryer Type", self.clothes_dryer_type, ""))
        data.append(msg.format("UCEF Range", self.clothes_dryer_ucef_range, ""))
        data.append(
            msg.format("# Of of efficient dryers", self.efficient_clothes_dryers_installed, "")
        )
        data.append(msg.format("Annual Energy Savings", self.clothes_dryer_annual_savings, "kWh"))
        return "\n".join(data)

    @property
    def heating_type(self):
        """Primary heating type"""
        return self.improved_data.primary_heating_type

    improved_data_primary_heating_type = heating_type

    @property
    def cooling_type(self):
        """Primary cooling type"""
        return self.improved_data.primary_cooling_type

    improved_data_primary_cooling_type = cooling_type

    @property
    def cooling_fuel(self):
        """Primary cooling fuel"""
        return self.improved_data.primary_cooling_fuel

    improved_data_primary_cooling_fuel = cooling_fuel

    @property
    def is_primary_heating_is_heat_pump(self):
        """Is primary heating a heat pump"""
        return self.improved_data.is_primary_heating_is_heat_pump

    improved_data_is_primary_heating_is_heat_pump = is_primary_heating_is_heat_pump

    def get_smart_thermostat_savings(self):
        """Smart Thermostat therm savings"""
        data = dict(self.constants.SMART_TSTAT_SAVINGS)

        if not self.smart_thermostat_installed:
            return data[("all", "zonal", False)]

        try:
            return data[
                (
                    self.heating_fuel,
                    self.heating_system_config,
                    self.is_primary_heating_is_heat_pump,
                )
            ]
        except KeyError:
            return data[("all", "zonal", False)]

    @property
    def heating_savings_rate(self):
        """Heating savings rate"""
        return self.get_smart_thermostat_savings()["heating_pct"]

    @property
    def cooling_savings_rate(self):
        """Cooling savings rate"""
        return self.get_smart_thermostat_savings()["cooling_pct"]

    @property
    def smart_thermostat_heating_kwh_savings(self):
        """Smart Thermostat kWh heating savings"""
        return self.improved_data_heating_kwh * self.heating_savings_rate

    @property
    def smart_thermostat_cooling_kwh_savings(self):
        """Smart Thermostat kWh cooling savings"""
        return self.improved_data_cooling_kwh * self.cooling_savings_rate

    @property
    def smart_thermostat_heating_therm_savings(self):
        """Smart Thermostat therm heating savings"""
        return self.improved_data_heating_therms * self.heating_savings_rate

    @property
    def smart_thermostat_cooling_therm_savings(self):
        """Smart Thermostat therm cooling savings"""
        return 0 * self.cooling_savings_rate

    @property
    def smart_thermostat_kwh_savings(self):
        """Smart Thermostat kWh savings"""
        return self.smart_thermostat_heating_kwh_savings + self.smart_thermostat_cooling_kwh_savings

    @property
    def smart_thermostat_therm_savings(self):
        """Smart Thermostat therm savings"""
        return (
            self.smart_thermostat_heating_therm_savings
            + self.smart_thermostat_cooling_therm_savings
        )

    def thermostat_report(self):
        """Report"""
        data = []
        data.append("\n--- Appliance Energy Savings Calculations: ----")
        msg = "{:<60} {:<10}{:<5}"
        data.append(
            msg.format("Smart Tstat Installed?", "{}".format(self.smart_thermostat_installed), "")
        )
        data.append(
            msg.format(
                "Is the primary heating system a HP?",
                "{}".format(self.is_primary_heating_is_heat_pump),
                "({})".format(self.heating_type),
            )
        )
        data.append("")
        msg = "{:<60} {:<10}{:<10}{:<10}{:<6}"
        data.append(msg.format("", "Heating", "Cooling", "Total", ""))
        data.append(
            msg.format(
                "Approved Savings Rate",
                self.round1p__heating_savings_rate,
                self.round1p__cooling_savings_rate,
                "",
                "",
            )
        )
        data.append(
            msg.format(
                "Savings resulting from Smart Tstat",
                self.round2__smart_thermostat_heating_kwh_savings,
                self.round2__smart_thermostat_cooling_kwh_savings,
                self.round2__smart_thermostat_kwh_savings,
                "kWh",
            )
        )
        data.append(
            msg.format(
                "Savings resulting from Smart Tstat",
                self.round2__smart_thermostat_heating_therm_savings,
                self.round2__smart_thermostat_cooling_therm_savings,
                self.round2__smart_thermostat_therm_savings,
                "Therms",
            )
        )
        return "\n".join(data)

    @property
    def water_heater_type(self):
        """Water heater type"""
        return self.improved_data.primary_water_heating_type.lower()

    @property
    def water_heater_fuel(self):
        """Water heater type"""
        try:
            return self.improved_data.primary_water_heating_fuel
        except AttributeError:
            # Simulated data.
            return FuelType.NATURAL_GAS if self.water_heater_type == "gas" else FuelType.ELECTRIC

    improved_data_primary_water_heating_type = water_heater_type

    @property
    def water_heating_savings_unit(self):
        """Water heater savings unit"""
        return "Therms" if self.water_heater_type == "gas" else "kWh"

    @property
    def project_energy_consumption_showerhead(self):
        """Energy consumption showerhead"""
        if not self.water_heater_type:
            return 0
        key = "{}_consumption".format(self.water_heating_savings_unit.lower())
        data = dict(self.constants.LOWFLOW_CONSUMPTION)
        total = data[(self.water_heater_type, 1.5)][key] * self.qty_shower_head_1p5
        total += data[(self.water_heater_type, 1.75)][key] * self.qty_shower_head_1p75
        return total

    @property
    def baseline_energy_consumption_showerhead(self):
        """Baseline consumption showerhead"""
        key = (
            self.us_state,
            self.heating_fuel,
            self.heating_system_config,
            self.home_size,
            self.water_heater_type,
        )
        data = dict(self.constants.LOWFLOW_UEC)
        return data.get(key, {}).get("consumption", 0) * (
            self.qty_shower_head_1p5 + self.qty_shower_head_1p75
        )

    @property
    def baseline_energy_consumption_showerhead_unit(self):
        """Baseline consumption showerhead unit"""
        key = (
            self.us_state,
            self.heating_fuel,
            self.heating_system_config,
            self.home_size,
            self.water_heater_type,
        )
        data = dict(self.constants.LOWFLOW_UEC)
        return data.get(key, {}).get("units", "")

    @property
    def showerhead_kwh_savings(self):
        """Showerhead kWh savings"""
        if self.water_heater_type == "gas":
            return 0.0
        return (
            self.baseline_energy_consumption_showerhead - self.project_energy_consumption_showerhead
        )

    @property
    def showerhead_therm_savings(self):
        """Showerhead therm savings"""
        if self.water_heater_type != "gas":
            return 0.0
        return (
            self.baseline_energy_consumption_showerhead - self.project_energy_consumption_showerhead
        )

    def shower_head_report(self):
        """Report"""
        data = []
        data.append("\n--- Low Flow Showerhead Savings ----")
        msg = "{:<60} {:<10}{:<5}"
        data.append(msg.format("# Low Flow Showerhead 1.5 gpm?", self.qty_shower_head_1p5, ""))
        data.append(msg.format("# Low Flow Showerhead 1.75 gpm?", self.qty_shower_head_1p75, ""))
        data.append(msg.format("Water Heater Type", self.water_heater_type, ""))
        data.append("")

        lookup = "{}, {}, {}, {}, {}".format(
            self.us_state,
            self.heating_fuel,
            self.heating_system_config,
            self.home_size,
            self.water_heater_type,
        )

        data.append("{:<60} {}".format("Low Flow Lookup", lookup))
        data.append("")

        data.append(
            msg.format(
                "Project Energy Consumption",
                self.round1__project_energy_consumption_showerhead,
                self.water_heating_savings_unit,
            )
        )
        data.append(
            msg.format(
                "Baseline Energy Consumption",
                self.round1__baseline_energy_consumption_showerhead,
                self.baseline_energy_consumption_showerhead_unit,
            )
        )

        total = self.round2__showerhead_kwh_savings
        if self.water_heater_type == "gas":
            total = self.round2__showerhead_therm_savings
        data.append(
            msg.format("Annual Energy Savings", total, self.round2__water_heating_savings_unit)
        )
        return "\n".join(data)

    @property
    def water_heater_kwh_savings(self):
        """Water heater kWh savings"""
        return self.heat_pump_water_heater_kwh_savings

    @property
    def water_heater_therm_savings(self):
        """Water heater therm savings"""
        return 0.0

    @property
    def total_kwh_savings(self):
        """Total kWh savings"""
        return (
            self.heating_kwh_savings
            + self.cooling_kwh_savings
            + self.smart_thermostat_heating_kwh_savings
            + self.smart_thermostat_cooling_kwh_savings
            + self.heat_pump_water_heater_kwh_savings
            + self.showerhead_kwh_savings
            + self.lighting_kwh_savings
            + self.appliance_kwh_savings
        )

    @property
    def total_therm_savings(self):
        """Total therm savings"""
        return (
            self.heating_therm_savings
            + self.cooling_therm_savings
            + self.smart_thermostat_heating_therm_savings
            + self.smart_thermostat_cooling_therm_savings
            + self.showerhead_therm_savings
        )

    @property
    def total_mmbtu_savings(self):
        """Total mBtu savings"""
        return self.total_therm_savings / 10.0 + (self.total_kwh_savings * 3.412) / 1000.0

    @property
    def improved_total_consumption_mmbtu_with_savings(self):
        """Improved total consumption mBtu savings"""
        return max([0, self.code_data_total_consumption_mmbtu - self.total_mmbtu_savings])

    @property
    def revised_percent_improvement(self):
        """Revised % improvement"""
        try:
            return max([0, (self.total_mmbtu_savings / self.code_data_total_consumption_mmbtu)])
        except ZeroDivisionError:
            return 0

    def total_report(self):
        """Report"""
        data = []
        data.append("\n--- Savings Summary ----")
        msg = "{:<60} {:<10}{:<10}"
        data.append(msg.format("", "kWh", "Therms"))
        data.append(
            msg.format(
                "Heating", self.round2__heating_kwh_savings, self.round2__heating_therm_savings
            )
        )
        data.append(
            msg.format(
                "Cooling", self.round2__cooling_kwh_savings, self.round2__cooling_therm_savings
            )
        )
        data.append(
            msg.format(
                "Smart Thermostat",
                self.round2__smart_thermostat_kwh_savings,
                self.round2__smart_thermostat_therm_savings,
            )
        )
        data.append(
            msg.format(
                "Heat Pump Water Heater", self.round2__heat_pump_water_heater_kwh_savings, "-"
            )
        )
        data.append(
            msg.format(
                "Low Flow Shower Head",
                self.round2__showerhead_kwh_savings,
                self.round2__showerhead_therm_savings,
            )
        )
        data.append(msg.format("Lighting", self.round2__lighting_kwh_savings, "-"))
        data.append(msg.format("Appliances", self.round2__appliance_kwh_savings, "-"))
        data.append(msg.format("-------------", "-" * 8, "-" * 8))
        data.append(
            msg.format("  Total", self.round2__total_kwh_savings, self.round2__total_therm_savings)
        )
        final = "    Total {:<10} MMBtu".format(self.round2__total_mmbtu_savings)
        data.append(final)
        return "\n".join(data)

    def result_data(self):
        """Result data"""
        data = OrderedDict()
        data["heating_kwh_savings"] = self.heating_kwh_savings
        data["heating_therm_savings"] = self.heating_therm_savings
        data["cooling_kwh_savings"] = self.cooling_kwh_savings
        data["cooling_therm_savings"] = self.cooling_therm_savings
        data["smart_thermostat_kwh_savings"] = self.smart_thermostat_kwh_savings
        data["smart_thermostat_therm_savings"] = self.smart_thermostat_therm_savings
        data["heat_pump_water_heater_kwh_savings"] = self.heat_pump_water_heater_kwh_savings
        data["showerhead_kwh_savings"] = self.showerhead_kwh_savings
        data["showerhead_therm_savings"] = self.showerhead_therm_savings
        data["lighting_kwh_savings"] = self.lighting_kwh_savings
        data["appliance_kwh_savings"] = self.appliance_kwh_savings
        data["total_kwh_savings"] = self.total_kwh_savings
        data["total_therm_savings"] = self.total_therm_savings
        data["total_mmbtu_savings"] = self.total_mmbtu_savings
        data["revised_percent_improvement"] = self.revised_percent_improvement
        data["code_total_consumption_mmbtu"] = self.code_data_total_consumption_mmbtu
        data["improved_total_consumption_mmbtu"] = self.improved_data_total_consumption_mmbtu
        _val = self.improved_total_consumption_mmbtu_with_savings
        data["improved_total_consumption_mmbtu_with_savings"] = _val
        data.update(self.incentives.data())
        return data

    @property
    def utility_requirements(self):
        """Utility requirements"""
        pass

    @property
    def incentive_kwargs(self):
        """Stuff to feed into the incentives"""

        return dict(
            program=self.program,
            us_state=self.us_state,
            constants=self.constants,
            heating_kwh_savings=self.heating_kwh_savings,
            heating_therm_savings=self.heating_therm_savings,
            cooling_kwh_savings=self.cooling_kwh_savings,
            cooling_therm_savings=self.cooling_therm_savings,
            water_heater_kwh_savings=self.water_heater_kwh_savings,
            water_heater_therm_savings=self.water_heater_therm_savings,
            smart_thermostat_kwh_savings=self.smart_thermostat_kwh_savings,
            smart_thermostat_therm_savings=self.smart_thermostat_therm_savings,
            showerhead_kwh_savings=self.showerhead_kwh_savings,
            showerhead_therm_savings=self.showerhead_therm_savings,
            lighting_kwh_savings=self.lighting_kwh_savings,
            lighting_therm_savings=self.lighting_therm_savings,
            appliance_kwh_savings=self.appliance_kwh_savings,
            appliance_therm_savings=self.appliance_therm_savings,
            default_percent_improvement=self.default_percent_improvement,
            revised_percent_improvement=self.revised_percent_improvement,
            reference_home_kwh=self.code_data_total_consumption_kwh,
            total_kwh_savings=self.total_kwh_savings,
            total_therm_savings=self.total_therm_savings,
            heating_fuel=self.heating_fuel,
            heating_type=self.heating_type,
            cooling_fuel=self.cooling_fuel,
            cooling_type=self.cooling_type,
            water_heater_type=self.water_heater_type,
            water_heater_tier=self.water_heater_tier,
            electric_meter_number=self.electric_meter_number,
            electric_utility=self.electric_utility,
            gas_utility=self.gas_utility,
            earth_advantage_certified=self.earth_advantage_certified,
        )

    @property
    def incentives(self):
        """Incentives requirements"""

        if self._incentives is not None:
            return self._incentives

        incentive_kwargs = self.incentive_kwargs
        self._incentives = BPAIncentivesCalculator(**incentive_kwargs)
        return self._incentives

    @property
    def use_revised_pct_improvement(self):
        """Use revised pct improvement"""
        return self.incentives.use_revised_pct_improvement
