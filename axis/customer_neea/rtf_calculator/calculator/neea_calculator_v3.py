"""neea_calculator_v3.py - Axis"""

__author__ = "Steven K"
__date__ = "6/21/21 13:49"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import json
import logging

from simulation.enumerations import FuelType

from .neea_calculator_v2 import NEEAV2Calculator
from .. import constants
from ..base import RTFInputException
from ..constants.neea_v3 import (
    NEEA_REFRIGERATOR_SAVINGS_MAP,
    NEEA_REFRIGERATOR_CHOICE_MAP,
    NEEA_CLOTHES_WASHER_CHOICE_MAP,
    NEEA_CLOTHES_DRYER_TIER_MAP,
)

log = logging.getLogger(__name__)


class NEEAV3Calculator(NEEAV2Calculator):
    """Main NEEA V3 Standard Protocol calculator"""

    def __init__(self, **kwargs):
        self.input_clothes_dryer_fuel = kwargs.pop("clothes_dryer_fuel", None)
        super(NEEAV3Calculator, self).__init__(**kwargs)

        self.clothes_dryer_fuel = self.normalize_input_clothes_dryer_fuel(
            self.input_clothes_dryer_fuel, self.improved_data
        )

        if self.issues:
            raise RTFInputException(*self.issues)

    def get_constants(self):
        return getattr(constants, "neea_v3")

    @property
    def program(self):
        return "neea-bpa-v3"

    @property
    def estar_refrigerators_installed(self):
        return self.estar_std_refrigerators_installed

    def normalize_estar_std_refrigerators_installed(self, input_name):
        """This is no longer an integer it is one of bottom, top, other"""
        if input_name in [None, "None", ""]:
            return None

        if input_name in [True, False]:
            msg = "Invalid Refrigerator option for V3 - You must use one of %s"
            return self.append_issue(
                msg,
                ", ".join([x[1] for x in self.constants.NEEA_REFRIGERATOR_CHOICE_MAP]),
            )

        original = input_name
        input_name = input_name.lower().strip()

        valid_list = [x[0] for x in self.constants.NEEA_REFRIGERATOR_CHOICE_MAP if x[0]]
        lower_list = [x[0].lower() for x in self.constants.NEEA_REFRIGERATOR_CHOICE_MAP if x[0]]
        if input_name.lower() in lower_list:
            input_name = valid_list[lower_list.index(input_name.lower())]

        if input_name not in valid_list:
            lower_list = [x[1].lower() for x in self.constants.NEEA_REFRIGERATOR_CHOICE_MAP if x[0]]
            if input_name.lower() in lower_list:
                input_name = valid_list[lower_list.index(input_name.lower())]

        if input_name not in valid_list:
            msg = "Invalid Refrigerator identified '%s' must be one of %s"
            return self.append_issue(
                msg,
                original,
                ", ".join([x[1] for x in self.constants.NEEA_REFRIGERATOR_CHOICE_MAP]),
            )

        return input_name

    @property
    def estar_clothes_washer_installed(self):
        return self.estar_front_load_clothes_washer_installed

    def normalize_estar_clothes_washer_installed(self, input_name):
        if input_name in [None, "None", ""]:
            return None

        if input_name in [True, False]:
            msg = "Invalid Clothes Washer option for V3 - You must use one of %s"
            return self.append_issue(
                msg,
                ", ".join([x[1] for x in self.constants.NEEA_CLOTHES_WASHER_CHOICE_MAP]),
            )

        original = input_name
        input_name = input_name.lower().strip()

        valid_list = [x[0] for x in self.constants.NEEA_CLOTHES_WASHER_CHOICE_MAP if x[0]]
        lower_list = [x[0].lower() for x in self.constants.NEEA_CLOTHES_WASHER_CHOICE_MAP if x[0]]
        if input_name.lower() in lower_list:
            input_name = valid_list[lower_list.index(input_name.lower())]

        if input_name not in valid_list:
            lower_list = [
                x[1].lower() for x in self.constants.NEEA_CLOTHES_WASHER_CHOICE_MAP if x[0]
            ]
            if input_name.lower() in lower_list:
                input_name = valid_list[lower_list.index(input_name.lower())]

        if input_name not in valid_list:
            msg = "Invalid Clothes Washer identified '%s' must be one of %s"
            return self.append_issue(
                msg,
                original,
                ", ".join([x[1] for x in self.constants.NEEA_CLOTHES_WASHER_CHOICE_MAP]),
            )
        return input_name

    def normalize_input_clothes_dryer_fuel(self, input_data=None, simulation=None):
        """Clothes dryer fuel must be either electric / gas"""
        if input_data is not None:
            if input_data not in [FuelType.ELECTRIC, FuelType.NATURAL_GAS]:
                self.append_issue(
                    f"Provided clothes dryer fuel {input_data} is invalid. Must be "
                    f"one of {FuelType.ELECTRIC} or {FuelType.NATURAL_GAS}"
                )
            return input_data
        if simulation:
            if simulation.clothes_dryer_fuel not in [FuelType.ELECTRIC, FuelType.NATURAL_GAS]:
                self.append_issue(
                    f"Provided simulation clothes dryer fuel {input_data} is invalid. Must be "
                    f"one of {FuelType.ELECTRIC} or {FuelType.NATURAL_GAS}"
                )
            return simulation.clothes_dryer_fuel

    @property
    def refrigerator_annual_savings(self):
        """Refrigerator annual savings"""
        return dict(NEEA_REFRIGERATOR_SAVINGS_MAP).get(self.estar_std_refrigerators_installed, 0.0)

    def dump_simulation(self, as_dict=False):
        _kwargs = super(NEEAV3Calculator, self).dump_simulation(as_dict=True)

        _kwargs["estar_clothes_washer_installed"] = self.estar_front_load_clothes_washer_installed
        _kwargs["clothes_dryer_fuel"] = self.clothes_dryer_fuel

        skipped = [
            "cfl_installed",
            "led_installed",
            "total_installed_lamps",
            "qty_shower_head_1p5",
            "qty_shower_head_1p75",
            "estar_front_load_clothes_washer_installed",
        ]
        kwargs = {}
        for k, v in list(_kwargs.items())[:]:
            if k in skipped:
                continue
            kwargs[k] = _kwargs.pop(k)

        if as_dict:
            return kwargs
        return "kwargs = " + json.dumps(kwargs, indent=4)

    @property
    def lighting_kwh_savings(self):
        return 0.0

    def lighting_report(self):
        return "Removed in V3"

    @property
    def showerhead_kwh_savings(self):
        return 0.0

    @property
    def showerhead_therm_savings(self):
        return 0.0

    def shower_head_report(self):
        return "Removed in V3"

    @property
    def refrigerator_per_unit_savings(self):
        """Refrigerator per unit savings"""
        return 0.0

    @property
    def refrigerator_annual_kwh_savings(self):
        """Refrigerator annual savings"""
        data = dict(self.constants.NEEA_REFRIGERATOR_SAVINGS_MAP)
        return data.get(self.estar_std_refrigerators_installed, 0.0)

    @property
    def refrigerator_annual_therm_savings(self):
        """Refrigerator annual savings"""
        return 0.0

    @property
    def dishwasher_annual_kwh_savings(self):
        """Dishwasher annual savings"""
        return self.dishwasher_annual_savings

    @property
    def dishwasher_annual_therm_savings(self):
        """Dishwasher annual savings"""
        return 0.0

    @property
    def clothes_washer_per_unit_savings(self):
        """Washer per unit savings"""
        return 0.0

    @property
    def clothes_washer_annual_kwh_savings(self):
        """Washer annual savings"""
        data = dict(self.constants.NEEA_CLOTHES_WASHER_SAVINGS_MAP)
        key = (
            self.estar_front_load_clothes_washer_installed,
            self.water_heater_fuel,
            self.clothes_dryer_fuel,
        )
        return data.get(key, {}).get("kwh_savings", 0.0)

    @property
    def clothes_washer_annual_therm_savings(self):
        """Washer annual savings"""
        data = dict(self.constants.NEEA_CLOTHES_WASHER_SAVINGS_MAP)
        key = (
            self.estar_front_load_clothes_washer_installed,
            self.water_heater_fuel,
            self.clothes_dryer_fuel,
        )
        return data.get(key, {}).get("therm_savings", 0.0)

    @property
    def clothes_dryer_annual_kwh_savings(self):
        """Dryer per unit savings"""
        return dict(self.constants.NEEA_CLOTHES_DRYER_TIER_SAVINGS_MAP).get(
            self.clothes_dryer_tier, 0.0
        )

    @property
    def clothes_dryer_annual_therm_savings(self):
        """Dryer per unit savings"""
        return 0.0

    @property
    def appliance_kwh_savings(self):
        """Refrigerator annual savings"""
        return (
            self.refrigerator_annual_kwh_savings
            + self.dishwasher_annual_kwh_savings
            + self.clothes_washer_annual_kwh_savings
            + self.clothes_dryer_annual_kwh_savings
        )

    @property
    def appliance_therm_savings(self):
        """Refrigerator annual savings"""
        return (
            self.refrigerator_annual_therm_savings
            + self.dishwasher_annual_therm_savings
            + self.clothes_washer_annual_therm_savings
            + self.clothes_dryer_annual_therm_savings
        )

    def appliance_report(self):
        data = []
        data.append("\n--- Appliance Energy Savings Calculations: ----")
        msg = "{:<30} {:<40}{:<15}{:<15}{:<5}"
        data.append(msg.format("Water Heating Fuel", self.water_heater_fuel, "", "", ""))
        data.append(msg.format("Clothes Dryer Fuel", self.clothes_dryer_fuel, "", "", ""))

        data.append(msg.format("", "", "", "", ""))

        pretty_refer = dict(NEEA_REFRIGERATOR_CHOICE_MAP)
        data.append(
            msg.format(
                "ENERGYSTAR Refrigerators",
                pretty_refer.get(self.estar_std_refrigerators_installed),
                self.round2__refrigerator_annual_kwh_savings,
                self.round2__refrigerator_annual_therm_savings,
                "",
            )
        )
        data.append(
            msg.format(
                "ENERGYSTAR Dishwashers",
                int(self.estar_dishwasher_installed),
                self.round2__dishwasher_annual_kwh_savings,
                self.round2__dishwasher_annual_therm_savings,
                "",
            )
        )

        pretty_washer = dict(NEEA_CLOTHES_WASHER_CHOICE_MAP)
        data.append(
            msg.format(
                "ENERGYSTAR Clothes Washer",
                pretty_washer.get(self.estar_front_load_clothes_washer_installed, "-"),
                self.round2__clothes_washer_annual_kwh_savings,
                self.round2__clothes_washer_annual_therm_savings,
                "",
            )
        )
        pretty_dryer = dict(NEEA_CLOTHES_DRYER_TIER_MAP)
        data.append(
            msg.format(
                "Clothes Dryer",
                pretty_dryer.get(self.clothes_dryer_tier, "-"),
                self.round2__clothes_dryer_annual_kwh_savings,
                self.round2__clothes_dryer_annual_therm_savings,
                "",
            )
        )
        data.append(msg.format("", "", "", "", ""))

        msg = "{:<30} {:<40}{:<10}{:<5}{:<10}{:<5}"
        data.append(
            msg.format(
                "Annual Energy Savings",
                "",
                self.round2__appliance_kwh_savings,
                "kWh",
                self.round2__appliance_therm_savings,
                "Therms",
            )
        )
        return "\n".join(data)
