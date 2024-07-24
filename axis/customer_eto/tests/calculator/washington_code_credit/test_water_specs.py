"""water_specs.py - Axis"""

__author__ = "Steven K"
__date__ = "8/13/21 09:09"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from django.test import TestCase

from ....calculator.washington_code_credit.specifications.water import WaterSpecification
from ....eep_programs.washington_code_credit import EfficientWaterHeating, DWHR, WACCFuelType
from ....enumerations import YesNo

log = logging.getLogger(__name__)


class WaterSpecificationTests(TestCase):
    @property
    def no_data(self):
        data = {
            "dwhr_installed": None,
            "water_heater_brand": None,
            "water_heater_model": None,
            "gas_water_heater_uef": None,
            "electric_water_heater_uef": None,
        }
        return data.copy()

    def _verify_no_data(self, spec):
        self.assertTrue(spec.data["dwhr_installed"]["meets_requirement"])
        self.assertIsNone(spec.data["dwhr_installed"]["warning"])
        self.assertFalse(spec.data["water_heater_brand"]["meets_requirement"])
        self.assertIsNotNone(spec.data["water_heater_brand"]["warning"])
        self.assertFalse(spec.data["water_heater_model"]["meets_requirement"])
        self.assertIsNotNone(spec.data["water_heater_model"]["warning"])
        if spec.water_heating_fuel == WACCFuelType.GAS:
            self.assertFalse(spec.data["gas_water_heater_uef"]["meets_requirement"])
            self.assertTrue(spec.data["electric_water_heater_uef"]["meets_requirement"])
        else:
            self.assertTrue(spec.data["gas_water_heater_uef"]["meets_requirement"])
            self.assertFalse(spec.data["electric_water_heater_uef"]["meets_requirement"])
        self.assertIsNone(spec.data["gas_water_heater_uef"]["warning"])
        self.assertIsNone(spec.data["electric_water_heater_uef"]["warning"])

    def _verify_passing_no_warning(self, spec, skip_keys=[], meet_requirements=True):
        self.assertTrue(spec.data["dwhr_installed"]["meets_requirement"])
        self.assertIsNone(spec.data["dwhr_installed"]["warning"])
        self.assertTrue(spec.data["water_heater_brand"]["meets_requirement"])
        self.assertIsNone(spec.data["water_heater_brand"]["warning"])
        self.assertTrue(spec.data["water_heater_model"]["meets_requirement"])
        self.assertIsNone(spec.data["water_heater_model"]["warning"])
        if "gas_water_heater_uef" not in skip_keys:
            self.assertTrue(spec.data["gas_water_heater_uef"]["meets_requirement"])
            self.assertIsNone(spec.data["gas_water_heater_uef"]["warning"])
        if "electric_water_heater_uef" not in skip_keys:
            self.assertTrue(spec.data["electric_water_heater_uef"]["meets_requirement"])
            self.assertIsNone(spec.data["electric_water_heater_uef"]["warning"])
        if "fuel_alignment" not in skip_keys:
            self.assertTrue(spec.data["fuel_alignment"]["meets_requirement"])
            self.assertIsNone(spec.data["fuel_alignment"]["warning"])
        if meet_requirements:
            self.assertTrue(spec.meet_requirements)
        else:
            self.assertFalse(spec.meet_requirements)

    def test_dhwr_options(self):
        """Verify DHWR Options work as expected"""
        dhwr_option = DWHR.NONE
        efficient_water_option = EfficientWaterHeating.OPTION_5p3
        fuel = WACCFuelType.GAS
        spec = WaterSpecification(dhwr_option, efficient_water_option, fuel, **self.no_data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)
        with self.subTest(f"{dhwr_option.value} No Data"):
            self._verify_no_data(spec)
            self.assertTrue(spec.meet_requirements)

        data = self.no_data
        data.update(
            {
                "dwhr_installed": YesNo.YES,
                "water_heater_brand": "FOOBAR",
                "water_heater_model": "FOOBAR",
                "gas_water_heater_uef": 0.92,
            }
        )
        spec = WaterSpecification(dhwr_option, efficient_water_option, fuel, **data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{dhwr_option.value} Passing Data"):
            self._verify_passing_no_warning(spec)

        # Sneak in the passing for 5.1
        dhwr_option = DWHR.OPTION_5p1
        spec = WaterSpecification(dhwr_option, efficient_water_option, fuel, **data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{dhwr_option.value} Passing Data"):
            self._verify_passing_no_warning(spec)

        data = self.no_data
        update = {
            "dwhr_installed": YesNo.NO,
        }
        data.update(update)
        spec = WaterSpecification(dhwr_option, efficient_water_option, fuel, **data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{dhwr_option.value} Failing Data"):
            for key in update:
                self.assertFalse(spec.data[key]["meets_requirement"], f"{key} {dhwr_option}")
                self.assertIsNotNone(spec.data[key]["warning"], f"{key} {dhwr_option}")
            self.assertFalse(spec.meet_requirements)

    def test_efficient_water_option_5p2(self):
        """Verify Efficient Water Options 5.2 work as expected"""
        dhwr_option = DWHR.NONE
        efficient_water_option = EfficientWaterHeating.OPTION_5p2
        fuel = WACCFuelType.GAS

        spec = WaterSpecification(dhwr_option, efficient_water_option, fuel, **self.no_data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{efficient_water_option.value} {fuel.value} No Data"):
            self._verify_no_data(spec)
            self.assertFalse(spec.meet_requirements)

        data = self.no_data
        data.update(
            {
                "dwhr_installed": YesNo.YES,
                "water_heater_brand": "FOOBAR",
                "water_heater_model": "FOOBAR",
                "gas_water_heater_uef": 0.80,
            }
        )
        spec = WaterSpecification(dhwr_option, efficient_water_option, fuel, **data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{efficient_water_option.value} {fuel.value} Passing Data"):
            self.assertFalse(spec.meet_requirements)

        # Send wrong fuel
        fuel = WACCFuelType.ELECTRIC
        spec = WaterSpecification(dhwr_option, efficient_water_option, fuel, **data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{efficient_water_option.value} {fuel.value} Wrong Fuel"):
            self.assertFalse(spec.meet_requirements)
            self.assertIsNotNone(spec.data["gas_water_heater_uef"]["warning"])

        # Go foward
        fuel = WACCFuelType.GAS
        data = self.no_data
        update = {
            "water_heater_brand": None,
            "water_heater_model": None,
            "gas_water_heater_uef": 0.79,
        }
        data.update(update)
        spec = WaterSpecification(dhwr_option, efficient_water_option, fuel, **data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{efficient_water_option.value} {fuel.value} Failing Data"):
            for key in update:
                self.assertFalse(spec.data[key]["meets_requirement"], f"{key} {dhwr_option}")
                self.assertIsNotNone(spec.data[key]["warning"], f"{key} {dhwr_option}")
            self.assertFalse(spec.meet_requirements)

    def test_efficient_water_option_5p3(self):
        """Verify Efficient Water Options 5.3 work as expected"""
        dhwr_option = DWHR.NONE
        efficient_water_option = EfficientWaterHeating.OPTION_5p3
        fuel = WACCFuelType.GAS

        spec = WaterSpecification(dhwr_option, efficient_water_option, fuel, **self.no_data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)
        with self.subTest(f"{efficient_water_option.value} {fuel.value} No Data"):
            self._verify_no_data(spec)
            self.assertTrue(spec.meet_requirements)

        data = self.no_data
        data.update(
            {
                "dwhr_installed": YesNo.YES,
                "water_heater_brand": "FOOBAR",
                "water_heater_model": "FOOBAR",
                "gas_water_heater_uef": 0.91,
            }
        )
        spec = WaterSpecification(dhwr_option, efficient_water_option, fuel, **data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{efficient_water_option.value} {fuel.value} Passing Data"):
            self._verify_passing_no_warning(spec)

        # Send wrong fuel
        fuel = WACCFuelType.ELECTRIC
        spec = WaterSpecification(dhwr_option, efficient_water_option, fuel, **data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{efficient_water_option.value} {fuel.value} Wrong Fuel"):
            self._verify_passing_no_warning(
                spec, skip_keys=["gas_water_heater_uef", "fuel_alignment"], meet_requirements=False
            )
            self.assertIsNotNone(spec.data["gas_water_heater_uef"]["warning"])
            self.assertIsNotNone(spec.data["fuel_alignment"]["warning"])

        # Go foward
        fuel = WACCFuelType.GAS
        data = self.no_data
        update = {
            "water_heater_brand": None,
            "water_heater_model": None,
            "gas_water_heater_uef": 0.90,
        }
        data.update(update)
        spec = WaterSpecification(dhwr_option, efficient_water_option, fuel, **data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{efficient_water_option.value} {fuel.value} Failing Data"):
            for key in update:
                self.assertFalse(
                    spec.data[key]["meets_requirement"], f"{key} {efficient_water_option}"
                )
                self.assertIsNotNone(spec.data[key]["warning"], f"{key} {efficient_water_option}")
            self.assertTrue(spec.meet_requirements)

    def test_efficient_water_option_5p4(self):
        """Verify Efficient Water Options 5.4 work as expected"""
        dhwr_option = DWHR.NONE
        efficient_water_option = EfficientWaterHeating.OPTION_5p4
        fuel = WACCFuelType.ELECTRIC

        spec = WaterSpecification(dhwr_option, efficient_water_option, fuel, **self.no_data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)
        with self.subTest(f"{efficient_water_option.value} {fuel.value} No Data"):
            self._verify_no_data(spec)
            self.assertFalse(spec.meet_requirements)

        data = self.no_data
        data.update(
            {
                "dwhr_installed": YesNo.YES,
                "water_heater_brand": "FOOBAR",
                "water_heater_model": "FOOBAR",
                "electric_water_heater_uef": 2.0,
            }
        )
        spec = WaterSpecification(dhwr_option, efficient_water_option, fuel, **data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{efficient_water_option.value} {fuel.value} Passing Data"):
            self._verify_passing_no_warning(spec)

        # Send wrong fuel
        fuel = WACCFuelType.GAS
        spec = WaterSpecification(dhwr_option, efficient_water_option, fuel, **data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{efficient_water_option.value} {fuel.value} Wrong Fuel"):
            self._verify_passing_no_warning(
                spec,
                skip_keys=["electric_water_heater_uef", "fuel_alignment"],
                meet_requirements=False,
            )
            self.assertIsNotNone(spec.data["electric_water_heater_uef"]["warning"])
            self.assertIsNotNone(spec.data["fuel_alignment"]["warning"])

        # Go foward
        fuel = WACCFuelType.ELECTRIC
        data = self.no_data
        update = {
            "water_heater_brand": None,
            "water_heater_model": None,
            "electric_water_heater_uef": 1.999,
        }
        data.update(update)
        spec = WaterSpecification(dhwr_option, efficient_water_option, fuel, **data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{efficient_water_option.value} {fuel.value} Failing Data"):
            for key in update:
                self.assertFalse(
                    spec.data[key]["meets_requirement"], f"{key} {efficient_water_option}"
                )
                self.assertIsNotNone(spec.data[key]["warning"], f"{key} {efficient_water_option}")
            self.assertFalse(spec.meet_requirements)

    def test_efficient_water_option_5p5(self):
        """Verify Efficient Water Options 5.5 work as expected"""
        dhwr_option = DWHR.NONE
        efficient_water_option = EfficientWaterHeating.OPTION_5p5
        fuel = WACCFuelType.ELECTRIC

        spec = WaterSpecification(dhwr_option, efficient_water_option, fuel, **self.no_data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)
        with self.subTest(f"{efficient_water_option.value} {fuel.value} No Data"):
            self._verify_no_data(spec)
            self.assertFalse(spec.meet_requirements)

        data = self.no_data
        data.update(
            {
                "dwhr_installed": YesNo.YES,
                "water_heater_brand": "FOOBAR",
                "water_heater_model": "FOOBAR",
                "electric_water_heater_uef": 2.6,
            }
        )
        spec = WaterSpecification(dhwr_option, efficient_water_option, fuel, **data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{efficient_water_option.value} {fuel.value} Passing Data"):
            self._verify_passing_no_warning(spec)

        # Send wrong fuel
        fuel = WACCFuelType.GAS
        spec = WaterSpecification(dhwr_option, efficient_water_option, fuel, **data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{efficient_water_option.value} {fuel.value} Wrong Fuel"):
            self._verify_passing_no_warning(
                spec,
                skip_keys=["electric_water_heater_uef", "fuel_alignment"],
                meet_requirements=False,
            )
            self.assertIsNotNone(spec.data["electric_water_heater_uef"]["warning"])
            self.assertIsNotNone(spec.data["fuel_alignment"]["warning"])

        # Go foward
        fuel = WACCFuelType.ELECTRIC
        data = self.no_data
        update = {
            "water_heater_brand": None,
            "water_heater_model": None,
            "electric_water_heater_uef": 2.5,
        }
        data.update(update)
        spec = WaterSpecification(dhwr_option, efficient_water_option, fuel, **data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{efficient_water_option.value} {fuel.value} Failing Data"):
            for key in update:
                self.assertFalse(
                    spec.data[key]["meets_requirement"], f"{key} {efficient_water_option}"
                )
                self.assertIsNotNone(spec.data[key]["warning"], f"{key} {efficient_water_option}")
            self.assertFalse(spec.meet_requirements)

    def test_efficient_water_option_5p6(self):
        """Verify Efficient Water Options 5.6 work as expected"""
        dhwr_option = DWHR.NONE
        efficient_water_option = EfficientWaterHeating.OPTION_5p6
        fuel = WACCFuelType.ELECTRIC

        spec = WaterSpecification(dhwr_option, efficient_water_option, fuel, **self.no_data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)
        with self.subTest(f"{efficient_water_option.value} {fuel.value} No Data"):
            self._verify_no_data(spec)
            self.assertFalse(spec.meet_requirements)

        data = self.no_data
        data.update(
            {
                "dwhr_installed": YesNo.YES,
                "water_heater_brand": "FOOBAR",
                "water_heater_model": "FOOBAR",
                "electric_water_heater_uef": 2.9,
            }
        )
        spec = WaterSpecification(dhwr_option, efficient_water_option, fuel, **data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{efficient_water_option.value} {fuel.value} Passing Data"):
            self._verify_passing_no_warning(spec)

        # Send wrong fuel
        fuel = WACCFuelType.GAS
        spec = WaterSpecification(dhwr_option, efficient_water_option, fuel, **data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{efficient_water_option.value} {fuel.value} Wrong Fuel"):
            self._verify_passing_no_warning(
                spec,
                skip_keys=["electric_water_heater_uef", "fuel_alignment"],
                meet_requirements=False,
            )
            self.assertIsNotNone(spec.data["electric_water_heater_uef"]["warning"])
            self.assertIsNotNone(spec.data["fuel_alignment"]["warning"])

        # Go foward
        fuel = WACCFuelType.ELECTRIC
        data = self.no_data
        update = {
            "water_heater_brand": None,
            "water_heater_model": None,
            "electric_water_heater_uef": 2.8,
        }
        data.update(update)
        spec = WaterSpecification(dhwr_option, efficient_water_option, fuel, **data)
        self.assertIsNotNone(spec.data)
        self.assertIsNotNone(spec.report)

        with self.subTest(f"{efficient_water_option.value} {fuel.value} Failing Data"):
            for key in update:
                self.assertFalse(
                    spec.data[key]["meets_requirement"], f"{key} {efficient_water_option}"
                )
                self.assertIsNotNone(spec.data[key]["warning"], f"{key} {efficient_water_option}")
            self.assertFalse(spec.meet_requirements)
