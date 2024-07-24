"""envelope_specs.py - Axis"""

__author__ = "Steven K"
__date__ = "8/11/21 14:48"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from django.test import TestCase

from axis.customer_eto.calculator.washington_code_credit.specifications import EnvelopeSpecification
from axis.customer_eto.eep_programs.washington_code_credit import (
    BuildingEnvelope,
    FramingType,
)
from axis.customer_eto.enumerations import YesNo

log = logging.getLogger(__name__)


class EnvelopeSpecificationTests(TestCase):
    """This is how we test the guts of the calculator"""

    @property
    def no_data(self):
        data = {
            "wall_cavity_r_value": 0.0,
            "wall_continuous_r_value": 0.0,
            "framing_type": None,
            "window_u_value": 0.0,
            "window_shgc": None,
            "floor_cavity_r_value": 0.0,
            "slab_perimeter_r_value": 0.0,
            "under_slab_r_value": 0.0,
            "ceiling_r_value": 0.0,
            "raised_heel": None,
            "total_ua_alternative": None,
        }
        return data.copy()

    def _verify_building_envelope_no_data(self, spec, skip_keys=[]):
        """No data should always return this"""
        if "wall_cavity_r_value" not in skip_keys:
            self.assertFalse(spec.data["wall_cavity_r_value"]["meets_requirement"])
            self.assertIsNone(spec.data["wall_cavity_r_value"]["warning"])
        if "wall_continuous_r_value" not in skip_keys:
            self.assertTrue(spec.data["wall_continuous_r_value"]["meets_requirement"])
            self.assertIsNone(spec.data["wall_continuous_r_value"]["warning"])
        if "framing_type" not in skip_keys:
            self.assertTrue(spec.data["framing_type"]["meets_requirement"])
            self.assertIsNone(spec.data["framing_type"]["warning"])
        self.assertFalse(spec.data["window_u_value"]["meets_requirement"])
        self.assertIsNone(spec.data["window_u_value"]["warning"])
        self.assertTrue(spec.data["window_shgc"]["meets_requirement"])
        self.assertIsNone(spec.data["window_shgc"]["warning"])
        self.assertFalse(spec.data["floor_cavity_r_value"]["meets_requirement"])
        self.assertIsNone(spec.data["floor_cavity_r_value"]["warning"])
        self.assertFalse(spec.data["slab_perimeter_r_value"]["meets_requirement"])
        self.assertIsNone(spec.data["slab_perimeter_r_value"]["warning"])
        self.assertTrue(spec.data["under_slab_r_value"]["meets_requirement"])
        self.assertIsNone(spec.data["under_slab_r_value"]["warning"])
        self.assertFalse(spec.data["ceiling_r_value"]["meets_requirement"])
        self.assertIsNone(spec.data["ceiling_r_value"]["warning"])
        self.assertTrue(spec.data["raised_heel"]["meets_requirement"])
        self.assertIsNone(spec.data["raised_heel"]["warning"])
        self.assertFalse(spec.data["total_ua_alternative"]["meets_requirement"])
        self.assertIsNone(spec.data["total_ua_alternative"]["warning"])
        self.assertFalse(spec.meet_requirements)

    def _verify_building_envelope_passing_no_warning(self, spec):
        """Verify we completely pass"""
        self.assertTrue(spec.data["wall_cavity_r_value"]["meets_requirement"])
        self.assertIsNone(spec.data["wall_cavity_r_value"]["warning"])
        self.assertTrue(spec.data["wall_continuous_r_value"]["meets_requirement"])
        self.assertIsNone(spec.data["wall_continuous_r_value"]["warning"])
        self.assertTrue(spec.data["framing_type"]["meets_requirement"])
        self.assertIsNone(spec.data["framing_type"]["warning"])
        self.assertTrue(spec.data["window_u_value"]["meets_requirement"])
        self.assertIsNone(spec.data["window_u_value"]["warning"])
        self.assertTrue(spec.data["window_shgc"]["meets_requirement"])
        self.assertIsNone(spec.data["window_shgc"]["warning"])
        self.assertTrue(spec.data["floor_cavity_r_value"]["meets_requirement"])
        self.assertIsNone(spec.data["floor_cavity_r_value"]["warning"])
        self.assertTrue(spec.data["slab_perimeter_r_value"]["meets_requirement"])
        self.assertIsNone(spec.data["slab_perimeter_r_value"]["warning"])
        self.assertTrue(spec.data["under_slab_r_value"]["meets_requirement"])
        self.assertIsNone(spec.data["under_slab_r_value"]["warning"])
        self.assertTrue(spec.data["ceiling_r_value"]["meets_requirement"])
        self.assertIsNone(spec.data["ceiling_r_value"]["warning"])
        self.assertTrue(spec.data["raised_heel"]["meets_requirement"])
        self.assertIsNone(spec.data["raised_heel"]["warning"])
        self.assertTrue(spec.meet_requirements)

    def test_building_envelope_option_0_none(self):
        """Verify when the NONE Option is selected it works"""
        option = BuildingEnvelope.NONE

        spec = EnvelopeSpecification(option, **self.no_data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{option.value} No Data"):
            self._verify_building_envelope_no_data(spec)

        data = self.no_data
        data.update(
            {
                "wall_cavity_r_value": 22,
                "framing_type": FramingType.ADVANCED,
                "window_u_value": 0.3,
                "floor_cavity_r_value": 30,
                "slab_perimeter_r_value": 11,
                "ceiling_r_value": 52.1,
                "raised_heel": YesNo.YES,
            }
        )
        spec = EnvelopeSpecification(option, **data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{option.value} Passing Data"):
            self.assertFalse(spec.data["total_ua_alternative"]["meets_requirement"])
            self.assertIsNone(spec.data["total_ua_alternative"]["warning"])
            self._verify_building_envelope_passing_no_warning(spec)

    def test_building_envelope_option_1p1(self):
        """Verify when Option 1.1 is selected it works"""
        option = BuildingEnvelope.OPTION_1p1

        spec = EnvelopeSpecification(option, **self.no_data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{option.value} No Data"):
            self._verify_building_envelope_no_data(spec)

        data = self.no_data
        data.update(
            {
                "wall_cavity_r_value": 21,
                "window_u_value": 0.22,
                "floor_cavity_r_value": 31,
                "slab_perimeter_r_value": 11,
                "ceiling_r_value": 49,
            }
        )
        spec = EnvelopeSpecification(option, **data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{option.value} Passing Data"):
            self.assertFalse(spec.data["total_ua_alternative"]["meets_requirement"])
            self.assertIsNone(spec.data["total_ua_alternative"]["warning"])
            self._verify_building_envelope_passing_no_warning(spec)

        data = self.no_data
        update = {
            "wall_cavity_r_value": 1,
            "window_u_value": 0.25,
            "floor_cavity_r_value": 29,
            "slab_perimeter_r_value": 9,
            "ceiling_r_value": 48,
            "total_ua_alternative": 0.5,
        }
        data.update(update)
        spec = EnvelopeSpecification(option, **data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{option.value} Failing Data"):
            for key in update:
                self.assertFalse(spec.data[key]["meets_requirement"], f"{key} {option}")
                self.assertIsNotNone(spec.data[key]["warning"], f"{key} {option}")
            self.assertFalse(spec.meet_requirements)

    def test_building_envelope_option_1p2(self):
        """Verify when Option 1.2 is selected it works"""
        option = BuildingEnvelope.OPTION_1p2

        spec = EnvelopeSpecification(option, **self.no_data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{option.value} No Data"):
            self._verify_building_envelope_no_data(spec)

        data = self.no_data
        data.update(
            {
                "wall_cavity_r_value": 21,
                "window_u_value": 0.19,
                "floor_cavity_r_value": 31,
                "slab_perimeter_r_value": 11,
                "ceiling_r_value": 49,
            }
        )
        spec = EnvelopeSpecification(option, **data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{option.value} Passing Data"):
            self.assertFalse(spec.data["total_ua_alternative"]["meets_requirement"])
            self.assertIsNone(spec.data["total_ua_alternative"]["warning"])
            self._verify_building_envelope_passing_no_warning(spec)

        data = self.no_data
        update = {
            "wall_cavity_r_value": 1,
            "window_u_value": 0.21,
            "floor_cavity_r_value": 29,
            "slab_perimeter_r_value": 9,
            "ceiling_r_value": 48,
            "total_ua_alternative": 0.5,
        }
        data.update(update)
        spec = EnvelopeSpecification(option, **data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{option.value} Failing Data"):
            for key in update:
                self.assertFalse(spec.data[key]["meets_requirement"], f"{key} {option}")
                self.assertIsNotNone(spec.data[key]["warning"], f"{key} {option}")
            self.assertFalse(spec.meet_requirements)

    def test_building_envelope_option_1p3a(self):
        """Verify when Option 1.2 is selected it works"""
        option = BuildingEnvelope.OPTION_1p3a

        spec = EnvelopeSpecification(option, **self.no_data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{option.value} No Data"):
            self._verify_building_envelope_no_data(spec)

        data = self.no_data
        data.update(
            {
                "wall_cavity_r_value": 21,
                "window_u_value": 0.28,
                "floor_cavity_r_value": 38,
                "slab_perimeter_r_value": 10,
                "under_slab_r_value": 10,
                "ceiling_r_value": 49,
            }
        )
        spec = EnvelopeSpecification(option, **data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{option.value} Passing Data"):
            self.assertFalse(spec.data["total_ua_alternative"]["meets_requirement"])
            self._verify_building_envelope_passing_no_warning(spec)

        data = self.no_data
        update = {
            "wall_cavity_r_value": 20,
            "window_u_value": 0.29,
            "floor_cavity_r_value": 37,
            "slab_perimeter_r_value": 9,
            "under_slab_r_value": 9,
            "ceiling_r_value": 48,
            "total_ua_alternative": 4.0,
        }
        data.update(update)
        spec = EnvelopeSpecification(option, **data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{option.value} Failing Data"):
            for key in update:
                self.assertFalse(spec.data[key]["meets_requirement"], f"{key} {option}")
                self.assertIsNotNone(spec.data[key]["warning"], f"{key} {option}")
            self.assertFalse(spec.meet_requirements)

        data.update({"total_ua_alternative": 5.0})
        spec = EnvelopeSpecification(option, **data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)
        with self.subTest(f"{option.value} Passing UA"):
            self.assertTrue(spec.data["total_ua_alternative"]["meets_requirement"])
            self.assertIsNotNone(spec.data["total_ua_alternative"]["warning"])
            update.pop("total_ua_alternative")
            for key in update:
                self.assertIsNone(spec.data[key]["warning"], f"{key} {option}")
            self.assertTrue(spec.meet_requirements)

    def test_building_envelope_option_1p3b(self):
        """Verify when Option 1.3b is selected it works"""
        option = BuildingEnvelope.OPTION_1p3b

        spec = EnvelopeSpecification(option, **self.no_data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{option.value} No Data"):
            self._verify_building_envelope_no_data(spec)

        data = self.no_data
        data.update(
            {
                "wall_cavity_r_value": 21,
                "window_u_value": 0.30,
                "floor_cavity_r_value": 30,
                "slab_perimeter_r_value": 10,
                "ceiling_r_value": 49,
            }
        )
        spec = EnvelopeSpecification(option, **data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{option.value} Passing Data"):
            self.assertFalse(spec.data["total_ua_alternative"]["meets_requirement"])
            self._verify_building_envelope_passing_no_warning(spec)

        data = self.no_data
        update = {
            "wall_cavity_r_value": 20,
            "window_u_value": 0.31,
            "floor_cavity_r_value": 29,
            "slab_perimeter_r_value": 9,
            "ceiling_r_value": 48,
            "total_ua_alternative": 4.0,
        }
        data.update(update)
        spec = EnvelopeSpecification(option, **data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{option.value} Failing Data"):
            for key in update:
                self.assertFalse(spec.data[key]["meets_requirement"], f"{key} {option}")
                self.assertIsNotNone(spec.data[key]["warning"], f"{key} {option}")
            self.assertFalse(spec.meet_requirements)

        data.update({"total_ua_alternative": 5.0})
        spec = EnvelopeSpecification(option, **data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)
        with self.subTest(f"{option.value} Passing UA"):
            self.assertTrue(spec.data["total_ua_alternative"]["meets_requirement"])
            self.assertIsNotNone(spec.data["total_ua_alternative"]["warning"])
            update.pop("total_ua_alternative")
            for key in update:
                self.assertIsNone(spec.data[key]["warning"], f"{key} {option}")
            self.assertTrue(spec.meet_requirements)

    def test_building_envelope_option_1p4a(self):
        """Verify when Option 1.4a is selected it works"""
        option = BuildingEnvelope.OPTION_1p4a

        spec = EnvelopeSpecification(option, **self.no_data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{option.value} No Data"):
            self._verify_building_envelope_no_data(spec, ["wall_continuous_r_value"])
            self.assertFalse(spec.data["wall_continuous_r_value"]["meets_requirement"])
            self.assertIsNone(spec.data["wall_continuous_r_value"]["warning"])

        data = self.no_data
        data.update(
            {
                "wall_cavity_r_value": 21,
                "wall_continuous_r_value": 4,
                "window_u_value": 0.25,
                "floor_cavity_r_value": 38,
                "slab_perimeter_r_value": 10,
                "under_slab_r_value": 10,
                "ceiling_r_value": 49,
            }
        )
        spec = EnvelopeSpecification(option, **data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{option.value} Passing Data"):
            self.assertFalse(spec.data["total_ua_alternative"]["meets_requirement"])
            self._verify_building_envelope_passing_no_warning(spec)

        data = self.no_data
        update = {
            "wall_cavity_r_value": 20,
            "wall_continuous_r_value": 3,
            "window_u_value": 0.26,
            "floor_cavity_r_value": 37,
            "slab_perimeter_r_value": 9,
            "under_slab_r_value": 9,
            "ceiling_r_value": 48,
            "total_ua_alternative": 14.0,
        }
        data.update(update)
        spec = EnvelopeSpecification(option, **data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{option.value} Failing Data"):
            for key in update:
                self.assertFalse(spec.data[key]["meets_requirement"], f"{key} {option}")
                self.assertIsNotNone(spec.data[key]["warning"], f"{key} {option}")
            self.assertFalse(spec.meet_requirements)

        data.update({"total_ua_alternative": 15.0})
        spec = EnvelopeSpecification(option, **data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)
        with self.subTest(f"{option.value} Passing UA"):
            self.assertTrue(spec.data["total_ua_alternative"]["meets_requirement"])
            self.assertIsNotNone(spec.data["total_ua_alternative"]["warning"])
            update.pop("total_ua_alternative")
            for key in update:
                self.assertIsNone(spec.data[key]["warning"], f"{key} {option}")
            self.assertTrue(spec.meet_requirements)

    def test_building_envelope_option_1p4b(self):
        """Verify when Option 1.4b is selected it works"""
        option = BuildingEnvelope.OPTION_1p4b

        spec = EnvelopeSpecification(option, **self.no_data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{option.value} No Data"):
            self._verify_building_envelope_no_data(spec)

        data = self.no_data
        data.update(
            {
                "wall_cavity_r_value": 21,
                "window_u_value": 0.30,
                "floor_cavity_r_value": 30,
                "slab_perimeter_r_value": 10,
                "ceiling_r_value": 49,
            }
        )
        spec = EnvelopeSpecification(option, **data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{option.value} Passing Data"):
            self.assertFalse(spec.data["total_ua_alternative"]["meets_requirement"])
            self._verify_building_envelope_passing_no_warning(spec)

        data = self.no_data
        update = {
            "wall_cavity_r_value": 20,
            "window_u_value": 0.31,
            "floor_cavity_r_value": 29,
            "slab_perimeter_r_value": 9,
            "ceiling_r_value": 48,
            "total_ua_alternative": 14.0,
        }
        data.update(update)
        spec = EnvelopeSpecification(option, **data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{option.value} Failing Data"):
            for key in update:
                self.assertFalse(spec.data[key]["meets_requirement"], f"{key} {option}")
                self.assertIsNotNone(spec.data[key]["warning"], f"{key} {option}")
            self.assertFalse(spec.meet_requirements)

        data.update({"total_ua_alternative": 15.0})
        spec = EnvelopeSpecification(option, **data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)
        with self.subTest(f"{option.value} Passing UA"):
            self.assertTrue(spec.data["total_ua_alternative"]["meets_requirement"])
            self.assertIsNotNone(spec.data["total_ua_alternative"]["warning"])
            update.pop("total_ua_alternative")
            for key in update:
                self.assertIsNone(spec.data[key]["warning"], f"{key} {option}")
            self.assertTrue(spec.meet_requirements)

    def test_building_envelope_option_1p5a(self):
        """Verify when Option 1.5a is selected it works"""
        option = BuildingEnvelope.OPTION_1p5a

        spec = EnvelopeSpecification(option, **self.no_data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{option.value} No Data"):
            self._verify_building_envelope_no_data(spec, ["wall_continuous_r_value"])
            self.assertFalse(spec.data["wall_continuous_r_value"]["meets_requirement"])
            self.assertIsNone(spec.data["wall_continuous_r_value"]["warning"])

        data = self.no_data
        data.update(
            {
                "wall_cavity_r_value": 21,
                "wall_continuous_r_value": 12,
                "window_u_value": 0.22,
                "floor_cavity_r_value": 38,
                "slab_perimeter_r_value": 10,
                "under_slab_r_value": 10,
                "ceiling_r_value": 49,
                "raised_heel": YesNo.YES,
            }
        )
        spec = EnvelopeSpecification(option, **data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{option.value} Passing Data"):
            self.assertFalse(spec.data["total_ua_alternative"]["meets_requirement"])
            self._verify_building_envelope_passing_no_warning(spec)

        data = self.no_data
        update = {
            "wall_cavity_r_value": 20,
            "wall_continuous_r_value": 11,
            "window_u_value": 0.23,
            "floor_cavity_r_value": 37,
            "slab_perimeter_r_value": 9,
            "under_slab_r_value": 9,
            "ceiling_r_value": 48,
            "raised_heel": YesNo.NO,
            "total_ua_alternative": 29.0,
        }
        data.update(update)
        spec = EnvelopeSpecification(option, **data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{option.value} Failing Data"):
            for key in update:
                self.assertFalse(spec.data[key]["meets_requirement"], f"{key} {option}")
                self.assertIsNotNone(spec.data[key]["warning"], f"{key} {option}")
            self.assertFalse(spec.meet_requirements)

        data.update({"total_ua_alternative": 30.0})
        spec = EnvelopeSpecification(option, **data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)
        with self.subTest(f"{option.value} Passing UA"):
            self.assertTrue(spec.data["total_ua_alternative"]["meets_requirement"])
            self.assertIsNotNone(spec.data["total_ua_alternative"]["warning"])
            update.pop("total_ua_alternative")
            self.assertFalse(spec.data["raised_heel"]["meets_requirement"])
            self.assertIsNotNone(spec.data["raised_heel"]["warning"])
            update.pop("raised_heel")
            for key in update:
                self.assertIsNone(spec.data[key]["warning"], f"{key} {option}")
            self.assertTrue(spec.meet_requirements)

    def test_building_envelope_option_1p5b(self):
        """Verify when Option 1.5b is selected it works"""
        option = BuildingEnvelope.OPTION_1p5b

        spec = EnvelopeSpecification(option, **self.no_data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{option.value} No Data"):
            self._verify_building_envelope_no_data(spec)

        data = self.no_data
        data.update(
            {
                "wall_cavity_r_value": 21,
                "window_u_value": 0.30,
                "floor_cavity_r_value": 30,
                "slab_perimeter_r_value": 10,
                "ceiling_r_value": 49,
            }
        )
        spec = EnvelopeSpecification(option, **data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{option.value} Passing Data"):
            self.assertFalse(spec.data["total_ua_alternative"]["meets_requirement"])
            self._verify_building_envelope_passing_no_warning(spec)

        data = self.no_data
        update = {
            "wall_cavity_r_value": 20,
            "window_u_value": 0.31,
            "floor_cavity_r_value": 29,
            "slab_perimeter_r_value": 9,
            "ceiling_r_value": 48,
            "total_ua_alternative": 29.0,
        }
        data.update(update)
        spec = EnvelopeSpecification(option, **data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{option.value} Failing Data"):
            for key in update:
                self.assertFalse(spec.data[key]["meets_requirement"], f"{key} {option}")
                self.assertIsNotNone(spec.data[key]["warning"], f"{key} {option}")
            self.assertFalse(spec.meet_requirements)

        data.update({"total_ua_alternative": 30.0})
        spec = EnvelopeSpecification(option, **data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)
        with self.subTest(f"{option.value} Passing UA"):
            self.assertTrue(spec.data["total_ua_alternative"]["meets_requirement"])
            self.assertIsNotNone(spec.data["total_ua_alternative"]["warning"])
            update.pop("total_ua_alternative")
            for key in update:
                self.assertIsNone(spec.data[key]["warning"], f"{key} {option}")
            self.assertTrue(spec.meet_requirements)

    def test_building_envelope_option_1p6a(self):
        """Verify when Option 1.5a is selected it works"""
        option = BuildingEnvelope.OPTION_1p6a

        spec = EnvelopeSpecification(option, **self.no_data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{option.value} No Data"):
            self._verify_building_envelope_no_data(spec, ["wall_continuous_r_value"])
            self.assertFalse(spec.data["wall_continuous_r_value"]["meets_requirement"])
            self.assertIsNone(spec.data["wall_continuous_r_value"]["warning"])

        data = self.no_data
        data.update(
            {
                "wall_cavity_r_value": 21,
                "wall_continuous_r_value": 16,
                "window_u_value": 0.18,
                "floor_cavity_r_value": 48,
                "slab_perimeter_r_value": 20,
                "under_slab_r_value": 20,
                "ceiling_r_value": 60,
                "raised_heel": YesNo.YES,
            }
        )
        spec = EnvelopeSpecification(option, **data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{option.value} Passing Data"):
            self.assertFalse(spec.data["total_ua_alternative"]["meets_requirement"])
            self._verify_building_envelope_passing_no_warning(spec)

        data = self.no_data
        update = {
            "wall_cavity_r_value": 20,
            "wall_continuous_r_value": 15,
            "window_u_value": 0.19,
            "floor_cavity_r_value": 47,
            "slab_perimeter_r_value": 19,
            "under_slab_r_value": 19,
            "ceiling_r_value": 59,
            "raised_heel": YesNo.NO,
            "total_ua_alternative": 39.0,
        }
        data.update(update)
        spec = EnvelopeSpecification(option, **data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{option.value} Failing Data"):
            for key in update:
                self.assertFalse(spec.data[key]["meets_requirement"], f"{key} {option}")
                self.assertIsNotNone(spec.data[key]["warning"], f"{key} {option}")
            self.assertFalse(spec.meet_requirements)

        data.update({"total_ua_alternative": 40.0})
        spec = EnvelopeSpecification(option, **data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)
        with self.subTest(f"{option.value} Passing UA"):
            self.assertTrue(spec.data["total_ua_alternative"]["meets_requirement"])
            self.assertIsNotNone(spec.data["total_ua_alternative"]["warning"])
            update.pop("total_ua_alternative")
            self.assertFalse(spec.data["raised_heel"]["meets_requirement"])
            self.assertIsNotNone(spec.data["raised_heel"]["warning"])
            update.pop("raised_heel")
            for key in update:
                self.assertIsNone(spec.data[key]["warning"], f"{key} {option}")
            self.assertTrue(spec.meet_requirements)

    def test_building_envelope_option_1p6b(self):
        """Verify when Option 1.6b is selected it works"""
        option = BuildingEnvelope.OPTION_1p6b

        spec = EnvelopeSpecification(option, **self.no_data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{option.value} No Data"):
            self._verify_building_envelope_no_data(spec)

        data = self.no_data
        data.update(
            {
                "wall_cavity_r_value": 21,
                "window_u_value": 0.30,
                "floor_cavity_r_value": 30,
                "slab_perimeter_r_value": 10,
                "ceiling_r_value": 49,
            }
        )
        spec = EnvelopeSpecification(option, **data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{option.value} Passing Data"):
            self.assertFalse(spec.data["total_ua_alternative"]["meets_requirement"])
            self._verify_building_envelope_passing_no_warning(spec)

        data = self.no_data
        update = {
            "wall_cavity_r_value": 20,
            "window_u_value": 0.31,
            "floor_cavity_r_value": 29,
            "slab_perimeter_r_value": 9,
            "ceiling_r_value": 48,
            "total_ua_alternative": 39.0,
        }
        data.update(update)
        spec = EnvelopeSpecification(option, **data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{option.value} Failing Data"):
            for key in update:
                self.assertFalse(spec.data[key]["meets_requirement"], f"{key} {option}")
                self.assertIsNotNone(spec.data[key]["warning"], f"{key} {option}")
            self.assertFalse(spec.meet_requirements)

        data.update({"total_ua_alternative": 40.0})
        spec = EnvelopeSpecification(option, **data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)
        with self.subTest(f"{option.value} Passing UA"):
            self.assertTrue(spec.data["total_ua_alternative"]["meets_requirement"])
            self.assertIsNotNone(spec.data["total_ua_alternative"]["warning"])
            update.pop("total_ua_alternative")
            for key in update:
                self.assertIsNone(spec.data[key]["warning"], f"{key} {option}")
            self.assertTrue(spec.meet_requirements)

    def test_building_envelope_option_1p7(self):
        """Verify when Option 1.7a is selected it works"""
        option = BuildingEnvelope.OPTION_1p7

        spec = EnvelopeSpecification(option, **self.no_data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{option.value} No Data"):
            self._verify_building_envelope_no_data(spec, ["framing_type", "wall_cavity_r_value"])
            self.assertTrue(spec.data["wall_cavity_r_value"]["meets_requirement"])
            self.assertIsNone(spec.data["wall_cavity_r_value"]["warning"])
            self.assertFalse(spec.data["framing_type"]["meets_requirement"])
            self.assertIsNotNone(spec.data["framing_type"]["warning"])

        data = self.no_data
        data.update(
            {
                "framing_type": FramingType.ADVANCED,
                "window_u_value": 0.28,
                "floor_cavity_r_value": 30,
                "slab_perimeter_r_value": 10,
                "ceiling_r_value": 49,
                "raised_heel": YesNo.YES,
            }
        )
        spec = EnvelopeSpecification(option, **data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{option.value} Passing Data"):
            self.assertFalse(spec.data["total_ua_alternative"]["meets_requirement"])
            self._verify_building_envelope_passing_no_warning(spec)

        data = self.no_data
        update = {
            "framing_type": FramingType.INTERMEDIATE,
            "window_u_value": 0.29,
            "floor_cavity_r_value": 29,
            "slab_perimeter_r_value": 9,
            "ceiling_r_value": 48,
        }
        data.update(update)
        spec = EnvelopeSpecification(option, **data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{option.value} Failing Data"):
            for key in update:
                self.assertFalse(spec.data[key]["meets_requirement"], f"{key} {option}")
                self.assertIsNotNone(spec.data[key]["warning"], f"{key} {option}")
                self.assertFalse(spec.meet_requirements)
            self.assertFalse(spec.meet_requirements)
