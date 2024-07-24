"""test_calculator.py - Axis"""

__author__ = "Steven K"
__date__ = "9/10/21 09:59"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
from django.test import TestCase

from axis.customer_eto.calculator.eps_2021.calculator import EPS2021Calculator
from axis.customer_eto.enumerations import (
    ClimateLocation,
    HeatType,
    ElectricUtility,
    GasUtility,
    Fireplace2020,
    PNWUSStates,
    PrimaryHeatingEquipment2020,
    SmartThermostatBrands2020,
    GridHarmonization2020,
    AdditionalIncentives2020,
    SolarElements2020,
    QualifyingThermostat,
)

log = logging.getLogger(__name__)


class EPS2021CalculatorTests(TestCase):
    @property
    def input_options(self):
        return {
            "us_state": PNWUSStates.WA,
            "climate_location": ClimateLocation.EUGENE,
            "primary_heating_class": PrimaryHeatingEquipment2020.GAS_FURNACE,
            "conditioned_area": 2500.00,
            "electric_utility": ElectricUtility.PACIFIC_POWER,
            "gas_utility": GasUtility.NW_NATURAL,
            "fireplace": Fireplace2020.FE_50_59,
            "thermostat_brand": SmartThermostatBrands2020.BRYANT,
            "grid_harmonization_elements": GridHarmonization2020.NONE,
            "eps_additional_incentives": AdditionalIncentives2020.NO,
            "solar_elements": SolarElements2020.NONE,
            "code_heating_therms": 23.3,
            "code_heating_kwh": 1501.2,
            "code_cooling_kwh": 2503.6,
            "code_hot_water_therms": 25.2,
            "code_hot_water_kwh": 1025.2,
            "code_lights_and_appliance_therms": 5.2,
            "code_lights_and_appliance_kwh": 1975.2,
            "code_electric_cost": 32.1,
            "code_gas_cost": 8.1,
            "improved_heating_therms": 18.1,
            "improved_heating_kwh": 1223.3,
            "improved_cooling_kwh": 2356.4,
            "improved_hot_water_therms": 18.799999999,
            "improved_hot_water_kwh": 967.73,
            "improved_solar_hot_water_therms": 1.3,
            "improved_solar_hot_water_kwh": 1.4,
            "improved_lights_and_appliance_therms": 4.8,
            "improved_lights_and_appliance_kwh": 1387.43,
            "improved_pv_kwh": 5,
            "improved_electric_cost": 18.2,
            "improved_gas_cost": 5.1,
        }

    def dump_assertions(self, calculator, basic=False, report_only=False):
        if report_only:
            print(calculator.input_report)
            if basic:
                print(calculator.as_built_report)
                return
            print(calculator.code_calculations.calculation_report)
            print(calculator.improved_calculations.calculation_report)
            print(calculator.improvement_report)
            print(calculator.incentives.incentive_report)
            print(calculator.projected.projected_consumption_report)
            print(calculator.net_zero.mad_max_report)
            print(calculator.net_zero.incentive_allocation_report)
            print(calculator.net_zero.net_zero_allocation_report)
            return

        print(
            f"self.assertEqual(calculator.improved_calculations.eps_score, "
            f"{calculator.improved_calculations.eps_score})"
        )
        print(
            f"self.assertEqual(calculator.code_calculations.code_eps_score, "
            f"{calculator.code_calculations.code_eps_score})"
        )
        if calculator.us_state == PNWUSStates.WA:
            print(
                f"self.assertEqual(calculator.improvement_data.floored_improvement_breakout.therms, "
                f"{calculator.improvement_data.floored_improvement_breakout.therms})"
            )
        else:
            print(
                f"self.assertEqual(calculator.improvement_data.floored_improvement_breakout.mbtu, "
                f"{calculator.improvement_data.floored_improvement_breakout.mbtu})"
            )

        print(
            f"self.assertAlmostEqual(calculator.incentives.builder_incentive, "
            f"{round(calculator.incentives.builder_incentive, 2)}, 2)"
        )
        print(
            f"self.assertAlmostEqual(calculator.incentives.verifier_incentive, "
            f"{round(calculator.incentives.verifier_incentive, 2)}, 2)"
        )
        print(
            f"self.assertAlmostEqual(calculator.improved_calculations.carbon_score, "
            f"{round(calculator.improved_calculations.carbon_score, 3)}, 3)"
        )
        print(
            f"self.assertAlmostEqual(calculator.code_calculations.code_carbon_score, "
            f"{round(calculator.code_calculations.code_carbon_score, 3)}, 3)"
        )
        print(
            f"self.assertAlmostEqual(calculator.annual_cost, "
            f"{round(calculator.annual_cost, 2)}, 2)"
        )
        print(
            f"self.assertAlmostEqual(calculator.monthly_cost, "
            f"{round(calculator.monthly_cost, 2)}, 2)"
        )
        print(
            f"self.assertAlmostEqual(calculator.projected.similar_size_eps, "
            f"{round(calculator.projected.similar_size_eps, 3)}, 3)"
        )
        print(
            f"self.assertAlmostEqual(calculator.projected.similar_size_carbon, "
            f"{round(calculator.projected.similar_size_carbon, 3)}, 3)"
        )

        # Reporting
        if basic:
            return

        print(
            f'self.assertIn("{calculator.improved_calculations.eps_score}", '
            f"calculator.as_built_report)"
        )
        print(
            f'self.assertIn("{calculator.code_calculations.code_eps_score}", '
            f"calculator.as_built_report)"
        )
        if calculator.us_state == PNWUSStates.WA:
            print(
                f'self.assertIn("{calculator.improvement_data.floored_improvement_breakout.therms:.0%}", '
                f"calculator.as_built_report)"
            )
        else:
            print(
                f'self.assertIn("{calculator.improvement_data.floored_improvement_breakout.mbtu:.0%}", '
                f"calculator.as_built_report)"
            )

        print(
            f'self.assertIn("{calculator.incentives.builder_incentive:,.0f}", '
            f"calculator.as_built_report)"
        )
        print(
            f'self.assertIn("{calculator.incentives.verifier_incentive:,.0f}", '
            f"calculator.as_built_report)"
        )
        print(
            f'self.assertIn("{calculator.improved_calculations.carbon_score:.1f}", '
            f"calculator.as_built_report)"
        )
        print(
            f'self.assertIn("{calculator.code_calculations.code_carbon_score:.1f}", '
            f"calculator.as_built_report)"
        )
        print(f'self.assertIn("{calculator.annual_cost:,.0f}", calculator.as_built_report)')
        print(f'self.assertIn("{calculator.monthly_cost:,.0f}", calculator.as_built_report)')
        print(
            f'self.assertIn("{calculator.projected.similar_size_eps:.0f}", '
            f"calculator.as_built_report)"
        )
        print(
            f'self.assertIn("{calculator.projected.similar_size_carbon:.1f}", '
            f"calculator.as_built_report)"
        )
        print(calculator.as_built_report)

    def test_heat_type(self):
        """Test out the primary heating class to heat type input"""
        input_options = self.input_options.copy()
        for heat_type in PrimaryHeatingEquipment2020:
            with self.subTest(f"Test {heat_type.value}"):
                input_options["primary_heating_class"] = heat_type
                calculator = EPS2021Calculator(**input_options)
                expected = HeatType.GAS if "gas" in heat_type.value.lower() else HeatType.ELECTRIC
                self.assertEqual(calculator.heat_type, expected)

    def test_thermostat(self):
        """Test out the smart thermostat to qualifying thermostat input"""
        input_options = self.input_options.copy()
        input_options["thermostat_brand"] = SmartThermostatBrands2020.CARRIER
        for heat_type in PrimaryHeatingEquipment2020:
            with self.subTest(f"Test {heat_type.value}"):
                input_options["primary_heating_class"] = heat_type
                calculator = EPS2021Calculator(**input_options)
                expected = QualifyingThermostat.NONE
                if heat_type == PrimaryHeatingEquipment2020.DFHP:
                    expected = QualifyingThermostat.NONE
                elif "mini" in heat_type.value.lower() and "split" in heat_type.value.lower():
                    expected = QualifyingThermostat.NONE
                elif "gas" in heat_type.value.lower():
                    expected = QualifyingThermostat.DUCTED_FURNACE
                elif "electric" in heat_type.value.lower():
                    expected = QualifyingThermostat.DUCTED_ASHP
                self.assertEqual(calculator.thermostat, expected)
        with self.subTest(f"Test No Smarts.."):
            input_options["primary_heating_class"] = PrimaryHeatingEquipment2020.DUCTED_ASHP
            input_options["thermostat_brand"] = SmartThermostatBrands2020.NONE
            calculator = EPS2021Calculator(**input_options)
            self.assertEqual(calculator.thermostat, QualifyingThermostat.NONE)

    def test_input_report(self):
        calculator = EPS2021Calculator(**self.input_options)
        data = calculator.input_data
        for k, v in self.input_options.items():
            str_value = v
            self.assertEqual(data[k], str_value)
            if k.startswith("code_"):
                self.assertEqual(getattr(calculator.code, k.replace("code_", "")), v)
                if k not in ["code_pv_kwh", "code_electric_cost", "code_gas_cost"]:
                    self.assertEqual(
                        getattr(calculator.code_calculations.unadjusted, k.replace("code_", "")), v
                    )
            elif k.startswith("improved_"):
                self.assertEqual(getattr(calculator.improved, k.replace("improved_", "")), v)
                if k not in ["improved_electric_cost", "improved_gas_cost"]:
                    self.assertEqual(
                        getattr(
                            calculator.improved_calculations.input_data, k.replace("improved_", "")
                        ),
                        v,
                    )
            else:
                self.assertEqual(getattr(calculator, k), v)

        # print(calculator.input_report)

    def test_input_totals(self):
        calculator = EPS2021Calculator(**self.input_options)

        total_kwh = (
            self.input_options.get("code_heating_kwh", 0)
            + self.input_options.get("code_cooling_kwh", 0)
            + self.input_options.get("code_hot_water_kwh", 0)
            + self.input_options.get("code_lights_and_appliance_kwh", 0)
        )
        total_therms = (
            self.input_options.get("code_heating_therms", 0)
            + self.input_options.get("code_hot_water_therms", 0)
            + self.input_options.get("code_lights_and_appliance_therms", 0)
        )
        self.assertEqual(round(calculator.code.total_therms, 4), round(total_therms, 4))
        self.assertEqual(round(calculator.code.total_kwh, 4), round(total_kwh, 4))

        total_kwh = (
            self.input_options.get("improved_heating_kwh", 0)
            + self.input_options.get("improved_cooling_kwh", 0)
            + self.input_options.get("improved_solar_hot_water_kwh", 0)
            + self.input_options.get("improved_lights_and_appliance_kwh", 0)
            - self.input_options.get("improved_pv_kwh", 0)
        )
        total_therms = (
            self.input_options.get("improved_heating_therms", 0)
            + self.input_options.get("improved_solar_hot_water_therms", 0)
            + self.input_options.get("improved_lights_and_appliance_therms", 0)
        )
        self.assertEqual(round(calculator.improved.total_therms, 4), round(total_therms, 4))
        self.assertEqual(round(calculator.improved.total_kwh, 4), round(total_kwh, 4))

    def test_input_totals_no_solar(self):
        input_data = self.input_options.copy()
        input_data.pop("improved_solar_hot_water_kwh")
        input_data.pop("improved_solar_hot_water_therms")
        calculator = EPS2021Calculator(**input_data)

        total_kwh = (
            input_data.get("improved_heating_kwh", 0)
            + input_data.get("improved_cooling_kwh", 0)
            + input_data.get("improved_hot_water_kwh", 0)
            + input_data.get("improved_lights_and_appliance_kwh", 0)
            - input_data.get("improved_pv_kwh", 0)
        )
        total_therms = (
            input_data.get("improved_heating_therms", 0)
            + input_data.get("improved_hot_water_therms", 0)
            + input_data.get("improved_lights_and_appliance_therms", 0)
        )
        self.assertEqual(calculator.improved.total_therms, total_therms)
        self.assertEqual(calculator.improved.total_kwh, total_kwh)
        # print(calculator.input_report)

    def test_code_data(self):
        calculator = EPS2021Calculator(**self.input_options)
        data = calculator.input_data
        for k, value in self.input_options.items():
            self.assertEqual(data[k], value)
            if k.startswith("code_"):
                if k not in ["code_pv_kwh", "code_electric_cost", "code_gas_cost"]:
                    self.assertEqual(
                        getattr(calculator.code_calculations.unadjusted, k.replace("code_", "")),
                        value,
                    )

    def test_improvements_data(self):
        calculator = EPS2021Calculator(**self.input_options)
        for k, v in self.input_options.items():
            if k.startswith("improved_"):
                self.assertEqual(getattr(calculator.improved, k.replace("improved_", "")), v)
                if k not in ["improved_electric_cost", "improved_gas_cost"]:
                    self.assertEqual(
                        getattr(
                            calculator.improved_calculations.input_data, k.replace("improved_", "")
                        ),
                        v,
                    )
            elif k in ("fireplace", "thermostat"):
                self.assertEqual(getattr(calculator.improved_calculations, k), v)

    def test_improvement(self):
        calculator = EPS2021Calculator(**self.input_options)

        # Gas

        self.assertEqual(round(calculator.improvement_data.code.mbtu, 2), 38.12)
        self.assertEqual(round(calculator.improvement_data.improved.mbtu, 2), 33.16)
        self.assertEqual(round(calculator.improvement_data.savings.mbtu, 2), 4.96)
        self.assertEqual(round(calculator.improvement_data.percent_improvement, 4), 0.1301)

        report = calculator.improvement_report.split("\n")
        self.assertIn("13.", report[-1])

        # ELECTRIC

        input_options = self.input_options.copy()
        input_options["primary_heating_class"] = PrimaryHeatingEquipment2020.DUCTED_ASHP
        calculator = EPS2021Calculator(**input_options)
        self.assertEqual(calculator.heat_type, HeatType.ELECTRIC)

        self.assertEqual(round(calculator.improvement_data.code.mbtu, 2), 38.12)
        self.assertEqual(round(calculator.improvement_data.improved.mbtu, 2), 33.27)
        self.assertEqual(round(calculator.improvement_data.savings.mbtu, 2), 4.85)
        self.assertEqual(round(calculator.improvement_data.percent_improvement, 4), 0.1273)

        report = calculator.improvement_report.split("\n")
        self.assertIn("12.", report[-1])

    def test_incentives_input(self):
        calculator = EPS2021Calculator(**self.input_options)
        self.assertEqual(calculator.incentives.__class__.__name__, "Incentives2021WA")
        self.assertEqual(
            calculator.improvement_data.percent_improvement_breakout.therms,
            calculator.incentives.percent_improvement,
        )
        self.assertEqual(calculator.electric_utility, calculator.incentives.electric_utility)
        self.assertEqual(calculator.gas_utility, calculator.incentives.gas_utility)
        self.assertEqual(calculator.improved.heating_therms, calculator.incentives.heating_therms)
        self.assertEqual(
            calculator.improved.hot_water_therms,
            calculator.incentives.hot_water_therms,  # TODO BUG REPORT
        )
        self.assertEqual(calculator.improved.hot_water_kwh, calculator.incentives.hot_water_kwh)
        self.assertEqual(calculator.constants, calculator.incentives.constants)

        input_options = self.input_options.copy()
        input_options["us_state"] = PNWUSStates.OR
        calculator = EPS2021Calculator(**input_options)

        self.assertEqual(
            calculator.improvement_data.percent_improvement,
            calculator.incentives.percent_improvement,
        )
        self.assertEqual(calculator.incentives.__class__.__name__, "Incentives2020")
        self.assertEqual(calculator.electric_utility, calculator.incentives.electric_utility)
        self.assertEqual(calculator.gas_utility, calculator.incentives.gas_utility)
        self.assertEqual(calculator.improved.heating_therms, calculator.incentives.heating_therms)
        self.assertEqual(
            calculator.improved.hot_water_therms, calculator.incentives.hot_water_therms
        )
        self.assertEqual(calculator.improved.hot_water_kwh, calculator.incentives.hot_water_kwh)
        self.assertEqual(calculator.constants, calculator.incentives.constants)

    def test_projected_inputs(self):
        calculator = EPS2021Calculator(**self.input_options)
        self.assertEqual(calculator.projected.climate_location, ClimateLocation.PORTLAND)
        self.assertEqual(calculator.projected.heat_type, calculator.heat_type)
        self.assertEqual(
            calculator.projected.conditioned_area, self.input_options["conditioned_area"]
        )
        self.assertEqual(
            calculator.projected.electric_utility, self.input_options["electric_utility"]
        )
        self.assertEqual(calculator.projected.gas_utility, self.input_options["gas_utility"])

    def test_net_zero_inputs(self):
        input_options = self.input_options.copy()
        input_options["thermostat_brand"] = (SmartThermostatBrands2020.NEST_LEARNING,)
        input_options["grid_harmonization_elements"] = (GridHarmonization2020.STORAGE,)
        input_options["eps_additional_incentives"] = AdditionalIncentives2020.ALL
        input_options["solar_elements"] = SolarElements2020.SOLAR_PV

        calculator = EPS2021Calculator(**self.input_options)
        self.assertEqual(calculator.net_zero.total_kwh, calculator.improved.total_kwh)
        self.assertEqual(calculator.net_zero.total_therms, calculator.improved.total_therms)
        self.assertEqual(calculator.net_zero.cooling_kwh, calculator.improved.cooling_kwh)
        self.assertEqual(calculator.net_zero.pv_kwh, calculator.improved.pv_kwh)
        self.assertEqual(
            calculator.net_zero.percent_improvement, calculator.improvement_data.percent_improvement
        )
        self.assertEqual(
            calculator.net_zero.percent_improvement_therms,
            calculator.improvement_data.percent_improvement_breakout.therms,
        )
        self.assertEqual(calculator.net_zero.constants, calculator.constants)
        self.assertEqual(calculator.net_zero.electric_utility, calculator.electric_utility)
        self.assertEqual(
            calculator.net_zero.primary_heating_class, calculator.primary_heating_class
        )
        self.assertEqual(calculator.net_zero.thermostat_brand, calculator.thermostat_brand)
        self.assertEqual(
            calculator.net_zero.grid_harmonization_elements, calculator.grid_harmonization_elements
        )
        self.assertEqual(
            calculator.net_zero.eps_additional_incentives, calculator.eps_additional_incentives
        )
        self.assertEqual(calculator.net_zero.solar_elements, calculator.solar_elements)

    def test_OR_2020_all_electric_real_data_with_esh_and_nz(self):
        input_data = {
            "us_state": PNWUSStates.OR,
            "climate_location": ClimateLocation.PORTLAND,
            "primary_heating_class": PrimaryHeatingEquipment2020.DUCTED_ASHP,
            "conditioned_area": 2500.00,
            "electric_utility": ElectricUtility.PACIFIC_POWER,
            "gas_utility": GasUtility.NW_NATURAL,
            "fireplace": Fireplace2020.NONE,
            "thermostat_brand": SmartThermostatBrands2020.NEST_LEARNING,
            "grid_harmonization_elements": GridHarmonization2020.ALL,
            "eps_additional_incentives": AdditionalIncentives2020.SOLAR_ELEMENTS_AND_ENERGY_SMART,
            "solar_elements": SolarElements2020.SOLAR_PV,
            "code_heating_therms": 0.0,
            "code_heating_kwh": 3328.2,
            "code_cooling_kwh": 2503.6,
            "code_hot_water_therms": 0.0,
            "code_hot_water_kwh": 2503.6,
            "code_lights_and_appliance_therms": 0.0,
            "code_lights_and_appliance_kwh": 4960.0,
            "code_electric_cost": 823,
            "code_gas_cost": 0.0,
            "improved_heating_therms": 0.0,
            "improved_heating_kwh": 1400.0,
            "improved_cooling_kwh": 120.0,
            "improved_hot_water_therms": 0.0,
            "improved_hot_water_kwh": 1200.0,
            "improved_lights_and_appliance_therms": 0.0,
            "improved_lights_and_appliance_kwh": 4396.0,
            "improved_pv_kwh": 8000,
            "improved_electric_cost": 729,
            "improved_gas_cost": 0,
        }

        calculator = EPS2021Calculator(**input_data)
        # self.dump_assertions(calculator)
        self.assertEqual(calculator.improved_calculations.eps_score, 0)
        self.assertEqual(calculator.code_calculations.code_eps_score, 75.0)
        self.assertEqual(calculator.improvement_data.floored_improvement_breakout.mbtu, 0.47)
        self.assertAlmostEqual(calculator.incentives.builder_incentive, 6473.0, 2)
        self.assertAlmostEqual(calculator.incentives.verifier_incentive, 1889.0, 2)
        self.assertAlmostEqual(calculator.improved_calculations.carbon_score, 0, 3)
        self.assertAlmostEqual(calculator.code_calculations.code_carbon_score, 7.246, 3)
        self.assertAlmostEqual(calculator.annual_cost, 729, 2)
        self.assertAlmostEqual(calculator.monthly_cost, 60.75, 2)
        self.assertAlmostEqual(calculator.projected.similar_size_eps, 127.512, 3)
        self.assertAlmostEqual(calculator.projected.similar_size_carbon, 11.267, 3)
        self.assertIn("0", calculator.as_built_report)
        self.assertIn("75.0", calculator.as_built_report)
        self.assertIn("47%", calculator.as_built_report)
        self.assertIn("6,473", calculator.as_built_report)
        self.assertIn("1,889", calculator.as_built_report)
        self.assertIn("0.0", calculator.as_built_report)
        self.assertIn("7.2", calculator.as_built_report)
        self.assertIn("729", calculator.as_built_report)
        self.assertIn("61", calculator.as_built_report)
        self.assertIn("128", calculator.as_built_report)
        self.assertIn("11.3", calculator.as_built_report)

    def test_OR_2020_all_electric_real_data_with_esh_only(self):
        input_data = {
            "us_state": PNWUSStates.OR,
            "climate_location": ClimateLocation.PORTLAND,
            "primary_heating_class": PrimaryHeatingEquipment2020.DUCTED_ASHP,
            "conditioned_area": 2500.00,
            "electric_utility": ElectricUtility.PACIFIC_POWER,
            "gas_utility": GasUtility.NW_NATURAL,
            "fireplace": Fireplace2020.NONE,
            "thermostat_brand": SmartThermostatBrands2020.NEST_LEARNING,
            "grid_harmonization_elements": GridHarmonization2020.ALL,
            "eps_additional_incentives": AdditionalIncentives2020.SOLAR_ELEMENTS_AND_ENERGY_SMART,
            "solar_elements": SolarElements2020.SOLAR_PV,
            "code_heating_therms": 0.0,
            "code_heating_kwh": 3328.2,
            "code_cooling_kwh": 2503.6,
            "code_hot_water_therms": 0.0,
            "code_hot_water_kwh": 2503.6,
            "code_lights_and_appliance_therms": 0.0,
            "code_lights_and_appliance_kwh": 4960.0,
            "code_electric_cost": 823,
            "code_gas_cost": 0.0,
            "improved_heating_therms": 0.0,
            "improved_heating_kwh": 1400.0,
            "improved_cooling_kwh": 120.0,
            "improved_hot_water_therms": 0.0,
            "improved_hot_water_kwh": 1200.0,
            "improved_lights_and_appliance_therms": 0.0,
            "improved_lights_and_appliance_kwh": 4396.0,
            "improved_pv_kwh": 0.0,
            "improved_electric_cost": 729,
            "improved_gas_cost": 0,
        }

        calculator = EPS2021Calculator(**input_data)
        # self.dump_assertions(calculator)
        self.assertEqual(calculator.improved_calculations.eps_score, 35.0)
        self.assertEqual(calculator.code_calculations.code_eps_score, 75.0)
        self.assertEqual(calculator.improvement_data.floored_improvement_breakout.mbtu, 0.47)
        self.assertAlmostEqual(calculator.incentives.builder_incentive, 5723.0, 2)
        self.assertAlmostEqual(calculator.incentives.verifier_incentive, 1889.0, 2)
        self.assertAlmostEqual(calculator.improved_calculations.carbon_score, 3.783, 3)
        self.assertAlmostEqual(calculator.code_calculations.code_carbon_score, 7.246, 3)
        self.assertAlmostEqual(calculator.annual_cost, 729, 2)
        self.assertAlmostEqual(calculator.monthly_cost, 60.75, 2)
        self.assertAlmostEqual(calculator.projected.similar_size_eps, 127.512, 3)
        self.assertAlmostEqual(calculator.projected.similar_size_carbon, 11.267, 3)
        self.assertIn("35.0", calculator.as_built_report)
        self.assertIn("75.0", calculator.as_built_report)
        self.assertIn("47%", calculator.as_built_report)
        self.assertIn("5,723", calculator.as_built_report)
        self.assertIn("1,889", calculator.as_built_report)
        self.assertIn("3.8", calculator.as_built_report)
        self.assertIn("7.2", calculator.as_built_report)
        self.assertIn("729", calculator.as_built_report)
        self.assertIn("61", calculator.as_built_report)
        self.assertIn("128", calculator.as_built_report)
        self.assertIn("11.3", calculator.as_built_report)

    def test_OR_2020_all_electric_no_esh(self):
        input_data = {
            "us_state": PNWUSStates.OR,
            "climate_location": ClimateLocation.PORTLAND,
            "primary_heating_class": PrimaryHeatingEquipment2020.DUCTED_ASHP,
            "conditioned_area": 2500.00,
            "electric_utility": ElectricUtility.PACIFIC_POWER,
            "gas_utility": GasUtility.NW_NATURAL,
            "fireplace": Fireplace2020.NONE,
            "thermostat_brand": SmartThermostatBrands2020.BRYANT,
            "grid_harmonization_elements": GridHarmonization2020.ALL,
            "eps_additional_incentives": AdditionalIncentives2020.SOLAR_ELEMENTS_AND_ENERGY_SMART,
            "solar_elements": SolarElements2020.SOLAR_PV,
            "code_heating_therms": 0.0,
            "code_heating_kwh": 3328.2,
            "code_cooling_kwh": 2503.6,
            "code_hot_water_therms": 0.0,
            "code_hot_water_kwh": 2503.6,
            "code_lights_and_appliance_therms": 0.0,
            "code_lights_and_appliance_kwh": 4960.0,
            "code_electric_cost": 823,
            "code_gas_cost": 0.0,
            "improved_heating_therms": 0.0,
            "improved_heating_kwh": 1400.0,
            "improved_cooling_kwh": 120.0,
            "improved_hot_water_therms": 0.0,
            "improved_hot_water_kwh": 1200.0,
            "improved_lights_and_appliance_therms": 0.0,
            "improved_lights_and_appliance_kwh": 4396.0,
            "improved_pv_kwh": 0.0,
            "improved_electric_cost": 729,
            "improved_gas_cost": 0,
        }
        calculator = EPS2021Calculator(**input_data)
        self.assertEqual(calculator.improved_calculations.eps_score, 35.0)
        self.assertEqual(calculator.code_calculations.code_eps_score, 75.0)
        self.assertEqual(calculator.improvement_data.floored_improvement_breakout.mbtu, 0.47)
        self.assertAlmostEqual(calculator.incentives.builder_incentive, 5223.0, 2)
        self.assertAlmostEqual(calculator.incentives.verifier_incentive, 1889.0, 2)
        self.assertAlmostEqual(calculator.improved_calculations.carbon_score, 3.783, 3)
        self.assertAlmostEqual(calculator.code_calculations.code_carbon_score, 7.246, 3)
        self.assertAlmostEqual(calculator.annual_cost, 729, 2)
        self.assertAlmostEqual(calculator.monthly_cost, 60.75, 2)
        self.assertAlmostEqual(calculator.projected.similar_size_eps, 127.512, 3)
        self.assertAlmostEqual(calculator.projected.similar_size_carbon, 11.267, 3)
        self.assertIn("35.0", calculator.as_built_report)
        self.assertIn("75.0", calculator.as_built_report)
        self.assertIn("47%", calculator.as_built_report)
        self.assertIn("5,223", calculator.as_built_report)
        self.assertIn("1,889", calculator.as_built_report)
        self.assertIn("3.8", calculator.as_built_report)
        self.assertIn("7.2", calculator.as_built_report)
        self.assertIn("729", calculator.as_built_report)
        self.assertIn("61", calculator.as_built_report)
        self.assertIn("128", calculator.as_built_report)
        self.assertIn("11.3", calculator.as_built_report)

    def test_OR_2020_gas_only(self):
        input_data = {
            "us_state": PNWUSStates.OR,
            "climate_location": ClimateLocation.PORTLAND,
            "primary_heating_class": PrimaryHeatingEquipment2020.GAS_FURNACE,
            "conditioned_area": 2500.00,
            "electric_utility": ElectricUtility.PACIFIC_POWER,
            "gas_utility": GasUtility.NW_NATURAL,
            "fireplace": Fireplace2020.FE_50_59,
            "thermostat_brand": SmartThermostatBrands2020.BRYANT,
            "grid_harmonization_elements": GridHarmonization2020.ALL,
            "eps_additional_incentives": AdditionalIncentives2020.SOLAR_ELEMENTS_AND_ENERGY_SMART,
            "solar_elements": SolarElements2020.SOLAR_PV,
            "code_heating_therms": 1200.0,
            "code_heating_kwh": 20,
            "code_cooling_kwh": 2503.6,
            "code_hot_water_therms": 35.0,
            "code_hot_water_kwh": 5.0,
            "code_lights_and_appliance_therms": 8.0,
            "code_lights_and_appliance_kwh": 4960.0,
            "code_electric_cost": 823,
            "code_gas_cost": 50.0,
            "improved_heating_therms": 900.0,
            "improved_heating_kwh": 10.0,
            "improved_cooling_kwh": 120.0,
            "improved_hot_water_therms": 25.0,
            "improved_hot_water_kwh": 2.0,
            "improved_lights_and_appliance_therms": 7.5,
            "improved_lights_and_appliance_kwh": 4396.0,
            "improved_pv_kwh": 0.0,
            "improved_electric_cost": 729,
            "improved_gas_cost": 20,
        }
        calculator = EPS2021Calculator(**input_data)
        # self.dump_assertions(calculator)
        self.assertEqual(calculator.improved_calculations.eps_score, 112.0)
        self.assertEqual(calculator.code_calculations.code_eps_score, 159.0)
        self.assertEqual(calculator.improvement_data.floored_improvement_breakout.mbtu, 0.29)
        self.assertAlmostEqual(calculator.incentives.builder_incentive, 3018.0, 2)
        self.assertAlmostEqual(calculator.incentives.verifier_incentive, 739.0, 2)
        self.assertAlmostEqual(calculator.improved_calculations.carbon_score, 8.12, 3)
        self.assertAlmostEqual(calculator.code_calculations.code_carbon_score, 11.871, 3)
        self.assertAlmostEqual(calculator.annual_cost, 749, 2)
        self.assertAlmostEqual(calculator.monthly_cost, 62.42, 2)
        self.assertAlmostEqual(calculator.projected.similar_size_eps, 121.025, 3)
        self.assertAlmostEqual(calculator.projected.similar_size_carbon, 10.767, 3)
        self.assertIn("112.0", calculator.as_built_report)
        self.assertIn("159.0", calculator.as_built_report)
        self.assertIn("29%", calculator.as_built_report)
        self.assertIn("3,018", calculator.as_built_report)
        self.assertIn("739", calculator.as_built_report)
        self.assertIn("8.1", calculator.as_built_report)
        self.assertIn("11.9", calculator.as_built_report)
        self.assertIn("749", calculator.as_built_report)
        self.assertIn("62", calculator.as_built_report)
        self.assertIn("121", calculator.as_built_report)
        self.assertIn("10.8", calculator.as_built_report)

    def test_OR_2020_gas_with_net_zero(self):
        input_data = {
            "us_state": PNWUSStates.OR,
            "climate_location": ClimateLocation.PORTLAND,
            "primary_heating_class": PrimaryHeatingEquipment2020.GAS_FURNACE,
            "conditioned_area": 2500.00,
            "electric_utility": ElectricUtility.PACIFIC_POWER,
            "gas_utility": GasUtility.NW_NATURAL,
            "fireplace": Fireplace2020.FE_50_59,
            "thermostat_brand": SmartThermostatBrands2020.BRYANT,
            "grid_harmonization_elements": GridHarmonization2020.ALL,
            "eps_additional_incentives": AdditionalIncentives2020.SOLAR_ELEMENTS_AND_ENERGY_SMART,
            "solar_elements": SolarElements2020.SOLAR_PV,
            "code_heating_therms": 1200.0,
            "code_heating_kwh": 20,
            "code_cooling_kwh": 2503.6,
            "code_hot_water_therms": 35.0,
            "code_hot_water_kwh": 5.0,
            "code_lights_and_appliance_therms": 8.0,
            "code_lights_and_appliance_kwh": 4960.0,
            "code_electric_cost": 823,
            "code_gas_cost": 50.0,
            "improved_heating_therms": 900.0,
            "improved_heating_kwh": 10.0,
            "improved_cooling_kwh": 120.0,
            "improved_hot_water_therms": 25.0,
            "improved_hot_water_kwh": 2.0,
            "improved_lights_and_appliance_therms": 7.5,
            "improved_lights_and_appliance_kwh": 4396.0,
            "improved_pv_kwh": 4600.0,
            "improved_electric_cost": 729,
            "improved_gas_cost": 20,
        }
        calculator = EPS2021Calculator(**input_data)
        # self.dump_assertions(calculator)
        self.assertEqual(calculator.improved_calculations.eps_score, 96.0)
        self.assertEqual(calculator.code_calculations.code_eps_score, 159.0)
        self.assertEqual(calculator.improvement_data.floored_improvement_breakout.mbtu, 0.29)
        self.assertAlmostEqual(calculator.incentives.builder_incentive, 3768.0, 2)
        self.assertAlmostEqual(calculator.incentives.verifier_incentive, 739.0, 2)
        self.assertAlmostEqual(calculator.improved_calculations.carbon_score, 5.613, 3)
        self.assertAlmostEqual(calculator.code_calculations.code_carbon_score, 11.871, 3)
        self.assertAlmostEqual(calculator.annual_cost, 749, 2)
        self.assertAlmostEqual(calculator.monthly_cost, 62.42, 2)
        self.assertAlmostEqual(calculator.projected.similar_size_eps, 121.025, 3)
        self.assertAlmostEqual(calculator.projected.similar_size_carbon, 10.767, 3)
        self.assertIn("96.0", calculator.as_built_report)
        self.assertIn("159.0", calculator.as_built_report)
        self.assertIn("29%", calculator.as_built_report)
        self.assertIn("3,768", calculator.as_built_report)
        self.assertIn("739", calculator.as_built_report)
        self.assertIn("5.6", calculator.as_built_report)
        self.assertIn("11.9", calculator.as_built_report)
        self.assertIn("749", calculator.as_built_report)
        self.assertIn("62", calculator.as_built_report)
        self.assertIn("121", calculator.as_built_report)
        self.assertIn("10.8", calculator.as_built_report)

    def test_OR_2020_gas_with_net_zero_and_esh(self):
        input_data = {
            "us_state": PNWUSStates.OR,
            "climate_location": ClimateLocation.PORTLAND,
            "primary_heating_class": PrimaryHeatingEquipment2020.GAS_FURNACE,
            "conditioned_area": 2500.00,
            "electric_utility": ElectricUtility.PACIFIC_POWER,
            "gas_utility": GasUtility.NW_NATURAL,
            "fireplace": Fireplace2020.FE_50_59,
            "thermostat_brand": SmartThermostatBrands2020.ECOBEE4,
            "grid_harmonization_elements": GridHarmonization2020.ALL,
            "eps_additional_incentives": AdditionalIncentives2020.SOLAR_ELEMENTS_AND_ENERGY_SMART,
            "solar_elements": SolarElements2020.SOLAR_PV,
            "code_heating_therms": 1200.0,
            "code_heating_kwh": 20,
            "code_cooling_kwh": 2503.6,
            "code_hot_water_therms": 35.0,
            "code_hot_water_kwh": 5.0,
            "code_lights_and_appliance_therms": 8.0,
            "code_lights_and_appliance_kwh": 4960.0,
            "code_electric_cost": 823,
            "code_gas_cost": 50.0,
            "improved_heating_therms": 900.0,
            "improved_heating_kwh": 10.0,
            "improved_cooling_kwh": 120.0,
            "improved_hot_water_therms": 25.0,
            "improved_hot_water_kwh": 2.0,
            "improved_lights_and_appliance_therms": 7.5,
            "improved_lights_and_appliance_kwh": 4396.0,
            "improved_pv_kwh": 4600.0,
            "improved_electric_cost": 729,
            "improved_gas_cost": 20,
        }
        calculator = EPS2021Calculator(**input_data)
        # self.dump_assertions(calculator)
        self.assertEqual(calculator.improved_calculations.eps_score, 96.0)
        self.assertEqual(calculator.code_calculations.code_eps_score, 159.0)
        self.assertEqual(calculator.improvement_data.floored_improvement_breakout.mbtu, 0.29)
        self.assertAlmostEqual(calculator.incentives.builder_incentive, 4268.0, 2)
        self.assertAlmostEqual(calculator.incentives.verifier_incentive, 739.0, 2)
        self.assertAlmostEqual(calculator.improved_calculations.carbon_score, 5.613, 3)
        self.assertAlmostEqual(calculator.code_calculations.code_carbon_score, 11.871, 3)
        self.assertAlmostEqual(calculator.annual_cost, 749, 2)
        self.assertAlmostEqual(calculator.monthly_cost, 62.42, 2)
        self.assertAlmostEqual(calculator.projected.similar_size_eps, 121.025, 3)
        self.assertAlmostEqual(calculator.projected.similar_size_carbon, 10.767, 3)
        self.assertIn("96.0", calculator.as_built_report)
        self.assertIn("159.0", calculator.as_built_report)
        self.assertIn("29%", calculator.as_built_report)
        self.assertIn("4,268", calculator.as_built_report)
        self.assertIn("739", calculator.as_built_report)
        self.assertIn("5.6", calculator.as_built_report)
        self.assertIn("11.9", calculator.as_built_report)
        self.assertIn("749", calculator.as_built_report)
        self.assertIn("62", calculator.as_built_report)
        self.assertIn("121", calculator.as_built_report)
        self.assertIn("10.8", calculator.as_built_report)

    def test_2021_WA_gas_with_esh_and_nz(self):
        input_data = {
            "us_state": PNWUSStates.WA,
            "climate_location": ClimateLocation.EUGENE,
            "primary_heating_class": PrimaryHeatingEquipment2020.GAS_FURNACE,
            "conditioned_area": 2500.00,
            "electric_utility": ElectricUtility.PACIFIC_POWER,
            "gas_utility": GasUtility.NW_NATURAL,
            "fireplace": Fireplace2020.FE_50_59,
            "thermostat_brand": SmartThermostatBrands2020.ECOBEE4,
            "grid_harmonization_elements": GridHarmonization2020.ALL,
            "eps_additional_incentives": AdditionalIncentives2020.SOLAR_ELEMENTS_AND_ENERGY_SMART,
            "solar_elements": SolarElements2020.SOLAR_PV,
            "code_heating_therms": 1200.0,
            "code_heating_kwh": 20,
            "code_cooling_kwh": 2503.6,
            "code_hot_water_therms": 35.0,
            "code_hot_water_kwh": 5.0,
            "code_lights_and_appliance_therms": 8.0,
            "code_lights_and_appliance_kwh": 4960.0,
            "code_electric_cost": 823,
            "code_gas_cost": 50.0,
            "improved_heating_therms": 1100.0,
            "improved_heating_kwh": 10.0,
            "improved_cooling_kwh": 2450.0,
            "improved_hot_water_therms": 90.0,
            "improved_hot_water_kwh": 2.0,
            "improved_lights_and_appliance_therms": 7.5,
            "improved_lights_and_appliance_kwh": 4396.0,
            "improved_pv_kwh": 4600.0,
            "improved_electric_cost": 729,
            "improved_gas_cost": 20,
        }
        calculator = EPS2021Calculator(**input_data)
        # self.dump_assertions(calculator)
        self.assertEqual(calculator.improved_calculations.eps_score, 130.0)
        self.assertEqual(calculator.code_calculations.code_eps_score, 159.0)
        self.assertEqual(calculator.improvement_data.floored_improvement_breakout.therms, 0.08)
        self.assertAlmostEqual(calculator.incentives.builder_incentive, 1104.0, 2)
        self.assertAlmostEqual(calculator.incentives.verifier_incentive, 100.0, 2)
        self.assertAlmostEqual(calculator.improved_calculations.carbon_score, 8.368, 3)
        self.assertAlmostEqual(calculator.code_calculations.code_carbon_score, 11.871, 3)
        self.assertAlmostEqual(calculator.annual_cost, 749, 2)
        self.assertAlmostEqual(calculator.monthly_cost, 62.42, 2)
        self.assertAlmostEqual(calculator.projected.similar_size_eps, 121.025, 3)
        self.assertAlmostEqual(calculator.projected.similar_size_carbon, 10.767, 3)
        self.assertIn("130.0", calculator.as_built_report)
        self.assertIn("159.0", calculator.as_built_report)
        self.assertIn("8%", calculator.as_built_report)
        self.assertIn("1,104", calculator.as_built_report)
        self.assertIn("100", calculator.as_built_report)
        self.assertIn("8.4", calculator.as_built_report)
        self.assertIn("11.9", calculator.as_built_report)
        self.assertIn("749", calculator.as_built_report)
        self.assertIn("62", calculator.as_built_report)
        self.assertIn("121", calculator.as_built_report)
        self.assertIn("10.8", calculator.as_built_report)

    def test_2021_WA_electric(self):
        input_data = {
            "us_state": PNWUSStates.WA,
            "climate_location": ClimateLocation.EUGENE,
            "primary_heating_class": PrimaryHeatingEquipment2020.DUCTED_ASHP,
            "conditioned_area": 2500.00,
            "electric_utility": ElectricUtility.PACIFIC_POWER,
            "gas_utility": GasUtility.NW_NATURAL,
            "fireplace": Fireplace2020.FE_50_59,
            "thermostat_brand": SmartThermostatBrands2020.ECOBEE4,
            "grid_harmonization_elements": GridHarmonization2020.ALL,
            "eps_additional_incentives": AdditionalIncentives2020.SOLAR_ELEMENTS_AND_ENERGY_SMART,
            "solar_elements": SolarElements2020.SOLAR_PV,
            "code_heating_therms": 0.0,
            "code_heating_kwh": 1200,
            "code_cooling_kwh": 2503.6,
            "code_hot_water_therms": 0.0,
            "code_hot_water_kwh": 250.0,
            "code_lights_and_appliance_therms": 20.0,
            "code_lights_and_appliance_kwh": 4960.0,
            "code_electric_cost": 823,
            "code_gas_cost": 50.0,
            "improved_heating_therms": 0.0,
            "improved_heating_kwh": 750.0,
            "improved_cooling_kwh": 2450.0,
            "improved_hot_water_therms": 0.0,
            "improved_hot_water_kwh": 200.0,
            "improved_lights_and_appliance_therms": 1.0,
            "improved_lights_and_appliance_kwh": 4396.0,
            "improved_pv_kwh": 0.0,
            "improved_electric_cost": 729,
            "improved_gas_cost": 20,
        }
        calculator = EPS2021Calculator(**input_data)
        # self.dump_assertions(calculator)
        self.assertEqual(calculator.improved_calculations.eps_score, 41.0)
        self.assertEqual(calculator.code_calculations.code_eps_score, 51.0)
        self.assertEqual(calculator.improvement_data.floored_improvement_breakout.therms, 0.17)
        self.assertAlmostEqual(calculator.incentives.builder_incentive, 1701.0, 2)
        self.assertAlmostEqual(calculator.incentives.verifier_incentive, 100.0, 2)
        self.assertAlmostEqual(calculator.improved_calculations.carbon_score, 4.748, 3)
        self.assertAlmostEqual(calculator.code_calculations.code_carbon_score, 5.493, 3)
        self.assertAlmostEqual(calculator.annual_cost, 749, 2)
        self.assertAlmostEqual(calculator.monthly_cost, 62.42, 2)
        self.assertAlmostEqual(calculator.projected.similar_size_eps, 127.512, 3)
        self.assertAlmostEqual(calculator.projected.similar_size_carbon, 11.267, 3)
        self.assertIn("41.0", calculator.as_built_report)
        self.assertIn("51.0", calculator.as_built_report)
        self.assertIn("17%", calculator.as_built_report)
        self.assertIn("1,701", calculator.as_built_report)
        self.assertIn("100", calculator.as_built_report)
        self.assertIn("4.7", calculator.as_built_report)
        self.assertIn("5.5", calculator.as_built_report)
        self.assertIn("749", calculator.as_built_report)
        self.assertIn("62", calculator.as_built_report)
        self.assertIn("128", calculator.as_built_report)
        self.assertIn("11.3", calculator.as_built_report)

    def test_too_low(self):
        input_data = {
            "us_state": PNWUSStates.OR,
            "climate_location": ClimateLocation.PORTLAND,
            "primary_heating_class": PrimaryHeatingEquipment2020.DUCTED_ASHP,
            "conditioned_area": 2497,
            "electric_utility": ElectricUtility.NONE,
            "gas_utility": GasUtility.NW_NATURAL,
            "fireplace": Fireplace2020.FE_50_59,
            "thermostat_brand": SmartThermostatBrands2020.BRYANT,
            "grid_harmonization_elements": GridHarmonization2020.NONE,
            "eps_additional_incentives": AdditionalIncentives2020.SOLAR_ELEMENTS,
            "solar_elements": SolarElements2020.SOLAR_READY,
            "code_heating_therms": 0.0,
            "code_heating_kwh": 3479.303955,
            "code_cooling_kwh": 695.220215,
            "code_hot_water_therms": 0.0,
            "code_hot_water_kwh": 3516.385986,
            "code_lights_and_appliance_therms": 36.099998,
            "code_lights_and_appliance_kwh": 5373.15332,
            "code_electric_cost": 1521.713867,
            "code_gas_cost": 32.75425,
            "improved_heating_therms": 0.0,
            "improved_heating_kwh": 3479.078125,
            "improved_cooling_kwh": 621.320801,
            "improved_hot_water_therms": 0.0,
            "improved_hot_water_kwh": 3516.061279,
            "improved_lights_and_appliance_therms": 36.099998,
            "improved_lights_and_appliance_kwh": 5373.15332,
            "improved_pv_kwh": 0.0,
            "improved_solar_hot_water_therms": 0.0,
            "improved_solar_hot_water_kwh": 0.0,
            "improved_electric_cost": 1521.345825,
            "improved_gas_cost": 32.75425,
        }
        calculator = EPS2021Calculator(**input_data)
        # self.dump_assertions(calculator)
        self.assertEqual(calculator.improved_calculations.eps_score, 84.0)
        self.assertEqual(calculator.code_calculations.code_eps_score, 89.0)
        self.assertEqual(calculator.improvement_data.floored_improvement_breakout.mbtu, 0.03)
        self.assertAlmostEqual(calculator.incentives.builder_incentive, 0.0, 2)
        self.assertAlmostEqual(calculator.incentives.verifier_incentive, 0, 2)
        self.assertAlmostEqual(calculator.improved_calculations.carbon_score, 1.149, 3)
        self.assertAlmostEqual(calculator.code_calculations.code_carbon_score, 7.849, 3)
        self.assertAlmostEqual(calculator.annual_cost, 1554.1, 2)
        self.assertAlmostEqual(calculator.monthly_cost, 129.51, 2)
        self.assertAlmostEqual(calculator.projected.similar_size_eps, 127.455, 3)
        self.assertAlmostEqual(calculator.projected.similar_size_carbon, 0.692, 3)
        self.assertIn("84.0", calculator.as_built_report)
        self.assertIn("89.0", calculator.as_built_report)
        self.assertIn("3%", calculator.as_built_report)
        self.assertIn("0", calculator.as_built_report)
        self.assertIn("0", calculator.as_built_report)
        self.assertIn("1.1", calculator.as_built_report)
        self.assertIn("7.8", calculator.as_built_report)
        self.assertIn("1,554", calculator.as_built_report)
        self.assertIn("130", calculator.as_built_report)
        self.assertIn("127", calculator.as_built_report)
        self.assertIn("0.7", calculator.as_built_report)

    def test_138477(self):
        input_data = {
            "us_state": PNWUSStates.OR,
            "climate_location": ClimateLocation.PORTLAND,
            "primary_heating_class": PrimaryHeatingEquipment2020.GAS_FURNACE,
            "conditioned_area": 1922,
            "electric_utility": ElectricUtility.NONE,
            "gas_utility": GasUtility.NW_NATURAL,
            "fireplace": Fireplace2020.FE_50_59,
            "thermostat_brand": SmartThermostatBrands2020.NONE,
            "grid_harmonization_elements": GridHarmonization2020.NONE,
            "eps_additional_incentives": AdditionalIncentives2020.NO,
            "solar_elements": SolarElements2020.NONE,
            "code_heating_therms": 294.767914,
            "code_heating_kwh": 295.231689,
            "code_cooling_kwh": 0.0,
            "code_hot_water_therms": 183.639435,
            "code_hot_water_kwh": 0.0,
            "code_lights_and_appliance_therms": 33.400002,
            "code_lights_and_appliance_kwh": 4721.441406,
            "code_electric_cost": 291.43222,
            "code_gas_cost": 463.803894,
            "improved_heating_therms": 208.300308,
            "improved_heating_kwh": 123.565407,
            "improved_cooling_kwh": 0.0,
            "improved_hot_water_therms": 96.834358,
            "improved_hot_water_kwh": 0.0,
            "improved_lights_and_appliance_therms": 33.400002,
            "improved_lights_and_appliance_kwh": 4714.088379,
            "improved_pv_kwh": 0.0,
            "improved_solar_hot_water_therms": 0.0,
            "improved_solar_hot_water_kwh": 0.0,
            "improved_electric_cost": 281.052368,
            "improved_gas_cost": 306.757111,
        }
        calculator = EPS2021Calculator(**input_data)
        # print(self.dump_assertions(calculator))
        self.assertEqual(calculator.improved_calculations.eps_score, 59.0)
        self.assertEqual(calculator.code_calculations.code_eps_score, 77.0)
        self.assertEqual(calculator.improvement_data.floored_improvement_breakout.mbtu, 0.23)
        self.assertAlmostEqual(calculator.incentives.builder_incentive, 1957.0, 2)
        self.assertAlmostEqual(calculator.incentives.verifier_incentive, 378.0, 2)
        self.assertAlmostEqual(calculator.improved_calculations.carbon_score, 2.66, 3)
        self.assertAlmostEqual(calculator.code_calculations.code_carbon_score, 6.246, 3)
        self.assertAlmostEqual(calculator.annual_cost, 587.81, 2)
        self.assertAlmostEqual(calculator.monthly_cost, 48.98, 2)
        self.assertAlmostEqual(calculator.projected.similar_size_eps, 103.017, 3)
        self.assertAlmostEqual(calculator.projected.similar_size_carbon, 4.483, 3)
        self.assertIn("59.0", calculator.as_built_report)
        self.assertIn("77.0", calculator.as_built_report)
        self.assertIn("23%", calculator.as_built_report)
        self.assertIn("1,957", calculator.as_built_report)
        self.assertIn("378", calculator.as_built_report)
        self.assertIn("2.7", calculator.as_built_report)
        self.assertIn("6.2", calculator.as_built_report)
        self.assertIn("588", calculator.as_built_report)
        self.assertIn("49", calculator.as_built_report)
        self.assertIn("103", calculator.as_built_report)
        self.assertIn("4.5", calculator.as_built_report)

    def test_156263(self):
        input_data = {
            "us_state": PNWUSStates.OR,
            "climate_location": ClimateLocation.PORTLAND,
            "primary_heating_class": PrimaryHeatingEquipment2020.DUCTED_ASHP,
            "conditioned_area": 1679,
            "electric_utility": ElectricUtility.PORTLAND_GENERAL,
            "gas_utility": GasUtility.NW_NATURAL,
            "fireplace": Fireplace2020.NONE,
            "thermostat_brand": SmartThermostatBrands2020.ECOBEE4,
            "grid_harmonization_elements": GridHarmonization2020.NONE,
            "eps_additional_incentives": AdditionalIncentives2020.NO,
            "solar_elements": SolarElements2020.NONE,
            "code_heating_therms": 0.0,
            "code_heating_kwh": 3105.820068,
            "code_cooling_kwh": 431.95697,
            "code_hot_water_therms": 0.0,
            "code_hot_water_kwh": 2559.936035,
            "code_lights_and_appliance_therms": 0.0,
            "code_lights_and_appliance_kwh": 4664.444336,
            "code_electric_cost": 1248.610962,
            "code_gas_cost": 0.0,
            "improved_heating_therms": 0.0,
            "improved_heating_kwh": 2552.915039,
            "improved_cooling_kwh": 449.412598,
            "improved_hot_water_therms": 0.0,
            "improved_hot_water_kwh": 749.551147,
            "improved_lights_and_appliance_therms": 0.0,
            "improved_lights_and_appliance_kwh": 4658.063477,
            "improved_pv_kwh": 0.0,
            "improved_solar_hot_water_therms": 0.0,
            "improved_solar_hot_water_kwh": 0.0,
            "improved_electric_cost": 971.901001,
            "improved_gas_cost": 0.0,
        }

        calculator = EPS2021Calculator(**input_data)
        # print(self.dump_assertions(calculator))
        self.assertEqual(calculator.improved_calculations.eps_score, 46.0)
        self.assertEqual(calculator.code_calculations.code_eps_score, 65.0)
        self.assertEqual(calculator.improvement_data.floored_improvement_breakout.mbtu, 0.24)
        self.assertAlmostEqual(calculator.incentives.builder_incentive, 2349.0, 2)
        self.assertAlmostEqual(calculator.incentives.verifier_incentive, 461.0, 2)
        self.assertAlmostEqual(calculator.improved_calculations.carbon_score, 4.402, 3)
        self.assertAlmostEqual(calculator.code_calculations.code_carbon_score, 5.865, 3)
        self.assertAlmostEqual(calculator.annual_cost, 971.9, 2)
        self.assertAlmostEqual(calculator.monthly_cost, 80.99, 2)
        self.assertAlmostEqual(calculator.projected.similar_size_eps, 111.992, 3)
        self.assertAlmostEqual(calculator.projected.similar_size_carbon, 9.692, 3)
        self.assertIn("46.0", calculator.as_built_report)
        self.assertIn("65.0", calculator.as_built_report)
        self.assertIn("24%", calculator.as_built_report)
        self.assertIn("2,349", calculator.as_built_report)
        self.assertIn("461", calculator.as_built_report)
        self.assertIn("4.4", calculator.as_built_report)
        self.assertIn("5.9", calculator.as_built_report)
        self.assertIn("972", calculator.as_built_report)
        self.assertIn("81", calculator.as_built_report)
        self.assertIn("112", calculator.as_built_report)
        self.assertIn("9.7", calculator.as_built_report)
        # print(calculator.improved_calculations.calculation_report)
