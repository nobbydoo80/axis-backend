"""test_washington_code_credit.py - Axis"""

__author__ = "Steven K"
__date__ = "11/5/21 11:15"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
import pprint

from django.core import management

from analytics.models import AnalyticRollup

from axis.annotation.tests.test_mixins import AnnotationMixin
from axis.checklist.collection.test_mixins import CollectionRequestMixin
from axis.core.tests.testcases import AxisTestCase
from axis.core.tests.test_views import DevNull
from ...program_checks.test_washington_code_credit import (
    WashingtonCodeCreditTestMixin,
    add_required_washington_code_credit_responses,
    washington_code_credit_default_data,
)
from axis.customer_eto.api_v3.serializers.analytics.washington_code_credit import (
    WashingtonCodeCreditAnalyticRollupSerializer,
)

log = logging.getLogger(__name__)


class AnalyticsSerializerTests(
    WashingtonCodeCreditTestMixin,
    CollectionRequestMixin,
    AnnotationMixin,
    AxisTestCase,
):
    @classmethod
    def setUpTestData(cls):
        super(AnalyticsSerializerTests, cls).setUpTestData()

        management.call_command(
            "add_analytics_program",
            "-p",
            "washington-code-credit",
            stderr=DevNull(),
            stdout=DevNull(),
        )

        add_required_washington_code_credit_responses(
            data=washington_code_credit_default_data(), home_status=cls.home_status
        )
        missing_checks = cls.home_status.report_eligibility_for_certification()
        assert len(missing_checks) == 0, missing_checks

    def run_analytics(self):
        management.call_command(
            "run_analytics",
            "-p",
            "washington-code-credit",
            "--immediate",
            "--force",
            stderr=DevNull(),
            stdout=DevNull(),
        )
        return AnalyticRollup.objects.get()

    def test_run_analytics(self):
        analytics = self.run_analytics()
        initial_date_modified = analytics.date_modified
        initial_data = analytics.get_flattened_results()

        self.assertEqual(AnalyticRollup.objects.count(), 1)
        self.assertEqual(AnalyticRollup.objects.get().content_object, self.home_status)
        self.assertEqual(AnalyticRollup.objects.get().analytics.count(), 6)
        self.assertEqual(AnalyticRollup.objects.get().status, "READY")

        analytics = self.run_analytics()
        self.assertGreater(analytics.date_modified, initial_date_modified)
        self.assertEqual(analytics.get_flattened_results(), initial_data)

    def test_serializer(self):
        analytics = self.run_analytics()
        serializer = WashingtonCodeCreditAnalyticRollupSerializer(
            instance=AnalyticRollup.objects.get()
        )
        data = serializer.to_representation(instance=analytics)
        self.assertEqual(
            set(data.keys()),
            {"id", "date_modified", "program_name", "status", "home_analysis", "spec_analysis"},
        )

    def test_home_analysis_serializer(self):
        analytics = self.run_analytics()
        serializer = WashingtonCodeCreditAnalyticRollupSerializer(
            instance=AnalyticRollup.objects.get()
        )
        data = serializer.to_representation(instance=analytics)["home_analysis"]
        self.assertEqual(
            set(data.keys()),
            {
                "rater",
                "rater_of_record",
                "builder",
                "addresss_long",
                "electric_utility",
                "gas_utility",
            },
        )

        self.assertEqual(data["rater"]["value"], str(self.home_status.company))
        self.assertEqual(data["rater_of_record"]["value"], str(self.home_status.rater_of_record))
        self.assertEqual(data["builder"]["value"], str(self.home_status.home.get_builder()))
        self.assertEqual(
            data["addresss_long"]["value"],
            self.home_status.home.get_addr(include_city_state_zip=True, raw=True),
        )
        self.assertEqual(
            data["electric_utility"]["value"], str(self.home_status.get_electric_company())
        )
        self.assertEqual(data["gas_utility"]["value"], str(self.home_status.home.get_gas_company()))

    def test_spec_analysis_serializer(self):
        analytics = self.run_analytics()
        serializer = WashingtonCodeCreditAnalyticRollupSerializer(
            instance=AnalyticRollup.objects.get()
        )
        data = serializer.to_representation(instance=analytics)["spec_analysis"]
        self.assertEqual(
            set(data.keys()),
            {
                "building_envelope_specification",
                "air_leakage_specification",
                "hvac_specification",
                "hvac_distribution_specification",
                "water_specification",
                "warnings",
            },
        )
        self.assertIn("meet_requirements", data["building_envelope_specification"])
        self.assertIn("specifications", data["building_envelope_specification"])
        self.assertTrue(isinstance(data["building_envelope_specification"]["specifications"], list))

        self.assertIn("meet_requirements", data["air_leakage_specification"])
        self.assertIn("specifications", data["air_leakage_specification"])
        self.assertTrue(isinstance(data["air_leakage_specification"]["specifications"], list))

        self.assertIn("meet_requirements", data["hvac_specification"])
        self.assertIn("specifications", data["hvac_specification"])
        self.assertTrue(isinstance(data["hvac_specification"]["specifications"], list))

        self.assertIn("meet_requirements", data["hvac_distribution_specification"])
        self.assertIn("specifications", data["hvac_distribution_specification"])
        self.assertTrue(isinstance(data["hvac_distribution_specification"]["specifications"], list))

        self.assertIn("meet_requirements", data["water_specification"])
        self.assertIn("specifications", data["water_specification"])
        self.assertTrue(isinstance(data["water_specification"]["specifications"], list))
