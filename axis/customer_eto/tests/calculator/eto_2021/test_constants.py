"""test_constants.py - Axis"""

__author__ = "Steven K"
__date__ = "9/15/21 09:37"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from django.test import TestCase

from axis.customer_eto.calculator.eps_2021.base import HomePath, HomeSubType
from axis.customer_eto.calculator.eps_2021.constants import (
    Constants,
    ELECTRIC_SPACE_HEAT_FUEL_WEIGHT,
    ELECTRIC_HOT_WATER_FUEL_WEIGHT,
    HEAT_PUMP_HEATING_CORRECTION_FACTOR,
    HEAT_PUMP_COOLING_CORRECTION_FACTOR,
    ELECTRIC_CARBON_FACTOR,
    NATURAL_GAS_CARBON_FACTOR,
    FIREPLACE_ADDITION_THERMS,
    FIREPLACE_ADDITION_THERMS_GT70,
    CARBON_WEIGHTS,
)
from axis.customer_eto.enumerations import ElectricUtility, PNWUSStates, ClimateLocation

log = logging.getLogger(__name__)


class ConstantsTests(TestCase):
    def test_constants(self):
        c = Constants(ElectricUtility.NONE)
        self.assertEqual(c.electric_space_heat_fuel_weight, ELECTRIC_SPACE_HEAT_FUEL_WEIGHT)
        self.assertEqual(c.electric_hot_water_fuel_weight, ELECTRIC_HOT_WATER_FUEL_WEIGHT)
        self.assertEqual(c.heat_pump_heating_correction_factor, HEAT_PUMP_HEATING_CORRECTION_FACTOR)
        self.assertEqual(c.heat_pump_cooling_correction_factor, HEAT_PUMP_COOLING_CORRECTION_FACTOR)
        self.assertEqual(c.electric_carbon_factor, ELECTRIC_CARBON_FACTOR)
        self.assertEqual(c.natural_gas_carbon_factor, NATURAL_GAS_CARBON_FACTOR)
        self.assertEqual(c.fireplace_addition_therms, FIREPLACE_ADDITION_THERMS)
        self.assertEqual(c.fireplace_addition_therms_gt70, FIREPLACE_ADDITION_THERMS_GT70)

    def test_constant_report(self):
        c = Constants(ElectricUtility.PACIFIC_POWER)
        report = c.code_constant_report
        self.assertIn("Natural Gas Carbon Factor", report)
        # print(report)

        report = c.carbon_report
        self.assertIn("Pounds of Carbon per therm/kWh", report)
        # print(report)

        report = c.improved_constant_report
        self.assertIn("Smart Thermostat savings %", report)
        # print(report)

    def test_improved_electric_carbon_factor(self):
        c = Constants(ElectricUtility.PACIFIC_POWER)
        self.assertEqual(
            c.improved_electric_carbon_factor, CARBON_WEIGHTS[ElectricUtility.PACIFIC_POWER]
        )
        c = Constants(ElectricUtility.PORTLAND_GENERAL)
        self.assertEqual(
            c.improved_electric_carbon_factor, CARBON_WEIGHTS[ElectricUtility.PORTLAND_GENERAL]
        )
        c = Constants(ElectricUtility.NONE)
        self.assertEqual(c.improved_electric_carbon_factor, CARBON_WEIGHTS[ElectricUtility.NONE])

    def test_load_profile(self):
        c = Constants(ElectricUtility.PACIFIC_POWER)
        load_profile = c.get_load_profile(HomePath.PATH_4, HomeSubType.GHGW)
        self.assertEqual(load_profile.weighted_avg_measure_life, 40.0)
        self.assertEqual(load_profile.gas_allocation, 0.8338713576822170000)
        self.assertEqual(load_profile.electric_allocation, 0.1661286423177830000)

        c = Constants(ElectricUtility.PACIFIC_POWER, PNWUSStates.WA)
        load_profile = c.get_load_profile(HomePath.PATH_4, HomeSubType.GHGW)
        self.assertEqual(load_profile.weighted_avg_measure_life, 41.0)
        self.assertEqual(load_profile.gas_allocation, 1.0)
        self.assertEqual(load_profile.electric_allocation, 0.0)

    def test_simiplified_locations(self):
        c = Constants(ElectricUtility.PACIFIC_POWER)
        redmond = ClimateLocation.REDMOND
        self.assertEqual(c.get_simplified_location(ClimateLocation.BURNS), redmond)
        self.assertEqual(c.get_simplified_location(ClimateLocation.PENDLETON), redmond)
        self.assertEqual(c.get_simplified_location(ClimateLocation.REDMOND), redmond)

        portland = ClimateLocation.PORTLAND
        self.assertEqual(c.get_simplified_location(ClimateLocation.ASTORIA), portland)
        self.assertEqual(c.get_simplified_location(ClimateLocation.EUGENE), portland)
        self.assertEqual(c.get_simplified_location(ClimateLocation.NORTH_BEND), portland)
        self.assertEqual(c.get_simplified_location(ClimateLocation.PORTLAND), portland)
        self.assertEqual(c.get_simplified_location(ClimateLocation.SALEM), portland)

        medford = ClimateLocation.MEDFORD
        self.assertEqual(c.get_simplified_location(ClimateLocation.MEDFORD), medford)
