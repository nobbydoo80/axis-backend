"""calculator.py - Axis"""

__author__ = "Steven K"
__date__ = "12/1/21 16:03"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

from django.test import TestCase

from axis.customer_eto.calculator.eps_fire_2021.calculator import EPSFire2021Calculator
from axis.customer_eto.eep_programs.fire_rebuild_2021 import FireResilienceBonus
from axis.customer_eto.enumerations import (
    PNWUSStates,
    ClimateLocation,
    PrimaryHeatingEquipment2020,
    ElectricUtility,
    GasUtility,
    Fireplace2020,
    SmartThermostatBrands2020,
    GridHarmonization2020,
    AdditionalIncentives2020,
    SolarElements2020,
    YesNo,
)


class EPSFire2021CalculatorTests(TestCase):
    @property
    def input_options(self):
        return {
            "us_state": PNWUSStates.OR,
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
            "fire_resilience_bonus": FireResilienceBonus.NO,
            "fire_rebuild_qualification": YesNo.NO,
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

    def test_fire_resilience_bonus(self):
        input_options = self.input_options.copy()
        for fire in FireResilienceBonus:
            with self.subTest(f"Test {fire.value}"):
                input_options["fire_resilience_bonus"] = fire
                calculator = EPSFire2021Calculator(**input_options)
                self.assertEqual(calculator.fire_resilience_bonus, fire)

    def test_fire_rebuild_qualification(self):
        input_options = self.input_options.copy()
        for ans in YesNo:
            with self.subTest(f"Test {ans.value}"):
                input_options["fire_rebuild_qualification"] = ans
                calculator = EPSFire2021Calculator(**input_options)
                self.assertEqual(calculator.fire_rebuild_qualification, ans)

    def test_net_zero_inputs(self):
        input_options = self.input_options.copy()
        input_options["thermostat_brand"] = (SmartThermostatBrands2020.NEST_LEARNING,)
        input_options["grid_harmonization_elements"] = (GridHarmonization2020.STORAGE,)
        input_options["eps_additional_incentives"] = AdditionalIncentives2020.ALL
        input_options["solar_elements"] = SolarElements2020.SOLAR_PV
        input_options[
            "fire_resilience_bonus"
        ] = FireResilienceBonus.TRIPLE_PANE_AND_RIGID_INSULATION_AND_SEALED_ATTIC
        input_options["fire_rebuild_qualification"] = YesNo.YES

        calculator = EPSFire2021Calculator(**input_options)
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

        self.assertEqual(
            calculator.fire_resilience_bonus,
            FireResilienceBonus.TRIPLE_PANE_AND_RIGID_INSULATION_AND_SEALED_ATTIC,
        )
        self.assertEqual(
            calculator.net_zero.fire_resilience_bonus, calculator.fire_resilience_bonus
        )

        self.assertEqual(calculator.fire_rebuild_qualification, YesNo.YES)
        self.assertEqual(
            calculator.net_zero.fire_resilience_bonus, calculator.fire_resilience_bonus
        )

    def test_incentives_input(self):
        calculator = EPSFire2021Calculator(**self.input_options)
        self.assertEqual(
            calculator.improvement_data.percent_improvement,
            calculator.incentives.percent_improvement,
        )
        self.assertEqual(calculator.incentives.__class__.__name__, "Incentives2021Fire")

    def test_constants(self):
        calculator = EPSFire2021Calculator(**self.input_options)
        self.assertEqual(calculator.constants.__class__.__name__, "FireConstants")

    def test_gamma_11573(self):
        input_data = {
            "us_state": PNWUSStates.OR,
            "climate_location": ClimateLocation.PORTLAND,
            "primary_heating_class": PrimaryHeatingEquipment2020.DUCTED_ASHP,
            "conditioned_area": 1865,
            "electric_utility": ElectricUtility.PORTLAND_GENERAL,
            "gas_utility": GasUtility.NW_NATURAL,
            "fireplace": Fireplace2020.NONE,
            "thermostat_brand": SmartThermostatBrands2020.NONE,
            "grid_harmonization_elements": GridHarmonization2020.NONE,
            "eps_additional_incentives": AdditionalIncentives2020.NO,
            "solar_elements": SolarElements2020.NONE,
            "fire_resilience_bonus": FireResilienceBonus.TRIPLE_PANE_AND_RIGID_INSULATION_AND_SEALED_ATTIC,
            "fire_rebuild_qualification": YesNo.YES,
            "code_heating_therms": 0.0,
            "code_heating_kwh": 3304.074219,
            "code_cooling_kwh": 615.237061,
            "code_hot_water_therms": 0.0,
            "code_hot_water_kwh": 2061.128418,
            "code_lights_and_appliance_therms": 0.0,
            "code_lights_and_appliance_kwh": 4360.966797,
            "code_electric_cost": 1198.946777,
            "code_gas_cost": 0.0,
            "improved_heating_therms": 0.0,
            "improved_heating_kwh": 1383.913086,
            "improved_cooling_kwh": 809.945313,
            "improved_hot_water_therms": 0.0,
            "improved_hot_water_kwh": 360.08902,
            "improved_lights_and_appliance_therms": 0.0,
            "improved_lights_and_appliance_kwh": 4222.242188,
            "improved_pv_kwh": 0.0,
            "improved_solar_hot_water_therms": 0.0,
            "improved_solar_hot_water_kwh": 0.0,
            "improved_electric_cost": 783.126831,
            "improved_gas_cost": 0.0,
        }
        calculator = EPSFire2021Calculator(**input_data)
        self.assertAlmostEqual(calculator.improvement_data.improved.kwh, 6776.19, 2)
