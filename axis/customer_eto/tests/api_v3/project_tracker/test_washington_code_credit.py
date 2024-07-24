"""washington_code_credit.py - Axis"""

__author__ = "Steven K"
__date__ = "8/26/21 10:37"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import datetime
import logging
from unittest import mock
from urllib.error import HTTPError

from celery.exceptions import Retry
from django.conf import settings
from django.urls import reverse_lazy
from django.utils.timezone import now

from rest_framework import status
from rest_framework.test import APITestCase

from axis.company.models import Company
from axis.home.models import Home
from axis.incentive_payment.models import IncentivePaymentStatus
from ...factories import eto_mocked_soap_responses as mocked_post
from ...program_checks.test_washington_code_credit import WashingtonCodeCreditProgramBase
from ....api_v3.serializers.project_tracker.measures import MeasureSerializer
from ....api_v3.serializers.project_tracker.site import (
    SitePropertySerializer,
    SiteTechnologySerializer,
)

from ....api_v3.viewsets import ProjectTrackerXMLViewSet
from ....eep_programs.washington_code_credit import (
    WACCFuelType,
    FurnaceLocation,
    EfficientWaterHeating,
)
from ....models import FastTrackSubmission

log = logging.getLogger(__name__)


class TestProjectTrackerWashingtonCodeCredit(WashingtonCodeCreditProgramBase, APITestCase):
    @classmethod
    def setUpTestData(cls):
        super(TestProjectTrackerWashingtonCodeCredit, cls).setUpTestData()
        from axis.core.tests.factories import rater_user_factory

        cls.user = rater_user_factory(company=cls.rater_company)
        cls.rater_company.update_permissions()

        cls.project_tracker = FastTrackSubmission.objects.create(
            home_status=cls.home_status,
            builder_incentive=125.69,
            rater_incentive=225.21,
            required_credits_to_meet_code=43.2,
            achieved_total_credits=31.2,
            eligible_gas_points=20,
            code_credit_incentive=150.0,
            thermostat_incentive=210.0,
            fireplace_incentive=432.0,
        )
        future = datetime.datetime.now() + datetime.timedelta(days=30)
        cls.install_date = future.strftime("%Y-%m-%d")

    def render(self, response):
        response.render()
        return response.content.decode("utf8")

    def test_viewset_calculator_context_data(self):
        self.add_required_responses(self.max_program_data)
        viewset = ProjectTrackerXMLViewSet()
        data = viewset.get_washington_code_credit_calculator_context(self.project_tracker)
        self.assertEqual(data["builder_incentive"], 2725.0)
        self.assertEqual(data["verifier_incentive"], 100.0)
        self.assertEqual(data["fireplace_incentive"], 200.0)
        self.assertEqual(data["thermostat_incentive"], 125.0)
        self.assertEqual(data["code_credit_incentive"], 2400.0)
        self.assertEqual(data["water_heating_option"], EfficientWaterHeating.OPTION_5p6.value)

        # for k, v in data.items():
        #     print(f"self.assertEqual(data['{k}'], {v!r})")
        # print(data)

    def test_viewset_collected_input_context_data(self):
        self.add_required_responses(self.default_program_data)
        viewset = ProjectTrackerXMLViewSet()
        data = viewset.get_collected_input_context(self.project_tracker)

        self.assertEqual(data["conditioned_floor_area"], 2000)
        self.assertEqual(data["water_heater_brand"], "string")
        self.assertEqual(data["water_heater_model"], "string")
        self.assertEqual(data["water_heater_gas_uef"], 0.92)
        self.assertEqual(data["water_heater_electric_uef"], 2.5)
        self.assertEqual(data["water_heater_fuel"], "Electric")
        self.assertEqual(data["furnace_brand"], "furnace_brand")
        self.assertEqual(data["furnace_model"], "furnace_model")
        self.assertEqual(data["furnace_afue"], 92)
        self.assertEqual(data["furnace_location"], "Unconditioned Space")
        self.assertEqual(data["thermostat_brand"], "ecobee: Smart Thermostat with Voice Control")

        # for k, v in data.items():
        #     print(f"self.assertEqual(data['{k}'], {v!r})")

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

    def test_site_property_serialzier(self):
        context = {"conditioned_floor_area": 2001}
        serializer = SitePropertySerializer(instance=self.project_tracker, context=context)
        data = serializer.to_representation(self.project_tracker)

        self.assertIn("Properties", data)
        self.assertIn("Property", data["Properties"])
        self.assertEqual(len(data["Properties"]["Property"]), 2)

        data = {x["Name"]: x["Value"] for x in data["Properties"]["Property"]}
        self.assertEqual(data["YRBLT"], now().year)
        self.assertEqual(data["AREA"], context["conditioned_floor_area"])

    def test_site_technology_serialzier(self):
        serializer = SiteTechnologySerializer(instance=FastTrackSubmission.objects.get())
        data = serializer.to_representation(FastTrackSubmission.objects.get())
        self.assertIn("Technology", data)
        self.assertEqual(len(data["Technology"]), 1)
        data = data["Technology"][0]
        self.assertEqual(data["@ID"], "1")
        self.assertEqual(data["Code"], "GASFURN")
        with self.subTest("Gas Water Heater"):
            context = {"water_heater_fuel": WACCFuelType.GAS.value}
            serializer = SiteTechnologySerializer(
                instance=FastTrackSubmission.objects.get(), context=context
            )
            data = serializer.to_representation(FastTrackSubmission.objects.get())
            self.assertIn("Technology", data)
            self.assertEqual(len(data["Technology"]), 2)
            data = data["Technology"][1]
            self.assertEqual(data["@ID"], "2")
            self.assertEqual(data["Code"], "GASDHWTNKLS")
        with self.subTest("Electric Water Heater"):
            context = {"water_heater_fuel": WACCFuelType.ELECTRIC.value}
            serializer = SiteTechnologySerializer(
                instance=FastTrackSubmission.objects.get(), context=context
            )
            data = serializer.to_representation(FastTrackSubmission.objects.get())
            self.assertIn("Technology", data)
            self.assertEqual(len(data["Technology"]), 2)
            data = data["Technology"][1]
            self.assertEqual(data["@ID"], "2")
            self.assertEqual(data["Code"], "DHWHP")

    def test_wcc_hot_water_measure(self):
        with self.subTest("Electric Heat Pump"):
            context = {
                "water_heater_brand": "Brand",
                "water_heater_model": "Model",
                "water_heater_fuel": WACCFuelType.ELECTRIC.value,
                "water_heater_electric_uef": 9.2,
                "water_heating_option": EfficientWaterHeating.OPTION_5p6.value,
            }

            serializer = MeasureSerializer(
                instance=FastTrackSubmission.objects.get(), context=context
            )
            self.assertEqual(len(serializer.data["Measures"]["Measure"]), 1)
            data = serializer.data["Measures"]["Measure"][0]
            self.assertEqual(data["@ID"], 1)
            self.assertEqual(data["Code"], "WHEPS")
            self.assertEqual(data["Quantity"], 1)
            self.assertEqual(data["InstallDate"], self.install_date)
            self.assertEqual(data["Cost"], 0)
            self.assertEqual(data["Incentive"], "0.00")

            self.assertEqual(len(data["Attributes"]["Attribute"]), 5)
            data = {x["Name"]: x["Value"] for x in data["Attributes"]["Attribute"]}
            self.assertEqual(data["ENFACT"], context["water_heater_electric_uef"])
            self.assertEqual(data["MANUFACTURER"], context["water_heater_brand"])
            self.assertEqual(data["MODEL"], context["water_heater_model"])
            self.assertEqual(data["FUELTYPE"], "Ele")
            self.assertEqual(data["DHWTYPE"], "Tank")

        with self.subTest("Gas Tankless"):
            context = {
                "water_heater_brand": "Brand",
                "water_heater_model": "Model",
                "water_heater_fuel": WACCFuelType.GAS.value,
                "water_heater_gas_uef": 9.2,
                "water_heating_option": EfficientWaterHeating.OPTION_5p3.value,
            }

            serializer = MeasureSerializer(
                instance=FastTrackSubmission.objects.get(), context=context
            )
            self.assertEqual(len(serializer.data["Measures"]["Measure"]), 1)
            data = serializer.data["Measures"]["Measure"][0]
            self.assertEqual(data["@ID"], 1)
            self.assertEqual(data["Code"], "WHEPS")
            self.assertEqual(data["Quantity"], 1)
            self.assertEqual(data["InstallDate"], self.install_date)
            self.assertEqual(data["Cost"], 0)
            self.assertEqual(data["Incentive"], "0.00")

            self.assertEqual(len(data["Attributes"]["Attribute"]), 5)
            data = {x["Name"]: x["Value"] for x in data["Attributes"]["Attribute"]}
            self.assertEqual(data["ENFACT"], context["water_heater_gas_uef"])
            self.assertEqual(data["MANUFACTURER"], context["water_heater_brand"])
            self.assertEqual(data["MODEL"], context["water_heater_model"])
            self.assertEqual(data["FUELTYPE"], "Gas")
            self.assertEqual(data["DHWTYPE"], "Tankless")

        with self.subTest("None"):
            context = {
                "water_heater_brand": "Brand",
                "water_heater_model": "Model",
                "water_heater_fuel": None,
                "water_heater_gas_uef": None,
                "water_heating_option": EfficientWaterHeating.NONE.value,
            }

            serializer = MeasureSerializer(
                instance=FastTrackSubmission.objects.get(), context=context
            )
            self.assertEqual(len(serializer.data["Measures"]["Measure"]), 0)

        with self.subTest("Missing"):
            context = {
                "water_heater_brand": None,
                "water_heater_model": "Model",
                "water_heater_fuel": WACCFuelType.GAS.value,
                "water_heater_gas_uef": 9.2,
                "water_heating_option": EfficientWaterHeating.OPTION_5p3.value,
            }

            serializer = MeasureSerializer(
                instance=FastTrackSubmission.objects.get(), context=context
            )
            self.assertEqual(len(serializer.data["Measures"]["Measure"]), 0)

        with self.subTest("5.2: INELIGIBLE SELECTION"):
            context = {
                "water_heater_brand": "Brand",
                "water_heater_model": "Model",
                "water_heater_fuel": WACCFuelType.GAS.value,
                "water_heater_gas_uef": 9.2,
                "water_heating_option": EfficientWaterHeating.OPTION_5p2.value,
            }

            serializer = MeasureSerializer(
                instance=FastTrackSubmission.objects.get(), context=context
            )
            self.assertEqual(len(serializer.data["Measures"]["Measure"]), 0)

    def test_wcc_heater_measure(self):
        context = {
            "furnace_brand": "Brand",
            "furnace_model": "Model",
            "furnace_location": FurnaceLocation.CONDITIONED_SPACE.value,
            "furnace_afue": 9.2,
        }

        serializer = MeasureSerializer(instance=FastTrackSubmission.objects.get(), context=context)
        self.assertEqual(len(serializer.data["Measures"]["Measure"]), 1)
        data = serializer.data["Measures"]["Measure"][0]
        self.assertEqual(data["@ID"], 1)
        self.assertEqual(data["Code"], "GASFFURNEPS")
        self.assertEqual(data["Quantity"], 1)
        self.assertEqual(data["InstallDate"], self.install_date)
        self.assertEqual(data["Cost"], 0)
        self.assertEqual(data["Incentive"], "0.00")

        self.assertEqual(len(data["Attributes"]["Attribute"]), 3)
        data = {x["Name"]: x["Value"] for x in data["Attributes"]["Attribute"]}
        self.assertEqual(data["AFUE"], context["furnace_afue"])
        self.assertEqual(data["MANUFACTURER"], context["furnace_brand"])
        self.assertEqual(data["MODEL"], context["furnace_model"])

    def test_fireplace_incentive_measure(self):
        context = {
            "fireplace_incentive": 500.15,
        }

        serializer = MeasureSerializer(instance=FastTrackSubmission.objects.get(), context=context)
        self.assertEqual(len(serializer.data["Measures"]["Measure"]), 1)
        data = serializer.data["Measures"]["Measure"][0]
        self.assertEqual(data["@ID"], 1)
        self.assertEqual(data["Code"], "WACODECREDTSEF")
        self.assertEqual(data["Quantity"], 1)

        self.assertEqual(data["InstallDate"], self.install_date)
        self.assertEqual(data["Incentive"], str(context["fireplace_incentive"]))

    def test_get_thermostat_incentive_measure(self):
        context = {
            "thermostat_incentive": 500.25,
        }

        serializer = MeasureSerializer(instance=FastTrackSubmission.objects.get(), context=context)
        self.assertEqual(len(serializer.data["Measures"]["Measure"]), 1)
        data = serializer.data["Measures"]["Measure"][0]
        self.assertEqual(data["@ID"], 1)
        self.assertEqual(data["Code"], "WACODECREDTSST")
        self.assertEqual(data["Quantity"], 1)

        self.assertEqual(data["InstallDate"], self.install_date)
        self.assertEqual(data["Incentive"], str(context["thermostat_incentive"]))

    def test_get_code_credit_incentive_measure(self):
        context = {
            "code_credit_incentive": 501.25,
        }

        serializer = MeasureSerializer(instance=FastTrackSubmission.objects.get(), context=context)
        self.assertEqual(len(serializer.data["Measures"]["Measure"]), 1)
        data = serializer.data["Measures"]["Measure"][0]
        self.assertEqual(data["@ID"], 1)
        self.assertEqual(data["Code"], "WACODECREDT")
        self.assertEqual(data["Quantity"], 1)

        self.assertEqual(data["InstallDate"], self.install_date)
        self.assertEqual(data["Incentive"], str(context["code_credit_incentive"]))

    def test_xml_basic(self):
        self.add_required_responses(self.default_program_data)
        url = reverse_lazy("api_v3:project_tracker-xml", kwargs={"pk": self.home_status.pk})

        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        # print(self.render(response))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @mock.patch("requests.post", side_effect=mocked_post)
    def test_submit_api_endpoint(self, _mock):
        self.add_required_responses(self.default_program_data)

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
            self.assertIn("ETOImport", response.content.decode())
