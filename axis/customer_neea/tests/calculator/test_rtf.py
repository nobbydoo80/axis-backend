"""rtf.py - Axis"""

__author__ = "Steven K"
__date__ = "6/26/21 10:04"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from axis.core.tests.client import AxisClient
from axis.core.tests.testcases import AxisTestCase
from axis.customer_neea.models import StandardProtocolCalculator
from axis.customer_neea.rtf_calculator.base import RTFInputException
from axis.customer_neea.rtf_calculator.calculator import RTFCalculator, NEEAV2Calculator
from axis.customer_neea.tests.mixins import CustomerNEEAModelTestMixin

log = logging.getLogger(__name__)


class RTFCalculatorBaseTests(CustomerNEEAModelTestMixin, AxisTestCase):
    """Test out community app"""

    client_class = AxisClient

    def base_kwargs(self):
        return {
            "us_state": "Wa",
            "heating_fuel": "gaS",
            "heating_system_config": "zonal",
            "home_size": "small",
            "heating_zone": "hz1",
            "code_data": {"heating_therms": 30.0, "heating_kwh": 10000.0, "cooling_kwh": 2100.0},
            "improved_data": {"heating_therms": 20.0, "heating_kwh": 8000.0, "cooling_kwh": 2000.0},
        }

    def test_input_us_state(self):
        calc = RTFCalculator(**self.base_kwargs().copy())
        self.assertEqual(calc.us_state, "WA")
        for state in ["id", "OR", "wA", "mt"]:
            kw = self.base_kwargs().copy()
            kw.update({"us_state": state})
            calc = RTFCalculator(**kw)
            self.assertEqual(calc.us_state, state.upper())

        kw = self.base_kwargs().copy()
        kw.update({"us_state": "WI"})
        self.assertRaises(RTFInputException, RTFCalculator, **kw)

        del kw["us_state"]
        self.assertRaises(RTFInputException, RTFCalculator, **kw)

    def test_input_heating_fuel(self):
        calc = RTFCalculator(**self.base_kwargs().copy())
        self.assertEqual(calc.heating_fuel, "gas")
        for obj in ["Electric", "Gas"]:
            kw = self.base_kwargs().copy()
            kw.update({"heating_fuel": obj})
            calc = RTFCalculator(**kw)
            self.assertEqual(calc.heating_fuel, obj.lower())

        kw = self.base_kwargs().copy()
        kw.update({"heating_fuel": "Propane"})
        self.assertRaises(RTFInputException, RTFCalculator, **kw)

        del kw["heating_fuel"]
        self.assertRaises(RTFInputException, RTFCalculator, **kw)

    def test_input_home_size(self):
        calc = RTFCalculator(**self.base_kwargs().copy())
        self.assertEqual(calc.home_size, "small")
        for obj in ["small", "Medium", "LARGE"]:
            kw = self.base_kwargs().copy()
            kw.update({"home_size": obj})
            calc = RTFCalculator(**kw)
            self.assertEqual(calc.home_size, obj.lower())

        kw = self.base_kwargs().copy()
        kw.update({"home_size": "all"})
        self.assertRaises(RTFInputException, RTFCalculator, **kw)

        del kw["home_size"]
        self.assertRaises(RTFInputException, RTFCalculator, **kw)

        for state in ["id", "OR", "mt"]:
            kw = self.base_kwargs().copy()
            kw.update({"us_state": state})
            calc = RTFCalculator(**kw)
            self.assertEqual(calc.home_size, "all")

    def test_input_heating_zone(self):
        calc = RTFCalculator(**self.base_kwargs().copy())
        self.assertEqual(calc.heating_zone, "hz1")
        for obj in ["hz1", "hZ2", "HZ3"]:
            kw = self.base_kwargs().copy()
            kw.update({"heating_zone": obj})
            calc = RTFCalculator(**kw)
            self.assertEqual(calc.heating_zone, obj.lower())

        kw = self.base_kwargs().copy()
        kw.update({"heating_zone": "ZZZ"})
        self.assertRaises(RTFInputException, RTFCalculator, **kw)

        del kw["heating_zone"]
        self.assertRaises(RTFInputException, RTFCalculator, **kw)

    def test_heating_cooling_savings(self):
        calc = RTFCalculator(**self.base_kwargs().copy())
        self.assertEqual(calc.heating_kwh_savings, 2000.0)
        self.assertEqual(calc.heating_therm_savings, 10.0)
        self.assertEqual(calc.cooling_kwh_savings, 100.0)
        self.assertEqual(calc.cooling_therm_savings, 0.0)

    def test_value_storages(self):
        kwargs = {
            "heating_fuel": "electric",
            "qty_shower_head_1p75": 0,
            "improved_data": {
                "cooling_kwh": 2000.0,
                "primary_heating_type": "heater",
                "primary_water_heating_type": "gas",
                "primary_cooling_type": "air conditioner",
                "primary_cooling_fuel": "electric",
                "heating_kwh": 8000.0,
                "heating_therms": 20.0,
            },
            "cfl_installed": 5,
            "clothes_dryer_tier": "tier3",
            "smart_thermostat_installed": True,
            "water_heater_tier": "electric resistance",
            "led_installed": 35,
            "estar_front_load_clothes_washer_installed": True,
            "electric_utility": "clark-pud",
            "code_data": {"cooling_kwh": 2100.0, "heating_kwh": 10000.0, "heating_therms": 30.0},
            "home_size": "small",
            "raise_issues": False,
            "gas_utility": "foo",
            "heating_zone": "hz2",
            "qty_shower_head_1p5": 3,
            "estar_std_refrigerators_installed": True,
            "heating_system_config": "central",
            "total_installed_lamps": 40,
            "estar_dishwasher_installed": True,
            "us_state": "WA",
        }

        calculator = NEEAV2Calculator(**kwargs.copy())

        from axis.home.models import EEPProgramHomeStatus, Home
        from axis.company.models import Company
        from axis.eep_program.models import EEPProgram

        clark, _ = Company.objects.get_or_create(
            slug=kwargs["electric_utility"], defaults={"name": "Clark"}
        )
        home_status, _ = EEPProgramHomeStatus.objects.get_or_create(
            company=Company.objects.first(),
            eep_program=EEPProgram.objects.first(),
            home=Home.objects.first(),
        )
        calculator.home_status = home_status
        sp, create = StandardProtocolCalculator.objects.update_or_create_from_calculator(calculator)

        self.assertEqual(calculator.heating_fuel, "electric")
        self.assertEqual(calculator.heating_fuel, sp.heating_fuel)

        self.assertEqual(calculator.heating_system_config, "central")
        self.assertEqual(calculator.heating_system_config, sp.heating_system_config)

        self.assertEqual(calculator.home_size, "small")
        self.assertEqual(calculator.home_size, sp.home_size)

        self.assertEqual(calculator.cfl_installed, 5)
        self.assertEqual(calculator.cfl_installed, sp.cfl_installed)

        self.assertEqual(calculator.led_installed, 35)
        self.assertEqual(calculator.led_installed, sp.led_installed)

        self.assertEqual(calculator.total_installed_lamps, 40)
        self.assertEqual(calculator.total_installed_lamps, sp.total_installed_lamps)

        self.assertEqual(calculator.smart_thermostat_installed, True)
        self.assertEqual(calculator.smart_thermostat_installed, sp.smart_thermostat_installed)

        self.assertEqual(calculator.qty_shower_head_1p5, 3)
        self.assertEqual(calculator.qty_shower_head_1p5, sp.qty_shower_head_1p5)

        self.assertEqual(calculator.qty_shower_head_1p75, 0)
        self.assertEqual(calculator.qty_shower_head_1p75, sp.qty_shower_head_1p75)

        self.assertEqual(calculator.estar_dishwasher_installed, True)
        self.assertEqual(calculator.estar_dishwasher_installed, sp.estar_dishwasher_installed)

        self.assertEqual(calculator.estar_std_refrigerators_installed, True)
        self.assertEqual(
            calculator.estar_std_refrigerators_installed, sp.estar_std_refrigerators_installed
        )

        self.assertEqual(calculator.estar_front_load_clothes_washer_installed, True)
        self.assertEqual(
            calculator.estar_front_load_clothes_washer_installed,
            sp.estar_front_load_clothes_washer_installed,
        )

        self.assertEqual(round(calculator.heating_kwh_savings, 0), 2000.0)
        self.assertEqual(round(calculator.heating_therm_savings, 0), 10.0)
        self.assertEqual(round(calculator.cooling_kwh_savings, 0), 100.0)
        self.assertEqual(round(calculator.cooling_therm_savings, 0), 0.0)
        self.assertEqual(round(calculator.smart_thermostat_kwh_savings, 0), 600.0)
        self.assertEqual(round(calculator.smart_thermostat_therm_savings, 0), 1.0)
        self.assertEqual(round(calculator.water_heater_kwh_savings, 0), 0.0)
        self.assertEqual(round(calculator.showerhead_kwh_savings, 0), 160.0)
        self.assertEqual(round(calculator.showerhead_therm_savings, 0), 0.0)
        self.assertEqual(round(calculator.lighting_kwh_savings, 0), 135.0)
        self.assertEqual(round(calculator.appliance_kwh_savings, 0), 562.0)
        self.assertEqual(round(calculator.total_kwh_savings, 0), 3557.0)
        self.assertEqual(round(calculator.total_therm_savings, 0), 11.0)
        self.assertEqual(round(calculator.total_mmbtu_savings, 0), 13.0)
        self.assertEqual(round(calculator.incentives.busbar_consumption, 0), 8543.0)
        self.assertEqual(round(calculator.incentives.busbar_savings, 0), 3557.0)
        self.assertEqual(calculator.incentives.pct_improvement_method, "alternate")
        self.assertEqual(
            calculator.incentives.incentive_paying_organization, kwargs["electric_utility"]
        )
        self.assertEqual(round(calculator.incentives.default_percent_improvement, 3), 0.184)
        self.assertEqual(round(calculator.incentives.percent_improvement, 3), 0.299)
        self.assertEqual(round(calculator.code_data_total_consumption_mmbtu, 3), 44.285)
        self.assertEqual(round(calculator.improved_data_total_consumption_mmbtu, 3), 36.12)
        self.assertEqual(round(calculator.improved_total_consumption_mmbtu_with_savings, 3), 31.028)

        self.assertEqual(calculator.heating_kwh_savings, sp.heating_kwh_savings)
        self.assertEqual(calculator.heating_therm_savings, sp.heating_therm_savings)
        self.assertEqual(calculator.cooling_kwh_savings, sp.cooling_kwh_savings)
        self.assertEqual(calculator.cooling_therm_savings, sp.cooling_therm_savings)
        self.assertEqual(calculator.smart_thermostat_kwh_savings, sp.smart_thermostat_kwh_savings)
        self.assertEqual(
            calculator.smart_thermostat_therm_savings, sp.smart_thermostat_therm_savings
        )
        self.assertEqual(calculator.water_heater_kwh_savings, sp.water_heater_kwh_savings)
        self.assertEqual(calculator.showerhead_kwh_savings, sp.showerhead_kwh_savings)
        self.assertEqual(calculator.showerhead_therm_savings, sp.showerhead_therm_savings)
        self.assertEqual(calculator.lighting_kwh_savings, sp.lighting_kwh_savings)
        self.assertEqual(calculator.appliance_kwh_savings, sp.appliance_kwh_savings)
        self.assertEqual(calculator.total_kwh_savings, sp.total_kwh_savings)
        self.assertEqual(calculator.total_therm_savings, sp.total_therm_savings)
        self.assertEqual(calculator.total_mmbtu_savings, sp.total_mmbtu_savings)
        self.assertEqual(calculator.incentives.busbar_consumption, sp.busbar_consumption)
        self.assertEqual(calculator.incentives.busbar_savings, sp.busbar_savings)
        self.assertEqual(calculator.incentives.default_percent_improvement, sp.percent_improvement)
        self.assertEqual(calculator.incentives.pct_improvement_method, sp.pct_improvement_method)
        self.assertEqual(sp.incentive_paying_organization, clark)
        self.assertEqual(
            calculator.code_data_total_consumption_mmbtu, sp.code_total_consumption_mmbtu
        )
        self.assertEqual(
            calculator.improved_data_total_consumption_mmbtu, sp.improved_total_consumption_mmbtu
        )
        self.assertEqual(
            calculator.improved_total_consumption_mmbtu_with_savings,
            sp.improved_total_consumption_mmbtu_with_savings,
        )

        self.assertEqual(round(calculator.incentives.total_incentive, 2), 1136.75)
        self.assertEqual(round(calculator.incentives.bpa_hvac_kwh_savings, 0), 275.0)
        self.assertEqual(round(calculator.incentives.hvac_kwh_incentive, 2), 74.25)
        self.assertEqual(round(calculator.incentives.bpa_lighting_kwh_savings, 0), 135.0)
        self.assertEqual(round(calculator.incentives.lighting_kwh_incentive, 2), 13.46)
        self.assertEqual(round(calculator.incentives.bpa_water_heater_kwh_savings, 0), 0.0)
        self.assertEqual(round(calculator.incentives.water_heater_kwh_incentive, 2), 0.0)
        self.assertEqual(round(calculator.incentives.bpa_appliance_kwh_savings, 0), 562.0)
        self.assertEqual(round(calculator.incentives.appliance_kwh_incentive, 2), 151.75)
        self.assertEqual(round(calculator.incentives.bpa_windows_shell_kwh_savings, 0), 1825.0)
        self.assertEqual(round(calculator.incentives.windows_shell_kwh_incentive, 2), 821.25)
        self.assertEqual(round(calculator.incentives.bpa_showerhead_kwh_savings, 0), 160.0)
        self.assertEqual(round(calculator.incentives.showerhead_kwh_incentive, 2), 16.04)
        self.assertEqual(round(calculator.incentives.bpa_smart_thermostat_kwh_savings, 0), 600.0)
        self.assertEqual(round(calculator.incentives.smart_thermostat_kwh_incentive, 2), 60.0)

        self.assertEqual(calculator.incentives.total_incentive, sp.total_incentive)
        self.assertEqual(calculator.incentives.bpa_hvac_kwh_savings, sp.bpa_hvac_kwh_savings)
        self.assertEqual(calculator.incentives.hvac_kwh_incentive, sp.hvac_kwh_incentive)
        self.assertEqual(
            calculator.incentives.bpa_lighting_kwh_savings, sp.bpa_lighting_kwh_savings
        )
        self.assertEqual(calculator.incentives.lighting_kwh_incentive, sp.lighting_kwh_incentive)
        self.assertEqual(
            calculator.incentives.bpa_water_heater_kwh_savings, sp.bpa_water_heater_kwh_savings
        )
        self.assertEqual(
            calculator.incentives.water_heater_kwh_incentive, sp.water_heater_kwh_incentive
        )
        self.assertEqual(
            calculator.incentives.bpa_appliance_kwh_savings, sp.bpa_appliance_kwh_savings
        )
        self.assertEqual(calculator.incentives.appliance_kwh_incentive, sp.appliance_kwh_incentive)
        self.assertEqual(
            calculator.incentives.bpa_windows_shell_kwh_savings, sp.bpa_windows_shell_kwh_savings
        )
        self.assertEqual(
            calculator.incentives.windows_shell_kwh_incentive, sp.windows_shell_kwh_incentive
        )
        self.assertEqual(
            calculator.incentives.bpa_showerhead_kwh_savings, sp.bpa_showerhead_kwh_savings
        )
        self.assertEqual(
            calculator.incentives.showerhead_kwh_incentive, sp.showerhead_kwh_incentive
        )
        self.assertEqual(
            calculator.incentives.bpa_smart_thermostat_kwh_savings,
            sp.bpa_smart_thermostat_kwh_savings,
        )
        self.assertEqual(
            calculator.incentives.smart_thermostat_kwh_incentive, sp.smart_thermostat_kwh_incentive
        )
