"""test_washington_code_credit.py - Axis"""

__author__ = "Steven K"
__date__ = "10/18/21 12:20"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import datetime
import logging


from axis.customer_eto.api_v3.serializers import WashingtonCodeCreditCalculatorSerializer
from axis.customer_eto.api_v3.serializers.reports import WashingtonCodeCreditReportSerializer
from axis.customer_eto.tests.program_checks.test_washington_code_credit import (
    WashingtonCodeCreditProgramBase,
)

log = logging.getLogger(__name__)


class TestWashingtonCodeCreditReportSerializer(WashingtonCodeCreditProgramBase):
    def test_test_serializer_data(self):
        # Add our responses and run the calculator
        self.add_required_responses(self.max_program_data)
        serializer = WashingtonCodeCreditCalculatorSerializer(
            data={"home_status": self.home_status.pk}
        )
        serializer.is_valid(raise_exception=True)
        self.project_tracker = serializer.save()

        serializer = WashingtonCodeCreditReportSerializer(instance=self.project_tracker)

        with self.subTest("Address"):
            self.assertEqual(
                self.home_status.home.get_home_address_display(
                    include_lot_number=False, include_city_state_zip=True
                ),
                serializer.data["address"],
            )
        with self.subTest("Builder"):
            self.assertEqual(
                str(self.home_status.home.get_builder()),
                serializer.data["builder"],
            )
        with self.subTest("Certification Date"):
            self.assertEqual(
                "Pending",
                serializer.data["certification_date"],
            )
        with self.subTest("Rater"):
            self.assertEqual(
                str(self.home_status.company),
                serializer.data["rater"],
            )
        with self.subTest("Year Built"):
            self.assertEqual(
                str(datetime.date.today().year),
                serializer.data["year_built"],
            )
        with self.subTest("SQ Feet"):
            self.assertEqual(
                f"{self.max_program_data.get('conditioned_floor_area'):,}",
                serializer.data["square_footage"],
            )
        with self.subTest("Electric"):
            self.assertEqual(
                str(self.home_status.get_electric_company()),
                serializer.data["electric_utility"],
            )
        with self.subTest("Gas"):
            self.assertEqual(
                str(self.home_status.get_gas_company()),
                serializer.data["gas_utility"],
            )
        with self.subTest("envelope_option"):
            value = self.max_program_data["envelope_option"]
            self.assertEqual(
                value,
                serializer.data["envelope_option"].value,
            )

        with self.subTest("air_leakage_option"):
            value = self.max_program_data["air_leakage_option"]
            self.assertEqual(
                value,
                serializer.data["air_leakage_option"].value,
            )

        with self.subTest("hvac_option"):
            value = self.max_program_data["hvac_option"]
            self.assertEqual(
                value,
                serializer.data["hvac_option"].value,
            )

        with self.subTest("hvac_distribution_option"):
            value = self.max_program_data["hvac_distribution_option"]
            self.assertEqual(
                value,
                serializer.data["hvac_distribution_option"].value,
            )

        with self.subTest("dwhr_option"):
            value = self.max_program_data["dwhr_option"]
            self.assertEqual(
                value,
                serializer.data["dwhr_option"].value,
            )

        with self.subTest("water_heating_option"):
            value = self.max_program_data["water_heating_option"]
            self.assertEqual(
                value,
                serializer.data["water_heating_option"].value,
            )

        with self.subTest("renewable_electric_option"):
            value = self.max_program_data["renewable_electric_option"]
            self.assertEqual(
                value,
                serializer.data["renewable_electric_option"].value,
            )

        with self.subTest("appliance_option"):
            value = self.max_program_data["appliance_option"]
            self.assertEqual(
                value,
                serializer.data["appliance_option"].value,
            )

        with self.subTest("required_credits_to_meet_code"):
            self.assertEqual(
                self.project_tracker.required_credits_to_meet_code,
                serializer.data["required_credits_to_meet_code"],
            )

        with self.subTest("achieved_total_credits"):
            self.assertEqual(
                self.project_tracker.achieved_total_credits,
                serializer.data["achieved_total_credits"],
            )

        with self.subTest("eligible_gas_points"):
            self.assertEqual(
                self.project_tracker.eligible_gas_points,
                serializer.data["eligible_gas_points"],
            )
