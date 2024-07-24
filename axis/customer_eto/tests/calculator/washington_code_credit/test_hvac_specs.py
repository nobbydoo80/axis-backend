"""hvac_specs.py - Axis"""

__author__ = "Steven K"
__date__ = "8/12/21 16:15"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
from django.test import TestCase
from ....calculator.washington_code_credit.specifications import HVACSpecification
from ....calculator.washington_code_credit.specifications.hvac import HVACDistributionSpecification
from ....eep_programs.washington_code_credit import (
    HighEfficiencyHVAC,
    HighEfficiencyHVACDistribution,
    DuctLocation,
    FurnaceLocation,
)

log = logging.getLogger(__name__)


class HVACSpecificationTests(TestCase):
    @property
    def no_data(self):
        data = {
            "furnace_brand": None,
            "furnace_model": None,
            "furnace_afue": None,
        }
        return data.copy()

    def _verify_no_data(self, spec):
        self.assertFalse(spec.data["furnace_brand"]["meets_requirement"])
        self.assertIsNotNone(spec.data["furnace_brand"]["warning"])
        self.assertFalse(spec.data["furnace_model"]["meets_requirement"])
        self.assertIsNotNone(spec.data["furnace_model"]["warning"])
        self.assertFalse(spec.data["furnace_afue"]["meets_requirement"])
        self.assertIsNone(spec.data["furnace_afue"]["warning"])
        self.assertFalse(spec.meet_requirements)

    def _verify_passing_no_warning(self, spec):
        self.assertTrue(spec.data["furnace_brand"]["meets_requirement"])
        self.assertIsNone(spec.data["furnace_brand"]["warning"])
        self.assertTrue(spec.data["furnace_model"]["meets_requirement"])
        self.assertIsNone(spec.data["furnace_model"]["warning"])
        self.assertTrue(spec.data["furnace_afue"]["meets_requirement"])
        self.assertIsNone(spec.data["furnace_afue"]["warning"])
        self.assertTrue(spec.meet_requirements)

    def test_hvac_option_0_none(self):
        """Verify when the NONE Option is selected it works"""
        option = HighEfficiencyHVAC.NONE

        spec = HVACSpecification(option, **self.no_data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{option.value} No Data"):
            self._verify_no_data(spec)

        data = self.no_data
        data.update(
            {
                "furnace_brand": "FOO",
                "furnace_model": "BAR",
                "furnace_afue": 95,
            }
        )
        spec = HVACSpecification(option, **data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{option.value} Passing Data"):
            self._verify_passing_no_warning(spec)

        data = self.no_data
        update = {
            "furnace_brand": None,
            "furnace_model": None,
            "furnace_afue": 94,
        }
        data.update(update)
        spec = HVACSpecification(option, **data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{option.value} Failing Data"):
            for key in update:
                self.assertFalse(spec.data[key]["meets_requirement"], f"{key} {option}")
                self.assertIsNotNone(spec.data[key]["warning"], f"{key} {option}")
            self.assertFalse(spec.meet_requirements)

    def _test_hvac_option(self, option):
        """Verify when the Option is selected it works"""

        spec = HVACSpecification(option, **self.no_data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{option.value} No Data"):
            self._verify_no_data(spec)

        data = self.no_data
        data.update(
            {
                "furnace_brand": "FOO",
                "furnace_model": "BAR",
                "furnace_afue": 95,
            }
        )
        spec = HVACSpecification(option, **data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{option.value} Passing Data"):
            self._verify_passing_no_warning(spec)

        data = self.no_data
        update = {
            "furnace_brand": None,
            "furnace_model": None,
            "furnace_afue": 94,
        }
        data.update(update)
        spec = HVACSpecification(option, **data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{option.value} Failing Data"):
            for key in update:
                self.assertFalse(spec.data[key]["meets_requirement"], f"{key} {option}")
                self.assertIsNotNone(spec.data[key]["warning"], f"{key} {option}")
            self.assertFalse(spec.meet_requirements)

    # Note: there is not any difference between these options
    # They are here solely for completeness.

    def test_hvac_option_3p1(self):
        """Verify when the Option 3.1 is selected it works"""
        self._test_hvac_option(HighEfficiencyHVAC.OPTION_3p1)

    def test_hvac_option_3p2(self):
        """Verify when the Option 3.2 is selected it works"""
        self._test_hvac_option(HighEfficiencyHVAC.OPTION_3p2)

    def test_hvac_option_3p3(self):
        """Verify when the Option 3.3 is selected it works"""
        self._test_hvac_option(HighEfficiencyHVAC.OPTION_3p3)

    def test_hvac_option_3p4(self):
        """Verify when the Option 3.4 is selected it works"""
        self._test_hvac_option(HighEfficiencyHVAC.OPTION_3p4)

    def test_hvac_option_3p5(self):
        """Verify when the Option 3.5 is selected it works"""
        self._test_hvac_option(HighEfficiencyHVAC.OPTION_3p5)

    def test_hvac_option_3p6(self):
        """Verify when the Option 3.6 is selected it works"""
        self._test_hvac_option(HighEfficiencyHVAC.OPTION_3p6)


class HVACDistributionSpecificationTests(TestCase):
    @property
    def no_data(self):
        data = {
            "furnace_location": None,
            "duct_location": None,
            "duct_leakage": None,
        }
        return data.copy()

    def _verify_no_data(self, spec, skip_keys=[]):
        if "furnace_location" not in skip_keys:
            self.assertTrue(spec.data["furnace_location"]["meets_requirement"])
            self.assertIsNone(spec.data["furnace_location"]["warning"])
        self.assertFalse(spec.data["duct_location"]["meets_requirement"])
        self.assertIsNone(spec.data["duct_location"]["warning"])
        self.assertFalse(spec.data["duct_leakage"]["meets_requirement"])
        self.assertIsNotNone(spec.data["duct_leakage"]["warning"])
        self.assertFalse(spec.meet_requirements)

    def _verify_passing_no_warning(self, spec):
        self.assertTrue(spec.data["furnace_location"]["meets_requirement"])
        self.assertIsNone(spec.data["furnace_location"]["warning"])
        self.assertTrue(spec.data["duct_location"]["meets_requirement"])
        self.assertIsNone(spec.data["duct_location"]["warning"])
        self.assertTrue(spec.data["duct_leakage"]["meets_requirement"])
        self.assertIsNone(spec.data["duct_leakage"]["warning"])
        self.assertTrue(spec.meet_requirements)

    def test_distribution_option_0_none(self):
        """Verify when the NONE Option is selected it works"""
        option = HighEfficiencyHVACDistribution.NONE

        spec = HVACDistributionSpecification(option, **self.no_data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{option.value} No Data"):
            self._verify_no_data(spec)

        data = self.no_data
        data.update(
            {
                "duct_location": DuctLocation.UNCONDITIONED_SPACE,
                "duct_leakage": 1,
            }
        )
        spec = HVACDistributionSpecification(option, **data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{option.value} Passing Data"):
            self._verify_passing_no_warning(spec)

        data = self.no_data
        update = {
            "duct_location": None,
            "duct_leakage": None,
        }
        data.update(update)
        spec = HVACDistributionSpecification(option, **data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{option.value} Failing Data"):
            for key in update:
                self.assertFalse(spec.data[key]["meets_requirement"], f"{key} {option}")
                if key != "duct_location":
                    self.assertIsNotNone(spec.data[key]["warning"], f"{key} {option}")
            self.assertFalse(spec.meet_requirements)

    def test_distribution_option_4p1(self):
        """Verify when the Option 4p1 is selected it works"""
        option = HighEfficiencyHVACDistribution.OPTION_4p1

        spec = HVACDistributionSpecification(option, **self.no_data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{option.value} No Data"):
            self._verify_no_data(spec)

        data = self.no_data
        data.update(
            {
                "furnace_location": FurnaceLocation.UNCONDITIONED_SPACE,
                "duct_location": DuctLocation.CONDITIONED_SPACE,
                "duct_leakage": 1,
            }
        )
        spec = HVACDistributionSpecification(option, **data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{option.value} Passing Data"):
            self._verify_passing_no_warning(spec)

        data = self.no_data
        update = {
            "duct_location": DuctLocation.UNCONDITIONED_SPACE,
            "duct_leakage": None,
        }
        data.update(update)
        spec = HVACDistributionSpecification(option, **data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{option.value} Failing Data"):
            for key in update:
                self.assertFalse(spec.data[key]["meets_requirement"], f"{key} {option}")
                self.assertIsNotNone(spec.data[key]["warning"], f"{key} {option}")
            self.assertFalse(spec.meet_requirements)

    def test_distribution_option_4p2(self):
        """Verify when the Option 4p2 is selected it works"""
        option = HighEfficiencyHVACDistribution.OPTION_4p2

        spec = HVACDistributionSpecification(option, **self.no_data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{option.value} No Data"):
            self._verify_no_data(spec, skip_keys=["furnace_location"])
            self.assertFalse(spec.data["furnace_location"]["meets_requirement"])
            self.assertIsNone(spec.data["furnace_location"]["warning"])

        data = self.no_data
        data.update(
            {
                "furnace_location": FurnaceLocation.CONDITIONED_SPACE,
                "duct_location": DuctLocation.CONDITIONED_SPACE,
                "duct_leakage": 1,
            }
        )
        spec = HVACDistributionSpecification(option, **data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{option.value} Passing Data"):
            self._verify_passing_no_warning(spec)

        data = self.no_data
        update = {
            "duct_location": DuctLocation.UNCONDITIONED_SPACE,
            "duct_leakage": None,
        }
        data.update(update)
        spec = HVACDistributionSpecification(option, **data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{option.value} Failing Data"):
            for key in update:
                self.assertFalse(spec.data[key]["meets_requirement"], f"{key} {option}")
                self.assertIsNotNone(spec.data[key]["warning"], f"{key} {option}")
            self.assertFalse(spec.meet_requirements)
