"""water.py - Axis"""

__author__ = "Steven K"
__date__ = "8/13/21 08:59"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from functools import cached_property

from tabulate import tabulate
from ....eep_programs.washington_code_credit import WACCFuelType, EfficientWaterHeating
from ....enumerations import YesNo

log = logging.getLogger(__name__)


class WaterSpecification:
    DEFAULT_WARNING_ADDER = (
        "{} does not meet the minimum requirement. Please review credit selections."
    )

    def __init__(
        self,
        dhwr_target_credit,
        efficient_water_target_credit,
        water_heating_fuel,
        **kwargs,
    ):
        # These are combined due to the way the total meets target is structured
        self.dhwr_target_credit = dhwr_target_credit
        self.dwhr_installed = kwargs.get("dwhr_installed")
        self.water_heating_fuel = water_heating_fuel

        self.efficient_water_target_credit = efficient_water_target_credit
        self.water_heater_brand = kwargs.get("water_heater_brand")
        self.water_heater_model = kwargs.get("water_heater_model")
        self.gas_water_heater_uef = kwargs.get("gas_water_heater_uef")
        self.electric_water_heater_uef = kwargs.get("electric_water_heater_uef")

    @cached_property
    def dhwr_constants(self):
        from ..constants import defaults

        return defaults.DRAIN_WATER_HEAT_RECOVER[self.dhwr_target_credit]

    @cached_property
    def hot_water_constants(self):
        from ..constants import defaults

        return defaults.HOT_WATER[self.efficient_water_target_credit]

    @cached_property
    def dwhr_installed_measure(self):
        target = self.dhwr_constants.get("dwhr_installed")
        meets_requirements = any(
            [
                target == YesNo.NO,
                self.dwhr_installed == YesNo.YES,
            ]
        )
        warning = None
        if self.dwhr_installed and not meets_requirements:
            warning = self.DEFAULT_WARNING_ADDER.format("DWHR")
        return {
            "section": "Drain Water Heat Recovery",
            "label": "Installed?",
            "minimum_requirement": target.value,
            "installed": self.dwhr_installed.value if self.dwhr_installed else None,
            "meets_requirement": meets_requirements,
            "warning": warning,
        }

    @cached_property
    def water_heater_brand_measure(self):
        meets_requirements = self.water_heater_brand is not None
        warning = None
        if not meets_requirements:
            warning = "Please enter a water heater brand name."
        return {
            "section": "Water Heater",
            "label": "Brand Name",
            "minimum_requirement": None,
            "installed": self.water_heater_brand,
            "meets_requirement": meets_requirements,
            "warning": warning,
        }

    @cached_property
    def water_heater_model_measure(self):
        meets_requirements = self.water_heater_model is not None
        warning = None
        if not meets_requirements:
            warning = "Please enter a water heater model number."
        return {
            "section": "Water Heater",
            "label": "Model Number",
            "minimum_requirement": None,
            "installed": self.water_heater_model,
            "meets_requirement": meets_requirements,
            "warning": warning,
        }

    @cached_property
    def gas_water_heater_uef_measure(self):
        mininum_requirement = self.hot_water_constants["gas_water_heater_uef"]
        warning = None
        meets_requirements = mininum_requirement is None
        if self.water_heating_fuel != WACCFuelType.GAS:
            meets_requirements = True
            if self.gas_water_heater_uef:
                mininum_requirement = "N/A"
                warning = "N/A"
        else:
            if not meets_requirements and self.gas_water_heater_uef:
                meets_requirements = self.gas_water_heater_uef >= mininum_requirement
                if not meets_requirements:
                    warning = self.DEFAULT_WARNING_ADDER.format("WATER HEATING EFFICIENCY")
        return {
            "section": "Water Heater",
            "label": "Gas Water UEF (0-1)",
            "minimum_requirement": mininum_requirement,
            "installed": self.gas_water_heater_uef,
            "meets_requirement": meets_requirements,
            "warning": warning,
        }

    @cached_property
    def electric_water_heater_uef_measure(self):
        mininum_requirement = self.hot_water_constants["electric_water_heater_uef"]
        warning = None
        meets_requirements = mininum_requirement is None
        if self.water_heating_fuel != WACCFuelType.ELECTRIC:
            meets_requirements = True
            if self.electric_water_heater_uef:
                mininum_requirement = "N/A"
                warning = "N/A"
        else:
            if not meets_requirements and self.electric_water_heater_uef:
                meets_requirements = self.electric_water_heater_uef >= mininum_requirement
                if not meets_requirements:
                    warning = self.DEFAULT_WARNING_ADDER.format("WATER HEATING EFFICIENCY")

        return {
            "section": "Water Heater",
            "label": "Electric Water UEF (0-5)",
            "minimum_requirement": mininum_requirement,
            "installed": self.electric_water_heater_uef,
            "meets_requirement": meets_requirements,
            "warning": warning,
        }

    @cached_property
    def fuel_alignment_measure(self):
        valid = []
        minimum = ""
        if self.efficient_water_target_credit != EfficientWaterHeating.OPTION_5p2:
            if self.water_heating_fuel == WACCFuelType.ELECTRIC:
                valid = [
                    EfficientWaterHeating.NONE,
                    EfficientWaterHeating.OPTION_5p4,
                    EfficientWaterHeating.OPTION_5p5,
                    EfficientWaterHeating.OPTION_5p6,
                ]
                minimum = "None or Option 5.4-6"
            elif self.water_heating_fuel == WACCFuelType.GAS:
                valid = [EfficientWaterHeating.OPTION_5p3]
                minimum = "Option 5.3"

        warning = None
        if self.efficient_water_target_credit not in valid:
            warning = "Fuel Option mismatch"
        return {
            "section": "Water Heater",
            "label": "Fuel Type alignment",
            "minimum_requirement": minimum,
            "installed": self.efficient_water_target_credit.value,
            "meets_requirement": self.efficient_water_target_credit in valid,
            "warning": warning,
        }

    @cached_property
    def meets_dwhr_requirements(self):
        return self.dwhr_installed_measure["meets_requirement"]

    @cached_property
    def meets_water_heater_requirements(self):
        return all(
            [
                # self.water_heater_brand_measure["meets_requirement"],
                # self.water_heater_model_measure["meets_requirement"],
                self.fuel_alignment_measure["meets_requirement"],
                self.electric_water_heater_uef_measure["meets_requirement"],
            ]
        )

    @cached_property
    def meet_requirements(self):
        return all(
            [
                self.meets_dwhr_requirements,
                self.meets_water_heater_requirements,
            ]
        )

    @cached_property
    def data(self):
        return {
            "dwhr_installed": self.dwhr_installed_measure,
            "water_heater_brand": self.water_heater_brand_measure,
            "water_heater_model": self.water_heater_model_measure,
            "fuel_alignment": self.fuel_alignment_measure,
            "gas_water_heater_uef": self.gas_water_heater_uef_measure,
            "electric_water_heater_uef": self.electric_water_heater_uef_measure,
        }

    @cached_property
    def report(self):
        data = "5. Efficient Water Heating\n"
        data += f"  5a. Option Selected: {self.dhwr_target_credit.value}\n"
        data += f"  5b. Option Selected: {self.efficient_water_target_credit.value}\n\n"
        table = [
            (
                x["section"],
                x["label"],
                x["minimum_requirement"],
                x["installed"],
                "Yes" if x["meets_requirement"] else "No",
            )
            for x in self.data.values()
        ]
        data += tabulate(table, headers=["Section", "Label", "Minimum", "Installed", "Meets"])
        meet = "Yes" if self.meet_requirements else "No"
        data += f"\nMeets Requirements? {meet}"
        return data
