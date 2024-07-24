"""net_zero.py - Axis"""


import logging

__author__ = "Steven K"
__date__ = "4/14/20 12:48"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

from collections import OrderedDict

from axis.customer_eto.calculator.eps.base import EPSBase

log = logging.getLogger(__name__)


class NetZeroBase(EPSBase):
    """A base class to allow this thing to be used without fear in the calculations"""

    def __init__(self, **kwargs):
        self.constants = kwargs.get("constants")
        self.electric_utility = kwargs.get("electric_utility")
        self.improved_total_therms = kwargs.get("improved_total_therms")
        self.therms_pct_improvement = kwargs.get("therms_pct_improvement")
        self.percentage_improvement = kwargs.get("percentage_improvement")
        self.pv_kwh_unadjusted = kwargs.get("pv_kwh_unadjusted")
        self.improved_total_kwh = kwargs.get("improved_total_kwh")
        self.grid_harmonization_elements = kwargs.get("grid_harmonization_elements")
        self.smart_thermostat_brand = kwargs.get("smart_thermostat_brand")
        self.eps_additional_incentives = kwargs.get("eps_additional_incentives")
        self.primary_heat_type = kwargs.get("primary_heat_type")
        self.solar_elements = kwargs.get("solar_elements")
        self.improved_cooling_kwh = kwargs.get("improved_cooling_kwh", 0)

    @property
    def qualifies_net_zero(self):
        """This is the input line for Net Zero"""
        raise NotImplementedError

    @property
    def qualifies_net_zero_string(self):
        """This is the input line for Net Zero"""
        return "Net Zero" if self.qualifies_net_zero else "No"

    @property
    def grid_harmonization_elements_string(self):
        return self.grid_harmonization_elements if self.grid_harmonization_elements else "None"

    @property
    def smart_thermostat_requirement_met(self):
        raise NotImplementedError

    @property
    def smart_thermostat_requirement_met_string(self):
        return "Yes" if self.smart_thermostat_requirement_met else "No"

    @property
    def solar_exempt(self):
        raise NotImplementedError

    @property
    def solar_exempt_string(self):
        return "Solar exempt" if self.solar_exempt else "No solar exemption"

    @property
    def mini_split_in_use(self):
        raise NotImplementedError

    @property
    def mini_split_in_use_string(self):
        return "Yes" if self.mini_split_in_use else "No"

    @property
    def qualify_for_esh_base(self):
        raise NotImplementedError

    @property
    def qualify_for_esh_base_string(self):
        return "Yes" if self.qualify_for_esh_base else "No"

    @property
    def input_report(self):
        data = "\n------ NZ & ESH Inputs ----\n"
        data += "\n".join(["{:<40}{}".format(k, v) for k, v in self.input_data.items()])
        return data

    @property
    def input_data(self):
        """The input data"""
        return OrderedDict(
            [
                ("Net Zero", self.qualifies_net_zero_string),
                ("Checklist ESH", self.grid_harmonization_elements_string),
                (
                    "ESH Smart Thermostat requirement met?",
                    self.smart_thermostat_requirement_met_string,
                ),
                ("Solar Exempt?", self.solar_exempt_string),
                ("Mini-split for primary heat?", self.mini_split_in_use_string),
                ("Qualifying for ESH base?", self.qualify_for_esh_base_string),
            ]
        )

    @property
    def net_zero_incentive(self):
        """
        =VLOOKUP(
            'Input-2020'!F7,
            'ESH and NZ-2020'!K3:L9,
            2,
            FALSE)
        :return:
        """
        if self.qualifies_net_zero:
            return self.constants.NET_ZERO_INCENTIVE
        return 0.0

    @property
    def base_package_energy_smart_incentive(self):
        return 0.0

    @property
    def storage_ready_energy_smart_incentive(self):
        return 0.0

    @property
    def advanced_wiring_energy_smart_incentive(self):
        return 0.0

    @property
    def energy_smart_home_incentive(self):
        return (
            self.base_package_energy_smart_incentive
            + self.storage_ready_energy_smart_incentive
            + self.advanced_wiring_energy_smart_incentive
        )

    @property
    def incentive(self):
        return self.net_zero_incentive + self.energy_smart_home_incentive


class NetZero(NetZeroBase):
    @property
    def qualifies_net_zero(self):
        return False

    @property
    def smart_thermostat_requirement_met(self):
        return False

    @property
    def solar_exempt(self):
        return False

    @property
    def mini_split_in_use(self):
        return False

    @property
    def qualify_for_esh_base(self):
        return False


class ETO2020NetZero(NetZero):
    @property
    def valid_nz_electric(self):
        return self.electric_utility in ["pacific power", "portland general"]

    @property
    def valid_nz_therms(self):
        return self.improved_total_therms == 0.0 or self.therms_pct_improvement >= 0.2

    @property
    def valid_nz_solar_answer(self):
        if self.solar_elements is not None:
            return "Solar PV".lower() == self.solar_elements.lower()
        return False

    @property
    def valid_nz_pv(self):
        return self.pv_kwh_unadjusted >= self.improved_total_kwh

    @property
    def qualifies_net_zero(self):
        """This is the input line for Net Zero

        =IF(
            AND(
                OR(_ElectricUtility=_PortlandGeneral,_ElectricUtility=_PacificPower),
                OR('Calcs-2020'!C98=0,'Calcs-2020'!E98>=0.2),
                'Calcs-2020'!E101>=0.2,
                'Calcs-2020'!B82>='Calcs-2020'!C99
                ),
            "Net Zero",
            "No")

        """
        valid_pv_ans = self.valid_nz_solar_answer
        valid_electric = self.valid_nz_electric
        valid_therms = self.valid_nz_therms
        valid_pct_improvement = self.percentage_improvement >= 0.2
        valid_pv = self.valid_nz_pv
        return all([valid_electric, valid_therms, valid_pct_improvement, valid_pv, valid_pv_ans])

    @property
    def smart_thermostat_requirement_met(self):
        if "ecobee" in "{}".format(self.smart_thermostat_brand).lower():
            return True
        if "nest" in "{}".format(self.smart_thermostat_brand).lower():
            return True
        return False

    @property
    def solar_exempt(self):
        return "upload solar exemption" in "{}".format(self.eps_additional_incentives).lower()

    @property
    def mini_split_in_use(self):
        return "mini split" in "%s" % "{}".format(self.primary_heat_type).lower()

    @property
    def qualify_for_esh_base(self):
        """
        =IF(
            AND(
                OR(_ElectricUtility=_PacificPower,_ElectricUtility=_PortlandGeneral),
                OR(AND(F9=AF5,E21>0),F11=AG5)),
                AH5,AH6)
        """
        valid_electric = self.electric_utility in ["pacific power", "portland general"]
        valid_thermostat_and_cooling = all(
            [self.smart_thermostat_requirement_met, self.improved_cooling_kwh > 0]
        )
        valid_thermostat_and_cooling_or_mini_split = any(
            [valid_thermostat_and_cooling, self.mini_split_in_use]
        )
        return all([valid_electric, valid_thermostat_and_cooling_or_mini_split])

    @property
    def base_package_energy_smart_incentive(self):
        """
        =IF(
            AND(
                OR('Input-2020'!F8='Input-2020'!AD6,
                    'Input-2020'!F8='Input-2020'!AD7,
                    'Input-2020'!F8='Input-2020'!AD8,
                    'Input-2020'!F8='Input-2020'!AD9),
                'Input-2020'!F12='Input-2020'!AH5),
                200,
                0)
        """
        if "base package" not in "{}".format(self.grid_harmonization_elements).lower():
            return 0.0
        if self.grid_harmonization_elements is None or not self.qualify_for_esh_base:
            return 0.0
        return self.constants.ENERGY_SMART_HOMES_INCENTIVES.get("base_package")

    @property
    def storage_ready_energy_smart_incentive(self):
        """
        =IF(
            AND(L6>0,
                'Input-2020'!F10='Input-2020'!AE6,  # No Solar
                OR('Input-2020'!F8='Input-2020'!AD7,'Input-2020'!F8='Input-2020'!AD9)),
                150,0)
        """
        if not self.base_package_energy_smart_incentive:
            return 0.0
        if self.solar_exempt:
            return 0.0
        if "storage ready" not in "{}".format(self.grid_harmonization_elements).lower():
            return 0.0
        return self.constants.ENERGY_SMART_HOMES_INCENTIVES.get("storage_ready")

    @property
    def advanced_wiring_energy_smart_incentive(self):
        """
        =IF(
            AND(L6>0,
                OR('Input-2020'!F8='Input-2020'!AD8,'Input-2020'!F8='Input-2020'!AD9)),
                150,0)
        """
        if not self.base_package_energy_smart_incentive:
            return 0.0
        if "advanced wiring" not in "{}".format(self.grid_harmonization_elements).lower():
            return 0.0
        return self.constants.ENERGY_SMART_HOMES_INCENTIVES.get("advanced_wiring")
