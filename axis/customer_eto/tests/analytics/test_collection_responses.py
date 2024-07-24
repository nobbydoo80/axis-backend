"""collection_responses.py - Axis"""

__author__ = "Steven K"
__date__ = "10/30/20 09:52"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import datetime
import json
import logging
import os.path

from axis.core.tests.testcases import AxisTestCase
from axis.customer_eto.analytics import (
    get_collection_responses,
    get_qa_collection_responses,
    get_wcc_collection_responses,
)
from axis.customer_eto.eep_programs.eto_2022 import (
    SmartThermostatBrands2022,
    AdditionalElements2022,
    StorageElements2022,
    MechanicalVentilationSystemTypes,
    CobidQualification,
)
from axis.customer_eto.enumerations import YesNo
from axis.customer_eto.tests.analytics.test_appliances import (
    ETO2022ProgramAnalyticsTestMixin,
)
from axis.checklist.collection.test_mixins import CollectionRequestMixin
from axis.customer_eto.tests.program_checks.test_washington_code_credit import (
    WashingtonCodeCreditTestMixin,
)
from axis.home.models import EEPProgramHomeStatus

log = logging.getLogger(__name__)


class AnalyticsCollectionResponseTests(
    ETO2022ProgramAnalyticsTestMixin, CollectionRequestMixin, AxisTestCase
):
    def setUp(self):
        self.complete = EEPProgramHomeStatus.objects.get(state="complete")
        self.home_status = EEPProgramHomeStatus.objects.exclude(state="complete").get()
        self.simulation = self.home_status.floorplan.simulation

    def test_get_collection_responses(self):
        """This tests out that we only pull out relevant dict input data"""
        data = {
            "is-adu": YesNo.NO,
            "builder-payment-redirected": YesNo.NO,
            "eto-electric-elements": AdditionalElements2022.SOLAR,
            "smart-thermostat-brand": SmartThermostatBrands2022.NONE,
            "primary-heating-equipment-type": {
                "hints": {"LEGACY": True, "answer_id": 2312113, "SPECULATIVE": True},
                "input": "Gas Furnace",
                "comment": "",
            },
            "equipment-furnace": {
                "raw": {
                    "ecm": "Y",
                    "afue": "96.2",
                    "motor_hp": " 1/2",
                    "brand_name": "Bryant",
                    "eae_kwh_yr": "227",
                    "model_number": "915SB36040E17",
                    "capacity_mbtuh": "39",
                    "ventilation_fan_watts": "54.4",
                },
                "hints": {"SPECULATIVE": True},
                "input": {
                    "ecm": "Y",
                    "afue": "96.2",
                    "motor_hp": " 1/2",
                    "brand_name": "Bryant",
                    "eae_kwh_yr": "227",
                    "model_number": "915SB36040E17",
                    "capacity_mbtuh": "39",
                    "ventilation_fan_watts": "54.4",
                },
            },
            "equipment-heat-pump": {
                "input": {
                    "hspf": "8.2",
                    "seer": "14",
                    "brand_name": "Daikin",
                    "capacity_17f_kbtuh": "19.5",
                    "capacity_47f_kbtuh": "34.6",
                    "indoor_model_number": "Ducted",
                    "outdoor_model_number": "4MXS36RMVJU",
                    "cooling_capacity_kbtuh": "34.6",
                }
            },
            "equipment-water-heater": {
                "input": {
                    "capacity": "50",
                    "brand_name": "Rheem",
                    "model_number": "PROG50 40N RH62",
                    "energy_factor": "0.62",
                }
            },
            "equipment-air-conditioner-brand": {
                "raw": "Trane",
                "hints": {"SPECULATIVE": True},
                "input": "Trane",
            },
            "equipment-air-conditioner-model-number-indoor": {"input": "4PXCBU30"},
            "equipment-air-conditioner-model-number-outdoor": {"input": "RA1336AJ1"},
            "equipment-refrigerator": {
                "raw": {
                    "brand_name": "GE",
                    "model_number": "GSE25GSH****",
                    "annual_energy_use_kwh_yr": "645",
                },
                "hints": {"SPECULATIVE": True},
                "input": {
                    "brand_name": "GE",
                    "model_number": "GSE25GSH****",
                    "annual_energy_use_kwh_yr": "645",
                },
            },
            "equipment-dishwasher": {
                "input": {
                    "brand_name": "Dacor",
                    "model_number": "DDW24T*****",
                    "annual_energy_use_kwh_yr": "239",
                }
            },
            "equipment-clothes-washer": {
                "hints": {
                    "is_custom": True,
                    "model_number": {"is_custom": True},
                    "characteristics": {"is_custom": True},
                },
                "input": {
                    "brand_name": "Electrolux",
                    "model_number": "fftw4120sw1",
                    "volume_cu_ft": None,
                    "annual_energy_use_kwh_yr": None,
                    "integrated_modified_energy_factor": None,
                },
            },
            "equipment-clothes-dryer": {
                "input": {
                    "brand_name": "Electrolux",
                    "model_number": "EFME427****",
                    "combined_energy_factor": "3.93",
                }
            },
            "equipment-ventilation-exhaust": {
                "raw": {
                    "sp": "0.1",
                    "speed_cfm": "50",
                    "brand_name": "Panasonic",
                    "model_number": "FV0510VS1",
                    "input_power_watts": "4.4",
                },
                "hints": {"SPECULATIVE": True},
                "input": {
                    "sp": "0.1",
                    "speed_cfm": "50",
                    "brand_name": "Panasonic",
                    "model_number": "FV0510VS1",
                    "input_power_watts": "4.4",
                },
            },
            "equipment-ventilation-system-type": MechanicalVentilationSystemTypes.BALANCED_NO_HR,
            "non-ets-annual-pv-watts": 6000,
        }
        self.add_bulk_answers(data, home_status=self.home_status, remove_prior=True)
        result = get_collection_responses(self.home_status.collection_request_id)
        valid_resps = {k: v for k, v in result.items() if v["input"] is not None}
        self.assertEqual(set(valid_resps), set(data))
        self.assertEqual(len(valid_resps), len(data))
        self.assertTrue(result["equipment-clothes-washer"]["is_custom"])

    def test_get_qa_collection_responses(self):
        data = {
            "is-adu": YesNo.NO,
            "smart-thermostat-brand": SmartThermostatBrands2022.BRYANT,
            "primary-heating-equipment-type": {
                "input": "Gas Furnace",
                "comment": "925SA42060E17A-B",
            },
            "equipment-furnace": {
                "input": {
                    "ecm": "Y",
                    "afue": "96",
                    "motor_hp": "1/2",
                    "brand_name": "Bryant",
                    "eae_kwh_yr": "189",
                    "model_number": "926TA36040V17",
                    "capacity_mbtuh": "39",
                    "ventilation_fan_watts": "54.4",
                }
            },
            "equipment-heat-pump": {
                "input": {
                    "hspf": "8.2",
                    "seer": "14",
                    "brand_name": "Daikin",
                    "capacity_17f_kbtuh": "19.5",
                    "capacity_47f_kbtuh": "34.6",
                    "indoor_model_number": "Ducted",
                    "outdoor_model_number": "4MXS36RMVJU",
                    "cooling_capacity_kbtuh": "34.6",
                }
            },
            "equipment-water-heater": {
                "hints": {"is_custom": True},
                "input": {
                    "capacity": None,
                    "brand_name": "Not installed",
                    "model_number": None,
                    "energy_factor": None,
                    "characteristics": None,
                },
            },
            "equipment-ventilation-exhaust": {
                "input": {
                    "sp": "0.1",
                    "speed_cfm": "90",
                    "brand_name": "Air King",
                    "model_number": "AK90",
                    "input_power_watts": "25.4",
                }
            },
        }
        self.add_bulk_answers(data=data, user_role="qa", home_status=self.home_status)
        result = get_qa_collection_responses(self.home_status.collection_request_id)
        valid_resps = {k: v for k, v in result["qa-responses"].items() if v["input"] is not None}
        self.assertEqual(set(valid_resps), set(data))
        self.assertEqual(len(valid_resps), len(data))
        self.assertTrue(result["qa-responses"]["equipment-water-heater"]["is_custom"])


class AnalyticsCollectionResponseWashingtonCodeCreditTests(
    WashingtonCodeCreditTestMixin,
    CollectionRequestMixin,
    AxisTestCase,
):
    @property
    def expected_measures(self):
        return [
            x.replace("wcc-", "")
            for x in [
                "wcc-conditioned_floor_area",
                "wcc-water_heating_fuel",
                "wcc-thermostat_type",
                "wcc-fireplace_efficiency",
                "wcc-wall_cavity_r_value",
                "wcc-wall_continuous_r_value",
                "wcc-framing_type",
                "wcc-window_u_value",
                "wcc-window_shgc",
                "wcc-floor_cavity_r_value",
                "wcc-slab_perimeter_r_value",
                "wcc-under_slab_r_value",
                "wcc-ceiling_r_value",
                "wcc-raised_heel",
                "wcc-total_ua_alternative",
                "wcc-air_leakage_ach",
                "wcc-ventilation_type",
                "wcc-ventilation_brand",
                "wcc-ventilation_model",
                "wcc-hrv_asre",
                "wcc-furnace_brand",
                "wcc-furnace_model",
                "wcc-furnace_afue",
                "wcc-furnace_location",
                "wcc-duct_location",
                "wcc-duct_leakage",
                "wcc-dwhr_installed",
                "wcc-water_heater_brand",
                "wcc-water_heater_model",
                "wcc-gas_water_heater_uef",
                "wcc-electric_water_heater_uef",
            ]
        ]

    def test_analytic_provides_for(self):
        filename = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "../../analytics/definitions/washington_code_credit.json",
            )
        )
        self.assertTrue(os.path.exists(filename))

        with open(filename) as fp:
            json_data = json.load(fp)

        analytic_definition = next(
            (x for x in json_data["metrics"] if x["name"] == "wcc-home-status-checklist-responses")
        )

        data = get_wcc_collection_responses(9999999999, None)
        self.assertEqual(set(data.keys()), set(self.expected_measures))
        self.assertEqual(set(data.keys()), set(analytic_definition["provides_for"]))

    def test_get_collection_responses_invalid_collection_request(self):
        """Test invalid collection request"""
        data = get_wcc_collection_responses(9999999999, datetime.datetime.now())
        self.assertEqual(set(data.keys()), set(self.expected_measures))
        for k in self.expected_measures:
            self.assertEqual(data[k], None)

    def test_valid_collection_request(self):
        baseline_input_data = self.default_program_data
        self.add_required_responses(baseline_input_data, home_status=self.home_status)
        self.assertIsNotNone(self.home_status.collection_request.id)
        data = get_wcc_collection_responses(self.home_status.collection_request.id, None)
        self.assertEqual(set(data.keys()), set(self.expected_measures))
        for key in self.expected_measures:
            self.assertIsNotNone(data[key], baseline_input_data[key])
