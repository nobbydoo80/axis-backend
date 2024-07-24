"""neea_calculator.py: Django NEEA Standard Protocal Calculator"""


import json
import logging
from collections import OrderedDict

from .rtf_calculator import RTFCalculator
from ..base import RTFInputException
from ..data_models import NEEARemModeledInput, NEEASimulatedInput, NEEASimModeledInput
from ..incentives import (
    BPAIncentivesCalculator,
    ClarkIncentivesCalculator,
    BentonREAIncentivesCalculator,
    PugetIncentivesCalculator,
    CentralIncentivesCalculator,
    PacificPowerIncentivesCalculator,
    IdahoPowerIncentivesCalculator,
    InlandPowerCalculator,
    UtilityCityOfRichlandIncentivesCalculator,
    EWEBCalculator,
    TacomaPowerIncentivesCalculator,
    PeninsulaPowerIncentivesCalculator,
)

__author__ = "Steven K"
__date__ = "08/20/2019 07:50"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

log = logging.getLogger(__name__)


class NEEAV2Calculator(RTFCalculator):  # pylint: disable=too-many-public-methods
    """Main NEEA V2 Standard Protocol calculator"""

    def __init__(self, **kwargs):
        kwargs["raise_issues"] = kwargs.get("raise_issues", False)

        super(RTFCalculator, self).__init__(**kwargs)  # pylint: disable=bad-super-call

        self.input_water_heater_tier = kwargs.get("water_heater_tier")
        self.water_heater_tier = self.normalize_water_heater_tier(self.input_water_heater_tier)

        self.input_estar_std_refrigerators_installed = kwargs.get(
            "estar_std_refrigerators_installed", kwargs.get("neea_refrigerators_installed", False)
        )
        self.estar_std_refrigerators_installed = self.normalize_estar_std_refrigerators_installed(
            self.input_estar_std_refrigerators_installed
        )

        self.input_estar_dishwasher_installed = kwargs.get("estar_dishwasher_installed", False)
        self.estar_dishwasher_installed = self.normalize_boolean(
            self.input_estar_dishwasher_installed
        )

        self.input_estar_front_load_clothes_washer_installed = kwargs.get(
            "estar_front_load_clothes_washer_installed",
            kwargs.get(
                "estar_clothes_washer_installed", kwargs.get("neea_clothes_washer_installed", False)
            ),
        )
        self.estar_front_load_clothes_washer_installed = (
            self.normalize_estar_clothes_washer_installed(
                self.input_estar_front_load_clothes_washer_installed
            )
        )

        self.input_clothes_dryer_tier = kwargs.get("clothes_dryer_tier")
        self.clothes_dryer_tier = self.normalize_input_clothes_dryer_tier(
            self.input_clothes_dryer_tier
        )

        self.input_earth_advantage_certified = kwargs.get("certified_earth_advantage")
        self.earth_advantage_certified = self.normalize_input_earth_advantage_certified(
            self.input_earth_advantage_certified
        )

        self.input_electric_meter_number = kwargs.get("electric_meter_number")
        self.electric_meter_number = self.input_electric_meter_number

        if self.issues:
            raise RTFInputException(*self.issues)

    @property
    def program(self):
        return "neea-bpa"

    def normalize_estar_std_refrigerators_installed(self, value):
        return self.normalize_boolean(value)

    @property
    def estar_refrigerators_installed(self):
        return None

    def normalize_estar_clothes_washer_installed(self, value):
        return self.normalize_boolean(value)

    @property
    def estar_clothes_washer_installed(self):
        return None

    def normalize_water_heater_tier(self, input_name):
        """Normalize water heater tier"""
        if input_name is None:
            return self.append_issue("Missing NEEA Water Heater Tier")

        original = input_name
        input_name = input_name.lower().strip()

        valid_list = [x[0] for x in self.constants.NEEA_WATER_HEATER_TIER_MAP]
        lower_list = [x[0].lower() for x in self.constants.NEEA_WATER_HEATER_TIER_MAP]
        if input_name.lower() in lower_list:
            input_name = valid_list[lower_list.index(input_name.lower())]

        if input_name not in valid_list:
            lower_list = [x[1].lower() for x in self.constants.NEEA_WATER_HEATER_TIER_MAP]
            if input_name.lower() in lower_list:
                input_name = valid_list[lower_list.index(input_name.lower())]

        if input_name not in valid_list:
            msg = "Invalid Water Heater Tier identified '%s' must be one of %s"
            return self.append_issue(
                msg,
                original,
                ", ".join([x[1] for x in self.constants.NEEA_WATER_HEATER_TIER_MAP]),
            )

        return input_name

    def normalize_input_clothes_dryer_tier(self, input_name):
        """Normalize clothes dryer tier"""

        if input_name in [None, "None", "none"]:
            return None

        if input_name == "ENERGY STAR\xae":
            input_name = "estar"

        input_name = input_name.lower().replace(" ", "")

        if not input_name:
            return None

        valid_list = [x[0] for x in self.constants.NEEA_CLOTHES_DRYER_TIER_SAVINGS_MAP]
        lower_list = [x[0].lower() for x in self.constants.NEEA_CLOTHES_DRYER_TIER_SAVINGS_MAP]
        if input_name.lower() in lower_list:
            input_name = valid_list[lower_list.index(input_name.lower())]

        if input_name not in valid_list:
            msg = "Invalid clothes dryer tier identified '%s' must be one of %s"
            return self.append_issue(msg, input_name, ", ".join(valid_list))

        return input_name

    def normalize_input_earth_advantage_certified(self, input_name):
        """Normalize out the annotation for Earth Advantage cert"""
        if input_name in [None, "None", "none", ""]:
            return None

        from axis.customer_neea.eep_programs import NeeaBpa

        spec = NeeaBpa().annotations.get("certified-earth-advantage", {})
        valid_list = spec.get("valid_multiplechoice_values").split(",")
        if input_name not in valid_list:
            msg = "Invalid Earth Advantage Certification '%s' must be one of %s"
            return self.append_issue(msg, input_name, ", ".join(valid_list))

        return input_name

    def get_sim_modeled_input(self):
        """Simulation based input"""
        return NEEASimModeledInput

    def get_rem_modeled_input(self):
        """Modeled Input"""
        return NEEARemModeledInput

    def get_simulated_input(self):
        """Simulated Input"""
        return NEEASimulatedInput

    def dump_simulation(self, as_dict=False):
        """Dump the simulation. You should be able to feed this back in to test it."""
        kwargs = self._kwargs.copy()
        if "home_status_id" in self._kwargs.keys():
            kwargs.update(
                {
                    "us_state": self.us_state,
                    "heating_fuel": self.heating_fuel,
                    "home_size": self.home_size,
                    "heating_zone": self.heating_zone,
                    "code_data": {
                        "heating_therms": self.code_data.heating_therms,
                        "heating_kwh": self.code_data.heating_kwh,
                        "cooling_kwh": self.code_data.cooling_kwh,
                        "total_consumption_kwh": self.code_data.total_consumption_kwh,
                        "total_consumption_therms": self.code_data.total_consumption_therms,
                    },
                    "improved_data": {
                        "heating_therms": self.improved_data.heating_therms,
                        "heating_kwh": self.improved_data.heating_kwh,
                        "cooling_kwh": self.improved_data.cooling_kwh,
                        "primary_heating_type": self.improved_data.primary_heating_type,
                        "primary_cooling_type": self.improved_data.primary_cooling_type,
                        "primary_cooling_fuel": self.improved_data.primary_cooling_fuel,
                    },
                    "percent_improvement": self.default_percent_improvement,
                    "electric_utility": self.electric_utility,
                    "gas_utility": self.gas_utility,
                }
            )
            kwargs.pop("home_status_id")

        for item in ["county", "electric_utility", "gas_utility"]:
            value = kwargs.pop(item, None)
            if value is not None:
                try:
                    kwargs[item] = value.pk
                except AttributeError:
                    pass

        if as_dict:
            return kwargs
        return "kwargs = " + json.dumps(kwargs, indent=4)

    @property
    def water_heater_type(self):
        """Water heater type"""
        if self.water_heater_tier == "electric resistance":
            return "electric resistance"
        elif "tier" in self.water_heater_tier:
            return "hpwh"
        return "gas"

    @property
    def pretty_water_heater_tier(self):
        """Pretty Water heater type"""
        return dict(self.constants.NEEA_WATER_HEATER_TIER_MAP).get(self.water_heater_tier)

    @property
    def heat_pump_water_heater_kwh(self):
        """Heat Pump water heater kWh"""
        data = dict(self.constants.HEAT_PUMP_WATER_HEATER_KWH)
        return data.get((self.water_heater_tier, self.heating_zone), 0.0)

    @property
    def water_heater_kwh_savings(self):
        """Water heater kWh savings"""
        if "gas" in self.water_heater_tier or "propane" in self.water_heater_tier:
            return 0.0
        lookup = dict(self.constants.NEEA_WATER_HEATER_BASELINE_SAVINGS_RATES)
        key = lookup.get(
            (
                self.us_state,
                self.heating_system_config,
                self.home_size,
                self.heating_zone,
            ),
            {},
        )
        return key.get(self.water_heater_tier, 0.0)

    @property
    def water_heater_therm_savings(self):
        """Water heater therm savings"""
        if "gas" not in self.water_heater_tier:
            return 0.0
        lookup = dict(self.constants.NEEA_WATER_HEATER_BASELINE_SAVINGS_RATES)
        key = lookup.get(
            (
                self.us_state,
                self.heating_system_config,
                self.home_size,
                self.heating_zone,
            ),
            {},
        )
        return key.get(self.water_heater_tier, 0.0)

    def hot_water_report(self):
        """Report"""
        data = []
        data.append("\n--- NEEA Water Heating Energy Savings Calculations ----")
        msg = "{:<60} {:<10}{:<5}"
        data.append(msg.format("Water Heater Tier", self.pretty_water_heater_tier, ""))
        data.append(
            msg.format("Water Heater Savings", self.round1__water_heater_kwh_savings, "kWh")
        )
        data.append(
            msg.format(
                "Water Heater Savings",
                self.round1__water_heater_therm_savings,
                "Therms",
            )
        )
        return "\n".join(data)

    @property
    def refrigerator_per_unit_savings(self):
        """Refrigerator per unit savings"""
        return self.constants.NEEA_REFRIGERATOR_SAVINGS_PER_UNIT

    @property
    def refrigerator_annual_savings(self):
        """Refrigerator annual savings"""
        return int(self.estar_std_refrigerators_installed) * self.refrigerator_per_unit_savings

    @property
    def dishwasher_per_unit_savings(self):
        """Dishwasher per unit savings"""
        return self.constants.NEEA_DISHWASHER_SAVINGS_PER_UNIT

    @property
    def dishwasher_annual_savings(self):
        """Dishwasher annual savings"""
        return int(self.estar_dishwasher_installed) * self.dishwasher_per_unit_savings

    @property
    def clothes_washer_per_unit_savings(self):
        """Washer per unit savings"""
        return self.constants.NEEA_CLOTHES_WASTER_SAVINGS_PER_UNIT

    @property
    def clothes_washer_annual_savings(self):
        """Washer annual savings"""
        return (
            int(self.estar_front_load_clothes_washer_installed)
            * self.clothes_washer_per_unit_savings
        )

    @property
    def clothes_dryer_annual_savings(self):
        """Dryer per unit savings"""
        return dict(self.constants.NEEA_CLOTHES_DRYER_TIER_SAVINGS_MAP).get(
            self.clothes_dryer_tier, 0.0
        )

    @property
    def appliance_kwh_savings(self):
        """Refrigerator annual savings"""
        return (
            self.refrigerator_annual_savings
            + self.dishwasher_annual_savings
            + self.clothes_washer_annual_savings
            + self.clothes_dryer_annual_savings
        )

    def appliance_report(self):
        """Report"""
        data = []
        data.append("\n--- Appliance Energy Savings Calculations: ----")
        msg = "{:<60} {:<10}{:<10}{:<10}{:<5}"
        data.append(
            msg.format(
                "ENERGYSTAR Refrigerators (> 7.75ft3)",
                int(self.estar_std_refrigerators_installed),
                self.round2__refrigerator_per_unit_savings,
                self.round2__refrigerator_annual_savings,
                "",
            )
        )
        data.append(
            msg.format(
                "ENERGYSTAR Dishwashers",
                int(self.estar_dishwasher_installed),
                self.round2__dishwasher_per_unit_savings,
                self.round2__dishwasher_annual_savings,
                "",
            )
        )
        data.append(
            msg.format(
                "ENERGYSTAR Front Load Clothes Washer",
                int(self.estar_front_load_clothes_washer_installed),
                self.round2__clothes_washer_per_unit_savings,
                self.round2__clothes_washer_annual_savings,
                "",
            )
        )
        data.append(
            msg.format(
                "Clothes Dryer",
                self.clothes_dryer_tier or "-",
                self.clothes_dryer_annual_savings,
                self.round2__clothes_dryer_annual_savings,
                "",
            )
        )
        data.append(msg.format("", "", "", "", ""))
        data.append(
            msg.format(
                "Annual Energy Savings",
                "",
                "",
                self.round2__appliance_kwh_savings,
                "kWh",
            )
        )
        return "\n".join(data)

    @property
    def total_kwh_savings(self):
        """Total kWh savings"""
        return (
            self.heating_kwh_savings
            + self.cooling_kwh_savings
            + self.smart_thermostat_kwh_savings
            + self.water_heater_kwh_savings
            + self.showerhead_kwh_savings
            + self.lighting_kwh_savings
            + self.appliance_kwh_savings
        )

    @property
    def total_therm_savings(self):
        """Total Therm savings"""
        return (
            self.heating_therm_savings
            + self.cooling_therm_savings
            + self.smart_thermostat_therm_savings
            + self.water_heater_therm_savings
            + self.showerhead_therm_savings
            + self.lighting_therm_savings
            + self.appliance_therm_savings
        )

    def total_report(self):
        """Report"""
        data = []
        data.append("\n--- Savings Summary ----")
        data.append(" Electric Savings")
        msg = "{:<50} {:<15}{:<12}{:<12}{:<12}"
        data.append(msg.format("Measure", "Total kWh", "Short", "Medium", "Long"))
        data.append(
            msg.format(
                "Heating",
                self.round2__heating_kwh_savings,
                self.incentives.heating_kwh_measure_life.round2__short,
                self.incentives.heating_kwh_measure_life.round2__medium,
                self.incentives.heating_kwh_measure_life.round2__long,
            )
        )
        data.append(
            msg.format(
                "Smart Thermostat",
                self.round2__smart_thermostat_kwh_savings,
                self.incentives.smart_thermostat_kwh_measure_life.round2__short,
                self.incentives.smart_thermostat_kwh_measure_life.round2__medium,
                self.incentives.smart_thermostat_kwh_measure_life.round2__long,
            )
        )
        data.append(
            msg.format(
                "Cooling",
                self.round2__cooling_kwh_savings,
                self.incentives.cooling_kwh_measure_life.round2__short,
                self.incentives.cooling_kwh_measure_life.round2__medium,
                self.incentives.cooling_kwh_measure_life.round2__long,
            )
        )
        data.append(
            msg.format(
                "Water Heating",
                self.round2__water_heater_kwh_savings,
                self.incentives.water_heater_kwh_measure_life.round2__short,
                self.incentives.water_heater_kwh_measure_life.round2__medium,
                self.incentives.water_heater_kwh_measure_life.round2__long,
            )
        )
        if self.__class__.__name__ == "NEEAV2Calculator":
            data.append(
                msg.format(
                    "Low Flow Shower Head",
                    self.round2__showerhead_kwh_savings,
                    self.incentives.showerhead_kwh_measure_life.round2__short,
                    self.incentives.showerhead_kwh_measure_life.round2__medium,
                    self.incentives.showerhead_kwh_measure_life.round2__long,
                )
            )
            data.append(
                msg.format(
                    "Lighting",
                    self.round2__lighting_kwh_savings,
                    self.incentives.lighting_kwh_measure_life.round2__short,
                    self.incentives.lighting_kwh_measure_life.round2__medium,
                    self.incentives.lighting_kwh_measure_life.round2__long,
                )
            )
        data.append(
            msg.format(
                "Appliances",
                self.round2__appliance_kwh_savings,
                self.incentives.appliances_kwh_measure_life.round2__short,
                self.incentives.appliances_kwh_measure_life.round2__medium,
                self.incentives.appliances_kwh_measure_life.round2__long,
            )
        )
        data.append(msg.format("-------------", "-" * 8, "-" * 8, "-" * 8, "-" * 8))
        data.append(
            msg.format(
                "Total",
                self.round2__total_kwh_savings,
                self.incentives.total_kwh_measure_life.round2__short,
                self.incentives.total_kwh_measure_life.round2__medium,
                self.incentives.total_kwh_measure_life.round2__long,
            )
        )
        data.append("\n Gas Savings")
        msg = "{:<50} {:<15}{:<12}{:<12}{:<12}"
        data.append(msg.format("Measure", "Total Therms", "Short", "Medium", "Long"))
        data.append(
            msg.format(
                "Heating",
                self.round2__heating_therm_savings,
                self.incentives.heating_therm_measure_life.round2__short,
                self.incentives.heating_therm_measure_life.round2__medium,
                self.incentives.heating_therm_measure_life.round2__long,
            )
        )
        data.append(
            msg.format(
                "Smart Thermostat",
                self.round2__smart_thermostat_therm_savings,
                self.incentives.smart_thermostat_therm_measure_life.round2__short,
                self.incentives.smart_thermostat_therm_measure_life.round2__medium,
                self.incentives.smart_thermostat_therm_measure_life.round2__long,
            )
        )
        data.append(
            msg.format(
                "Cooling",
                self.round2__cooling_therm_savings,
                self.incentives.cooling_therm_measure_life.round2__short,
                self.incentives.cooling_therm_measure_life.round2__medium,
                self.incentives.cooling_therm_measure_life.round2__long,
            )
        )
        data.append(
            msg.format(
                "Water Heating",
                self.round2__water_heater_therm_savings,
                self.incentives.water_heater_therm_measure_life.round2__short,
                self.incentives.water_heater_therm_measure_life.round2__medium,
                self.incentives.water_heater_therm_measure_life.round2__long,
            )
        )
        if self.__class__.__name__ == "NEEAV2Calculator":
            data.append(
                msg.format(
                    "Low Flow Shower Head",
                    self.round2__showerhead_therm_savings,
                    self.incentives.showerhead_therm_measure_life.round2__short,
                    self.incentives.showerhead_therm_measure_life.round2__medium,
                    self.incentives.showerhead_therm_measure_life.round2__long,
                )
            )
            data.append(
                msg.format(
                    "Lighting",
                    self.round2__lighting_therm_savings,
                    self.incentives.lighting_therm_measure_life.round2__short,
                    self.incentives.lighting_therm_measure_life.round2__medium,
                    self.incentives.lighting_therm_measure_life.round2__long,
                )
            )
        data.append(
            msg.format(
                "Appliances",
                self.round2__appliance_therm_savings,
                self.incentives.appliances_therm_measure_life.round2__short,
                self.incentives.appliances_therm_measure_life.round2__medium,
                self.incentives.appliances_therm_measure_life.round2__long,
            )
        )
        data.append(msg.format("-------------", "-" * 8, "-" * 8, "-" * 8, "-" * 8))
        data.append(
            msg.format(
                "Total",
                self.round2__total_therm_savings,
                self.incentives.total_therm_measure_life.round2__short,
                self.incentives.total_therm_measure_life.round2__medium,
                self.incentives.total_therm_measure_life.round2__long,
            )
        )

        data.append("")
        msg = "{:<40}{:<10}{:<12}"
        data.append(
            msg.format(
                "Code Consumption",
                self.round2__code_data_total_consumption_mmbtu,
                "Mbtu",
            )
        )
        data.append(
            msg.format(
                "Improved Consumption",
                self.round2__improved_data_total_consumption_mmbtu,
                "Mbtu",
            )
        )
        data.append(msg.format("Calculated Savings", self.round2__total_mmbtu_savings, "Mbtu"))
        data.append(msg.format("-" * 40, "-" * 10, "-" * 12))
        data.append(
            msg.format(
                "Alternate percent improvement",
                self.round2p__revised_percent_improvement,
                "%",
            )
        )
        if 0.199 < self.revised_percent_improvement < 0.2:
            data.append(
                msg.format(
                    "True Alternate percent improvement",
                    self.revised_percent_improvement * 100.0,
                    "%",
                )
            )
        data.append(
            msg.format(
                "Initial percent improvement",
                self.round2p__default_percent_improvement,
                "%",
            )
        )
        if 0.199 < self.default_percent_improvement < 0.2:
            data.append(
                msg.format(
                    "True percent improvement",
                    self.revised_percent_improvement * 100.0,
                    "%",
                )
            )
        return "\n".join(data)

    def result_data(self, include_reports=True, recalculate=False):
        """Result data"""
        from axis.customer_neea.models import StandardProtocolCalculator

        if self.home_status and self.home_status.state == "complete":
            if not recalculate:
                try:
                    return StandardProtocolCalculator.objects.get(
                        home_status=self.home_status
                    ).as_dict()
                except StandardProtocolCalculator.DoesNotExist:
                    msg = (
                        "Updating StandardProtocolCalculator for Project [%r] "
                        "as it doesn't exist!"
                    )
                    log.warning(msg, self.home_status.id)

        sp = None
        if self.home_status:  # incomplete or recalc
            (
                sp,
                create,
            ) = StandardProtocolCalculator.objects.update_or_create_from_calculator(self)
            data = sp.as_dict()
        else:
            data = OrderedDict()
            data["program"] = self.program
            data["heating_kwh_savings"] = self.heating_kwh_savings
            data["heating_therm_savings"] = self.heating_therm_savings
            data["cooling_kwh_savings"] = self.cooling_kwh_savings
            data["cooling_therm_savings"] = self.cooling_therm_savings
            data["smart_thermostat_kwh_savings"] = self.smart_thermostat_kwh_savings
            data["smart_thermostat_therm_savings"] = self.smart_thermostat_therm_savings
            data["water_heater_kwh_savings"] = self.water_heater_kwh_savings
            data["showerhead_kwh_savings"] = self.showerhead_kwh_savings
            data["showerhead_therm_savings"] = self.showerhead_therm_savings
            data["lighting_kwh_savings"] = self.lighting_kwh_savings
            data["appliance_kwh_savings"] = self.appliance_kwh_savings
            data["appliance_therm_savings"] = self.appliance_therm_savings
            data["total_kwh_savings"] = self.total_kwh_savings
            data["total_therm_savings"] = self.total_therm_savings
            data["total_mmbtu_savings"] = self.total_mmbtu_savings

            # Note:  These are ONLY Available for live calculations.
            data["revised_percent_improvement"] = self.revised_percent_improvement
            data["code_total_consumption_mmbtu"] = self.code_data_total_consumption_mmbtu
            data["improved_total_consumption_mmbtu"] = self.improved_data_total_consumption_mmbtu
            val = self.improved_total_consumption_mmbtu_with_savings
            data["improved_total_consumption_mmbtu_with_savings"] = val
            data["heat_pump_water_heater_kwh_savings"] = self.heat_pump_water_heater_kwh_savings
            data["water_heater_therm_savings"] = self.water_heater_therm_savings

            data.update(self.incentives.data())

            builder_incentive = (
                "Builder incentive is dependent upon partner utility " "and managed outside of Axis"
            )
            if self.incentives.has_incentive is not None:
                builder_incentive = "${:.2f}".format(round(self.incentives.builder_incentive, 2))
            data["builder_incentive"] = builder_incentive
            data["incentive_paying_organization"] = self.incentives.incentive_paying_organization

        data["from_db"] = False  # This was just created - it is db backed but it's live.
        data["utility_requirements"] = self.utility_requirements
        if include_reports:
            data["reports"] = {
                "summary": self.report(),
                "heating_cooling": self.heating_cooling_report(),
                "hot_water": self.hot_water_report(),
                "lighting": self.lighting_report(),
                "appliances": self.appliance_report(),
                "thermostat": self.thermostat_report(),
                "shower_head": self.shower_head_report(),
                "incentives": self.incentives.report(),
                "total": self.total_report(),
                "simulation_dump": self.dump_simulation(),
            }
            if sp:
                sp.reports = data["reports"]
                sp.save()

        return data

    # pylint: disable=inconsistent-return-statements,too-many-return-statements
    @property
    def utility_requirements(self):
        """Utility requirements"""
        if self.incentives.has_incentive is False:
            incentive_class = self.incentives.__class__.__name__
            if incentive_class == "ClarkIncentivesCalculator":
                return self.constants.CLARK_REQUIREMENTS
            elif incentive_class == "UtilityCityOfRichlandIncentivesCalculator":
                return self.constants.UTILITY_CITY_OF_RICHLAND_REQUIREMENTS
            elif incentive_class == "BentonREAIncentivesCalculator":
                return self.constants.BENTON_REA_REQUIREMENTS
            elif incentive_class == "PugetIncentivesCalculator":
                return self.constants.PUGET_REQUIREMENTS
            elif incentive_class == "CentralIncentivesCalculator":
                return self.constants.CENTRAL_REQUIREMENTS
            elif incentive_class == "PacificPowerIncentivesCalculator":
                return self.constants.PACIFIC_REQUIREMENTS
            elif incentive_class == "IdahoPowerIncentivesCalculator":
                return self.constants.IDAHO_REQUIREMENTS
            elif incentive_class == "InlandPowerCalculator":
                return self.constants.INLAND_REQUIREMENTS
            elif incentive_class == "EWEBCalculator":
                return self.constants.EWEB_REQUIREMENTS
            elif incentive_class == "TacomaPowerIncentivesCalculator":
                return self.constants.TACOMA_REQUIREMENTS
            elif incentive_class == "PeninsulaPowerIncentivesCalculator":
                return self.constants.PENINSULA_POWER_REQUIREMENTS

    @property
    def incentives(self):  # noqa: C901
        """Incentives requirements"""

        if self._incentives is not None:
            return self._incentives

        incentive_kwargs = self.incentive_kwargs

        # Electric Incentives
        #
        # ATTENTION ADD THE SLUG TO customer_neea.apps.NEEA_SP_INCENTIVE_UTILITY_SLUGS
        #
        electric_incentive = BPAIncentivesCalculator(**incentive_kwargs)
        if self.electric_utility == "clark-pud":
            electric_incentive = ClarkIncentivesCalculator(**incentive_kwargs)
        elif self.electric_utility == "utility-city-of-richland":
            electric_incentive = UtilityCityOfRichlandIncentivesCalculator(**incentive_kwargs)
        elif self.electric_utility == "benton-rea":
            electric_incentive = BentonREAIncentivesCalculator(**incentive_kwargs)
        elif self.electric_utility == "puget-sound-energy":
            electric_incentive = PugetIncentivesCalculator(**incentive_kwargs)
        elif self.electric_utility == "central-electric":
            electric_incentive = CentralIncentivesCalculator(**incentive_kwargs)
        elif self.electric_utility == "pacific-power":
            electric_incentive = PacificPowerIncentivesCalculator(**incentive_kwargs)
        elif self.electric_utility == "idaho-power":
            electric_incentive = IdahoPowerIncentivesCalculator(**incentive_kwargs)
        elif self.electric_utility == "inland-power":
            electric_incentive = InlandPowerCalculator(**incentive_kwargs)
        elif self.electric_utility == "utility-eugene-water-electric-board":
            electric_incentive = EWEBCalculator(**incentive_kwargs)
        elif self.electric_utility == "utility-tacoma-public-utilities":
            electric_incentive = TacomaPowerIncentivesCalculator(**incentive_kwargs)
        elif self.electric_utility == "utility-peninsula-power-light":
            electric_incentive = PeninsulaPowerIncentivesCalculator(**incentive_kwargs)

        # Gas Incentives
        gas_incentive = None
        if self.gas_utility == "puget-sound-energy":
            gas_incentive = PugetIncentivesCalculator(**incentive_kwargs)

        if electric_incentive and gas_incentive:
            if self.gas_utility == "puget-sound-energy":
                # Per ZD22759
                # * Electric Space + Electric Water where PSE is the electric provider
                # * Gas Space + Gas Water where PSE is the gas and electric provider
                # * Gas Space + Gas Water where PSE is the gas provider,
                #                         other utility is electric provider

                if self.electric_utility == "puget-sound-energy":
                    return electric_incentive

                incentive_class = electric_incentive.__class__.__name__
                if "gas" in self.water_heater_tier.lower():
                    if self.heating_fuel == "gas" or incentive_class == "BPAIncentivesCalculator":
                        return gas_incentive
                return electric_incentive

            # If we have both get the highest incentive
            if electric_incentive.has_incentive and gas_incentive.has_incentive:
                self._incentives = electric_incentive
                if gas_incentive.builder_incentive > electric_incentive.builder_incentive:
                    self._incentives = gas_incentive
            elif gas_incentive.has_incentive:
                self._incentives = gas_incentive
            else:
                # Default to BPA
                self._incentives = electric_incentive

        else:
            # Default to BPA unless the gas utility is spelled out we only have one or the other.
            self._incentives = electric_incentive
            if gas_incentive:
                self._incentives = gas_incentive

        return self._incentives
