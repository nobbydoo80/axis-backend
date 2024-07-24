"""base.py: Django Base Incentives"""


import logging
from collections import OrderedDict

from axis.customer_neea.rtf_calculator.base import RTFBase

__author__ = "Steven K"
__date__ = "08/20/2019 08:31"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

log = logging.getLogger(__name__)


class MeasureLife(RTFBase):
    """A basic container for Measure live"""

    def __init__(self, short, medium, long):  # pylint: disable=redefined-builtin
        self.short = short
        self.medium = medium
        self.long = long


# pylint: disable=too-many-instance-attributes,too-many-public-methods
class BPAIncentivesCalculator(RTFBase):
    """Wrapper for the base BPA incentives"""

    def __init__(self, **kwargs):
        self.program = kwargs.get("program")
        self.us_state = kwargs.get("us_state")
        self.constants = kwargs.get("constants")
        self.heating_kwh_savings = kwargs.get("heating_kwh_savings", 0.0)
        self.heating_therm_savings = kwargs.get("heating_therm_savings", 0.0)
        self.cooling_kwh_savings = kwargs.get("cooling_kwh_savings", 0.0)
        self.cooling_therm_savings = kwargs.get("cooling_therm_savings", 0.0)
        self.water_heater_kwh_savings = kwargs.get("water_heater_kwh_savings", 0.0)
        self.water_heater_therm_savings = kwargs.get("water_heater_therm_savings", 0.0)
        self.smart_thermostat_kwh_savings = kwargs.get("smart_thermostat_kwh_savings", 0.0)
        self.smart_thermostat_therm_savings = kwargs.get("smart_thermostat_therm_savings", 0.0)
        self.showerhead_kwh_savings = kwargs.get("showerhead_kwh_savings", 0.0)
        self.showerhead_therm_savings = kwargs.get("showerhead_therm_savings", 0.0)
        self.lighting_kwh_savings = kwargs.get("lighting_kwh_savings", 0.0)
        self.lighting_therm_savings = kwargs.get("lighting_therm_savings", 0.0)
        self.appliance_kwh_savings = kwargs.get("appliance_kwh_savings", 0.0)
        self.appliance_therm_savings = kwargs.get("appliance_therm_savings", 0.0)
        self.default_percent_improvement = kwargs.get("default_percent_improvement", 0.0)
        self.revised_percent_improvement = kwargs.get("revised_percent_improvement", 0.0)
        self.reference_home_kwh = kwargs.get("reference_home_kwh", 0.0)
        self.total_kwh_savings = kwargs.get("total_kwh_savings", 0.0)
        self.total_therm_savings = kwargs.get("total_therm_savings", 0.0)
        self.heating_type = kwargs.get("heating_type")
        self.heating_fuel = kwargs.get("heating_fuel")
        self.cooling_type = kwargs.get("cooling_type")
        self.cooling_fuel = kwargs.get("cooling_fuel")
        self.water_heater_type = kwargs.get("water_heater_type")
        self.water_heater_tier = kwargs.get("water_heater_tier")
        self.electric_meter_number = kwargs.get("electric_meter_number")
        self.electric_utility = kwargs.get("electric_utility")
        self.gas_utility = kwargs.get("gas_utility")
        self.earth_advantage_certified = kwargs.get("earth_advantage_certified")
        self.short_incentive = dict(self.constants.BPA_KWH_PAYMENT_TIERS).get("short")
        self.medium_incentive = dict(self.constants.BPA_KWH_PAYMENT_TIERS).get("medium")
        self.long_incentive = dict(self.constants.BPA_KWH_PAYMENT_TIERS).get("long")

    @property
    def has_heat_pump(self):
        if "ashp" in self.heating_type.lower() or "gshp" in self.heating_type.lower():
            return True
        if "heat pump" in self.heating_type.lower():
            return True
        return False

    @property
    def use_revised_pct_improvement(self):
        """
        @deprecated
        The way to identify a utility incentive
        """
        return True

    @property
    def percent_improvement(self):
        """
        @deprecated
        Get the percent improvement"""
        return self.revised_percent_improvement

    @property
    def pct_improvement_method(self):
        """
        @deprecated
        Get the percent improvement method"""
        return "alternate"

    @property
    def heating_kwh_measure_life(self):
        """Heating kWh Measure Life"""
        medium_ml = self.heating_kwh_savings * self.constants.NEEA_MEDIUM_MEASURE_LIFE_PCT
        long_ml = self.heating_kwh_savings - medium_ml
        return MeasureLife(0.0, medium_ml, long_ml)

    @property
    def heating_therm_measure_life(self):
        """Heating therm Measure Life"""
        medium_ml = self.heating_therm_savings * self.constants.NEEA_MEDIUM_MEASURE_LIFE_PCT
        long_ml = self.heating_therm_savings - medium_ml
        return MeasureLife(0.0, medium_ml, long_ml)

    @property
    def cooling_kwh_measure_life(self):
        """Cooling kWh Measure Life"""
        medium_ml = self.cooling_kwh_savings * self.constants.NEEA_COOLING_INTERNAL_GAINS_PCT
        long_ml = self.cooling_kwh_savings - medium_ml
        return MeasureLife(0.0, medium_ml, long_ml)

    @property
    def cooling_therm_measure_life(self):
        """Heating therm Measure Life"""
        medium_ml = self.cooling_therm_savings * self.constants.NEEA_COOLING_INTERNAL_GAINS_PCT
        long_ml = self.cooling_therm_savings - medium_ml
        return MeasureLife(0.0, medium_ml, long_ml)

    @property
    def smart_thermostat_kwh_measure_life(self):
        """Smart thermostat kWh Measure Life"""
        return MeasureLife(self.smart_thermostat_kwh_savings, 0.0, 0.0)

    @property
    def smart_thermostat_therm_measure_life(self):
        """Smart thermostat therm Measure Life"""
        return MeasureLife(self.smart_thermostat_therm_savings, 0.0, 0.0)

    @property
    def water_heater_kwh_measure_life(self):
        """Water heater kWh Measure Life"""
        return MeasureLife(0.0, self.water_heater_kwh_savings, 0.0)

    @property
    def water_heater_therm_measure_life(self):
        """Water heater therm Measure Life"""
        return MeasureLife(0.0, self.water_heater_therm_savings, 0.0)

    @property
    def showerhead_kwh_measure_life(self):
        """Showerhead kWh Measure Life"""
        return MeasureLife(self.showerhead_kwh_savings, 0.0, 0.0)

    @property
    def showerhead_therm_measure_life(self):
        """Showerhead kWh Measure Life"""
        return MeasureLife(self.showerhead_therm_savings, 0.0, 0.0)

    @property
    def lighting_kwh_measure_life(self):
        """Lighting kWh Measure Life"""
        return MeasureLife(self.lighting_kwh_savings, 0.0, 0.0)

    @property
    def lighting_therm_measure_life(self):
        """Lighting therm Measure Life"""
        return MeasureLife(0.0, 0.0, 0.0)

    @property
    def appliances_kwh_measure_life(self):
        """Appliance kWh Measure Life"""
        return MeasureLife(0.0, self.appliance_kwh_savings, 0.0)

    @property
    def appliances_therm_measure_life(self):
        """Appliance therm Measure Life"""
        return MeasureLife(0.0, self.appliance_therm_savings, 0.0)

    @property
    def total_kwh_measure_life(self):
        """Total kWh Measure Life"""
        totals = [
            self.heating_kwh_measure_life,
            self.cooling_kwh_measure_life,
            self.smart_thermostat_kwh_measure_life,
            self.water_heater_kwh_measure_life,
            self.showerhead_kwh_measure_life,
            self.lighting_kwh_measure_life,
            self.appliances_kwh_measure_life,
        ]
        return MeasureLife(
            sum([x.short for x in totals]),
            sum([x.medium for x in totals]),
            sum([x.long for x in totals]),
        )

    @property
    def total_therm_measure_life(self):
        """Total therm Measure Life"""
        totals = [
            self.heating_therm_measure_life,
            self.cooling_therm_measure_life,
            self.smart_thermostat_therm_measure_life,
            self.water_heater_therm_measure_life,
            self.showerhead_therm_measure_life,
            self.lighting_therm_measure_life,
            self.appliances_therm_measure_life,
        ]
        return MeasureLife(
            sum([x.short for x in totals]),
            sum([x.medium for x in totals]),
            sum([x.long for x in totals]),
        )

    @property
    def bpa_hvac_kwh_savings(self):
        """BPA HVAC hWh Savings"""
        return self.heating_kwh_measure_life.medium + self.cooling_kwh_measure_life.medium

    @property
    def hvac_kwh_incentive(self):
        """BPA HVAC hWh Incentive"""
        return self.round_value(self.bpa_hvac_kwh_savings * self.medium_incentive, 2)

    @property
    def bpa_lighting_kwh_savings(self):
        """BPA Lighting hWh Savings"""
        return self.lighting_kwh_measure_life.short

    @property
    def lighting_kwh_incentive(self):
        """BPA Lighting hWh Incentive"""
        return self.round_value(self.bpa_lighting_kwh_savings * self.short_incentive, 2)

    @property
    def bpa_water_heater_kwh_savings(self):
        """BPA Hot Water hWh Savings"""
        return self.water_heater_kwh_measure_life.medium

    @property
    def water_heater_kwh_incentive(self):
        """BPA Hot Water hWh Incentive"""
        return self.round_value(self.bpa_water_heater_kwh_savings * self.medium_incentive, 2)

    @property
    def bpa_appliance_kwh_savings(self):
        """BPA Appliance hWh Savings"""
        return self.appliances_kwh_measure_life.medium

    @property
    def appliance_kwh_incentive(self):
        """BPA Appliance hWh Incentive"""
        return self.round_value(self.bpa_appliance_kwh_savings * self.medium_incentive, 2)

    @property
    def bpa_showerhead_kwh_savings(self):
        """BPA Showerhead hWh Savings"""
        return self.showerhead_kwh_measure_life.short

    @property
    def showerhead_kwh_incentive(self):
        """BPA Showerhead hWh Incentive"""
        return self.round_value(self.bpa_showerhead_kwh_savings * self.short_incentive, 2)

    @property
    def bpa_windows_shell_kwh_savings(self):
        """BPA Windows & Shell hWh Savings"""
        return self.heating_kwh_measure_life.long + self.cooling_kwh_measure_life.long

    @property
    def windows_shell_kwh_incentive(self):
        """BPA Windows & Shell hWh Incentive"""
        return self.round_value(self.bpa_windows_shell_kwh_savings * self.long_incentive, 2)

    @property
    def bpa_smart_thermostat_kwh_savings(self):
        """BPA Smart Thermostat hWh Savings"""
        return self.smart_thermostat_kwh_measure_life.short

    @property
    def smart_thermostat_kwh_incentive(self):
        """BPA Smart Thermostat hWh Incentive"""
        return self.round_value(self.bpa_smart_thermostat_kwh_savings * self.short_incentive, 2)

    @property
    def reported_shell_windows_kwh_savings(self):
        """Reported Shell & Windows hWh Savings"""
        # Sum of "Heating" and "Cooling" "LONG" kWh savings
        # Note that Appliances isn't to be included in any of these calculations
        return self.total_kwh_measure_life.long - self.appliances_kwh_measure_life.long

    @property
    def reported_shell_windows_incentive(self):
        """Reported Shell & Windows hWh Incentive"""
        return self.round_value(self.reported_shell_windows_kwh_savings * self.long_incentive, 2)

    @property
    def reported_hvac_waterheater_kwh_savings(self):
        """Reported HVAC Waterheater hWh Savings"""
        # Sum of "Heating", "Cooling", and "Water Heating" "MEDIUM" kWh savings
        # Note that Appliances isn't to be included in any of these calculations
        return self.total_kwh_measure_life.medium - self.appliances_kwh_measure_life.medium

    @property
    def reported_hvac_waterheater_incentive(self):
        """Reported HVAC Waterheater hWh Incentive"""
        return self.round_value(
            self.reported_hvac_waterheater_kwh_savings * self.medium_incentive, 2
        )

    @property
    def reported_lighting_showerhead_tstats_kwh_savings(self):
        """Reported Lighting / Showerhead / Tstats hWh Savings"""
        # Sum of "Smart Tstat", "Low Flow Shower Head", and "Lighting" "SHORT" kWh savings
        # Note that Appliances isn't to be included in any of these calculations
        return self.total_kwh_measure_life.short - self.appliances_kwh_measure_life.short

    @property
    def reported_lighting_showerhead_tstats_incentive(self):
        """Reported Lighting / Showerhead / Tstats hWh Incentive"""
        return self.round_value(
            self.reported_lighting_showerhead_tstats_kwh_savings * self.short_incentive, 2
        )

    @property
    def bpa_total_kwh_savings(self):
        """BPA Total kWh Savings"""
        return (
            self.bpa_hvac_kwh_savings
            + self.bpa_lighting_kwh_savings
            + self.bpa_water_heater_kwh_savings
            + self.bpa_appliance_kwh_savings
            + self.bpa_windows_shell_kwh_savings
            + self.bpa_smart_thermostat_kwh_savings
            + self.bpa_showerhead_kwh_savings
        )

    @property
    def busbar_savings(self):
        """BPA Total kWh Savings"""
        return self.bpa_total_kwh_savings

    @property
    def busbar_consumption(self):
        """BPA Total kWh Consumption"""
        return max(self.reference_home_kwh - self.busbar_savings, 0)

    @property
    def required_pct_improvement(self):
        """Required % improvement to qualify for an incentive"""
        return 0.1

    @property
    def has_bpa_incentive(self):
        """Are we eligibile for an incentive"""
        return self.percent_improvement >= self.required_pct_improvement

    @property
    def total_incentive(self):
        """What is the toal incentive.  This is NOT what is paid!"""
        if self.has_bpa_incentive:
            return self.round_value(
                max(
                    self.hvac_kwh_incentive
                    + self.lighting_kwh_incentive
                    + self.water_heater_kwh_incentive
                    + self.appliance_kwh_incentive
                    + self.windows_shell_kwh_incentive
                    + self.smart_thermostat_kwh_incentive
                    + self.showerhead_kwh_incentive,
                    0.0,
                ),
                2,
            )
        return 0.0

    @property
    def has_incentive(self):
        """The final way to look for an incentive"""
        return None

    @property
    def builder_incentive(self):
        """The amount paid by a utility to a builder"""
        return 0.0

    def utility_report(self):
        """Report on utility stuff"""
        return []

    @property
    def incentive_paying_organization(self):
        return None

    def report(self):
        """Report on utility stuff"""
        data = []
        data.append("\n--- BPA ({}) Incentives ----".format(self.__class__.__name__))
        msg = "{:<56} {:<15}{:>10}{:>15}"
        data.append(msg.format("Measure", "Savings (kWh)", "Rate ", "Payment"))
        data.append(
            msg.format(
                "Shell Upgrades, incl. Windows",
                self.round2__reported_shell_windows_kwh_savings,
                self.round2d__long_incentive,
                self.round2d__reported_shell_windows_incentive,
            )
        )
        data.append(
            msg.format(
                "HVAC and Water Heat Upgrades",
                self.round2__reported_hvac_waterheater_kwh_savings,
                self.round2d__medium_incentive,
                self.round2d__reported_hvac_waterheater_incentive,
            )
        )
        _msg = "Lighting, incl. Fixtures, Showerheads, and Smart Tstats"
        if self.program == "neea-bpa-v3":
            _msg = "Smart Tstats"
        data.append(
            msg.format(
                _msg,
                self.round2__reported_lighting_showerhead_tstats_kwh_savings,
                self.round2d__short_incentive,
                self.round2d__reported_lighting_showerhead_tstats_incentive,
            )
        )
        data.append("")

        msg = "{:<46} {:<10}{:<15}{:>10}{:>15}"
        data.append(msg.format("Measure", "Life", "Savings (kWh)", "Rate ", "Payment"))
        data.append(
            msg.format(
                "HVAC",
                "15",
                self.round2__bpa_hvac_kwh_savings,
                self.round2d__medium_incentive,
                self.round2d__hvac_kwh_incentive,
            )
        )
        if self.program == "neea-bpa":
            data.append(
                msg.format(
                    "Lighting",
                    "12",
                    self.round2__bpa_lighting_kwh_savings,
                    self.round2d__short_incentive,
                    self.round2d__lighting_kwh_incentive,
                )
            )
        data.append(
            msg.format(
                "Water Heating",
                "13",
                self.round2__bpa_water_heater_kwh_savings,
                self.round2d__medium_incentive,
                self.round2d__water_heater_kwh_incentive,
            )
        )
        data.append(
            msg.format(
                "Appliances & Other Electronics",
                "15",
                self.round2__bpa_appliance_kwh_savings,
                self.round2d__medium_incentive,
                self.round2d__appliance_kwh_incentive,
            )
        )
        data.append(
            msg.format(
                "Windows & Other Shell",
                "45",
                self.round2__bpa_windows_shell_kwh_savings,
                self.round2d__long_incentive,
                self.round2d__windows_shell_kwh_incentive,
            )
        )
        if self.program == "neea-bpa":
            data.append(
                msg.format(
                    "Low Flow Shower Head",
                    "5",
                    self.round2__bpa_showerhead_kwh_savings,
                    self.round2d__short_incentive,
                    self.round2d__showerhead_kwh_incentive,
                )
            )
        data.append(
            msg.format(
                "Smart Thermostat",
                "5",
                self.round2__bpa_smart_thermostat_kwh_savings,
                self.round2d__short_incentive,
                self.round2d__smart_thermostat_kwh_incentive,
            )
        )
        data.append("")

        msg = "{:<30}{:<8}{:<20}"
        data.append(
            msg.format(
                "Percent Improvement",
                self.round2p__percent_improvement,
                "*Alt Method" if self.use_revised_pct_improvement else "",
            )
        )
        data.append("")

        msg = "{:<20}{:<20}{:<20}{:<15}{:>20}"
        data.append(
            msg.format(
                "Reference Home kWh",
                "As-Built Home kWh",
                "Savings kWh",
                "Achieved Incentive",
                "Total BPA Payment",
            )
        )
        data.append(
            msg.format(
                self.round2__reference_home_kwh,
                self.round2__busbar_consumption,
                self.round2__busbar_savings,
                "Yes" if self.has_bpa_incentive else "No",
                self.round2d__total_incentive,
            )
        )

        data += self.utility_report()

        data.append("")
        msg = "{:<20}{:<20}{:<20}"
        data.append(msg.format("Builder Incentive", "", self.round2d__builder_incentive))

        return "\n".join(data)

    def data(self):
        """Data"""
        return OrderedDict(
            [
                ("has_incentive", self.has_incentive),
                ("busbar_consumption", self.busbar_consumption),
                ("busbar_savings", self.busbar_savings),
                ("pct_improvement_method", self.pct_improvement_method),
                ("pretty_pct_improvement_method", self.pct_improvement_method.capitalize()),
                ("required_pct_improvement", self.required_pct_improvement),
                ("percent_improvement", self.percent_improvement),
                ("pretty_percent_improvement", self.round1p__percent_improvement),
                ("revised_percent_improvement", self.revised_percent_improvement),
                ("pretty_revised_percent_improvement", self.round1p__revised_percent_improvement),
                ("total_incentive", self.total_incentive),
                ("pretty_total_incentive", self.round2d__total_incentive),
                ("builder_incentive", self.builder_incentive),
                ("pretty_builder_incentive", self.round2d__builder_incentive),
                ("bpa_hvac_kwh_savings", self.bpa_hvac_kwh_savings),
                ("hvac_kwh_incentive", self.hvac_kwh_incentive),
                ("bpa_lighting_kwh_savings", self.bpa_lighting_kwh_savings),
                ("lighting_kwh_incentive", self.lighting_kwh_incentive),
                ("bpa_water_heater_kwh_savings", self.bpa_water_heater_kwh_savings),
                ("water_heater_kwh_incentive", self.water_heater_kwh_incentive),
                ("bpa_appliance_kwh_savings", self.bpa_appliance_kwh_savings),
                ("appliance_kwh_incentive", self.appliance_kwh_incentive),
                ("bpa_windows_shell_kwh_savings", self.bpa_windows_shell_kwh_savings),
                ("windows_shell_kwh_incentive", self.windows_shell_kwh_incentive),
                ("bpa_showerhead_kwh_savings", self.bpa_showerhead_kwh_savings),
                ("showerhead_kwh_incentive", self.showerhead_kwh_incentive),
                ("bpa_smart_thermostat_kwh_savings", self.bpa_smart_thermostat_kwh_savings),
                ("smart_thermostat_kwh_incentive", self.smart_thermostat_kwh_incentive),
                ("incentive_paying_organization", self.incentive_paying_organization),
            ]
        )
