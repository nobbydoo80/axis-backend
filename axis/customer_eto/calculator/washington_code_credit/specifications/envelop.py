"""specifications.py - Axis"""

__author__ = "Steven K"
__date__ = "8/11/21 12:40"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
from functools import cached_property
from tabulate import tabulate

from axis.customer_eto.eep_programs.washington_code_credit import FramingType
from axis.customer_eto.enumerations import YesNo

log = logging.getLogger(__name__)


class EnvelopeSpecification:
    DEFAULT_WARNING_ADDER = (
        "{} does not meet the minimum requirement. "
        "Please review credit selections or submit UA reduction workbook."
    )

    def __init__(self, target_credit, **kwargs):
        self.target_credit = target_credit
        self.wall_cavity_r_value = kwargs.get("wall_cavity_r_value", 0)
        self.wall_continuous_r_value = kwargs.get("wall_continuous_r_value", 0)
        self.framing_type = kwargs.get("framing_type", None)
        self.window_u_value = kwargs.get("window_u_value", 0.0)
        self.window_shgc = kwargs.get("window_shgc", 0.0)
        self.floor_cavity_r_value = kwargs.get("floor_cavity_r_value", 0)
        self.slab_perimeter_r_value = kwargs.get("slab_perimeter_r_value", 0)
        self.under_slab_r_value = kwargs.get("under_slab_r_value", 0)
        self.ceiling_r_value = kwargs.get("ceiling_r_value", 0)
        self.raised_heel = kwargs.get("raised_heel", None)
        self.total_ua_alternative = kwargs.get("total_ua_alternative", None)

    @cached_property
    def constants(self):
        from ..constants import defaults

        return defaults.BUILDING_ENVELOPE_OPTIONS[self.target_credit]

    @cached_property
    def wall_cavity_r_value_measure(self):
        target = self.constants.get("wall_cavity_r_value")
        warning = None
        meets_requirement = self.wall_cavity_r_value >= target
        if (
            target > 0
            and self.wall_cavity_r_value > 0.0
            and not meets_requirement
            and not self.meets_ua_alternative_measure
        ):
            warning = self.DEFAULT_WARNING_ADDER.format("WALL CAVITY INSULATION")
        return {
            "section": "Above Grade Walls",
            "label": "Wall Cavity (R-)",
            "minimum_requirement": target,
            "installed": self.wall_cavity_r_value,
            "meets_requirement": meets_requirement,
            "warning": warning,
        }

    @cached_property
    def wall_continuous_r_value_measure(self):
        target = self.constants.get("wall_continuous_r_value")
        meets_requirement, warning = True, None
        if target:
            meets_requirement = self.wall_continuous_r_value >= target
        if (
            target
            and self.wall_continuous_r_value > 0
            and not meets_requirement
            and not self.meets_ua_alternative_measure
        ):
            warning = self.DEFAULT_WARNING_ADDER.format("WALL CONTINUOUS INSULATION")

        return {
            "section": "Above Grade Walls",
            "label": "Wall Continuous (R -)",
            "minimum_requirement": target,
            "installed": self.wall_continuous_r_value,
            "meets_requirement": meets_requirement,
            "warning": warning,
        }

    @cached_property
    def framing_type_measure(self):
        target = self.constants.get("framing_type")
        meets_requirement = target == FramingType.INTERMEDIATE or target == self.framing_type

        warning = None
        if not meets_requirement:
            warning = self.DEFAULT_WARNING_ADDER.format("AGW framing")

        return {
            "section": "Above Grade Walls",
            "label": "Framing Type",
            "minimum_requirement": target.value,
            "installed": self.framing_type.value if self.framing_type else "-",
            "meets_requirement": meets_requirement,
            "warning": warning,
        }

    @cached_property
    def window_u_value_measure(self):
        target = self.constants.get("window_u_value")
        warning, meets_requirement = None, False

        if self.window_u_value > 0.0 and target:
            meets_requirement = self.window_u_value <= target
            if not meets_requirement and not self.meets_ua_alternative_measure:
                warning = self.DEFAULT_WARNING_ADDER.format("WINDOW U-VALUE")
        return {
            "section": "Vertical Fennestration",
            "label": "Window (U-)",
            "minimum_requirement": target,
            "installed": self.window_u_value,
            "meets_requirement": meets_requirement,
            "warning": warning,
        }

    @cached_property
    def window_shgc_measure(self):
        target = self.constants.get("window_shgc")
        return {
            "section": "Vertical Fennestration",
            "label": "Window (SHGC-)",
            "minimum_requirement": target,
            "installed": self.window_shgc,
            "meets_requirement": True,
            "warning": None,
        }

    @cached_property
    def floor_cavity_r_value_measure(self):
        target = self.constants.get("floor_cavity_r_value")
        warning, meets_requirement = None, False
        if self.floor_cavity_r_value > 0 and target:
            meets_requirement = self.floor_cavity_r_value >= target
            if not meets_requirement and not self.meets_ua_alternative_measure:
                warning = self.DEFAULT_WARNING_ADDER.format("FLOOR CAVITY INSULATION")
        return {
            "section": "Floors",
            "label": "Floor Cavity (R-) (0.0 if slab)",
            "minimum_requirement": target,
            "installed": self.floor_cavity_r_value,
            "meets_requirement": meets_requirement,
            "warning": warning,
        }

    @cached_property
    def slab_perimeter_r_value_measure(self):
        target = self.constants.get("slab_perimeter_r_value")
        warning, meets_requirement = None, False
        if self.slab_perimeter_r_value > 0 and target:
            meets_requirement = self.slab_perimeter_r_value >= target
            if not meets_requirement and not self.meets_ua_alternative_measure:
                warning = self.DEFAULT_WARNING_ADDER.format("SLAB PERIMETER INSULATION")
        return {
            "section": "Floors",
            "label": "Slab Perimeter (R-) (0.0 if no slab)",
            "minimum_requirement": target,
            "installed": self.slab_perimeter_r_value,
            "meets_requirement": meets_requirement,
            "warning": warning,
        }

    @cached_property
    def under_slab_r_value_measure(self):
        target = self.constants.get("under_slab_r_value")
        warning, meets_requirement = None, True
        if self.under_slab_r_value > 0 and target:
            meets_requirement = self.under_slab_r_value >= target
            if not meets_requirement and not self.meets_ua_alternative_measure:
                warning = self.DEFAULT_WARNING_ADDER.format("UNDERSLAB INSULATION")

        return {
            "section": "Floors",
            "label": "Under slab (R-) (0.0 if no slab)",
            "minimum_requirement": target,
            "installed": self.under_slab_r_value,
            "meets_requirement": meets_requirement,
            "warning": warning,
        }

    @cached_property
    def ceiling_r_value_measure(self):
        target = self.constants.get("ceiling_r_value")
        meets_requirement = self.ceiling_r_value >= target
        warning = None
        if (
            self.ceiling_r_value > 0
            and not meets_requirement
            and not self.meets_ua_alternative_measure
        ):
            warning = self.DEFAULT_WARNING_ADDER.format("CEILING INSULATION")
        return {
            "section": "Ceiling",
            "label": "Ceiling (R-)",
            "minimum_requirement": target,
            "installed": self.ceiling_r_value,
            "meets_requirement": meets_requirement,
            "warning": warning,
        }

    @cached_property
    def raised_heel_measure(self):
        target = self.constants.get("raised_heel")
        meet_requirement = True
        warning = None
        if self.raised_heel:
            if target == YesNo.NO:
                meet_requirement = True
            elif target == YesNo.YES and self.raised_heel.value == "Yes":
                meet_requirement = True
            else:
                meet_requirement = False
            if not meet_requirement:
                warning = self.DEFAULT_WARNING_ADDER.format("RAISED HEEL TRUSS")

        return {
            "section": "Ceiling",
            "label": "Raised Heel",
            "minimum_requirement": target.value,
            "installed": self.raised_heel.value if self.raised_heel else "-",
            "meets_requirement": meet_requirement,
            "warning": warning,
        }

    @cached_property
    def meets_ua_alternative_measure(self):
        return self.total_ua_alternative_measure["meets_requirement"]

    @cached_property
    def total_ua_alternative_measure(self):
        target = self.constants.get("total_ua_alternative")
        meets_requirement, warning = False, None
        # D22 Minimum (target)
        # E22 total_ua_alternative
        if self.total_ua_alternative and target:
            meets_requirement = self.total_ua_alternative >= target
            warning = "Please submit a UA Reduction Form"
            if not meets_requirement:
                warning = self.DEFAULT_WARNING_ADDER.format("UA REDUCTION")
        # if target and not not self.total_ua_alternative:
        #     meets_requirement = False
        #     warning = self.DEFAULT_WARNING_ADDER.format("UA REDUCTION")
        if self.total_ua_alternative is not None and target is None:
            warning = "Not Applicable"
        return {
            "section": "Total UA Alternative (Opt)",
            "label": "UA Reduction",
            "minimum_requirement": target,
            "installed": self.total_ua_alternative,
            "meets_requirement": meets_requirement,
            "warning": warning,
        }

    @cached_property
    def meet_requirements(self):
        if self.total_ua_alternative_measure["meets_requirement"]:
            return True

        return all(
            [
                self.wall_cavity_r_value_measure["meets_requirement"],
                self.wall_continuous_r_value_measure["meets_requirement"],
                self.framing_type_measure["meets_requirement"],
                self.window_u_value_measure["meets_requirement"],
                self.window_shgc_measure["meets_requirement"],
                self.floor_cavity_r_value_measure["meets_requirement"],
                self.slab_perimeter_r_value_measure["meets_requirement"],
                self.under_slab_r_value_measure["meets_requirement"],
                self.ceiling_r_value_measure["meets_requirement"],
                self.raised_heel_measure["meets_requirement"],
            ]
        )

    @cached_property
    def data(self):
        return {
            "wall_cavity_r_value": self.wall_cavity_r_value_measure,
            "wall_continuous_r_value": self.wall_continuous_r_value_measure,
            "framing_type": self.framing_type_measure,
            "window_u_value": self.window_u_value_measure,
            "window_shgc": self.window_shgc_measure,
            "floor_cavity_r_value": self.floor_cavity_r_value_measure,
            "slab_perimeter_r_value": self.slab_perimeter_r_value_measure,
            "under_slab_r_value": self.under_slab_r_value_measure,
            "ceiling_r_value": self.ceiling_r_value_measure,
            "raised_heel": self.raised_heel_measure,
            "total_ua_alternative": self.total_ua_alternative_measure,
        }

    @cached_property
    def report(self):
        data = "1. Building Elements\n"
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
