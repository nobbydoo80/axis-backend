"""calculator.py: Django EPS Calculator"""


import logging
import math
from collections import OrderedDict

from .base import BaseEPSCalculator
from .. import ETO_GEN2
from ..base import EPSBase
from ..incentives import Incentives2019, Incentives2018, Incentives2017, Incentives, Incentives2020
from ..net_zero import ETO2020NetZero, NetZero
from ..projected import Projected

__author__ = "Steven K"
__date__ = "08/21/2019 16:15"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

log = logging.getLogger(__name__)


class EPSCalculator(BaseEPSCalculator, EPSBase):  # pylint: disable=too-many-public-methods
    """EPS Calculator the center of ETO"""

    @property
    def _calculation_data(self):
        return dict(
            constants=self.constants,
            location=self.location,
            electric_utility=self.electric_utility,
            gas_utility=self.gas_utility,
            program=self.program,
            smart_thermostat=self.smart_thermostat,
            smart_thermostat_furnace_type=self.smart_thermostat_furnace_type,
            qty_shower_head_1p5=self.qty_shower_head_1p5,
            qty_shower_head_1p6=self.qty_shower_head_1p6,
            qty_shower_head_1p75=self.qty_shower_head_1p75,
            qty_shower_wand_1p5=self.qty_shower_wand_1p5,
            us_state=self.us_state,
            generated_solar_pv_kwh=self.generated_solar_pv_kwh,
            has_gas_fireplace=self.has_gas_fireplace,
            grid_harmonization_elements=self.grid_harmonization_elements,
            smart_thermostat_brand=self.smart_thermostat_brand,
            eps_additional_incentives=self.eps_additional_incentives,
        )

    @property
    def code_calculations(self):
        """Code calculations"""
        return self.code_data.get_calculations(**self._calculation_data)

    @property
    def improved_calculations(self):
        """Imporoved calculations"""
        return self.improved_data.get_calculations(**self._calculation_data)

    @property
    def code_total_therms(self):
        """Code home total therms"""
        addr = 0.0
        if self.program in ETO_GEN2 and self.us_state == "WA" and self.code_data.hot_water_kwh > 0:
            addr = 124.0
        if self.heat_type == "gas heat":
            return self.code_calculations.consumption_gas_heat_total_therms + addr
        return self.code_calculations.consumption_heat_pump_total_therms + addr

    @property
    def improved_total_therms(self):
        """Improved home total therms"""
        addr = 0.0
        if self.program in ETO_GEN2 and self.us_state == "WA" and self.code_data.hot_water_kwh > 0:
            addr = 124.0
        if self.heat_type == "gas heat":
            return self.improved_calculations.consumption_gas_heat_total_therms + addr
        return self.improved_calculations.consumption_heat_pump_total_therms + addr

    def _get_alternate_method_total_mbtu(self):
        """Crunch the total mBtu manually"""
        therms_savings = self.therms_to_mbtu(self.code_total_therms - self.improved_total_therms)
        kwh_savings = self.kwh_to_mbtu(self.code_total_kwh - self.improved_total_kwh)
        return therms_savings + kwh_savings

    def get_alternate_method_therms_savings(self):
        """Get the therm savings allocation based off a % of total"""
        value = self._get_alternate_method_total_mbtu()
        value *= self.constants.ALTERNATE_METHOD_GAS_SAVINGS_ALLOCATION
        return self.mbtu_to_therms(value)

    def get_alternate_method_kwh_savings(self):
        """Gets the therms savings"""
        value = self._get_alternate_method_total_mbtu()
        value *= self.constants.ALTERNATE_METHOD_ELECTRIC_SAVINGS_ALLOCATION
        return self.mbtu_to_kwh(value)

    @property
    def therms_savings(self):
        """Final Therm Savings"""
        if self.use_alternate_allocation_method:
            return self.get_alternate_method_therms_savings()
        return self.code_total_therms - self.improved_total_therms

    @property
    def therms_pct_improvement(self):
        """Final Therm % improvement"""
        if self.therms_savings > 0:
            return self.therms_savings / self.code_total_therms
        return 0.0

    @property
    def code_total_kwh(self):
        """Code total kWh"""
        if self.heat_type == "gas heat":
            return self.code_calculations.consumption_gas_heat_total_kwh
        return self.code_calculations.consumption_heat_pump_total_kwh

    @property
    def improved_total_kwh(self):
        """Improved total kWh"""
        # TODO SUSPECTED BUG!  # Email on 12/23/19 from Julia says this ok..?
        if self.program != "eto-2020":
            if self.heat_type == "gas heat":
                return self.improved_calculations.consumption_gas_heat_total_kwh
        return self.improved_calculations.consumption_heat_pump_total_kwh

    @property
    def kwh_savings(self):
        """Final kWh Savings"""
        if self.use_alternate_allocation_method:
            return self.get_alternate_method_kwh_savings()
        return self.code_total_kwh - self.improved_total_kwh

    @property
    def kwh_pct_improvement(self):
        """Final kWh % improvement"""
        if self.kwh_savings > 0:
            return self.kwh_savings / self.code_total_kwh
        return 0.0

    @property
    def percentage_generation_kwh(self):
        """Percentage of kwn generated"""
        if self.generated_solar_pv_kwh == 0.0:
            return 0.0
        value = self.generated_solar_pv_kwh / self.improved_total_kwh
        return max(1, value)

    def is_eto_2020_zerod(self):
        """If ETO-2020 and not partial we zero this.."""
        parital_territory = (
            "gas" in "%s" % self.heat_type and "other" not in "%s" % self.gas_utility
        )
        if self.program == "eto-2020" and self.electric_utility == "other/none":
            return not parital_territory
        return False

    @property
    def code_total_mbtu(self):
        """Code total mBtu"""
        if self.is_eto_2020_zerod():
            return 0.0
        return self.therms_to_mbtu(self.code_total_therms) + self.kwh_to_mbtu(self.code_total_kwh)

    @property
    def improved_total_mbtu(self):
        """Improved total mBtu"""
        if self.is_eto_2020_zerod():
            return 0.0
        value = self.therms_to_mbtu(self.improved_total_therms)
        value += self.kwh_to_mbtu(self.improved_total_kwh)
        return value

    @property
    def mbtu_savings(self):
        """Total mBtu Savings"""
        if self.is_eto_2020_zerod():
            return 0.0
        return self.therms_to_mbtu(self.therms_savings) + self.kwh_to_mbtu(self.kwh_savings)

    @property
    def code_therm_savings(self):
        """Code therm Savings"""
        if self.heat_type == "gas heat":
            value = self.code_calculations.eps_gas_heat_total_therms
        else:
            value = self.code_calculations.eps_heat_pump_total_therms
        if self.program not in ETO_GEN2 and self.us_state == "WA" and not self.has_gas_hot_water:
            value += 98.0
        return value

    @property
    def improved_therm_savings(self):
        """Improved therm Savings"""
        if self.heat_type == "gas heat":
            value = self.improved_calculations.eps_gas_heat_total_therms
        else:
            value = self.improved_calculations.eps_heat_pump_total_therms
        if self.program not in ETO_GEN2 and self.us_state == "WA" and not self.has_gas_hot_water:
            value += 98.0
        return value

    @property
    def therm_only_percentage_improvement(self):
        """Therm only % improvement"""
        try:
            return (self.code_therm_savings - self.improved_therm_savings) / self.code_therm_savings
        except ZeroDivisionError:
            return 0.0

    @property
    def percentage_improvement(self):
        """Percent Improvement"""
        if self.us_state == "WA":
            if self.program in ETO_GEN2:
                return self.therms_pct_improvement
            return self.therm_only_percentage_improvement
        try:
            return self.mbtu_savings / self.code_total_mbtu
        except ZeroDivisionError:
            return 0.0

    @property
    def floored_percentage_improvement(self):
        """Floored Percent Improvement"""
        return math.floor(self.percentage_improvement * 100) / 100

    @property
    def floored_kwh_percentage_improvement(self):
        """Floored kWh Percent Improvement"""
        return math.floor(self.kwh_pct_improvement * 100) / 100

    @property
    def floored_therm_percentage_improvement(self):
        """Floored therm Percent Improvement"""
        return math.floor(self.therms_pct_improvement * 100) / 100

    def calculations_report(self):
        """Report"""
        data = []
        data.append("\n--- Calculations ----")
        msg = "{:<25} {:^15}{:^15}{:^15}{:^15}"
        data.append(msg.format("", "Code", "Improved", "Savings", "% Better"))
        data.append(
            msg.format(
                "Total Therms",
                self.round4__code_total_therms,
                self.round4__improved_total_therms,
                self.round4__therms_savings,
                self.round4p__therms_pct_improvement,
            )
        )
        data.append(
            msg.format(
                "Total kWh",
                self.round4__code_total_kwh,
                self.round4__improved_total_kwh,
                self.round4__kwh_savings,
                self.round4p__kwh_pct_improvement,
            )
        )
        data.append(
            msg.format(
                "Total Mbtu",
                self.round4__code_total_mbtu,
                self.round4__improved_total_mbtu,
                self.round4__mbtu_savings,
                "",
            )
        )
        data.append(
            msg.format("", "", "", "% Better than code", self.round4p__percentage_improvement)
        )
        return "\n".join(data)

    @property
    def calculations_data(self):
        """Calculations Data"""
        return OrderedDict(
            [
                (
                    "code",
                    OrderedDict(
                        [
                            ("total_therms", self.code_total_therms),
                            ("total_kwh", self.code_total_kwh),
                            ("total_mbtu", self.code_total_mbtu),
                        ]
                    ),
                ),
                (
                    "improved",
                    OrderedDict(
                        [
                            ("total_therms", self.improved_total_therms),
                            ("total_kwh", self.improved_total_kwh),
                            ("total_mbtu", self.improved_total_mbtu),
                        ]
                    ),
                ),
                (
                    "savings",
                    OrderedDict(
                        [
                            ("therms", self.therms_savings),
                            ("kwh", self.kwh_savings),
                            ("mbtu", self.mbtu_savings),
                        ]
                    ),
                ),
                (
                    "pct_improvement",
                    OrderedDict(
                        [
                            ("therms", self.therms_pct_improvement),
                            ("kwh", self.kwh_pct_improvement),
                        ]
                    ),
                ),
                ("percentage_generation_kwh", self.percentage_generation_kwh),
                ("percentage_improvement", self.percentage_improvement),
                ("floored_percentage_improvement", self.floored_percentage_improvement),
                ("floored_kwh_percentage_improvement", self.floored_kwh_percentage_improvement),
                ("floored_therm_percentage_improvement", self.floored_therm_percentage_improvement),
            ]
        )

    @property
    def eps_score(self):
        """EPS Score"""
        if self.heat_type == "gas heat":
            return max(self.improved_calculations.eps_gas_heat_total_mbtu, 0)
        return max(self.improved_calculations.eps_heat_pump_total_mbtu, 0)

    @property
    def code_eps_score(self):
        """Code EPS Score"""
        if self.heat_type == "gas heat":
            return max(self.code_calculations.eps_gas_heat_total_mbtu, 0)
        return max(self.code_calculations.eps_heat_pump_total_mbtu, 0)

    @property
    def carbon_score(self):
        """Carbon Score"""
        if self.heat_type == "gas heat":
            return max(self.improved_calculations.carbon_gas_heat_score, 0)
        return max(self.improved_calculations.carbon_heat_pump_score, 0)

    @property
    def code_carbon_score(self):
        """Code Carbon Score"""
        if self.heat_type == "gas heat":
            return max(self.code_calculations.carbon_gas_heat_score, 0)
        return max(self.code_calculations.carbon_heat_pump_score, 0)

    @property
    def total_electric_carbon(self):
        """Total Electric Carbon"""
        if self.heat_type == "gas heat":
            return self.improved_calculations.carbon_gas_heat_total_kwh
        return self.improved_calculations.carbon_heat_pump_total_kwh

    @property
    def total_gas_carbon(self):
        """Total Therm Carbon"""
        if self.heat_type == "gas heat":
            return self.improved_calculations.carbon_gas_heat_total_therms
        return self.improved_calculations.carbon_heat_pump_total_therms

    @property
    def estimated_annual_cost(self):
        """Estimated annual cost"""
        return max(0, sum([self.improved_data.gas_cost, self.improved_data.electric_cost]))

    @property
    def estimated_monthly_cost(self):
        """Estimated monthly cost"""
        return self.estimated_annual_cost / 12.0

    @property
    def home_subtype(self):
        """
        =IF(AND('Input-2017'!B21>1,'Input-2017'!E21>1),"GH+GW",
        IF(AND('Input-2017'!B21<1,'Input-2017'!F21>1),"EH+EW",
        IF(AND('Input-2017'!B21>1,'Input-2017'!F21>1),"GH+EW",
        IF(AND('Input-2017'!B21<1,'Input-2017'!E21>1),"EH+GW",
        "other"))))

        """
        if self.improved_data.heating_therms > 1.0 and self.improved_data.hot_water_therms > 1.0:
            return "GH+GW"
        if self.improved_data.heating_therms < 1.0 and self.improved_data.hot_water_kwh > 1.0:
            return "EH+EW"
        if self.improved_data.heating_therms > 1.0 and self.improved_data.hot_water_kwh > 1.0:
            return "GH+EW"
        if self.improved_data.heating_therms < 1.0 and self.improved_data.hot_water_therms > 1.0:
            return "EH+GW"
        return "other"

    @property
    def use_alternate_allocation_method(self):
        """Should we use alternate allocation method"""

        use_alt_method = False
        # New change to the 2020 program
        if self.program == "eto-2020":
            from axis.customer_eto.enumerations import ETO_2020_BUILDER_CHOICES

            valid_builder = self.builder == ETO_2020_BUILDER_CHOICES[0][0]
            valid_primary_heat_type = self.primary_heat_type.lower() == "gas furnace"
            valid_hpwh = self.hot_water_ef > 2.0
            use_alt_method = all([valid_builder, valid_primary_heat_type, valid_hpwh])
        elif self.improved_data.gas_furnace_afue and self.improved_data.gas_furnace_afue < 94.0:
            use_alt_method = self.home_subtype == "GH+EW" and self.hot_water_ef > 2.0

        if self.program in ["eto-2016", "eto-2017", "eto-2018"] or self.us_state != "OR":
            return False

        return use_alt_method

    @property
    def net_zero(self):
        kwargs = dict(
            constants=self.constants,
            electric_utility=self.electric_utility,
            improved_total_therms=self.improved_total_therms,
            therms_pct_improvement=self.therms_pct_improvement,
            percentage_improvement=self.percentage_improvement,
            pv_kwh_unadjusted=self.improved_data.pv_kwh,
            improved_total_kwh=self.improved_total_kwh,
            grid_harmonization_elements=self.grid_harmonization_elements,
            smart_thermostat_brand=self.smart_thermostat_brand,
            eps_additional_incentives=self.eps_additional_incentives,
            primary_heat_type=self.primary_heat_type,
            improved_cooling_kwh=self.improved_data.cooling_kwh,
            solar_elements=self.solar_elements,
        )
        if self.program == "eto-2020":
            return ETO2020NetZero(**kwargs)
        return NetZero(**kwargs)

    @property
    def incentives(self):
        """Incentive"""
        if self.program == "eto-2020":
            return Incentives2020(
                constants=self.constants,
                heating_therms=self.improved_data.heating_therms,
                hot_water_therms=self.improved_data.hot_water_therms,
                us_state=self.us_state,
                hot_water_kwh=self.improved_data.hot_water_kwh,
                electric_utility=self.electric_utility,
                gas_utility=self.gas_utility,
                heat_type=self.heat_type,
                pathway=self.pathway,
                percentage_improvement=self.percentage_improvement,
                has_heat_pump_water_heater=self.has_heat_pump_water_heater,
                hot_water_ef=self.hot_water_ef,
                home_subtype=self.home_subtype,
                use_alternate_allocation_method=self.use_alternate_allocation_method,
                net_zero=self.net_zero,
            )
        elif self.program == "eto-2019":
            return Incentives2019(
                constants=self.constants,
                heating_therms=self.improved_data.heating_therms,
                hot_water_therms=self.improved_data.hot_water_therms,
                us_state=self.us_state,
                hot_water_kwh=self.improved_data.hot_water_kwh,
                electric_utility=self.electric_utility,
                gas_utility=self.gas_utility,
                heat_type=self.heat_type,
                pathway=self.pathway,
                percentage_improvement=self.percentage_improvement,
                has_heat_pump_water_heater=self.has_heat_pump_water_heater,
                hot_water_ef=self.hot_water_ef,
                home_subtype=self.home_subtype,
                use_alternate_allocation_method=self.use_alternate_allocation_method,
            )
        elif self.program == "eto-2018":
            return Incentives2018(
                constants=self.constants,
                heating_therms=self.improved_data.heating_therms,
                hot_water_therms=self.improved_data.hot_water_therms,
                us_state=self.us_state,
                hot_water_kwh=self.improved_data.hot_water_kwh,
                electric_utility=self.electric_utility,
                gas_utility=self.gas_utility,
                heat_type=self.heat_type,
                pathway=self.pathway,
                home_subtype=self.home_subtype,
                percentage_improvement=self.percentage_improvement,
            )
        elif self.program == "eto-2017":
            return Incentives2017(
                constants=self.constants,
                heating_therms=self.improved_data.heating_therms,
                hot_water_therms=self.improved_data.hot_water_therms,
                us_state=self.us_state,
                hot_water_kwh=self.improved_data.hot_water_kwh,
                electric_utility=self.electric_utility,
                gas_utility=self.gas_utility,
                heat_type=self.heat_type,
                pathway=self.pathway,
                home_subtype=self.home_subtype,
                percentage_improvement=self.percentage_improvement,
            )
        return Incentives(
            constants=self.constants,
            electric_utility=self.electric_utility,
            gas_utility=self.gas_utility,
            us_state=self.us_state,
            heat_type=self.heat_type,
            has_gas_water_heater=self.has_gas_hot_water,
            has_tankless_water_heater=self.has_tankless_water_heater,
            hot_water_ef=self.hot_water_ef,
            pathway=self.pathway,
            percentage_improvement=self.percentage_improvement,
        )

    @property
    def total_verifier_incentive(self):
        """Verifier Incentive"""
        return self.incentives.verifier_incentive

    @property
    def total_builder_incentive(self):
        """Builder Incentive"""
        return self.incentives.builder_incentive

    @property
    def projected(self):
        """Projected data"""
        return Projected(
            constants=self.constants,
            electric_utility=self.electric_utility,
            gas_utility=self.gas_utility,
            heat_type=self.heat_type,
            conditioned_area=self.conditioned_area,
            location=self.location,
            us_state=self.us_state,
        )

    @property
    def projected_size_or_home_eps(self):
        """Projected Size or home EPS"""
        return self.projected.projected_size_or_home_eps

    @property
    def projected_size_or_home_carbon(self):
        """Projected Size or home Carbon Score"""
        return self.projected.projected_size_or_home_carbon

    def output(self):
        """Output data"""
        data = []
        data.append("\n--- Output ----")
        msg = "{:<40} {:<9} {}"
        data.append(msg.format("EPS", self.round4__eps_score, "MBtu"))
        data.append(msg.format("Code Build", self.round4__code_eps_score, "MBtu"))
        data.append(
            msg.format("Percentage Improvement", self.round4p__floored_percentage_improvement, "")
        )
        data.append(msg.format("Incentive", self.round4d__total_builder_incentive, ""))
        data.append(msg.format("Carbon Score", self.round4__carbon_score, "Tons CO2/year"))
        data.append(
            msg.format("Code Carbon Score", self.round4__code_carbon_score, "Tons CO2/year")
        )
        data.append(
            msg.format("Estimated Annual Cost", self.round4d__estimated_annual_cost, "per year")
        )
        data.append(
            msg.format("Estimated Monthly Cost", self.round4d__estimated_monthly_cost, "per month")
        )
        data.append(
            msg.format(
                "Similar Size {} Home EPS".format(self.us_state),
                self.round4__projected_size_or_home_eps,
                "MBtu",
            )
        )
        data.append(
            msg.format(
                "Similar Size {} Home Carbon Score".format(self.us_state),
                self.round4__projected_size_or_home_carbon,
                "Tons CO2/year",
            )
        )
        return "\n".join(data)

    @property
    def output_report(self):
        """Output Report"""
        return OrderedDict(
            [
                ("eps_score", self.eps_score),
                ("code_eps_score", self.code_eps_score),
                ("floored_percentage_improvement", self.floored_percentage_improvement),
                ("floored_kwh_percentage_improvement", self.floored_kwh_percentage_improvement),
                ("floored_therm_percentage_improvement", self.floored_therm_percentage_improvement),
                ("total_builder_incentive", self.total_builder_incentive),
                ("carbon_score", self.carbon_score),
                ("code_carbon_score", self.code_carbon_score),
                ("total_electric_carbon", self.total_electric_carbon),
                ("total_gas_carbon", self.total_gas_carbon),
                ("estimated_annual_cost", self.estimated_annual_cost),
                ("estimated_monthly_cost", self.estimated_monthly_cost),
                ("projected_size_or_home_eps", self.projected_size_or_home_eps),
                ("projected_size_or_home_carbon", self.projected_size_or_home_carbon),
            ]
        )

    def dump_simulation(self):
        """Utility to dump the simulatino"""
        data = OrderedDict(
            [
                ("site_address", self.input_site_address),
                ("location", self.location),
                ("us_state", self.us_state),
            ]
        )

        if self.program in [None, "eto", "eto-2016", "eto-2017", "eto-2018", "eto-2019"]:
            data["heat_type"] = self.heat_type
        else:
            data["primary_heating_equipment_type"] = self.primary_heat_type

        data.update(
            **OrderedDict(
                [
                    ("pathway", self.input_pathway),
                    ("conditioned_area", self.input_conditioned_area),
                    ("program", self.program),
                    ("electric_utility", self.electric_utility),
                    ("gas_utility", self.gas_utility),
                ]
            )
        )

        if self.program not in [None, "eto", "eto-2016", "eto-2017", "eto-2018", "eto-2019"]:
            data["builder"] = self.builder

        data.update(
            **OrderedDict(
                [
                    ("hot_water_ef", self.hot_water_ef),
                    ("has_tankless_water_heater", self.has_tankless_water_heater),
                    ("has_solar_hot_water", self.has_solar_hot_water),
                    ("has_ashp", self.improved_data.has_ashp),
                ]
            )
        )

        if self.program in [None, "eto", "eto-2016", "eto-2017", "eto-2018", "eto-2019"]:
            data["qualifying_thermostat"] = self.input_qualifying_thermostat
        else:
            data["smart_thermostat_brand"] = self.smart_thermostat_brand

        if self.program in ["eto-2017", "eto-2018"]:
            data.update(
                **OrderedDict(
                    [
                        ("qty_shower_head_1p5", self.input_qty_shower_head_1p5),
                        ("qty_shower_head_1p6", self.input_qty_shower_head_1p6),
                        ("qty_shower_head_1p75", self.input_qty_shower_head_1p75),
                        ("qty_shower_wand_1p5", self.input_qty_shower_wand_1p5),
                    ]
                )
            )

        if self.program not in ["eto-2015", "eto-2016", "eto-2017", "eto-2018"]:
            data["generated_solar_pv_kwh"] = self.input_generated_solar_pv_kwh
            data["has_heat_pump_water_heater"] = self.has_heat_pump_water_heater

        if self.program not in ["eto-2015", "eto-2016", "eto-2017", "eto-2018", "eto-2019"]:
            data["gas_furnace_afue"] = self.improved_data.gas_furnace_afue
            data["grid_harmonization_elements"] = self.input_grid_harmonization_elements
            data["smart_thermostat_brand"] = self.input_smart_thermostat_brand
            data["eps_additional_incentives"] = self.input_eps_additional_incentives
            data["has_gas_fireplace"] = self.input_has_gas_fireplace
            data["solar_elements"] = self.input_solar_elements

        nub_data = OrderedDict(
            [
                (
                    "code_data",
                    OrderedDict(
                        [
                            ("heating_therms", self.code_data.heating_therms),
                            ("heating_kwh", self.code_data.heating_kwh),
                            ("cooling_kwh", self.code_data.cooling_kwh),
                            ("hot_water_therms", self.code_data.hot_water_therms),
                            ("hot_water_kwh", self.code_data.hot_water_kwh),
                            (
                                "lights_and_appliances_therms",
                                self.code_data.lights_and_appliances_therms,
                            ),
                            ("lights_and_appliances_kwh", self.code_data.lights_and_appliances_kwh),
                            ("electric_cost", self.code_data.electric_cost),
                            ("gas_cost", self.code_data.gas_cost),
                        ]
                    ),
                ),
                (
                    "improved_data",
                    OrderedDict(
                        [
                            ("heating_therms", self.improved_data.heating_therms),
                            ("heating_kwh", self.improved_data.heating_kwh),
                            ("cooling_kwh", self.improved_data.cooling_kwh),
                            ("hot_water_therms", self.improved_data.hot_water_therms),
                            ("hot_water_kwh", self.improved_data.hot_water_kwh),
                            (
                                "lights_and_appliances_therms",
                                self.improved_data.lights_and_appliances_therms,
                            ),
                            (
                                "lights_and_appliances_kwh",
                                self.improved_data.lights_and_appliances_kwh,
                            ),
                            ("pv_kwh", self.improved_data.pv_kwh),
                            ("solar_hot_water_therms", self.improved_data.solar_hot_water_therms),
                            ("solar_hot_water_kwh", self.improved_data.solar_hot_water_kwh),
                            ("electric_cost", self.improved_data.electric_cost),
                            ("gas_cost", self.improved_data.gas_cost),
                        ]
                    ),
                ),
            ]
        )

        data.update(nub_data)

        import json

        return json.dumps(data, indent=4)

    def dump_exel(self):
        """Dump the Excel contents"""
        data = [
            self.code_data.heating_therms,
            self.code_data.heating_kwh,
            self.code_data.cooling_kwh,
            self.code_data.hot_water_therms,
            self.code_data.hot_water_kwh,
            self.code_data.lights_and_appliances_therms,
            self.code_data.lights_and_appliances_kwh,
            "",
            "",
            self.code_data.electric_cost,
            self.code_data.gas_cost,
        ]
        print("\t".join(["{}".format(x) for x in data]))

        data = [
            self.improved_data.heating_therms,
            self.improved_data.heating_kwh,
            self.improved_data.cooling_kwh,
            self.improved_data.hot_water_therms,
            self.improved_data.hot_water_kwh,
            self.improved_data.lights_and_appliances_therms,
            self.improved_data.lights_and_appliances_kwh,
            self.improved_data.pv_kwh,
            "",
            "",
            self.improved_data.electric_cost,
            self.improved_data.gas_cost,
        ]
        print("\t".join(["{}".format(x) for x in data]))

    def report_data(self, include_formated_data=False):
        """Report"""
        data = OrderedDict(
            [
                ("inputs", self.input_report_data),
                ("code_input", self.code_data.report_data),
                ("improved_input", self.improved_data.report_data),
                ("calculations", self.calculations_data),
                ("similar", self.projected.report_data),
                ("incentive", self.incentives.report_data),
                ("net_zero", self.incentives.net_zero_report_data),
                ("result", self.output_report),
                ("version", "20200420"),
            ]
        )
        if include_formated_data:
            data["inputs_report"] = self.report()
            data["code_input_report"] = self.code_data.report()
            data["improved_input_report"] = self.improved_data.report(show_header=False)
            data["code_calculator_report"] = self.code_data.report()
            data["calculator_report"] = self.improved_calculations.report()
            data["calculations_report"] = self.calculations_report()
            data["similar_report"] = self.projected.report()
            data["incentive_report"] = self.incentives.report()
            data["net_zero"] = self.incentives.net_zero_report()
            data["result_report"] = self.output()
            data["input_json"] = self.dump_simulation()
        return data
