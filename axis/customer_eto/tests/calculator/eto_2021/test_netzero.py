"""net_netzero.py - Axis"""

__author__ = "Steven K"
__date__ = "9/17/21 11:47"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
from django.test import TestCase

from axis.customer_eto.calculator.eps_2021.base import HomePath
from axis.customer_eto.calculator.eps_2021.constants import Constants
from axis.customer_eto.calculator.eps_2021.net_zero import NetZero2020
from axis.customer_eto.enumerations import (
    PNWUSStates,
    ElectricUtility,
    PrimaryHeatingEquipment2020,
    SmartThermostatBrands2020,
    GridHarmonization2020,
    AdditionalIncentives2020,
    SolarElements2020,
)

log = logging.getLogger(__name__)


class NetZeroCalculatorTests(TestCase):
    @property
    def input_options(self):
        return {
            "total_kwh": 500.0,
            "total_therms": 25.2,
            "cooling_kwh": 25.1,
            "pv_kwh": 500.01,
            "percent_improvement": 0.2623,
            "percent_improvement_therms": 0.2123,
            "constants": Constants(ElectricUtility.PACIFIC_POWER, PNWUSStates.OR),
            "electric_utility": ElectricUtility.PACIFIC_POWER,
            "primary_heating_class": PrimaryHeatingEquipment2020.GAS_FURNACE,
            "thermostat_brand": SmartThermostatBrands2020.NEST_LEARNING,
            "grid_harmonization_elements": GridHarmonization2020.WIRING,
            "eps_additional_incentives": AdditionalIncentives2020.AFFORDABLE_HOUSING,
            "solar_elements": SolarElements2020.SOLAR_PV,
            "us_state": PNWUSStates.OR,
        }

    def test_qualifies_for_net_zero(self):
        input_data = self.input_options.copy()
        net_zero = NetZero2020(**input_data)
        self.assertTrue(net_zero.qualifies_for_net_zero)
        self.assertEqual(net_zero.net_zero_incentive, 750.00)

        with self.subTest("Bad State"):
            input_data = self.input_options.copy()
            input_data.update({"us_state": PNWUSStates.WA})
            net_zero = NetZero2020(**input_data)
            self.assertFalse(net_zero.qualifies_for_net_zero)
            self.assertFalse(net_zero._net_zero_elements["Qualifying State"])
            self.assertTrue(net_zero._net_zero_elements["Valid Utility"])
            self.assertTrue(net_zero._net_zero_elements["Overall % Improvement"])
            self.assertTrue(net_zero._net_zero_elements["Acceptable Therms"])
            self.assertTrue(net_zero._net_zero_elements["PV Generation"])
            self.assertTrue(net_zero._net_zero_elements["Valid Solar Elements"])
            self.assertIn("Qualifying State", net_zero.input_report)
            self.assertEqual(net_zero.net_zero_incentive, 0.00)

        with self.subTest("Bad Utility"):
            input_data = self.input_options.copy()
            input_data.update({"electric_utility": ElectricUtility.NONE})
            net_zero = NetZero2020(**input_data)
            self.assertFalse(net_zero.qualifies_for_net_zero)
            self.assertTrue(net_zero._net_zero_elements["Qualifying State"])
            self.assertFalse(net_zero._net_zero_elements["Valid Utility"])
            self.assertTrue(net_zero._net_zero_elements["Overall % Improvement"])
            self.assertTrue(net_zero._net_zero_elements["Acceptable Therms"])
            self.assertTrue(net_zero._net_zero_elements["PV Generation"])
            self.assertTrue(net_zero._net_zero_elements["Valid Solar Elements"])
            self.assertIn("Valid Utility", net_zero.input_report)
            self.assertEqual(net_zero.net_zero_incentive, 0.00)

        with self.subTest("Overall % Improvement"):
            input_data = self.input_options.copy()
            input_data.update({"percent_improvement": 0.1999})
            net_zero = NetZero2020(**input_data)
            self.assertFalse(net_zero.qualifies_for_net_zero)
            self.assertTrue(net_zero._net_zero_elements["Qualifying State"])
            self.assertTrue(net_zero._net_zero_elements["Valid Utility"])
            self.assertFalse(net_zero._net_zero_elements["Overall % Improvement"])
            self.assertTrue(net_zero._net_zero_elements["Acceptable Therms"])
            self.assertTrue(net_zero._net_zero_elements["PV Generation"])
            self.assertTrue(net_zero._net_zero_elements["Valid Solar Elements"])
            self.assertIn("Overall % Improvement", net_zero.input_report)
            self.assertEqual(net_zero.net_zero_incentive, 0.00)

        with self.subTest("Acceptable Therms"):
            input_data = self.input_options.copy()
            input_data.update({"total_therms": 0.01, "percent_improvement_therms": 0.1999})
            net_zero = NetZero2020(**input_data)
            self.assertFalse(net_zero.qualifies_for_net_zero)
            self.assertTrue(net_zero._net_zero_elements["Qualifying State"])
            self.assertTrue(net_zero._net_zero_elements["Valid Utility"])
            self.assertTrue(net_zero._net_zero_elements["Overall % Improvement"])
            self.assertFalse(net_zero._net_zero_elements["Acceptable Therms"])
            self.assertTrue(net_zero._net_zero_elements["PV Generation"])
            self.assertTrue(net_zero._net_zero_elements["Valid Solar Elements"])
            self.assertIn("Acceptable Therms", net_zero.input_report)
            self.assertEqual(net_zero.net_zero_incentive, 0.00)

        with self.subTest("PV Generation"):
            input_data = self.input_options.copy()
            input_data.update({"pv_kwh": 0.01})
            net_zero = NetZero2020(**input_data)
            self.assertFalse(net_zero.qualifies_for_net_zero)
            self.assertTrue(net_zero._net_zero_elements["Qualifying State"])
            self.assertTrue(net_zero._net_zero_elements["Valid Utility"])
            self.assertTrue(net_zero._net_zero_elements["Overall % Improvement"])
            self.assertTrue(net_zero._net_zero_elements["Acceptable Therms"])
            self.assertFalse(net_zero._net_zero_elements["PV Generation"])
            self.assertTrue(net_zero._net_zero_elements["Valid Solar Elements"])
            self.assertIn("PV Generation", net_zero.input_report)
            self.assertEqual(net_zero.net_zero_incentive, 0.00)

        with self.subTest("Valid Solar Elements"):
            input_data = self.input_options.copy()
            input_data.update({"solar_elements": SolarElements2020.SOLAR_READY})
            net_zero = NetZero2020(**input_data)
            self.assertFalse(net_zero.qualifies_for_net_zero)
            self.assertTrue(net_zero._net_zero_elements["Qualifying State"])
            self.assertTrue(net_zero._net_zero_elements["Valid Utility"])
            self.assertTrue(net_zero._net_zero_elements["Overall % Improvement"])
            self.assertTrue(net_zero._net_zero_elements["Acceptable Therms"])
            self.assertTrue(net_zero._net_zero_elements["PV Generation"])
            self.assertFalse(net_zero._net_zero_elements["Valid Solar Elements"])
            self.assertIn("Valid Solar Elements", net_zero.input_report)
            self.assertEqual(net_zero.net_zero_incentive, 0.00)

    def test_smart_thermostat_requirement_met(self):
        for thermostat in SmartThermostatBrands2020:
            with self.subTest(f"{thermostat.value}"):
                expected = False
                if "ecobee" in thermostat.value.lower() or "nest" in thermostat.value.lower():
                    expected = True
                input_data = self.input_options.copy()
                input_data.update({"thermostat_brand": thermostat})
                net_zero = NetZero2020(**input_data)
                self.assertEqual(net_zero.smart_thermostat_requirement_met, expected)

    def test_solar_exempt(self):
        for additional_incentive in AdditionalIncentives2020:
            with self.subTest(f"{additional_incentive.value}"):
                expected = False
                if "upload solar exemption" in additional_incentive.value.lower():
                    expected = True
                input_data = self.input_options.copy()
                input_data.update({"eps_additional_incentives": additional_incentive})
                net_zero = NetZero2020(**input_data)
                self.assertEqual(net_zero.solar_exempt, expected)

    def test_mini_split(self):
        for heating_class in PrimaryHeatingEquipment2020:
            with self.subTest(f"{heating_class.value}"):
                expected = False
                if "mini" in heating_class.value.lower() and "split" in heating_class.value.lower():
                    expected = True
                input_data = self.input_options.copy()
                input_data.update({"primary_heating_class": heating_class})
                net_zero = NetZero2020(**input_data)
                self.assertEqual(net_zero.mini_split, expected)

    def test_qualifies_for_esh_base(self):
        input_data = self.input_options.copy()
        net_zero = NetZero2020(**input_data)
        self.assertEqual(net_zero.qualifies_for_esh_base, True)
        self.assertEqual(net_zero.energy_smart_incentive, 350.00)

        with self.subTest("Bad State"):
            input_data = self.input_options.copy()
            input_data.update({"us_state": PNWUSStates.WA})
            net_zero = NetZero2020(**input_data)
            self.assertFalse(net_zero.qualifies_for_esh_base)
            self.assertFalse(net_zero._esh_base_elements["Qualifying State"])
            self.assertTrue(net_zero._esh_base_elements["Valid Utility"])
            self.assertTrue(net_zero._esh_base_elements["Valid Thermostat w/cooling"])
            self.assertFalse(net_zero._esh_base_elements["Mini-Split"])
            self.assertIn("Qualifying State", net_zero.input_report)
            self.assertEqual(net_zero.energy_smart_incentive, 0.00)

        with self.subTest("Bad Utility"):
            input_data = self.input_options.copy()
            input_data.update({"electric_utility": ElectricUtility.NONE})
            net_zero = NetZero2020(**input_data)
            self.assertFalse(net_zero.qualifies_for_esh_base)
            self.assertTrue(net_zero._esh_base_elements["Qualifying State"])
            self.assertFalse(net_zero._esh_base_elements["Valid Utility"])
            self.assertTrue(net_zero._esh_base_elements["Valid Thermostat w/cooling"])
            self.assertFalse(net_zero._esh_base_elements["Mini-Split"])
            self.assertIn("Valid Utility", net_zero.input_report)
            self.assertEqual(net_zero.energy_smart_incentive, 0.00)

        with self.subTest("Valid Thermostat w/cooling bad"):
            input_data = self.input_options.copy()
            input_data.update(
                {"cooling_kwh": 1.0, "thermostat_brand": SmartThermostatBrands2020.BRYANT}
            )
            net_zero = NetZero2020(**input_data)
            self.assertFalse(net_zero.qualifies_for_esh_base)
            self.assertTrue(net_zero._esh_base_elements["Qualifying State"])
            self.assertTrue(net_zero._esh_base_elements["Valid Utility"])
            self.assertFalse(net_zero._esh_base_elements["Valid Thermostat w/cooling"])
            self.assertFalse(net_zero._esh_base_elements["Mini-Split"])
            self.assertIn("Valid Thermostat w/cooling", net_zero.input_report)
            self.assertEqual(net_zero.energy_smart_incentive, 0.00)

            input_data = self.input_options.copy()
            input_data.update(
                {"cooling_kwh": 0.0, "thermostat_brand": SmartThermostatBrands2020.ECOBEE4}
            )
            net_zero = NetZero2020(**input_data)
            self.assertFalse(net_zero.qualifies_for_esh_base)
            self.assertTrue(net_zero._esh_base_elements["Qualifying State"])
            self.assertTrue(net_zero._esh_base_elements["Valid Utility"])
            self.assertFalse(net_zero._esh_base_elements["Valid Thermostat w/cooling"])
            self.assertFalse(net_zero._esh_base_elements["Mini-Split"])
            self.assertIn("Valid Thermostat w/cooling", net_zero.input_report)
            self.assertEqual(net_zero.energy_smart_incentive, 0.00)

        with self.subTest("Valid Mini-split"):
            input_data = self.input_options.copy()
            input_data.update(
                {"cooling_kwh": 1.0, "thermostat_brand": SmartThermostatBrands2020.BRYANT}
            )
            net_zero = NetZero2020(**input_data)
            self.assertFalse(net_zero.qualifies_for_esh_base)
            self.assertTrue(net_zero._esh_base_elements["Qualifying State"])
            self.assertTrue(net_zero._esh_base_elements["Valid Utility"])
            self.assertFalse(net_zero._esh_base_elements["Valid Thermostat w/cooling"])
            self.assertFalse(net_zero._esh_base_elements["Mini-Split"])
            self.assertIn("Mini-Split", net_zero.input_report)
            self.assertEqual(net_zero.energy_smart_incentive, 0.00)

            input_data = self.input_options.copy()
            input_data.update(
                {
                    "cooling_kwh": 1.0,
                    "thermostat_brand": SmartThermostatBrands2020.BRYANT,
                    "primary_heating_class": PrimaryHeatingEquipment2020.MINI_SPLIT_MIXED,
                }
            )
            net_zero = NetZero2020(**input_data)
            self.assertTrue(net_zero.qualifies_for_esh_base)
            self.assertTrue(net_zero._esh_base_elements["Qualifying State"])
            self.assertTrue(net_zero._esh_base_elements["Valid Utility"])
            self.assertFalse(net_zero._esh_base_elements["Valid Thermostat w/cooling"])
            self.assertTrue(net_zero._esh_base_elements["Mini-Split"])
            self.assertNotIn("Mini-Split", net_zero.input_report)

    def test_energy_smart_incentive(self):
        with self.subTest("Base Only"):
            input_data = self.input_options.copy()
            input_data.update({"grid_harmonization_elements": GridHarmonization2020.BASE})
            net_zero = NetZero2020(**input_data)
            self.assertEqual(net_zero.qualifies_for_esh_base, True)
            self.assertEqual(net_zero.energy_smart_incentive, 200.00)

        with self.subTest("Solar Exempt"):
            input_data = self.input_options.copy()
            input_data.update(
                {
                    "grid_harmonization_elements": GridHarmonization2020.STORAGE,
                    "eps_additional_incentives": AdditionalIncentives2020.ENERGY_SMART,
                }
            )
            net_zero = NetZero2020(**input_data)
            self.assertEqual(net_zero.qualifies_for_esh_base, True)
            self.assertTrue(net_zero.solar_exempt)
            self.assertEqual(net_zero.energy_smart_incentive, 200.00)

            input_data = self.input_options.copy()
            input_data.update(
                {
                    "grid_harmonization_elements": GridHarmonization2020.STORAGE,
                    "eps_additional_incentives": AdditionalIncentives2020.NO,
                }
            )
            net_zero = NetZero2020(**input_data)
            self.assertEqual(net_zero.qualifies_for_esh_base, True)
            self.assertFalse(net_zero.solar_exempt)
            self.assertEqual(net_zero.energy_smart_incentive, 350.00)

        with self.subTest("Wiring"):
            input_data = self.input_options.copy()
            input_data.update({"grid_harmonization_elements": GridHarmonization2020.WIRING})
            net_zero = NetZero2020(**input_data)
            self.assertEqual(net_zero.qualifies_for_esh_base, True)
            self.assertFalse(net_zero.solar_exempt)
            self.assertEqual(net_zero.energy_smart_incentive, 350.00)

        with self.subTest("Full Enchilada"):
            input_data = self.input_options.copy()
            input_data.update(
                {
                    "grid_harmonization_elements": GridHarmonization2020.ALL,
                    "eps_additional_incentives": AdditionalIncentives2020.NO,
                }
            )
            net_zero = NetZero2020(**input_data)
            self.assertEqual(net_zero.qualifies_for_esh_base, True)
            self.assertFalse(net_zero.solar_exempt)
            self.assertEqual(net_zero.energy_smart_incentive, 500.00)

    def test_total_incentive(self):
        input_data = self.input_options.copy()
        net_zero = NetZero2020(**input_data)
        self.assertRaises(TypeError, getattr, net_zero, "total_incentive")

        net_zero.whole_home_incentive = 5000.0
        report = net_zero.incentive_report
        self.assertIn("5,000.00", report)
        self.assertEqual(net_zero.net_zero_incentive, 750.00)
        self.assertIn("$ 750.00", report)
        self.assertEqual(net_zero.energy_smart_incentive, 350.00)
        self.assertIn("$ 350.00", report)

        self.assertEqual(net_zero.total_incentive, 6100.00)
        self.assertIn("$ 6,100.00", report)

    def test_mad_max(self):
        input_data = self.input_options.copy()
        net_zero = NetZero2020(**input_data)

        self.assertEqual(net_zero.percent_improvement, input_data["percent_improvement"])

        with self.subTest("Home Path 1"):
            input_data["percent_improvement"] = 0.10
            net_zero = NetZero2020(**input_data)
            net_zero.home_path = HomePath.PATH_1
            self.assertEqual(net_zero.home_max_incentive, 1586.0)
            self.assertIn("10-19.9%", net_zero.mad_max_report)

        with self.subTest("Home Path 2"):
            input_data["percent_improvement"] = 0.20
            net_zero = NetZero2020(**input_data)
            net_zero.home_path = HomePath.PATH_2
            self.assertEqual(net_zero.home_max_incentive, 2917.0)
            self.assertIn("20-29.9", net_zero.mad_max_report)

        with self.subTest("Home Path 3"):
            input_data["percent_improvement"] = 0.30
            net_zero = NetZero2020(**input_data)
            net_zero.home_path = HomePath.PATH_3
            self.assertEqual(net_zero.home_max_incentive, 3509.0)
            self.assertIn("30-39.9%", net_zero.mad_max_report)

        with self.subTest("Home Path 4"):
            input_data["percent_improvement"] = 0.40
            net_zero = NetZero2020(**input_data)
            net_zero.home_path = HomePath.PATH_4
            self.assertEqual(net_zero.home_max_incentive, 5811.0)
            self.assertIn(">=40", net_zero.mad_max_report)

    def test_incentive_allocations_real_data(self):
        input_data = self.input_options.copy()
        input_data["percent_improvement"] = 0.3076923076923
        input_data["home_path"] = HomePath.PATH_3
        input_data["whole_home_incentive"] = 3264.5449704
        net_zero = NetZero2020(**input_data)

        self.assertEqual(round(net_zero.total_nz_and_energy_smart_incentive), 1100.0)
        self.assertEqual(round(net_zero.eps_allocation, 2), 421.53)
        self.assertEqual(round(net_zero.solar_allocation, 2), 678.47)
        self.assertIn("421.53", net_zero.incentive_allocation_report)
        self.assertIn("678.47", net_zero.incentive_allocation_report)

        self.assertEqual(round(net_zero.net_zero_eps_builder_allocation.incentive, 2), 287.41)
        self.assertIn("287.41", net_zero.net_zero_allocation_report)
        self.assertEqual(
            round(net_zero.net_zero_energy_smart_homes_builder_eps_allocation.incentive, 2), 134.12
        )
        self.assertIn("134.12", net_zero.net_zero_allocation_report)
        self.assertEqual(round(net_zero.net_zero_solar_builder_allocation.incentive, 2), 462.59)
        self.assertIn("462.59", net_zero.net_zero_allocation_report)
        self.assertEqual(
            round(net_zero.net_zero_energy_smart_homes_builder_solar_allocation.incentive, 2),
            215.88,
        )
        self.assertIn("215.88", net_zero.net_zero_allocation_report)

    def test_incentive_partial_allocations_real_data(self):
        input_data = self.input_options.copy()
        input_data["percent_improvement"] = 0.1089144500359
        input_data["home_path"] = HomePath.PATH_1
        input_data["whole_home_incentive"] = 1150.5181893
        net_zero = NetZero2020(**input_data)

        self.assertEqual(round(net_zero.total_nz_and_energy_smart_incentive), 350.0)
        self.assertEqual(round(net_zero.eps_allocation, 2), 350.0)
        self.assertEqual(round(net_zero.solar_allocation, 2), 0.0)
        self.assertIn("350.00", net_zero.incentive_allocation_report)
        self.assertIn("0.00", net_zero.incentive_allocation_report)

        self.assertEqual(round(net_zero.net_zero_eps_builder_allocation.incentive, 2), 0.00)
        self.assertIn("0.00", net_zero.net_zero_allocation_report)
        self.assertEqual(
            round(net_zero.net_zero_energy_smart_homes_builder_eps_allocation.incentive, 2), 350.0
        )
        self.assertIn("350.00", net_zero.net_zero_allocation_report)
        self.assertEqual(round(net_zero.net_zero_solar_builder_allocation.incentive, 2), 0.00)
        self.assertIn("0.00", net_zero.net_zero_allocation_report)
        self.assertEqual(
            round(net_zero.net_zero_energy_smart_homes_builder_solar_allocation.incentive, 2),
            0.00,
        )
        self.assertIn("0.00", net_zero.net_zero_allocation_report)

    def test_incentive_partial_allocations_two_real_data(self):
        input_data = self.input_options.copy()
        input_data["percent_improvement"] = 0.2526959022286
        input_data["grid_harmonization_elements"] = GridHarmonization2020.NONE
        input_data["home_path"] = HomePath.PATH_2
        input_data["whole_home_incentive"] = 2392.1835734
        net_zero = NetZero2020(**input_data)

        self.assertEqual(round(net_zero.total_nz_and_energy_smart_incentive), 750.0)
        self.assertEqual(round(net_zero.eps_allocation, 2), 750.0)
        self.assertEqual(round(net_zero.solar_allocation, 2), 0.0)
        self.assertIn("750.00", net_zero.incentive_allocation_report)
        self.assertIn("0.00", net_zero.incentive_allocation_report)

        self.assertEqual(round(net_zero.net_zero_eps_builder_allocation.incentive, 2), 750.00)
        self.assertIn("750.00", net_zero.net_zero_allocation_report)
        self.assertEqual(
            round(net_zero.net_zero_energy_smart_homes_builder_eps_allocation.incentive, 2), 0.0
        )
        self.assertIn("0.00", net_zero.net_zero_allocation_report)
        self.assertEqual(round(net_zero.net_zero_solar_builder_allocation.incentive, 2), 0.00)
        self.assertIn("0.00", net_zero.net_zero_allocation_report)
        self.assertEqual(
            round(net_zero.net_zero_energy_smart_homes_builder_solar_allocation.incentive, 2),
            0.00,
        )
        self.assertIn("0.00", net_zero.net_zero_allocation_report)
