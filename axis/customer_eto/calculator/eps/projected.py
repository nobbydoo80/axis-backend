"""projected: Django eps"""


import logging

from collections import OrderedDict

try:
    from .base import EPSBase
except (ValueError, ImportError):
    from axis.customer_eto.calculator.eps import EPSBase

__author__ = "Steven Klass"
__date__ = "11/3/16 08:37"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class Projected(EPSBase):
    """Provides all of the projected costs and carbon stuff"""

    def __init__(self, **kwargs):
        self.constants = kwargs.get("constants")
        self.location = self.constants.LOCATION_TRANSLATION.get(
            kwargs.get("location"), kwargs.get("location")
        )
        self.heat_type = kwargs.get("heat_type")
        self.conditioned_area = kwargs.get("conditioned_area")
        self.electric_utility = kwargs.get("electric_utility")
        self.gas_utility = kwargs.get("gas_utility")
        self.us_state = kwargs.get("us_state") or "OR"

        similar_size_reg = self.constants.EPS_SIMILAR_SIZE_REGRESSIVE_VALUES
        regressive_values = next((x for x in similar_size_reg if x["location"] == self.location))
        self.regressive_values = regressive_values["regression_values"]

        carbon_reg_constants = self.constants.EPS_SIMILAR_SIZE_CARBON_REGRESSIVE_VALUES
        carbon_values = next((x for x in carbon_reg_constants if x["location"] == self.location))
        self.carbon_values = carbon_values["regression_values"]

    @property
    def projected_electric_kwh(self):
        """Projected electric kWh"""
        if self.heat_type == "gas heat":
            return 0.0
        return self.regressive_values["electric_home_kwh"]["constant"] + (
            self.regressive_values["electric_home_kwh"]["slope"] * float(self.conditioned_area)
        )

    @property
    def projected_electric_mbtu(self):
        """Projected electric mBtu"""
        return self.kwh_to_mbtu(self.projected_electric_kwh)

    @property
    def projected_carbon_electric_kwh(self):
        """Projected carbon electric kWh"""
        if self.heat_type == "gas heat":
            return 0.0
        return self.carbon_values["electric_home_kwh"]["constant"] + (
            self.carbon_values["electric_home_kwh"]["slope"] * float(self.conditioned_area)
        )

    @property
    def projected_carbon_electric_mbtu(self):
        """Projected carbon electric mBtu"""
        return self.kwh_to_mbtu(self.projected_carbon_electric_kwh)

    @property
    def projected_gas_kwh(self):
        """Projected carbon gas kWh"""
        if self.heat_type != "gas heat":
            return 0.0
        value = self.regressive_values["gas_home_kwh"]["constant"]
        val = self.regressive_values["gas_home_kwh"]["slope"] * float(self.conditioned_area)
        value += val
        return value

    @property
    def projected_gas_mbtu(self):
        """Projected carbon gas mBtu"""
        return self.kwh_to_mbtu(self.projected_gas_kwh)

    @property
    def projected_gas_therms(self):
        """Projected gas therms"""
        if self.heat_type != "gas heat":
            return 0.0
        value = self.regressive_values["gas_home_therms"]["constant"]
        val = self.regressive_values["gas_home_therms"]["slope"] * float(self.conditioned_area)
        value += val
        return value

    @property
    def projected_gas_therms_mbtu(self):
        """Projected gas mBtu"""
        return self.therms_to_mbtu(self.projected_gas_therms)

    @property
    def projected_carbon_gas_kwh(self):
        """Projected carbon gas kWh"""
        if self.heat_type != "gas heat":
            return 0.0
        value = self.carbon_values["gas_home_kwh"]["constant"]
        val = self.carbon_values["gas_home_kwh"]["slope"] * float(self.conditioned_area)
        value += val
        return value

    @property
    def projected_carbon_gas_mbtu(self):
        """Projected carbon gas mBtu"""
        return self.kwh_to_mbtu(self.projected_carbon_gas_kwh)

    @property
    def projected_carbon_gas_therms(self):
        """Projected carbon gas therms"""
        if self.heat_type != "gas heat":
            return 0.0
        value = self.carbon_values["gas_home_therms"]["constant"]
        val = self.carbon_values["gas_home_therms"]["slope"] * float(self.conditioned_area)
        value += val
        return value

    @property
    def projected_carbon_gas_therms_mbtu(self):
        """Projected carbon gas mBtu"""
        return self.therms_to_mbtu(self.projected_carbon_gas_therms)

    @property
    def projected_size_or_home_eps(self):
        """Projected size or home EPS"""
        value = self.projected_electric_mbtu + self.projected_gas_mbtu
        value += self.projected_gas_therms_mbtu
        return value

    @property
    def projected_electric_carbon_score(self):
        """Projected electric carbon score"""
        elec_u = self.electric_utility if self.electric_utility != "other/none" else "bpa"
        value = self.projected_carbon_electric_kwh + self.projected_carbon_gas_kwh
        carbon_value = self.constants.EPS_POUNDS_OF_CARBON_PER_KWH_BY_COMPANY_OR[elec_u]
        if self.us_state == "WA":
            carbon_value = self.constants.EPS_POUNDS_OF_CARBON_PER_KWH_BY_COMPANY_WA[elec_u]
        value *= carbon_value
        value /= 2000.00
        return value

    @property
    def projected_gas_carbon_score(self):
        """Projected gas carbon score"""
        value = self.projected_carbon_gas_therms
        carbon_value = self.constants.EPS_POUNDS_OF_CARBON_PER_KWH_BY_COMPANY_OR["natural gas"]
        if self.us_state == "WA":
            carbon_value = self.constants.EPS_POUNDS_OF_CARBON_PER_KWH_BY_COMPANY_WA["natural gas"]
        value *= carbon_value
        value /= 2000.00
        return value

    @property
    def projected_size_or_home_carbon(self):
        """Projected size or home carbon"""
        return self.projected_electric_carbon_score + self.projected_gas_carbon_score

    def report(self):
        """Report"""
        data = []
        data.append("\n--- Projected ----")
        data.append("Projected Energy Consumption - {}".format(self.location))
        msg = "{:25}{}"
        data.append(msg.format("Electric Home - kWh", self.round4__projected_electric_kwh))
        data.append(msg.format("Gas Home - kWh", self.round4__projected_gas_kwh))
        data.append(msg.format("Gas Home - Therms", self.round4__projected_gas_therms))

        data.append("\nProjected EPS in MMBtu")
        data.append(msg.format("Electric Home", self.round4__projected_electric_mbtu))
        data.append(msg.format("Gas Home - Electric", self.round4__projected_gas_mbtu))
        data.append(msg.format("Gas Home - Gas", self.round4__projected_gas_therms_mbtu))
        data.append(
            "\n{:30}{:25}{:10.2f}".format(
                "", "Similar Size Home EPS:", self.round4__projected_size_or_home_eps
            )
        )

        data.append("\nProjected Carbon Score in Short Tons")
        data.append(
            msg.format("Carbon Score - electric", self.round4__projected_electric_carbon_score)
        )
        data.append(msg.format("Carbon Score - gas", self.round4__projected_gas_carbon_score))
        data.append(
            "\n{:30}{:25}{:10.2f}".format(
                "", "Similar Size Home Carbon:", self.round4__projected_size_or_home_carbon
            )
        )
        return "\n".join(data)

    @property
    def report_data(self):
        """Report"""
        return OrderedDict(
            [
                ("projected_electric_kwh", self.projected_electric_kwh),
                ("projected_gas_kwh", self.projected_gas_kwh),
                ("projected_gas_therms", self.projected_gas_therms),
                ("projected_electric_mbtu", self.projected_electric_mbtu),
                ("projected_gas_mbtu", self.projected_gas_mbtu),
                ("projected_gas_therms_mbtu", self.projected_gas_therms_mbtu),
                ("projected_size_or_home_eps", self.projected_size_or_home_eps),
                ("projected_electric_carbon_score", self.projected_electric_carbon_score),
                ("projected_gas_carbon_score", self.projected_gas_carbon_score),
                ("projected_size_or_home_carbon", self.projected_size_or_home_carbon),
            ]
        )
