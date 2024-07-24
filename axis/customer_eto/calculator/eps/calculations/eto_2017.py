"""eto_2017.py: Django Core Calculations for EPS Calculator"""


import logging

from .base import Calculations

__author__ = "Steven K"
__date__ = "08/21/2019 09:05"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

log = logging.getLogger(__name__)


class Calculations2017(Calculations):  # pylint: disable=too-many-public-methods
    """Calculation model for 2017"""

    def __init__(self, simulation, **kwargs):
        super(Calculations2017, self).__init__(simulation, **kwargs)
        self.program = kwargs.get("program")
        self.us_state = kwargs.get("us_state")
        self.smart_thermostat = kwargs.get("smart_thermostat")
        self.smart_thermostat_furnace_type = kwargs.get("smart_thermostat_furnace_type")
        self.qualifying_thermostat = kwargs.get(
            "qualifying_thermostat",
        )
        self.qty_shower_head_1p5 = kwargs.get("qty_shower_head_1p5", 0)
        self.qty_shower_head_1p6 = kwargs.get("qty_shower_head_1p6", 0)
        self.qty_shower_head_1p75 = kwargs.get("qty_shower_head_1p75", 0)
        self.qty_shower_wand_1p5 = kwargs.get("qty_shower_wand_1p5", 0)

        self.savings_pct = self.constants.EPS_WA_SAVINGS_PCT
        if self.us_state == "OR":
            self.savings_pct = self.constants.EPS_OR_SAVINGS_PCT

    @property
    def electric_smart_tstat_savings_pct(self):
        return self.savings_pct["electric_smart_tstat_savings_pct"]

    @property
    def gas_smart_tstat_savings_pct(self):
        return self.savings_pct["gas_smart_tstat_savings_pct"]

    @property
    def gas_showerhead_savings_pct(self):
        return self.savings_pct["gas_showerhead_savings_pct"]

    @property
    def electric_showerhead_savings_pct(self):
        return self.savings_pct["electric_showerhead_savings_pct"]

    @property
    def total_low_flow_shower_heads(self):
        """Total low flow shower heads"""
        return sum(
            [
                self.qty_shower_head_1p5,
                self.qty_shower_head_1p6,
                self.qty_shower_head_1p75,
                self.qty_shower_wand_1p5,
            ]
        )

    @property
    def gas_thermostat_savings_unadjusted(self):
        """Gas thermostat savings unaadjusted"""
        if not self.is_improved:
            return 0.0
        gas_smart_tstat = self.smart_thermostat and self.smart_thermostat_furnace_type == "GAS"
        if self.heating_therms_unadjusted > 0 and gas_smart_tstat:
            return self.heating_therms_unadjusted * self.gas_smart_tstat_savings_pct
        return 0.0

    @property
    def heating_therms_gas_heat_fuel_weight(self):
        """Heating therms gas fuel weight"""
        if not self.is_improved:
            return self.heating_therms_unadjusted
        return self.heating_therms_unadjusted - self.gas_thermostat_savings_unadjusted

    @property
    def electric_thermostat_savings_unadjusted(self):
        """Electric thermostat savings unadjusted"""
        if not self.is_improved:
            return 0.0
        ashp_smart_tstat = self.smart_thermostat and self.smart_thermostat_furnace_type == "ASHP"
        if self.heating_therms_unadjusted == 0 and ashp_smart_tstat:
            return self.heating_kwh_unadjusted * self.electric_smart_tstat_savings_pct
        return 0.0

    # pylint: disable=inconsistent-return-statements
    @property
    def heating_kwh_heat_pump_no_fuel_weight(self):
        """Heating kWh no fuel weight"""
        if not self.is_improved:
            return
        _val = self.heating_kwh_heat_pump_correction
        _val -= self.pv_kwh_unadjusted
        _val -= self.electric_thermostat_savings_unadjusted
        return max(0.0, _val)

    @property
    def heating_kwh_heat_pump_fuel_weight(self):
        """Heating heat pump fuel weight"""
        if not self.is_improved:
            return self.heating_kwh_heat_pump_correction * self.electric_space_heat_fuel_weight
        value = self.heating_kwh_heat_pump_no_fuel_weight * self.electric_space_heat_fuel_weight
        return max(0.0, value)

    @property
    def hot_water_gas_heat_low_flow_shower_head_unadjusted(self):
        """Hot water gas heat low flow shower head unadjusted"""
        has_low_flow_showerheads = self.total_low_flow_shower_heads >= 1
        if self.is_improved and self.hot_water_therms_unadjusted > 0 and has_low_flow_showerheads:
            return self.hot_water_therms_unadjusted * self.gas_showerhead_savings_pct
        return 0.0

    @property
    def hot_water_gas_heat_low_flow_shower_head_additional_unadjusted(self):
        """Hot water gas heat low flow additional shower head unadjusted"""
        has_low_flow_showerheads = self.total_low_flow_shower_heads >= 1
        if self.is_improved and self.hot_water_therms_unadjusted > 0 and has_low_flow_showerheads:
            return (self.hot_water_therms_unadjusted * self.gas_showerhead_savings_pct) / 2.0
        return 0.0

    @property
    def hot_water_electric_heat_low_flow_shower_head_unadjusted(self):
        """Hot water electric heat low flow shower head unadjusted"""
        has_low_flow_showerheads = self.total_low_flow_shower_heads >= 1
        if self.is_improved and self.hot_water_kwh_unadjusted > 0 and has_low_flow_showerheads:
            return self.hot_water_kwh_unadjusted * self.electric_showerhead_savings_pct
        return 0.0

    @property
    def hot_water_electric_heat_low_flow_shower_head_additional_unadjusted(self):
        """Hot water electric heat low flow additional shower head unadjusted"""
        has_low_flow_showerheads = self.total_low_flow_shower_heads >= 1
        if self.is_improved and self.hot_water_kwh_unadjusted > 0 and has_low_flow_showerheads:
            return (self.hot_water_kwh_unadjusted * self.electric_showerhead_savings_pct) / 2.0
        return 0.0

    @property
    def hot_water_therms_gas_heat_fuel_weight(self):
        """Hot water therms gas heat fuel weight"""
        if not self.is_improved:
            return super(Calculations2017, self).hot_water_therms_gas_heat_fuel_weight
        if self.solar_hot_water_therms_unadjusted > 0:
            return 0.0
        value = self.hot_water_therms_unadjusted
        value -= self.hot_water_gas_heat_low_flow_shower_head_unadjusted
        value -= self.hot_water_gas_heat_low_flow_shower_head_additional_unadjusted
        return value

    @property
    def hot_water_therms_heat_pump_fuel_weight(self):
        """Hot water therms heat pump fuel weight"""
        if not self.is_improved:
            return super(Calculations2017, self).hot_water_therms_heat_pump_fuel_weight
        if self.solar_hot_water_therms_unadjusted > 0:
            return 0.0
        value = self.hot_water_therms_unadjusted
        value -= self.hot_water_gas_heat_low_flow_shower_head_unadjusted
        value -= self.hot_water_gas_heat_low_flow_shower_head_additional_unadjusted
        return value

    @property
    def hot_water_kwh_gas_heat_fuel_weight(self):
        """Hot water gas heat kWh fuel weight"""
        if not self.is_improved:
            return super(Calculations2017, self).hot_water_kwh_gas_heat_fuel_weight
        if self.solar_hot_water_kwh_unadjusted > 0:
            return 0.0
        value = self.hot_water_kwh_unadjusted
        value -= self.hot_water_electric_heat_low_flow_shower_head_unadjusted
        value -= self.hot_water_electric_heat_low_flow_shower_head_additional_unadjusted
        value -= self.pv_kwh_unadjusted
        return max(0, value)

    @property
    def hot_water_electric_heat_low_flow_shower_head_gas_heat_fuel_weight(self):
        """Hot water electric heat low flow shower head gas heat fuel weight"""
        if self.solar_hot_water_kwh_unadjusted > 0:
            return 0.0
        if self.is_improved:
            return self.hot_water_kwh_gas_heat_fuel_weight * self.electric_hot_water_fuel_weight
        return 0.0

    # pylint: disable=inconsistent-return-statements
    @property
    def hot_water_kwh_heat_pump_no_fuel_weight(self):
        """Hot water electric heat low flow shower head heat pump fuel weight"""
        if not self.is_improved:
            return
        if self.solar_hot_water_kwh_unadjusted > 0:
            return 0.0
        if self.pv_kwh_unadjusted > 0 and self.pv_kwh_unadjusted > self.heating_kwh_unadjusted:
            value = self.hot_water_kwh_unadjusted
            value -= self.hot_water_electric_heat_low_flow_shower_head_unadjusted
            value -= self.hot_water_electric_heat_low_flow_shower_head_additional_unadjusted
            value -= self.pv_kwh_unadjusted
            value -= self.heating_kwh_unadjusted
            return max(0, value)
        value = self.hot_water_kwh_unadjusted
        value -= self.hot_water_electric_heat_low_flow_shower_head_unadjusted
        value -= self.hot_water_electric_heat_low_flow_shower_head_additional_unadjusted
        return max(0, value)

    @property
    def hot_water_kwh_heat_pump_fuel_weight(self):
        """Hot water kWh heat pump fuel weight"""
        if not self.is_improved:
            return super(Calculations2017, self).hot_water_kwh_heat_pump_fuel_weight
        return self.hot_water_kwh_heat_pump_no_fuel_weight * self.electric_hot_water_fuel_weight

    @property
    def lights_and_appliances_therms_heat_pump_fuel_weight(self):
        """Lights and appliances therm heat pump fuel weight"""
        if not self.is_improved:
            return super(Calculations2017, self).lights_and_appliances_therms_heat_pump_fuel_weight
        return 0.0

    @property
    def solar_hot_water_therms_gas_heat_fuel_weight(self):
        """Solar hot water therms gas heat fuel weight"""
        if not self.is_improved:
            return super(Calculations2017, self).solar_hot_water_therms_gas_heat_fuel_weight
        if self.solar_hot_water_therms_unadjusted > 0:
            value = self.solar_hot_water_therms_unadjusted
            value -= self.hot_water_gas_heat_low_flow_shower_head_unadjusted
            value -= self.hot_water_gas_heat_low_flow_shower_head_additional_unadjusted
            return value
        return 0.0

    @property
    def solar_hot_water_therms_heat_pump_fuel_weight(self):
        """Solar hot water therms heat pump fuel weight"""
        if not self.is_improved:
            return super(Calculations2017, self).solar_hot_water_therms_heat_pump_fuel_weight
        return self.solar_hot_water_therms_gas_heat_fuel_weight

    # pylint: disable=inconsistent-return-statements
    @property
    def solar_hot_water_kwh_gas_heat_no_fuel_weight(self):
        """Solar hot water kWh gas heat no fuel weight"""
        if not self.is_improved:
            return
        value = 0.0
        if self.solar_hot_water_kwh_unadjusted > 0:
            value = self.solar_hot_water_kwh_unadjusted
            value -= self.hot_water_electric_heat_low_flow_shower_head_unadjusted
            value -= self.hot_water_electric_heat_low_flow_shower_head_additional_unadjusted
            if self.pv_kwh_unadjusted > 0:
                value -= self.pv_kwh_unadjusted
        return max(0, value)

    @property
    def solar_hot_water_kwh_gas_heat_fuel_weight(self):
        """Solar hot water kWh gas heat fuel weight"""
        if not self.is_improved:
            return super(Calculations2017, self).solar_hot_water_kwh_gas_heat_fuel_weight
        value = self.solar_hot_water_kwh_gas_heat_no_fuel_weight
        value *= self.electric_hot_water_fuel_weight
        return value

    @property
    def solar_hot_water_kwh_heat_pump_no_fuel_weight(self):
        """Solar hot water kWh heat pump no fuel weight"""
        if not self.is_improved:
            return
        value = 0.0
        if self.solar_hot_water_kwh_unadjusted > 0:
            value = self.solar_hot_water_kwh_unadjusted
            value -= self.hot_water_electric_heat_low_flow_shower_head_unadjusted
            value -= self.hot_water_electric_heat_low_flow_shower_head_additional_unadjusted
            if self.pv_kwh_unadjusted > 0 and self.pv_kwh_unadjusted > self.heating_kwh_unadjusted:
                value -= self.pv_kwh_unadjusted
                value -= self.heating_kwh_unadjusted
        return max(0, value)

    @property
    def solar_hot_water_kwh_heat_pump_fuel_weight(self):
        """Solar hot water kWh heat pump fuel weight"""
        if not self.is_improved:
            return super(Calculations2017, self).solar_hot_water_kwh_heat_pump_fuel_weight
        value = self.solar_hot_water_kwh_heat_pump_no_fuel_weight
        value *= self.electric_hot_water_fuel_weight
        return value

    @property
    def pv_kwh_gas_heat_fuel_weight(self):
        """Photovoltaics gas heat fuel weight"""
        if not self.is_improved:
            return super(Calculations2017, self).pv_kwh_gas_heat_fuel_weight

        value = self.pv_kwh_unadjusted
        val = self.hot_water_kwh_unadjusted
        val -= self.hot_water_electric_heat_low_flow_shower_head_unadjusted
        val -= self.hot_water_electric_heat_low_flow_shower_head_additional_unadjusted
        value -= val
        if self.solar_hot_water_kwh_unadjusted > 0.0:
            value = self.pv_kwh_unadjusted
            val = self.solar_hot_water_kwh_unadjusted
            val -= self.hot_water_electric_heat_low_flow_shower_head_unadjusted
            val -= self.hot_water_electric_heat_low_flow_shower_head_additional_unadjusted
            value -= val
        return max(0.0, value)

    @property
    def pv_kwh_heat_pump_fuel_weight(self):
        """Photovoltaics heat pump fuel weight"""
        if not self.is_improved:
            return super(Calculations2017, self).pv_kwh_heat_pump_fuel_weight
        value = self.pv_kwh_unadjusted
        value -= self.heating_kwh_unadjusted
        val = self.hot_water_kwh_unadjusted
        val -= self.hot_water_electric_heat_low_flow_shower_head_unadjusted
        val -= self.hot_water_electric_heat_low_flow_shower_head_additional_unadjusted
        value -= val
        if self.solar_hot_water_kwh_unadjusted > 0.0:
            value = self.pv_kwh_unadjusted
            value -= self.heating_kwh_unadjusted
            val = self.solar_hot_water_kwh_unadjusted
            val -= self.hot_water_electric_heat_low_flow_shower_head_unadjusted
            val -= self.hot_water_electric_heat_low_flow_shower_head_additional_unadjusted
            value -= val
        return max(0.0, value)

    @property
    def eps_gas_heat_total_therms(self):
        """EPS Gas heat total therms"""
        if not self.is_improved:
            return super(Calculations2017, self).eps_gas_heat_total_therms
        value = self.heating_therms_gas_heat_fuel_weight
        value += self.hot_water_therms_gas_heat_fuel_weight
        value += self.lights_and_appliances_therms_gas_heat_fuel_weight
        value += self.solar_hot_water_therms_gas_heat_fuel_weight
        return value

    @property
    def eps_heat_pump_total_therms(self):
        """EPS heat pump therms"""
        if not self.is_improved:
            return super(Calculations2017, self).eps_heat_pump_total_therms
        value = self.heating_therms_heat_pump_fuel_weight
        value += self.hot_water_therms_heat_pump_fuel_weight
        value += self.lights_and_appliances_therms_heat_pump_fuel_weight
        value += self.solar_hot_water_therms_heat_pump_fuel_weight
        return value

    @property
    def eps_gas_heat_total_kwh(self):
        """EPS Gas heat total kWh"""
        if not self.is_improved:
            return super(Calculations2017, self).eps_gas_heat_total_kwh
        value = self.heating_kwh_gas_heat_fuel_weight
        value += self.cooling_kwh_gas_heat_fuel_weight
        value += self.hot_water_electric_heat_low_flow_shower_head_gas_heat_fuel_weight
        value += self.lights_and_appliances_kwh_gas_heat_fuel_weight
        value += self.solar_hot_water_kwh_gas_heat_fuel_weight
        value -= self.pv_kwh_gas_heat_fuel_weight
        return value

    @property
    def eps_heat_pump_total_kwh(self):
        """EPS heat pump total kWh"""
        if not self.is_improved:
            return super(Calculations2017, self).eps_heat_pump_total_kwh
        value = self.heating_kwh_heat_pump_fuel_weight
        value += self.cooling_kwh_heat_pump_fuel_weight
        value += self.hot_water_kwh_heat_pump_fuel_weight
        value += self.lights_and_appliances_kwh_heat_pump_fuel_weight
        value += self.solar_hot_water_kwh_heat_pump_fuel_weight
        value -= self.pv_kwh_heat_pump_fuel_weight
        return value

    @property
    def carbon_gas_heat_total_therms(self):
        """Carbon total therms"""
        if not self.is_improved:
            return super(Calculations2017, self).carbon_gas_heat_total_therms
        value = self.heating_therms_gas_heat_fuel_weight
        value += self.hot_water_therms_gas_heat_fuel_weight
        value += self.lights_and_appliances_therms_gas_heat_fuel_weight
        if self.solar_hot_water_therms_unadjusted > 0:
            value = self.heating_therms_gas_heat_fuel_weight
            value += self.solar_hot_water_therms_gas_heat_fuel_weight
            value += self.lights_and_appliances_therms_gas_heat_fuel_weight
        return value * self.gas_carbon_factor / 2000.0

    @property
    def carbon_gas_heat_total_therms_fuel_weight(self):
        """Carbon gas heat total therms fuel weight"""
        if not self.is_improved:
            return
        return self.carbon_gas_heat_total_therms * 2000 / self.gas_carbon_factor

    @property
    def carbon_heat_pump_total_therms(self):
        """Carbon heat pump total therms"""
        if not self.is_improved:
            return super(Calculations2017, self).carbon_heat_pump_total_therms
        value = self.heating_therms_heat_pump_fuel_weight
        value += self.hot_water_therms_heat_pump_fuel_weight
        value += self.lights_and_appliances_therms_heat_pump_fuel_weight
        if self.solar_hot_water_therms_unadjusted > 0:
            value = self.heating_therms_heat_pump_fuel_weight
            value += self.solar_hot_water_therms_gas_heat_fuel_weight
            value += self.lights_and_appliances_therms_heat_pump_fuel_weight
        return value * self.gas_carbon_factor / 2000.0

    @property
    def carbon_heat_pump_total_therms_fuel_weight(self):
        """Carbon heat pump total therms fuel weight"""
        if not self.is_improved:
            return
        return self.carbon_heat_pump_total_therms * 2000.0 / self.gas_carbon_factor

    @property
    def carbon_gas_heat_total_kwh(self):
        """Carbon gas heat total kWh"""
        if not self.is_improved:
            value = self.heating_kwh_unadjusted
            value += self.cooling_kwh_unadjusted
            value += self.hot_water_kwh_unadjusted
            value += self.lights_and_appliances_kwh_unadjusted
            value *= self.electric_carbon_factor
            value /= 2000.00
            return value
        if self.simulation.solar_hot_water_kwh > 0:
            value = self.heating_kwh_gas_heat_fuel_weight
            value += self.cooling_kwh_gas_heat_fuel_weight
            value += self.lights_and_appliances_kwh_gas_heat_fuel_weight
            value += self.solar_hot_water_kwh_gas_heat_fuel_weight
            value -= self.pv_kwh_gas_heat_fuel_weight
            value *= self.electric_carbon_factor
            value /= 2000.00
            return value
        value = self.heating_kwh_gas_heat_fuel_weight
        value += self.cooling_kwh_gas_heat_fuel_weight
        value += self.hot_water_kwh_gas_heat_fuel_weight
        value += self.lights_and_appliances_kwh_gas_heat_fuel_weight
        value -= self.pv_kwh_gas_heat_fuel_weight
        value *= self.electric_carbon_factor
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

        if self.simulation.solar_hot_water_kwh > 0:
            value = self.heating_kwh_heat_pump_no_fuel_weight
            value += self.cooling_kwh_heat_pump_fuel_weight
            value += self.lights_and_appliances_kwh_heat_pump_fuel_weight
            value += self.solar_hot_water_kwh_heat_pump_no_fuel_weight
            value -= self.pv_kwh_heat_pump_fuel_weight
            value *= self.electric_carbon_factor
            value /= 2000.00
            return value

        value = self.heating_kwh_heat_pump_no_fuel_weight
        value += self.cooling_kwh_heat_pump_fuel_weight
        value += self.hot_water_kwh_heat_pump_no_fuel_weight
        value += self.lights_and_appliances_kwh_heat_pump_fuel_weight
        value -= self.pv_kwh_heat_pump_fuel_weight
        value *= self.electric_carbon_factor
        value /= 2000.00
        return value

    @property
    def carbon_gas_heat_total_kwh_fuel_weight(self):
        """Carbon gas heat total kWh fuel weight"""
        if not self.is_improved:
            return
        return self.carbon_gas_heat_total_kwh * 2000.0 / self.electric_carbon_factor

    @property
    def carbon_heat_pump_total_kwh_fuel_weight(self):
        """Carbon heat pump total kWh fuel weight"""
        if not self.is_improved:
            return
        return self.carbon_heat_pump_total_kwh * 2000 / self.electric_carbon_factor

    @property
    def consumption_gas_heat_total_therms(self):
        """Gas heat total therms consumption"""
        if not self.is_improved:
            return super(Calculations2017, self).consumption_gas_heat_total_therms

        value = self.heating_therms_gas_heat_fuel_weight
        value += self.hot_water_therms_unadjusted
        value -= self.hot_water_gas_heat_low_flow_shower_head_unadjusted
        value -= self.hot_water_gas_heat_low_flow_shower_head_additional_unadjusted
        value += self.lights_and_appliances_therms_gas_heat_fuel_weight
        return value

    @property
    def consumption_heat_pump_total_therms(self):
        """Heat Pump total therms consumption"""
        if not self.is_improved:
            return super(Calculations2017, self).consumption_heat_pump_total_therms

        value = self.heating_therms_heat_pump_fuel_weight
        value += self.hot_water_therms_unadjusted
        value -= self.hot_water_gas_heat_low_flow_shower_head_unadjusted
        value -= self.hot_water_gas_heat_low_flow_shower_head_additional_unadjusted
        value += self.lights_and_appliances_therms_heat_pump_fuel_weight
        return value

    @property
    def consumption_gas_heat_total_kwh(self):
        """Gas heat total kWh consumption"""
        if not self.is_improved:
            return super(Calculations2017, self).consumption_gas_heat_total_kwh

        value = self.heating_kwh_gas_heat_fuel_weight
        value += self.cooling_kwh_gas_heat_fuel_weight
        value += self.hot_water_kwh_unadjusted
        value -= self.hot_water_electric_heat_low_flow_shower_head_unadjusted
        value -= self.hot_water_electric_heat_low_flow_shower_head_additional_unadjusted
        value += self.lights_and_appliances_kwh_gas_heat_fuel_weight
        return value

    @property
    def consumption_heat_pump_total_kwh(self):
        """Heat Pump total therms consumption"""
        if not self.is_improved:
            return super(Calculations2017, self).consumption_heat_pump_total_kwh

        value = self.heating_kwh_unadjusted
        value -= self.electric_thermostat_savings_unadjusted
        value += self.cooling_kwh_unadjusted
        value += self.hot_water_kwh_unadjusted
        value -= self.hot_water_electric_heat_low_flow_shower_head_unadjusted
        value -= self.hot_water_electric_heat_low_flow_shower_head_additional_unadjusted
        value += self.lights_and_appliances_kwh_heat_pump_fuel_weight
        return value

    def report(self):
        """Report"""
        if not self.is_improved:
            return super(Calculations2017, self).report()

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
                msg.format("Smart Gas Tstat savings percent", self.gas_smart_tstat_savings_pct)
            )
            data.append(
                msg.format(
                    "Smart Electric Tstat savings percent", self.electric_smart_tstat_savings_pct
                )
            )
            if self.program != "eto-2019":
                data.append(
                    msg.format("Gas Showerhead savings percent", self.gas_showerhead_savings_pct)
                )
                data.append(
                    msg.format(
                        "Electric showerhead savings percent", self.electric_showerhead_savings_pct
                    )
                )

        msg = "{:35}{:>30}{:>30}{:>30}{:>30}"
        data.append(msg.format("", "", "" "Gas Heated Home", "Heat", "Pump"))
        data.append(msg.format("", "Unadjusted", "Fuel Weight DHW", "HP Correction", "Fuel Weight"))

        data.append(
            msg.format(
                "Heating Therms",
                self.round4__heating_therms_unadjusted,
                self.round4__heating_therms_gas_heat_fuel_weight,
                "",
                self.round4__heating_therms_heat_pump_fuel_weight,
            )
        )
        if self.is_improved:
            data.append(
                msg.format(
                    "  Gas tstat Savings",
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
                "",
                self.round4__heating_kwh_heat_pump_no_fuel_weight,
            )
        )
        if self.is_improved:
            data.append(
                msg.format(
                    "  Electric tstat Savings",
                    self.round4__electric_thermostat_savings_unadjusted,
                    "",
                    "w/ Fuel Weight",
                    self.round4__heating_kwh_heat_pump_fuel_weight,
                )
            )

        data.append(
            msg.format(
                "Cooling kWh",
                self.round4__cooling_kwh_unadjusted,
                self.round4__cooling_kwh_gas_heat_fuel_weight,
                "",
                self.round4__cooling_kwh_heat_pump_fuel_weight,
            )
        )
        data.append(
            msg.format(
                "Water Heating Therms",
                self.round4__hot_water_therms_unadjusted,
                self.round4__hot_water_therms_gas_heat_fuel_weight,
                "",
                self.round4__hot_water_therms_heat_pump_fuel_weight,
            )
        )
        if self.is_improved and self.program == "eto-2018":
            data.append(
                msg.format(
                    "  Gas Low-Flow Showerhead",
                    self.round4__hot_water_gas_heat_low_flow_shower_head_unadjusted,
                    "",
                    "",
                    "",
                )
            )
            data.append(
                msg.format(
                    "  Gas Add'l showerhead",
                    self.round4__hot_water_gas_heat_low_flow_shower_head_additional_unadjusted,
                    "",
                    "",
                    "",
                )
            )

        data.append(
            msg.format(
                "Water Heating kWH",
                self.round4__hot_water_kwh_unadjusted,
                self.round4__hot_water_kwh_gas_heat_fuel_weight,
                "",
                self.round4__hot_water_kwh_heat_pump_no_fuel_weight,
            )
        )
        if self.is_improved and self.program == "eto-2018":
            data.append(
                msg.format(
                    "  Electric Low-Flow Showerhead",
                    self.round4__hot_water_electric_heat_low_flow_shower_head_unadjusted,
                    self.round4__hot_water_electric_heat_low_flow_shower_head_gas_heat_fuel_weight,
                    "w/ Fuel Weight",
                    self.round4__hot_water_kwh_heat_pump_fuel_weight,
                )
            )
            data.append(
                msg.format(
                    "  Electric Add'l showerhead",
                    self.round4__hot_water_electric_heat_low_flow_shower_head_additional_unadjusted,
                    "",
                    "",
                    "",
                )
            )

        data.append(
            msg.format(
                "Lights & Appliances Therms",
                self.round4__lights_and_appliances_therms_unadjusted,
                self.round4__lights_and_appliances_therms_gas_heat_fuel_weight,
                "",
                self.round4__lights_and_appliances_therms_heat_pump_fuel_weight,
            )
        )
        data.append(
            msg.format(
                "Lights & Appliances kWH",
                self.round4__lights_and_appliances_kwh_unadjusted,
                self.round4__lights_and_appliances_kwh_gas_heat_fuel_weight,
                "",
                self.round4__lights_and_appliances_kwh_heat_pump_fuel_weight,
            )
        )
        data.append(
            msg.format(
                "Solar Water Heating Therms",
                self.round4__solar_hot_water_therms_unadjusted,
                self.round4__solar_hot_water_therms_gas_heat_fuel_weight,
                "",
                self.round4__solar_hot_water_therms_heat_pump_fuel_weight,
            )
        )
        data.append(
            msg.format(
                "Solar Water Heating kWH",
                self.round4__solar_hot_water_kwh_unadjusted,
                self.round4__solar_hot_water_kwh_gas_heat_no_fuel_weight,
                "",
                self.round4__solar_hot_water_kwh_heat_pump_no_fuel_weight,
            )
        )
        data.append(
            msg.format(
                "  With Fuel Weight",
                "",
                self.round4__solar_hot_water_kwh_gas_heat_fuel_weight,
                "w/ Fuel Weight",
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
                self.round4__carbon_gas_heat_total_therms_fuel_weight,
                self.round4__carbon_heat_pump_total_therms,
                self.round4__carbon_heat_pump_total_therms_fuel_weight,
            )
        )
        data.append(
            msg.format(
                "Carbon Total kWh",
                self.round4__carbon_gas_heat_total_kwh,
                self.round4__carbon_gas_heat_total_kwh_fuel_weight,
                self.round4__carbon_heat_pump_total_kwh,
                self.round4__carbon_heat_pump_total_kwh_fuel_weight,
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
        data = super(Calculations2017, self).report_data
        if self.is_improved:
            _val = data["constants"]
            _val["electric_smart_tstat_savings_pct"] = self.electric_smart_tstat_savings_pct
            _val["gas_smart_tstat_savings_pct"] = self.gas_smart_tstat_savings_pct
            _val["gas_showerhead_savings_pct"] = self.gas_showerhead_savings_pct
            _val["electric_showerhead_savings_pct"] = self.electric_showerhead_savings_pct

            _val = data["unadjusted"]
            _val["gas_thermostat_savings"] = self.gas_thermostat_savings_unadjusted
            _val["electric_thermostat_savings"] = self.electric_thermostat_savings_unadjusted
            _val[
                "gas_low_flow_showerhead"
            ] = self.hot_water_gas_heat_low_flow_shower_head_unadjusted
            _val[
                "gas_low_flow_showerhead_additional"
            ] = self.hot_water_electric_heat_low_flow_shower_head_additional_unadjusted
            _val[
                "electric_low_flow_showerhead"
            ] = self.hot_water_electric_heat_low_flow_shower_head_unadjusted
            _val[
                "electric_low_flow_showerhead_additional"
            ] = self.hot_water_electric_heat_low_flow_shower_head_additional_unadjusted

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
