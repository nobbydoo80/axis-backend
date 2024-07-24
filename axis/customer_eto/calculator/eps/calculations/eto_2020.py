"""eto_2020.py: ETO 2020 Calculator"""


import logging

__author__ = "Steven K"
__date__ = "12/15/2019 20:09"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

from .eto_2019 import Calculations2019

log = logging.getLogger(__name__)


class Calculations2020(Calculations2019):
    """Core calculations for 2020 program"""

    def __init__(self, simulation, **kwargs):
        super(Calculations2020, self).__init__(simulation, **kwargs)
        self.has_gas_fireplace = kwargs.get("has_gas_fireplace", False)

        self.savings_pct = self.constants.EPS_WA_SAVINGS_PCT
        if self.us_state == "OR":
            self.savings_pct = self.constants.EPS_OR_SAVINGS_PCT

    @property
    def electric_smart_tstat_heating_savings_pct(self):
        return self.savings_pct["electric_smart_tstat_heating_savings_pct"]

    @property
    def electric_smart_tstat_cooling_savings_pct(self):
        return self.savings_pct["electric_smart_tstat_cooling_savings_pct"]

    @property
    def gas_smart_tstat_heating_savings_pct(self):
        return self.savings_pct["gas_smart_tstat_heating_savings_pct"]

    @property
    def smart_tstat_heating_savings_pct(self):
        if not self.is_improved:
            return 0.0
        gas_smart_tstat = self.smart_thermostat and self.smart_thermostat_furnace_type == "GAS"
        if gas_smart_tstat:
            return self.gas_smart_tstat_heating_savings_pct
        ele_smart_tstat = self.smart_thermostat and self.smart_thermostat_furnace_type == "ASHP"
        if ele_smart_tstat:
            return self.electric_smart_tstat_heating_savings_pct
        return 0.0

    @property
    def gas_thermostat_savings_unadjusted(self):
        """Gas thermostat savings unaadjusted"""
        if not self.is_improved:
            return 0.0
        if self.heating_therms_unadjusted > 0 and self.smart_thermostat:
            return self.heating_therms_unadjusted * self.smart_tstat_heating_savings_pct
        return 0.0

    @property
    def electric_thermostat_savings_unadjusted(self):
        """Electric thermostat savings unadjusted"""
        if not self.is_improved:
            return 0.0
        if self.us_state == "WA":
            return 0.0
        if self.heating_kwh_unadjusted > 0 and self.smart_thermostat:
            return self.heating_kwh_unadjusted * self.smart_tstat_heating_savings_pct
        return 0.0

    @property
    def heating_therms_gas_heat_fuel_weight(self):
        return self.heating_therms_unadjusted - self.gas_thermostat_savings_unadjusted

    @property
    def heating_kwh_gas_heat_fuel_weight(self):
        return self.heating_kwh_unadjusted - self.electric_thermostat_savings_unadjusted

    @property
    def heating_kwh_heat_pump_fuel_weight(self):
        if not self.is_improved:
            return super(Calculations2020, self).heating_kwh_heat_pump_fuel_weight
        value = self.heating_kwh_unadjusted
        value -= self.electric_thermostat_savings_unadjusted
        if self.pv_kwh_unadjusted > 0:
            value -= self.pv_kwh_unadjusted
        return max([0, value])

    @property
    def electric_thermostat_savings_heat_pump_fuel_weight(self):
        return self.heating_kwh_heat_pump_fuel_weight * self.electric_space_heat_fuel_weight

    @property
    def smart_tstat_cooling_savings_pct(self):
        if not self.is_improved:
            return 0.0
        if self.us_state == "WA":
            return 0.0
        if self.smart_thermostat:
            return self.electric_smart_tstat_cooling_savings_pct
        return 0.0

    @property
    def cooling_thermostat_savings_unadjusted(self):
        if not self.is_improved:
            return 0.0
        return self.cooling_kwh_unadjusted * self.smart_tstat_cooling_savings_pct

    @property
    def cooling_kwh_gas_heat_fuel_weight(self):
        if not self.is_improved:
            return self.cooling_kwh_unadjusted
        value = self.cooling_kwh_unadjusted
        value -= self.cooling_thermostat_savings_unadjusted
        return value

    @property
    def cooling_kwh_heat_pump_fuel_weight(self):
        if not self.is_improved:
            return self.cooling_kwh_heat_pump_correction
        value = self.cooling_kwh_unadjusted
        value -= self.cooling_thermostat_savings_unadjusted
        return value

    @property
    def fireplace_constant(self):
        if not self.has_gas_fireplace:
            return self.constants.FIREPLACE_ADJUSTMENTS.get("No fireplace")
        if not self.is_improved:
            return self.constants.FIREPLACE_ADJUSTMENTS.get("baseline")
        return self.constants.FIREPLACE_ADJUSTMENTS.get(self.has_gas_fireplace)

    @property
    def fireplace_therms_unadjusted(self):
        """Fireplace unadjusted amount"""
        return self.fireplace_constant

    @property
    def fireplace_therms_gas_heat_fuel_weight(self):
        """Fireplace gas heat fuel weight"""
        return self.fireplace_constant

    @property
    def fireplace_therms_heat_pump_correction(self):
        """Fireplace heat pump correction"""
        return self.fireplace_constant

    @property
    def fireplace_therms_heat_pump_fuel_weight(self):
        """Fireplace heat pump fuel weight"""
        return self.fireplace_constant

    @property
    def eps_gas_heat_total_therms(self):
        """EPS Gas heat total therms"""
        value = self.heating_therms_gas_heat_fuel_weight
        value += self.hot_water_therms_gas_heat_fuel_weight
        value += self.lights_and_appliances_therms_gas_heat_fuel_weight
        if self.is_improved:
            value += self.solar_hot_water_therms_gas_heat_fuel_weight
        value += self.fireplace_therms_gas_heat_fuel_weight
        return value

    @property
    def eps_heat_pump_total_therms(self):
        """EPS heat pump therms"""
        value = self.heating_therms_heat_pump_fuel_weight
        value += self.hot_water_therms_heat_pump_fuel_weight
        value += self.lights_and_appliances_therms_heat_pump_fuel_weight
        value += self.fireplace_therms_gas_heat_fuel_weight
        if self.is_improved:
            value += self.solar_hot_water_therms_heat_pump_fuel_weight
        return value

    @property
    def eps_heat_pump_total_kwh(self):
        """EPS heat pump total kWh"""
        if not self.is_improved:
            return super(Calculations2020, self).eps_heat_pump_total_kwh
        value = self.electric_thermostat_savings_heat_pump_fuel_weight
        value += self.cooling_kwh_heat_pump_fuel_weight
        value += self.hot_water_kwh_heat_pump_fuel_weight
        value += self.lights_and_appliances_kwh_heat_pump_fuel_weight
        value += self.solar_hot_water_kwh_heat_pump_fuel_weight
        value -= self.pv_kwh_heat_pump_fuel_weight
        return value

    @property
    def carbon_gas_heat_total_therms(self):
        """Add in the fireplace"""
        value = self.heating_therms_unadjusted
        value += self.hot_water_therms_unadjusted
        value += self.lights_and_appliances_therms_unadjusted
        value += self.fireplace_therms_unadjusted
        if self.is_improved:
            value = self.heating_therms_gas_heat_fuel_weight
            if self.solar_hot_water_therms_unadjusted > 0:
                value += self.solar_hot_water_therms_gas_heat_fuel_weight
            else:
                value += self.hot_water_therms_gas_heat_fuel_weight
            value += self.lights_and_appliances_therms_gas_heat_fuel_weight
            value += self.fireplace_therms_gas_heat_fuel_weight

        value *= self.gas_carbon_factor
        value /= 2000.0
        return value

    @property
    def carbon_heat_pump_total_therms(self):
        """Carbon heat pump total therms"""
        value = self.heating_therms_heat_pump_correction
        value += self.hot_water_therms_heat_pump_correction
        value += self.lights_and_appliances_therms_heat_pump_correction
        value += self.fireplace_therms_heat_pump_correction
        if self.us_state == "WA":  # TODO SUSPECTED BUG!
            if self.is_improved:
                value -= self.fireplace_therms_heat_pump_correction
        value *= self.gas_carbon_factor
        value /= 2000.00
        if self.is_improved and self.simulation.solar_hot_water_therms > 0:
            value = self.heating_therms_heat_pump_correction
            value += self.solar_hot_water_therms_heat_pump_correction
            value += self.lights_and_appliances_therms_heat_pump_correction
            if self.us_state != "WA":  # TODO SUSPECTED BUG
                value += self.fireplace_therms_heat_pump_correction
            value *= self.gas_carbon_factor
            value /= 2000.00
        return value

    @property
    def consumption_gas_heat_total_therms(self):
        """Gas heat total therms consumption"""
        value = self.heating_therms_gas_heat_fuel_weight + self.hot_water_therms_unadjusted
        value += self.lights_and_appliances_therms_gas_heat_fuel_weight
        value += self.fireplace_therms_gas_heat_fuel_weight
        return value

    @property
    def consumption_heat_pump_total_therms(self):
        """Heat pump total therms consumption"""
        value = self.heating_therms_heat_pump_correction
        value += self.hot_water_therms_heat_pump_correction
        value += self.lights_and_appliances_therms_heat_pump_correction
        value += self.fireplace_therms_heat_pump_correction
        return value

    @property
    def consumption_heat_pump_total_kwh(self):
        """Consumption Heat Pump kWh"""
        if not self.is_improved:
            return super(Calculations2020, self).consumption_heat_pump_total_kwh
        value = self.heating_kwh_unadjusted
        value -= self.electric_thermostat_savings_unadjusted
        value += self.cooling_kwh_unadjusted
        value -= self.cooling_thermostat_savings_unadjusted
        value += self.hot_water_kwh_unadjusted
        value += self.lights_and_appliances_kwh_heat_pump_fuel_weight
        return value

    @property
    def hot_water_therms_gas_heat_fuel_weight(self):
        return self.hot_water_therms_unadjusted

    @property
    def hot_water_therms_heat_pump_fuel_weight(self):
        return self.hot_water_therms_heat_pump_correction

    def report(self):
        """Report"""
        data = []
        data.append(
            "\n--- {} Home Calculations ----".format("Improved" if self.is_improved else "Code")
        )
        data.append("Consumption Adjustments")
        msg = "{:>38}: {}"
        data.append(
            msg.format("Electric Space Heat Fuel Weight", self.electric_space_heat_fuel_weight)
        )
        data.append(msg.format("Electric DHW Fuel Weight", self.electric_hot_water_fuel_weight))
        data.append(
            msg.format("HP Correction Factor-Heating", self.heat_pump_heating_correction_factor)
        )
        data.append(
            msg.format("HP Correction Factor-Cooling", self.heat_pump_cooling_correction_factor)
        )
        data.append(msg.format("Electric Carbon Factor (lbs/kWh)", self.electric_carbon_factor))
        data.append(msg.format("Natural Gas Carbon Factor (lbs/therm)", self.gas_carbon_factor))
        if self.is_improved:
            data.append(
                msg.format(
                    "Smart Thermostat heating savings %", self.smart_tstat_heating_savings_pct
                )
            )
            data.append(
                msg.format(
                    "Smart Thermostat cooling savings %", self.smart_tstat_cooling_savings_pct
                )
            )
            data.append(
                msg.format(
                    "Fireplace Addition for EF <70",
                    self.constants.FIREPLACE_ADJUSTMENTS.get("60-69FE"),
                )
            )
            data.append(
                msg.format(
                    "Fireplace Addition for EF >=70",
                    self.constants.FIREPLACE_ADJUSTMENTS.get(">=70FE"),
                )
            )
        else:
            data.append(msg.format("Fireplace addition for baseline", self.fireplace_constant))

        msg = "{:35}{:>30}{:>30}{:>30}{:>30}"
        data.append(msg.format("", "", "" "Gas Heated Home", "Heat", "Pump"))
        data.append(msg.format("", "Unadjusted", "Fuel Weight DHW", "HP Correction", "Fuel Weight"))

        data.append(
            msg.format(
                "Heating Therms",
                self.round4__heating_therms_unadjusted,
                self.round4__heating_therms_gas_heat_fuel_weight,
                self.round4__heating_therms_heat_pump_correction,
                self.round4__heating_therms_heat_pump_fuel_weight,
            )
        )
        if self.is_improved:
            data.append(
                msg.format(
                    "Gas Tstat Savings", self.round4__gas_thermostat_savings_unadjusted, "", "", ""
                )
            )
        data.append(
            msg.format(
                "Heating kWh",
                self.round4__heating_kwh_unadjusted,
                self.round4__heating_kwh_gas_heat_fuel_weight,
                "" if self.is_improved else self.round4__heating_kwh_heat_pump_correction,
                self.round4__heating_kwh_heat_pump_fuel_weight,
            )
        )
        if self.is_improved:
            data.append(
                msg.format(
                    "Electric Tstat Savings",
                    self.round4__electric_thermostat_savings_unadjusted,
                    "",
                    "",
                    self.round4__electric_thermostat_savings_heat_pump_fuel_weight,
                )
            )
        data.append(
            msg.format(
                "Cooling kWh",
                self.round4__cooling_kwh_unadjusted,
                self.round4__cooling_kwh_gas_heat_fuel_weight,
                "" if self.is_improved else self.round4__cooling_kwh_heat_pump_correction,
                self.round4__cooling_kwh_heat_pump_fuel_weight,
            )
        )
        if self.is_improved:
            data.append(
                msg.format(
                    "Cooling Tstat Savings",
                    self.round4__cooling_thermostat_savings_unadjusted,
                    "",
                    "",
                    "",
                )
            )

        data.append(
            msg.format(
                "Water Heating Therms",
                self.round4__hot_water_therms_unadjusted,
                self.round4__hot_water_therms_gas_heat_fuel_weight,
                self.round4__hot_water_therms_heat_pump_correction,
                self.round4__hot_water_therms_heat_pump_fuel_weight,
            )
        )
        data.append(
            msg.format(
                "Water Heating kWH",
                self.round4__hot_water_kwh_unadjusted,
                self.round4__hot_water_kwh_gas_heat_fuel_weight,
                self.round4__hot_water_kwh_heat_pump_correction,
                self.round4__hot_water_kwh_heat_pump_fuel_weight,
            )
        )
        data.append(
            msg.format(
                "Lights & Appliances Therms",
                self.round4__lights_and_appliances_therms_unadjusted,
                self.round4__lights_and_appliances_therms_gas_heat_fuel_weight,
                self.round4__lights_and_appliances_therms_heat_pump_correction,
                self.round4__lights_and_appliances_therms_heat_pump_fuel_weight,
            )
        )
        data.append(
            msg.format(
                "Lights & Appliances kWH",
                self.round4__lights_and_appliances_kwh_unadjusted,
                self.round4__lights_and_appliances_kwh_gas_heat_fuel_weight,
                self.round4__lights_and_appliances_kwh_heat_pump_correction,
                self.round4__lights_and_appliances_kwh_heat_pump_fuel_weight,
            )
        )
        data.append(
            msg.format(
                "Fireplace therms",
                self.round4__fireplace_therms_unadjusted,
                self.round4__fireplace_therms_gas_heat_fuel_weight,
                self.round4__fireplace_therms_heat_pump_correction,
                self.round4__fireplace_therms_heat_pump_fuel_weight,
            )
        )
        data.append(
            msg.format(
                "Solar Water Heating Therms",
                self.round4__solar_hot_water_therms_unadjusted,
                self.round4__solar_hot_water_therms_gas_heat_fuel_weight,
                self.round4__solar_hot_water_therms_heat_pump_correction,
                self.round4__solar_hot_water_therms_heat_pump_fuel_weight,
            )
        )
        data.append(
            msg.format(
                "Solar Water Heating kWH",
                self.round4__solar_hot_water_kwh_unadjusted,
                self.round4__solar_hot_water_kwh_gas_heat_fuel_weight,
                self.round4__solar_hot_water_kwh_heat_pump_correction,
                self.round4__solar_hot_water_kwh_heat_pump_fuel_weight,
            )
        )
        data.append(
            msg.format(
                "PV kWH",
                self.round4__pv_kwh_unadjusted,
                self.round4__pv_kwh_gas_heat_fuel_weight,
                self.round4__pv_kwh_heat_pump_correction,
                self.round4__pv_kwh_heat_pump_fuel_weight,
            )
        )

        data.append(msg.format(*["--"] * 5))

        data.append(
            msg.format(
                "EPS Total Therms",
                "",
                self.round4__eps_gas_heat_total_therms,
                "",
                self.round4__eps_heat_pump_total_therms,
            )
        )
        data.append(
            msg.format(
                "EPS Total kWh",
                "",
                self.round4__eps_gas_heat_total_kwh,
                "",
                self.round4__eps_heat_pump_total_kwh,
            )
        )
        data.append(
            msg.format(
                "EPS Total MBtu",
                "",
                self.round4__eps_gas_heat_total_mbtu,
                "",
                self.round4__eps_heat_pump_total_mbtu,
            )
        )

        data.append(msg.format(*["--"] * 5))

        data.append(
            msg.format(
                "Carbon Total Therms",
                self.round4__carbon_gas_heat_total_therms,
                "",
                self.round4__carbon_heat_pump_total_therms,
                "",
            )
        )
        data.append(
            msg.format(
                "Carbon Total kWh",
                self.round4__carbon_gas_heat_total_kwh,
                "",
                self.round4__carbon_heat_pump_total_kwh,
                "",
            )
        )
        data.append(
            msg.format(
                "Carbon Score",
                self.round4__carbon_gas_heat_score,
                "",
                self.round4__carbon_heat_pump_score,
                "",
            )
        )

        data.append(msg.format(*["--"] * 5))

        data.append(
            msg.format(
                "Total Therms",
                self.round4__consumption_gas_heat_total_therms,
                "",
                self.round4__consumption_heat_pump_total_therms,
                "",
            )
        )
        data.append(
            msg.format(
                "Total kWh",
                self.round4__consumption_gas_heat_total_kwh,
                "",
                self.round4__consumption_heat_pump_total_kwh,
                "",
            )
        )
        return "\n".join(data)

    @property
    def report_data(self):
        """Report"""
        data = super(Calculations2020, self).report_data
        if self.is_improved:
            _val = data["constants"]
            _val[
                "electric_smart_tstat_heating_savings_pct"
            ] = self.electric_smart_tstat_heating_savings_pct
            _val[
                "electric_smart_tstat_cooling_savings_pct"
            ] = self.electric_smart_tstat_cooling_savings_pct
            _val["gas_smart_tstat_heating_savings_pct"] = self.gas_smart_tstat_heating_savings_pct

            _val = data["unadjusted"]
            _val["gas_thermostat_heating_savings"] = self.gas_thermostat_savings_unadjusted
            _val["electric_thermostat_savings"] = self.electric_thermostat_savings_unadjusted
            _val["cooling_thermostat_savings"] = self.cooling_thermostat_savings_unadjusted

            data["gas_heat"][
                "solar_hot_water_kwh_no_fuel_weight"
            ] = self.solar_hot_water_kwh_gas_heat_no_fuel_weight

            _val = data["heat_pump"]
            _val["heating_kwh_no_fuel_weight"] = self.heating_kwh_heat_pump_no_fuel_weight
            _val["hot_water_kwh_no_fuel_weight"] = self.hot_water_kwh_heat_pump_no_fuel_weight
            _val[
                "solar_hot_water_kwh_no_fuel_weight"
            ] = self.solar_hot_water_kwh_heat_pump_no_fuel_weight
        return data
