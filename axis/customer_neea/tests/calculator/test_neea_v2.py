"""neea_v2.py - Axis"""

__author__ = "Steven K"
__date__ = "6/26/21 10:04"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from axis.core.tests.testcases import AxisTestCase
from axis.customer_neea.rtf_calculator.calculator import NEEAV2Calculator

log = logging.getLogger(__name__)


class NEEAV2CalculatorTests(AxisTestCase):
    def base_kwargs(self):
        return {
            "us_state": "OR",
            "heating_fuel": "electric",
            "heating_system_config": "central",  # zonal, central, all
            "home_size": "small",  # small, medium, large, all
            "heating_zone": "hz2",  # hz1, hz2, hz3
            "water_heater_tier": "electric resistance",  # tier1, tier2, tier3
            "cfl_installed": 5,
            "led_installed": 35,
            "total_installed_lamps": 40,
            "estar_std_refrigerators_installed": True,
            "estar_dishwasher_installed": True,
            "estar_front_load_clothes_washer_installed": True,
            "clothes_dryer_tier": "tier3",  # tier1, tier2, tier3
            "smart_thermostat_installed": True,
            "qty_shower_head_1p5": 1,
            "qty_shower_head_1p75": 0,
            "code_data": {
                "heating_therms": 30.0,
                "heating_kwh": 10000.0,
                "cooling_kwh": 2100.0,
            },
            "improved_data": {
                "heating_therms": 20.0,
                "heating_kwh": 8000.0,
                "cooling_kwh": 2000.0,
                "primary_heating_type": "heater",  # Add 'heat pump' to get heat_pump recognized
                "primary_cooling_type": "air conditioner",
                "primary_cooling_fuel": "electric",
            },
            "percent_improvement": 0.15,
            "electric_utility": "foo",
            "gas_utility": "foo",
            "certified_earth_advantage": None,
        }

    def test_neea_initial(self):
        kwargs = {
            "cfl_installed": 5,
            "clothes_dryer_tier": "tier3",
            "code_data": {"cooling_kwh": 2100.0, "heating_kwh": 10000.0, "heating_therms": 30.0},
            "estar_dishwasher_installed": True,
            "estar_front_load_clothes_washer_installed": True,
            "estar_std_refrigerators_installed": True,
            "heating_fuel": "electric",
            "heating_system_config": "central",
            "heating_zone": "hz2",
            "home_size": "small",
            "improved_data": {
                "cooling_kwh": 2000.0,
                "heating_kwh": 8000.0,
                "heating_therms": 20.0,
                "primary_heating_type": "Air-Source heat pump",
                "primary_cooling_type": "Air conditioner",
                "primary_cooling_fuel": "Electric",
            },
            "led_installed": 35,
            "percent_improvement": 0.15,
            "qty_shower_head_1p5": 1,
            "qty_shower_head_1p75": 0,
            "smart_thermostat_installed": True,
            "total_installed_lamps": 40,
            "us_state": "WA",
            "water_heater_tier": "electric resistance",
        }

        calculator = NEEAV2Calculator(**kwargs.copy())

        self.assertEqual(calculator.heating_fuel, "electric")
        self.assertEqual(calculator.heating_system_config, "central")
        self.assertEqual(calculator.home_size, "small")
        self.assertEqual(calculator.heating_zone, "hz2")
        self.assertEqual(calculator.cfl_installed, 5)
        self.assertEqual(calculator.led_installed, 35)
        self.assertEqual(calculator.total_installed_lamps, 40)
        self.assertEqual(calculator.smart_thermostat_installed, True)
        self.assertEqual(calculator.qty_shower_head_1p5, 1)
        self.assertEqual(calculator.qty_shower_head_1p75, 0)
        self.assertEqual(calculator.estar_dishwasher_installed, True)
        self.assertEqual(calculator.estar_std_refrigerators_installed, True)
        self.assertEqual(calculator.estar_front_load_clothes_washer_installed, True)
        self.assertEqual(round(calculator.heating_kwh_savings, 0), 2000.0)
        self.assertEqual(round(calculator.heating_therm_savings, 0), 10.0)
        self.assertEqual(round(calculator.cooling_kwh_savings, 0), 100.0)
        self.assertEqual(round(calculator.cooling_therm_savings, 0), 0.0)
        self.assertEqual(round(calculator.smart_thermostat_kwh_savings, 0), 1240.0)
        self.assertEqual(round(calculator.smart_thermostat_therm_savings, 0), 3.0)
        self.assertEqual(round(calculator.water_heater_kwh_savings, 0), 0.0)
        self.assertEqual(round(calculator.showerhead_kwh_savings, 0), 53.0)
        self.assertEqual(round(calculator.showerhead_therm_savings, 0), 0.0)
        self.assertEqual(round(calculator.lighting_kwh_savings, 0), 135.0)
        self.assertEqual(round(calculator.appliance_kwh_savings, 0), 562.0)
        self.assertEqual(round(calculator.total_kwh_savings, 0), 4090.0)
        self.assertEqual(round(calculator.total_therm_savings, 0), 13.0)
        self.assertEqual(round(calculator.total_mmbtu_savings, 0), 15.0)
        self.assertEqual(calculator.incentives.has_bpa_incentive, True)
        self.assertEqual(calculator.incentives.has_incentive, None)
        self.assertEqual(round(calculator.incentives.busbar_consumption, 0), 8010.0)
        self.assertEqual(round(calculator.incentives.busbar_savings, 0), 4090.0)
        self.assertEqual(calculator.incentives.pct_improvement_method, "alternate")
        self.assertEqual(calculator.incentives.incentive_paying_organization, None)
        self.assertEqual(round(calculator.incentives.default_percent_improvement, 3), 0.15)
        self.assertEqual(round(calculator.incentives.total_incentive, 0), 1190.0)
        self.assertEqual(round(calculator.incentives.bpa_hvac_kwh_savings, 0), 275.0)
        self.assertEqual(round(calculator.incentives.hvac_kwh_incentive, 0), 74.0)
        self.assertEqual(round(calculator.incentives.bpa_lighting_kwh_savings, 0), 135.0)
        self.assertEqual(round(calculator.incentives.lighting_kwh_incentive, 0), 13.0)
        self.assertEqual(round(calculator.incentives.bpa_water_heater_kwh_savings, 0), 0.0)
        self.assertEqual(round(calculator.incentives.water_heater_kwh_incentive, 0), 0.0)
        self.assertEqual(round(calculator.incentives.bpa_appliance_kwh_savings, 0), 562.0)
        self.assertEqual(round(calculator.incentives.appliance_kwh_incentive, 0), 152.0)
        self.assertEqual(round(calculator.incentives.bpa_windows_shell_kwh_savings, 0), 1825.0)
        self.assertEqual(round(calculator.incentives.windows_shell_kwh_incentive, 0), 821.0)
        self.assertEqual(round(calculator.incentives.bpa_smart_thermostat_kwh_savings, 0), 1240.0)
        self.assertEqual(round(calculator.incentives.smart_thermostat_kwh_incentive, 0), 124.0)

    def test_clark_14pct(self):
        # This was reported on home Home Status ID: 72082
        kwargs = {
            "heating_fuel": "gas",
            "qty_shower_head_1p75": "2",
            "hrv-combo": "Broan HRV160T",
            "ventilation-combo": "Broan 160HRV T",
            "improved_data": {
                "cooling_kwh": 815.05603,
                "primary_heating_type": "Fuel-fired air distribution heater",
                "primary_cooling_type": "Air conditioner",
                "primary_cooling_fuel": "Electric",
                "heating_kwh": 140.827835,
                "heating_therms": 369.596619,
            },
            "clothes_dryer_tier": "None",
            "smart_thermostat_installed": "Yes",
            "code_data": {
                "cooling_kwh": 717.479065,
                "total_consumption_therms": 622.326995,
                "total_consumption_kwh": 7742.188904,
                "heating_kwh": 587.599976,
                "heating_therms": 429.50592,
            },
            "home_size": "medium",
            "program_redirected": "No",
            "percent_improvement": 0.14915713958383725,
            "led_installed": "48",
            "estar_front_load_clothes_washer_installed": "No",
            "heating_source": "Gas with AC",
            "hvac-cooling-combo": "Trane 4PXCBD36/4TTR3030H1",
            "qty_shower_head_1p5": "0",
            "water_heater_tier": "Gas Tankless EF \u2265 0.82",
            "hvac-combo": "Trane S9V2B040D3PSAAB",
            "water-heater-combo": "Rinnai RL75i",
            "cfl_installed": "0",
            "gas_utility": "nw-natural-gas",
            "heating_zone": "hz1",
            "electric_utility": "clark-pud",
            "major-load-equipment": "No",
            "estar_std_refrigerators_installed": "No",
            "heating_system_config": "Central",
            "total_installed_lamps": "48",
            "estar_dishwasher_installed": "Yes",
            "us_state": "WA",
        }

        calculator = NEEAV2Calculator(**kwargs.copy())

        self.assertEqual(calculator.heating_fuel, "gas")
        self.assertEqual(calculator.heating_system_config, "central")
        self.assertEqual(calculator.home_size, "medium")
        self.assertEqual(calculator.heating_zone, "hz1")
        self.assertEqual(calculator.cfl_installed, 0)
        self.assertEqual(calculator.led_installed, 48)
        self.assertEqual(calculator.total_installed_lamps, 48)
        self.assertEqual(calculator.smart_thermostat_installed, True)
        self.assertEqual(calculator.qty_shower_head_1p5, 0)
        self.assertEqual(calculator.qty_shower_head_1p75, 2)
        self.assertEqual(calculator.estar_dishwasher_installed, True)
        self.assertEqual(calculator.estar_std_refrigerators_installed, False)
        self.assertEqual(calculator.estar_front_load_clothes_washer_installed, False)
        self.assertEqual(round(calculator.heating_kwh_savings, 0), 447.0)
        self.assertEqual(round(calculator.heating_therm_savings, 0), 60.0)
        self.assertEqual(round(calculator.cooling_kwh_savings, 0), -98.0)
        self.assertEqual(round(calculator.cooling_therm_savings, 0), 0.0)
        self.assertEqual(round(calculator.smart_thermostat_kwh_savings, 0), 57.0)
        self.assertEqual(round(calculator.smart_thermostat_therm_savings, 0), 22.0)
        self.assertEqual(round(calculator.water_heater_kwh_savings, 0), 0.0)
        self.assertEqual(round(calculator.water_heater_therm_savings, 0), 62.0)
        self.assertEqual(round(calculator.showerhead_kwh_savings, 0), 0.0)
        self.assertEqual(round(calculator.showerhead_therm_savings, 0), 4.0)
        self.assertEqual(round(calculator.lighting_kwh_savings, 0), 165.0)
        self.assertEqual(round(calculator.lighting_therm_savings, 0), 0.0)
        self.assertEqual(round(calculator.appliance_kwh_savings, 0), 59.0)
        self.assertEqual(round(calculator.appliance_therm_savings, 0), 0.0)
        self.assertEqual(round(calculator.total_kwh_savings, 0), 630.0)
        self.assertEqual(round(calculator.total_therm_savings, 0), 148.0)
        self.assertEqual(round(calculator.total_mmbtu_savings, 0), 17.0)
        self.assertEqual(calculator.incentives.has_incentive, True)
        self.assertEqual(round(calculator.incentives.reference_home_kwh, 0), 7742.0)
        self.assertEqual(round(calculator.incentives.busbar_consumption, 0), 7112.0)
        self.assertEqual(round(calculator.incentives.busbar_savings, 0), 630.0)
        self.assertEqual(calculator.incentives.pct_improvement_method, "alternate")
        self.assertEqual(calculator.incentives.incentive_paying_organization, "clark-pud")
        self.assertEqual(round(calculator.incentives.default_percent_improvement, 3), 0.149)
        self.assertEqual(round(calculator.incentives.percent_improvement, 3), 0.191)
        self.assertEqual(round(calculator.incentives.total_incentive, 0), 200.0)
        self.assertEqual(round(calculator.incentives.builder_incentive, 0), 200.0)
        self.assertEqual(round(calculator.incentives.bpa_hvac_kwh_savings, 0), -29.0)
        self.assertEqual(round(calculator.incentives.hvac_kwh_incentive, 0), -8.0)
        self.assertEqual(round(calculator.incentives.bpa_lighting_kwh_savings, 0), 165.0)
        self.assertEqual(calculator.incentives.lighting_kwh_incentive, 16.5)
        self.assertEqual(round(calculator.incentives.bpa_water_heater_kwh_savings, 0), 0.0)
        self.assertEqual(round(calculator.incentives.water_heater_kwh_incentive, 0), 0.0)
        self.assertEqual(round(calculator.incentives.bpa_appliance_kwh_savings, 0), 59.0)
        self.assertEqual(round(calculator.incentives.appliance_kwh_incentive, 0), 16.0)
        self.assertEqual(round(calculator.incentives.bpa_windows_shell_kwh_savings, 0), 378.0)
        self.assertEqual(round(calculator.incentives.windows_shell_kwh_incentive, 0), 170.0)
        self.assertEqual(round(calculator.incentives.bpa_smart_thermostat_kwh_savings, 0), 57.0)
        self.assertEqual(round(calculator.incentives.smart_thermostat_kwh_incentive, 0), 6.0)

    def test_clark_pud_full(self):
        kwargs = self.base_kwargs().copy()
        kwargs["electric_utility"] = "clark-pud"
        kwargs["gas_utility"] = "FOOBAR"
        kwargs["heating_fuel"] = "gas"
        kwargs["improved_data"]["heating_therms"] = 50.0
        kwargs["improved_data"]["heating_kwh"] = 10000.0
        kwargs["improved_data"]["cooling_kwh"] = 2100.0

        calculator = NEEAV2Calculator(**kwargs.copy())
        self.assertEqual(round(calculator.incentives.percent_improvement, 3), 0.073)
        self.assertEqual(calculator.incentives.has_incentive, False)
        self.assertEqual(round(calculator.incentives.total_incentive, 0), 0.0)
        self.assertEqual(round(calculator.incentives.builder_incentive, 0), 0.0)

        kwargs["gas_utility"] = "nw-natural-gas"
        kwargs["heating_fuel"] = "electric"
        calculator = NEEAV2Calculator(**kwargs.copy())
        self.assertEqual(round(calculator.incentives.percent_improvement, 3), 0.073)
        self.assertEqual(calculator.incentives.has_incentive, False)
        self.assertEqual(round(calculator.incentives.total_incentive, 0), 0.0)
        self.assertEqual(round(calculator.incentives.builder_incentive, 0), 0.0)

        kwargs["heating_fuel"] = "gas"
        calculator = NEEAV2Calculator(**kwargs.copy())
        self.assertEqual(round(calculator.incentives.percent_improvement, 3), 0.073)
        self.assertEqual(calculator.incentives.has_incentive, False)
        self.assertEqual(round(calculator.incentives.total_incentive, 0), 0.0)
        self.assertEqual(round(calculator.incentives.builder_incentive, 0), 0.0)

        kwargs["heating_fuel"] = "electric"
        kwargs["improved_data"]["heating_therms"] = 50.0
        kwargs["improved_data"]["heating_kwh"] = 9500.0
        kwargs["improved_data"]["cooling_kwh"] = 2100.0
        calculator = NEEAV2Calculator(**kwargs.copy())
        self.assertEqual(round(calculator.incentives.percent_improvement, 3), 0.109)
        self.assertEqual(calculator.incentives.has_incentive, True)
        self.assertEqual(round(calculator.incentives.total_incentive, 0), 453.0)
        self.assertEqual(round(calculator.incentives.builder_incentive, 0), 453.0)

        kwargs["heating_fuel"] = "gas"
        kwargs["improved_data"]["heating_therms"] = 50.0
        kwargs["improved_data"]["heating_kwh"] = 9500.0
        kwargs["improved_data"]["cooling_kwh"] = 2100.0
        calculator = NEEAV2Calculator(**kwargs.copy())
        self.assertEqual(round(calculator.incentives.percent_improvement, 3), 0.109)
        self.assertEqual(calculator.incentives.has_incentive, True)
        self.assertEqual(round(calculator.incentives.total_incentive, 0), 453.0)
        self.assertEqual(round(calculator.incentives.builder_incentive, 0), 453.0)

        kwargs["heating_fuel"] = "electric"
        kwargs["improved_data"]["heating_therms"] = 20.0
        kwargs["improved_data"]["heating_kwh"] = 7500.0
        kwargs["improved_data"]["cooling_kwh"] = 2000.0
        calculator = NEEAV2Calculator(**kwargs.copy())

        self.assertEqual(round(calculator.incentives.percent_improvement, 3), 0.325)
        self.assertEqual(calculator.incentives.has_incentive, True)
        self.assertEqual(round(calculator.incentives.total_incentive, 0), 1336.0)
        self.assertEqual(round(calculator.incentives.builder_incentive, 0), 1836.0)

        # Others
        self.assertEqual(calculator.heating_fuel, "electric")
        self.assertEqual(calculator.heating_system_config, "central")
        self.assertEqual(calculator.home_size, "all")
        self.assertEqual(calculator.heating_zone, "hz2")
        self.assertEqual(calculator.cfl_installed, 5)
        self.assertEqual(calculator.led_installed, 35)
        self.assertEqual(calculator.total_installed_lamps, 40)
        self.assertEqual(calculator.smart_thermostat_installed, True)
        self.assertEqual(calculator.qty_shower_head_1p5, 1)
        self.assertEqual(calculator.qty_shower_head_1p75, 0)
        self.assertEqual(calculator.estar_dishwasher_installed, True)
        self.assertEqual(calculator.estar_std_refrigerators_installed, True)
        self.assertEqual(calculator.estar_front_load_clothes_washer_installed, True)
        self.assertEqual(round(calculator.heating_kwh_savings, 0), 2500.0)
        self.assertEqual(round(calculator.heating_therm_savings, 0), 10.0)
        self.assertEqual(round(calculator.cooling_kwh_savings, 0), 100.0)
        self.assertEqual(round(calculator.cooling_therm_savings, 0), 0.0)
        self.assertEqual(round(calculator.smart_thermostat_kwh_savings, 0), 570.0)
        self.assertEqual(round(calculator.smart_thermostat_therm_savings, 0), 1.0)
        self.assertEqual(round(calculator.water_heater_kwh_savings, 0), 0.0)
        self.assertEqual(round(calculator.showerhead_kwh_savings, 0), 153.0)
        self.assertEqual(round(calculator.showerhead_therm_savings, 0), 0.0)
        self.assertEqual(round(calculator.lighting_kwh_savings, 0), 0.0)
        self.assertEqual(round(calculator.appliance_kwh_savings, 0), 562.0)
        self.assertEqual(round(calculator.total_kwh_savings, 0), 3885.0)
        self.assertEqual(round(calculator.total_therm_savings, 0), 11.0)
        self.assertEqual(round(calculator.total_mmbtu_savings, 0), 14.0)
        self.assertEqual(calculator.incentives.has_incentive, True)
        self.assertEqual(round(calculator.incentives.busbar_consumption, 0), 8215.0)
        self.assertEqual(round(calculator.incentives.busbar_savings, 0), 3885.0)
        self.assertEqual(calculator.incentives.pct_improvement_method, "alternate")
        self.assertEqual(round(calculator.incentives.default_percent_improvement, 3), 0.15)
        self.assertEqual(round(calculator.incentives.percent_improvement, 3), 0.325)
        self.assertEqual(round(calculator.incentives.total_incentive, 0), 1336.0)
        self.assertEqual(round(calculator.incentives.builder_incentive, 0), 1836.0)
        self.assertEqual(round(calculator.incentives.bpa_hvac_kwh_savings, 0), 325.0)
        self.assertEqual(round(calculator.incentives.hvac_kwh_incentive, 0), 88.0)
        self.assertEqual(round(calculator.incentives.bpa_lighting_kwh_savings, 0), 0.0)
        self.assertEqual(round(calculator.incentives.lighting_kwh_incentive, 0), 0.0)
        self.assertEqual(round(calculator.incentives.bpa_water_heater_kwh_savings, 0), 0.0)
        self.assertEqual(round(calculator.incentives.water_heater_kwh_incentive, 0), 0.0)
        self.assertEqual(round(calculator.incentives.bpa_appliance_kwh_savings, 0), 562.0)
        self.assertEqual(round(calculator.incentives.appliance_kwh_incentive, 0), 152.0)
        self.assertEqual(round(calculator.incentives.bpa_windows_shell_kwh_savings, 0), 2275.0)
        self.assertEqual(round(calculator.incentives.windows_shell_kwh_incentive, 0), 1024.0)
        self.assertEqual(round(calculator.incentives.bpa_smart_thermostat_kwh_savings, 0), 570.0)
        self.assertEqual(round(calculator.incentives.smart_thermostat_kwh_incentive, 0), 57.0)

    def get_pse_kwargs(self):
        return {
            "us_state": "OR",
            "heating_fuel": "electric",
            "heating_system_config": "central",  # zonal, central, all
            "home_size": "small",  # small, medium, large, all
            "heating_zone": "hz2",  # hz1, hz2, hz3
            "water_heater_tier": "Gas Conventional EF \u2265 0.67",  # tier1, tier2, tier3
            "cfl_installed": 5,
            "led_installed": 35,
            "total_installed_lamps": 40,
            "estar_std_refrigerators_installed": True,
            "estar_dishwasher_installed": True,
            "estar_front_load_clothes_washer_installed": True,
            "clothes_dryer_tier": "tier3",  # tier1, tier2, tier3
            "smart_thermostat_installed": True,
            "qty_shower_head_1p5": 1,
            "qty_shower_head_1p75": 0,
            "code_data": {
                "heating_therms": 30.0,
                "heating_kwh": 36000.0,
                "cooling_kwh": 2100.0,
            },
            "improved_data": {
                "heating_therms": 30.0,
                "heating_kwh": 36000.0,
                "cooling_kwh": 2100.0,
                "primary_heating_type": "heater",
                "primary_cooling_type": "air conditioner",
                "primary_cooling_fuel": "electric",
            },
            "percent_improvement": 0.08,
            "electric_utility": "puget-sound-energy",
            "gas_utility": "foo",
        }.copy()

    def test_puget_incentives(self):
        kwargs = self.get_pse_kwargs()
        calculator = NEEAV2Calculator(**kwargs.copy())
        self.assertEqual(calculator.incentives.pct_improvement_method, "alternate")
        self.assertEqual(round(calculator.incentives.default_percent_improvement, 3), 0.08)
        self.assertEqual(round(calculator.incentives.revised_percent_improvement, 3), 0.099)
        self.assertEqual(
            round(calculator.incentives.revised_percent_improvement, 3),
            round(calculator.incentives.percent_improvement, 3),
        )
        self.assertEqual(calculator.incentives.required_pct_improvement, 0.0)
        self.assertEqual(calculator.incentives.incentive_paying_organization, "puget-sound-energy")

        with self.subTest("Gas Only"):
            kwargs = self.get_pse_kwargs()
            kwargs["electric_utility"] = "foo"
            kwargs["gas_utility"] = "puget-sound-energy"
            calculator = NEEAV2Calculator(**kwargs)
            self.assertFalse(calculator.incentives.has_incentive)
            self.assertFalse(calculator.incentives.has_bpa_incentive)
            self.assertEqual(calculator.incentives.builder_incentive, 0)
            self.assertIn("No", calculator.incentives.utility_report()[-1])

        with self.subTest("Electric Only"):
            kwargs = self.get_pse_kwargs()
            calculator = NEEAV2Calculator(**kwargs)
            self.assertTrue(calculator.incentives.has_incentive)
            self.assertTrue(calculator.incentives.has_bpa_incentive)
            default = sum(
                [
                    # calculator.incentives.hvac_kwh_incentive,
                    calculator.incentives.lighting_kwh_incentive,
                    # calculator.incentives.water_heater_kwh_incentive,
                    calculator.incentives.appliance_kwh_incentive,
                    calculator.incentives.windows_shell_kwh_incentive,
                    calculator.incentives.smart_thermostat_kwh_incentive,
                    calculator.incentives.showerhead_kwh_incentive,
                ]
            )
            self.assertEqual(calculator.incentives.builder_incentive, default)
            self.assertAlmostEqual(calculator.incentives.builder_incentive, 380.35, 2)
            self.assertIn("Yes", calculator.incentives.utility_report()[-1])

        with self.subTest("Electric & Gas"):
            kwargs = self.get_pse_kwargs()
            kwargs["gas_utility"] = "puget-sound-energy"
            kwargs["heating_fuel"] = "gas"
            calculator = NEEAV2Calculator(**kwargs)
            self.assertTrue(calculator.incentives.has_incentive)
            self.assertTrue(calculator.incentives.has_bpa_incentive)
            default = 5.0 * calculator.incentives.total_therm_savings
            self.assertEqual(calculator.incentives.builder_incentive, default)
            self.assertAlmostEqual(calculator.incentives.builder_incentive, 170.29, 2)
            self.assertIn("Yes", calculator.incentives.utility_report()[-1])

    def test_pacific_power_incentives(self):
        kwargs = self.base_kwargs().copy()
        kwargs["us_state"] = "WA"
        kwargs["electric_utility"] = "pacific-power"
        kwargs["gas_utility"] = "FOOBAR"
        kwargs["heating_fuel"] = "gas"
        kwargs["water_heater_tier"] = "electric resistance"
        kwargs["improved_data"]["primary_heating_type"] = "Fuel-fired heat pump"
        kwargs["improved_data"]["primary_cooling_type"] = "air conditioner"
        kwargs["improved_data"]["primary_cooling_fuel"] = "Natural Gas"

        with self.subTest(
            "Heat: Electric, Cooling: Electric, Electric Water: 10-20% Improvement - $1875"
        ):
            kwargs["heating_fuel"] = "electric"
            kwargs["water_heater_tier"] = "electric resistance"
            kwargs["improved_data"]["heating_therms"] = 50.0
            kwargs["improved_data"]["heating_kwh"] = 10000.0
            kwargs["improved_data"]["cooling_kwh"] = 2100.0
            calculator = NEEAV2Calculator(**kwargs.copy())
            self.assertAlmostEqual(calculator.incentives.percent_improvement, 0.146, 3)
            self.assertAlmostEqual(calculator.incentives.total_incentive, 323.0, 0)
            self.assertAlmostEqual(calculator.incentives.builder_incentive, 1875.0, 0)
            self.assertEqual(
                calculator.incentives.incentive_paying_organization, kwargs["electric_utility"]
            )
            kwargs["water_heater_tier"] = "Gas Conventional EF < 0.67"
            calculator = NEEAV2Calculator(**kwargs.copy())
            self.assertAlmostEqual(calculator.incentives.percent_improvement, 0.147, 3)
            self.assertAlmostEqual(calculator.incentives.total_incentive, 317.81, 0)
            self.assertAlmostEqual(calculator.incentives.builder_incentive, 0.0, 0)

        with self.subTest(
            "Heat: Electric, Cooling: Electric, Electric Water: 20+% Improvement - $3125"
        ):
            kwargs["heating_fuel"] = "electric"
            kwargs["improved_data"]["heating_therms"] = 50.0
            kwargs["improved_data"]["heating_kwh"] = 9000.0
            kwargs["improved_data"]["cooling_kwh"] = 2100.0
            kwargs["water_heater_tier"] = "electric resistance"
            calculator = NEEAV2Calculator(**kwargs.copy())
            self.assertEqual(calculator.incentives.pct_improvement_method, "alternate")
            self.assertAlmostEqual(calculator.incentives.percent_improvement, 0.21227, 3)
            self.assertAlmostEqual(calculator.incentives.total_incentive, 741.16, 0)
            self.assertAlmostEqual(calculator.incentives.builder_incentive, 3125.0, 0)
            kwargs["water_heater_tier"] = "Gas Conventional EF < 0.67"
            calculator = NEEAV2Calculator(**kwargs.copy())
            self.assertAlmostEqual(calculator.incentives.percent_improvement, 0.213647, 3)
            self.assertAlmostEqual(calculator.incentives.total_incentive, 735.81, 0)
            self.assertAlmostEqual(calculator.incentives.builder_incentive, 0.0, 0)

        with self.subTest(
            "Heat: Electric, Cooling: Electric, Electric Water: 0-10% Improvement - $Variable"
        ):
            kwargs["heating_fuel"] = "electric"
            kwargs["improved_data"]["heating_therms"] = 90.0
            kwargs["improved_data"]["heating_kwh"] = 10000.0
            kwargs["improved_data"]["cooling_kwh"] = 2100.0
            kwargs["water_heater_tier"] = "electric resistance"
            calculator = NEEAV2Calculator(**kwargs.copy())
            self.assertAlmostEqual(calculator.incentives.percent_improvement, 0.06833, 3)
            self.assertAlmostEqual(calculator.incentives.total_incentive, 0.0, 0)
            self.assertAlmostEqual(
                calculator.incentives.builder_incentive / calculator.incentives.total_kwh_savings,
                0.500,
                3,
            )
            kwargs["water_heater_tier"] = "Gas Conventional EF < 0.67"
            calculator = NEEAV2Calculator(**kwargs.copy())
            self.assertAlmostEqual(calculator.incentives.percent_improvement, 0.06970, 3)
            self.assertAlmostEqual(calculator.incentives.total_incentive, 0.0, 0)
            self.assertAlmostEqual(calculator.incentives.builder_incentive, 0.0, 0)

        with self.subTest("Heat: Gas, Cooling: Electric, Electric Water: 0-10% Improvement - $625"):
            kwargs["heating_fuel"] = "gas"
            kwargs["improved_data"]["heating_therms"] = 32.0
            kwargs["improved_data"]["heating_kwh"] = 10000.0
            kwargs["improved_data"]["cooling_kwh"] = 2100.0
            kwargs["water_heater_tier"] = "electric resistance"
            kwargs["improved_data"]["primary_cooling_fuel"] = "electric"
            kwargs["gas_utility"] = "cascade-gas"
            calculator = NEEAV2Calculator(**kwargs.copy())
            calculator.incentives.utility_report()
            self.assertAlmostEqual(calculator.incentives.percent_improvement, 0.11355, 3)
            self.assertAlmostEqual(calculator.incentives.total_incentive, 243.16, 0)
            self.assertAlmostEqual(calculator.incentives.builder_incentive, 625.0, 0)
            kwargs["improved_data"]["primary_cooling_fuel"] = "wood"
            calculator = NEEAV2Calculator(**kwargs.copy())
            self.assertAlmostEqual(calculator.incentives.percent_improvement, 0.11355, 3)
            self.assertAlmostEqual(calculator.incentives.total_incentive, 243.16, 0)
            self.assertAlmostEqual(calculator.incentives.builder_incentive, 0.0, 0)

            kwargs["improved_data"]["primary_cooling_fuel"] = "electric"
            kwargs["improved_data"]["heating_therms"] = 40.0
            calculator = NEEAV2Calculator(**kwargs.copy())
            self.assertAlmostEqual(calculator.incentives.percent_improvement, 0.09657, 3)
            self.assertAlmostEqual(calculator.incentives.total_incentive, 0.0, 0)
            self.assertAlmostEqual(calculator.incentives.builder_incentive, 0.0, 0)

    def test_idaho_power_incentive(self):
        kwargs = self.base_kwargs().copy()
        kwargs["electric_utility"] = "idaho-power"
        kwargs["heating_fuel"] = "electric"

        kwargs["code_data"] = {
            "heating_therms": 30.0,
            "heating_kwh": 10000.0,
            "cooling_kwh": 2100.0,
        }
        kwargs["improved_data"] = {
            "heating_therms": 30.0,
            "heating_kwh": 11000.0,
            "cooling_kwh": 2100.0,
            "primary_heating_type": "heat pump",
            "primary_cooling_type": "air conditioner",
            "primary_cooling_fuel": "electric",
        }

        # Valid
        # incentive tier - 1200
        calculator = NEEAV2Calculator(**kwargs.copy())
        self.assertEqual(calculator.incentives.pct_improvement_method, "alternate")
        self.assertEqual(round(calculator.incentives.percent_improvement, 3), 0.116)
        self.assertEqual(round(calculator.incentives.total_incentive, 0), 0.0)
        self.assertEqual(round(calculator.incentives.builder_incentive, 0), 1200.0)
        self.assertEqual(
            calculator.incentives.incentive_paying_organization, kwargs["electric_utility"]
        )

        # incentive tier - 1500
        kwargs["improved_data"]["heating_therms"] = 30.0
        kwargs["improved_data"]["heating_kwh"] = 10000.0
        kwargs["improved_data"]["cooling_kwh"] = 2100.0

        calculator = NEEAV2Calculator(**kwargs.copy())
        self.assertEqual(calculator.incentives.pct_improvement_method, "alternate")
        self.assertEqual(round(calculator.incentives.percent_improvement, 3), 0.182)
        self.assertEqual(round(calculator.incentives.total_incentive, 0), 320.0)
        self.assertEqual(round(calculator.incentives.builder_incentive, 0), 1500.0)

        # incentive tier - 2000
        kwargs["improved_data"]["heating_therms"] = 30.0
        kwargs["improved_data"]["heating_kwh"] = 8000.0
        kwargs["improved_data"]["cooling_kwh"] = 2100.0
        calculator = NEEAV2Calculator(**kwargs.copy())
        self.assertEqual(calculator.incentives.pct_improvement_method, "alternate")
        self.assertEqual(round(calculator.incentives.percent_improvement, 3), 0.315)
        self.assertEqual(round(calculator.incentives.total_incentive, 0), 1156.0)
        self.assertEqual(round(calculator.incentives.builder_incentive, 0), 2000.0)

        # Invalid
        kwargs["improved_data"]["heating_therms"] = 30.0
        kwargs["improved_data"]["heating_kwh"] = 12000.0
        kwargs["improved_data"]["cooling_kwh"] = 2100.0
        calculator = NEEAV2Calculator(**kwargs.copy())
        self.assertEqual(round(calculator.incentives.percent_improvement, 3), 0.05)
        self.assertEqual(round(calculator.incentives.total_incentive, 0), 0.0)
        self.assertEqual(round(calculator.incentives.builder_incentive, 0), 0.0)

        kwargs["heating_fuel"] = "gas"
        kwargs["improved_data"]["heating_therms"] = 30.0
        kwargs["improved_data"]["heating_kwh"] = 10000.0
        kwargs["improved_data"]["cooling_kwh"] = 2100.0
        calculator = NEEAV2Calculator(**kwargs.copy())
        self.assertEqual(round(calculator.incentives.percent_improvement, 3), 0.115)
        self.assertEqual(round(calculator.incentives.total_incentive, 0), 240.0)
        self.assertEqual(round(calculator.incentives.builder_incentive, 0), 0.0)

        kwargs["heating_fuel"] = "electric"
        kwargs["improved_data"]["primary_heating_type"] = "heater"
        kwargs["improved_data"]["heating_therms"] = 30.0
        kwargs["improved_data"]["heating_kwh"] = 10000.0
        kwargs["improved_data"]["cooling_kwh"] = 2100.0

        calculator = NEEAV2Calculator(**kwargs.copy())
        self.assertEqual(round(calculator.incentives.percent_improvement, 3), 0.115)
        self.assertEqual(round(calculator.incentives.total_incentive, 0), 240.0)
        self.assertEqual(round(calculator.incentives.builder_incentive, 0), 0.0)

    def test_benton_rea_incentive(self):
        kwargs = self.base_kwargs().copy()
        kwargs["electric_utility"] = "benton-rea"
        kwargs["heating_fuel"] = "electric"

        kwargs["improved_data"]["heating_therms"] = 30.0
        kwargs["improved_data"]["heating_kwh"] = 10000.0
        kwargs["improved_data"]["cooling_kwh"] = 2100.0

        # Valid
        calculator = NEEAV2Calculator(**kwargs.copy())
        self.assertEqual(calculator.incentives.has_incentive, True)
        self.assertEqual(calculator.incentives.pct_improvement_method, "alternate")
        self.assertEqual(round(calculator.incentives.percent_improvement, 3), 0.115)
        self.assertEqual(round(calculator.incentives.total_incentive, 0), 240.0)
        self.assertEqual(round(calculator.incentives.builder_incentive, 0), 240.0)
        self.assertEqual(
            calculator.incentives.incentive_paying_organization, kwargs["electric_utility"]
        )

        kwargs["improved_data"]["heating_therms"] = 30.0
        kwargs["improved_data"]["heating_kwh"] = 12000.0
        kwargs["improved_data"]["cooling_kwh"] = 2100.0
        calculator = NEEAV2Calculator(**kwargs.copy())
        self.assertEqual(calculator.incentives.has_incentive, False)
        self.assertEqual(round(calculator.incentives.builder_incentive, 0), 0.0)

        kwargs["improved_data"]["heating_therms"] = 30.0
        kwargs["improved_data"]["heating_kwh"] = 10000.0
        kwargs["improved_data"]["cooling_kwh"] = 2100.0
        kwargs["heating_fuel"] = "gas"
        kwargs.pop("gas_utility")
        calculator = NEEAV2Calculator(**kwargs.copy())
        self.assertEqual(calculator.incentives.has_incentive, False)
        self.assertEqual(round(calculator.incentives.builder_incentive, 0), 0.0)

    def test_inland_power_incentives(self):
        kwargs = self.base_kwargs().copy()
        kwargs["electric_utility"] = "inland-power"
        kwargs["improved_data"]["heating_therms"] = 30.0
        kwargs["improved_data"]["heating_kwh"] = 11000.0
        kwargs["improved_data"]["cooling_kwh"] = 2100.0
        kwargs["heating_fuel"] = "gas"

        calculator = NEEAV2Calculator(**kwargs.copy())
        self.assertEqual(calculator.incentives.pct_improvement_method, "alternate")
        self.assertEqual(round(calculator.incentives.percent_improvement, 3), 0.043)
        self.assertEqual(round(calculator.incentives.total_incentive, 0), 0.0)
        self.assertEqual(round(calculator.incentives.builder_incentive, 0), 0.0)
        self.assertEqual(
            calculator.incentives.incentive_paying_organization, kwargs["electric_utility"]
        )

        kwargs["improved_data"]["heating_therms"] = 30.0
        kwargs["improved_data"]["heating_kwh"] = 11000.0
        kwargs["improved_data"]["cooling_kwh"] = 2100.0
        kwargs["heating_fuel"] = "electric"
        calculator = NEEAV2Calculator(**kwargs.copy())
        self.assertEqual(round(calculator.incentives.percent_improvement, 3), 0.043)
        self.assertEqual(round(calculator.incentives.total_incentive, 0), 0.0)
        self.assertEqual(round(calculator.incentives.builder_incentive, 0), 0.0)

        kwargs["improved_data"]["heating_therms"] = 30.0
        kwargs["improved_data"]["heating_kwh"] = 10000.0
        kwargs["improved_data"]["cooling_kwh"] = 2100.0
        kwargs["heating_fuel"] = "electric"
        kwargs["water_heater_tier"] = "Gas Conventional EF \u2265 0.67"
        calculator = NEEAV2Calculator(**kwargs.copy())
        self.assertEqual(round(calculator.incentives.percent_improvement, 3), 0.176)
        self.assertEqual(round(calculator.incentives.total_incentive, 0), 224.0)
        self.assertEqual(round(calculator.incentives.builder_incentive, 0), 0.0)

        # Valid
        kwargs["improved_data"]["heating_therms"] = 30.0
        kwargs["improved_data"]["heating_kwh"] = 10000.0
        kwargs["improved_data"]["cooling_kwh"] = 2100.0
        kwargs["water_heater_tier"] = "Electric Resistance"
        calculator = NEEAV2Calculator(**kwargs.copy())
        self.assertEqual(round(calculator.incentives.percent_improvement, 3), 0.115)
        self.assertEqual(round(calculator.incentives.total_incentive, 0), 240.0)
        self.assertEqual(round(calculator.incentives.builder_incentive, 0), 240.0)

    def test_utility_city_of_richland_incentives(self):
        kwargs = self.base_kwargs().copy()
        kwargs["electric_utility"] = "utility-city-of-richland"
        kwargs["improved_data"]["heating_therms"] = 30.0
        kwargs["improved_data"]["heating_kwh"] = 10000.0
        kwargs["improved_data"]["cooling_kwh"] = 2100.0
        kwargs["heating_fuel"] = "electric"

        # Valid
        calculator = NEEAV2Calculator(**kwargs.copy())
        self.assertEqual(calculator.incentives.has_incentive, True)
        self.assertEqual(calculator.incentives.pct_improvement_method, "alternate")
        self.assertEqual(round(calculator.incentives.percent_improvement, 3), 0.115)
        self.assertEqual(round(calculator.incentives.total_incentive, 0), 240.0)
        self.assertEqual(round(calculator.incentives.builder_incentive, 0), 240.0)
        self.assertEqual(
            calculator.incentives.incentive_paying_organization, kwargs["electric_utility"]
        )

        kwargs["improved_data"]["heating_therms"] = 30.0
        kwargs["improved_data"]["heating_kwh"] = 11000.0
        kwargs["improved_data"]["cooling_kwh"] = 2100.0
        calculator = NEEAV2Calculator(**kwargs.copy())
        self.assertEqual(calculator.incentives.has_incentive, False)
        self.assertEqual(round(calculator.incentives.builder_incentive, 0), 0.0)

        kwargs["percent_improvement"] = 0.10
        kwargs["heating_fuel"] = "gas"
        calculator = NEEAV2Calculator(**kwargs.copy())
        self.assertEqual(calculator.incentives.has_incentive, False)
        self.assertEqual(round(calculator.incentives.builder_incentive, 0), 0.0)

    def test_eweb_incentives(self):
        kwargs = self.base_kwargs().copy()
        kwargs["electric_utility"] = "utility-eugene-water-electric-board"

        # All but heating type
        kwargs["improved_data"]["heating_therms"] = 30.0
        kwargs["improved_data"]["heating_kwh"] = 10000.0
        kwargs["improved_data"]["cooling_kwh"] = 2100.0
        kwargs["improved_data"]["primary_heating_type"] = "Fuel-fired air distribution heater"
        kwargs["heating_fuel"] = "gas"
        kwargs["water_heater_tier"] = "HPWH Tier 1"
        kwargs["certified_earth_advantage"] = "Platinum"
        calculator = NEEAV2Calculator(**kwargs.copy())
        self.assertEqual(round(calculator.incentives.percent_improvement, 3), 0.203)
        self.assertEqual(round(calculator.incentives.total_incentive, 0), 560.0)
        self.assertEqual(round(calculator.incentives.builder_incentive, 0), 0.0)

        # All but hot water type
        kwargs["improved_data"]["heating_therms"] = 30.0
        kwargs["improved_data"]["heating_kwh"] = 10000.0
        kwargs["improved_data"]["cooling_kwh"] = 2100.0
        kwargs["heating_fuel"] = "electric"
        kwargs["water_heater_tier"] = "Gas Tankless EF \u2265 0.82"
        kwargs["certified_earth_advantage"] = "Platinum"
        calculator = NEEAV2Calculator(**kwargs.copy())
        self.assertEqual(round(calculator.incentives.percent_improvement, 3), 0.259)
        self.assertEqual(round(calculator.incentives.total_incentive, 0), 224.0)
        self.assertEqual(round(calculator.incentives.builder_incentive, 0), 0.0)

        # All but heating fuel
        kwargs["improved_data"]["heating_therms"] = 30.0
        kwargs["improved_data"]["heating_kwh"] = 10000.0
        kwargs["improved_data"]["cooling_kwh"] = 2100.0
        kwargs["heating_fuel"] = "gas"
        kwargs["water_heater_tier"] = "HPWH Tier 1"
        kwargs["certified_earth_advantage"] = "Platinum"
        calculator = NEEAV2Calculator(**kwargs.copy())
        self.assertEqual(round(calculator.incentives.percent_improvement, 3), 0.203)
        self.assertEqual(round(calculator.incentives.total_incentive, 0), 560.0)
        self.assertEqual(round(calculator.incentives.builder_incentive, 0), 0.0)

        # All but EA Certfied
        kwargs["improved_data"]["heating_therms"] = 30.0
        kwargs["improved_data"]["heating_kwh"] = 10000.0
        kwargs["improved_data"]["cooling_kwh"] = 2100.0
        kwargs["heating_fuel"] = "electric"
        kwargs["water_heater_tier"] = "HPWH Tier 1"
        kwargs["certified_earth_advantage"] = None
        calculator = NEEAV2Calculator(**kwargs.copy())
        self.assertEqual(round(calculator.incentives.percent_improvement, 3), 0.203)
        self.assertEqual(round(calculator.incentives.total_incentive, 0), 560.0)
        self.assertEqual(round(calculator.incentives.builder_incentive, 0), 0.0)

        # Valid Path 1 Non-Equipment Path
        kwargs["improved_data"]["heating_therms"] = 30.0
        kwargs["improved_data"]["heating_kwh"] = 10000.0
        kwargs["improved_data"]["cooling_kwh"] = 2100.0
        kwargs["heating_fuel"] = "electric"
        kwargs["water_heater_tier"] = "electric resistance"
        kwargs["certified_earth_advantage"] = "Gold"
        calculator = NEEAV2Calculator(**kwargs.copy())

        self.assertEqual(round(calculator.incentives.percent_improvement, 3), 0.115)
        self.assertEqual(round(calculator.incentives.total_incentive, 0), 240.0)
        self.assertEqual(round(calculator.incentives.builder_incentive, 0), 240.0)

        # Valid Path 2 HPWH Only
        kwargs["improved_data"]["heating_therms"] = 30.0
        kwargs["improved_data"]["heating_kwh"] = 10000.0
        kwargs["improved_data"]["cooling_kwh"] = 2100.0
        kwargs["heating_fuel"] = "electric"
        kwargs["water_heater_tier"] = "HPWH Tier 1"
        kwargs["certified_earth_advantage"] = "Gold"
        calculator = NEEAV2Calculator(**kwargs.copy())

        self.assertEqual(round(calculator.incentives.percent_improvement, 3), 0.203)
        self.assertEqual(round(calculator.incentives.total_incentive, 0), 560.0)
        self.assertEqual(round(calculator.incentives.builder_incentive, 0), 800.0)

        # Valid Path 2 HPWH and HP
        kwargs["improved_data"]["heating_therms"] = 30.0
        kwargs["improved_data"]["heating_kwh"] = 10000.0
        kwargs["improved_data"]["cooling_kwh"] = 2100.0
        kwargs["improved_data"]["primary_heating_type"] = "Air-Source heat pump"
        kwargs["heating_fuel"] = "electric"
        kwargs["water_heater_tier"] = "HPWH Tier 1"
        kwargs["certified_earth_advantage"] = "Gold"
        calculator = NEEAV2Calculator(**kwargs.copy())

        self.assertEqual(round(calculator.incentives.percent_improvement, 3), 0.270)
        self.assertEqual(round(calculator.incentives.total_incentive, 0), 640.0)
        self.assertEqual(round(calculator.incentives.builder_incentive, 0), 1800.0)

    def test_tacoma_incentives(self):
        kwargs = self.base_kwargs().copy()
        kwargs["electric_utility"] = "utility-tacoma-public-utilities"

        # All but heating type
        kwargs["improved_data"]["heating_therms"] = 30.0
        kwargs["improved_data"]["heating_kwh"] = 10000.0
        kwargs["improved_data"]["cooling_kwh"] = 2100.0
        kwargs["improved_data"]["primary_heating_type"] = "Fuel-fired air distribution heater"
        kwargs["heating_fuel"] = "gas"
        kwargs["water_heater_tier"] = "HPWH Tier 1"
        kwargs["certified_earth_advantage"] = "Platinum"
        calculator = NEEAV2Calculator(**kwargs.copy())
        self.assertEqual(round(calculator.incentives.percent_improvement, 3), 0.203)
        self.assertEqual(round(calculator.incentives.total_incentive, 0), 560.0)
        self.assertEqual(round(calculator.incentives.builder_incentive, 0), 0.0)

        # All but hot water type
        kwargs["improved_data"]["heating_therms"] = 30.0
        kwargs["improved_data"]["heating_kwh"] = 10000.0
        kwargs["improved_data"]["cooling_kwh"] = 4200.0
        kwargs["heating_fuel"] = "electric"
        kwargs["water_heater_tier"] = "Gas Tankless EF \u2265 0.82"
        calculator = NEEAV2Calculator(**kwargs.copy())
        self.assertEqual(round(calculator.incentives.percent_improvement, 3), 0.107)
        self.assertEqual(round(calculator.incentives.total_incentive, 0), 0.0)
        self.assertEqual(round(calculator.incentives.builder_incentive, 0), 0.0)

        # All but heating fuel
        kwargs["improved_data"]["heating_therms"] = 30.0
        kwargs["improved_data"]["heating_kwh"] = 10000.0
        kwargs["improved_data"]["cooling_kwh"] = 3000.0
        kwargs["heating_fuel"] = "gas"
        kwargs["water_heater_tier"] = "HPWH Tier 1"
        calculator = NEEAV2Calculator(**kwargs.copy())
        self.assertEqual(round(calculator.incentives.percent_improvement, 3), 0.138)
        self.assertEqual(round(calculator.incentives.total_incentive, 0), 282.0)
        self.assertEqual(round(calculator.incentives.builder_incentive, 0), 0.0)

        # Valid Path
        kwargs["improved_data"]["heating_therms"] = 30.0
        kwargs["improved_data"]["heating_kwh"] = 10000.0
        kwargs["improved_data"]["cooling_kwh"] = 2100.0
        kwargs["heating_fuel"] = "electric"
        kwargs["water_heater_tier"] = "electric resistance"
        calculator = NEEAV2Calculator(**kwargs.copy())

        self.assertEqual(round(calculator.incentives.percent_improvement, 3), 0.115)
        self.assertEqual(round(calculator.incentives.total_incentive, 0), 240.0)
        self.assertEqual(round(calculator.incentives.total_kwh_savings, 0), 1441.0)
        self.assertEqual(round(calculator.incentives.builder_incentive, 0), 1009.0)
        self.assertEqual(round(calculator.incentives.total_kwh_savings * 0.7), 1009.0)

    def test_peninsula_power_incentives(self):
        """Test out"""
        kwargs = self.base_kwargs().copy()
        kwargs["electric_utility"] = "utility-peninsula-power-light"

        # All but heating type (Fuel)
        kwargs["improved_data"]["heating_therms"] = 30.0
        kwargs["improved_data"]["heating_kwh"] = 10000.0
        kwargs["improved_data"]["cooling_kwh"] = 2100.0
        kwargs["heating_fuel"] = "gas"
        kwargs["electric_meter_number"] = "FOO BAR"
        calculator = NEEAV2Calculator(**kwargs.copy())

        self.assertEqual(calculator.incentives.heating_fuel, kwargs["heating_fuel"])
        self.assertEqual(
            calculator.incentives.electric_meter_number, kwargs["electric_meter_number"]
        )

        self.assertEqual(
            calculator.incentives.__class__.__name__, "PeninsulaPowerIncentivesCalculator"
        )
        self.assertIn("Peninsula Power & Light", calculator.utility_requirements["title"])
        self.assertIn("Peninsula Power & Light", "\n".join(calculator.incentives.utility_report()))

        self.assertIn("Peninsula Power & Light", calculator.utility_requirements["title"])
        self.assertIn("Peninsula Power & Light", "\n".join(calculator.incentives.utility_report()))
        self.assertEqual(round(calculator.incentives.percent_improvement, 3), 0.115)
        self.assertEqual(round(calculator.incentives.total_incentive, 0), 240.0)
        self.assertEqual(round(calculator.incentives.builder_incentive, 0), 0.0)

        # All but meter_number
        kwargs["improved_data"]["heating_therms"] = 30.0
        kwargs["improved_data"]["heating_kwh"] = 10000.0
        kwargs["improved_data"]["cooling_kwh"] = 2100.0
        kwargs["heating_fuel"] = "electric"
        kwargs.pop("electric_meter_number")
        calculator = NEEAV2Calculator(**kwargs.copy())
        self.assertEqual(round(calculator.incentives.percent_improvement, 3), 0.115)
        self.assertFalse(calculator.incentives.has_incentive)
        self.assertEqual(round(calculator.incentives.total_incentive, 0), 240.0)
        self.assertEqual(round(calculator.incentives.builder_incentive, 0), 0.0)

        # Valid Path
        kwargs["improved_data"]["heating_therms"] = 30.0
        kwargs["improved_data"]["heating_kwh"] = 10000.0
        kwargs["improved_data"]["cooling_kwh"] = 2100.0
        kwargs["electric_meter_number"] = "FOO BAR"
        calculator = NEEAV2Calculator(**kwargs.copy())

        self.assertEqual(round(calculator.incentives.percent_improvement, 3), 0.115)
        self.assertTrue(calculator.incentives.has_incentive)
        self.assertEqual(round(calculator.incentives.total_incentive, 0), 240.0)
        self.assertEqual(round(calculator.incentives.total_kwh_savings, 0), 1441.0)
        self.assertEqual(round(calculator.incentives.builder_incentive, 0), 240.0)
