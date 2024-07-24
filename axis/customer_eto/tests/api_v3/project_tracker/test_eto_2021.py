"""test_eto_2021.py - Axis"""

__author__ = "Steven K"
__date__ = "9/27/21 09:34"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import datetime
import json
import logging
from unittest import mock
from urllib.error import HTTPError

from celery.exceptions import Retry
from django.conf import settings
from django.urls import reverse_lazy
from rest_framework import status
from rest_framework.test import APITestCase

from axis.checklist.collection.test_mixins import CollectionRequestMixin
from axis.company.models import Company
from axis.home.models import Home
from axis.incentive_payment.models import IncentivePaymentStatus
from simulation.enumerations import FuelType, DistributionSystemType
from ...factories import eto_mocked_soap_responses as mocked_post
from ...program_checks.test_eto_2021 import ETO2021ProgramTestMixin
from ....api_v3.serializers.project_tracker import ProjectTrackerXMLSerializer
from ....api_v3.viewsets import ProjectTrackerXMLViewSet
from ....models import FastTrackSubmission
from ....tasks import submit_fasttrack_xml

log = logging.getLogger(__name__)


class TestProjectTrackerETO2021(ETO2021ProgramTestMixin, APITestCase):
    @classmethod
    def setUpTestData(cls):
        super(TestProjectTrackerETO2021, cls).setUpTestData()
        from axis.core.tests.factories import rater_user_factory

        # Needed to get the calculator to validate
        cls.simulation = cls.home_status.floorplan.simulation
        cls.simulation.heaters.update(fuel=FuelType.NATURAL_GAS)
        cls.simulation.hvac_distribution_systems.update(
            system_type=DistributionSystemType.FORCED_AIR
        )

        cls.user = rater_user_factory(company=cls.rater_company)
        cls.rater_company.update_permissions()

        collection_mixin = CollectionRequestMixin()
        data = {
            "primary-heating-equipment-type": "Gas Furnace",
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
            "has-battery-storage": {"input": "Yes"},
            "grid-harmonization-elements": {
                "input": "Energy smart homes – Base package + " "advanced wiring"
            },
            "ets-annual-etsa-kwh": {"input": 25000},
            "solar-elements": {"input": "Solar PV"},
            "smart-thermostat-brand": {"input": "Ecobee4"},
            "eto-additional-incentives": {"input": "Solar elements and energy smart homes"},
        }
        collection_mixin.add_bulk_answers(data=data, home_status=cls.home_status)

        cls.project_tracker = FastTrackSubmission.objects.create(
            home_status=cls.home_status,
            builder_incentive=125.69,
            rater_incentive=225.21,
        )

    def render(self, response):
        response.render()
        return response.content.decode("utf8")

    def test_viewset_calculator_context_data(self):
        viewset = ProjectTrackerXMLViewSet()
        data = viewset.get_context_data(self.project_tracker)

        # for k, v in data.items():
        #     print(k, v)
        #     if isinstance(v, str):
        #         print(f"self.assertEqual(data[{k!r}], {v!r})")
        #     elif isinstance(v, (float, int)):
        #         if float(v) == 0.0:
        #             print(f"self.assertEqual(round(data[{k!r}], 2), 0)")
        #         else:
        #             print(f"self.assertGreater(round(data[{k!r}], 2), 0)")
        #     else:
        #         print(f"self.assertEqual(data[{k!r}], {v!r})")

        self.assertGreater(round(data["annual_cost_electric"], 2), 0)
        self.assertGreater(round(data["annual_cost_gas"], 2), 0)
        self.assertEqual(round(data["carbon_score"], 2), 0)
        self.assertGreater(round(data["code_carbon_score"], 2), 0)
        self.assertGreater(round(data["code_carbon_similar"], 2), 0)
        self.assertEqual(data["eto_path"], "Pathway 2")
        self.assertEqual(data["home_config"], "Gas Heat - Gas DHW")
        self.assertGreater(round(data["code_eps_score"], 2), 0)
        self.assertGreater(round(data["eps_similar"], 2), 0)
        self.assertGreater(round(data["total_therms"], 2), 0)
        self.assertGreater(round(data["estimated_annual_cost"], 2), 0)
        self.assertEqual(round(data["eps_score"], 2), 0)
        self.assertGreater(round(data["estimated_monthly_cost"], 2), 0)
        self.assertGreater(int(round(data["percentage_improvement"])), 19)
        self.assertGreater(round(data["electric_life"], 2), 0)
        self.assertEqual(data["electric_load_profile"], "Res Space Conditioning")
        self.assertGreater(round(data["verifier_electric_incentive"], 2), 0)
        self.assertGreater(round(data["builder_electric_incentive"], 2), 0)
        self.assertGreater(round(data["gas_life"], 2), 0)
        self.assertEqual(data["gas_load_profile"], "Res Heating")
        self.assertGreater(round(data["verifier_gas_incentive"], 2), 0)
        self.assertGreater(round(data["builder_gas_incentive"], 2), 0)
        self.assertGreater(round(data["kwh_savings"], 2), 0)
        self.assertGreater(round(data["therm_savings"], 2), 0)
        self.assertGreater(round(data["net_zero_eps_incentive"], 2), 0)
        self.assertGreater(round(data["percentage_generation_kwh"], 2), 0)
        self.assertGreater(round(data["percentage_therm_improvement"], 2), 0)
        self.assertGreater(round(data["energy_smart_homes_eps_incentive"], 2), 0)

    def test_viewset_collected_input_context_data(self):
        viewset = ProjectTrackerXMLViewSet()
        data = viewset.get_collected_input_context(self.project_tracker)

        # for k, v in data.items():
        #     if isinstance(v, (str, type(None))):
        #         print(f"self.assertEqual(data[{k!r}], {v!r})")
        #     else:
        #         print(f"self.assertGreater(round(data[{k!r}], 2), 0)")

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

        self.assertEqual(data["has_battery_storage"], "Yes")
        self.assertEqual(
            data["grid_harmonization_elements"],
            "Energy smart homes – Base package + advanced wiring",
        )
        self.assertEqual(data["solar_elements"], "Solar PV")
        self.assertEqual(data["thermostat_brand"], "Ecobee4")
        self.assertEqual(data["eto_additional_incentives"], "Solar elements and energy smart homes")

    def test_viewset_utility_codes_context_data(self):
        self.assertEqual(self.home_status.home.get_electric_company().slug, "pacific-power")
        self.assertEqual(self.home_status.home.get_gas_company().slug, "nw-natural-gas")
        viewset = ProjectTrackerXMLViewSet()
        data = viewset.get_utility_codes_context(self.project_tracker)
        self.assertEqual(data["gas_utility_code"], "NWN")
        self.assertEqual(data["electric_utility_code"], "PAC")

        Company.objects.filter(slug="pacific-power").update(slug="XXX")
        Company.objects.filter(slug="nw-natural-gas").update(slug="YYY")

        viewset = ProjectTrackerXMLViewSet()
        data = viewset.get_utility_codes_context(self.project_tracker)
        self.assertEqual(data["gas_utility_code"], "N/A")
        self.assertEqual(data["electric_utility_code"], "N/A")

    def test_top_structure(self):
        viewset = ProjectTrackerXMLViewSet()
        context = viewset.get_eto_2021_calculator_context(self.project_tracker)
        context.update(viewset.get_collected_input_context(self.project_tracker))
        context.update(viewset.get_utility_codes_context(self.project_tracker))

        serializer = ProjectTrackerXMLSerializer(instance=self.project_tracker, context=context)
        data = serializer.to_representation(self.project_tracker)

        with self.subTest("Top Level Organizational SOAP Validations"):
            self.assertIn("soap:Envelope", data)
            self.assertIn("soap:Body", data["soap:Envelope"])
            self.assertIn("FTImportXML", data["soap:Envelope"]["soap:Body"])
            self.assertIn("xmlIn", data["soap:Envelope"]["soap:Body"]["FTImportXML"])
            self.assertIn("ETOImport", data["soap:Envelope"]["soap:Body"]["FTImportXML"]["xmlIn"])
        with self.subTest("ETO Import Keys"):
            data = data["soap:Envelope"]["soap:Body"]["FTImportXML"]["xmlIn"]
            self.assertIn("ETOImport", data)
            self.assertIn("ImportCode", data["ETOImport"])
            self.assertIn("APIKey", data["ETOImport"])
            self.assertIn("Project", data["ETOImport"])
            self.assertIn("Site", data["ETOImport"])
            self.assertIn("TradeAlly", data["ETOImport"])

        data = data["ETOImport"]
        # print(json.dumps(data, indent=4))
        measures = data["Project"]["Measures"]["Measure"]
        with self.subTest("Verify measures get replicated to Site"):
            site = data["Site"]["Associations"]["Projects"]["Project"]["Measures"]["Measure"]
            self.assertEqual(len(measures), len(site))
            measure_ids = [x["@ID"] for x in measures]
            site_ids = [x["@ID"] for x in site]
            self.assertEqual(set(measure_ids), set(site_ids))

        with self.subTest("Verify builder measures get replicated to trade ally"):
            measure_ids = [
                x["@ID"] for x in measures if x["Code"] in ["EPSENHELE", "EPSENHGAS", "EPSESH"]
            ]
            builder = data["TradeAlly"][0]
            self.assertEqual(builder["Associations"]["Projects"]["Project"]["Role"], "BUILDER")
            trade_ally = builder["Associations"]["Projects"]["Project"]["Measures"]["Measure"]
            trade_measures = [x["@ID"] for x in trade_ally]
            self.assertEqual(set(measure_ids), set(trade_measures))

        with self.subTest("Verify verifier measures get replicated to trade ally"):
            measure_ids = [
                x["@ID"] for x in measures if x["Code"] in ["CUSTEPSVERFELE", "CUSTEPSVERFGAS"]
            ]
            verifier = data["TradeAlly"][1]
            self.assertEqual(verifier["Associations"]["Projects"]["Project"]["Role"], "VERIFIER")
            trade_ally = verifier["Associations"]["Projects"]["Project"]["Measures"]["Measure"]
            trade_measures = [x["@ID"] for x in trade_ally]
            self.assertEqual(set(measure_ids), set(trade_measures))

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
            Home.objects.all().update(street_line1="BAD_API")
            self.assertRaises(
                (HTTPError, Retry, KeyError), submit_fasttrack_xml.delay, self.home_status.id
            )
            self.assertEqual(FastTrackSubmission.objects.count(), 1)
            self.assertEqual(FastTrackSubmission.objects.get().project_id, "")
            self.assertEqual(IncentivePaymentStatus.objects.count(), 0)

        with self.subTest("Passing XML Post"):
            Home.objects.all().update(street_line1="200 N Church")
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

        with self.subTest("Failing XML Post"):
            Home.objects.all().update(street_line1="BAD_API")
            url = reverse_lazy("api_v3:project_tracker-submit", kwargs={"pk": self.home_status.id})
            self.client.force_authenticate(user=self.provider_user)
            self.assertRaises((HTTPError, Retry, KeyError), self.client.post, url)
            self.assertEqual(FastTrackSubmission.objects.get().project_id, "")
            self.assertEqual(IncentivePaymentStatus.objects.count(), 0)

        with self.subTest("Passing XML Post"):
            Home.objects.all().update(street_line1="200 N Church")
            FastTrackSubmission.objects.all().update(project_id="", submit_status=None)
            url = reverse_lazy("api_v3:project_tracker-submit", kwargs={"pk": self.home_status.id})
            self.client.force_authenticate(user=self.provider_user)
            response = self.client.post(url)
            self.assertEqual(response.status_code, 202)
            project_id = f"P{str(self.home_status.id).zfill(11)}"
            self.assertEqual(FastTrackSubmission.objects.get().project_id, project_id)
            self.assertEqual(IncentivePaymentStatus.objects.count(), 1)

        with self.subTest("Get XML"):
            url = reverse_lazy("api_v3:project_tracker-xml", kwargs={"pk": self.home_status.id})
            self.client.force_authenticate(user=self.provider_user)
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"ETOImport", response.content)
