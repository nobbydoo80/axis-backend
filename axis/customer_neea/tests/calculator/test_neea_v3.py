"""neea_v3.py - Axis"""

__author__ = "Steven K"
__date__ = "6/26/21 10:05"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from simulation.enumerations import FuelType

from axis.core.tests.client import AxisClient
from axis.core.tests.testcases import AxisTestCase
from ..mixins import CustomerNEEABaseTestMixin
from ...rtf_calculator.base import RTFInputException
from ...rtf_calculator.calculator import NEEAV3Calculator
from ...rtf_calculator.constants.default import DRYER_TIER_3
from ...rtf_calculator.constants.neea_v3 import (
    REFRIGERATOR_BOTTOM_FREEZER,
    NEEA_REFRIGERATOR_CHOICE_MAP,
    CLOTHES_WASHER_TOP,
    NEEA_CLOTHES_WASHER_CHOICE_MAP,
    REFRIGERATOR_SIDE_FREEZER,
    REFRIGERATOR_OTHER_FREEZER,
    CLOTHES_WASHER_SIDE,
    NEEA_WATER_HEATER_TIER_MAP,
)

log = logging.getLogger(__name__)


class NEEAV3CalculatorTests(CustomerNEEABaseTestMixin, AxisTestCase):
    client_class = AxisClient

    def base_kwargs(self):
        return {
            "us_state": "OR",
            "heating_fuel": "electric",
            "heating_system_config": "central",  # zonal, central, all
            "home_size": "small",  # small, medium, large, all
            "heating_zone": "hz2",  # hz1, hz2, hz3
            "improved_data": {
                "heating_therms": 20.0,
                "heating_kwh": 8000.0,
                "cooling_kwh": 2000.0,
                "primary_heating_type": "heater",  # Add 'heat pump' to get heat_pump recognized
                "primary_cooling_type": "air conditioner",
                "primary_cooling_fuel": "electric",
                "primary_water_heating_efficiency": 0.0,
            },
            "code_data": {
                "heating_therms": 30.0,
                "heating_kwh": 10000.0,
                "cooling_kwh": 2100.0,
            },
            "water_heater_tier": "electric resistance",  # tier1, tier2, tier3
            "estar_std_refrigerators_installed": REFRIGERATOR_BOTTOM_FREEZER,
            "estar_dishwasher_installed": True,
            "estar_clothes_washer_installed": CLOTHES_WASHER_TOP,
            "clothes_dryer_tier": "tier3",  # tier1, tier2, tier3
            "clothes_dryer_fuel": FuelType.ELECTRIC,
            "smart_thermostat_installed": True,
            "certified_earth_advantage": None,
            "percent_improvement": 0.15,
            "electric_utility": "foo",
            "gas_utility": "foo",
        }

    def test_zero_dhw_tiers(self):
        """Make sure that we are zeroing"""
        kwargs = self.base_kwargs().copy()
        calculator = NEEAV3Calculator(**kwargs.copy())
        tested_count = 0
        for k, tiers in dict(calculator.constants.NEEA_WATER_HEATER_BASELINE_SAVINGS_RATES).items():
            self.assertEqual(tiers["electric resistance"], 0)
            self.assertEqual(tiers["tier1"], 0)
            self.assertEqual(tiers["tier2"], 0)
            if k[:3] in [("WA", "zonal", "large"), ("WA", "central", "large")]:
                self.assertEqual(tiers["tier3"], 0)
            else:
                self.assertNotEqual(tiers["tier3"], 0)
            self.assertEqual(tiers["gas_ef_lt_0p67"], 0)
            self.assertEqual(round(tiers["gas_ef_gte_0p67"], 1), 25.2)
            self.assertEqual(round(tiers["gas_ef_gte_0p7"], 1), 55.4)
            self.assertEqual(round(tiers["gas_tankless_ef_gte_0p82"], 1), 46.1)
            self.assertEqual(round(tiers["gas_tankless_ef_gte_0p9"], 1), 60.7)
            tested_count += 1
        self.assertEqual(tested_count, 36)

    def test_refrigerator_type_normalization(self):
        """Test refrigerator type changeout"""
        kwargs = self.base_kwargs().copy()

        for k, v in dict(NEEA_REFRIGERATOR_CHOICE_MAP).items():
            kwargs["estar_std_refrigerators_installed"] = k
            calculator = NEEAV3Calculator(**kwargs.copy())
            self.assertEqual(len(calculator.issues), 0)
            self.assertEqual(calculator.estar_std_refrigerators_installed, k)
            kwargs["estar_std_refrigerators_installed"] = v
            calculator = NEEAV3Calculator(**kwargs.copy())
            self.assertEqual(len(calculator.issues), 0)
            self.assertEqual(calculator.estar_std_refrigerators_installed, k)

        kwargs["estar_std_refrigerators_installed"] = "foobar"
        self.assertRaises(RTFInputException, NEEAV3Calculator, **kwargs.copy())
        kwargs["estar_std_refrigerators_installed"] = True
        self.assertRaises(RTFInputException, NEEAV3Calculator, **kwargs.copy())
        kwargs["estar_std_refrigerators_installed"] = False
        self.assertRaises(RTFInputException, NEEAV3Calculator, **kwargs.copy())

    def test_clothes_washer_type_normalization(self):
        kwargs = self.base_kwargs().copy()

        for k, v in dict(NEEA_CLOTHES_WASHER_CHOICE_MAP).items():
            kwargs["estar_clothes_washer_installed"] = k
            calculator = NEEAV3Calculator(**kwargs.copy())
            self.assertEqual(len(calculator.issues), 0)
            self.assertEqual(calculator.estar_front_load_clothes_washer_installed, k)
            kwargs["estar_clothes_washer_installed"] = v
            calculator = NEEAV3Calculator(**kwargs.copy())
            self.assertEqual(len(calculator.issues), 0)
            self.assertEqual(calculator.estar_front_load_clothes_washer_installed, k)

        kwargs["estar_clothes_washer_installed"] = "foobar"
        self.assertRaises(RTFInputException, NEEAV3Calculator, **kwargs.copy())
        kwargs["estar_clothes_washer_installed"] = True
        self.assertRaises(RTFInputException, NEEAV3Calculator, **kwargs.copy())
        kwargs["estar_clothes_washer_installed"] = False
        self.assertRaises(RTFInputException, NEEAV3Calculator, **kwargs.copy())

    def test_clothes_dryer_fuel(self):
        kwargs = self.base_kwargs().copy()
        kwargs["clothes_dryer_fuel"] = FuelType.ELECTRIC
        calculator = NEEAV3Calculator(**kwargs.copy())
        self.assertEqual(calculator.input_clothes_dryer_fuel, FuelType.ELECTRIC)
        self.assertEqual(calculator.clothes_dryer_fuel, FuelType.ELECTRIC)

        kwargs = self.base_kwargs().copy()
        kwargs["clothes_dryer_fuel"] = FuelType.NATURAL_GAS
        calculator = NEEAV3Calculator(**kwargs.copy())
        self.assertEqual(calculator.input_clothes_dryer_fuel, FuelType.NATURAL_GAS)
        self.assertEqual(calculator.clothes_dryer_fuel, FuelType.NATURAL_GAS)

    def test_water_heater_tiers(self):
        """Verify we correctly parse out the values"""
        kwargs = self.base_kwargs().copy()
        for internal_name, description in dict(NEEA_WATER_HEATER_TIER_MAP).items():
            kwargs["water_heater_tier"] = internal_name
            calculator = NEEAV3Calculator(**kwargs.copy())
            self.assertEqual(calculator.input_water_heater_tier, internal_name)
            self.assertEqual(calculator.water_heater_tier, internal_name)

            kwargs["water_heater_tier"] = description
            calculator = NEEAV3Calculator(**kwargs.copy())
            self.assertEqual(calculator.input_water_heater_tier, description)
            self.assertEqual(calculator.water_heater_tier, internal_name)

    def test_dump(self):
        kwargs = self.base_kwargs().copy()
        calculator = NEEAV3Calculator(**kwargs.copy())
        data = calculator.dump_simulation(True)
        self.assertNotIn("cfl_installed", data)
        self.assertNotIn("led_installed", data)
        self.assertNotIn("total_installed_lamps", data)
        self.assertNotIn("qty_shower_head_1p5", data)
        self.assertNotIn("qty_shower_head_1p75", data)
        self.assertNotIn("qty_shower_head_1p75", data)
        self.assertNotIn("estar_front_load_clothes_washer_installed", data)
        self.assertIn("clothes_dryer_fuel", data)
        self.assertIn("estar_clothes_washer_installed", data)

        calculator.dump_simulation(as_dict=True)

    def test_heating_cooling_basics(self):
        """Test out the Heating / Cooling Report"""
        kwargs = {
            "us_state": "WA",
            "heating_fuel": "electric",
            "heating_system_config": "central",  # zonal, central, all
            "home_size": "medium",  # small, medium, large, all
            "heating_zone": "hz1",  # hz1, hz2, hz3
            "water_heater_tier": "tier2",  # tier1, tier2, tier3
            "estar_std_refrigerators_installed": REFRIGERATOR_BOTTOM_FREEZER,
            "estar_dishwasher_installed": False,
            "estar_clothes_washer_installed": CLOTHES_WASHER_TOP,
            "clothes_dryer_tier": "estar",  # tier1, tier2, tier3, estar
            "clothes_dryer_fuel": FuelType.ELECTRIC,
            "smart_thermostat_installed": True,
            "code_data": {
                "heating_therms": 10.0,
                "heating_kwh": 7630.0,
                "cooling_kwh": 570.0,
            },
            "improved_data": {
                "heating_therms": 9.0,
                "heating_kwh": 7272.0,
                "cooling_kwh": 590.0,
                "primary_heating_type": "heater",  # Add 'heat pump' to get heat_pump recognized
                "primary_cooling_type": "air conditioner",
                "primary_cooling_fuel": "electric",
                "primary_water_heating_type": "gas",  # None, 'gas', 'hpwh', 'electric resistance'
            },
            "percent_improvement": 0.15,
            "electric_utility": "puget-sound-energy",
            "gas_utility": "foo",
        }

        neea_kwargs = kwargs.copy()

        calculator = NEEAV3Calculator(**neea_kwargs)
        _x = calculator.heating_cooling_report()

        self.assertEqual(calculator.code_data_heating_kwh, kwargs["code_data"]["heating_kwh"])
        self.assertEqual(calculator.code_data_heating_therms, kwargs["code_data"]["heating_therms"])
        self.assertEqual(calculator.code_data_cooling_kwh, kwargs["code_data"]["cooling_kwh"])

        self.assertEqual(
            calculator.improved_data_heating_kwh, kwargs["improved_data"]["heating_kwh"]
        )
        self.assertEqual(
            calculator.improved_data_heating_therms, kwargs["improved_data"]["heating_therms"]
        )
        self.assertEqual(
            calculator.improved_data_cooling_kwh, kwargs["improved_data"]["cooling_kwh"]
        )

        self.assertEqual(calculator.electricity_adjustment_factor, 1)
        self.assertEqual(calculator.gas_adjustment_factor, 1)

        self.assertEqual(calculator.heating_kwh_savings, 358)
        self.assertEqual(calculator.heating_therm_savings, 1)

        self.assertEqual(calculator.cooling_kwh_savings, -20)
        self.assertEqual(calculator.cooling_therm_savings, 0)

    def test_hot_water_basics(self):
        """Test out the Heating / Cooling Report"""
        kwargs = {
            "us_state": "OR",
            "heating_fuel": "electric",
            "heating_system_config": "central",  # zonal, central, all
            "home_size": "all",  # small, medium, large, all
            "heating_zone": "hz2",  # hz1, hz2, hz3
            "water_heater_tier": "tier3",  # tier1, tier2, tier3
            "estar_std_refrigerators_installed": REFRIGERATOR_BOTTOM_FREEZER,
            "estar_dishwasher_installed": False,
            "estar_clothes_washer_installed": CLOTHES_WASHER_TOP,
            "clothes_dryer_tier": "estar",  # tier1, tier2, tier3, estar
            "clothes_dryer_fuel": FuelType.ELECTRIC,
            "smart_thermostat_installed": True,
            "code_data": {
                "heating_therms": 10.0,
                "heating_kwh": 7630.0,
                "cooling_kwh": 570.0,
            },
            "improved_data": {
                "heating_therms": 9.0,
                "heating_kwh": 7272.0,
                "cooling_kwh": 590.0,
                "primary_heating_type": "heater",  # Add 'heat pump' to get heat_pump recognized
                "primary_cooling_type": "air conditioner",
                "primary_cooling_fuel": "electric",
                "primary_water_heating_type": "gas",  # None, 'gas', 'hpwh', 'electric resistance'
            },
            "percent_improvement": 0.15,
            "electric_utility": "puget-sound-energy",
            "gas_utility": "foo",
        }

        neea_kwargs = kwargs.copy()

        calculator = NEEAV3Calculator(**neea_kwargs)
        _x = calculator.hot_water_report()

        self.assertEqual(calculator.pretty_water_heater_tier, "HPWH Tier 3")
        self.assertEqual(round(calculator.water_heater_kwh_savings, 3), 1372.198)
        self.assertEqual(calculator.water_heater_therm_savings, 0)

    def test_lighting_basics(self):
        """Test out the Lighting Report - This was removed in V3"""
        kwargs = {
            "us_state": "OR",
            "heating_fuel": "electric",
            "heating_system_config": "central",  # zonal, central, all
            "home_size": "all",  # small, medium, large, all
            "heating_zone": "hz2",  # hz1, hz2, hz3
            "water_heater_tier": "tier3",  # tier1, tier2, tier3
            "estar_std_refrigerators_installed": REFRIGERATOR_BOTTOM_FREEZER,
            "estar_dishwasher_installed": False,
            "estar_clothes_washer_installed": CLOTHES_WASHER_TOP,
            "clothes_dryer_tier": "estar",  # tier1, tier2, tier3, estar
            "clothes_dryer_fuel": FuelType.ELECTRIC,
            "smart_thermostat_installed": True,
            "code_data": {
                "heating_therms": 10.0,
                "heating_kwh": 7630.0,
                "cooling_kwh": 570.0,
            },
            "improved_data": {
                "heating_therms": 9.0,
                "heating_kwh": 7272.0,
                "cooling_kwh": 590.0,
                "primary_heating_type": "heater",  # Add 'heat pump' to get heat_pump recognized
                "primary_cooling_type": "air conditioner",
                "primary_cooling_fuel": "electric",
                "primary_water_heating_type": "gas",  # None, 'gas', 'hpwh', 'electric resistance'
            },
            "percent_improvement": 0.15,
            "electric_utility": "puget-sound-energy",
            "gas_utility": "foo",
        }

        neea_kwargs = kwargs.copy()

        calculator = NEEAV3Calculator(**neea_kwargs)
        self.assertEqual(calculator.lighting_kwh_savings, 0.0)
        self.assertEqual(calculator.lighting_report(), "Removed in V3")

    def test_shower_basics(self):
        """Test out the Showered Report - This was removed in V3"""
        kwargs = {
            "us_state": "OR",
            "heating_fuel": "electric",
            "heating_system_config": "central",  # zonal, central, all
            "home_size": "all",  # small, medium, large, all
            "heating_zone": "hz2",  # hz1, hz2, hz3
            "water_heater_tier": "tier3",  # tier1, tier2, tier3
            "estar_std_refrigerators_installed": REFRIGERATOR_BOTTOM_FREEZER,
            "estar_dishwasher_installed": False,
            "estar_clothes_washer_installed": CLOTHES_WASHER_TOP,
            "clothes_dryer_tier": "estar",  # tier1, tier2, tier3, estar
            "clothes_dryer_fuel": FuelType.ELECTRIC,
            "smart_thermostat_installed": True,
            "code_data": {
                "heating_therms": 10.0,
                "heating_kwh": 7630.0,
                "cooling_kwh": 570.0,
            },
            "improved_data": {
                "heating_therms": 9.0,
                "heating_kwh": 7272.0,
                "cooling_kwh": 590.0,
                "primary_heating_type": "heater",  # Add 'heat pump' to get heat_pump recognized
                "primary_cooling_type": "air conditioner",
                "primary_cooling_fuel": "electric",
                "primary_water_heating_type": "gas",
                # None, 'gas', 'hpwh', 'electric resistance'
            },
            "percent_improvement": 0.15,
            "electric_utility": "puget-sound-energy",
            "gas_utility": "foo",
        }

        neea_kwargs = kwargs.copy()

        calculator = NEEAV3Calculator(**neea_kwargs)

        self.assertEqual(calculator.showerhead_kwh_savings, 0.0)
        self.assertEqual(calculator.showerhead_therm_savings, 0.0)
        self.assertEqual(calculator.shower_head_report(), "Removed in V3")

    def test_thermostat_report_basics(self):
        """Test out the Thermostat no change since V2"""
        kwargs = {
            "us_state": "OR",
            "heating_fuel": "electric",
            "heating_system_config": "central",  # zonal, central, all
            "home_size": "all",  # small, medium, large, all
            "heating_zone": "hz2",  # hz1, hz2, hz3
            "water_heater_tier": "tier3",  # tier1, tier2, tier3
            "estar_std_refrigerators_installed": REFRIGERATOR_BOTTOM_FREEZER,
            "estar_dishwasher_installed": False,
            "estar_clothes_washer_installed": CLOTHES_WASHER_TOP,
            "clothes_dryer_tier": "estar",  # tier1, tier2, tier3, estar
            "clothes_dryer_fuel": FuelType.ELECTRIC,
            "smart_thermostat_installed": True,
            "code_data": {
                "heating_therms": 10.0,
                "heating_kwh": 7630.0,
                "cooling_kwh": 570.0,
            },
            "improved_data": {
                "heating_therms": 9.0,
                "heating_kwh": 7272.0,
                "cooling_kwh": 590.0,
                "primary_heating_type": "heater",  # Add 'heat pump' to get heat_pump recognized
                "primary_cooling_type": "air conditioner",
                "primary_cooling_fuel": "electric",
                "primary_water_heating_type": "gas",
                # None, 'gas', 'hpwh', 'electric resistance'
            },
            "percent_improvement": 0.15,
            "electric_utility": "puget-sound-energy",
            "gas_utility": "foo",
        }

        neea_kwargs = kwargs.copy()

        calculator = NEEAV3Calculator(**neea_kwargs)
        _x = calculator.thermostat_report()

        self.assertTrue(calculator.smart_thermostat_installed)
        self.assertEqual(calculator.heating_savings_rate, 0.06)
        self.assertEqual(calculator.cooling_savings_rate, 0.06)

        self.assertEqual(round(calculator.smart_thermostat_heating_kwh_savings, 2), 436.32)
        self.assertEqual(round(calculator.smart_thermostat_cooling_kwh_savings, 2), 35.40)
        self.assertEqual(round(calculator.smart_thermostat_kwh_savings, 2), 471.72)

        self.assertEqual(round(calculator.smart_thermostat_heating_therm_savings, 2), 0.54)
        self.assertEqual(round(calculator.smart_thermostat_cooling_therm_savings, 2), 0)
        self.assertEqual(round(calculator.smart_thermostat_therm_savings, 2), 0.54)

    def test_refrigerator_annual_savings(self):
        """Test out the refrigerator savings"""
        neea_kwargs = self.base_kwargs().copy()
        calculator = NEEAV3Calculator(**neea_kwargs)
        self.assertEqual(
            neea_kwargs["estar_std_refrigerators_installed"], REFRIGERATOR_BOTTOM_FREEZER
        )
        self.assertEqual(calculator.refrigerator_annual_kwh_savings, 7.0)
        self.assertEqual(calculator.refrigerator_annual_therm_savings, 0.0)

        neea_kwargs["estar_std_refrigerators_installed"] = REFRIGERATOR_SIDE_FREEZER
        calculator = NEEAV3Calculator(**neea_kwargs)
        self.assertEqual(calculator.refrigerator_annual_kwh_savings, 45.0)
        self.assertEqual(calculator.refrigerator_annual_therm_savings, 0.0)

        neea_kwargs["estar_std_refrigerators_installed"] = REFRIGERATOR_OTHER_FREEZER
        calculator = NEEAV3Calculator(**neea_kwargs)
        self.assertEqual(calculator.refrigerator_annual_kwh_savings, 21.0)
        self.assertEqual(calculator.refrigerator_annual_therm_savings, 0.0)

        neea_kwargs["estar_std_refrigerators_installed"] = None
        calculator = NEEAV3Calculator(**neea_kwargs)
        self.assertEqual(calculator.refrigerator_annual_kwh_savings, 0.0)
        self.assertEqual(calculator.refrigerator_annual_therm_savings, 0.0)

    def test_dishwasher_annual_savings(self):
        """Test out the dishwasher savings"""
        neea_kwargs = self.base_kwargs().copy()
        calculator = NEEAV3Calculator(**neea_kwargs)
        self.assertEqual(neea_kwargs["estar_dishwasher_installed"], True)
        self.assertEqual(calculator.dishwasher_annual_kwh_savings, 58.672)
        self.assertEqual(calculator.dishwasher_annual_therm_savings, 0.0)

        neea_kwargs["estar_dishwasher_installed"] = False
        calculator = NEEAV3Calculator(**neea_kwargs)
        self.assertEqual(calculator.dishwasher_annual_kwh_savings, 0.0)
        self.assertEqual(calculator.dishwasher_annual_therm_savings, 0.0)

    def test_clothes_washer_saving(self):
        neea_kwargs = self.base_kwargs().copy()
        calculator = NEEAV3Calculator(**neea_kwargs)

        self.assertEqual(calculator.estar_front_load_clothes_washer_installed, CLOTHES_WASHER_TOP)
        self.assertEqual(calculator.water_heater_fuel, FuelType.ELECTRIC)
        self.assertEqual(calculator.clothes_dryer_fuel, FuelType.ELECTRIC)
        self.assertEqual(round(calculator.clothes_washer_annual_kwh_savings, 2), 16.61)
        self.assertEqual(round(calculator.clothes_washer_annual_therm_savings, 2), 0.0)

        neea_kwargs["estar_front_load_clothes_washer_installed"] = CLOTHES_WASHER_SIDE
        neea_kwargs["clothes_dryer_fuel"] = FuelType.NATURAL_GAS
        neea_kwargs["water_heater_tier"] = "gas_ef_gte_0p67"
        calculator = NEEAV3Calculator(**neea_kwargs)

        self.assertEqual(calculator.estar_front_load_clothes_washer_installed, CLOTHES_WASHER_SIDE)
        self.assertEqual(calculator.water_heater_fuel, FuelType.NATURAL_GAS)
        self.assertEqual(calculator.clothes_dryer_fuel, FuelType.NATURAL_GAS)
        self.assertEqual(round(calculator.clothes_washer_annual_kwh_savings, 2), -11.91)
        self.assertEqual(round(calculator.clothes_washer_annual_therm_savings, 2), 8.50)

        neea_kwargs["estar_front_load_clothes_washer_installed"] = CLOTHES_WASHER_TOP
        neea_kwargs["clothes_dryer_fuel"] = FuelType.NATURAL_GAS
        neea_kwargs["water_heater_tier"] = "tier3"
        calculator = NEEAV3Calculator(**neea_kwargs)

        self.assertEqual(calculator.estar_front_load_clothes_washer_installed, CLOTHES_WASHER_TOP)
        self.assertEqual(calculator.water_heater_fuel, FuelType.ELECTRIC)
        self.assertEqual(calculator.clothes_dryer_fuel, FuelType.NATURAL_GAS)
        self.assertEqual(round(calculator.clothes_washer_annual_kwh_savings, 2), 27.97)
        self.assertEqual(round(calculator.clothes_washer_annual_therm_savings, 2), -0.43)

        neea_kwargs["estar_front_load_clothes_washer_installed"] = None
        neea_kwargs["clothes_dryer_fuel"] = FuelType.NATURAL_GAS
        neea_kwargs["water_heater_tier"] = "gas_ef_gte_0p67"
        calculator = NEEAV3Calculator(**neea_kwargs)

        self.assertEqual(calculator.estar_front_load_clothes_washer_installed, None)
        self.assertEqual(calculator.water_heater_fuel, FuelType.NATURAL_GAS)
        self.assertEqual(calculator.clothes_dryer_fuel, FuelType.NATURAL_GAS)
        self.assertEqual(round(calculator.clothes_washer_annual_kwh_savings, 2), 0.0)
        self.assertEqual(round(calculator.clothes_washer_annual_therm_savings, 2), 0.0)

    def test_clothes_dryer_saving(self):
        neea_kwargs = self.base_kwargs().copy()
        calculator = NEEAV3Calculator(**neea_kwargs)

        self.assertEqual(calculator.clothes_dryer_tier, DRYER_TIER_3)
        self.assertEqual(calculator.clothes_dryer_annual_kwh_savings, 485.0)
        self.assertEqual(calculator.clothes_dryer_annual_therm_savings, 0.0)

        neea_kwargs["clothes_dryer_tier"] = "estar"
        calculator = NEEAV3Calculator(**neea_kwargs)
        self.assertEqual(calculator.clothes_dryer_annual_kwh_savings, 68.0)
        self.assertEqual(calculator.clothes_dryer_annual_therm_savings, 0.0)

        neea_kwargs["clothes_dryer_tier"] = None
        calculator = NEEAV3Calculator(**neea_kwargs)
        self.assertEqual(calculator.clothes_dryer_annual_kwh_savings, 0.0)
        self.assertEqual(calculator.clothes_dryer_annual_therm_savings, 0.0)

    def test_appliance_report_basics(self):
        """Test out the Thermostat no change since V2"""

        kwargs = {
            "us_state": "OR",
            "heating_fuel": "electric",
            "heating_system_config": "central",  # zonal, central, all
            "home_size": "all",  # small, medium, large, all
            "heating_zone": "hz2",  # hz1, hz2, hz3
            "water_heater_tier": "gas_ef_gte_0p67",  # tier1, tier2, tier3
            "estar_std_refrigerators_installed": REFRIGERATOR_BOTTOM_FREEZER,
            "estar_dishwasher_installed": True,
            "estar_clothes_washer_installed": CLOTHES_WASHER_SIDE,
            "clothes_dryer_tier": "tier3",  # tier1, tier2, tier3, estar
            "clothes_dryer_fuel": FuelType.ELECTRIC,
            "smart_thermostat_installed": True,
            "code_data": {
                "heating_therms": 10.0,
                "heating_kwh": 7630.0,
                "cooling_kwh": 570.0,
            },
            "improved_data": {
                "heating_therms": 9.0,
                "heating_kwh": 7272.0,
                "cooling_kwh": 590.0,
                "primary_heating_type": "heater",  # Add 'heat pump' to get heat_pump recognized
                "primary_cooling_type": "air conditioner",
                "primary_cooling_fuel": "electric",
                "primary_water_heating_type": "gas",
                # None, 'gas', 'hpwh', 'electric resistance'
            },
            "percent_improvement": 0.15,
            "electric_utility": "puget-sound-energy",
            "gas_utility": "foo",
        }

        neea_kwargs = kwargs.copy()

        calculator = NEEAV3Calculator(**neea_kwargs)
        _x = calculator.appliance_report()

        self.assertEqual(round(calculator.refrigerator_annual_kwh_savings, 2), 7.0)
        self.assertEqual(round(calculator.refrigerator_annual_therm_savings, 2), 0.0)

        self.assertEqual(round(calculator.dishwasher_annual_kwh_savings, 2), 58.67)
        self.assertEqual(round(calculator.dishwasher_annual_therm_savings, 2), 0.0)

        self.assertEqual(round(calculator.clothes_washer_annual_kwh_savings, 2), 83.67)
        self.assertEqual(round(calculator.clothes_washer_annual_therm_savings, 2), 4.84)

        self.assertEqual(round(calculator.clothes_dryer_annual_kwh_savings, 2), 485.0)
        self.assertEqual(round(calculator.clothes_dryer_annual_therm_savings, 2), 0.0)

        self.assertEqual(round(calculator.appliance_kwh_savings, 2), 634.35)
        self.assertEqual(round(calculator.appliance_therm_savings, 2), 4.84)

    def test_total_report_kwh_basics(self):
        """Test out the Thermostat no change since V2"""

        kwargs = {
            "us_state": "OR",
            "heating_fuel": FuelType.ELECTRIC,
            "heating_system_config": "central",  # zonal, central, all
            "home_size": "all",  # small, medium, large, all
            "heating_zone": "hz2",  # hz1, hz2, hz3
            "water_heater_tier": "tier3",  # tier1, tier2, tier3
            "estar_std_refrigerators_installed": None,
            "estar_dishwasher_installed": True,
            "estar_clothes_washer_installed": CLOTHES_WASHER_TOP,
            "clothes_dryer_tier": None,  # tier1, tier2, tier3, estar
            "clothes_dryer_fuel": FuelType.NATURAL_GAS,
            "smart_thermostat_installed": True,
            "code_data": {
                "heating_therms": 10.0,
                "heating_kwh": 7630.0,
                "cooling_kwh": 570.0,
            },
            "improved_data": {
                "heating_therms": 9.0,
                "heating_kwh": 7272.0,
                "cooling_kwh": 590.0,
                "primary_heating_type": "heater",  # Add 'heat pump' to get heat_pump recognized
                "primary_cooling_type": "air conditioner",
                "primary_cooling_fuel": "electric",
                "primary_water_heating_type": "hpwh",
                # None, 'gas', 'hpwh', 'electric resistance'
            },
            "percent_improvement": 0.15,
            "electric_utility": "puget-sound-energy",
            "gas_utility": "foo",
        }

        neea_kwargs = kwargs.copy()

        calculator = NEEAV3Calculator(**neea_kwargs)

        _x = calculator.total_report()

        self.assertEqual(round(calculator.heating_kwh_savings, 2), 358.0)
        self.assertEqual(round(calculator.incentives.heating_kwh_measure_life.short, 2), 0.0)
        self.assertEqual(round(calculator.incentives.heating_kwh_measure_life.medium, 2), 35.8)
        self.assertEqual(round(calculator.incentives.heating_kwh_measure_life.long, 2), 322.2)

        self.assertEqual(round(calculator.smart_thermostat_kwh_savings, 2), 471.72)
        self.assertEqual(
            round(calculator.incentives.smart_thermostat_kwh_measure_life.short, 2), 471.72
        )
        self.assertEqual(
            round(calculator.incentives.smart_thermostat_kwh_measure_life.medium, 2), 0.0
        )
        self.assertEqual(
            round(calculator.incentives.smart_thermostat_kwh_measure_life.long, 2), 0.0
        )

        self.assertEqual(round(calculator.cooling_kwh_savings, 2), -20.0)
        self.assertEqual(round(calculator.incentives.cooling_kwh_measure_life.short, 2), 0.0)
        self.assertEqual(round(calculator.incentives.cooling_kwh_measure_life.medium, 2), -15.0)
        self.assertEqual(round(calculator.incentives.cooling_kwh_measure_life.long, 2), -5.0)

        self.assertEqual(round(calculator.water_heater_kwh_savings, 2), 1372.2)
        self.assertEqual(round(calculator.incentives.water_heater_kwh_measure_life.short, 2), 0.0)
        self.assertEqual(
            round(calculator.incentives.water_heater_kwh_measure_life.medium, 2), 1372.2
        )
        self.assertEqual(round(calculator.incentives.water_heater_kwh_measure_life.long, 2), 0.0)

        self.assertEqual(round(calculator.appliance_kwh_savings, 2), 86.64)
        self.assertEqual(round(calculator.incentives.appliances_kwh_measure_life.short, 2), 0.0)
        self.assertEqual(round(calculator.incentives.appliances_kwh_measure_life.medium, 2), 86.64)
        self.assertEqual(round(calculator.incentives.appliances_kwh_measure_life.long, 2), 0.0)

        self.assertEqual(round(calculator.total_kwh_savings, 2), 2268.56)
        self.assertEqual(round(calculator.incentives.total_kwh_measure_life.short, 2), 471.72)
        self.assertEqual(round(calculator.incentives.total_kwh_measure_life.medium, 2), 1479.64)
        self.assertEqual(round(calculator.incentives.total_kwh_measure_life.long, 2), 317.2)

        self.assertEqual(round(calculator.heating_therm_savings, 2), 1.0)
        self.assertEqual(round(calculator.incentives.heating_therm_measure_life.short, 2), 0.0)
        self.assertEqual(round(calculator.incentives.heating_therm_measure_life.medium, 2), 0.1)
        self.assertEqual(round(calculator.incentives.heating_therm_measure_life.long, 2), 0.9)

        self.assertEqual(round(calculator.smart_thermostat_therm_savings, 2), 0.54)
        self.assertEqual(
            round(calculator.incentives.smart_thermostat_therm_measure_life.short, 2), 0.54
        )
        self.assertEqual(
            round(calculator.incentives.smart_thermostat_therm_measure_life.medium, 2), 0.0
        )
        self.assertEqual(
            round(calculator.incentives.smart_thermostat_therm_measure_life.long, 2), 0.0
        )

        self.assertEqual(round(calculator.cooling_therm_savings, 2), 0.0)
        self.assertEqual(round(calculator.incentives.cooling_therm_measure_life.short, 2), 0.0)
        self.assertEqual(round(calculator.incentives.cooling_therm_measure_life.medium, 2), 0.0)
        self.assertEqual(round(calculator.incentives.cooling_therm_measure_life.long, 2), 0.0)

        self.assertEqual(round(calculator.appliance_therm_savings, 2), -0.43)
        self.assertEqual(round(calculator.incentives.appliances_therm_measure_life.short, 2), 0.0)
        self.assertEqual(
            round(calculator.incentives.appliances_therm_measure_life.medium, 2), -0.43
        )
        self.assertEqual(round(calculator.incentives.appliances_therm_measure_life.long, 2), 0.0)

        self.assertEqual(round(calculator.total_therm_savings, 2), 1.11)
        self.assertEqual(round(calculator.incentives.total_therm_measure_life.short, 2), 0.54)
        self.assertEqual(round(calculator.incentives.total_therm_measure_life.medium, 2), -0.33)
        self.assertEqual(round(calculator.incentives.total_therm_measure_life.long, 2), 0.9)

        self.assertEqual(round(calculator.code_data_total_consumption_mmbtu, 2), 28.98)
        self.assertEqual(round(calculator.improved_data_total_consumption_mmbtu, 2), 27.73)
        self.assertEqual(round(calculator.total_mmbtu_savings, 2), 7.85)

        self.assertEqual(round(calculator.incentives.percent_improvement, 2), 0.27)
        self.assertEqual(round(calculator.incentives.default_percent_improvement, 2), 0.15)
