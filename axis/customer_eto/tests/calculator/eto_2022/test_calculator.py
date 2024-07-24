"""test_calculator.py - Axis"""

__author__ = "Steven K"
__date__ = "3/2/22 14:08"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
from decimal import Decimal

from django.test import TestCase

from axis.customer_eto.calculator.eps_2022.calculator import EPS2022Calculator
from axis.customer_eto.eep_programs.eto_2022 import (
    AdditionalElements2022,
    SmartThermostatBrands2022,
    CobidRegistered,
    SolarElements2022,
    CobidQualification,
)
from axis.customer_eto.eep_programs.fire_rebuild_2021 import FireResilienceBonus
from axis.customer_eto.enumerations import (
    ClimateLocation,
    HeatType,
    ElectricUtility,
    GasUtility,
    Fireplace2020,
    PNWUSStates,
    PrimaryHeatingEquipment2020,
    QualifyingThermostat,
)

log = logging.getLogger(__name__)


class EPS2022CalculatorTests(TestCase):
    @property
    def input_options(self):
        return {
            "us_state": PNWUSStates.OR,
            "climate_location": ClimateLocation.EUGENE,
            "primary_heating_class": PrimaryHeatingEquipment2020.GAS_FURNACE,
            "conditioned_area": 2500.00,
            "electric_utility": ElectricUtility.PACIFIC_POWER,
            "gas_utility": GasUtility.NW_NATURAL,
            "code_heating_therms": 23.3,
            "code_heating_kwh": 1501.2,
            "code_cooling_kwh": 2503.6,
            "code_hot_water_therms": 25.2,
            "code_hot_water_kwh": 1025.2,
            "code_lights_and_appliance_therms": 5.2,
            "code_lights_and_appliance_kwh": 1975.2,
            "improved_heating_therms": 18.1,
            "improved_heating_kwh": 1223.3,
            "improved_cooling_kwh": 2356.4,
            "improved_hot_water_therms": 18.799999999,
            "improved_hot_water_kwh": 967.73,
            "improved_lights_and_appliance_therms": 4.8,
            "improved_lights_and_appliance_kwh": 1387.43,
            "has_heat_pump_water_heater": False,
            "improved_pv_kwh": 5,
            "thermostat_brand": SmartThermostatBrands2022.BRYANT,
            "fireplace": Fireplace2020.FE_50_59,
            "electric_elements": AdditionalElements2022.NO,
            "solar_elements": None,
            "cobid_registered": CobidRegistered.NO,
            "fire_resiliance_bonus": FireResilienceBonus.NO,
            "electric_rate": Decimal("0.11"),
            "gas_rate": Decimal("1.04"),
        }

    def dump_assertions(self, calculator, basic=False, report_only=False):
        if report_only:
            print(calculator.input_report)
            if basic:
                # print(calculator.as_built_report)
                return
            print(calculator.savings.report)
            print(calculator.incentives.incentive_report)
            print(calculator.allocations.allocation_report)
            print(calculator.projected.projected_report)
            print(calculator.calculations.consumption_report)
            return

        # Saving Data
        print(
            f"self.assertAlmostEqual(calculator.savings.therm.baseline, "
            f"{calculator.savings.therm.baseline:.2f}, 2)"
        )
        print(
            f"self.assertAlmostEqual(calculator.savings.kwh.baseline, "
            f"{calculator.savings.kwh.baseline:.2f}, 2)"
        )
        print(
            f"self.assertAlmostEqual(calculator.savings.mbtu.baseline, "
            f"{calculator.savings.mbtu.baseline:.2f}, 2)"
        )

        print(
            f"self.assertAlmostEqual(calculator.savings.therm.proposed, "
            f"{calculator.savings.therm.proposed:.2f}, 2)"
        )
        print(
            f"self.assertAlmostEqual(calculator.savings.kwh.proposed, "
            f"{calculator.savings.kwh.proposed:.2f}, 2)"
        )
        print(
            f"self.assertAlmostEqual(calculator.savings.mbtu.proposed, "
            f"{calculator.savings.mbtu.proposed:.2f}, 2)"
        )

        print(
            f"self.assertAlmostEqual(calculator.savings.therm.savings, "
            f"{calculator.savings.therm.savings:.2f}, 2)"
        )
        print(
            f"self.assertAlmostEqual(calculator.savings.kwh.savings, "
            f"{calculator.savings.kwh.savings:.2f}, 2)"
        )
        print(
            f"self.assertAlmostEqual(calculator.savings.mbtu.savings, "
            f"{calculator.savings.mbtu.savings:.2f}, 2)"
        )

        print(
            f"self.assertAlmostEqual(calculator.savings.therm.pct_improvement, "
            f"{calculator.savings.therm.pct_improvement:.4f}, 4)"
        )
        print(
            f"self.assertAlmostEqual(calculator.savings.kwh.pct_improvement, "
            f"{calculator.savings.kwh.pct_improvement:.4f}, 4)"
        )
        print(
            f"self.assertAlmostEqual(calculator.savings.mbtu.pct_improvement, "
            f"{calculator.savings.mbtu.pct_improvement:.4f}, 4)"
        )

        # Incentives
        print(
            f"self.assertAlmostEqual(calculator.incentives.baseline_builder_incentive, "
            f"{calculator.incentives.baseline_builder_incentive:.2f}, 2)"
        )
        print(
            f"self.assertAlmostEqual(calculator.incentives.baseline_verifier_incentive, "
            f"{calculator.incentives.baseline_verifier_incentive:.2f}, 2)"
        )
        print(
            f"self.assertEqual(calculator.incentives.builder_incentive, "
            f"{int(calculator.incentives.builder_incentive)})"
        )
        print(
            f"self.assertEqual(calculator.incentives.verifier_incentive, "
            f"{int(calculator.incentives.verifier_incentive)})"
        )

        # Allocations
        print(
            f"self.assertAlmostEqual(calculator.allocations.electric.builder_incentive, "
            f"{calculator.allocations.electric.builder_incentive:.2f}, 2)"
        )
        print(
            f"self.assertAlmostEqual(calculator.allocations.electric.verifier_incentive, "
            f"{calculator.allocations.electric.verifier_incentive:.2f}, 2)"
        )
        print(
            f"self.assertAlmostEqual(calculator.allocations.gas.builder_incentive, "
            f"{calculator.allocations.gas.builder_incentive:.2f}, 2)"
        )
        print(
            f"self.assertAlmostEqual(calculator.allocations.gas.verifier_incentive, "
            f"{calculator.allocations.gas.verifier_incentive:.2f}, 2)"
        )
        print(
            f"self.assertAlmostEqual(calculator.allocations.builder_total_incentive.electric_incentive, "
            f"{calculator.allocations.builder_total_incentive.electric_incentive:.2f}, 2)"
        )
        print(
            f"self.assertAlmostEqual(calculator.allocations.builder_total_incentive.gas_incentive, "
            f"{calculator.allocations.builder_total_incentive.gas_incentive:.2f}, 2)"
        )
        print(
            f"self.assertAlmostEqual(calculator.allocations.builder_total_incentive.solar_incentive, "
            f"{calculator.allocations.builder_total_incentive.solar_incentive:.2f}, 2)"
        )
        print(
            f"self.assertAlmostEqual(calculator.allocations.builder_total_incentive.total, "
            f"{calculator.allocations.builder_total_incentive.total:.2f}, 2)"
        )

        print(
            f"self.assertAlmostEqual(calculator.allocations.verifier_total_incentive.electric_incentive, "
            f"{calculator.allocations.verifier_total_incentive.electric_incentive:.2f}, 2)"
        )
        print(
            f"self.assertAlmostEqual(calculator.allocations.verifier_total_incentive.gas_incentive, "
            f"{calculator.allocations.verifier_total_incentive.gas_incentive:.2f}, 2)"
        )
        print(
            f"self.assertAlmostEqual(calculator.allocations.verifier_total_incentive.solar_incentive, "
            f"{calculator.allocations.verifier_total_incentive.solar_incentive:.2f}, 2)"
        )
        print(
            f"self.assertAlmostEqual(calculator.allocations.verifier_total_incentive.total, "
            f"{calculator.allocations.verifier_total_incentive.total:.2f}, 2)"
        )
        # Calculations
        print(
            f"self.assertAlmostEqual("
            f"calculator.calculations.code_consumption.unadjusted.total_mbtu, "
            f"{calculator.calculations.code_consumption.unadjusted.total_mbtu:.2f}, 2)"
        )
        print(
            f"self.assertAlmostEqual("
            f"calculator.calculations.code_consumption.gas_heat.total_mbtu, "
            f"{calculator.calculations.code_consumption.gas_heat.total_mbtu:.2f}, 2)"
        )
        print(
            f"self.assertAlmostEqual("
            f"calculator.calculations.code_consumption.electric_heat.total_mbtu, "
            f"{calculator.calculations.code_consumption.electric_heat.total_mbtu:.2f}, 2)"
        )

        print(
            f"self.assertAlmostEqual("
            f"calculator.calculations.improved_consumption.unadjusted.total_mbtu, "
            f"{calculator.calculations.improved_consumption.unadjusted.total_mbtu:.2f}, 2)"
        )
        print(
            f"self.assertAlmostEqual("
            f"calculator.calculations.improved_consumption.gas_heat.total_mbtu, "
            f"{calculator.calculations.improved_consumption.gas_heat.total_mbtu:.2f}, 2)"
        )
        print(
            f"self.assertAlmostEqual("
            f"calculator.calculations.improved_consumption.electric_heat.total_mbtu, "
            f"{calculator.calculations.improved_consumption.electric_heat.total_mbtu:.2f}, 2)"
        )

        print(
            f"self.assertEqual(calculator.calculations.code_eps_score, "
            f"{calculator.calculations.code_eps_score})"
        )
        print(
            f"self.assertEqual(calculator.calculations.eps_score, "
            f"{calculator.calculations.eps_score})"
        )
        # Projected
        print(
            f"self.assertEqual(calculator.projected.similar_size_eps, "
            f"{calculator.projected.similar_size_eps})"
        )
        # Carbon
        print(
            f"self.assertAlmostEqual(calculator.carbon.carbon_score.total, "
            f"{calculator.carbon.carbon_score.total:.1f}, 1)"
        )
        print(
            f"self.assertAlmostEqual(calculator.carbon.code_carbon_score.total, "
            f"{calculator.carbon.code_carbon_score.total:.1f}, 1)"
        )
        print(
            f"self.assertAlmostEqual(calculator.carbon.similar_size_carbon_score.total, "
            f"{calculator.carbon.similar_size_carbon_score.total:.1f}, 1)"
        )

    def test_thermostat(self):
        """Test out the smart thermostat to qualifying thermostat input"""
        input_options = self.input_options.copy()
        input_options["thermostat_brand"] = SmartThermostatBrands2022.CARRIER

        qual_list = {
            PrimaryHeatingEquipment2020.GAS_FURNACE: QualifyingThermostat.DUCTED_FURNACE,
            PrimaryHeatingEquipment2020.DFHP: QualifyingThermostat.DUCTED_ASHP,
            PrimaryHeatingEquipment2020.DUCTED_ASHP: QualifyingThermostat.DUCTED_ASHP,
            PrimaryHeatingEquipment2020.MINI_SPLIT_DUCTED: QualifyingThermostat.DUCTED_ASHP,
        }

        for heat_type in PrimaryHeatingEquipment2020:
            with self.subTest(f"Test {heat_type.value}"):
                input_options["primary_heating_class"] = heat_type
                calculator = EPS2022Calculator(**input_options)
                expected = qual_list.get(heat_type, QualifyingThermostat.NONE)
                self.assertEqual(calculator.thermostat, expected)
                self.assertIn(calculator.thermostat.value, calculator._input_savings_data_report)
        with self.subTest(f"Test No Smarts.."):
            input_options["primary_heating_class"] = PrimaryHeatingEquipment2020.DUCTED_ASHP
            input_options["thermostat_brand"] = SmartThermostatBrands2022.NONE
            calculator = EPS2022Calculator(**input_options)
            self.assertEqual(calculator.thermostat, QualifyingThermostat.NONE)
            input_options["thermostat_brand"] = SmartThermostatBrands2022.OTHER
            calculator = EPS2022Calculator(**input_options)
            self.assertEqual(calculator.thermostat, QualifyingThermostat.NONE)
            self.assertIn(calculator.thermostat.value, calculator._input_savings_data_report)

    def test_heat_type(self):
        """Test out the primary heating class to heat type input"""
        input_options = self.input_options.copy()
        for heat_type in PrimaryHeatingEquipment2020:
            with self.subTest(f"Test {heat_type.value}"):
                input_options["primary_heating_class"] = heat_type
                calculator = EPS2022Calculator(**input_options)
                expected = HeatType.GAS if "gas" in heat_type.value.lower() else HeatType.ELECTRIC
                self.assertEqual(calculator.heat_type, expected)
                self.assertIn(calculator.heat_type.value, calculator.input_report)

    def test_data(self):
        input_options = {
            "code_heating_therms": 100.0,
            "improved_heating_therms": 50.0,
            "code_heating_kwh": 500,
            "improved_heating_kwh": 400,
            "code_cooling_kwh": 1000.0,
            "improved_cooling_kwh": 80,
            "code_hot_water_therms": 0.0,
            "improved_hot_water_therms": 0.0,
            "code_hot_water_kwh": 1500.0,
            "improved_hot_water_kwh": 1000.0,
            "code_lights_and_appliance_therms": 0,
            "improved_lights_and_appliance_therms": 0.0,
            "code_lights_and_appliance_kwh": 100,
            "improved_lights_and_appliance_kwh": 80,
            "primary_heating_class": PrimaryHeatingEquipment2020.GAS_FURNACE,
            "thermostat_brand": SmartThermostatBrands2022.BRYANT,
            "fireplace": Fireplace2020.FE_50_59,
            # Axis Data for Incentives
            "electric_utility": ElectricUtility.PACIFIC_POWER,
            "gas_utility": GasUtility.CASCADE,
            # Solar Production
            "improved_pv_kwh": 2000,
            "electric_elements": AdditionalElements2022.ALL,
            "solar_elements": SolarElements2022.NET_ZERO,
            "cobid_registered": CobidRegistered.BOTH,
            "has_heat_pump_water_heater": True,
            # Fire
            "fire_resiliance_bonus": None,
            # EPS Sheet
            "us_state": PNWUSStates.OR,
            "climate_location": ClimateLocation.PORTLAND,
            "conditioned_area": 2000.00,
            "electric_rate": Decimal("0.11130"),
            "gas_rate": Decimal("2.35"),
        }
        calculator = EPS2022Calculator(**input_options)
        # self.dump_assertions(calculator)

        self.assertAlmostEqual(calculator.savings.therm.baseline, 188.50, 2)
        self.assertAlmostEqual(calculator.savings.kwh.baseline, 3100.00, 2)
        self.assertAlmostEqual(calculator.savings.mbtu.baseline, 29.43, 2)
        self.assertAlmostEqual(calculator.savings.therm.proposed, 135.50, 2)
        self.assertAlmostEqual(calculator.savings.kwh.proposed, 1531.20, 2)
        self.assertAlmostEqual(calculator.savings.mbtu.proposed, 18.77, 2)
        self.assertAlmostEqual(calculator.savings.therm.savings, 53.00, 2)
        self.assertAlmostEqual(calculator.savings.kwh.savings, 1568.80, 2)
        self.assertAlmostEqual(calculator.savings.mbtu.savings, 10.65, 2)
        self.assertAlmostEqual(calculator.savings.therm.pct_improvement, 0.2812, 4)
        self.assertAlmostEqual(calculator.savings.kwh.pct_improvement, 0.5061, 4)
        self.assertAlmostEqual(calculator.savings.mbtu.pct_improvement, 0.3620, 4)
        self.assertAlmostEqual(calculator.incentives.baseline_builder_incentive, 4085.00, 2)
        self.assertAlmostEqual(calculator.incentives.baseline_verifier_incentive, 817.00, 2)
        self.assertEqual(calculator.incentives.builder_incentive, 5735)
        self.assertEqual(calculator.incentives.verifier_incentive, 1067)
        self.assertAlmostEqual(calculator.allocations.electric.builder_incentive, 1674.85, 2)
        self.assertAlmostEqual(calculator.allocations.electric.verifier_incentive, 334.97, 2)
        self.assertAlmostEqual(calculator.allocations.gas.builder_incentive, 2410.15, 2)
        self.assertAlmostEqual(calculator.allocations.gas.verifier_incentive, 482.03, 2)
        self.assertAlmostEqual(
            calculator.allocations.builder_total_incentive.electric_incentive, 1772.00, 2
        )
        self.assertAlmostEqual(
            calculator.allocations.builder_total_incentive.gas_incentive, 2763.00, 2
        )
        self.assertAlmostEqual(
            calculator.allocations.builder_total_incentive.solar_incentive, 1200.00, 2
        )
        self.assertAlmostEqual(calculator.allocations.builder_total_incentive.total, 5735.00, 2)
        self.assertAlmostEqual(
            calculator.allocations.verifier_total_incentive.electric_incentive, 335.00, 2
        )
        self.assertAlmostEqual(
            calculator.allocations.verifier_total_incentive.gas_incentive, 732.00, 2
        )
        self.assertAlmostEqual(
            calculator.allocations.verifier_total_incentive.solar_incentive, 0.00, 2
        )
        self.assertAlmostEqual(calculator.allocations.verifier_total_incentive.total, 1067.00, 2)
        self.assertAlmostEqual(
            calculator.calculations.code_consumption.unadjusted.total_mbtu, 29.43, 2
        )
        self.assertAlmostEqual(
            calculator.calculations.code_consumption.gas_heat.total_mbtu, 40.59, 2
        )
        self.assertAlmostEqual(
            calculator.calculations.code_consumption.electric_heat.total_mbtu, 45.14, 2
        )
        self.assertAlmostEqual(
            calculator.calculations.improved_consumption.unadjusted.total_mbtu, 11.95, 2
        )
        self.assertAlmostEqual(
            calculator.calculations.improved_consumption.gas_heat.total_mbtu, 19.39, 2
        )
        self.assertAlmostEqual(
            calculator.calculations.improved_consumption.electric_heat.total_mbtu, 18.11, 2
        )
        self.assertEqual(calculator.calculations.code_eps_score, 41)
        self.assertEqual(calculator.calculations.eps_score, 19)
        self.assertEqual(calculator.projected.similar_size_eps, 105)
        self.assertAlmostEqual(calculator.carbon.carbon_score.total, 1.6, 1)
        self.assertAlmostEqual(calculator.carbon.code_carbon_score.total, 2.8, 1)
        self.assertAlmostEqual(calculator.carbon.similar_size_carbon_score.total, 9.4, 1)

    def test_fire_rebuild(self):
        input_options = {
            "code_heating_therms": 100.0,
            "improved_heating_therms": 50.0,
            "code_heating_kwh": 500,
            "improved_heating_kwh": 400,
            "code_cooling_kwh": 1000.0,
            "improved_cooling_kwh": 80,
            "code_hot_water_therms": 0.0,
            "improved_hot_water_therms": 0.0,
            "code_hot_water_kwh": 1500.0,
            "improved_hot_water_kwh": 1000.0,
            "code_lights_and_appliance_therms": 0,
            "improved_lights_and_appliance_therms": 0.0,
            "code_lights_and_appliance_kwh": 100,
            "improved_lights_and_appliance_kwh": 80,
            "primary_heating_class": PrimaryHeatingEquipment2020.GAS_FURNACE,
            "thermostat_brand": SmartThermostatBrands2022.BRYANT,
            "fireplace": Fireplace2020.FE_50_59,
            # Axis Data for Incentives
            "electric_utility": ElectricUtility.PACIFIC_POWER,
            "gas_utility": GasUtility.CASCADE,
            # Solar Production
            "improved_pv_kwh": 2000,
            "electric_elements": AdditionalElements2022.ALL,
            "solar_elements": SolarElements2022.NET_ZERO,
            "cobid_registered": CobidRegistered.BOTH,
            "has_heat_pump_water_heater": True,
            # Fire
            "fire_resiliance_bonus": FireResilienceBonus.NO,
            # EPS Sheet
            "us_state": PNWUSStates.OR,
            "climate_location": ClimateLocation.PORTLAND,
            "conditioned_area": 2000.00,
            "electric_rate": Decimal("0.112"),
            "gas_rate": Decimal("1.35"),
        }
        calculator = EPS2022Calculator(**input_options)
        # self.dump_assertions(calculator)
        self.assertAlmostEqual(calculator.incentives.baseline_builder_incentive, 8170.00, 2)
        self.assertAlmostEqual(calculator.incentives.baseline_verifier_incentive, 817.00, 2)

    def test_fire_eps_sheet_data(self):
        input_data = {
            "us_state": PNWUSStates.OR,
            "climate_location": ClimateLocation.PORTLAND,
            "primary_heating_class": PrimaryHeatingEquipment2020.MINI_SPLIT_NON_DUCTED,
            "conditioned_area": ClimateLocation.PORTLAND,
            "electric_utility": ElectricUtility.NONE,
            "gas_utility": GasUtility.NONE,
            "fireplace": Fireplace2020.FE_GTE_70,
            "thermostat_brand": SmartThermostatBrands2022.NONE,
            "electric_elements": AdditionalElements2022.NO,
            "solar_elements": None,
            "cobid_registered": CobidRegistered.NO,
            "cobid_type": CobidQualification.NO,
            "fire_resiliance_bonus": None,
            "code_heating_therms": 0.0,
            "code_heating_kwh": 327,
            "code_cooling_kwh": 450,
            "code_hot_water_therms": 0.0,
            "code_hot_water_kwh": 0.0,
            "code_lights_and_appliance_therms": 0.0,
            "code_lights_and_appliance_kwh": 3903,
            "improved_heating_therms": 0.0,
            "improved_heating_kwh": 195,
            "improved_cooling_kwh": 499,
            "improved_hot_water_therms": 0.0,
            "improved_hot_water_kwh": 0.0,
            "improved_lights_and_appliance_therms": 0.0,
            "improved_lights_and_appliance_kwh": 3824,
            "improved_pv_kwh": 0,
            "electric_rate": 0.1123,
            "gas_rate": 1.0377,
        }
        calculator = EPS2022Calculator(**input_data)
        self.assertAlmostEqual(calculator.annual_cost, 580.22, 2)
        self.assertAlmostEqual(calculator.monthly_cost, 48.35, 2)

    def test_all_electric(self):
        input_data = {
            "us_state": PNWUSStates.OR,
            "climate_location": ClimateLocation.NORTH_BEND,
            "primary_heating_class": PrimaryHeatingEquipment2020.MINI_SPLIT_NON_DUCTED,
            "conditioned_area": ClimateLocation.NORTH_BEND,
            "electric_utility": ElectricUtility.PACIFIC_POWER,
            "gas_utility": GasUtility.NONE,
            "fireplace": Fireplace2020.NONE,
            "thermostat_brand": SmartThermostatBrands2022.BRYANT,
            "electric_elements": AdditionalElements2022.ALL,
            "solar_elements": SolarElements2022.NET_ZERO,
            "cobid_registered": CobidRegistered.BOTH,
            "cobid_type": CobidQualification.ALL,
            "fire_resiliance_bonus": FireResilienceBonus.TRIPLE_PANE_AND_RIGID_INSULATION_AND_SEALED_ATTIC,
            "code_heating_therms": 0.0,
            "code_heating_kwh": 2022.981323,
            "code_cooling_kwh": 120.225677,
            "code_hot_water_therms": 0.0,
            "code_hot_water_kwh": 2657.459473,
            "code_lights_and_appliance_therms": 0.0,
            "code_lights_and_appliance_kwh": 4194.941406,
            "improved_heating_therms": 0.0,
            "improved_heating_kwh": 1074.823486,
            "improved_cooling_kwh": 74.99575,
            "improved_hot_water_therms": 0.0,
            "improved_hot_water_kwh": 658.204102,
            "improved_lights_and_appliance_therms": 0.0,
            "improved_lights_and_appliance_kwh": 3795.087891,
            "improved_pv_kwh": 10000.0,
            "electric_rate": 0.1115,
            "gas_rate": 0.0,
        }
        calculator = EPS2022Calculator(**input_data)
        self.assertAlmostEqual(calculator.incentives.baseline_builder_incentive, 8170.0)
        self.assertAlmostEqual(calculator.incentives.baseline_verifier_incentive, 817.0)

    def test_dei_no_incentive(self):
        """If a home does not qualify > 10% then negate the dei incentives too"""

        input_data = {
            "us_state": PNWUSStates.OR,
            "climate_location": ClimateLocation.REDMOND,
            "primary_heating_class": PrimaryHeatingEquipment2020.MINI_SPLIT_NON_DUCTED,
            "conditioned_area": 600,
            "electric_utility": ElectricUtility.PACIFIC_POWER,
            "gas_utility": GasUtility.CASCADE,
            "fireplace": Fireplace2020.NONE,
            "thermostat_brand": SmartThermostatBrands2022.NONE,
            "electric_elements": AdditionalElements2022.NO,
            "solar_elements": None,
            "cobid_registered": CobidRegistered.NO,
            "cobid_type": CobidQualification.AFFORDABLE,
            "fire_resiliance_bonus": None,
            "code_heating_therms": 0.0,
            "code_heating_kwh": 1825.240479,
            "code_cooling_kwh": 246.655838,
            "code_hot_water_therms": 158.954697,
            "code_hot_water_kwh": 0.0,
            "code_lights_and_appliance_therms": 28.0,
            "code_lights_and_appliance_kwh": 2545.060791,
            "improved_heating_therms": 0.0,
            "improved_heating_kwh": 1019.736328,
            "improved_cooling_kwh": 208.269913,
            "improved_hot_water_therms": 152.654327,
            "improved_hot_water_kwh": 0.0,
            "improved_lights_and_appliance_therms": 28.0,
            "improved_lights_and_appliance_kwh": 2697.514893,
            "improved_pv_kwh": 0.0,
            "electric_rate": 0.1115,
            "gas_rate": 1.253,
        }
        calculator = EPS2022Calculator(**input_data)
        # self.dump_assertions(calculator)

        self.assertAlmostEqual(calculator.savings.therm.pct_improvement, 0.0337, 4)
        self.assertAlmostEqual(calculator.savings.kwh.pct_improvement, 0.1498, 4)
        self.assertAlmostEqual(calculator.savings.mbtu.pct_improvement, 0.0868, 4)

        self.assertEqual(calculator.incentives.builder_incentive, 0.0)
        self.assertEqual(calculator.incentives.verifier_incentive, 0.0)
