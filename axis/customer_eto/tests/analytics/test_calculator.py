"""eps.py - Axis"""

__author__ = "Steven K"
__date__ = "10/30/20 11:32"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
import random

from axis.checklist.collection.test_mixins import CollectionRequestMixin
from axis.core.tests.testcases import AxisTestCase
from axis.customer_eto.analytics import (
    get_eps_required_data,
    get_washington_code_credit_calculator_specifications_data,
)
from axis.customer_eto.models import FastTrackSubmission
from axis.customer_eto.tests.analytics.test_appliances import ETO2022ProgramAnalyticsTestMixin
from axis.customer_eto.tests.program_checks.test_washington_code_credit import (
    WashingtonCodeCreditTestMixin,
)
from axis.eep_program.models import EEPProgram
from axis.home.models import EEPProgramHomeStatus

log = logging.getLogger(__name__)


class CalculatorAnalyticsTests(
    ETO2022ProgramAnalyticsTestMixin, CollectionRequestMixin, AxisTestCase
):
    def setUp(self):
        self.complete = EEPProgramHomeStatus.objects.get(state="complete")
        self.home_status = EEPProgramHomeStatus.objects.exclude(state="complete").get()

    @property
    def input_data(self):
        input_data = {
            "simulation_id": None,
            "city_id": None,
            "us_state": None,
            "electric_utility_id": None,
            "gas_utility_id": None,
            "builder_id": None,
            "primary_heating_equipment_type": None,
            "smart_thermostat_brand": None,
            "ets_annual_etsa_kwh": None,
            "non_ets_annual_pv_watts": None,
            "home_status_id": self.home_status.id,
        }
        return input_data.copy()

    def test_eps_calculator(self):
        data = get_eps_required_data(**self.input_data)
        self.assertEqual(set(data.keys()), {"percent_improvement"})

    def test_eto_2021(self):
        EEPProgram.objects.filter(slug="eto-2020").update(slug="eto-2021")
        self.home_status = EEPProgramHomeStatus.objects.exclude(state="complete").get()

        data = get_eps_required_data(**self.input_data)
        self.assertEqual(set(data.keys()), {"percent_improvement"})


class AnalyticsCalculatorWashingtonCodeCreditTests(WashingtonCodeCreditTestMixin, AxisTestCase):
    def test_invalid_data(self):
        bad_data = {
            k: random.choice([v, None, None, None]) for k, v in self.default_program_data.items()
        }

        data = get_washington_code_credit_calculator_specifications_data(**bad_data)
        self.assertIn("errors", data)
        self.assertTrue(len(data["errors"]) > 1)

    def test_calculator_data_valid(self):
        data = get_washington_code_credit_calculator_specifications_data(
            **self.default_program_data
        )
        self.assertNotIn("errors", data)
        self.assertIn("building_envelope_specification", data)
        self.assertIn("specifications", data["building_envelope_specification"])
        self.assertIn("meet_requirements", data["building_envelope_specification"])
        self.assertEqual(len(data["building_envelope_specification"]["specifications"]), 11)

        self.assertIn("air_leakage_specification", data)
        self.assertIn("specifications", data["air_leakage_specification"])
        self.assertIn("meet_requirements", data["air_leakage_specification"])
        self.assertEqual(len(data["air_leakage_specification"]["specifications"]), 5)

        self.assertIn("hvac_specification", data)
        self.assertIn("specifications", data["hvac_specification"])
        self.assertIn("meet_requirements", data["hvac_specification"])
        self.assertEqual(len(data["hvac_specification"]["specifications"]), 3)

        self.assertIn("hvac_distribution_specification", data)
        self.assertIn("specifications", data["hvac_distribution_specification"])
        self.assertIn("meet_requirements", data["hvac_distribution_specification"])
        self.assertEqual(len(data["hvac_distribution_specification"]["specifications"]), 3)

        self.assertIn("water_specification", data)
        self.assertIn("specifications", data["water_specification"])
        self.assertIn("meet_requirements", data["water_specification"])
        self.assertEqual(len(data["water_specification"]["specifications"]), 6)

        # for k, v in data.items():
        #
        #     print(f"self.assertIn({k!r}, data)")
        #     print(f'self.assertIn("specifications", data[{k!r}])')
        #     print(f'self.assertIn("meet_requirements", data[{k!r}])')
        #     print(
        #         f'self.assertEqual(len(data[{k!r}]["specifications"]),'
        #         f" {len(data[k]['specifications'])})"
        #     )
