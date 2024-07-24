"""test_ventilation.py - Axis"""

__author__ = "Steven K"
__date__ = "3/17/22 15:33"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
from unittest import mock

from axis.gbr.tests.mocked_responses import gbr_mocked_response
from simulation.enumerations import MechanicalVentilationType, AuxEnergyUnit, VentilationRateUnit
from simulation.tests.factories import simulation_factory

from axis.core.tests.testcases import AxisTestCase
from axis.customer_eto.analytics.ventilation import (
    eto_simulation_exhaust_ventilation_model_characteristics,
    eto_simulation_supply_ventilation_model_characteristics,
    eto_simulation_balanced_ventilation_model_characteristics,
)

log = logging.getLogger(__name__)


class AnalyticsExhaustVentilationTests(AxisTestCase):
    @classmethod
    @mock.patch(
        "axis.gbr.gbr.GreenBuildingRegistryAPIConnect.post", side_effect=gbr_mocked_response
    )
    def setUpTestData(cls, _mock):
        super(AnalyticsExhaustVentilationTests, cls).setUpTestData()
        cls.simulation = simulation_factory(
            mechanical_ventilation_count=1,
            mechanical_ventilation__type=MechanicalVentilationType.EXHAUST_ONLY,
            mechanical_ventilation__consumption=10.2,
            mechanical_ventilation__consumption_unit=AuxEnergyUnit.WATT,
            mechanical_ventilation__ventilation_rate_unit=VentilationRateUnit.CFM,
            mechanical_ventilation__ventilation_rate=25.3,
            mechanical_ventilation__hour_per_day=16.6,
        )
        cls.equipment_ventilation_system_type = {"input": "WA - Exhaust Only"}

    def test_basic_fail_eto_simulation_exhaust_ventilation_model_characteristics(self):
        with self.subTest("Nones"):
            data = eto_simulation_exhaust_ventilation_model_characteristics(None, None, None)
            self.assertEqual(data["model_exhaust_ventilation_characteristics"]["simulation"], None)
            self.assertEqual(data["model_exhaust_ventilation_characteristics"]["checklist"], None)
            self.assertEqual(data["model_exhaust_ventilation_characteristics"]["warning"], None)
            self.assertEqual(data["model_exhaust_ventilation_characteristics"]["warnings"], [])

        with self.subTest("Bad ID"):
            data = eto_simulation_exhaust_ventilation_model_characteristics(-2, None, None)
            self.assertEqual(data["model_exhaust_ventilation_characteristics"]["simulation"], None)
            self.assertEqual(data["model_exhaust_ventilation_characteristics"]["checklist"], None)
            self.assertEqual(data["model_exhaust_ventilation_characteristics"]["warning"], None)
            self.assertEqual(data["model_exhaust_ventilation_characteristics"]["warnings"], [])

        with self.subTest("Wrong Type"):
            self.simulation.mechanical_ventilation_systems.update(
                type=MechanicalVentilationType.ERV
            )
            data = eto_simulation_exhaust_ventilation_model_characteristics(
                self.simulation.id, None, None
            )
            self.assertEqual(data["model_exhaust_ventilation_characteristics"]["simulation"], None)
            self.assertEqual(data["model_exhaust_ventilation_characteristics"]["checklist"], None)
            self.assertEqual(data["model_exhaust_ventilation_characteristics"]["warning"], None)
            self.assertEqual(data["model_exhaust_ventilation_characteristics"]["warnings"], [])

        with self.subTest("Wrong consumption_unit"):
            self.simulation.mechanical_ventilation_systems.update(
                type=MechanicalVentilationType.EXHAUST_ONLY,
                consumption_unit=AuxEnergyUnit.KWH_YEAR,
            )
            data = eto_simulation_exhaust_ventilation_model_characteristics(
                self.simulation.id, None, None
            )
            self.assertEqual(data["model_exhaust_ventilation_characteristics"]["simulation"], None)
            self.assertEqual(data["model_exhaust_ventilation_characteristics"]["checklist"], None)
            self.assertIn("mismatch", data["model_exhaust_ventilation_characteristics"]["warning"])
            self.assertIn("Watts", data["model_exhaust_ventilation_characteristics"]["warnings"][0])

        with self.subTest("Wrong ventilation_rate_unit"):
            self.simulation.mechanical_ventilation_systems.update(
                type=MechanicalVentilationType.EXHAUST_ONLY,
                consumption_unit=AuxEnergyUnit.WATT,
                # The VentilationRateUnit only supports one unit now (which is obviously a valid choice),
                # so we have to manually set an invalid unit instead of using an enum as we usually would
                ventilation_rate_unit="cmm",
            )
            data = eto_simulation_exhaust_ventilation_model_characteristics(
                self.simulation.id, None, self.equipment_ventilation_system_type
            )
            self.assertEqual(data["model_exhaust_ventilation_characteristics"]["simulation"], None)
            self.assertEqual(data["model_exhaust_ventilation_characteristics"]["checklist"], None)
            self.assertIn("mismatch", data["model_exhaust_ventilation_characteristics"]["warning"])
            self.assertIn("CFM", data["model_exhaust_ventilation_characteristics"]["warnings"][0])

    def test_eto_simulation_exhaust_ventilation_model_custom_characteristics(self):
        answer = {
            "hints": {
                "is_custom": True,
                "model_number": {"is_custom": True},
                "characteristics": {"is_custom": True},
            },
            "input": {
                "sp": None,
                "speed_cfm": None,
                "brand_name": "Broan",
                "model_number": "A80-B",
                "input_power_watts": None,
            },
        }

        data = eto_simulation_exhaust_ventilation_model_characteristics(
            self.simulation.id,
            answer,
            self.equipment_ventilation_system_type,
        )
        self.assertIsNotNone(data["model_exhaust_ventilation_characteristics"]["simulation"])
        self.assertIsNotNone(data["model_exhaust_ventilation_characteristics"]["checklist"])
        self.assertIn("mismatch", data["model_exhaust_ventilation_characteristics"]["warning"])
        self.assertIn(" +", data["model_exhaust_ventilation_characteristics"]["warning"])
        self.assertIn("Custom", data["model_exhaust_ventilation_characteristics"]["warnings"][0])
        self.assertEqual(len(data["model_exhaust_ventilation_characteristics"]["warnings"]), 1)

    def test_eto_simulation_exhaust_ventilation_model_mismatch_characteristics(self):
        answer = {
            "input": {
                "sp": "0.1",
                "speed_cfm": "25.4",
                "brand_name": "Panasonic",
                "model_number": "FV-0511VQ1",
                "input_power_watts": "10.2",
            }
        }
        with self.subTest("Bad Rate"):
            data = eto_simulation_exhaust_ventilation_model_characteristics(
                self.simulation.id, answer, self.equipment_ventilation_system_type
            )
            self.assertIsNotNone(data["model_exhaust_ventilation_characteristics"]["simulation"])
            self.assertIsNotNone(data["model_exhaust_ventilation_characteristics"]["checklist"])
            self.assertIn("mismatch", data["model_exhaust_ventilation_characteristics"]["warning"])
            self.assertIn("rate", data["model_exhaust_ventilation_characteristics"]["warnings"][0])
            self.assertEqual(len(data["model_exhaust_ventilation_characteristics"]["warnings"]), 1)

        answer = {
            "input": {
                "sp": "0.1",
                "speed_cfm": "25.3",
                "brand_name": "Panasonic",
                "model_number": "FV-0511VQ1",
                "input_power_watts": "10.3",
            }
        }

        with self.subTest("Bad Power"):
            data = eto_simulation_exhaust_ventilation_model_characteristics(
                self.simulation.id, answer, self.equipment_ventilation_system_type
            )
            self.assertIsNotNone(data["model_exhaust_ventilation_characteristics"]["simulation"])
            self.assertIsNotNone(data["model_exhaust_ventilation_characteristics"]["checklist"])
            self.assertIn("mismatch", data["model_exhaust_ventilation_characteristics"]["warning"])
            self.assertIn("power", data["model_exhaust_ventilation_characteristics"]["warnings"][0])
            self.assertEqual(len(data["model_exhaust_ventilation_characteristics"]["warnings"]), 1)

        answer = {
            "input": {
                "sp": "0.1",
                "speed_cfm": "25.3",
                "brand_name": "Panasonic",
                "model_number": "FV-0511VQ1",
                "input_power_watts": "10.2",
            }
        }

        with self.subTest("Solid pass"):
            data = eto_simulation_exhaust_ventilation_model_characteristics(
                self.simulation.id, answer, self.equipment_ventilation_system_type
            )
            self.assertIsNotNone(data["model_exhaust_ventilation_characteristics"]["simulation"])
            self.assertIsNotNone(data["model_exhaust_ventilation_characteristics"]["checklist"])
            self.assertIsNone(data["model_exhaust_ventilation_characteristics"]["warning"])
            self.assertEqual(len(data["model_exhaust_ventilation_characteristics"]["warnings"]), 0)

    def test_air_cycler(self):
        self.simulation.mechanical_ventilation_systems.update(
            type=MechanicalVentilationType.AIR_CYCLER
        )

        answer = {
            "input": {
                "sp": "0.1",
                "speed_cfm": "25.3",
                "brand_name": "Panasonic",
                "model_number": "FV-0511VQ1",
                "input_power_watts": "10.2",
            }
        }

        data = eto_simulation_exhaust_ventilation_model_characteristics(
            self.simulation.id, answer, self.equipment_ventilation_system_type
        )["model_exhaust_ventilation_characteristics"]
        self.assertIn("25.3", data["checklist"])
        self.assertIn("10.2", data["checklist"])


class AnalyticsSupplyVentilationTests(AxisTestCase):
    @classmethod
    @mock.patch(
        "axis.gbr.gbr.GreenBuildingRegistryAPIConnect.post", side_effect=gbr_mocked_response
    )
    def setUpTestData(cls, _mock):
        super(AnalyticsSupplyVentilationTests, cls).setUpTestData()
        cls.simulation = simulation_factory(
            mechanical_ventilation_count=1,
            mechanical_ventilation__type=MechanicalVentilationType.SUPPLY_ONLY,
            mechanical_ventilation__consumption=10.2,
            mechanical_ventilation__consumption_unit=AuxEnergyUnit.WATT,
            mechanical_ventilation__ventilation_rate_unit=VentilationRateUnit.CFM,
            mechanical_ventilation__ventilation_rate=25.3,
        )

    def test_basic_fail_eto_simulation_supply_ventilation_model_characteristics(self):
        with self.subTest("Nones"):
            data = eto_simulation_supply_ventilation_model_characteristics(None, None, None, None)
            self.assertEqual(data["model_supply_ventilation_characteristics"]["simulation"], None)
            self.assertEqual(data["model_supply_ventilation_characteristics"]["checklist"], None)
            self.assertEqual(data["model_supply_ventilation_characteristics"]["warning"], None)
            self.assertEqual(data["model_supply_ventilation_characteristics"]["warnings"], [])

        with self.subTest("Bad ID"):
            data = eto_simulation_supply_ventilation_model_characteristics(-2, None, None, None)
            self.assertEqual(data["model_supply_ventilation_characteristics"]["simulation"], None)
            self.assertEqual(data["model_supply_ventilation_characteristics"]["checklist"], None)
            self.assertEqual(data["model_supply_ventilation_characteristics"]["warning"], None)
            self.assertEqual(data["model_supply_ventilation_characteristics"]["warnings"], [])

        with self.subTest("Wrong Type"):
            self.simulation.mechanical_ventilation_systems.update(
                type=MechanicalVentilationType.ERV
            )
            data = eto_simulation_supply_ventilation_model_characteristics(
                self.simulation.id, None, None, None
            )
            self.assertEqual(data["model_supply_ventilation_characteristics"]["simulation"], None)
            self.assertEqual(data["model_supply_ventilation_characteristics"]["checklist"], None)
            self.assertEqual(data["model_supply_ventilation_characteristics"]["warning"], None)
            self.assertEqual(data["model_supply_ventilation_characteristics"]["warnings"], [])

        with self.subTest("Wrong consumption_unit"):
            self.simulation.mechanical_ventilation_systems.update(
                type=MechanicalVentilationType.SUPPLY_ONLY,
                consumption_unit=AuxEnergyUnit.KWH_YEAR,
            )
            data = eto_simulation_supply_ventilation_model_characteristics(
                self.simulation.id, None, None, None
            )
            self.assertEqual(data["model_supply_ventilation_characteristics"]["simulation"], None)
            self.assertEqual(data["model_supply_ventilation_characteristics"]["checklist"], None)
            self.assertIn("mismatch", data["model_supply_ventilation_characteristics"]["warning"])
            self.assertIn("Watts", data["model_supply_ventilation_characteristics"]["warnings"][0])

        with self.subTest("Wrong ventilation_rate_unit"):
            self.simulation.mechanical_ventilation_systems.update(
                type=MechanicalVentilationType.SUPPLY_ONLY,
                consumption_unit=AuxEnergyUnit.WATT,
                # The VentilationRateUnit only supports one unit now (which is obviously a valid choice),
                # so we have to manually set an invalid unit instead of using an enum as we usually would
                ventilation_rate_unit="cmm",
            )
            data = eto_simulation_supply_ventilation_model_characteristics(
                self.simulation.id, None, None, None
            )
            self.assertEqual(data["model_supply_ventilation_characteristics"]["simulation"], None)
            self.assertEqual(data["model_supply_ventilation_characteristics"]["checklist"], None)
            self.assertIn("mismatch", data["model_supply_ventilation_characteristics"]["warning"])
            self.assertIn("CFM", data["model_supply_ventilation_characteristics"]["warnings"][0])

    def test_eto_simulation_supply_ventilation_model_custom_characteristics(self):
        equipment_furnace = {
            "hints": {
                "is_custom": True,
                "model_number": {"is_custom": True},
                "characteristics": {"is_custom": True},
            },
            "input": {
                "ecm": None,
                "afue": None,
                "motor_hp": None,
                "brand_name": "Lennox",
                "eae_kwh_yr": None,
                "model_number": "ML196UH070XE48B*",
                "capacity_mbtuh": None,
                "ventilation_fan_watts": None,
            },
        }

        data = eto_simulation_supply_ventilation_model_characteristics(
            self.simulation.id, equipment_furnace, None, None
        )
        self.assertIsNotNone(data["model_supply_ventilation_characteristics"]["simulation"])
        self.assertIsNotNone(data["model_supply_ventilation_characteristics"]["checklist"])
        self.assertIn("mismatch", data["model_supply_ventilation_characteristics"]["warning"])
        self.assertIn(" +", data["model_supply_ventilation_characteristics"]["warning"])
        self.assertIn("Custom", data["model_supply_ventilation_characteristics"]["warnings"][0])
        self.assertEqual(len(data["model_supply_ventilation_characteristics"]["warnings"]), 1)

    def test_eto_simulation_supply_ventilation_model_mismatch_characteristics(self):
        equipment_furnace = {
            "input": {
                "ecm": "Y",
                "afue": "96.2",
                "motor_hp": "1/2",
                "brand_name": "Bryant",
                "eae_kwh_yr": "227",
                "model_number": "915SB36040E17",
                "capacity_mbtuh": "39",
                "ventilation_fan_watts": "10.1",
            }
        }

        with self.subTest("Furnace Bad Rate"):
            data = eto_simulation_supply_ventilation_model_characteristics(
                self.simulation.id, equipment_furnace, None, None
            )
            self.assertIsNotNone(data["model_supply_ventilation_characteristics"]["simulation"])
            self.assertIsNotNone(data["model_supply_ventilation_characteristics"]["checklist"])
            self.assertIn("mismatch", data["model_supply_ventilation_characteristics"]["warning"])
            self.assertIn("power", data["model_supply_ventilation_characteristics"]["warnings"][0])
            self.assertEqual(len(data["model_supply_ventilation_characteristics"]["warnings"]), 1)

        equipment_ashp = {
            "input": {
                "hspf": "11",
                "seer": "19.2",
                "motor_hp": "-",
                "brand_name": "Mitsubishi",
                "capacity_17f_kbtuh": "22.2",
                "capacity_47f_kbtuh": "36",
                "indoor_model_number": "Non-Ducted",
                "outdoor_model_number": "MXZ-4C36NA2",
                "ventilation_fan_watts": "-",
                "cooling_capacity_kbtuh": "35.4",
            }
        }

        with self.subTest("ASHP Bad Rate"):
            data = eto_simulation_supply_ventilation_model_characteristics(
                self.simulation.id, None, equipment_ashp, None
            )
            self.assertIsNotNone(data["model_supply_ventilation_characteristics"]["simulation"])
            self.assertIsNotNone(data["model_supply_ventilation_characteristics"]["checklist"])
            self.assertIn("mismatch", data["model_supply_ventilation_characteristics"]["warning"])
            self.assertIn("power", data["model_supply_ventilation_characteristics"]["warnings"][0])
            self.assertEqual(len(data["model_supply_ventilation_characteristics"]["warnings"]), 1)

        equipment_furnace = {
            "input": {
                "ecm": "Y",
                "afue": "96.2",
                "motor_hp": "1/2",
                "brand_name": "Bryant",
                "eae_kwh_yr": "227",
                "model_number": "915SB36040E17",
                "capacity_mbtuh": "39",
                "ventilation_fan_watts": "10.2",
            }
        }

        with self.subTest("Furnace Solid pass"):
            data = eto_simulation_supply_ventilation_model_characteristics(
                self.simulation.id, equipment_furnace, None, {"input": "Furnace"}
            )
            self.assertIsNotNone(data["model_supply_ventilation_characteristics"]["simulation"])
            self.assertIsNotNone(data["model_supply_ventilation_characteristics"]["checklist"])
            self.assertIsNone(data["model_supply_ventilation_characteristics"]["warning"])
            self.assertEqual(len(data["model_supply_ventilation_characteristics"]["warnings"]), 0)

        equipment_ashp = {
            "input": {
                "hspf": "11",
                "seer": "19.2",
                "motor_hp": "-",
                "brand_name": "Mitsubishi",
                "capacity_17f_kbtuh": "22.2",
                "capacity_47f_kbtuh": "36",
                "indoor_model_number": "Non-Ducted",
                "outdoor_model_number": "MXZ-4C36NA2",
                "ventilation_fan_watts": "10.2",
                "cooling_capacity_kbtuh": "35.4",
            }
        }

        with self.subTest("ASHP Solid pass"):
            data = eto_simulation_supply_ventilation_model_characteristics(
                self.simulation.id, None, equipment_ashp, {"input": "Heat Pump"}
            )
            self.assertIsNotNone(data["model_supply_ventilation_characteristics"]["simulation"])
            self.assertIsNotNone(data["model_supply_ventilation_characteristics"]["checklist"])
            self.assertIsNone(data["model_supply_ventilation_characteristics"]["warning"])
            self.assertEqual(len(data["model_supply_ventilation_characteristics"]["warnings"]), 0)

        primary_heat = {"input": "Electric Heat Pump \u2013 Ground Source"}

        with self.subTest("ASHP Switch pass"):
            data = eto_simulation_supply_ventilation_model_characteristics(
                self.simulation.id, equipment_furnace, equipment_ashp, primary_heat
            )
            self.assertIsNotNone(data["model_supply_ventilation_characteristics"]["simulation"])
            self.assertIsNotNone(data["model_supply_ventilation_characteristics"]["checklist"])
            self.assertIn(
                "Heat Pump", data["model_supply_ventilation_characteristics"]["checklist"]
            )
            self.assertIsNone(data["model_supply_ventilation_characteristics"]["warning"])
            self.assertEqual(len(data["model_supply_ventilation_characteristics"]["warnings"]), 0)


class AnalyticsBalancedVentilationTests(AxisTestCase):
    @classmethod
    @mock.patch(
        "axis.gbr.gbr.GreenBuildingRegistryAPIConnect.post", side_effect=gbr_mocked_response
    )
    def setUpTestData(cls, _mock):
        super(AnalyticsBalancedVentilationTests, cls).setUpTestData()
        cls.simulation = simulation_factory(
            mechanical_ventilation_count=1,
            mechanical_ventilation__type=MechanicalVentilationType.BALANCED,
            mechanical_ventilation__consumption=10.2,
            mechanical_ventilation__consumption_unit=AuxEnergyUnit.WATT,
            mechanical_ventilation__ventilation_rate_unit=VentilationRateUnit.CFM,
            mechanical_ventilation__ventilation_rate=25.3,
        )

        cls.no_answer = {
            "input": None,
            "_question": None,
            "is_custom": None,
            "pretty": "",
        }
        cls.equipment_ventilation_hrv_erv = {
            "raw": {
                "asre": "66",
                "brand_name": "Panasonic",
                "model_number": "FV04VE1",
                "net_airflow_cfm": "40",
                "power_consumption_watts": "23",
            },
            "hints": {"SPECULATIVE": True},
            "input": {
                "asre": "66",
                "brand_name": "Panasonic",
                "model_number": "FV04VE1",
                "net_airflow_cfm": "40",
                "power_consumption_watts": "23",
            },
            "_question": "Select the HRV/ERV",
            "is_custom": None,
            "pretty": "Panasonic; FV04VE1; Net Airflow=40 CFM, Power Consumption=23 watts, ASRE=66%",
        }
        cls.equipment_ventilation_spot_erv_count = {
            "raw": 999,
            "hints": {"SPECULATIVE": True},
            "input": 999,
            "_question": "Number of Spot ERV units",
            "is_custom": None,
            "pretty": "999",
        }
        cls.primary_heating_equipment_type_furnace = {
            "input": "Gas Furnace",
            "_question": "Select the Primary Heating Equipment Type",
            "is_custom": None,
            "pretty": "Gas Furnace",
        }
        cls.primary_heating_equipment_type_ashp = {
            "input": "Electric Heat Pump – Air Source Ducted",
            "_question": "Select the Primary Heating Equipment Type",
            "is_custom": None,
            "pretty": "Electric Heat Pump – Air Source Ducted",
        }
        cls.equipment_furnace = {
            "input": {
                "ecm": "Y",
                "afue": "95",
                "motor_hp": " 1/2",
                "brand_name": "Coleman",
                "eae_kwh_yr": "487",
                "model_number": "TM9E060B12MP12",
                "capacity_mbtuh": "57",
                "ventilation_fan_watts": "54.4",
            },
            "_question": "Select the furnace",
            "is_custom": None,
            "pretty": "Coleman; TM9E060B12MP12; Capacity=57 MBtuh, AFUE=95%, Eae=487 kWh/yr, "
            "ECM=Y, HP= 1/2, Fan=54.4W",
        }

        cls.equipment_heat_pump = {
            "input": {
                "hspf": "11.7",
                "seer": "16",
                "motor_hp": "1/3",
                "brand_name": "Mitsubishi",
                "capacity_17f_kbtuh": "23.2",
                "capacity_47f_kbtuh": "33.4",
                "indoor_model_number": "SVZ-KP36NA",
                "outdoor_model_number": "SUZ-KA36NA2",
                "ventilation_fan_watts": "36.3",
                "cooling_capacity_kbtuh": "33.4",
            },
            "_question": "Select the primary heat pump used for space conditioning",
            "is_custom": None,
            "pretty": "Mitsubishi; SUZ-KA36NA2/SVZ-KP36NA; Capacity (17F)=23.2 kBtuh, "
            "Capacity (47F)=33.4 kBtuh, HSPF=11.7, Cooling Capacity=33.4 kBTUh, SEER=16, "
            "HP=1/3, Fan=36.3W",
        }
        cls.equipment_ventilation_supply_brand = {
            "raw": "Honeywell",
            "hints": {"SPECULATIVE": True},
            "input": "Honeywell",
            "_question": "Select the supply only ventilation brand",
            "is_custom": None,
            "pretty": "Honeywell",
        }
        cls.equipment_ventilation_supply_model = {
            "raw": "Y8150A1017",
            "hints": {"SPECULATIVE": True},
            "input": "Y8150A1017",
            "_question": "Select the supply only ventilation model",
            "is_custom": None,
            "pretty": "Y8150A1017",
        }
        cls.equipment_ventilation_exhaust = {
            "input": {
                "sp": "0.1",
                "speed_cfm": "80",
                "brand_name": "Panasonic",
                "model_number": "FV-0511VQ1",
                "input_power_watts": "5.9",
            },
            "_question": "Select the exhaust ventilation",
            "is_custom": None,
            "pretty": "Panasonic; FV-0511VQ1; SP=0.1, Speed=80 (CFM), Input power=5.9 (watts)",
        }
        cls.equipment_ventilation_system_type = {
            "input": "Balanced Ventilation without Heat Recovery",
            "_question": "Select the ventilation system type",
            "is_custom": None,
            "pretty": "Balanced Ventilation without Heat Recovery",
        }

    def test_basic_fail_eto_simulation_balanced_ventilation_model_characteristics(self):
        with self.subTest("Nones"):
            data = eto_simulation_balanced_ventilation_model_characteristics(None)
            self.assertEqual(data["model_balanced_ventilation_characteristics"]["simulation"], None)
            self.assertEqual(data["model_balanced_ventilation_characteristics"]["checklist"], None)
            self.assertEqual(data["model_balanced_ventilation_characteristics"]["warning"], None)
            self.assertEqual(data["model_balanced_ventilation_characteristics"]["warnings"], [])

        with self.subTest("Bad ID"):
            data = eto_simulation_balanced_ventilation_model_characteristics(-2)
            self.assertEqual(data["model_balanced_ventilation_characteristics"]["simulation"], None)
            self.assertEqual(data["model_balanced_ventilation_characteristics"]["checklist"], None)
            self.assertEqual(data["model_balanced_ventilation_characteristics"]["warning"], None)
            self.assertEqual(data["model_balanced_ventilation_characteristics"]["warnings"], [])

        with self.subTest("Wrong Type"):
            self.simulation.mechanical_ventilation_systems.update(
                type=MechanicalVentilationType.SUPPLY_ONLY
            )
            data = eto_simulation_balanced_ventilation_model_characteristics(self.simulation.id)
            self.assertEqual(data["model_balanced_ventilation_characteristics"]["simulation"], None)
            self.assertEqual(data["model_balanced_ventilation_characteristics"]["checklist"], None)
            self.assertEqual(data["model_balanced_ventilation_characteristics"]["warning"], None)
            self.assertEqual(data["model_balanced_ventilation_characteristics"]["warnings"], [])

        with self.subTest("Wrong consumption_unit"):
            self.simulation.mechanical_ventilation_systems.update(
                type=MechanicalVentilationType.ERV,
                consumption_unit=AuxEnergyUnit.KWH_YEAR,
            )
            data = eto_simulation_balanced_ventilation_model_characteristics(self.simulation.id)
            self.assertEqual(data["model_balanced_ventilation_characteristics"]["simulation"], None)
            self.assertEqual(data["model_balanced_ventilation_characteristics"]["checklist"], None)
            self.assertIn("mismatch", data["model_balanced_ventilation_characteristics"]["warning"])
            self.assertIn(
                "Watts", data["model_balanced_ventilation_characteristics"]["warnings"][0]
            )

        with self.subTest("Wrong ventilation_rate_unit"):
            self.simulation.mechanical_ventilation_systems.update(
                type=MechanicalVentilationType.HRV,
                consumption_unit=AuxEnergyUnit.WATT,
                # The VentilationRateUnit only supports one unit now (which is obviously a valid choice),
                # so we have to manually set an invalid unit instead of using an enum as we usually would
                ventilation_rate_unit="cmm",
            )
            data = eto_simulation_balanced_ventilation_model_characteristics(self.simulation.id)
            self.assertEqual(data["model_balanced_ventilation_characteristics"]["simulation"], None)
            self.assertEqual(data["model_balanced_ventilation_characteristics"]["checklist"], None)
            self.assertIn("mismatch", data["model_balanced_ventilation_characteristics"]["warning"])
            self.assertIn("CFM", data["model_balanced_ventilation_characteristics"]["warnings"][0])

        with self.subTest("Wrong Checklist Response"):
            self.simulation.mechanical_ventilation_systems.update(
                type=MechanicalVentilationType.EXHAUST_ONLY,
                ventilation_rate_unit=VentilationRateUnit.CFM,
            )
            data = eto_simulation_balanced_ventilation_model_characteristics(
                self.simulation.id, equipment_ventilation_system_type={"input": "WA - Exhaust Only"}
            )
            self.assertEqual(data["model_balanced_ventilation_characteristics"]["simulation"], None)
            self.assertEqual(data["model_balanced_ventilation_characteristics"]["checklist"], None)
            self.assertEqual(data["model_balanced_ventilation_characteristics"]["warning"], None)
            self.assertEqual(data["model_balanced_ventilation_characteristics"]["warnings"], [])

    def test_checklist_balanced_with_heat_recovery(self):
        with self.subTest("Basic Balance HRV"):
            data = eto_simulation_balanced_ventilation_model_characteristics(
                self.simulation.id, self.equipment_ventilation_hrv_erv
            )["model_balanced_ventilation_characteristics"]
            input_data = self.equipment_ventilation_hrv_erv["input"]
            self.assertIn(input_data["asre"], data["checklist"])
            self.assertIn(input_data["net_airflow_cfm"], data["checklist"])
            self.assertIn(input_data["power_consumption_watts"], data["checklist"])
            self.assertNotIn("Units", data["checklist"])
            self.assertEqual(data["warning"], "Balanced ventilation must be individually verified")
            self.assertFalse(data["warning"].endswith("+"))

        with self.subTest("Balance HRV and HRV/ERV counts"):
            data = eto_simulation_balanced_ventilation_model_characteristics(
                self.simulation.id,
                self.equipment_ventilation_hrv_erv,
                self.equipment_ventilation_spot_erv_count,
            )["model_balanced_ventilation_characteristics"]
            self.assertIn(input_data["asre"], data["checklist"])
            self.assertIn(input_data["net_airflow_cfm"], data["checklist"])
            self.assertIn(input_data["power_consumption_watts"], data["checklist"])
            self.assertIn(
                str(self.equipment_ventilation_spot_erv_count.get("input")), data["checklist"]
            )
            self.assertFalse(data["warning"].endswith("+"))
        with self.subTest("Balanced with Furnace Supply"):
            data = eto_simulation_balanced_ventilation_model_characteristics(
                self.simulation.id,
                self.equipment_ventilation_hrv_erv,
                self.equipment_ventilation_spot_erv_count,
                self.primary_heating_equipment_type_furnace,
                self.equipment_furnace,
                self.no_answer,
            )["model_balanced_ventilation_characteristics"]
            self.assertIn(input_data["asre"], data["checklist"])
            self.assertIn(input_data["net_airflow_cfm"], data["checklist"])
            self.assertIn(input_data["power_consumption_watts"], data["checklist"])
            self.assertIn(
                str(self.equipment_ventilation_spot_erv_count.get("input")), data["checklist"]
            )
            self.assertIn(
                str(self.equipment_furnace["input"]["ventilation_fan_watts"]), data["checklist"]
            )
            self.assertFalse(data["warning"].endswith("+"))
        with self.subTest("Balanced with ASHP Supply"):
            data = eto_simulation_balanced_ventilation_model_characteristics(
                self.simulation.id,
                self.equipment_ventilation_hrv_erv,
                self.equipment_ventilation_spot_erv_count,
                self.primary_heating_equipment_type_ashp,
                self.no_answer,
                self.equipment_heat_pump,
            )["model_balanced_ventilation_characteristics"]
            self.assertIn(input_data["asre"], data["checklist"])
            self.assertIn(input_data["net_airflow_cfm"], data["checklist"])
            self.assertIn(input_data["power_consumption_watts"], data["checklist"])
            self.assertIn(
                str(self.equipment_ventilation_spot_erv_count.get("input")), data["checklist"]
            )
            self.assertIn(
                str(self.equipment_heat_pump["input"]["ventilation_fan_watts"]), data["checklist"]
            )
            self.assertFalse(data["warning"].endswith("+"))
        with self.subTest("Balanced with ASHP Supply CUSTOM"):
            equipment_ventilation_hrv_erv = {
                "hints": {
                    "is_custom": True,
                    "model_number": {"is_custom": True},
                    "characteristics": {"is_custom": True},
                },
                "input": {
                    "asre": None,
                    "brand_name": "Broan",
                    "model_number": "HERO 120H",
                    "net_airflow_cfm": None,
                    "power_consumption_watts": None,
                },
                "_question": "Select the HRV/ERV",
                "is_custom": True,
                "pretty": "Broan; HERO 120H; Net Airflow=None CFM, Power Consumption=None watts, ASRE=None%",
            }
            data = eto_simulation_balanced_ventilation_model_characteristics(
                self.simulation.id,
                equipment_ventilation_hrv_erv,
                self.equipment_ventilation_spot_erv_count,
                self.primary_heating_equipment_type_ashp,
                self.no_answer,
                self.equipment_heat_pump,
            )["model_balanced_ventilation_characteristics"]
            self.assertIn("ASRE: -", data["checklist"])
            self.assertIn("Rate (CFM): -", data["checklist"])
            self.assertIn("Fan (Watts): -", data["checklist"])
            self.assertIn(
                str(self.equipment_ventilation_spot_erv_count.get("input")), data["checklist"]
            )
            self.assertIn(
                str(self.equipment_heat_pump["input"]["ventilation_fan_watts"]), data["checklist"]
            )
            self.assertTrue(data["warning"].endswith("+"))

    def test_checklist_balanced_exhaust_only(self):
        with self.subTest("Balanced Exhaust Only no Supply"):
            data = eto_simulation_balanced_ventilation_model_characteristics(
                self.simulation.id,
                equipment_ventilation_exhaust=self.equipment_ventilation_exhaust,
            )["model_balanced_ventilation_characteristics"]
            input_data = self.equipment_ventilation_exhaust["input"]
            self.assertIn(input_data["speed_cfm"], data["checklist"])
            self.assertIn(input_data["input_power_watts"], data["checklist"])
            self.assertNotIn("Supply", data["checklist"])
            self.assertFalse(data["warning"].endswith("+"))
        with self.subTest("Balanced Exhaust with supply"):
            data = eto_simulation_balanced_ventilation_model_characteristics(
                self.simulation.id,
                primary_heating_equipment_type=self.primary_heating_equipment_type_furnace,
                equipment_furnace=self.equipment_furnace,
                equipment_ventilation_exhaust=self.equipment_ventilation_exhaust,
            )["model_balanced_ventilation_characteristics"]
            self.assertIn(input_data["speed_cfm"], data["checklist"])
            self.assertIn(input_data["input_power_watts"], data["checklist"])
            self.assertIn("Supply", data["checklist"])
            self.assertIn(
                str(self.equipment_furnace["input"]["ventilation_fan_watts"]), data["checklist"]
            )
            self.assertFalse(data["warning"].endswith("+"))

    def test_checklist_balanced_supply_brand_model(self):
        input_data = " ".join(
            [
                self.equipment_ventilation_supply_model["input"],
                self.equipment_ventilation_supply_brand["input"],
            ]
        )
        with self.subTest("Balanced Exhaust Only no Supply"):
            data = eto_simulation_balanced_ventilation_model_characteristics(
                self.simulation.id,
                equipment_ventilation_supply_brand=self.equipment_ventilation_supply_brand,
                equipment_ventilation_supply_model=self.equipment_ventilation_supply_model,
            )["model_balanced_ventilation_characteristics"]
            self.assertIn(input_data, data["checklist"])
            self.assertNotIn("(Supply)", data["checklist"])
            self.assertFalse(data["warning"].endswith("+"))
        with self.subTest("Balanced Exhaust with supply"):
            data = eto_simulation_balanced_ventilation_model_characteristics(
                self.simulation.id,
                primary_heating_equipment_type=self.primary_heating_equipment_type_ashp,
                equipment_heat_pump=self.equipment_heat_pump,
                equipment_ventilation_supply_brand=self.equipment_ventilation_supply_brand,
                equipment_ventilation_supply_model=self.equipment_ventilation_supply_model,
            )["model_balanced_ventilation_characteristics"]
            self.assertIn(input_data, data["checklist"])
            self.assertIn("(Supply)", data["checklist"])
            self.assertIn(
                str(self.equipment_heat_pump["input"]["ventilation_fan_watts"]), data["checklist"]
            )
            self.assertFalse(data["warning"].endswith("+"))

    def test_heating_only(self):
        with self.subTest("Balanced Exhaust heating equipment only Furnace"):
            data = eto_simulation_balanced_ventilation_model_characteristics(
                self.simulation.id,
                primary_heating_equipment_type=self.primary_heating_equipment_type_furnace,
                equipment_furnace=self.equipment_furnace,
            )["model_balanced_ventilation_characteristics"]
            input_data = self.equipment_furnace["input"]
            self.assertIn(input_data["ventilation_fan_watts"], data["checklist"])
            self.assertIn("(Heating Supply)", data["checklist"])
            self.assertFalse(data["warning"].endswith("+"))

        with self.subTest("Balanced Exhaust heating equipment only ASHP"):
            data = eto_simulation_balanced_ventilation_model_characteristics(
                self.simulation.id,
                primary_heating_equipment_type=self.primary_heating_equipment_type_ashp,
                equipment_heat_pump=self.equipment_heat_pump,
            )["model_balanced_ventilation_characteristics"]
            input_data = self.equipment_heat_pump["input"]
            self.assertIn(input_data["ventilation_fan_watts"], data["checklist"])
            self.assertIn("(Heating Supply)", data["checklist"])
            self.assertFalse(data["warning"].endswith("+"))
