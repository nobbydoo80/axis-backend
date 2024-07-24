"""air_leakage_specs.py - Axis"""

__author__ = "Steven K"
__date__ = "8/12/21 11:21"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
from django.test import TestCase
from ....calculator.washington_code_credit.specifications import AirLeakageSpecification
from ....eep_programs.washington_code_credit import AirLeakageControl, VentilationType

log = logging.getLogger(__name__)


class AirLeakageSpecificationTests(TestCase):
    @property
    def no_data(self):
        data = {
            "air_leakage_ach": 0.0,
            "ventilation_type": None,
            "ventilation_brand": None,
            "ventilation_model": None,
            "hrv_asre": None,
        }
        return data.copy()

    def _verify_no_data(self, spec, skip_keys=[]):
        self.assertFalse(spec.data["air_leakage_ach"]["meets_requirement"])
        self.assertIsNone(spec.data["air_leakage_ach"]["warning"])
        if "ventilation_type" not in skip_keys:
            self.assertTrue(spec.data["ventilation_type"]["meets_requirement"])
            self.assertIsNone(spec.data["ventilation_type"]["warning"])
        self.assertFalse(spec.data["ventilation_brand"]["meets_requirement"])
        self.assertIsNotNone(spec.data["ventilation_brand"]["warning"])
        self.assertFalse(spec.data["ventilation_model"]["meets_requirement"])
        self.assertIsNotNone(spec.data["ventilation_model"]["warning"])
        if "hrv_asre" not in skip_keys:
            self.assertTrue(spec.data["hrv_asre"]["meets_requirement"])
            self.assertIsNone(spec.data["hrv_asre"]["warning"])
        self.assertFalse(spec.meet_requirements)

    def _verify_passing_no_warning(self, spec):
        self.assertTrue(spec.data["air_leakage_ach"]["meets_requirement"])
        self.assertIsNone(spec.data["air_leakage_ach"]["warning"])
        self.assertTrue(spec.data["ventilation_type"]["meets_requirement"])
        self.assertIsNone(spec.data["ventilation_type"]["warning"])
        self.assertTrue(spec.data["ventilation_brand"]["meets_requirement"])
        self.assertIsNone(spec.data["ventilation_brand"]["warning"])
        self.assertTrue(spec.data["ventilation_model"]["meets_requirement"])
        self.assertIsNone(spec.data["ventilation_model"]["warning"])
        self.assertTrue(spec.data["hrv_asre"]["meets_requirement"])
        self.assertIsNone(spec.data["hrv_asre"]["warning"])
        self.assertTrue(spec.meet_requirements)

    def test_air_leakage_option_0_none(self):
        """Verify when the NONE Option is selected it works"""
        option = AirLeakageControl.NONE

        spec = AirLeakageSpecification(option, **self.no_data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{option.value} No Data"):
            self._verify_no_data(spec)

        data = self.no_data
        data.update(
            {
                "air_leakage_ach": 4,
                "ventilation_brand": "FOO",
                "ventilation_model": "BAR",
            }
        )
        spec = AirLeakageSpecification(option, **data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{option.value} Passing Data"):
            self._verify_passing_no_warning(spec)

        data = self.no_data
        update = {
            "air_leakage_ach": 5.1,
            "ventilation_brand": None,
            "ventilation_model": None,
        }
        data.update(update)
        spec = AirLeakageSpecification(option, **data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{option.value} Failing Data"):
            for key in update:
                self.assertFalse(spec.data[key]["meets_requirement"], f"{key} {option}")
                self.assertIsNotNone(spec.data[key]["warning"], f"{key} {option}")
            self.assertFalse(spec.meet_requirements)

    def test_air_leakage_option_2p1(self):
        """Verify when Option 2.1 is selected it works"""
        option = AirLeakageControl.OPTION_2p1

        spec = AirLeakageSpecification(option, **self.no_data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{option.value} No Data"):
            self._verify_no_data(spec)

        data = self.no_data
        data.update(
            {
                "air_leakage_ach": 2.9,
                "ventilation_brand": "FOO",
                "ventilation_model": "BAR",
            }
        )
        spec = AirLeakageSpecification(option, **data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{option.value} Passing Data"):
            self._verify_passing_no_warning(spec)

        data = self.no_data
        update = {
            "air_leakage_ach": 3.1,
            "ventilation_brand": None,
            "ventilation_model": None,
        }
        data.update(update)
        spec = AirLeakageSpecification(option, **data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{option.value} Failing Data"):
            for key in update:
                self.assertFalse(spec.data[key]["meets_requirement"], f"{key} {option}")
                self.assertIsNotNone(spec.data[key]["warning"], f"{key} {option}")
            self.assertFalse(spec.meet_requirements)

    def test_air_leakage_option_2p2(self):
        """Verify when Option 2.2 is selected it works"""
        option = AirLeakageControl.OPTION_2p2

        spec = AirLeakageSpecification(option, **self.no_data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{option.value} No Data"):
            self._verify_no_data(spec, skip_keys=["ventilation_type", "hrv_asre"])
            self.assertFalse(spec.data["ventilation_type"]["meets_requirement"])
            self.assertIsNotNone(spec.data["ventilation_type"]["warning"])
            self.assertFalse(spec.data["hrv_asre"]["meets_requirement"])
            self.assertIsNone(spec.data["hrv_asre"]["warning"])

        data = self.no_data
        data.update(
            {
                "air_leakage_ach": 1.9,
                "ventilation_type": VentilationType.HRV_ERV,
                "ventilation_brand": "FOO",
                "ventilation_model": "BAR",
                "hrv_asre": 65.0,
            }
        )
        spec = AirLeakageSpecification(option, **data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{option.value} Passing Data"):
            self._verify_passing_no_warning(spec)

        data = self.no_data
        update = {
            "air_leakage_ach": 2.1,
            "ventilation_type": VentilationType.SUPPLY_ONLY,
            "ventilation_brand": None,
            "ventilation_model": None,
            "hrv_asre": 64.9,
        }
        data.update(update)
        spec = AirLeakageSpecification(option, **data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{option.value} Failing Data"):
            for key in update:
                self.assertFalse(spec.data[key]["meets_requirement"], f"{key} {option}")
                self.assertIsNotNone(spec.data[key]["warning"], f"{key} {option}")
            self.assertFalse(spec.meet_requirements)

    def test_air_leakage_option_2p3(self):
        """Verify when Option 2.3 is selected it works"""
        option = AirLeakageControl.OPTION_2p3

        spec = AirLeakageSpecification(option, **self.no_data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{option.value} No Data"):
            self._verify_no_data(spec, skip_keys=["ventilation_type", "hrv_asre"])
            self.assertFalse(spec.data["ventilation_type"]["meets_requirement"])
            self.assertIsNotNone(spec.data["ventilation_type"]["warning"])
            self.assertFalse(spec.data["hrv_asre"]["meets_requirement"])
            self.assertIsNone(spec.data["hrv_asre"]["warning"])

        data = self.no_data
        data.update(
            {
                "air_leakage_ach": 1.4,
                "ventilation_type": VentilationType.HRV_ERV,
                "ventilation_brand": "FOO",
                "ventilation_model": "BAR",
                "hrv_asre": 75.0,
            }
        )
        spec = AirLeakageSpecification(option, **data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{option.value} Passing Data"):
            self._verify_passing_no_warning(spec)

        data = self.no_data
        update = {
            "air_leakage_ach": 1.6,
            "ventilation_type": VentilationType.SUPPLY_ONLY,
            "ventilation_brand": None,
            "ventilation_model": None,
            "hrv_asre": 74.9,
        }
        data.update(update)
        spec = AirLeakageSpecification(option, **data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{option.value} Failing Data"):
            for key in update:
                self.assertFalse(spec.data[key]["meets_requirement"], f"{key} {option}")
                self.assertIsNotNone(spec.data[key]["warning"], f"{key} {option}")
            self.assertFalse(spec.meet_requirements)

    def test_air_leakage_option_2p4(self):
        """Verify when Option 2.4 is selected it works"""
        option = AirLeakageControl.OPTION_2p4

        spec = AirLeakageSpecification(option, **self.no_data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{option.value} No Data"):
            self._verify_no_data(spec, skip_keys=["ventilation_type", "hrv_asre"])
            self.assertFalse(spec.data["ventilation_type"]["meets_requirement"])
            self.assertIsNotNone(spec.data["ventilation_type"]["warning"])
            self.assertFalse(spec.data["hrv_asre"]["meets_requirement"])
            self.assertIsNone(spec.data["hrv_asre"]["warning"])

        data = self.no_data
        data.update(
            {
                "air_leakage_ach": 0.5,
                "ventilation_type": VentilationType.HRV_ERV,
                "ventilation_brand": "FOO",
                "ventilation_model": "BAR",
                "hrv_asre": 80.0,
            }
        )
        spec = AirLeakageSpecification(option, **data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{option.value} Passing Data"):
            self._verify_passing_no_warning(spec)

        data = self.no_data
        update = {
            "air_leakage_ach": 0.7,
            "ventilation_type": VentilationType.SUPPLY_ONLY,
            "ventilation_brand": None,
            "ventilation_model": None,
            "hrv_asre": 9.9,
        }
        data.update(update)
        spec = AirLeakageSpecification(option, **data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{option.value} Failing Data"):
            for key in update:
                self.assertFalse(spec.data[key]["meets_requirement"], f"{key} {option}")
                self.assertIsNotNone(spec.data[key]["warning"], f"{key} {option}")
            self.assertFalse(spec.meet_requirements)
