"""test_washington_code_credit.py - Axis"""

__author__ = "Steven K"
__date__ = "9/8/21 15:07"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from django.urls import reverse_lazy
from rest_framework import status
from rest_framework.test import APITestCase

from axis.customer_eto.eep_programs.washington_code_credit import (
    BuildingEnvelope,
    AirLeakageControl,
    HighEfficiencyHVAC,
    HighEfficiencyHVACDistribution,
    DWHR,
    EfficientWaterHeating,
    RenewableEnergy,
    Appliances,
    WACCFuelType,
    ThermostatType,
    FireplaceType,
    VentilationType,
    FurnaceLocation,
    DuctLocation,
)
from axis.customer_eto.enumerations import YesNo
from axis.customer_eto.models import FastTrackSubmission
from axis.customer_eto.tests.program_checks.test_washington_code_credit import (
    WashingtonCodeCreditProgramBase,
)

log = logging.getLogger(__name__)


class WashingtonCodeCreditCalculatorAPITest(WashingtonCodeCreditProgramBase, APITestCase):
    @classmethod
    def setUpTestData(cls):
        super(WashingtonCodeCreditCalculatorAPITest, cls).setUpTestData()
        from axis.core.tests.factories import rater_user_factory

        cls.user = rater_user_factory(company=cls.rater_company)
        cls.rater_company.update_permissions()

    def create(self, url, user, data=None, data_format="json"):
        """
        Return an object with the create action.
        """
        self.client.force_authenticate(user=user)
        response = self.client.post(url, data=data, format=data_format)
        data = response.data
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            "{url}: Unexpected status code {response.status_code}: {data}".format(**locals()),
        )
        return data

    def test_raw_calculator_api_post(self):
        """Test good data to Calculator"""
        data = self.default_program_data
        results = self.create(
            url=reverse_lazy("api_v3:washington_code_credit-calculator"),
            user=self.user,
            data=data,
        )
        for k, v in data.items():
            self.assertEqual(results["input"][k], v)
        self.assertIn("incentive_data", results)
        self.assertIn("incentive_data", results)

    def test_raw_calculator_api_fail_missing_data(self):
        """Test bad data to Calculator"""
        url = reverse_lazy("api_v3:washington_code_credit-calculator")

        data = self.default_program_data
        data.pop("ceiling_r_value")
        data.pop("window_u_value")

        self.client.force_authenticate(user=self.user)
        response = self.client.post(url, data=data, data_format="json")
        response_data = response.data
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            "{url}: Unexpected status code {response.status_code}: {data}".format(**locals()),
        )
        self.assertEqual(len(response_data.get("errors").keys()), 2)
        self.assertEqual(
            set(response_data.get("errors").keys()), {"ceiling_r_value", "window_u_value"}
        )

    def test_home_status_api_post_fail_no_data(self):
        url = reverse_lazy(
            "api_v3:washington_code_credit-generate", kwargs={"pk": self.home_status.pk}
        )

        self.client.force_authenticate(user=self.user)
        response = self.client.post(url)
        response_data = response.data

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn("errors", response_data)
        self.assertEqual(
            response_data["status"],
            "Input Error: 8 annotation errors; 17 checklist response errors",
        )
        self.assertIn("annotations", response_data["errors"])
        self.assertEqual(len(response_data["errors"]["annotations"]), 8)
        self.assertIn("checklist_questions", response_data["errors"])
        self.assertEqual(len(response_data["errors"]["checklist_questions"]), 17)

    def test_home_status_api_missing_data(self):
        """Test to make sure that a valid post will return data"""
        self.assertEqual(FastTrackSubmission.objects.count(), 0)
        url = reverse_lazy(
            "api_v3:washington_code_credit-generate", kwargs={"pk": self.home_status.pk}
        )

        data = self.default_program_data
        _post = {"wall_cavity_r_value": data.pop("wall_cavity_r_value")}
        self.add_required_responses(data)
        self.client.force_authenticate(user=self.user)

        response = self.client.post(url)
        with self.subTest("Initial Posting of missing data"):
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(FastTrackSubmission.objects.count(), 0)

        self.add_required_responses(_post)

        FastTrackSubmission.objects.all().delete()
        self.assertEqual(FastTrackSubmission.objects.count(), 0)

        response = self.client.post(url)
        with self.subTest("Final Posting of good data"):
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(FastTrackSubmission.objects.count(), 1)

    def test_home_status_api_post_pass(self):
        """Test to make sure that a valid post will return data"""
        self.assertEqual(FastTrackSubmission.objects.count(), 0)
        url = reverse_lazy(
            "api_v3:washington_code_credit-generate", kwargs={"pk": self.home_status.pk}
        )

        self.add_required_responses(self.default_program_data)
        self.client.force_authenticate(user=self.user)

        FastTrackSubmission.objects.all().delete()
        self.assertEqual(FastTrackSubmission.objects.count(), 0)

        response = self.client.post(url)
        with self.subTest("Initial Posting of good data"):
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertIn("reports", response.data)
            self.assertEqual(FastTrackSubmission.objects.count(), 1)
            fastrack = FastTrackSubmission.objects.get()
            self.assertEqual(fastrack.required_credits_to_meet_code, 6.0)
            self.assertEqual(fastrack.achieved_total_credits, 8.0)
            self.assertEqual(fastrack.eligible_gas_points, 1.5)
            self.assertEqual(fastrack.code_credit_incentive, 2400.0)
            self.assertEqual(fastrack.thermostat_incentive, 125.0)
            self.assertEqual(fastrack.fireplace_incentive, 0.0)
            self.assertEqual(fastrack.builder_incentive, 2525.0)
            self.assertEqual(fastrack.rater_incentive, 100.0)

        response = self.client.post(url)
        with self.subTest("Second Posting of good data"):
            self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
            self.assertIn("reports", response.data)
            self.assertEqual(FastTrackSubmission.objects.count(), 1)

    def test_home_status_with_max_data_storage(self):
        max_data = {
            "envelope_option": BuildingEnvelope.OPTION_1p6a.value,
            "air_leakage_option": AirLeakageControl.OPTION_2p4.value,
            "hvac_option": HighEfficiencyHVAC.OPTION_3p1.value,
            "hvac_distribution_option": HighEfficiencyHVACDistribution.OPTION_4p2.value,
            "dwhr_option": DWHR.OPTION_5p1.value,
            "water_heating_option": EfficientWaterHeating.OPTION_5p6.value,
            "renewable_electric_option": RenewableEnergy.OPTION_6p1b.value,
            "appliance_option": Appliances.OPTION_7p1.value,
            "conditioned_floor_area": 2500,
            "water_heating_fuel": WACCFuelType.ELECTRIC.value,
            "thermostat_type": ThermostatType.ECOBEE4.value,
            "fireplace_efficiency": FireplaceType.FP_70_75.value,
            "wall_cavity_r_value": 22,
            "wall_continuous_r_value": 16,
            "framing_type": "Advanced",
            "window_u_value": 0.16,
            "window_shgc": 1.0,
            "floor_cavity_r_value": 49,
            "slab_perimeter_r_value": 21,
            "under_slab_r_value": 21,
            "ceiling_r_value": 61,
            "raised_heel": "Yes",
            "air_leakage_ach": 0.5,
            "ventilation_type": VentilationType.HRV_ERV.value,
            "ventilation_brand": "Brand",
            "ventilation_model": "Model",
            "hrv_asre": 85.0,
            "furnace_brand": "Brand",
            "furnace_model": "Model",
            "furnace_afue": 97,
            "furnace_location": FurnaceLocation.CONDITIONED_SPACE.value,
            "duct_location": DuctLocation.CONDITIONED_SPACE.value,
            "duct_leakage": 4,
            "dwhr_installed": YesNo.YES.value,
            "water_heater_brand": "Brand",
            "water_heater_model": "Model",
            "gas_water_heater_uef": 0.92,
            "electric_water_heater_uef": 2.95,
        }

        url = reverse_lazy(
            "api_v3:washington_code_credit-generate", kwargs={"pk": self.home_status.pk}
        )
        self.add_required_responses(max_data)
        self.client.force_authenticate(user=self.user)

        FastTrackSubmission.objects.all().delete()
        self.assertEqual(FastTrackSubmission.objects.count(), 0)

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(FastTrackSubmission.objects.count(), 1)
        fastrack = FastTrackSubmission.objects.get()
        self.assertEqual(fastrack.required_credits_to_meet_code, 6.0)
        self.assertEqual(fastrack.achieved_total_credits, 12.5)
        self.assertEqual(fastrack.eligible_gas_points, 1.5)
        self.assertEqual(fastrack.code_credit_incentive, 2400.00)
        self.assertEqual(fastrack.thermostat_incentive, 125.0)
        self.assertEqual(fastrack.fireplace_incentive, 200.00)
        self.assertEqual(fastrack.builder_incentive, 2725.0)
        self.assertEqual(fastrack.rater_incentive, 100.0)
