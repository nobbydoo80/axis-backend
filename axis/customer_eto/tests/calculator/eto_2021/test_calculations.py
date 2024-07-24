"""test_calculations.py - Axis"""

__author__ = "Steven K"
__date__ = "9/15/21 09:37"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from django.test import TestCase

from axis.customer_eto.calculator.eps_2021.calculations import CodeCalculation, ImprovedCalculation
from axis.customer_eto.calculator.eps_2021.constants import Constants, FIREPLACE_ADDITION_THERMS
from axis.customer_eto.enumerations import (
    Fireplace2020,
    ElectricUtility,
    QualifyingThermostat,
    HeatType,
    PNWUSStates,
)

log = logging.getLogger(__name__)


class CodeCalculationTests(TestCase):
    @property
    def input_data(self):
        return {
            "heating_therms": 23.3,
            "heating_kwh": 1501.2,
            "cooling_kwh": 2503.6,
            "hot_water_therms": 25.2,
            "hot_water_kwh": 1025.2,
            "lights_and_appliance_therms": 5.2,
            "lights_and_appliance_kwh": 1975.2,
            "fireplace": Fireplace2020.FE_50_59,
            "heat_type": HeatType.ELECTRIC,
            "constants": Constants(ElectricUtility.PACIFIC_POWER),
        }

    def test_unadjusted(self):
        c = CodeCalculation(**self.input_data)
        self.assertEqual(c.unadjusted.heating_therms, self.input_data["heating_therms"])
        self.assertEqual(c.unadjusted.heating_kwh, self.input_data["heating_kwh"])
        self.assertEqual(c.unadjusted.hot_water_therms, self.input_data["hot_water_therms"])
        self.assertEqual(c.unadjusted.hot_water_kwh, self.input_data["hot_water_kwh"])
        self.assertEqual(
            c.unadjusted.lights_and_appliance_therms, self.input_data["lights_and_appliance_therms"]
        )
        self.assertEqual(
            c.unadjusted.lights_and_appliance_kwh, self.input_data["lights_and_appliance_kwh"]
        )
        self.assertEqual(c.unadjusted.fireplace_therms, FIREPLACE_ADDITION_THERMS)
        self.assertEqual(
            c.unadjusted_consumption.total_therms,
            sum(
                [
                    self.input_data["heating_therms"],
                    self.input_data["hot_water_therms"],
                    self.input_data["lights_and_appliance_therms"],
                    FIREPLACE_ADDITION_THERMS,
                ]
            ),
        )
        self.assertEqual(
            c.unadjusted_consumption.total_kwh,
            sum(
                [
                    self.input_data["heating_kwh"],
                    self.input_data["cooling_kwh"],
                    self.input_data["hot_water_kwh"],
                    self.input_data["lights_and_appliance_kwh"],
                ]
            ),
        )

        c.calculation_report

    def test_heating_therms(self):
        c = CodeCalculation(**self.input_data)
        self.assertEqual(c.unadjusted.heating_therms, c.gas_fuel_weight.heating_therms)
        self.assertEqual(c.unadjusted.heating_therms, c.hp_correction.heating_therms)
        self.assertEqual(c.unadjusted.heating_therms, c.hp_fuel_weight.heating_therms)

    def test_heating_kwh(self):
        c = CodeCalculation(**self.input_data)
        self.assertEqual(c.unadjusted.heating_kwh, c.gas_fuel_weight.heating_kwh)
        self.assertEqual(c.unadjusted.heating_kwh, c.hp_correction.heating_kwh)
        self.assertNotEqual(c.unadjusted.heating_kwh, c.hp_fuel_weight.heating_kwh)

    def test_cooling_kwh(self):
        c = CodeCalculation(**self.input_data)
        self.assertEqual(c.unadjusted.cooling_kwh, c.gas_fuel_weight.cooling_kwh)
        self.assertEqual(c.unadjusted.cooling_kwh, c.hp_correction.cooling_kwh)
        self.assertEqual(c.unadjusted.cooling_kwh, c.hp_fuel_weight.cooling_kwh)

    def test_hot_water_therms(self):
        c = CodeCalculation(**self.input_data)
        self.assertEqual(c.unadjusted.hot_water_therms, c.gas_fuel_weight.hot_water_therms)
        self.assertEqual(c.unadjusted.hot_water_therms, c.hp_correction.hot_water_therms)
        self.assertEqual(c.unadjusted.hot_water_therms, c.hp_fuel_weight.hot_water_therms)

    def test_hot_water_kwh(self):
        c = CodeCalculation(**self.input_data)
        self.assertNotEqual(c.unadjusted.hot_water_kwh, c.gas_fuel_weight.hot_water_kwh)
        self.assertEqual(c.unadjusted.hot_water_kwh, c.hp_correction.hot_water_kwh)
        self.assertNotEqual(c.unadjusted.hot_water_kwh, c.hp_fuel_weight.hot_water_kwh)
        self.assertEqual(c.gas_fuel_weight.hot_water_kwh, c.hp_fuel_weight.hot_water_kwh)

    def test_lights_and_appliance_therms(self):
        c = CodeCalculation(**self.input_data)
        self.assertEqual(
            c.unadjusted.lights_and_appliance_therms, c.gas_fuel_weight.lights_and_appliance_therms
        )
        self.assertEqual(
            c.unadjusted.lights_and_appliance_therms, c.hp_correction.lights_and_appliance_therms
        )
        self.assertEqual(
            c.unadjusted.lights_and_appliance_therms, c.hp_fuel_weight.lights_and_appliance_therms
        )

    def test_lights_and_appliance_kwh(self):
        c = CodeCalculation(**self.input_data)
        self.assertEqual(
            c.unadjusted.lights_and_appliance_kwh, c.gas_fuel_weight.lights_and_appliance_kwh
        )
        self.assertEqual(
            c.unadjusted.lights_and_appliance_kwh, c.hp_correction.lights_and_appliance_kwh
        )
        self.assertEqual(
            c.unadjusted.lights_and_appliance_kwh, c.hp_fuel_weight.lights_and_appliance_kwh
        )

    def test_fireplace_therms(self):
        c = CodeCalculation(**self.input_data)
        self.assertEqual(c.unadjusted.fireplace_therms, c.gas_fuel_weight.fireplace_therms)
        self.assertEqual(c.unadjusted.fireplace_therms, c.hp_correction.fireplace_therms)
        self.assertEqual(c.unadjusted.fireplace_therms, c.hp_fuel_weight.fireplace_therms)

    def test_gas_fuel_weight_eps(self):
        c = CodeCalculation(**self.input_data)
        self.assertEqual(c.gas_fuel_weight_eps.total_therms, c.unadjusted_consumption.total_therms)
        self.assertNotEqual(c.gas_fuel_weight_eps.total_kwh, c.unadjusted_consumption.total_kwh)
        self.assertEqual(round(c.gas_fuel_weight_eps.total_mbtu), 40)

    def test_hp_fuel_weight_eps(self):
        c = CodeCalculation(**self.input_data)
        self.assertEqual(c.hp_fuel_weight_eps.total_therms, c.unadjusted_consumption.total_therms)
        self.assertNotEqual(c.hp_fuel_weight_eps.total_kwh, c.unadjusted_consumption.total_kwh)
        self.assertEqual(round(c.hp_fuel_weight_eps.total_mbtu), 51)

    def test_unadjusted_carbon(self):
        c = CodeCalculation(**self.input_data)
        self.assertEqual(round(c.unadjusted_carbon.total_therms, 1), 0.8)
        self.assertEqual(round(c.unadjusted_carbon.total_kwh, 1), 3.8)
        self.assertEqual(round(c.unadjusted_carbon.carbon_score, 1), 4.6)

    def test_hp_correction_carbon(self):
        c = CodeCalculation(**self.input_data)
        self.assertEqual(c.hp_correction_carbon.total_therms, c.unadjusted_carbon.total_therms)
        self.assertEqual(c.hp_correction_carbon.total_kwh, c.unadjusted_carbon.total_kwh)
        self.assertEqual(c.hp_correction_carbon.carbon_score, c.unadjusted_carbon.carbon_score)

    def test_unadjusted_consumption(self):
        c = CodeCalculation(**self.input_data)
        self.assertEqual(round(c.unadjusted_consumption.total_therms, 1), 142.2)
        self.assertEqual(round(c.unadjusted_consumption.total_kwh, 1), 7005.2)

    def test_hp_consumption(self):
        c = CodeCalculation(**self.input_data)
        self.assertEqual(
            c.unadjusted_consumption.total_therms, c.unadjusted_consumption.total_therms
        )
        self.assertEqual(c.unadjusted_consumption.total_kwh, c.unadjusted_consumption.total_kwh)

    def test_code_eps_score(self):
        input_data = self.input_data.copy()
        with self.subTest("Gas Heat"):
            input_data["heat_type"] = HeatType.GAS
            c = CodeCalculation(**input_data)
            self.assertEqual(c.code_eps_score, round(c.gas_fuel_weight_eps.total_mbtu))
        with self.subTest("Electric Heat"):
            input_data["heat_type"] = HeatType.ELECTRIC
            c = CodeCalculation(**input_data)
            self.assertEqual(c.code_eps_score, round(c.hp_fuel_weight_eps.total_mbtu))

    def test_code_carbon_score(self):
        input_data = self.input_data.copy()
        with self.subTest("Gas Heat"):
            input_data["heat_type"] = HeatType.GAS
            c = CodeCalculation(**input_data)
            self.assertEqual(c.code_carbon_score, c.unadjusted_carbon.carbon_score)
        with self.subTest("Electric Heat"):
            input_data["heat_type"] = HeatType.ELECTRIC
            c = CodeCalculation(**input_data)
            self.assertEqual(c.code_carbon_score, c.hp_correction_carbon.carbon_score)


class ImprovedCalculationTests(TestCase):
    @property
    def input_data(self):
        return {
            "heating_therms": 18.1,
            "heating_kwh": 1223.3,
            "cooling_kwh": 2356.4,
            "hot_water_therms": 18.799999999,
            "hot_water_kwh": 967.73,
            "solar_hot_water_therms": 1.3,
            "solar_hot_water_kwh": 1.4,
            "lights_and_appliance_therms": 4.8,
            "lights_and_appliance_kwh": 1387.43,
            "pv_kwh": 5,
            "fireplace": Fireplace2020.FE_50_59,
            "thermostat": QualifyingThermostat.DUCTED_FURNACE,
            "heat_type": HeatType.ELECTRIC,
            "constants": Constants(ElectricUtility.PACIFIC_POWER),
        }

    def dump_assertions(self, c):
        def print_assertion(label, k, v):
            if v is None:
                print(f"self.assertIsNone(c.{label}.{k})")
            elif isinstance(v, float):
                print(f"self.assertAlmostEqual(c.{label}.{k}, {round(v, 4)}, 4)")
            elif isinstance(v, int):
                print(f"self.assertEqual(c.{label}.{k}, {v!r})")

        for k, v in c.unadjusted._asdict().items():
            print_assertion("unadjusted", k, v)
        for k, v in c.gas_fuel_weight._asdict().items():
            print_assertion("gas_fuel_weight", k, v)
        for k, v in c.hp_correction._asdict().items():
            print_assertion("hp_correction", k, v)
        for k, v in c.hp_fuel_weight._asdict().items():
            print_assertion("hp_fuel_weight", k, v)

        for k, v in c.gas_fuel_weight_eps._asdict().items():
            print_assertion("gas_fuel_weight_eps", k, v)
        for k, v in c.hp_fuel_weight_eps._asdict().items():
            print_assertion("hp_fuel_weight_eps", k, v)

        for k, v in c.unadjusted_carbon._asdict().items():
            print_assertion("unadjusted_carbon", k, v)
        for k, v in c.hp_correction_carbon._asdict().items():
            print_assertion("hp_correction_carbon", k, v)

        for k, v in c.unadjusted_consumption._asdict().items():
            print_assertion("unadjusted_consumption", k, v)
        for k, v in c.hp_correction_consumption._asdict().items():
            print_assertion("hp_correction_consumption", k, v)

        print(c.calculation_report)

    def test_solar_low_pv_power(self):
        input_data = {
            "heating_therms": 18.1,
            "heating_kwh": 1223.3,
            "cooling_kwh": 2356.4,
            "hot_water_therms": 18.799999999,
            "hot_water_kwh": 967.73,
            "solar_hot_water_therms": 1.3,
            "solar_hot_water_kwh": 1.4,
            "lights_and_appliance_therms": 4.8,
            "lights_and_appliance_kwh": 1387.43,
            "pv_kwh": 5,
            "fireplace": Fireplace2020.FE_50_59,
            "thermostat": QualifyingThermostat.DUCTED_FURNACE,
            "heat_type": HeatType.ELECTRIC,
            "constants": Constants(ElectricUtility.PACIFIC_POWER, PNWUSStates.WA),
            "us_state": PNWUSStates.WA,
        }

        c = ImprovedCalculation(**input_data)
        # self.dump_assertions(c)

        self.assertAlmostEqual(c.unadjusted.heating_therms, 18.1, 4)
        self.assertAlmostEqual(c.unadjusted.gas_thermostat_savings, 0.0, 4)
        self.assertAlmostEqual(c.unadjusted.heating_kwh, 1223.3, 4)
        self.assertEqual(c.unadjusted.electric_thermostat_savings, 0)
        self.assertAlmostEqual(c.unadjusted.cooling_kwh, 2356.4, 4)
        self.assertEqual(c.unadjusted.cooling_thermostat_savings, 0)
        self.assertAlmostEqual(c.unadjusted.hot_water_therms, 18.8, 4)
        self.assertAlmostEqual(c.unadjusted.hot_water_kwh, 967.73, 4)
        self.assertAlmostEqual(c.unadjusted.lights_and_appliance_therms, 4.8, 4)
        self.assertAlmostEqual(c.unadjusted.lights_and_appliance_kwh, 1387.43, 4)
        self.assertAlmostEqual(c.unadjusted.fireplace_therms, 88.5, 4)
        self.assertAlmostEqual(c.unadjusted.solar_hot_water_therms, 1.3, 4)
        self.assertAlmostEqual(c.unadjusted.solar_hot_water_kwh, 1.4, 4)
        self.assertEqual(c.unadjusted.pv_kwh, 5)
        self.assertAlmostEqual(c.gas_fuel_weight.heating_therms, 18.1, 4)
        self.assertIsNone(c.gas_fuel_weight.gas_thermostat_savings)
        self.assertAlmostEqual(c.gas_fuel_weight.heating_kwh, 1223.3, 4)
        self.assertIsNone(c.gas_fuel_weight.electric_thermostat_savings)
        self.assertAlmostEqual(c.gas_fuel_weight.cooling_kwh, 2356.4, 4)
        self.assertIsNone(c.gas_fuel_weight.cooling_thermostat_savings)
        self.assertEqual(c.gas_fuel_weight.hot_water_therms, 0)
        self.assertEqual(c.gas_fuel_weight.hot_water_kwh, 0)
        self.assertAlmostEqual(c.gas_fuel_weight.lights_and_appliance_therms, 4.8, 4)
        self.assertAlmostEqual(c.gas_fuel_weight.lights_and_appliance_kwh, 1387.43, 4)
        self.assertAlmostEqual(c.gas_fuel_weight.fireplace_therms, 88.5, 4)
        self.assertAlmostEqual(c.gas_fuel_weight.solar_hot_water_therms, 1.3, 4)
        self.assertEqual(c.gas_fuel_weight.solar_hot_water_kwh, 0)
        self.assertAlmostEqual(c.gas_fuel_weight.pv_kwh, 3.6, 4)
        self.assertIsNone(c.hp_correction.heating_therms)
        self.assertIsNone(c.hp_correction.gas_thermostat_savings)
        self.assertIsNone(c.hp_correction.heating_kwh)
        self.assertIsNone(c.hp_correction.electric_thermostat_savings)
        self.assertIsNone(c.hp_correction.cooling_kwh)
        self.assertIsNone(c.hp_correction.cooling_thermostat_savings)
        self.assertIsNone(c.hp_correction.hot_water_therms)
        self.assertIsNone(c.hp_correction.hot_water_kwh)
        self.assertIsNone(c.hp_correction.lights_and_appliance_therms)
        self.assertIsNone(c.hp_correction.lights_and_appliance_kwh)
        self.assertIsNone(c.hp_correction.fireplace_therms)
        self.assertIsNone(c.hp_correction.solar_hot_water_therms)
        self.assertIsNone(c.hp_correction.solar_hot_water_kwh)
        self.assertIsNone(c.hp_correction.pv_kwh)
        self.assertAlmostEqual(c.hp_fuel_weight.heating_therms, 18.1, 4)
        self.assertIsNone(c.hp_fuel_weight.gas_thermostat_savings)
        self.assertAlmostEqual(c.hp_fuel_weight.heating_kwh, 1218.3, 4)
        self.assertAlmostEqual(c.hp_fuel_weight.electric_thermostat_savings, 4008.207, 4)
        self.assertAlmostEqual(c.hp_fuel_weight.cooling_kwh, 2356.4, 4)
        self.assertIsNone(c.hp_fuel_weight.cooling_thermostat_savings)
        self.assertEqual(c.hp_fuel_weight.hot_water_therms, 0)
        self.assertEqual(c.hp_fuel_weight.hot_water_kwh, 0)
        self.assertAlmostEqual(c.hp_fuel_weight.lights_and_appliance_therms, 4.8, 4)
        self.assertAlmostEqual(c.hp_fuel_weight.lights_and_appliance_kwh, 1387.43, 4)
        self.assertAlmostEqual(c.hp_fuel_weight.fireplace_therms, 88.5, 4)
        self.assertAlmostEqual(c.hp_fuel_weight.solar_hot_water_therms, 1.3, 4)
        self.assertAlmostEqual(c.hp_fuel_weight.solar_hot_water_kwh, 1.4, 4)
        self.assertEqual(c.hp_fuel_weight.pv_kwh, 0)
        self.assertAlmostEqual(c.gas_fuel_weight_eps.total_therms, 112.7, 4)
        self.assertAlmostEqual(c.gas_fuel_weight_eps.total_kwh, 4963.53, 4)
        self.assertAlmostEqual(c.gas_fuel_weight_eps.total_mbtu, 28.2063, 4)
        self.assertAlmostEqual(c.hp_fuel_weight_eps.total_therms, 112.7, 4)
        self.assertAlmostEqual(c.hp_fuel_weight_eps.total_kwh, 7754.039, 4)
        self.assertAlmostEqual(c.hp_fuel_weight_eps.total_mbtu, 37.7279, 4)
        self.assertAlmostEqual(c.unadjusted_carbon.total_therms, 0.6593, 4)
        self.assertAlmostEqual(c.unadjusted_carbon.total_kwh, 2.7051, 4)
        self.assertAlmostEqual(c.unadjusted_carbon.carbon_score, 3.3644, 4)
        self.assertAlmostEqual(c.hp_correction_carbon.total_therms, 0.6593, 4)
        self.assertAlmostEqual(c.hp_correction_carbon.total_kwh, 2.7051, 4)
        self.assertAlmostEqual(c.hp_correction_carbon.carbon_score, 3.3644, 4)
        self.assertAlmostEqual(c.unadjusted_consumption.total_therms, 130.2, 4)
        self.assertAlmostEqual(c.unadjusted_consumption.total_kwh, 5934.86, 4)
        self.assertAlmostEqual(c.unadjusted_consumption.total_mbtu, 33.2706, 4)
        self.assertAlmostEqual(c.hp_correction_consumption.total_therms, 130.2, 4)
        self.assertAlmostEqual(c.hp_correction_consumption.total_kwh, 5934.86, 4)
        self.assertAlmostEqual(c.hp_correction_consumption.total_mbtu, 33.2706, 4)

    def test_solar_high_pv_power(self):
        input_data = {
            "heating_therms": 18.1,
            "heating_kwh": 1223.3,
            "cooling_kwh": 2356.4,
            "hot_water_therms": 18.799999999,
            "hot_water_kwh": 967.73,
            "solar_hot_water_therms": 1.3,
            "solar_hot_water_kwh": 1.4,
            "lights_and_appliance_therms": 4.8,
            "lights_and_appliance_kwh": 1387.43,
            "pv_kwh": 100000,
            "fireplace": Fireplace2020.FE_50_59,
            "thermostat": QualifyingThermostat.DUCTED_FURNACE,
            "heat_type": HeatType.ELECTRIC,
            "constants": Constants(ElectricUtility.PACIFIC_POWER, PNWUSStates.WA),
            "us_state": PNWUSStates.WA,
        }

        c = ImprovedCalculation(**input_data)
        # self.dump_assertions(c)

        self.assertAlmostEqual(c.unadjusted.heating_therms, 18.1, 4)
        self.assertAlmostEqual(c.unadjusted.gas_thermostat_savings, 0.0, 4)
        self.assertAlmostEqual(c.unadjusted.heating_kwh, 1223.3, 4)
        self.assertEqual(c.unadjusted.electric_thermostat_savings, 0)
        self.assertAlmostEqual(c.unadjusted.cooling_kwh, 2356.4, 4)
        self.assertEqual(c.unadjusted.cooling_thermostat_savings, 0)
        self.assertAlmostEqual(c.unadjusted.hot_water_therms, 18.8, 4)
        self.assertAlmostEqual(c.unadjusted.hot_water_kwh, 967.73, 4)
        self.assertAlmostEqual(c.unadjusted.lights_and_appliance_therms, 4.8, 4)
        self.assertAlmostEqual(c.unadjusted.lights_and_appliance_kwh, 1387.43, 4)
        self.assertAlmostEqual(c.unadjusted.fireplace_therms, 88.5, 4)
        self.assertAlmostEqual(c.unadjusted.solar_hot_water_therms, 1.3, 4)
        self.assertAlmostEqual(c.unadjusted.solar_hot_water_kwh, 1.4, 4)
        self.assertEqual(c.unadjusted.pv_kwh, 100000)
        self.assertAlmostEqual(c.gas_fuel_weight.heating_therms, 18.1, 4)
        self.assertIsNone(c.gas_fuel_weight.gas_thermostat_savings)
        self.assertAlmostEqual(c.gas_fuel_weight.heating_kwh, 1223.3, 4)
        self.assertIsNone(c.gas_fuel_weight.electric_thermostat_savings)
        self.assertAlmostEqual(c.gas_fuel_weight.cooling_kwh, 2356.4, 4)
        self.assertIsNone(c.gas_fuel_weight.cooling_thermostat_savings)
        self.assertEqual(c.gas_fuel_weight.hot_water_therms, 0)
        self.assertEqual(c.gas_fuel_weight.hot_water_kwh, 0)
        self.assertAlmostEqual(c.gas_fuel_weight.lights_and_appliance_therms, 4.8, 4)
        self.assertAlmostEqual(c.gas_fuel_weight.lights_and_appliance_kwh, 1387.43, 4)
        self.assertAlmostEqual(c.gas_fuel_weight.fireplace_therms, 88.5, 4)
        self.assertAlmostEqual(c.gas_fuel_weight.solar_hot_water_therms, 1.3, 4)
        self.assertEqual(c.gas_fuel_weight.solar_hot_water_kwh, 0)
        self.assertAlmostEqual(c.gas_fuel_weight.pv_kwh, 99998.6, 4)
        self.assertIsNone(c.hp_correction.heating_therms)
        self.assertIsNone(c.hp_correction.gas_thermostat_savings)
        self.assertIsNone(c.hp_correction.heating_kwh)
        self.assertIsNone(c.hp_correction.electric_thermostat_savings)
        self.assertIsNone(c.hp_correction.cooling_kwh)
        self.assertIsNone(c.hp_correction.cooling_thermostat_savings)
        self.assertIsNone(c.hp_correction.hot_water_therms)
        self.assertIsNone(c.hp_correction.hot_water_kwh)
        self.assertIsNone(c.hp_correction.lights_and_appliance_therms)
        self.assertIsNone(c.hp_correction.lights_and_appliance_kwh)
        self.assertIsNone(c.hp_correction.fireplace_therms)
        self.assertIsNone(c.hp_correction.solar_hot_water_therms)
        self.assertIsNone(c.hp_correction.solar_hot_water_kwh)
        self.assertIsNone(c.hp_correction.pv_kwh)
        self.assertAlmostEqual(c.hp_fuel_weight.heating_therms, 18.1, 4)
        self.assertIsNone(c.hp_fuel_weight.gas_thermostat_savings)
        self.assertEqual(c.hp_fuel_weight.heating_kwh, 0)
        self.assertAlmostEqual(c.hp_fuel_weight.electric_thermostat_savings, -324975.343, 4)
        self.assertAlmostEqual(c.hp_fuel_weight.cooling_kwh, 2356.4, 4)
        self.assertIsNone(c.hp_fuel_weight.cooling_thermostat_savings)
        self.assertEqual(c.hp_fuel_weight.hot_water_therms, 0)
        self.assertEqual(c.hp_fuel_weight.hot_water_kwh, 0)
        self.assertAlmostEqual(c.hp_fuel_weight.lights_and_appliance_therms, 4.8, 4)
        self.assertAlmostEqual(c.hp_fuel_weight.lights_and_appliance_kwh, 1387.43, 4)
        self.assertAlmostEqual(c.hp_fuel_weight.fireplace_therms, 88.5, 4)
        self.assertAlmostEqual(c.hp_fuel_weight.solar_hot_water_therms, 1.3, 4)
        self.assertEqual(c.hp_fuel_weight.solar_hot_water_kwh, 0)
        self.assertAlmostEqual(c.hp_fuel_weight.pv_kwh, 98775.3, 4)
        self.assertAlmostEqual(c.gas_fuel_weight_eps.total_therms, 112.7, 4)
        self.assertAlmostEqual(c.gas_fuel_weight_eps.total_kwh, -95031.47, 4)
        self.assertAlmostEqual(c.gas_fuel_weight_eps.total_mbtu, -312.9909, 4)
        self.assertAlmostEqual(c.hp_fuel_weight_eps.total_therms, 112.7, 4)
        self.assertAlmostEqual(c.hp_fuel_weight_eps.total_kwh, -95031.47, 4)
        self.assertAlmostEqual(c.hp_fuel_weight_eps.total_mbtu, -312.9909, 4)
        self.assertAlmostEqual(c.unadjusted_carbon.total_therms, 0.6593, 4)
        self.assertAlmostEqual(c.unadjusted_carbon.total_kwh, -51.7922, 4)
        self.assertAlmostEqual(c.unadjusted_carbon.carbon_score, -51.1329, 4)
        self.assertAlmostEqual(c.hp_correction_carbon.total_therms, 0.6593, 4)
        self.assertAlmostEqual(c.hp_correction_carbon.total_kwh, -51.7922, 4)
        self.assertAlmostEqual(c.hp_correction_carbon.carbon_score, -51.1329, 4)
        self.assertAlmostEqual(c.unadjusted_consumption.total_therms, 130.2, 4)
        self.assertAlmostEqual(c.unadjusted_consumption.total_kwh, 5934.86, 4)
        self.assertAlmostEqual(c.unadjusted_consumption.total_mbtu, 33.2706, 4)
        self.assertAlmostEqual(c.hp_correction_consumption.total_therms, 130.2, 4)
        self.assertAlmostEqual(c.hp_correction_consumption.total_kwh, 5934.86, 4)
        self.assertAlmostEqual(c.hp_correction_consumption.total_mbtu, 33.2706, 4)

    def test_no_solar_high_pv_power(self):
        input_data = {
            "heating_therms": 18.1,
            "heating_kwh": 1223.3,
            "cooling_kwh": 2356.4,
            "hot_water_therms": 18.799999999,
            "hot_water_kwh": 967.73,
            "solar_hot_water_therms": 0,
            "solar_hot_water_kwh": 0,
            "lights_and_appliance_therms": 4.8,
            "lights_and_appliance_kwh": 1387.43,
            "pv_kwh": 100000,
            "fireplace": Fireplace2020.FE_50_59,
            "thermostat": QualifyingThermostat.DUCTED_FURNACE,
            "heat_type": HeatType.ELECTRIC,
            "constants": Constants(ElectricUtility.PACIFIC_POWER, PNWUSStates.WA),
        }
        c = ImprovedCalculation(**input_data)
        # self.dump_assertions(c)

        self.assertAlmostEqual(c.unadjusted.heating_therms, 18.1, 4)
        self.assertAlmostEqual(c.unadjusted.gas_thermostat_savings, 0.0, 4)
        self.assertAlmostEqual(c.unadjusted.heating_kwh, 1223.3, 4)
        self.assertAlmostEqual(c.unadjusted.electric_thermostat_savings, 0.0, 4)
        self.assertAlmostEqual(c.unadjusted.cooling_kwh, 2356.4, 4)
        self.assertAlmostEqual(c.unadjusted.cooling_thermostat_savings, 0.0, 4)
        self.assertAlmostEqual(c.unadjusted.hot_water_therms, 18.8, 4)
        self.assertAlmostEqual(c.unadjusted.hot_water_kwh, 967.73, 4)
        self.assertAlmostEqual(c.unadjusted.lights_and_appliance_therms, 4.8, 4)
        self.assertAlmostEqual(c.unadjusted.lights_and_appliance_kwh, 1387.43, 4)
        self.assertAlmostEqual(c.unadjusted.fireplace_therms, 88.5, 4)
        self.assertEqual(c.unadjusted.solar_hot_water_therms, 0)
        self.assertEqual(c.unadjusted.solar_hot_water_kwh, 0)
        self.assertEqual(c.unadjusted.pv_kwh, 100000)
        self.assertAlmostEqual(c.gas_fuel_weight.heating_therms, 18.1, 4)
        self.assertIsNone(c.gas_fuel_weight.gas_thermostat_savings)
        self.assertAlmostEqual(c.gas_fuel_weight.heating_kwh, 1223.3, 4)
        self.assertIsNone(c.gas_fuel_weight.electric_thermostat_savings)
        self.assertAlmostEqual(c.gas_fuel_weight.cooling_kwh, 2356.4, 4)
        self.assertIsNone(c.gas_fuel_weight.cooling_thermostat_savings)
        self.assertAlmostEqual(c.gas_fuel_weight.hot_water_therms, 18.8, 4)
        self.assertEqual(c.gas_fuel_weight.hot_water_kwh, 0)
        self.assertAlmostEqual(c.gas_fuel_weight.lights_and_appliance_therms, 4.8, 4)
        self.assertAlmostEqual(c.gas_fuel_weight.lights_and_appliance_kwh, 1387.43, 4)
        self.assertAlmostEqual(c.gas_fuel_weight.fireplace_therms, 88.5, 4)
        self.assertEqual(c.gas_fuel_weight.solar_hot_water_therms, 0)
        self.assertEqual(c.gas_fuel_weight.solar_hot_water_kwh, 0)
        self.assertAlmostEqual(c.gas_fuel_weight.pv_kwh, 99032.27, 4)
        self.assertIsNone(c.hp_correction.heating_therms)
        self.assertIsNone(c.hp_correction.gas_thermostat_savings)
        self.assertIsNone(c.hp_correction.heating_kwh)
        self.assertIsNone(c.hp_correction.electric_thermostat_savings)
        self.assertIsNone(c.hp_correction.cooling_kwh)
        self.assertIsNone(c.hp_correction.cooling_thermostat_savings)
        self.assertIsNone(c.hp_correction.hot_water_therms)
        self.assertIsNone(c.hp_correction.hot_water_kwh)
        self.assertIsNone(c.hp_correction.lights_and_appliance_therms)
        self.assertIsNone(c.hp_correction.lights_and_appliance_kwh)
        self.assertIsNone(c.hp_correction.fireplace_therms)
        self.assertIsNone(c.hp_correction.solar_hot_water_therms)
        self.assertIsNone(c.hp_correction.solar_hot_water_kwh)
        self.assertIsNone(c.hp_correction.pv_kwh)
        self.assertAlmostEqual(c.hp_fuel_weight.heating_therms, 18.1, 4)
        self.assertIsNone(c.hp_fuel_weight.gas_thermostat_savings)
        self.assertEqual(c.hp_fuel_weight.heating_kwh, 0)
        self.assertAlmostEqual(c.hp_fuel_weight.electric_thermostat_savings, -324975.343, 4)
        self.assertAlmostEqual(c.hp_fuel_weight.cooling_kwh, 2356.4, 4)
        self.assertIsNone(c.hp_fuel_weight.cooling_thermostat_savings)
        self.assertAlmostEqual(c.hp_fuel_weight.hot_water_therms, 18.8, 4)
        self.assertEqual(c.hp_fuel_weight.hot_water_kwh, 0)
        self.assertAlmostEqual(c.hp_fuel_weight.lights_and_appliance_therms, 4.8, 4)
        self.assertAlmostEqual(c.hp_fuel_weight.lights_and_appliance_kwh, 1387.43, 4)
        self.assertAlmostEqual(c.hp_fuel_weight.fireplace_therms, 88.5, 4)
        self.assertEqual(c.hp_fuel_weight.solar_hot_water_therms, 0)
        self.assertEqual(c.hp_fuel_weight.solar_hot_water_kwh, 0)
        self.assertAlmostEqual(c.hp_fuel_weight.pv_kwh, 97808.97, 4)
        self.assertAlmostEqual(c.gas_fuel_weight_eps.total_therms, 130.2, 4)
        self.assertAlmostEqual(c.gas_fuel_weight_eps.total_kwh, -94065.14, 4)
        self.assertAlmostEqual(c.gas_fuel_weight_eps.total_mbtu, -307.9437, 4)
        self.assertAlmostEqual(c.hp_fuel_weight_eps.total_therms, 130.2, 4)
        self.assertAlmostEqual(c.hp_fuel_weight_eps.total_kwh, -94065.14, 4)
        self.assertAlmostEqual(c.hp_fuel_weight_eps.total_mbtu, -307.9437, 4)
        self.assertAlmostEqual(c.unadjusted_carbon.total_therms, 0.7617, 4)
        self.assertAlmostEqual(c.unadjusted_carbon.total_kwh, -51.2655, 4)
        self.assertAlmostEqual(c.unadjusted_carbon.carbon_score, -50.5038, 4)
        self.assertAlmostEqual(c.hp_correction_carbon.total_therms, 0.7617, 4)
        self.assertAlmostEqual(c.hp_correction_carbon.total_kwh, -51.2655, 4)
        self.assertAlmostEqual(c.hp_correction_carbon.carbon_score, -50.5038, 4)
        self.assertAlmostEqual(c.unadjusted_consumption.total_therms, 130.2, 4)
        self.assertAlmostEqual(c.unadjusted_consumption.total_kwh, 5934.86, 4)
        self.assertAlmostEqual(c.unadjusted_consumption.total_mbtu, 33.2706, 4)
        self.assertAlmostEqual(c.hp_correction_consumption.total_therms, 130.2, 4)
        self.assertAlmostEqual(c.hp_correction_consumption.total_kwh, 5934.86, 4)
        self.assertAlmostEqual(c.hp_correction_consumption.total_mbtu, 33.2706, 4)

    def test_no_solar_no_pv_power(self):
        input_data = {
            "heating_therms": 18.1,
            "heating_kwh": 1223.3,
            "cooling_kwh": 2356.4,
            "hot_water_therms": 18.799999999,
            "hot_water_kwh": 967.73,
            "solar_hot_water_therms": 0,
            "solar_hot_water_kwh": 0,
            "lights_and_appliance_therms": 4.8,
            "lights_and_appliance_kwh": 1387.43,
            "pv_kwh": 0,
            "fireplace": Fireplace2020.FE_50_59,
            "thermostat": QualifyingThermostat.DUCTED_FURNACE,
            "heat_type": HeatType.ELECTRIC,
            "constants": Constants(ElectricUtility.PACIFIC_POWER, PNWUSStates.WA),
            "us_state": PNWUSStates.WA,
        }
        c = ImprovedCalculation(**input_data)
        # self.dump_assertions(c)

        self.assertAlmostEqual(c.unadjusted.heating_therms, 18.1, 4)
        self.assertAlmostEqual(c.unadjusted.gas_thermostat_savings, 0.0, 4)
        self.assertAlmostEqual(c.unadjusted.heating_kwh, 1223.3, 4)
        self.assertEqual(c.unadjusted.electric_thermostat_savings, 0)
        self.assertAlmostEqual(c.unadjusted.cooling_kwh, 2356.4, 4)
        self.assertEqual(c.unadjusted.cooling_thermostat_savings, 0)
        self.assertAlmostEqual(c.unadjusted.hot_water_therms, 18.8, 4)
        self.assertAlmostEqual(c.unadjusted.hot_water_kwh, 967.73, 4)
        self.assertAlmostEqual(c.unadjusted.lights_and_appliance_therms, 4.8, 4)
        self.assertAlmostEqual(c.unadjusted.lights_and_appliance_kwh, 1387.43, 4)
        self.assertAlmostEqual(c.unadjusted.fireplace_therms, 88.5, 4)
        self.assertEqual(c.unadjusted.solar_hot_water_therms, 0)
        self.assertEqual(c.unadjusted.solar_hot_water_kwh, 0)
        self.assertEqual(c.unadjusted.pv_kwh, 0)
        self.assertAlmostEqual(c.gas_fuel_weight.heating_therms, 18.1, 4)
        self.assertIsNone(c.gas_fuel_weight.gas_thermostat_savings)
        self.assertAlmostEqual(c.gas_fuel_weight.heating_kwh, 1223.3, 4)
        self.assertIsNone(c.gas_fuel_weight.electric_thermostat_savings)
        self.assertAlmostEqual(c.gas_fuel_weight.cooling_kwh, 2356.4, 4)
        self.assertIsNone(c.gas_fuel_weight.cooling_thermostat_savings)
        self.assertAlmostEqual(c.gas_fuel_weight.hot_water_therms, 18.8, 4)
        self.assertAlmostEqual(c.gas_fuel_weight.hot_water_kwh, 967.73, 4)
        self.assertAlmostEqual(c.gas_fuel_weight.lights_and_appliance_therms, 4.8, 4)
        self.assertAlmostEqual(c.gas_fuel_weight.lights_and_appliance_kwh, 1387.43, 4)
        self.assertAlmostEqual(c.gas_fuel_weight.fireplace_therms, 88.5, 4)
        self.assertEqual(c.gas_fuel_weight.solar_hot_water_therms, 0)
        self.assertEqual(c.gas_fuel_weight.solar_hot_water_kwh, 0)
        self.assertEqual(c.gas_fuel_weight.pv_kwh, 0)
        self.assertIsNone(c.hp_correction.heating_therms)
        self.assertIsNone(c.hp_correction.gas_thermostat_savings)
        self.assertIsNone(c.hp_correction.heating_kwh)
        self.assertIsNone(c.hp_correction.electric_thermostat_savings)
        self.assertIsNone(c.hp_correction.cooling_kwh)
        self.assertIsNone(c.hp_correction.cooling_thermostat_savings)
        self.assertIsNone(c.hp_correction.hot_water_therms)
        self.assertIsNone(c.hp_correction.hot_water_kwh)
        self.assertIsNone(c.hp_correction.lights_and_appliance_therms)
        self.assertIsNone(c.hp_correction.lights_and_appliance_kwh)
        self.assertIsNone(c.hp_correction.fireplace_therms)
        self.assertIsNone(c.hp_correction.solar_hot_water_therms)
        self.assertIsNone(c.hp_correction.solar_hot_water_kwh)
        self.assertIsNone(c.hp_correction.pv_kwh)
        self.assertAlmostEqual(c.hp_fuel_weight.heating_therms, 18.1, 4)
        self.assertIsNone(c.hp_fuel_weight.gas_thermostat_savings)
        self.assertAlmostEqual(c.hp_fuel_weight.heating_kwh, 1223.3, 4)
        self.assertAlmostEqual(c.hp_fuel_weight.electric_thermostat_savings, 4024.657, 4)
        self.assertAlmostEqual(c.hp_fuel_weight.cooling_kwh, 2356.4, 4)
        self.assertIsNone(c.hp_fuel_weight.cooling_thermostat_savings)
        self.assertAlmostEqual(c.hp_fuel_weight.hot_water_therms, 18.8, 4)
        self.assertAlmostEqual(c.hp_fuel_weight.hot_water_kwh, 967.73, 4)
        self.assertAlmostEqual(c.hp_fuel_weight.lights_and_appliance_therms, 4.8, 4)
        self.assertAlmostEqual(c.hp_fuel_weight.lights_and_appliance_kwh, 1387.43, 4)
        self.assertAlmostEqual(c.hp_fuel_weight.fireplace_therms, 88.5, 4)
        self.assertEqual(c.hp_fuel_weight.solar_hot_water_therms, 0)
        self.assertEqual(c.hp_fuel_weight.solar_hot_water_kwh, 0)
        self.assertEqual(c.hp_fuel_weight.pv_kwh, 0)
        self.assertAlmostEqual(c.gas_fuel_weight_eps.total_therms, 130.2, 4)
        self.assertAlmostEqual(c.gas_fuel_weight_eps.total_kwh, 6350.9839, 4)
        self.assertAlmostEqual(c.gas_fuel_weight_eps.total_mbtu, 34.6905, 4)
        self.assertAlmostEqual(c.hp_fuel_weight_eps.total_therms, 130.2, 4)
        self.assertAlmostEqual(c.hp_fuel_weight_eps.total_kwh, 9152.3409, 4)
        self.assertAlmostEqual(c.hp_fuel_weight_eps.total_mbtu, 44.2491, 4)
        self.assertAlmostEqual(c.unadjusted_carbon.total_therms, 0.7617, 4)
        self.assertAlmostEqual(c.unadjusted_carbon.total_kwh, 3.2345, 4)
        self.assertAlmostEqual(c.unadjusted_carbon.carbon_score, 3.9962, 4)
        self.assertAlmostEqual(c.hp_correction_carbon.total_therms, 0.7617, 4)
        self.assertAlmostEqual(c.hp_correction_carbon.total_kwh, 3.2345, 4)
        self.assertAlmostEqual(c.hp_correction_carbon.carbon_score, 3.9962, 4)
        self.assertAlmostEqual(c.unadjusted_consumption.total_therms, 130.2, 4)
        self.assertAlmostEqual(c.unadjusted_consumption.total_kwh, 5934.86, 4)
        self.assertAlmostEqual(c.unadjusted_consumption.total_mbtu, 33.2706, 4)
        self.assertAlmostEqual(c.hp_correction_consumption.total_therms, 130.2, 4)
        self.assertAlmostEqual(c.hp_correction_consumption.total_kwh, 5934.86, 4)
        self.assertAlmostEqual(c.hp_correction_consumption.total_mbtu, 33.2706, 4)

    def test_no_solar_no_pv_no_tstat_power(self):
        input_data = {
            "heating_therms": 18.1,
            "heating_kwh": 1223.3,
            "cooling_kwh": 2356.4,
            "hot_water_therms": 18.799999999,
            "hot_water_kwh": 967.73,
            "solar_hot_water_therms": 0,
            "solar_hot_water_kwh": 0,
            "lights_and_appliance_therms": 4.8,
            "lights_and_appliance_kwh": 1387.43,
            "pv_kwh": 0,
            "fireplace": Fireplace2020.NONE,
            "thermostat": QualifyingThermostat.NONE,
            "heat_type": HeatType.ELECTRIC,
            "constants": Constants(ElectricUtility.NONE, PNWUSStates.WA),
        }
        c = ImprovedCalculation(**input_data)
        # self.dump_assertions(c)

        self.assertAlmostEqual(c.unadjusted.heating_therms, 18.1, 4)
        self.assertAlmostEqual(c.unadjusted.gas_thermostat_savings, 0.0, 4)
        self.assertAlmostEqual(c.unadjusted.heating_kwh, 1223.3, 4)
        self.assertAlmostEqual(c.unadjusted.electric_thermostat_savings, 0.0, 4)
        self.assertAlmostEqual(c.unadjusted.cooling_kwh, 2356.4, 4)
        self.assertAlmostEqual(c.unadjusted.cooling_thermostat_savings, 0.0, 4)
        self.assertAlmostEqual(c.unadjusted.hot_water_therms, 18.8, 4)
        self.assertAlmostEqual(c.unadjusted.hot_water_kwh, 967.73, 4)
        self.assertAlmostEqual(c.unadjusted.lights_and_appliance_therms, 4.8, 4)
        self.assertAlmostEqual(c.unadjusted.lights_and_appliance_kwh, 1387.43, 4)
        self.assertEqual(c.unadjusted.fireplace_therms, 0)
        self.assertEqual(c.unadjusted.solar_hot_water_therms, 0)
        self.assertEqual(c.unadjusted.solar_hot_water_kwh, 0)
        self.assertEqual(c.unadjusted.pv_kwh, 0)
        self.assertAlmostEqual(c.gas_fuel_weight.heating_therms, 18.1, 4)
        self.assertIsNone(c.gas_fuel_weight.gas_thermostat_savings)
        self.assertAlmostEqual(c.gas_fuel_weight.heating_kwh, 1223.3, 4)
        self.assertIsNone(c.gas_fuel_weight.electric_thermostat_savings)
        self.assertAlmostEqual(c.gas_fuel_weight.cooling_kwh, 2356.4, 4)
        self.assertIsNone(c.gas_fuel_weight.cooling_thermostat_savings)
        self.assertAlmostEqual(c.gas_fuel_weight.hot_water_therms, 18.8, 4)
        self.assertAlmostEqual(c.gas_fuel_weight.hot_water_kwh, 967.73, 4)
        self.assertAlmostEqual(c.gas_fuel_weight.lights_and_appliance_therms, 4.8, 4)
        self.assertAlmostEqual(c.gas_fuel_weight.lights_and_appliance_kwh, 1387.43, 4)
        self.assertEqual(c.gas_fuel_weight.fireplace_therms, 0)
        self.assertEqual(c.gas_fuel_weight.solar_hot_water_therms, 0)
        self.assertEqual(c.gas_fuel_weight.solar_hot_water_kwh, 0)
        self.assertEqual(c.gas_fuel_weight.pv_kwh, 0)
        self.assertIsNone(c.hp_correction.heating_therms)
        self.assertIsNone(c.hp_correction.gas_thermostat_savings)
        self.assertIsNone(c.hp_correction.heating_kwh)
        self.assertIsNone(c.hp_correction.electric_thermostat_savings)
        self.assertIsNone(c.hp_correction.cooling_kwh)
        self.assertIsNone(c.hp_correction.cooling_thermostat_savings)
        self.assertIsNone(c.hp_correction.hot_water_therms)
        self.assertIsNone(c.hp_correction.hot_water_kwh)
        self.assertIsNone(c.hp_correction.lights_and_appliance_therms)
        self.assertIsNone(c.hp_correction.lights_and_appliance_kwh)
        self.assertIsNone(c.hp_correction.fireplace_therms)
        self.assertIsNone(c.hp_correction.solar_hot_water_therms)
        self.assertIsNone(c.hp_correction.solar_hot_water_kwh)
        self.assertIsNone(c.hp_correction.pv_kwh)
        self.assertAlmostEqual(c.hp_fuel_weight.heating_therms, 18.1, 4)
        self.assertIsNone(c.hp_fuel_weight.gas_thermostat_savings)
        self.assertAlmostEqual(c.hp_fuel_weight.heating_kwh, 1223.3, 4)
        self.assertAlmostEqual(c.hp_fuel_weight.electric_thermostat_savings, 4024.657, 4)
        self.assertAlmostEqual(c.hp_fuel_weight.cooling_kwh, 2356.4, 4)
        self.assertIsNone(c.hp_fuel_weight.cooling_thermostat_savings)
        self.assertAlmostEqual(c.hp_fuel_weight.hot_water_therms, 18.8, 4)
        self.assertAlmostEqual(c.hp_fuel_weight.hot_water_kwh, 967.73, 4)
        self.assertAlmostEqual(c.hp_fuel_weight.lights_and_appliance_therms, 4.8, 4)
        self.assertAlmostEqual(c.hp_fuel_weight.lights_and_appliance_kwh, 1387.43, 4)
        self.assertEqual(c.hp_fuel_weight.fireplace_therms, 0)
        self.assertEqual(c.hp_fuel_weight.solar_hot_water_therms, 0)
        self.assertEqual(c.hp_fuel_weight.solar_hot_water_kwh, 0)
        self.assertEqual(c.hp_fuel_weight.pv_kwh, 0)
        self.assertAlmostEqual(c.gas_fuel_weight_eps.total_therms, 41.7, 4)
        self.assertAlmostEqual(c.gas_fuel_weight_eps.total_kwh, 6350.9839, 4)
        self.assertAlmostEqual(c.gas_fuel_weight_eps.total_mbtu, 25.8405, 4)
        self.assertAlmostEqual(c.hp_fuel_weight_eps.total_therms, 41.7, 4)
        self.assertAlmostEqual(c.hp_fuel_weight_eps.total_kwh, 9152.3409, 4)
        self.assertAlmostEqual(c.hp_fuel_weight_eps.total_mbtu, 35.3991, 4)
        self.assertAlmostEqual(c.unadjusted_carbon.total_therms, 0.2439, 4)
        self.assertAlmostEqual(c.unadjusted_carbon.total_kwh, 0.1988, 4)
        self.assertAlmostEqual(c.unadjusted_carbon.carbon_score, 0.4428, 4)
        self.assertAlmostEqual(c.hp_correction_carbon.total_therms, 0.2439, 4)
        self.assertAlmostEqual(c.hp_correction_carbon.total_kwh, 0.1988, 4)
        self.assertAlmostEqual(c.hp_correction_carbon.carbon_score, 0.4428, 4)
        self.assertAlmostEqual(c.unadjusted_consumption.total_therms, 41.7, 4)
        self.assertAlmostEqual(c.unadjusted_consumption.total_kwh, 5934.86, 4)
        self.assertAlmostEqual(c.unadjusted_consumption.total_mbtu, 24.4206, 4)
        self.assertAlmostEqual(c.hp_correction_consumption.total_therms, 41.7, 4)
        self.assertAlmostEqual(c.hp_correction_consumption.total_kwh, 5934.86, 4)
        self.assertAlmostEqual(c.hp_correction_consumption.total_mbtu, 24.4206, 4)

    def test_wa_no_solar_no_pv_no_tstat_power(self):
        input_data = {
            "heating_therms": 18.1,
            "heating_kwh": 1223.3,
            "cooling_kwh": 2356.4,
            "hot_water_therms": 18.799999999,
            "hot_water_kwh": 967.73,
            "solar_hot_water_therms": 0,
            "solar_hot_water_kwh": 0,
            "lights_and_appliance_therms": 4.8,
            "lights_and_appliance_kwh": 1387.43,
            "pv_kwh": 0,
            "fireplace": Fireplace2020.NONE,
            "thermostat": QualifyingThermostat.NONE,
            "heat_type": HeatType.ELECTRIC,
            "constants": Constants(ElectricUtility.NONE, PNWUSStates.WA),
            "us_state": PNWUSStates.WA,
        }
        c = ImprovedCalculation(**input_data)
        # self.dump_assertions(c)
        self.assertEqual(round(c.unadjusted.heating_therms, 4), 18.1)
        self.assertEqual(round(c.unadjusted.gas_thermostat_savings, 4), 0)
        self.assertEqual(round(c.unadjusted.heating_kwh, 4), 1223.3)
        self.assertEqual(round(c.unadjusted.electric_thermostat_savings, 4), 0)
        self.assertEqual(round(c.unadjusted.cooling_kwh, 4), 2356.4)
        self.assertEqual(round(c.unadjusted.cooling_thermostat_savings, 4), 0.0)
        self.assertEqual(round(c.unadjusted.hot_water_therms, 4), 18.8)
        self.assertEqual(round(c.unadjusted.hot_water_kwh, 4), 967.73)
        self.assertEqual(round(c.unadjusted.lights_and_appliance_therms, 4), 4.8)
        self.assertEqual(round(c.unadjusted.lights_and_appliance_kwh, 4), 1387.43)
        self.assertEqual(round(c.unadjusted.fireplace_therms, 4), 0)
        self.assertEqual(round(c.unadjusted.solar_hot_water_therms, 4), 0)
        self.assertEqual(round(c.unadjusted.solar_hot_water_kwh, 4), 0)
        self.assertEqual(round(c.unadjusted.pv_kwh, 4), 0)
        self.assertEqual(round(c.gas_fuel_weight.heating_therms, 4), 18.1)
        self.assertIsNone(c.gas_fuel_weight.gas_thermostat_savings)
        self.assertEqual(round(c.gas_fuel_weight.heating_kwh, 4), 1223.3)
        self.assertIsNone(c.gas_fuel_weight.electric_thermostat_savings)
        self.assertEqual(round(c.gas_fuel_weight.cooling_kwh, 4), 2356.4)
        self.assertIsNone(c.gas_fuel_weight.cooling_thermostat_savings)
        self.assertEqual(round(c.gas_fuel_weight.hot_water_therms, 4), 18.8)
        self.assertEqual(round(c.gas_fuel_weight.hot_water_kwh, 4), 967.73)
        self.assertEqual(round(c.gas_fuel_weight.lights_and_appliance_therms, 4), 4.8)
        self.assertEqual(round(c.gas_fuel_weight.lights_and_appliance_kwh, 4), 1387.43)
        self.assertEqual(round(c.gas_fuel_weight.fireplace_therms, 4), 0)
        self.assertEqual(round(c.gas_fuel_weight.solar_hot_water_therms, 4), 0)
        self.assertEqual(round(c.gas_fuel_weight.solar_hot_water_kwh, 4), 0)
        self.assertEqual(round(c.gas_fuel_weight.pv_kwh, 4), 0)
        self.assertIsNone(c.hp_correction.heating_therms)
        self.assertIsNone(c.hp_correction.gas_thermostat_savings)
        self.assertIsNone(c.hp_correction.heating_kwh)
        self.assertIsNone(c.hp_correction.electric_thermostat_savings)
        self.assertIsNone(c.hp_correction.cooling_kwh)
        self.assertIsNone(c.hp_correction.cooling_thermostat_savings)
        self.assertIsNone(c.hp_correction.hot_water_therms)
        self.assertIsNone(c.hp_correction.hot_water_kwh)
        self.assertIsNone(c.hp_correction.lights_and_appliance_therms)
        self.assertIsNone(c.hp_correction.lights_and_appliance_kwh)
        self.assertIsNone(c.hp_correction.fireplace_therms)
        self.assertIsNone(c.hp_correction.solar_hot_water_therms)
        self.assertIsNone(c.hp_correction.solar_hot_water_kwh)
        self.assertIsNone(c.hp_correction.pv_kwh)
        self.assertEqual(round(c.hp_fuel_weight.heating_therms, 4), 18.1)
        self.assertIsNone(c.hp_fuel_weight.gas_thermostat_savings)
        self.assertEqual(round(c.hp_fuel_weight.heating_kwh, 4), 1223.3)
        self.assertEqual(round(c.hp_fuel_weight.electric_thermostat_savings, 4), 4024.657)
        self.assertEqual(round(c.hp_fuel_weight.cooling_kwh, 4), 2356.4)
        self.assertIsNone(c.hp_fuel_weight.cooling_thermostat_savings)
        self.assertEqual(round(c.hp_fuel_weight.hot_water_therms, 4), 18.8)
        self.assertEqual(round(c.hp_fuel_weight.hot_water_kwh, 4), 967.73)
        self.assertEqual(round(c.hp_fuel_weight.lights_and_appliance_therms, 4), 4.8)
        self.assertEqual(round(c.hp_fuel_weight.lights_and_appliance_kwh, 4), 1387.43)
        self.assertEqual(round(c.hp_fuel_weight.fireplace_therms, 4), 0)
        self.assertEqual(round(c.hp_fuel_weight.solar_hot_water_therms, 4), 0)
        self.assertEqual(round(c.hp_fuel_weight.solar_hot_water_kwh, 4), 0)
        self.assertEqual(round(c.hp_fuel_weight.pv_kwh, 4), 0)
        self.assertEqual(round(c.gas_fuel_weight_eps.total_therms, 4), 41.7)
        self.assertEqual(round(c.gas_fuel_weight_eps.total_kwh, 4), 6350.9839)
        self.assertEqual(round(c.gas_fuel_weight_eps.total_mbtu, 4), 25.8405)
        self.assertEqual(round(c.hp_fuel_weight_eps.total_therms, 4), 41.7)
        self.assertEqual(round(c.hp_fuel_weight_eps.total_kwh, 4), 9152.3409)
        self.assertEqual(round(c.hp_fuel_weight_eps.total_mbtu, 4), 35.3991)
        self.assertEqual(round(c.unadjusted_carbon.total_therms, 4), 0.2439)
        self.assertEqual(round(c.unadjusted_carbon.total_kwh, 4), 0.1988)
        self.assertEqual(round(c.unadjusted_carbon.carbon_score, 4), 0.4428)
        self.assertEqual(round(c.hp_correction_carbon.total_therms, 4), 0.2439)
        self.assertEqual(round(c.hp_correction_carbon.total_kwh, 4), 0.1988)
        self.assertEqual(round(c.hp_correction_carbon.carbon_score, 4), 0.4428)
        self.assertEqual(round(c.unadjusted_consumption.total_therms, 4), 41.7)
        self.assertEqual(round(c.unadjusted_consumption.total_kwh, 4), 5934.86)
        self.assertEqual(round(c.unadjusted_consumption.total_mbtu, 4), 24.4206)
        self.assertEqual(round(c.hp_correction_consumption.total_therms, 4), 41.7)
        self.assertEqual(round(c.hp_correction_consumption.total_kwh, 4), 5934.86)
        self.assertEqual(round(c.hp_correction_consumption.total_mbtu, 4), 24.4206)

    def test_eps_score(self):
        input_data = self.input_data.copy()
        with self.subTest("Gas Heat"):
            input_data["heat_type"] = HeatType.GAS
            c = ImprovedCalculation(**input_data)
            self.assertEqual(c.eps_score, round(c.gas_fuel_weight_eps.total_mbtu))
        with self.subTest("Electric Heat"):
            input_data["heat_type"] = HeatType.ELECTRIC
            c = ImprovedCalculation(**input_data)
            self.assertEqual(c.eps_score, round(c.hp_fuel_weight_eps.total_mbtu))

    def test_carbon_score(self):
        input_data = self.input_data.copy()
        with self.subTest("Gas Heat"):
            input_data["heat_type"] = HeatType.GAS
            c = ImprovedCalculation(**input_data)
            self.assertEqual(c.carbon_score, c.unadjusted_carbon.carbon_score)
        with self.subTest("Electric Heat"):
            input_data["heat_type"] = HeatType.ELECTRIC
            c = ImprovedCalculation(**input_data)
            self.assertEqual(c.carbon_score, c.hp_correction_carbon.carbon_score)

    def test_electric_carbon_score(self):
        input_data = self.input_data.copy()
        with self.subTest("Gas Heat"):
            input_data["heat_type"] = HeatType.GAS
            c = ImprovedCalculation(**input_data)
            self.assertEqual(c.electric_carbon_score, c.unadjusted_carbon.total_kwh)
        with self.subTest("Electric Heat"):
            input_data["heat_type"] = HeatType.ELECTRIC
            c = ImprovedCalculation(**input_data)
            self.assertEqual(c.electric_carbon_score, c.hp_correction_carbon.total_kwh)

    def test_gas_carbon_score(self):
        input_data = self.input_data.copy()
        with self.subTest("Gas Heat"):
            input_data["heat_type"] = HeatType.GAS
            c = ImprovedCalculation(**input_data)
            self.assertEqual(c.gas_carbon_score, c.unadjusted_carbon.total_therms)
        with self.subTest("Electric Heat"):
            input_data["heat_type"] = HeatType.ELECTRIC
            c = ImprovedCalculation(**input_data)
            self.assertEqual(c.gas_carbon_score, c.hp_correction_carbon.total_therms)
