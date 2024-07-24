"""test_annotations.py - Axis"""

__author__ = "Steven K"
__date__ = "11/5/21 10:06"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
import os
import datetime
import json

from axis.annotation.tests.test_mixins import AnnotationMixin
from axis.core.tests.testcases import AxisTestCase
from axis.customer_eto.analytics import get_wcc_annotations
from axis.customer_eto.tests.program_checks.test_washington_code_credit import (
    WashingtonCodeCreditTestMixin,
)

log = logging.getLogger(__name__)


class AnalyticsAnnotationsWashingtonCodeCreditTests(
    WashingtonCodeCreditTestMixin,
    AnnotationMixin,
    AxisTestCase,
):
    @property
    def expected_annotations(self):
        return [
            "envelope_option",
            "air_leakage_option",
            "hvac_option",
            "hvac_distribution_option",
            "dwhr_option",
            "water_heating_option",
            "renewable_electric_option",
            "appliance_option",
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
            (x for x in json_data["metrics"] if x["name"] == "wcc-annotations")
        )

        data = get_wcc_annotations(9999999999, self.eep_program.id, datetime.datetime.now())
        self.assertEqual(set(data.keys()), set(self.expected_annotations))
        self.assertEqual(set(data.keys()), set(analytic_definition["provides_for"]))

    def test_get_wcc_annotations_invalid_home_status_id(self):
        """Test invalid collection request"""
        data = get_wcc_annotations(9999999999, self.eep_program.id, datetime.datetime.now())
        self.assertEqual(set(data.keys()), set(self.expected_annotations))
        for k in self.expected_annotations:
            self.assertEqual(data[k], None)

    def test_get_wcc_annotations_valid_annotations(self):
        baseline_input_data = self.default_program_data
        self.add_required_responses(baseline_input_data, home_status=self.home_status)
        self.assertIsNotNone(self.home_status.id)
        data = get_wcc_annotations(
            self.home_status.id, self.eep_program.id, datetime.datetime.now()
        )
        self.assertEqual(set(data.keys()), set(self.expected_annotations))
        for key in self.expected_annotations:
            self.assertIsNotNone(data[key], baseline_input_data[key])
