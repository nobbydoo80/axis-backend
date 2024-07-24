"""test_eto_2021_fire.py - Axis"""

__author__ = "Steven K"
__date__ = "12/4/21 09:56"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
import datetime
from decimal import Decimal

from django.urls import reverse_lazy

from rest_framework import status
from rest_framework.test import APITestCase

from axis.checklist.collection.test_mixins import CollectionRequestMixin
from axis.customer_eto.api_v3.serializers import EPSFire2021CalculatorSerializer
from axis.customer_eto.eep_programs.fire_rebuild_2021 import FireResilienceBonus
from axis.customer_eto.enumerations import (
    PrimaryHeatingEquipment2020,
    SmartThermostatBrands2020,
    Fireplace2020,
    GridHarmonization2020,
    AdditionalIncentives2020,
    SolarElements2020,
    YesNo,
)
from axis.customer_eto.models import FastTrackSubmission
from axis.customer_eto.tests.program_checks.test_fire_rebuild_2021 import (
    FireRebuild2021ProgramTestMixin,
)
from axis.floorplan.models import Floorplan

log = logging.getLogger(__name__)


class EPSFire2021CalculatorAPITest(
    FireRebuild2021ProgramTestMixin, APITestCase, CollectionRequestMixin
):
    @classmethod
    def setUpTestData(cls):
        super(EPSFire2021CalculatorAPITest, cls).setUpTestData()
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
            url=reverse_lazy("api_v3:eto_fire_2021-calculator"),  # NOTE: Pattern on slug.
            user=self.user,
            data=data,
        )

        for k, v in data.items():
            self.assertEqual(results["input"][k], v)

    def test_raw_calculator_api_fail_missing_data(self):
        """Test bad data to Calculator"""
        url = reverse_lazy("api_v3:eto_fire_2021-calculator")

        data = self.default_program_data
        data.pop("climate_location")
        data.pop("conditioned_area")

        self.client.force_authenticate(user=self.user)
        response = self.client.post(url, data=data, data_format="json")
        response_data = response.data
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            "{url}: Unexpected status code {response.status_code}: {data}".format(**locals()),
        )
        self.assertEqual(len(response_data.get("errors").keys()), 2, response_data.get("errors"))

        self.assertEqual(
            set(response_data.get("errors").keys()), {"climate_location", "conditioned_area"}
        )

    def test_home_status_api_post_fail_no_data(self):
        url = reverse_lazy("api_v3:eto_fire_2021-generate", kwargs={"pk": self.home_status.pk})

        Floorplan.objects.update(simulation=None)

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
            "Input Error: 1 Simulation errors; 1 checklist response errors",
        )
        self.assertIn("simulation", response_data["errors"])
        self.assertEqual(len(response_data["errors"]["simulation"]), 1)
        self.assertIn("checklist_questions", response_data["errors"])
        self.assertEqual(len(response_data["errors"]["checklist_questions"]), 1)

    def test_inputs(self):
        """Test out the inputs will traverse"""

        self.add_collected_input(
            value=PrimaryHeatingEquipment2020.GAS_FURNACE.value,
            measure_id="primary-heating-equipment-type",
            home_status=self.home_status,
        )
        self.add_collected_input(
            value=SmartThermostatBrands2020.BRYANT.value,
            measure_id="smart-thermostat-brand",
            home_status=self.home_status,
        )
        self.add_collected_input(
            value=Fireplace2020.FE_60_69.value,
            measure_id="has-gas-fireplace",
            home_status=self.home_status,
        )
        self.add_collected_input(
            value=GridHarmonization2020.ALL.value,
            measure_id="grid-harmonization-elements",
            home_status=self.home_status,
        )
        self.add_collected_input(
            value=AdditionalIncentives2020.ENERGY_SMART.value,
            measure_id="eto-additional-incentives",
            home_status=self.home_status,
        )
        self.add_collected_input(
            value=SolarElements2020.SOLAR_PV.value,
            measure_id="solar-elements",
            home_status=self.home_status,
        )
        self.add_collected_input(
            value="200",
            measure_id="ets-annual-etsa-kwh",
            home_status=self.home_status,
        )
        self.add_collected_input(
            value=FireResilienceBonus.TRIPLE_PANE_AND_RIGID_INSULATION.value,
            measure_id="fire-resilience-bonus",
            home_status=self.home_status,
        )
        self.add_collected_input(
            value=YesNo.YES.value,
            measure_id="fire-rebuild-qualification",
            home_status=self.home_status,
        )

        serializer = EPSFire2021CalculatorSerializer(data={"home_status": self.home_status.id})
        self.assertTrue(serializer.is_valid(raise_exception=True))

        self.assertEqual(
            serializer.calculator.primary_heating_class,
            PrimaryHeatingEquipment2020.GAS_FURNACE,
        )
        self.assertEqual(
            serializer.calculator.thermostat_brand,
            SmartThermostatBrands2020.BRYANT,
        )
        self.assertEqual(
            serializer.calculator.fireplace,
            Fireplace2020.FE_60_69,
        )
        self.assertEqual(
            serializer.calculator.grid_harmonization_elements,
            GridHarmonization2020.ALL,
        )
        self.assertEqual(
            serializer.calculator.eps_additional_incentives,
            AdditionalIncentives2020.ENERGY_SMART,
        )
        self.assertEqual(
            serializer.calculator.solar_elements,
            SolarElements2020.SOLAR_PV,
        )
        self.assertEqual(serializer.calculator.improved.pv_kwh, 200.0)
        self.assertEqual(
            serializer.calculator.fire_resilience_bonus,
            FireResilienceBonus.TRIPLE_PANE_AND_RIGID_INSULATION,
        )
        self.assertEqual(
            serializer.calculator.fire_rebuild_qualification,
            YesNo.YES,
        )

    def test_home_status_api_post_solid_data(self):
        url = reverse_lazy("api_v3:eto_fire_2021-generate", kwargs={"pk": self.home_status.pk})

        data = {
            "primary-heating-equipment-type": PrimaryHeatingEquipment2020.GAS_FURNACE,
            "fire-resilience-bonus": FireResilienceBonus.TRIPLE_PANE_AND_RIGID_INSULATION_AND_SEALED_ATTIC,
            "fire-rebuild-qualification": YesNo.YES,
        }
        self.add_bulk_answers(data=data, home_status=self.home_status)

        self.client.force_authenticate(user=self.user)
        response = self.client.post(url)
        # response_data = response.data
        # print(response_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.json())

        # We don't save it we simply want the calculator to verify our values.
        serializer = EPSFire2021CalculatorSerializer(data={"home_status": self.home_status.pk})
        self.assertTrue(serializer.is_valid(raise_exception=True))
        serializer.to_internal_value(data={"home_status": self.home_status.pk})
        calculator = serializer.calculator

        self.assertEqual(FastTrackSubmission.objects.count(), 1)
        fastrack_1 = FastTrackSubmission.objects.get()

        self.assertEqual(fastrack_1.home_status, self.home_status)

        self.assertEqual(calculator.net_zero.triple_pane_window_incentive, Decimal("750.00"))
        self.assertEqual(
            fastrack_1.triple_pane_window_incentive,
            calculator.net_zero.triple_pane_window_incentive,
        )

        self.assertEqual(calculator.net_zero.rigid_insulation_incentive, Decimal("750.00"))
        self.assertEqual(
            fastrack_1.rigid_insulation_incentive, calculator.net_zero.rigid_insulation_incentive
        )

        self.assertEqual(calculator.net_zero.sealed_attic_incentive, Decimal("400.00"))
        self.assertEqual(
            fastrack_1.sealed_attic_incentive, calculator.net_zero.sealed_attic_incentive
        )

        self.assertEqual(fastrack_1.project_id, "")

        response = self.client.post(url)
        self.assertEqual(
            response.status_code,
            status.HTTP_202_ACCEPTED,
        )

        self.assertEqual(FastTrackSubmission.objects.count(), 1)
        FastTrackSubmission.objects.get()

        # print(response.json())
