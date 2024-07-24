"""hvac.py - Axis"""

__author__ = "Steven K"
__date__ = "8/12/21 16:03"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
from functools import cached_property

from tabulate import tabulate

from axis.customer_eto.eep_programs.washington_code_credit import FurnaceLocation, DuctLocation

log = logging.getLogger(__name__)


class HVACSpecification:
    DEFAULT_WARNING_ADDER = (
        "{} does not meet the minimum requirement. Please review credit selections."
    )

    def __init__(self, target_credit, **kwargs):
        self.target_credit = target_credit

        self.furnace_brand = kwargs.get("furnace_brand")
        self.furnace_model = kwargs.get("furnace_model")
        self.furnace_afue = kwargs.get("furnace_afue")

    @cached_property
    def constants(self):
        from ..constants import defaults

        return defaults.HVAC[self.target_credit]

    @cached_property
    def furnace_brand_measure(self):
        meets_requirements = self.furnace_brand is not None
        warning = None
        if not meets_requirements:
            warning = "Please enter a furnace brand name."
        return {
            "section": "Furnace",
            "label": "Brand Name",
            "minimum_requirement": None,
            "installed": self.furnace_brand,
            "meets_requirement": meets_requirements,
            "warning": warning,
        }

    @cached_property
    def furnace_model_measure(self):
        meets_requirements = self.furnace_model is not None
        warning = None
        if not meets_requirements:
            warning = "Please enter a furnace model number."
        return {
            "section": "Furnace",
            "label": "Model Number",
            "minimum_requirement": None,
            "installed": self.furnace_model,
            "meets_requirement": meets_requirements,
            "warning": warning,
        }

    @cached_property
    def furnace_afue_measure(self):
        target = self.constants.get("furnace_afue")
        meets_requirements = self.furnace_afue and self.furnace_afue >= target
        warning = None
        if self.furnace_afue and not meets_requirements:
            warning = self.DEFAULT_WARNING_ADDER.format("FURNACE AFUE")
        return {
            "section": "Furnace",
            "label": "Furnace AFUE",
            "minimum_requirement": None,
            "installed": self.furnace_afue,
            "meets_requirement": meets_requirements,
            "warning": warning,
        }

    @cached_property
    def meet_requirements(self):
        return all(
            [
                # self.furnace_model_measure["meets_requirement"],
                # self.furnace_brand_measure["meets_requirement"],
                self.furnace_afue_measure["meets_requirement"],
            ]
        )

    @cached_property
    def data(self):
        return {
            "furnace_brand": self.furnace_brand_measure,
            "furnace_model": self.furnace_model_measure,
            "furnace_afue": self.furnace_afue_measure,
        }

    @cached_property
    def report(self):
        data = "3. High Efficiency HVAC Equipment Options\n"
        data += f"  Option Selected: {self.target_credit.value}\n\n"
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


class HVACDistributionSpecification:
    DEFAULT_WARNING_ADDER = (
        "{} does not meet the minimum requirement. Please review credit selections."
    )

    def __init__(self, target_credit, **kwargs):
        self.target_credit = target_credit

        self.furnace_location = kwargs.get("furnace_location")
        self.duct_location = kwargs.get("duct_location")
        self.duct_leakage = kwargs.get("duct_leakage")

    @cached_property
    def constants(self):
        from ..constants import defaults

        return defaults.HVAC_DISTRIBUTION[self.target_credit]

    @cached_property
    def furnace_location_measure(self):
        target = self.constants.get("furnace_location")
        meets_requirements = any(
            [
                target == FurnaceLocation.UNCONDITIONED_SPACE,
                self.furnace_location == FurnaceLocation.CONDITIONED_SPACE,
            ]
        )
        warning = None
        if self.furnace_location and not meets_requirements:
            warning = self.DEFAULT_WARNING_ADDER.format("FURNACE LOCATION")
        return {
            "section": "Furnace",
            "label": "Furnace Location",
            "minimum_requirement": target.value,
            "installed": self.furnace_location.value if self.furnace_location else None,
            "meets_requirement": meets_requirements,
            "warning": warning,
        }

    @cached_property
    def duct_location_measure(self):
        """This involves a bit of juggling to get to what they wanted.

        Required - Look up the target Unconditioned Space we get the "Validation Number"  1
        Installed - Look up what was installed Deeply buried get Validation Number 2

        """
        validation_number_lookup = {
            None: 0,
            DuctLocation.UNCONDITIONED_SPACE: 1,
            DuctLocation.DEEPLY_BURIED: 2,
            DuctLocation.CONDITIONED_SPACE: 3,
        }
        target = self.constants.get("duct_location")
        required_value = validation_number_lookup.get(target)
        installed_value = validation_number_lookup.get(self.duct_location)
        meets_requirements = installed_value >= required_value
        warning = None
        if self.duct_location and not meets_requirements:
            warning = self.DEFAULT_WARNING_ADDER.format("DUCT LOCATION")
        return {
            "section": "Duct Location",
            "label": "Duct Location",
            "minimum_requirement": target.value,
            "installed": self.duct_location.value if self.duct_location else None,
            "meets_requirement": meets_requirements,
            "warning": warning,
        }

    @cached_property
    def duct_leakage_measure(self):
        meets_requirements = self.duct_leakage is not None
        warning = None
        if not meets_requirements:
            warning = "Please enter the tested duct leakage @CFM50."
        return {
            "section": "Duct Leakage",
            "label": "CFM50",
            "minimum_requirement": None,
            "installed": self.duct_leakage,
            "meets_requirement": meets_requirements,
            "warning": warning,
        }

    @cached_property
    def meet_requirements(self):
        return all(
            [
                self.furnace_location_measure["meets_requirement"],
                self.duct_location_measure["meets_requirement"],
                # self.duct_leakage_measure["meets_requirement"],
            ]
        )

    @cached_property
    def data(self):
        return {
            "furnace_location": self.furnace_location_measure,
            "duct_location": self.duct_location_measure,
            "duct_leakage": self.duct_leakage_measure,
        }

    @cached_property
    def report(self):
        data = "4. High Efficiency HVAC Distribution System\n"
        data += f"  Option Selected: {self.target_credit.value}\n\n"
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
