"""test_eto_2022.py - Axis"""

__author__ = "Steven K"
__date__ = "3/15/22 08:20"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import datetime
import json
import logging
from urllib.error import HTTPError
from unittest import mock
from urllib.parse import urlencode

from celery.exceptions import Retry
from django.conf import settings
from django.core import mail
from django.utils.timezone import now
from rest_framework import status
from rest_framework.reverse import reverse_lazy
from rest_framework.test import APITestCase

from axis.checklist.collection.test_mixins import CollectionRequestMixin
from axis.core.tests.api_v3.viewsets.test_task import MockAsyncResult
from axis.customer_eto.api_v3.serializers import EPS2022CalculatorSerializer
from axis.customer_eto.api_v3.serializers.project_tracker import ProjectTrackerXMLSerializer
from axis.customer_eto.api_v3.serializers.project_tracker.measures import MeasureSerializer
from axis.customer_eto.api_v3.viewsets import ProjectTrackerXMLViewSet
from axis.customer_eto.eep_programs.eto_2022 import (
    SmartThermostatBrands2022,
    AdditionalElements2022,
    SolarElements2022,
    CobidRegistered,
    CobidQualification,
)
from axis.customer_eto.eep_programs.fire_rebuild_2021 import FireResilienceBonus
from axis.customer_eto.enumerations import (
    PrimaryHeatingEquipment2020,
    Fireplace2020,
    YesNo,
    ProjectTrackerSubmissionStatus,
)
from axis.customer_eto.models import FastTrackSubmission
from axis.customer_eto.tasks import submit_fasttrack_xml
from axis.customer_eto.tests.program_checks.test_eto_2022 import ETO2022ProgramTestMixin
from axis.customer_eto.tests.factories import eto_mocked_soap_responses as mocked_post
from axis.geocoder.models import Geocode
from axis.incentive_payment.models import IncentivePaymentStatus

from simulation.enumerations import DistributionSystemType, FuelType, EnergyUnit

log = logging.getLogger(__name__)


class TestProjectTracker2022Mixin(ETO2022ProgramTestMixin):
    @classmethod
    def setUpTestData(cls):
        super(TestProjectTracker2022Mixin, cls).setUpTestData()
        from axis.core.tests.factories import rater_user_factory

        # Needed to get the calculator to validate
        cls.simulation = cls.home_status.floorplan.simulation
        cls.simulation.heaters.update(fuel=FuelType.NATURAL_GAS)
        cls.simulation.hvac_distribution_systems.update(
            system_type=DistributionSystemType.FORCED_AIR
        )
        summary = cls.simulation.as_designed_analysis.summary
        summary.solar_generation = summary.convert_value_to(
            5000.0, EnergyUnit.KWH, summary.consumption_units
        )
        summary.save()

        cls.user = rater_user_factory(company=cls.rater_company)
        cls.rater_company.update_permissions()

        collection_mixin = CollectionRequestMixin()
        data = {
            "primary-heating-equipment-type": PrimaryHeatingEquipment2020.GAS_FURNACE,
            "equipment-water-heater": {
                "input": {
                    "uef_cce": "3.2",
                    "capacity": "50",
                    "brand_name": "Rheem",
                    "converted_ef": "3.27",
                    "model_number": "PRO H50 T2 RH350BM",
                    "energy_factor": "-",
                }
            },
            "equipment-heat-pump-water-heater-serial-number": {"input": "2104122964708"},
            "equipment-gas-tank-water-heater-serial-number": {"input": "XD47640358"},
            "equipment-gas-tankless-water-heater-serial-number": {"input": "CA-012870"},
            "equipment-furnace": {
                "input": {
                    "ecm": "Y",
                    "afue": "96.3",
                    "motor_hp": " 3/4",
                    "brand_name": "Lennox",
                    "eae_kwh_yr": "416",
                    "model_number": "ML196UH090XE48C-*",
                    "capacity_mbtuh": "86",
                    "ventilation_fan_watts": "81.7",
                }
            },
            "equipment-heat-pump": {
                "input": {
                    "hspf": "8.5",
                    "seer": "16",
                    "motor_hp": "-",
                    "brand_name": "Mitsubishi",
                    "capacity_17f_kbtuh": "7.6",
                    "capacity_47f_kbtuh": "12.2",
                    "indoor_model_number": "MSZ-WR12NA-U1",
                    "outdoor_model_number": "MUZ-WR12NA-U1",
                    "ventilation_fan_watts": "-",
                    "cooling_capacity_kbtuh": "12",
                }
            },
            "equipment-heating-other-type": {"input": "Gas Fireplace"},
            "equipment-heating-other-brand": {"input": "Bryant"},
            "equipment-heating-other-model-number": {"input": "915SB36040E17A-B"},
            "smart-thermostat-brand": SmartThermostatBrands2022.BRYANT,
            "has-gas-fireplace": Fireplace2020.FE_60_69,
            "eto-electric-elements": AdditionalElements2022.ALL,
            "solar-elements": SolarElements2022.SOLAR_READY,
            "fire-rebuild-qualification": YesNo.YES,
            "fire-resilience-bonus": FireResilienceBonus.TRIPLE_PANE_AND_RIGID_INSULATION_AND_SEALED_ATTIC,
            "cobid-registered": CobidRegistered.BOTH,
            "cobid-type": CobidQualification.ALL,
            "builder-payment-redirected": YesNo.YES,
        }
        collection_mixin.add_bulk_answers(data=data, home_status=cls.home_status)

        serializer = EPS2022CalculatorSerializer(data={"home_status": cls.home_status.id})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        cls.calculator = serializer.calculator
        cls.project_tracker = FastTrackSubmission.objects.get()

        from axis.messaging.models import MessagingPreference

        for message_name in [
            "ProjectTrackerSuccessSubmissionMessage",
            "ProjectTrackerFailedSubmissionMessage",
        ]:
            MessagingPreference.objects.create(
                message_name=message_name,
                user=cls.provider_user,
                category="ETO",
                receive_email=True,
                receive_notification=True,
            )


class TestProjectTrackerETO2022(TestProjectTracker2022Mixin, APITestCase):
    def test_viewset_calculator_context_data(self):
        viewset = ProjectTrackerXMLViewSet()
        data = viewset.get_context_data(self.project_tracker)

        self.assertGreaterEqual(data["annual_cost_electric"], 0)
        self.assertAlmostEqual(
            data["annual_cost_electric"], self.calculator.improved_electric_cost, 2
        )

        self.assertGreater(data["annual_cost_gas"], 0)
        self.assertAlmostEqual(data["annual_cost_gas"], self.calculator.improved_gas_cost, 2)

        self.assertGreater(data["carbon_score"], 0)
        self.assertAlmostEqual(data["carbon_score"], self.calculator.carbon.carbon_score.total, 2)

        self.assertGreater(data["code_carbon_similar"], 0)
        self.assertAlmostEqual(
            data["code_carbon_score"], self.calculator.carbon.code_carbon_score.total, 2
        )

        self.assertIn("Pathway", data["eto_path"])
        self.assertEqual(data["home_config"], "Gas Heat - Gas DHW")

        self.assertGreater(data["code_eps_score"], 0)
        self.assertAlmostEqual(
            data["code_eps_score"], self.calculator.calculations.code_eps_score, 2
        )

        self.assertGreater(data["eps_similar"], 0)
        self.assertAlmostEqual(data["eps_similar"], self.calculator.projected.similar_size_eps, 2)

        self.assertGreater(data["total_kwh"], 0)
        self.assertAlmostEqual(data["total_kwh"], self.calculator.savings.kwh.proposed, 2)

        self.assertGreater(data["total_therms"], 0)
        self.assertAlmostEqual(data["total_therms"], self.calculator.savings.therm.proposed, 2)

        self.assertGreater(data["estimated_annual_cost"], 0)
        self.assertAlmostEqual(data["estimated_annual_cost"], self.calculator.annual_cost, 2)

        self.assertGreater(data["eps_score"], 0)
        self.assertAlmostEqual(data["eps_score"], self.calculator.calculations.eps_score, 2)

        self.assertGreater(data["estimated_monthly_cost"], 0)
        self.assertAlmostEqual(data["estimated_monthly_cost"], self.calculator.monthly_cost, 2)

        self.assertGreater(data["percentage_improvement"], 0)
        self.assertAlmostEqual(
            data["percentage_improvement"],
            self.calculator.savings.mbtu.floored_pct_improvement * 100.0,
            2,
        )

        self.assertGreater(data["electric_life"], 0)
        self.assertAlmostEqual(
            data["electric_life"], self.calculator.allocations.electric.measure_life, 2
        )

        self.assertEqual(data["electric_load_profile"], "Res Central AC")
        self.assertGreater(data["verifier_electric_incentive"], 0)
        self.assertAlmostEqual(
            data["verifier_electric_incentive"],
            round(self.calculator.allocations.electric.verifier_incentive, 0),
            2,
        )

        self.assertGreater(data["builder_electric_incentive"], 0)
        self.assertAlmostEqual(
            data["builder_electric_incentive"],
            round(
                max(
                    [
                        self.calculator.allocations.electric.builder_incentive
                        + self.calculator.allocations.pt_builder_heat_pump_water_heater_allocation.electric,
                        0,
                    ]
                ),
                0,
            ),
            2,
        )

        self.assertGreater(data["gas_life"], 0)
        self.assertAlmostEqual(data["gas_life"], self.calculator.allocations.gas.measure_life, 2)

        self.assertEqual(data["gas_load_profile"], "Res Heating")

        self.assertGreater(data["verifier_gas_incentive"], 0)
        self.assertAlmostEqual(
            data["verifier_gas_incentive"],
            round(self.calculator.allocations.gas.verifier_incentive),
            2,
        )

        self.assertGreater(data["builder_gas_incentive"], 0)
        self.assertAlmostEqual(
            data["builder_gas_incentive"],
            round(
                max(
                    [
                        self.calculator.allocations.gas.builder_incentive
                        + self.calculator.allocations.pt_builder_heat_pump_water_heater_allocation.gas,
                        0,
                    ]
                ),
                0,
            ),
            2,
        )

        self.assertGreater(data["kwh_savings"], 0)
        self.assertAlmostEqual(data["kwh_savings"], self.calculator.savings.kwh.savings, 2)
        self.assertGreater(data["therm_savings"], 0)
        self.assertAlmostEqual(data["therm_savings"], self.calculator.savings.therm.savings, 2)

        self.assertEqual(data["percentage_generation_kwh"], 0)
        self.assertAlmostEqual(
            data["percentage_generation_kwh"], self.calculator.percent_generation_kwh * 100, 2
        )
        self.assertAlmostEqual(
            data["percentage_generation_kwh"], self.project_tracker.percent_generation_kwh * 100, 2
        )

        self.assertGreater(data["percentage_therm_improvement"], 0)
        self.assertAlmostEqual(
            data["percentage_therm_improvement"],
            self.calculator.savings.therm.floored_pct_improvement * 100.0,
            2,
        )
        self.assertEqual(data["ev_ready_builder_incentive"], 200)

        # SLE
        self.assertEqual(data["net_zero_eps_incentive"], 0)
        self.assertEqual(data["solar_ready_builder_incentive"], 200)
        self.assertEqual(data["solar_ready_verifier_incentive"], 50)

        self.assertEqual(data["solar_storage_builder_incentive"], 200)
        self.assertGreater(data["cobid_builder_measure"], 0)
        self.assertAlmostEqual(
            data["cobid_builder_measure"],
            self.calculator.incentives.cobid_builder_incentive.incentive,
            2,
        )

        self.assertGreater(data["cobid_verifier_incentive"], 0)
        self.assertAlmostEqual(
            data["cobid_verifier_incentive"],
            self.calculator.incentives.cobid_verifier_incentive.incentive,
            2,
        )

        self.assertTrue(data["has_triple_pane_windows"])
        self.assertTrue(data["has_rigid_insulation"])
        self.assertTrue(data["has_sealed_attic"])
        self.assertEqual(data["water_heater_brand"], "Rheem")
        self.assertEqual(data["water_heater_model"], "PRO H50 T2 RH350BM")
        self.assertEqual(data["water_heater_heat_pump_sn"], "2104122964708")
        self.assertEqual(data["water_heater_gas_sn"], "XD47640358")
        self.assertEqual(data["water_heater_tankless_sn"], "CA-012870")
        self.assertEqual(data["primary_heating_type"], "Gas Furnace")
        self.assertEqual(data["furnace_brand"], "Lennox")
        self.assertEqual(data["furnace_model"], "ML196UH090XE48C-*")
        self.assertEqual(data["heat_pump_brand"], "Mitsubishi")
        self.assertEqual(data["heat_pump_model"], "MUZ-WR12NA-U1")
        self.assertEqual(data["heat_pump_sn"], "2104122964708")
        self.assertEqual(data["other_heater_type"], "Gas Fireplace")
        self.assertEqual(data["other_heater_brand"], "Bryant")
        self.assertEqual(data["other_heater_model"], "915SB36040E17A-B")
        self.assertEqual(data["has_battery_storage"], None)
        self.assertEqual(data["grid_harmonization_elements"], None)
        self.assertEqual(data["solar_elements"], "Solar Ready")
        self.assertEqual(data["thermostat_brand"], "Bryant Housewise WiFi model T6-WEM01-A")
        self.assertEqual(data["eto_additional_incentives"], None)
        self.assertEqual(data["electric_elements"], "Solar, electric vehicle and storage elements")
        self.assertEqual(data["gas_utility_code"], "NWN")
        self.assertEqual(data["electric_utility_code"], "PAC")
        self.assertEqual(data["fire_rebuild_qualification"], YesNo.YES.value)
        self.assertEqual(data["payment_redirected"], YesNo.YES.value)

    def test_updatable_fields(self):
        self.project_tracker.original_therm_savings = 99.95
        self.project_tracker.therm_savings = 90.01

        self.project_tracker.original_builder_gas_incentive = 89.89
        self.project_tracker.builder_gas_incentive = 98.98

        self.project_tracker.payment_change_datetime = now()
        self.project_tracker.save()

        viewset = ProjectTrackerXMLViewSet()
        data = viewset.get_context_data(self.project_tracker)

        self.assertAlmostEqual(float(data["therm_savings"]), 90.01, 2)
        self.assertAlmostEqual(float(data["builder_gas_incentive"]), 98.98, 2)

    def test_SLE_EPSNZ_measure(self):
        viewset = ProjectTrackerXMLViewSet()
        context = viewset.get_context_data(self.project_tracker)
        # Make sure we have it.
        context["project_type"] = "SLE"
        context["solar_ready_builder_incentive"] = 0.0
        context["solar_ready_verifier_incentive"] = 0.0

        if context["net_zero_eps_incentive"] == 0.0:
            context["net_zero_eps_incentive"] = 123.37

        serializer = MeasureSerializer(instance=self.project_tracker, context=context)
        measures = [x["Code"] for x in serializer.data["Measures"]["Measure"]]
        # print(measures)
        self.assertIn("EPSNZ", measures)
        measure_data = next(
            (x for x in serializer.data["Measures"]["Measure"] if x["Code"] == "EPSNZ"), None
        )
        self.assertIsNotNone(measure_data)
        self.assertEqual(measure_data["Incentive"], f'{context["net_zero_eps_incentive"]:.2f}')

        # Make sure our measure shows up for the builder
        serializer = ProjectTrackerXMLSerializer(instance=self.project_tracker, context=context)
        ally = serializer.data["soap:Envelope"]["soap:Body"]["FTImportXML"]["xmlIn"]["ETOImport"][
            "TradeAlly"
        ][0]
        self.assertEqual(ally["Associations"]["Projects"]["Project"]["Role"], "BUILDER")
        self.assertEqual(len(ally["Associations"]["Projects"]["Project"]["Measures"]["Measure"]), 2)

        # SLE Removed
        # value = next(
        #     (
        #         x
        #         for x in measure_data["Attributes"]["Attribute"]
        #         if x["Name"] == "PERCENTGENERATION"
        #     ),
        #     None,
        # )
        # self.assertAlmostEqual(value["Value"], context["percentage_generation_kwh"], 2)
        # value = next(
        #     (x for x in measure_data["Attributes"]["Attribute"] if x["Name"] == "GASIMPROV"), None
        # )
        # self.assertAlmostEqual(value["Value"], context["percentage_therm_improvement"], 2)

    def test_SOLRDYCON_builder_measure(self):
        viewset = ProjectTrackerXMLViewSet()
        context = viewset.get_context_data(self.project_tracker)
        context["solar_ready_builder_incentive"] = 123.30
        context["solar_ready_verifier_incentive"] = 0.0
        context["project_type"] = "SLE"

        serializer = MeasureSerializer(instance=self.project_tracker, context=context)
        measures = [x["Code"] for x in serializer.data["Measures"]["Measure"]]
        self.assertIn("SOLRDYCON", measures)
        measure_data = next(
            (x for x in serializer.data["Measures"]["Measure"] if x["Code"] == "SOLRDYCON"), None
        )
        self.assertIsNotNone(measure_data)
        self.assertEqual(
            measure_data["Incentive"], f'{context["solar_ready_builder_incentive"]:.2f}'
        )
        # Make sure our measure shows up for the builder
        serializer = ProjectTrackerXMLSerializer(instance=self.project_tracker, context=context)
        ally = serializer.data["soap:Envelope"]["soap:Body"]["FTImportXML"]["xmlIn"]["ETOImport"][
            "TradeAlly"
        ][0]
        self.assertEqual(ally["Associations"]["Projects"]["Project"]["Role"], "BUILDER")
        self.assertEqual(len(ally["Associations"]["Projects"]["Project"]["Measures"]["Measure"]), 2)

    def test_SOLRDYCON_verifier_measure(self):
        viewset = ProjectTrackerXMLViewSet()
        context = viewset.get_context_data(self.project_tracker)
        context["solar_ready_builder_incentive"] = 0.0
        context["solar_ready_verifier_incentive"] = 123.30
        context["project_type"] = "SLE"
        serializer = MeasureSerializer(instance=self.project_tracker, context=context)
        measures = [x["Code"] for x in serializer.data["Measures"]["Measure"]]
        self.assertIn("SOLRDYCON", measures)
        measure_data = next(
            (x for x in serializer.data["Measures"]["Measure"] if x["Code"] == "SOLRDYCON"), None
        )
        self.assertIsNotNone(measure_data)
        self.assertEqual(
            measure_data["Incentive"], f'{context["solar_ready_verifier_incentive"]:.2f}'
        )

        # Make sure our measure shows up for the builder
        serializer = ProjectTrackerXMLSerializer(instance=self.project_tracker, context=context)
        ally = serializer.data["soap:Envelope"]["soap:Body"]["FTImportXML"]["xmlIn"]["ETOImport"][
            "TradeAlly"
        ][1]
        self.assertEqual(ally["Associations"]["Projects"]["Project"]["Role"], "SOINSP")
        self.assertEqual(len(ally["Associations"]["Projects"]["Project"]["Measures"]["Measure"]), 1)

    def test_EPSESH_measure(self):
        viewset = ProjectTrackerXMLViewSet()
        context = viewset.get_context_data(self.project_tracker)

        context["ev_ready_builder_incentive"] = 500.00
        context["solar_storage_builder_incentive"] = 200.00

        with self.subTest("ENH"):
            context["project_type"] = "ENH"
            serializer = MeasureSerializer(instance=self.project_tracker, context=context)
            measures = [x["Code"] for x in serializer.data["Measures"]["Measure"]]
            self.assertIn("EPSESH", measures)
            measure_data = next(
                (x for x in serializer.data["Measures"]["Measure"] if x["Code"] == "EPSESH"), None
            )
            self.assertIsNotNone(measure_data)
            self.assertEqual(
                measure_data["Incentive"], f'{context["ev_ready_builder_incentive"]:.2f}'
            )
        with self.subTest("SLE"):
            context["project_type"] = "SLE"
            serializer = MeasureSerializer(instance=self.project_tracker, context=context)
            measures = [x["Code"] for x in serializer.data["Measures"]["Measure"]]
            self.assertIn("EPSESH", measures)
            measure_data = next(
                (x for x in serializer.data["Measures"]["Measure"] if x["Code"] == "EPSESH"), None
            )
            self.assertIsNotNone(measure_data)
            self.assertEqual(
                measure_data["Incentive"], f'{context["solar_storage_builder_incentive"]:.2f}'
            )

        with self.subTest("No SOLAR Storage"):
            context["solar_storage_builder_incentive"] = 0.00
            context["project_type"] = "SLE"
            serializer = MeasureSerializer(instance=self.project_tracker, context=context)
            measures = [x["Code"] for x in serializer.data["Measures"]["Measure"]]
            self.assertNotIn("EPSESH", measures)

    def test_DEIBONUSBUILDER_measure(self):
        viewset = ProjectTrackerXMLViewSet()
        context = viewset.get_context_data(self.project_tracker)

        serializer = MeasureSerializer(instance=self.project_tracker, context=context)
        measures = [x["Code"] for x in serializer.data["Measures"]["Measure"]]
        self.assertIn("DEIBONUSBUILDER", measures)
        measure_data = next(
            (x for x in serializer.data["Measures"]["Measure"] if x["Code"] == "DEIBONUSBUILDER"),
            None,
        )
        self.assertIsNotNone(measure_data)
        self.assertEqual(float(measure_data["Incentive"]), context["cobid_builder_measure"])

    def test_DEIBONUSVERIFIER_measure(self):
        viewset = ProjectTrackerXMLViewSet()
        context = viewset.get_context_data(self.project_tracker)

        serializer = MeasureSerializer(instance=self.project_tracker, context=context)
        measures = [x["Code"] for x in serializer.data["Measures"]["Measure"]]
        self.assertIn("DEIBONUSVERIFIER", measures)
        measure_data = next(
            (x for x in serializer.data["Measures"]["Measure"] if x["Code"] == "DEIBONUSVERIFIER"),
            None,
        )
        self.assertIsNotNone(measure_data)
        self.assertEqual(float(measure_data["Incentive"]), context["cobid_verifier_incentive"])

    def test_EPSFRFRTW_measure(self):
        viewset = ProjectTrackerXMLViewSet()
        context = viewset.get_context_data(self.project_tracker)
        self.assertEqual(context["fire_rebuild_qualification"], YesNo.YES.value)
        self.assertTrue(context["has_triple_pane_windows"])

        serializer = MeasureSerializer(instance=self.project_tracker, context=context)
        measures = [x["Code"] for x in serializer.data["Measures"]["Measure"]]
        self.assertIn("EPSFRFRTW", measures)
        self.assertIn("EPSFRELE", measures)
        self.assertIn("EPSFRGAS", measures)
        measure_data = next(
            (x for x in serializer.data["Measures"]["Measure"] if x["Code"] == "EPSFRFRTW"),
            None,
        )
        self.assertIsNotNone(measure_data)
        self.assertEqual(
            measure_data["Incentive"], str(self.project_tracker.triple_pane_window_incentive)
        )

    def test_EPSFRFREI_measure(self):
        viewset = ProjectTrackerXMLViewSet()
        context = viewset.get_context_data(self.project_tracker)
        self.assertEqual(context["fire_rebuild_qualification"], YesNo.YES.value)
        self.assertTrue(context["has_rigid_insulation"])

        serializer = MeasureSerializer(instance=self.project_tracker, context=context)
        measures = [x["Code"] for x in serializer.data["Measures"]["Measure"]]
        self.assertIn("EPSFRFREI", measures)
        self.assertIn("EPSFRELE", measures)
        self.assertIn("EPSFRGAS", measures)
        measure_data = next(
            (x for x in serializer.data["Measures"]["Measure"] if x["Code"] == "EPSFRFREI"),
            None,
        )
        self.assertIsNotNone(measure_data)
        self.assertEqual(
            measure_data["Incentive"], str(self.project_tracker.rigid_insulation_incentive)
        )

    def test_EPSFRFRSA_measure(self):
        viewset = ProjectTrackerXMLViewSet()
        context = viewset.get_context_data(self.project_tracker)
        self.assertEqual(context["fire_rebuild_qualification"], YesNo.YES.value)
        self.assertTrue(context["has_sealed_attic"])

        serializer = MeasureSerializer(instance=self.project_tracker, context=context)
        measures = [x["Code"] for x in serializer.data["Measures"]["Measure"]]
        self.assertIn("EPSFRFRSA", measures)
        self.assertIn("EPSFRELE", measures)
        self.assertIn("EPSFRGAS", measures)
        measure_data = next(
            (x for x in serializer.data["Measures"]["Measure"] if x["Code"] == "EPSFRFRSA"),
            None,
        )
        self.assertIsNotNone(measure_data)
        self.assertEqual(
            measure_data["Incentive"], str(self.project_tracker.sealed_attic_incentive)
        )

    def test_no_fire_measure(self):
        viewset = ProjectTrackerXMLViewSet()
        context = viewset.get_context_data(self.project_tracker)
        context["fire_rebuild_qualification"] = YesNo.NO.value
        context["has_triple_pane_windows"] = False
        context["has_rigid_insulation"] = None
        context["has_sealed_attic"] = False

        serializer = MeasureSerializer(instance=self.project_tracker, context=context)
        measures = [x["Code"] for x in serializer.data["Measures"]["Measure"]]
        self.assertNotIn("EPSFRFRTW", measures)
        self.assertNotIn("EPSFRFREI", measures)
        self.assertNotIn("EPSFRFRSA", measures)
        self.assertNotIn("EPSFRELE", measures)
        self.assertNotIn("EPSFRGAS", measures)

    def test_thermostat_brand(self):
        viewset = ProjectTrackerXMLViewSet()
        context = viewset.get_context_data(self.project_tracker)
        self.assertIsNotNone(context.get("thermostat_brand"))
        context["thermostat_brand"] = "Ecobee4"
        serializer = MeasureSerializer(instance=self.project_tracker, context=context)
        measures = [x["Code"] for x in serializer.data["Measures"]["Measure"]]
        self.assertIn("SMARTTHERMOEPS", measures)

    def test_sle_measure(self):
        viewset = ProjectTrackerXMLViewSet()
        context = viewset.get_context_data(self.project_tracker)
        context["pt_group"] = "SLE"
        pass

    def test_xml_basic(self):
        url = reverse_lazy("api_v3:project_tracker-xml", kwargs={"pk": self.home_status.pk})

        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @mock.patch("requests.post", side_effect=mocked_post)
    def test_submit_fastrack_xml_task(self, _mock):
        """Verify we can submit a project"""
        self.assertIn("stg", settings.FASTTRACK_API_ENDPOINT)
        self.assertEqual(FastTrackSubmission.objects.count(), 1)
        self.assertEqual(FastTrackSubmission.objects.get().project_id, "")
        self.assertEqual(IncentivePaymentStatus.objects.count(), 0)
        # Fake certify this pig.
        self.home_status.certification_date = datetime.date.today()
        self.home_status.state = "complete"
        self.home_status.save()

        # Submit this sucker
        with self.subTest("Failing XML Post"):
            # We send the raw data.
            Geocode.objects.all().update(raw_street_line1="BAD_API")
            self.assertRaises(
                (HTTPError, Retry, KeyError), submit_fasttrack_xml.delay, self.home_status.id
            )
            self.assertEqual(FastTrackSubmission.objects.count(), 1)
            self.assertEqual(FastTrackSubmission.objects.get().project_id, "")
            self.assertEqual(IncentivePaymentStatus.objects.count(), 0)

        with self.subTest("Passing XML Post"):
            Geocode.objects.all().update(raw_street_line1="200 N Church")
            FastTrackSubmission.objects.all().update(project_id="")
            submit_fasttrack_xml.delay(self.home_status.id)
            self.assertEqual(FastTrackSubmission.objects.count(), 1)
            project_id = f"P{str(self.home_status.id).zfill(11)}"
            self.assertEqual(FastTrackSubmission.objects.get().project_id, project_id)
            self.assertEqual(IncentivePaymentStatus.objects.count(), 1)

        with self.subTest("Get XML"):
            data = submit_fasttrack_xml(self.home_status.id, only_return_xml=True)
            self.assertIn("ETOImport", data)

    @mock.patch("requests.post", side_effect=mocked_post)
    def test_submit_api_endpoint(self, _mock):
        self.assertIn("stg", settings.FASTTRACK_API_ENDPOINT)
        self.assertEqual(FastTrackSubmission.objects.count(), 1)
        self.assertEqual(FastTrackSubmission.objects.get().project_id, "")
        self.assertEqual(IncentivePaymentStatus.objects.count(), 0)

        # Fake certify this pig.
        self.home_status.certification_date = datetime.date.today()
        self.home_status.state = "complete"
        self.home_status.save()

        self.assertIn(
            "customer_eto.view_fasttracksubmission", self.provider_user.get_all_permissions()
        )
        self.assertEqual(len(mail.outbox), 0)

        with self.subTest("Failing XML Post"):
            # We send the raw data.
            Geocode.objects.all().update(raw_street_line1="BAD_API")
            url = reverse_lazy("api_v3:project_tracker-submit", kwargs={"pk": self.home_status.id})
            self.client.force_authenticate(user=self.provider_user)
            self.assertRaises((HTTPError, Retry, KeyError), self.client.post, url)
            self.assertEqual(FastTrackSubmission.objects.get().project_id, "")
            self.assertEqual(IncentivePaymentStatus.objects.count(), 0)
            self.assertEqual(self.provider_user.is_company_admin, True)

        with self.subTest("Passing XML Post"):
            Geocode.objects.all().update(raw_street_line1="200 N Church")
            FastTrackSubmission.objects.all().update(project_id="", submit_status=None)
            url = reverse_lazy("api_v3:project_tracker-submit", kwargs={"pk": self.home_status.id})
            self.client.force_authenticate(user=self.provider_user)
            response = self.client.post(url)
            data = response.json()
            self.assertEqual(data["id"], self.home_status.id)
            self.assertIn("ENH and SLE PT on home ", data["content"])
            self.assertEqual(data["project_types"], ["ENH", "SLE"])
            self.assertEqual(len(data["task_ids"]), 2)
            self.assertEqual(response.status_code, 202)
            project_id = f"P{str(self.home_status.id).zfill(11)}"
            self.assertEqual(FastTrackSubmission.objects.get().project_id, project_id)
            self.assertEqual(IncentivePaymentStatus.objects.count(), 1)
            self.assertEqual(len(mail.outbox), 2)  # One for SLE and ENH

            # for item in FastTrackSubmission.objects.get().history.all().order_by("history_id"):
            #     print(
            #         f"{item.home_status.id=} {item.home_status.state=} {item.project_id=} "
            #         f"{item.solar_project_id=} {item.submit_status=} {item.submit_user}"
            #     )

        with self.subTest("Prevent Back to Back XML Post"):
            Geocode.objects.all().update(raw_street_line1="200 N Church")
            url = reverse_lazy("api_v3:project_tracker-submit", kwargs={"pk": self.home_status.id})
            self.client.force_authenticate(user=self.provider_user)
            response = self.client.post(url)
            self.assertEqual(response.status_code, 400)

        with self.subTest("Get XML"):
            url = reverse_lazy("api_v3:project_tracker-xml", kwargs={"pk": self.home_status.id})
            self.client.force_authenticate(user=self.provider_user)
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"ETOImport", response.content)

    @mock.patch(
        "axis.core.api_v3.serializers.task.CeleryAsyncResultSerializer.get_async_result",
        MockAsyncResult,
    )
    def test_status_endpoint(self):
        """This will test out the status endpoint"""
        self.assertIn("stg", settings.FASTTRACK_API_ENDPOINT)
        self.assertEqual(FastTrackSubmission.objects.count(), 1)
        self.assertEqual(FastTrackSubmission.objects.get().project_id, "")
        self.assertEqual(IncentivePaymentStatus.objects.count(), 0)

        # Fake certify this pig.
        self.home_status.certification_date = datetime.date.today()
        self.home_status.state = "complete"
        self.home_status.save()

        submission = FastTrackSubmission.objects.get()
        submission.submit_status = ProjectTrackerSubmissionStatus.SUBMITTED
        submission.solar_submit_status = ProjectTrackerSubmissionStatus.SUBMITTED
        submission.save()

        # When we submit a job we are given the corresponding task ids back.  Our job is to get a unified answer

        # When a job is first kicked off submitted is the norm there isn't and Async Result yet.
        base_url = reverse_lazy(
            "api_v3:project_tracker-status",
            kwargs={"pk": self.home_status.id},
        )
        with self.subTest("Submitted"):
            task_ids = (
                "10bc50f6-b24c-4f9e-a08c-c0435495c688",
                "10bc50f6-b24c-4f9e-a08c-c0435495c689",
            )
            url = base_url + f"?{urlencode(dict(task_ids=','.join(task_ids)))}"
            self.client.force_authenticate(user=self.provider_user)
            response = self.client.get(url)
            data = response.json()
            # print(json.dumps(data, indent=4))
            self.assertEqual(data["status"], ProjectTrackerSubmissionStatus.SUBMITTED)
            self.assertIn("submitted", data["result"])
            self.assertEqual(data["task_ids"], list(task_ids))
            self.assertIn("kwargs", data["task_statuses"][0])
            self.assertIn("result", data["task_statuses"][0])
            self.assertIn("args", data["task_statuses"][0])
            self.assertIn("date_done", data["task_statuses"][0])

        with self.subTest("One Started"):
            task_ids = (
                "10bc50f6-b24c-4f9e-a08c-c0435495c688",
                "32bc50f6-b24c-4f9e-a08c-c0435495c689",
            )
            url = base_url + f"?{urlencode(dict(task_ids=','.join(task_ids)))}"
            self.client.force_authenticate(user=self.provider_user)
            response = self.client.get(url)
            data = response.json()
            self.assertEqual(data["status"], ProjectTrackerSubmissionStatus.STARTED)
            self.assertIn("started", data["result"])

        with self.subTest("Both Started"):
            task_ids = (
                "32bc50f6-b24c-4f9e-a08c-c0435495c688",
                "32bc50f6-b24c-4f9e-a08c-c0435495c689",
            )
            url = base_url + f"?{urlencode(dict(task_ids=','.join(task_ids)))}"
            self.client.force_authenticate(user=self.provider_user)
            response = self.client.get(url)
            data = response.json()
            self.assertEqual(data["status"], ProjectTrackerSubmissionStatus.STARTED)
            self.assertIn("started", data["result"])

        with self.subTest("A failing PT Push"):
            task_ids = (
                "27ac50f6-b24c-4f9e-a08c-c0435495c688",
                "27cc50f6-b24c-4f9e-a08c-c0435495c689",
            )
            url = base_url + f"?{urlencode(dict(task_ids=','.join(task_ids)))}"
            self.client.force_authenticate(user=self.provider_user)
            response = self.client.get(url)
            data = response.json()
            self.assertEqual(data["status"], ProjectTrackerSubmissionStatus.FAILURE)
            self.assertIn("submission Error", data["result"])
            self.assertIn("SLE Project", data["result"])

        with self.subTest("Successes"):
            task_ids = (
                "27bc50f6-b24c-4f9e-a08c-c0435495c688",
                "27cc50f6-b24c-4f9e-a08c-c0435495c689",
            )
            url = base_url + f"?{urlencode(dict(task_ids=','.join(task_ids)))}"
            self.client.force_authenticate(user=self.provider_user)
            response = self.client.get(url)
            data = response.json()
            self.assertEqual(data["status"], ProjectTrackerSubmissionStatus.SUCCESS)
            self.assertIn("ENH Project", data["result"])
            self.assertIn("SLE Project", data["result"])

        with self.subTest("No Task ID Presented"):
            self.client.force_authenticate(user=self.provider_user)
            response = self.client.get(base_url)
            data = response.json()
            self.assertEqual(data["status"], ProjectTrackerSubmissionStatus.SUBMITTED)
            self.assertIn("ENH: submitted", data["result"])
            self.assertIn("SLE: submitted", data["result"])

        with self.subTest("No Task ID Presented Started"):
            submission = FastTrackSubmission.objects.get()
            submission.submit_status = ProjectTrackerSubmissionStatus.STARTED
            submission.solar_submit_status = ProjectTrackerSubmissionStatus.SUCCESS
            submission.save()
            self.client.force_authenticate(user=self.provider_user)
            response = self.client.get(base_url)
            data = response.json()
            self.assertEqual(data["status"], ProjectTrackerSubmissionStatus.STARTED)
            self.assertIn("ENH: started", data["result"])
            self.assertIn("SLE: success", data["result"])

        with self.subTest("No Task ID Presented Completed"):
            submission = FastTrackSubmission.objects.get()
            submission.project_id = "FOO"
            submission.submit_status = ProjectTrackerSubmissionStatus.SUCCESS
            submission.solar_submit_status = ProjectTrackerSubmissionStatus.FAILURE
            submission.save()
            self.client.force_authenticate(user=self.provider_user)
            response = self.client.get(base_url)
            data = response.json()
            self.assertEqual(data["status"], ProjectTrackerSubmissionStatus.FAILURE)
            self.assertIn("ENH: FOO identified.", data["result"])
            self.assertIn("SLE: failure", data["result"])

    def test_notes_project(self):
        viewset = ProjectTrackerXMLViewSet()
        context = viewset.get_context_data(self.project_tracker)
        with self.subTest("ENH Notes"):
            self.assertEqual(context["fire_rebuild_qualification"], YesNo.YES.value)
            self.assertEqual(context["payment_redirected"], YesNo.YES.value)
            context["project_type"] = "ENH"

            serializer = ProjectTrackerXMLSerializer(instance=self.project_tracker, context=context)
            notes = serializer.data["soap:Envelope"]["soap:Body"]["FTImportXML"]["xmlIn"][
                "ETOImport"
            ]["Project"]["Notes"]
            self.assertEqual(notes, "Fire Rebuild, Payment Redirect")

        with self.subTest("SLE Notes"):
            context = viewset.get_context_data(self.project_tracker)
            self.assertEqual(context["fire_rebuild_qualification"], YesNo.YES.value)
            self.assertEqual(context["payment_redirected"], YesNo.YES.value)
            context["project_type"] = "SLE"

            serializer = ProjectTrackerXMLSerializer(instance=self.project_tracker, context=context)
            notes = serializer.data["soap:Envelope"]["soap:Body"]["FTImportXML"]["xmlIn"][
                "ETOImport"
            ]["Project"]["Notes"]
            self.assertEqual(notes, "")
