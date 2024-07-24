"""test_eto_2022.py - Axis"""

__author__ = "Steven K"
__date__ = "3/16/22 14:07"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import json
import logging
import random

from analytics.management.commands.add_analytics_program import DevNull
from analytics.models import AnalyticRollup
from django.core import management
from django.urls import reverse_lazy
from rest_framework import status
from rest_framework.test import APITestCase
from simulation.analytics.simulation import AnalyticsMixin

from axis.core.tests.testcases import AxisTestCase
from axis.customer_eto.api_v3.serializers.analytics.analytics import (
    OutputSerializer,
    ETOAnalyticsSerializer,
    InsulationSerializer,
    MechanicalSerializer,
    DuctSerializer,
)
from axis.customer_eto.tests.program_checks.test_eto_2022 import (
    ETO2022ProgramCompleteTestMixin,
)
from axis.customer_eto.api_v3.serializers.analytics.home_analysis import (
    HomeOverViewSerializer,
    ETOHomeAnalysisSerializer,
    get_flat_analytic_rollup_results,
    EPSAdminSerializer,
    ModelComplexitySerializer,
    ModelInputsSerializer,
    HeatingAllocationSerializer,
    FieldQASerializer,
)

log = logging.getLogger(__name__)


class ETO2022AnalyticsSerializerTestMixin(ETO2022ProgramCompleteTestMixin):
    @classmethod
    def setUpTestData(cls):
        super(ETO2022AnalyticsSerializerTestMixin, cls).setUpTestData()

        management.call_command(
            "add_analytics_program",
            "-p",
            "eto-2022",
            stderr=DevNull(),
            stdout=DevNull(),
        )

        missing_checks = cls.home_status.report_eligibility_for_certification()
        assert len(missing_checks) == 0, missing_checks

    def run_analytics(self):
        management.call_command(
            "run_analytics",
            "-p",
            "eto-2022",
            "--immediate",
            "--force",
            stderr=DevNull(),
            stdout=DevNull(),
        )
        return AnalyticRollup.objects.get()

    def get_analytic(
        self, target: int | float | None = None, similar: list | None = None, **kw
    ) -> dict:
        if target is None:
            target = random.uniform(0, 10)
        if similar is None:
            similar = []
            for _i in range(3):
                similar.append(random.uniform(target * 0.95, target * 1.05))
            for _i in range(5):
                similar.append(random.uniform(target * 0.90, target * 1.1))
            for _i in range(10):
                similar.append(random.uniform(target * 0.80, target * 1.20))
            for _i in range(2):
                similar.append(random.uniform(target * 0.7, target * 1.30))

        mxin = AnalyticsMixin()
        result = mxin.calculate_core_analytics(target, similar)
        result["label"] = kw.pop("label", "Something")
        result.update(kw)
        return result


class ETO2022HomeAnalysisSerializerTests(ETO2022AnalyticsSerializerTestMixin, AxisTestCase):
    def test_home_overview_serializer(self):
        analytic = self.run_analytics()
        context = get_flat_analytic_rollup_results(analytic)
        with self.subTest("No Data"):
            serializer = HomeOverViewSerializer(instance=analytic, context={})
            self.assertGreater(serializer.data["warnings"], 0)
            self.assertEqual(len(serializer.data["fields"]), 10)

        with self.subTest("Generic Data"):
            serializer = HomeOverViewSerializer(instance=analytic, context=context)
            self.assertGreater(serializer.data["warnings"], 1)  # Min rater_builder_completed_homes
            self.assertEqual(len(serializer.data["fields"]), 10)

            serializer = ETOHomeAnalysisSerializer(instance=analytic, context=context)
            self.assertGreater(serializer.data["warnings"], 1)  # Min rater_builder_completed_homes

        with self.subTest("Matching Data"):
            serializer = HomeOverViewSerializer(
                instance=analytic,
                context={
                    "simulation_rating_company": "Rater Co.",
                    "rater": "Rater",
                    "simulation_rater_of_record": "Steven Ku",
                    "rater_of_record": "steveN ku ",
                    "simulation_builder": "BOB & BUILDER Co.",
                    "builder": "BOB and BUILDEr    ",
                    "simulation_property_address": "555 E. Maple",
                    "addresss_long": "555 e. Maple",
                    "rater_builder_completed_homes": 100,
                    "simulation_climate_zone": "5C",
                    "climate_zone": "5C",
                    "simulation_url": "/simu/12",
                    "simulation_external_url": "google.com/",
                    "source_type": "Something",
                },
            )
            self.assertEqual(serializer.data["warnings"], 0)
            self.assertEqual(len(serializer.data["fields"]), 10)

    def test_eps_admin_serializer(self):
        analytic = self.run_analytics()
        with self.subTest("No context"):
            serializer = EPSAdminSerializer(instance=analytic, context={})
            self.assertEqual(serializer.data["warnings"], 2)
            self.assertEqual(len(serializer.data["fields"]), 2)
        with self.subTest("Some Context"):
            serializer = EPSAdminSerializer(
                instance=analytic,
                context={
                    "eto-electric-elements": {"input": "Yeah"},
                    "fire-rebuild-qualification": {"input": "Sure"},
                    "is-adu": {"input": "No"},
                    "fuel_used": ["electric", "propane"],
                    "low_flow_fixtures_used": False,
                    "pipes_fully_insulated": True,
                },
            )
            self.assertEqual(serializer.data["warnings"], 3)
            self.assertEqual(len(serializer.data["fields"]), 3)

    def test_model_complexity_serializer(self):
        analytic = self.run_analytics()
        with self.subTest("No context"):
            serializer = ModelComplexitySerializer(instance=analytic, context={})
            self.assertEqual(serializer.data["warnings"], 2)  # Dryer Fuel, Shelter Class
            self.assertEqual(len(serializer.data["fields"]), 15)

        with self.subTest("No Errors"):
            serializer = ModelComplexitySerializer(
                instance=analytic,
                context={"shelter_class": 4, "dryer_fuel": "electric"},
            )
            self.assertEqual(serializer.data["warnings"], 0)

        with self.subTest("Basic"):
            serializer = ModelComplexitySerializer(
                instance=analytic,
                context={
                    "shelter_class": 4,
                    "qty_hot_water": {"value": 4},
                    "fixture_max_length": 12.0,
                    "dryer_fuel": "gas",
                },
            )
            self.assertEqual(serializer.data["warnings"], 1)

    def test_model_inputs_serializer(self):
        analytic = self.run_analytics()

        with self.subTest("No context"):
            serializer = ModelInputsSerializer(instance=analytic, context={})
            self.assertEqual(serializer.data["warnings"], 0)
            self.assertEqual(len(serializer.data["fields"]), 0)

        with self.subTest("model_heater_characteristics"):
            context = {
                "model_heater_characteristics": {
                    "warning": None,
                    "warnings": [],
                    "simulation": "Foo",
                    "checklist": "Bar",
                }
            }
            serializer = ModelInputsSerializer(instance=analytic, context=context)
            self.assertEqual(serializer.data["warnings"], 0)
            self.assertEqual(len(serializer.data["fields"]), 1)

        with self.subTest("model_heat_pump_characteristics"):
            context = {
                "model_heat_pump_characteristics": {
                    "warning": "Something",
                    "warnings": [],
                    "simulation": "Foo",
                    "checklist": "Bar",
                }
            }
            serializer = ModelInputsSerializer(instance=analytic, context=context)
            self.assertEqual(serializer.data["warnings"], 1)
            self.assertEqual(len(serializer.data["fields"]), 1)

        with self.subTest("model_heat_pump_cooling_characteristics"):
            context = {
                "model_heat_pump_cooling_characteristics": {
                    "warnings": ["XYS", "FOO"],
                    "simulation": "Foo",
                    "checklist": "Bar",
                }
            }
            serializer = ModelInputsSerializer(instance=analytic, context=context)
            self.assertEqual(serializer.data["warnings"], 2)
            self.assertEqual(len(serializer.data["fields"]), 1)

        remaining = [
            "model_water_heater_characteristics",
            "model_ventilation_characteristics",
            "model_exhaust_ventilation_characteristics",
            "model_supply_ventilation_characteristics",
            "model_balanced_ventilation_characteristics",
            "model_refrigerator_characteristics",
            "model_dishwasher_characteristics",
            "model_clothes_washer_characteristics",
            "model_clothes_dryer_characteristics",
            "model_pv_characteristics",
        ]
        for item in remaining:
            with self.subTest(f"{item}"):
                context = {
                    f"{item}": {
                        "warning": None,
                        "warnings": [],
                        "simulation": "Foo",
                        "checklist": "Bar",
                    }
                }
                serializer = ModelInputsSerializer(instance=analytic, context=context)
                self.assertEqual(serializer.data["warnings"], 0)
                self.assertEqual(len(serializer.data["fields"]), 1)

    def test_heating_allocations_serializer(self):
        analytic = self.run_analytics()
        context = get_flat_analytic_rollup_results(analytic)
        self.assertIsNotNone(context)

        with self.subTest("No context"):
            serializer = HeatingAllocationSerializer(instance=analytic, context={})
            self.assertEqual(serializer.data["warnings"], 0)
            self.assertEqual(len(serializer.data["values"]), 0)

            serializer = ETOHomeAnalysisSerializer(instance=analytic, context=context)
            self.assertIn("heating_allocations", serializer.data)

        with self.subTest("Context"):
            context = {
                "heating_load_allocations": {
                    "warning": None,
                    "values": ["Electric Heater with serving 100.0% heating"],
                },
                "cooling_load_allocations": {
                    "warning": "Crap",
                    "values": ["A", "B", "C"],
                },
            }
            serializer = HeatingAllocationSerializer(instance=analytic, context=context)
            self.assertEqual(serializer.data["warnings"], 1)
            self.assertEqual(serializer.data["warning"], "Crap")
            self.assertEqual(len(serializer.data["values"]), 4)

    def test_field_qa_serializer(self):
        analytic = self.run_analytics()
        context = get_flat_analytic_rollup_results(analytic)
        self.assertIsNotNone(context)

        with self.subTest("No context"):
            serializer = FieldQASerializer(instance=analytic, context={})
            self.assertEqual(serializer.data["warnings"], 0)
            self.assertEqual(len(serializer.data["fields"]), 0)

            serializer = ETOHomeAnalysisSerializer(instance=analytic, context=context)
            self.assertIn("field_qa", serializer.data)

        basic = {
            "input": "No",
            "comment": "",
            "_question": "Does this home have solar, electric vehicle, or storage elements?",
            "is_custom": None,
            "pretty": "No",
        }
        context = {
            "eto-electric-elements": basic.copy(),
            "qa-responses": {
                "eto-electric-elements": {"input": None},
            },
        }
        with self.subTest("Limited context"):
            serializer = FieldQASerializer(instance=analytic, context={})
            self.assertEqual(serializer.data["warnings"], 0)
            self.assertEqual(len(serializer.data["fields"]), 0)

            serializer = ETOHomeAnalysisSerializer(instance=analytic, context=context)
            self.assertIn("field_qa", serializer.data)

        with self.subTest("Mismatch context"):
            context["qa-responses"]["eto-electric-elements"] = basic.copy()
            context["qa-responses"]["eto-electric-elements"]["pretty"] = "Yes"
            serializer = FieldQASerializer(instance=analytic, context=context)
            self.assertEqual(serializer.data["warnings"], 1)
            self.assertEqual(len(serializer.data["fields"]), 1)

            serializer = ETOHomeAnalysisSerializer(instance=analytic, context=context)
            self.assertIn("field_qa", serializer.data)

        with self.subTest("Match context"):
            context["qa-responses"]["eto-electric-elements"] = basic.copy()
            serializer = FieldQASerializer(instance=analytic, context=context)
            self.assertEqual(serializer.data["warnings"], 0)
            self.assertEqual(len(serializer.data["fields"]), 1)


class ETO2022AnalyticsSerializerTests(ETO2022AnalyticsSerializerTestMixin, AxisTestCase):
    def test_output_analysis(self):
        analytic = self.run_analytics()
        context = get_flat_analytic_rollup_results(analytic)
        self.assertIsNotNone(context)

        with self.subTest("No context"):
            serializer = OutputSerializer(instance=analytic, context={})
            self.assertEqual(serializer.data["warnings"], 0)
            self.assertEqual(len(serializer.data["fields"]), 0)

            serializer = ETOAnalyticsSerializer(instance=analytic, context={})
            self.assertEqual(serializer.data["warnings"], 0)
            self.assertEqual(len(serializer.data["output_analysis"]), 2)

        with self.subTest("Context"):
            analytic = self.get_analytic()
            context = {"heating_consumption_kwh": analytic}
            serializer = OutputSerializer(instance=analytic, context=context)
            self.assertEqual(serializer.data["warnings"], 1 if analytic["warning"] else 0)

            serializer = ETOAnalyticsSerializer(instance=analytic, context=context)
            self.assertEqual(serializer.data["warnings"], 1 if analytic["warning"] else 0)
            self.assertEqual(len(serializer.data["output_analysis"]), 2)

    def test_insulation_analysis(self):
        analytic = self.run_analytics()
        context = get_flat_analytic_rollup_results(analytic)
        self.assertIsNotNone(context)

        with self.subTest("No context"):
            serializer = InsulationSerializer(instance=analytic, context={})
            self.assertEqual(serializer.data["warnings"], 0)
            self.assertEqual(len(serializer.data["fields"]), 0)

            serializer = ETOAnalyticsSerializer(instance=analytic, context={})
            self.assertEqual(serializer.data["warnings"], 0)
            self.assertEqual(len(serializer.data["insulation_analysis"]), 2)

        with self.subTest("Context"):
            analytic = self.get_analytic()
            context = {"total_frame_floor_area": analytic}
            serializer = InsulationSerializer(instance=analytic, context=context)
            self.assertEqual(serializer.data["warnings"], 1 if analytic["warning"] else 0)

            serializer = ETOAnalyticsSerializer(instance=analytic, context=context)
            self.assertEqual(serializer.data["warnings"], 1 if analytic["warning"] else 0)
            self.assertEqual(len(serializer.data["insulation_analysis"]), 2)

    def test_mechanical_analysis(self):
        analytic = self.run_analytics()
        context = get_flat_analytic_rollup_results(analytic)
        self.assertIsNotNone(context)

        with self.subTest("No context"):
            serializer = MechanicalSerializer(instance=analytic, context={})
            self.assertEqual(serializer.data["warnings"], 0)
            self.assertEqual(len(serializer.data["fields"]), 0)

            serializer = ETOAnalyticsSerializer(instance=analytic, context={})
            self.assertEqual(serializer.data["warnings"], 0)
            self.assertEqual(len(serializer.data["mechanical_analysis"]), 2)

        with self.subTest("Context"):
            analytic = self.get_analytic()
            context = {"heater_heating_capacity": analytic}
            serializer = MechanicalSerializer(instance=analytic, context=context)
            self.assertEqual(serializer.data["warnings"], 1 if analytic["warning"] else 0)

            serializer = ETOAnalyticsSerializer(instance=analytic, context=context)
            self.assertEqual(serializer.data["warnings"], 1 if analytic["warning"] else 0)
            self.assertEqual(len(serializer.data["mechanical_analysis"]), 2)

    def test_ducts_infiltration_analysis(self):
        analytic = self.run_analytics()
        context = get_flat_analytic_rollup_results(analytic)
        self.assertIsNotNone(context)

        with self.subTest("No context"):
            serializer = DuctSerializer(instance=analytic, context={})
            self.assertEqual(serializer.data["warnings"], 0)
            self.assertEqual(len(serializer.data["fields"]), 0)

            serializer = ETOAnalyticsSerializer(instance=analytic, context={})
            self.assertEqual(serializer.data["warnings"], 0)
            self.assertEqual(len(serializer.data["ducts_infiltration_analysis"]), 2)

        with self.subTest("Context"):
            analytic = self.get_analytic()
            context = {"heater_heating_capacity": analytic}
            serializer = DuctSerializer(instance=analytic, context=context)
            self.assertEqual(serializer.data["warnings"], 1 if analytic["warning"] else 0)

            serializer = ETOAnalyticsSerializer(instance=analytic, context=context)
            self.assertEqual(serializer.data["warnings"], 1 if analytic["warning"] else 0)
            self.assertEqual(len(serializer.data["ducts_infiltration_analysis"]), 2)


class ETO2022AnalyticsAnalyticTopLevel(ETO2022AnalyticsSerializerTestMixin, APITestCase):
    def test_analytics_examine_endpoint(self):
        analytics = self.run_analytics()

        url = f"/api/v2/analytics/{analytics.id}/region"
        self.client.force_authenticate(user=self.provider_user)
        response = self.client.get(url, follow=True)  # Follow is required.
        # print(json.dumps(response.data, indent=4, default=str))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail_template_url"], "/examine/analytics_eto_2022.html")
        self.assertEqual(response.data["object"]["program_name"], "Energy Trust Oregon - 2022")
        self.assertIn("home_analysis", response.data["object"])
        self.assertIn("analytics", response.data["object"])
