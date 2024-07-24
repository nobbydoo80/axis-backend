"""base.py: Django Core Calculations for EPS Calculator"""


import logging
from collections import OrderedDict

from ..base import EPSBase

__author__ = "Steven K"
__date__ = "08/21/2019 09:04"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

log = logging.getLogger(__name__)


# pylint: disable=too-many-public-methods,too-many-instance-attributes
class Calculations(EPSBase):
    """Calculation model for pre-2017"""

    def __init__(self, simulation, **kwargs):
        self.simulation = simulation
        self.is_improved = kwargs.get("is_improved", False)
        self.constants = kwargs.get("constants")
        self.location = self.constants.LOCATION_TRANSLATION.get(
            kwargs.get("location"), kwargs.get("location")
        )
        self.electric_utility = kwargs.get("electric_utility")
        self.gas_utility = kwargs.get("gas_utility")
        self.us_state = kwargs.get("us_state")

        _val = self.constants.EPS_ELECTRIC_SPACE_HEAT_FUEL_WEIGHT.get(self.location)
        self.electric_space_heat_fuel_weight = _val
        _val = self.constants.EPS_ELECTRIC_HOT_WATER_FUEL_WEIGHT.get(self.location)
        self.electric_hot_water_fuel_weight = _val

        _val = self.constants.EPS_CODE_HEATING_AJUSTMENT_FACTORS.get(self.location)
        self.heat_pump_heating_correction_factor = _val
        _val = self.constants.EPS_CODE_COOLING_AJUSTMENT_FACTORS.get(self.location)
        self.heat_pump_cooling_correction_factor = _val
        if self.is_improved:
            _val = self.constants.EPS_IMPROVED_HEATING_AJUSTMENT_FACTORS.get(self.location)
            self.heat_pump_heating_correction_factor = _val
            _val = self.constants.EPS_IMPROVED_COOLING_AJUSTMENT_FACTORS.get(self.location)
            self.heat_pump_cooling_correction_factor = _val

        _val = self.constants.EPS_POUNDS_OF_CARBON_PER_KWH_BY_COMPANY_OR.get(self.electric_utility)
        if self.us_state == "WA":
            _val = self.constants.EPS_POUNDS_OF_CARBON_PER_KWH_BY_COMPANY_WA.get(
                self.electric_utility
            )
        self.electric_carbon_factor = _val
        if not self.electric_carbon_factor:
            _val = self.constants.EPS_POUNDS_OF_CARBON_PER_KWH_BY_COMPANY_OR.get("bpa")
            if self.us_state == "WA":
                _val = self.constants.EPS_POUNDS_OF_CARBON_PER_KWH_BY_COMPANY_WA.get("bpa")
            self.electric_carbon_factor = _val

        _val = self.constants.EPS_POUNDS_OF_CARBON_PER_KWH_BY_COMPANY_OR.get("natural gas")
        if self.us_state == "WA":
            _val = self.constants.EPS_POUNDS_OF_CARBON_PER_KWH_BY_COMPANY_WA.get("natural gas")
        self.gas_carbon_factor = _val

        base_value = self.simulation.heating_therms
        self.heating_therms_unadjusted = base_value
        self.heating_therms_heat_pump_correction = base_value
        self.heating_therms_heat_pump_fuel_weight = base_value

        base_value = self.simulation.heating_kwh
        self.heating_kwh_unadjusted = base_value

        self.heating_kwh_heat_pump_correction = base_value
        self.heating_kwh_heat_pump_correction *= self.heat_pump_heating_correction_factor

        base_value = self.simulation.cooling_kwh
        self.cooling_kwh_unadjusted = base_value

        self.cooling_kwh_heat_pump_correction = base_value
        self.cooling_kwh_heat_pump_correction *= self.heat_pump_cooling_correction_factor

        base_value = self.simulation.hot_water_therms
        self.hot_water_therms_unadjusted = base_value
        self.hot_water_therms_heat_pump_correction = base_value

        base_value = self.simulation.hot_water_kwh
        self.hot_water_kwh_unadjusted = base_value
        self.hot_water_kwh_heat_pump_correction = base_value

        base_value = self.simulation.lights_and_appliances_therms
        self.lights_and_appliances_therms_unadjusted = base_value
        self.lights_and_appliances_therms_gas_heat_fuel_weight = base_value
        self.lights_and_appliances_therms_heat_pump_correction = base_value

        base_value = self.simulation.lights_and_appliances_kwh
        self.lights_and_appliances_kwh_unadjusted = base_value
        self.lights_and_appliances_kwh_gas_heat_fuel_weight = base_value
        self.lights_and_appliances_kwh_heat_pump_correction = base_value
        self.lights_and_appliances_kwh_heat_pump_fuel_weight = base_value

    @property
    def heating_kwh_gas_heat_fuel_weight(self):
        """This changed in 2020 to account for smart thermostats"""
        return self.simulation.heating_kwh

    @property
    def heating_therms_gas_heat_fuel_weight(self):
        """Heating therms gas fuel weight"""
        return self.heating_therms_unadjusted

    @property
    def heating_kwh_heat_pump_fuel_weight(self):
        """Heating kWh heat pump fuel weight"""
        if not self.is_improved:
            return self.heating_kwh_heat_pump_correction * self.electric_space_heat_fuel_weight
        _val = self.heating_kwh_heat_pump_correction - self.pv_kwh_unadjusted
        _val *= self.electric_space_heat_fuel_weight
        return max(0.0, _val)

    @property
    def cooling_kwh_gas_heat_fuel_weight(self):
        return self.simulation.cooling_kwh

    @property
    def cooling_kwh_heat_pump_fuel_weight(self):
        return self.cooling_kwh_heat_pump_correction

    @property
    def hot_water_therms_gas_heat_fuel_weight(self):
        """Hot water therms gas heat fuel weight"""
        if not self.is_improved:
            return self.hot_water_therms_unadjusted
        if self.solar_hot_water_therms_unadjusted > 0.0:
            return 0.0
        return self.hot_water_therms_unadjusted

    @property
    def hot_water_therms_heat_pump_fuel_weight(self):
        """Hot water heat pump fuel weight"""
        if not self.is_improved:
            return self.hot_water_therms_heat_pump_correction
        if self.solar_hot_water_therms_unadjusted > 0.0:
            return 0.0
        return self.hot_water_therms_heat_pump_correction

    @property
    def hot_water_kwh_gas_heat_fuel_weight(self):
        """Hot water kWh gas heat fuel weight"""
        if not self.is_improved:
            return self.hot_water_kwh_unadjusted * self.electric_hot_water_fuel_weight
        if self.solar_hot_water_kwh_unadjusted > 0.0:
            return 0.0
        if self.pv_kwh_unadjusted > 0.0:
            _val = self.hot_water_kwh_unadjusted - self.pv_kwh_unadjusted
            _val *= self.electric_hot_water_fuel_weight
            return max(0.0, _val)
        return max(0.0, self.hot_water_kwh_unadjusted * self.electric_hot_water_fuel_weight)

    @property
    def hot_water_kwh_heat_pump_fuel_weight(self):
        """Hot water kWh heat pump fuel weight"""
        if not self.is_improved:
            return self.hot_water_kwh_unadjusted * self.electric_hot_water_fuel_weight

        pv_exists = self.pv_kwh_unadjusted > 0.0
        if self.solar_hot_water_kwh_unadjusted > 0.0:
            value = 0.0
        elif pv_exists and self.pv_kwh_unadjusted > self.heating_kwh_heat_pump_correction:
            value = self.hot_water_kwh_unadjusted - self.pv_kwh_unadjusted
            value -= self.heating_kwh_heat_pump_correction
            value *= self.electric_hot_water_fuel_weight
        else:
            value = self.hot_water_kwh_unadjusted * self.electric_hot_water_fuel_weight

        return max(0.0, value)

    @property
    def lights_and_appliances_therms_heat_pump_fuel_weight(self):
        """Lights and appliances therm heat pump fuel weight"""
        return self.lights_and_appliances_therms_heat_pump_correction

    @property
    def solar_hot_water_therms_unadjusted(self):
        """Solar hot water therms unadjusted"""
        if not self.is_improved:
            return "N/A"
        return self.simulation.solar_hot_water_therms

    @property
    def solar_hot_water_therms_gas_heat_fuel_weight(self):
        """Solar hot water therms gas heat fuel weight"""
        if not self.is_improved:
            return "N/A"
        if self.solar_hot_water_therms_unadjusted > 0:
            return self.solar_hot_water_therms_unadjusted
        return 0.0

    @property
    def solar_hot_water_therms_heat_pump_correction(self):
        """Solar hot water therms heat pump correction"""
        if not self.is_improved:
            return "N/A"
        if self.solar_hot_water_therms_unadjusted > 0:
            return self.solar_hot_water_therms_unadjusted
        return 0.0

    @property
    def solar_hot_water_therms_heat_pump_fuel_weight(self):
        """Solar hot water therms heat pump fuel weight"""
        if not self.is_improved:
            return "N/A"
        if self.solar_hot_water_therms_unadjusted > 0:
            return self.solar_hot_water_therms_unadjusted
        return 0.0

    @property
    def solar_hot_water_kwh_unadjusted(self):
        """Solar hot water kWh unadjusted"""
        if not self.is_improved:
            return "N/A"
        return self.simulation.solar_hot_water_kwh

    @property
    def solar_hot_water_kwh_gas_heat_fuel_weight(self):
        """Solar hot water kWh gas heat fuel weight"""
        if not self.is_improved:
            return "N/A"
        value = 0.0
        if self.solar_hot_water_kwh_unadjusted > 0.0:
            value = self.solar_hot_water_kwh_unadjusted * self.electric_hot_water_fuel_weight
            if self.pv_kwh_unadjusted > 0.0:
                value = self.solar_hot_water_kwh_unadjusted - self.pv_kwh_unadjusted
                value *= self.electric_hot_water_fuel_weight
        return max(0.0, value)

    @property
    def solar_hot_water_kwh_heat_pump_correction(self):
        """Solar hot water kWh heat pump correction"""
        if not self.is_improved:
            return "N/A"
        return self.solar_hot_water_kwh_unadjusted

    @property
    def solar_hot_water_kwh_heat_pump_fuel_weight(self):
        """Solar hot water kWh heat pump fuel weight"""
        if not self.is_improved:
            return "N/A"
        value = 0.0

        if self.solar_hot_water_kwh_unadjusted > 0.0:
            value = self.solar_hot_water_kwh_unadjusted * self.electric_hot_water_fuel_weight
            pv_exists = self.pv_kwh_unadjusted > 0.0
            if pv_exists and self.pv_kwh_unadjusted > self.heating_kwh_heat_pump_correction:
                value = self.solar_hot_water_kwh_unadjusted
                value -= self.pv_kwh_unadjusted - self.heating_kwh_heat_pump_correction
                value *= self.electric_hot_water_fuel_weight
        return max(0.0, value)

    @property
    def pv_kwh_unadjusted(self):
        """Photovoltaics kWh unadjusted"""
        if not self.is_improved:
            return "N/A"
        return self.simulation.pv_kwh

    @property
    def pv_kwh_gas_heat_fuel_weight(self):
        """Photovoltaics gas heat fuel weight"""
        if not self.is_improved:
            return "N/A"
        value = self.pv_kwh_unadjusted - self.hot_water_kwh_unadjusted
        if self.solar_hot_water_kwh_unadjusted > 0.0:
            value = self.pv_kwh_unadjusted - self.solar_hot_water_kwh_unadjusted
        return max(0.0, value)

    @property
    def pv_kwh_heat_pump_correction(self):
        """Photovoltaics heat pump correction"""
        if not self.is_improved:
            return "N/A"
        return self.pv_kwh_unadjusted

    @property
    def pv_kwh_heat_pump_fuel_weight(self):
        """Photovoltaics heat pump fuel weight"""
        if not self.is_improved:
            return "N/A"
        value = self.pv_kwh_unadjusted - self.heating_kwh_heat_pump_correction
        value -= self.hot_water_kwh_unadjusted
        if self.solar_hot_water_kwh_unadjusted > 0.0:
            value = self.pv_kwh_unadjusted - self.heating_kwh_heat_pump_correction
            value -= self.solar_hot_water_kwh_unadjusted
        return max(0.0, value)

    @property
    def eps_gas_heat_total_therms(self):
        """EPS Gas heat total therms"""
        value = self.heating_therms_gas_heat_fuel_weight
        value += self.hot_water_therms_gas_heat_fuel_weight
        value += self.lights_and_appliances_therms_gas_heat_fuel_weight
        if self.is_improved:
            value += self.solar_hot_water_therms_gas_heat_fuel_weight
        return value

    @property
    def eps_gas_heat_total_kwh(self):
        """EPS Gas heat total kWh"""
        value = self.heating_kwh_gas_heat_fuel_weight
        value += self.cooling_kwh_gas_heat_fuel_weight
        value += self.hot_water_kwh_gas_heat_fuel_weight
        value += self.lights_and_appliances_kwh_gas_heat_fuel_weight
        if self.is_improved:
            value += self.solar_hot_water_kwh_gas_heat_fuel_weight
            value -= self.pv_kwh_gas_heat_fuel_weight
        return value

    @property
    def eps_gas_heat_total_mbtu(self):
        """EPS Gas heat total mBtu"""
        value = self.therms_to_mbtu(self.eps_gas_heat_total_therms)
        value += self.kwh_to_mbtu(self.eps_gas_heat_total_kwh)
        return value

    @property
    def eps_heat_pump_total_therms(self):
        """EPS heat pump therms"""
        value = self.heating_therms_heat_pump_fuel_weight
        value += self.hot_water_therms_heat_pump_fuel_weight
        value += self.lights_and_appliances_therms_heat_pump_fuel_weight
        if self.is_improved:
            value += self.solar_hot_water_therms_heat_pump_fuel_weight
        return value

    @property
    def eps_heat_pump_total_kwh(self):
        """EPS heat pump total kWh"""
        value = self.heating_kwh_heat_pump_fuel_weight
        value += self.cooling_kwh_heat_pump_fuel_weight
        value += self.hot_water_kwh_heat_pump_fuel_weight
        value += self.lights_and_appliances_kwh_heat_pump_fuel_weight
        if self.is_improved:
            value += self.solar_hot_water_kwh_heat_pump_fuel_weight
            value -= self.pv_kwh_heat_pump_fuel_weight
        return value

    @property
    def eps_heat_pump_total_mbtu(self):
        """EPS heat pump total mBtu"""
        value = self.therms_to_mbtu(self.eps_heat_pump_total_therms)
        value += self.kwh_to_mbtu(self.eps_heat_pump_total_kwh)
        return value

    @property
    def carbon_gas_heat_total_therms(self):
        """Carbon total therms"""
        value = self.heating_therms_unadjusted
        value += self.hot_water_therms_unadjusted
        value += self.lights_and_appliances_therms_unadjusted
        if self.is_improved and self.simulation.solar_hot_water_therms > 0:
            value = self.heating_therms_unadjusted
            value += self.solar_hot_water_therms_unadjusted
            value += self.lights_and_appliances_therms_unadjusted
        value *= self.gas_carbon_factor
        value /= 2000.0
        return value

    @property
    def carbon_gas_heat_total_kwh(self):
        """Carbon gas heat total kWh"""
        if not self.is_improved:
            value = self.heating_kwh_unadjusted
            value += self.cooling_kwh_unadjusted
            value += self.hot_water_kwh_unadjusted
            value += self.lights_and_appliances_kwh_unadjusted
            value *= self.electric_carbon_factor
            value /= 2000.0
            return value
        if self.simulation.solar_hot_water_kwh > 0:
            value = self.heating_kwh_unadjusted
            value += self.cooling_kwh_unadjusted
            value += self.lights_and_appliances_kwh_unadjusted
            value += self.solar_hot_water_kwh_unadjusted
            value -= self.pv_kwh_unadjusted
            value *= self.electric_carbon_factor
            value /= 2000.0
            return value

        value = self.heating_kwh_unadjusted
        value += self.cooling_kwh_unadjusted
        value += self.hot_water_kwh_unadjusted
        value += self.lights_and_appliances_kwh_unadjusted
        value -= self.pv_kwh_unadjusted
        value *= self.electric_carbon_factor
        value /= 2000.0
        return value

    @property
    def carbon_gas_heat_score(self):
        """Carbon gas heat score"""
        return self.carbon_gas_heat_total_therms + self.carbon_gas_heat_total_kwh

    @property
    def carbon_heat_pump_total_therms(self):
        """Carbon heat pump total therms"""
        value = self.heating_therms_heat_pump_correction
        value += self.hot_water_therms_heat_pump_correction
        value += self.lights_and_appliances_therms_heat_pump_correction
        value *= self.gas_carbon_factor
        value /= 2000.00
        if self.is_improved and self.simulation.solar_hot_water_therms > 0:
            value = self.heating_therms_heat_pump_correction
            value += self.solar_hot_water_therms_heat_pump_correction
            value += self.lights_and_appliances_therms_heat_pump_correction
            value *= self.gas_carbon_factor
            value /= 2000.00
        return value

    @property
    def carbon_heat_pump_total_kwh(self):
        """Carbon heat pump total kWh"""
        if not self.is_improved:
            value = self.heating_kwh_heat_pump_correction
            value += self.cooling_kwh_heat_pump_correction
            value += self.hot_water_kwh_heat_pump_correction
            value += self.lights_and_appliances_kwh_heat_pump_correction
            value *= self.electric_carbon_factor
            value /= 2000.00
            return value
        if self.is_improved and self.simulation.solar_hot_water_kwh > 0:
            value = self.heating_kwh_heat_pump_correction
            value += self.cooling_kwh_heat_pump_correction
            value += self.solar_hot_water_kwh_heat_pump_correction
            value += self.lights_and_appliances_kwh_heat_pump_correction
            value -= self.pv_kwh_heat_pump_correction
            value *= self.electric_carbon_factor
            value /= 2000.00
            return value
        value = self.heating_kwh_heat_pump_correction
        value += self.cooling_kwh_heat_pump_correction
        value += self.hot_water_kwh_heat_pump_correction
        value += self.lights_and_appliances_kwh_heat_pump_correction
        value -= self.pv_kwh_heat_pump_correction
        value *= self.electric_carbon_factor
        value /= 2000.00
        return value

    @property
    def carbon_heat_pump_score(self):
        """Carbon heat pump score"""
        return self.carbon_heat_pump_total_therms + self.carbon_heat_pump_total_kwh

    @property
    def consumption_gas_heat_total_therms(self):
        """Gas heat total therms consumption"""
        value = self.heating_therms_unadjusted + self.hot_water_therms_unadjusted
        value += self.lights_and_appliances_therms_unadjusted
        return value

    @property
    def consumption_gas_heat_total_kwh(self):
        """Gas heat total kWh consumption"""
        value = self.heating_kwh_unadjusted + self.cooling_kwh_unadjusted
        value += self.hot_water_kwh_unadjusted + self.lights_and_appliances_kwh_unadjusted
        return value

    @property
    def consumption_heat_pump_total_therms(self):
        """Heat Pump total therms consumption"""
        value = self.heating_therms_heat_pump_correction
        value += self.hot_water_therms_heat_pump_correction
        value += self.lights_and_appliances_therms_heat_pump_correction
        return value

    @property
    def consumption_heat_pump_total_kwh(self):
        """Heat Pump total therms consumption"""
        value = self.heating_kwh_heat_pump_correction
        value += self.cooling_kwh_heat_pump_correction
        value += self.hot_water_kwh_heat_pump_correction
        value += self.lights_and_appliances_kwh_heat_pump_correction
        return value

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
                    "Gas Tstat Savings",
                    self.round4__gas_thermostat_savings_unadjusted,
                    "",
                    "",
                    "",
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
                    "",
                )
            )
        data.append(
            msg.format(
                "Cooling kWh",
                self.round4__cooling_kwh_unadjusted,
                self.round4__cooling_kwh_gas_heat_fuel_weight,
                self.round4__cooling_kwh_heat_pump_correction,
                self.round4__cooling_kwh_heat_pump_fuel_weight,
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
        """Report Data"""
        return OrderedDict(
            [
                ("is_improved", self.is_improved),
                ("type", "Improved" if self.is_improved else "Code"),
                (
                    "constants",
                    OrderedDict(
                        [
                            (
                                "electric_space_heat_fuel_weight",
                                self.electric_space_heat_fuel_weight,
                            ),
                            (
                                "electric_hot_water_fuel_weight",
                                self.electric_hot_water_fuel_weight,
                            ),
                            (
                                "heat_pump_heating_correction_factor",
                                self.heat_pump_heating_correction_factor,
                            ),
                            (
                                "heat_pump_cooling_correction_factor",
                                self.heat_pump_cooling_correction_factor,
                            ),
                            ("electric_carbon_factor", self.electric_carbon_factor),
                            ("gas_carbon_factor", self.gas_carbon_factor),
                        ]
                    ),
                ),
                (
                    "unadjusted",
                    OrderedDict(
                        [
                            ("heating_therms", self.heating_therms_unadjusted),
                            ("heating_therms", self.heating_therms_unadjusted),
                            ("cooling_kwh", self.cooling_kwh_unadjusted),
                            ("hot_water_therms", self.hot_water_therms_unadjusted),
                            ("hot_water_kwh", self.hot_water_kwh_unadjusted),
                            (
                                "lights_and_appliances_therms",
                                self.lights_and_appliances_therms_unadjusted,
                            ),
                            (
                                "lights_and_appliances_kwh",
                                self.lights_and_appliances_kwh_unadjusted,
                            ),
                            (
                                "solar_hot_water_therms",
                                self.solar_hot_water_therms_unadjusted,
                            ),
                            (
                                "solar_hot_water_kwh",
                                self.solar_hot_water_kwh_unadjusted,
                            ),
                            ("pv_kwh", self.pv_kwh_unadjusted),
                        ]
                    ),
                ),
                (
                    "gas_heat",
                    OrderedDict(
                        [
                            (
                                "heating_therms",
                                self.heating_therms_gas_heat_fuel_weight,
                            ),
                            (
                                "heating_therms",
                                self.heating_therms_gas_heat_fuel_weight,
                            ),
                            ("cooling_kwh", self.cooling_kwh_gas_heat_fuel_weight),
                            (
                                "hot_water_therms",
                                self.hot_water_therms_gas_heat_fuel_weight,
                            ),
                            ("hot_water_kwh", self.hot_water_kwh_gas_heat_fuel_weight),
                            (
                                "lights_and_appliances_therms",
                                self.lights_and_appliances_therms_gas_heat_fuel_weight,
                            ),
                            (
                                "lights_and_appliances_kwh",
                                self.lights_and_appliances_kwh_gas_heat_fuel_weight,
                            ),
                            (
                                "solar_hot_water_therms",
                                self.solar_hot_water_therms_gas_heat_fuel_weight,
                            ),
                            (
                                "solar_hot_water_kwh",
                                self.solar_hot_water_kwh_gas_heat_fuel_weight,
                            ),
                            ("pv_kwh", self.pv_kwh_gas_heat_fuel_weight),
                        ]
                    ),
                ),
                (
                    "heat_pump_correction",
                    OrderedDict(
                        [
                            (
                                "heating_therms",
                                self.heating_therms_heat_pump_correction,
                            ),
                            (
                                "heating_therms",
                                self.heating_therms_heat_pump_correction,
                            ),
                            ("cooling_kwh", self.cooling_kwh_heat_pump_correction),
                            (
                                "hot_water_therms",
                                self.hot_water_therms_heat_pump_correction,
                            ),
                            ("hot_water_kwh", self.hot_water_kwh_heat_pump_correction),
                            (
                                "lights_and_appliances_therms",
                                self.lights_and_appliances_therms_heat_pump_correction,
                            ),
                            (
                                "lights_and_appliances_kwh",
                                self.lights_and_appliances_kwh_heat_pump_correction,
                            ),
                            (
                                "solar_hot_water_therms",
                                self.solar_hot_water_therms_heat_pump_correction,
                            ),
                            (
                                "solar_hot_water_kwh",
                                self.solar_hot_water_kwh_heat_pump_correction,
                            ),
                            ("pv_kwh", self.pv_kwh_heat_pump_correction),
                        ]
                    ),
                ),
                (
                    "heat_pump",
                    OrderedDict(
                        [
                            (
                                "heating_therms",
                                self.heating_therms_heat_pump_fuel_weight,
                            ),
                            (
                                "heating_therms",
                                self.heating_therms_heat_pump_fuel_weight,
                            ),
                            ("cooling_kwh", self.cooling_kwh_heat_pump_fuel_weight),
                            (
                                "hot_water_therms",
                                self.hot_water_therms_heat_pump_fuel_weight,
                            ),
                            ("hot_water_kwh", self.hot_water_kwh_heat_pump_fuel_weight),
                            (
                                "lights_and_appliances_therms",
                                self.lights_and_appliances_therms_heat_pump_fuel_weight,
                            ),
                            (
                                "lights_and_appliances_kwh",
                                self.lights_and_appliances_kwh_heat_pump_fuel_weight,
                            ),
                            (
                                "solar_hot_water_therms",
                                self.solar_hot_water_therms_heat_pump_fuel_weight,
                            ),
                            (
                                "solar_hot_water_kwh",
                                self.solar_hot_water_kwh_heat_pump_fuel_weight,
                            ),
                            ("pv_kwh", self.pv_kwh_heat_pump_fuel_weight),
                        ]
                    ),
                ),
                (
                    "eps",
                    OrderedDict(
                        [
                            ("gas_therms", self.eps_gas_heat_total_therms),
                            ("heat_pump_therms", self.eps_heat_pump_total_therms),
                            ("gas_kwh", self.eps_gas_heat_total_kwh),
                            ("heat_pump_kwh", self.eps_gas_heat_total_kwh),
                            ("gas_mbtu", self.eps_gas_heat_total_mbtu),
                            ("heat_pump_mbtu", self.eps_heat_pump_total_mbtu),
                        ]
                    ),
                ),
                (
                    "carbon",
                    OrderedDict(
                        [
                            ("gas_therms", self.carbon_gas_heat_total_therms),
                            ("heat_pump_therms", self.carbon_heat_pump_total_therms),
                            ("gas_kwh", self.carbon_gas_heat_total_kwh),
                            ("heat_pump_kwh", self.carbon_gas_heat_total_kwh),
                            ("gas_score", self.carbon_gas_heat_score),
                            ("heat_pump_score", self.carbon_heat_pump_score),
                        ]
                    ),
                ),
                (
                    "consumption",
                    OrderedDict(
                        [
                            ("gas_therms", self.consumption_gas_heat_total_therms),
                            (
                                "heat_pump_therms",
                                self.consumption_heat_pump_total_therms,
                            ),
                            ("gas_kwh", self.consumption_gas_heat_total_kwh),
                            ("heat_pump_kwh", self.consumption_heat_pump_total_kwh),
                        ]
                    ),
                ),
            ]
        )
