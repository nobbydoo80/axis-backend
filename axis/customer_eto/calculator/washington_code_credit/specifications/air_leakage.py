"""air_leakage.py - Axis"""

__author__ = "Steven K"
__date__ = "8/12/21 11:05"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from functools import cached_property

from tabulate import tabulate

from axis.customer_eto.eep_programs.washington_code_credit import VentilationType

log = logging.getLogger(__name__)


class AirLeakageSpecification:
    DEFAULT_WARNING_ADDER = (
        "{} does not meet the minimum requirement. Please review credit selections."
    )

    def __init__(self, target_credit, **kwargs):
        self.target_credit = target_credit

        self.air_leakage_ach = kwargs.get("air_leakage_ach")
        self.ventilation_type = kwargs.get("ventilation_type")
        self.ventilation_brand = kwargs.get("ventilation_brand")
        self.ventilation_model = kwargs.get("ventilation_model")
        self.hrv_asre = kwargs.get("hrv_asre")

    @cached_property
    def constants(self):
        from ..constants import defaults

        return defaults.AIR_LEAKAGE[self.target_credit]

    @cached_property
    def air_leakage_ach_measure(self):
        target = self.constants.get("air_leakage_ach")
        meets_requirements, warning = False, None
        if self.air_leakage_ach > 0:
            meets_requirements = self.air_leakage_ach < target
            if not meets_requirements:
                warning = self.DEFAULT_WARNING_ADDER.format("AIR LEAKAGE")
        return {
            "section": "Air Leakage",
            "label": "ACH50",
            "minimum_requirement": target,
            "installed": self.air_leakage_ach,
            "meets_requirement": meets_requirements,
            "warning": warning,
        }

    @cached_property
    def ventilation_type_measure(self):
        target = self.constants.get("ventilation_type")
        meets_requirements, warning = False, None
        meets_requirements = any(
            [
                self.ventilation_type == VentilationType.HRV_ERV,
                target and target == self.ventilation_type,
                target is None,
            ]
        )
        if not meets_requirements:
            warning = self.DEFAULT_WARNING_ADDER.format("Ventilation type")
        return {
            "section": "Ventilation",
            "label": "Type",
            "minimum_requirement": target.value if target else None,
            "installed": self.ventilation_type.value if self.ventilation_type else None,
            "meets_requirement": meets_requirements,
            "warning": warning,
        }

    @cached_property
    def ventilation_brand_measure(self):
        meets_requirements = self.ventilation_brand is not None
        warning = None
        if not meets_requirements:
            warning = "Please enter a ventilation brand name."
        return {
            "section": "Ventilation",
            "label": "Brand Name",
            "minimum_requirement": None,
            "installed": self.ventilation_brand,
            "meets_requirement": meets_requirements,
            "warning": warning,
        }

    @cached_property
    def ventilation_model_measure(self):
        meets_requirements = self.ventilation_model is not None
        warning = None
        if not meets_requirements:
            warning = "Please enter a ventilation model number."
        return {
            "section": "Ventilation",
            "label": "Model Number",
            "minimum_requirement": None,
            "installed": self.ventilation_model,
            "meets_requirement": meets_requirements,
            "warning": warning,
        }

    @cached_property
    def hrv_asre_measure(self):
        target = self.constants.get("hrv_asre")
        meets_requirements = target is None
        if self.hrv_asre and target:
            meets_requirements = self.hrv_asre >= target
        warning = None
        if self.hrv_asre and not meets_requirements:
            warning = self.DEFAULT_WARNING_ADDER.format("HRV ASRE")
        return {
            "section": "Ventilation",
            "label": "HRV  ASRE% (0-100)",
            "minimum_requirement": target,
            "installed": self.hrv_asre,
            "meets_requirement": meets_requirements,
            "warning": warning,
        }

    @cached_property
    def meet_requirements(self):
        return all(
            [
                self.air_leakage_ach_measure["meets_requirement"],
                self.ventilation_type_measure["meets_requirement"],
                # self.ventilation_brand_measure["meets_requirement"],
                # self.ventilation_model_measure["meets_requirement"],
                self.hrv_asre_measure["meets_requirement"],
            ]
        )

    @cached_property
    def data(self):
        return {
            "air_leakage_ach": self.air_leakage_ach_measure,
            "ventilation_type": self.ventilation_type_measure,
            "ventilation_brand": self.ventilation_brand_measure,
            "ventilation_model": self.ventilation_model_measure,
            "hrv_asre": self.hrv_asre_measure,
        }

    @cached_property
    def report(self):
        data = "2. Air Leakage Control & Efficient Ventilation Options\n"
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
