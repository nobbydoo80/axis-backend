"""test_eto_2022.py - Axis"""

__author__ = "Steven K"
__date__ = "3/29/22 09:18"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import datetime
import json
import logging
import random
import tempfile
from io import BytesIO

import tabulate
from PyPDF2 import PdfReader
from django.core import management
from django.forms import model_to_dict
from django.urls import reverse_lazy
from rest_framework import status
from rest_framework.test import APITestCase

from analytics.management.commands.add_analytics_program import DevNull
from axis.checklist.collection.test_mixins import CollectionRequestMixin
from axis.core.tests.testcases import AxisTestCase
from axis.customer_eto.api_v3.serializers.reports.eps_report.eto_2022 import (
    EPSReport2022BaseSerializer,
    EPSReport2022Serializer,
)
from axis.customer_eto.api_v3.serializers.reports.home_project.eto_2022 import (
    HomeProjectETO2022IncentiveSerializer,
)
from axis.customer_eto.eep_programs.eto_2022 import (
    SolarElements2022,
    ElectricCarElements2022,
    StorageElements2022,
)
from axis.customer_eto.enumerations import HeatType, PrimaryHeatingEquipment2020
from axis.customer_eto.models import FastTrackSubmission
from axis.customer_eto.tests.api_v3.project_tracker.test_eto_2022 import (
    TestProjectTracker2022Mixin,
)
from axis.filehandling.models import CustomerDocument
from axis.home.reports import HomeDetailReport
from simulation.enumerations import EnergyUnit, PvCapacity, SourceType
from simulation.tests.factories import photovoltaic_factory

log = logging.getLogger(__name__)


class EPSReport2022BaseSerializerTests(TestProjectTracker2022Mixin, AxisTestCase):
    """Test EPS Report lowlevel stuff"""

    def test_2022_base(self):
        input_data = {
            "street_line": "STREET_LINE",
            "city": "CITY",
            "state": "WI",
            "zipcode": "53094",
            "year": "2022",
            "square_footage": "2560",
            "eps_issue_date": datetime.date(2022, 10, 1),
            "rater": "RATER",
            "builder": "BUILDER",
            "electric_utility": "ELECTRIC_UTILITY",
            "gas_utility": "GAS_UTILITY",
            "energy_score": 25,
            "energy_consumption_similar_home": 92,
            "energy_consumption_to_code": 64,
            "estimated_monthly_energy_costs": 123.888,
            "estimated_monthly_energy_costs_code": 2600,
            "electric_per_month": 36.99,
            "natural_gas_per_month": 1.299,
            "kwh_cost": 77.272,
            "therm_cost": 4.321,
            "total_electric_kwhs": 96.2,
            "total_natural_gas_therms": 56.2,
            "annual_savings": 100.0,
            "thirty_year_savings": 3600,
            "solar_elements": "SOLAR_ELEMENTS",
            "electric_vehicle_type": "ELECTRIC_VEHICLE_TYPE",
            "storage_type": "STORAGE_TYPE",
            "pv_capacity_watts": 56.2,
            "pv_watts": "326.2",
            "storage_capacity": "1000",
        }

        serializer = EPSReport2022BaseSerializer(data=input_data)
        self.assertTrue(serializer.is_valid(raise_exception=True))

        data = serializer.data
        self.assertEqual(set(input_data.keys()), set(data.keys()))

        self.assertEqual(data["street_line"], "STREET_LINE")
        self.assertEqual(data["city"], "CITY")
        self.assertEqual(data["state"], "WI")
        self.assertEqual(data["zipcode"], "53094")
        self.assertEqual(data["year"], "2022")
        self.assertEqual(data["square_footage"], "2,560")
        self.assertEqual(data["eps_issue_date"], str(datetime.date(2022, 10, 1)))
        self.assertEqual(data["rater"], "RATER")
        self.assertEqual(data["builder"], "BUILDER")
        self.assertEqual(data["electric_utility"], "ELECTRIC_UTILITY")
        self.assertEqual(data["gas_utility"], "GAS_UTILITY")
        self.assertEqual(data["energy_score"], 25)
        self.assertEqual(data["energy_consumption_similar_home"], 92)
        self.assertEqual(data["energy_consumption_to_code"], 64)
        self.assertEqual(data["estimated_monthly_energy_costs"], "$124")
        self.assertEqual(data["estimated_monthly_energy_costs_code"], "$2,600")
        self.assertEqual(data["electric_per_month"], "37")
        self.assertEqual(data["natural_gas_per_month"], "1")
        self.assertEqual(data["kwh_cost"], "$77.27")
        self.assertEqual(data["therm_cost"], "$4.32")
        self.assertEqual(data["total_electric_kwhs"], "96")
        self.assertEqual(data["total_natural_gas_therms"], "56")
        self.assertEqual(data["annual_savings"], "$100")
        self.assertEqual(data["thirty_year_savings"], "$3,600")
        self.assertEqual(data["solar_elements"], "SOLAR_ELEMENTS")
        self.assertEqual(data["electric_vehicle_type"], "ELECTRIC_VEHICLE_TYPE")
        self.assertEqual(data["storage_type"], "STORAGE_TYPE")
        self.assertEqual(data["pv_watts"], "326")
        self.assertEqual(data["pv_capacity_watts"], "56")
        self.assertEqual(data["storage_capacity"], "1,000")


class EPSReport2022SerializerTests(TestProjectTracker2022Mixin, AxisTestCase):
    @classmethod
    def setUpTestData(cls):
        super(EPSReport2022SerializerTests, cls).setUpTestData()
        cls.serializer = EPSReport2022Serializer(instance=cls.project_tracker, data={})
        cls.serializer.is_valid(raise_exception=True)

    def test_keys(self):
        data = self.serializer.to_representation(instance=self.project_tracker)
        self.assertEqual(
            set(data.keys()),
            {
                "street_line",
                "city",
                "state",
                "zipcode",
                "year",
                "square_footage",
                "eps_issue_date",
                "rater",
                "builder",
                "electric_utility",
                "gas_utility",
                "energy_score",
                "energy_consumption_similar_home",
                "energy_consumption_to_code",
                "estimated_monthly_energy_costs",
                "estimated_monthly_energy_costs_code",
                "electric_per_month",
                "natural_gas_per_month",
                "kwh_cost",
                "therm_cost",
                "total_electric_kwhs",
                "total_natural_gas_therms",
                "annual_savings",
                "thirty_year_savings",
                "solar_elements",
                "electric_vehicle_type",
                "storage_type",
                "pv_capacity_watts",
                "pv_watts",
                "storage_capacity",
            },
        )

    def test_address_components(self):
        serializer = EPSReport2022Serializer(instance=self.project_tracker, data={})
        serializer.is_valid(raise_exception=True)

        with self.subTest("Home / Home Status Elements"):
            self.assertIn(self.home_status.home.street_line1, serializer.data["street_line"])
            self.assertEqual(self.home_status.home.city.name, serializer.data["city"])
            self.assertEqual(self.home_status.home.state, serializer.data["state"])
            self.assertEqual(self.home_status.home.zipcode, serializer.data["zipcode"])
            self.assertTrue(isinstance(serializer.data["street_line"], str))
            self.assertTrue(isinstance(serializer.data["city"], str))
            self.assertTrue(isinstance(serializer.data["state"], str))
            self.assertTrue(isinstance(serializer.data["zipcode"], str))

    def test_year(self):
        serializer = EPSReport2022Serializer(instance=self.project_tracker, data={})
        serializer.is_valid(raise_exception=True)

        self.assertEqual(
            serializer.data["year"],
            str(self.simulation.project.construction_year),
        )
        self.assertTrue(isinstance(serializer.data["year"], str))

    def test_square_footage(self):
        serializer = EPSReport2022Serializer(instance=self.project_tracker, data={})
        serializer.is_valid(raise_exception=True)

        self.assertEqual(
            serializer.data["square_footage"],
            f"{self.simulation.conditioned_area:,.0f}",
        )
        self.assertTrue(isinstance(serializer.data["square_footage"], str))

    def test_eps_issue_date(self):
        with self.subTest("Not Certified"):
            serializer = EPSReport2022Serializer(instance=self.project_tracker, data={})
            serializer.is_valid(raise_exception=True)
            self.assertIsNone(self.project_tracker.home_status.certification_date)
            self.assertEqual(
                serializer.data["eps_issue_date"],
                None,
            )
        with self.subTest("Certified"):
            today = datetime.date.today()
            self.home_status.certification_date = today
            self.home_status.save()
            self.project_tracker.refresh_from_db()
            serializer = EPSReport2022Serializer(instance=self.project_tracker, data={})
            serializer.is_valid(raise_exception=True)
            self.assertEqual(self.project_tracker.home_status.certification_date, today)
            self.assertEqual(
                serializer.data["eps_issue_date"],
                str(today),
            )
            self.assertTrue(isinstance(serializer.data["eps_issue_date"], str))

    def test_company_components(self):
        serializer = EPSReport2022Serializer(instance=self.project_tracker, data={})
        serializer.is_valid(raise_exception=True)

        with self.subTest("Rater"):
            self.assertEqual(str(self.home_status.company), serializer.data["rater"])
            self.assertTrue(isinstance(serializer.data["rater"], str))

        with self.subTest("Builder"):
            self.assertEqual(str(self.home_status.home.get_builder()), serializer.data["builder"])
            self.assertTrue(isinstance(serializer.data["builder"], str))

        with self.subTest("Electric"):
            self.assertEqual(
                str(self.home_status.get_electric_company()),
                serializer.data["electric_utility"],
            )
            self.assertTrue(isinstance(serializer.data["electric_utility"], str))

        with self.subTest("Gas"):
            self.assertEqual(
                str(self.home_status.get_gas_company()), serializer.data["gas_utility"]
            )
            self.assertTrue(isinstance(serializer.data["gas_utility"], str))

    def test_energy_data(self):
        serializer = EPSReport2022Serializer(instance=self.project_tracker, data={})
        serializer.is_valid(raise_exception=True)

        with self.subTest("energy_score"):
            self.assertEqual(self.project_tracker.eps_score, serializer.data["energy_score"])
            self.assertTrue(isinstance(serializer.data["energy_score"], int))

        with self.subTest("energy_consumption_similar_home"):
            self.assertEqual(
                self.project_tracker.similar_size_eps_score,
                serializer.data["energy_consumption_similar_home"],
            )
            self.assertTrue(isinstance(serializer.data["energy_consumption_similar_home"], int))

        with self.subTest("energy_consumption_to_code"):
            self.assertEqual(
                self.project_tracker.eps_score_built_to_code_score,
                serializer.data["energy_consumption_to_code"],
            )
            self.assertTrue(isinstance(serializer.data["energy_consumption_to_code"], int))

    def test_energy_costing(self):
        serializer = EPSReport2022Serializer(instance=self.project_tracker, data={})
        serializer.is_valid(raise_exception=True)

        with self.subTest("estimated_monthly_energy_costs"):
            self.assertEqual(
                f"${self.project_tracker.estimated_monthly_energy_costs:,.0f}",
                serializer.data["estimated_monthly_energy_costs"],
            )
            self.assertTrue(isinstance(serializer.data["estimated_monthly_energy_costs"], str))

        with self.subTest("estimated_monthly_energy_costs_code"):
            self.assertEqual(
                f"${self.project_tracker.estimated_monthly_energy_costs_code:,.0f}",
                serializer.data["estimated_monthly_energy_costs_code"],
            )
            self.assertTrue(isinstance(serializer.data["estimated_monthly_energy_costs_code"], str))

        with self.subTest("electric_per_month"):
            self.assertEqual(
                f"{self.project_tracker.electric_cost_per_month:,.0f}",
                serializer.data["electric_per_month"],
            )
            self.assertTrue(isinstance(serializer.data["electric_per_month"], str))

        with self.subTest("natural_gas_per_month"):
            self.assertEqual(
                f"{self.project_tracker.natural_gas_cost_per_month:,.0f}",
                serializer.data["natural_gas_per_month"],
            )
            self.assertTrue(isinstance(serializer.data["natural_gas_per_month"], str))

        with self.subTest("kwh_cost"):
            self.assertEqual(
                f"${serializer._simulation_data.get('electric_unit_cost'):,.2f}",
                serializer.data["kwh_cost"],
            )
            self.assertTrue(isinstance(serializer.data["kwh_cost"], str))

        with self.subTest("therm_cost"):
            self.assertEqual(
                f"${serializer._simulation_data.get('gas_unit_cost'):,.2f}",
                serializer.data["therm_cost"],
            )
            self.assertTrue(isinstance(serializer.data["therm_cost"], str))

        with self.subTest("total_electric_kwhs"):
            self.assertEqual(
                f"{self.project_tracker.improved_total_kwh + self.project_tracker.pv_kwh:,.0f}",
                serializer.data["total_electric_kwhs"],
            )
            self.assertTrue(isinstance(serializer.data["total_electric_kwhs"], str))

        with self.subTest("total_natural_gas_therms"):
            self.assertEqual(
                f"{self.project_tracker.improved_total_therms:,.0f}",
                serializer.data["total_natural_gas_therms"],
            )
            self.assertTrue(isinstance(serializer.data["total_natural_gas_therms"], str))

        with self.subTest("annual_savings"):
            self.assertEqual(
                f"${self.project_tracker.estimated_annual_energy_savings_cost:,.0f}",
                serializer.data["annual_savings"],
            )
            self.assertTrue(isinstance(serializer.data["annual_savings"], str))

        with self.subTest("thirty_year_savings"):
            self.assertEqual(
                f"${float(self.project_tracker.estimated_annual_energy_savings_cost) * 30 :,.0f}",
                serializer.data["thirty_year_savings"],
            )
            self.assertTrue(isinstance(serializer.data["thirty_year_savings"], str))

    def test_checklist_answers(self):
        collection_mixin = CollectionRequestMixin()

        with self.subTest("No answers"):
            collection_mixin.remove_collected_input("solar-elements", home_status=self.home_status)

            serializer = EPSReport2022Serializer(instance=self.project_tracker, data={})
            serializer.is_valid(raise_exception=True)

            self.assertEqual(serializer.data["solar_elements"], "")
            self.assertEqual(serializer.data["electric_vehicle_type"], "")
            self.assertEqual(serializer.data["storage_type"], "")
            self.assertEqual(serializer.data["storage_capacity"], "0")

        with self.subTest("Answers"):
            solar = random.choice([el.value for el in SolarElements2022])
            storage_type = random.choice([el.value for el in StorageElements2022])
            ev_type = random.choice([el.value for el in ElectricCarElements2022])
            collection_mixin.add_bulk_answers(
                {
                    "solar-elements": solar,
                    "electric-vehicle-type": ev_type,
                    "storage-type": storage_type,
                    "storage-capacity": "123",
                },
                home_status=self.home_status,
            )
            serializer = EPSReport2022Serializer(instance=self.project_tracker, data={})
            serializer.is_valid(raise_exception=True)

            self.assertEqual(serializer.data["solar_elements"], solar)
            self.assertEqual(serializer.data["electric_vehicle_type"], ev_type)
            self.assertEqual(serializer.data["storage_type"], storage_type)
            self.assertEqual(serializer.data["storage_capacity"], "123")

    def test_pv_watts(self):
        collection_mixin = CollectionRequestMixin()

        with self.subTest("non-ets-annual-pv-watts"):
            collection_mixin.add_bulk_answers(
                {"non-ets-annual-pv-watts": 500},
                home_status=self.home_status,
            )

            serializer = EPSReport2022Serializer(instance=self.project_tracker, data={})
            serializer.is_valid(raise_exception=True)

            self.assertEqual(serializer.data["pv_watts"], "500")
            collection_mixin.remove_collected_input(
                "non-ets-annual-pv-watts", home_status=self.home_status
            )

        with self.subTest("ets-annual-etsa-kwh"):
            collection_mixin.add_bulk_answers(
                {"ets-annual-etsa-kwh": 1200},
                home_status=self.home_status,
            )

            serializer = EPSReport2022Serializer(instance=self.project_tracker, data={})
            serializer.is_valid(raise_exception=True)

            self.assertEqual(serializer.data["pv_watts"], "1,200")

    def test_pv_capacity_watts(self):
        self.simulation.photovoltaics.all().delete()

        with self.subTest("no pv_capacity_watts"):
            serializer = EPSReport2022Serializer(instance=self.project_tracker, data={})
            serializer.is_valid(raise_exception=True)
            self.assertEqual(serializer.data["pv_capacity_watts"], "0")

        with self.subTest("pv_capacity_watts"):
            photovoltaic_factory(
                simulation=self.simulation,
                company=self.simulation.company,
                capacity=9600.51,
                capacity_units=PvCapacity.WATT,
            )
            serializer = EPSReport2022Serializer(instance=self.project_tracker, data={})
            serializer.is_valid(raise_exception=True)
            self.assertEqual(serializer.data["pv_capacity_watts"], "9,601")


class TestEPSViewSet2022(TestProjectTracker2022Mixin, APITestCase):
    def test_eto_2022_report_generation(self):
        """Make sure that the right report is grabbed."""
        address = ", ".join(
            [
                self.home_status.home.street_line1,
                self.home_status.home.city.name,
                self.home_status.home.city.state,
                self.home_status.home.zipcode,
            ]
        )

        with self.subTest("Not Certified"):
            url = reverse_lazy("api_v3:eps_report-report", kwargs={"pk": self.home_status.pk})
            self.client.force_authenticate(user=self.user)
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)

            document = PdfReader(BytesIO(response.content))

            self.assertEqual(document.metadata["/Title"], address)
            self.assertEqual(document.metadata["/Author"], self.user.get_full_name())
            self.assertEqual(len(document.pages), 1)
            self.assertIsNone(document.get_fields())
        with self.subTest("Certified"):
            self.home_status.state = "complete"
            self.home_status.certification_date = datetime.date(2022, 11, 1)
            self.home_status.save()
            url = reverse_lazy("api_v3:eps_report-report", kwargs={"pk": self.home_status.pk})
            self.client.force_authenticate(user=self.user)
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)

            document = PdfReader(BytesIO(response.content))

            self.assertEqual(document.metadata["/Title"], address)
            self.assertEqual(document.metadata["/Author"], self.user.get_full_name())
            self.assertEqual(len(document.pages), 1)
            self.assertIsNone(document.get_fields())

        with self.subTest("Old Certified"):
            self.home_status.state = "complete"
            self.home_status.certification_date = datetime.date(2019, 1, 1)
            self.home_status.save()
            url = reverse_lazy("api_v3:eps_report-report", kwargs={"pk": self.home_status.pk})
            self.client.force_authenticate(user=self.user)
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)

            document = PdfReader(BytesIO(response.content))

            # This is your first indication you are seeing an old report
            self.assertEqual(len(document.pages), 2)
            self.assertIsNone(document.get_fields())

    def test_generate_eps_report(self):
        """Test that we can generate a new eps report"""

        with self.subTest("With Store"):
            management.call_command(
                "generate_eto_report",
                "--home-status",
                self.home_status.id,
                "--store",
                stdout=DevNull(),
            )
            doc = CustomerDocument.objects.get()
            self.assertIsNotNone(doc.filesize)
            self.assertIsNotNone(doc.description)
            self.assertIsNotNone(doc.filename)
            document = PdfReader(doc.document)
            self.assertEqual(document.metadata["/Author"], "Pivotal Energy Solutions")
            self.assertEqual(len(document.pages), 1)
            self.assertIsNone(document.get_fields())

        with self.subTest("Home Based"):
            filename = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
            management.call_command(
                "generate_eto_report",
                "--home",
                self.home_status.home.id,
                "--user",
                self.provider_user.username,
                "--filename",
                filename,
                stdout=DevNull(),
            )
            with open(filename, "rb") as fh:
                document = PdfReader(fh)
                self.assertEqual(document.metadata["/Author"], str(self.provider_user))
                self.assertEqual(len(document.pages), 1)
                self.assertIsNone(document.get_fields())

        with self.subTest("Home Status Based"):
            filename = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
            management.call_command(
                "generate_eto_report",
                "--home-status",
                self.home_status.id,
                "--user",
                self.provider_user.id,
                "--filename",
                filename,
                stdout=DevNull(),
            )
            with open(filename, "rb") as fh:
                document = PdfReader(fh)
                self.assertEqual(document.metadata["/Author"], str(self.provider_user))
                self.assertEqual(len(document.pages), 1)
                self.assertIsNone(document.get_fields())

        with self.subTest("Simulation Source Type"):
            filename = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
            simulator = "ekotrope" if self.simulation.source_type == SourceType.EKOTROPE else "rem"
            management.call_command(
                "generate_eto_report",
                "--simulation_source",
                simulator,
                "--user",
                self.provider_user.id,
                "--filename",
                filename,
                stdout=DevNull(),
            )
            with open(filename, "rb") as fh:
                document = PdfReader(fh)
                self.assertEqual(document.metadata["/Author"], str(self.provider_user))
                self.assertEqual(len(document.pages), 1)
                self.assertIsNone(document.get_fields())

    def test_single_home_report(self):
        """Test out the single home export for eto-2002"""
        self.user.company_id = self.eto.id
        self.user.save()
        project_tracker = FastTrackSubmission.objects.first()
        response = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False).name
        # print(response)
        HomeDetailReport(filename=response).build(project_tracker.home_status, response, self.user)

    def test_single_home_project_incentive_serializer(self):
        """Test out the single home export for eto-2022"""

        with self.subTest("Heat Type Gas"):
            serializer = HomeProjectETO2022IncentiveSerializer(
                instance=FastTrackSubmission.objects.first()
            )
            # Ensure that we have the right data pulled out.
            self.assertEqual(len(serializer.data.keys()), 32)
            table = serializer.get_detail_table(**serializer.data)
            self.assertEqual(len(table), 18)
            table = serializer.get_incentive_table(**serializer.data)
            self.assertEqual(len(table), 11)
            # print(tabulate.tabulate(table))

            project_tracker = FastTrackSubmission.objects.first()
            response = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False).name
            # print(f"GAS: {response}")

            HomeDetailReport(filename=response).build(
                project_tracker.home_status, response, self.provider_user
            )

        with self.subTest("Heat Type Ele"):
            collection_mixin = CollectionRequestMixin()
            collection_mixin.remove_collected_input(
                "primary-heating-equipment-type", home_status=self.home_status
            )
            collection_mixin.add_bulk_answers(
                {
                    "primary-heating-equipment-type": PrimaryHeatingEquipment2020.ELECTRIC_RESISTANCE,
                    "solar-elements": SolarElements2022.NET_ZERO.value,
                    "electric-vehicle-type": ElectricCarElements2022.EV_INSTALLED.value,
                    "storage-type": StorageElements2022.STORAGE_INSTALLED.value,
                    "storage-capacity": "123",
                    "ets-annual-etsa-kwh": 1200,
                },
                home_status=self.home_status,
            )
            serializer = HomeProjectETO2022IncentiveSerializer(
                instance=FastTrackSubmission.objects.first()
            )
            table = serializer.get_detail_table(**serializer.data)
            # print(tabulate.tabulate(table))
            self.assertEqual(len(table), 18)

            project_tracker = FastTrackSubmission.objects.first()
            response = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False).name
            # print(f"ELE: {response}")
            HomeDetailReport(filename=response).build(
                project_tracker.home_status, response, self.provider_user
            )

        with self.subTest("Heat Heat Pump"):
            FastTrackSubmission.objects.all().update(heat_pump_water_heater_incentive=-250)
            serializer = HomeProjectETO2022IncentiveSerializer(
                instance=FastTrackSubmission.objects.first()
            )
            table = serializer.get_detail_table(**serializer.data)
            # print(tabulate.tabulate(table))
            self.assertEqual(len(table), 18)

            project_tracker = FastTrackSubmission.objects.first()
            response = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False).name
            # print(f"HP: {response}")
            HomeDetailReport(filename=response).build(
                project_tracker.home_status, response, self.provider_user
            )

    def test_all_fields(self):
        """Make sure we hit all if statements"""

        summary = self.simulation.as_designed_analysis.summary
        summary.solar_generation = 25000
        summary.consumption_units = EnergyUnit.KWH
        summary.save()

        collection_mixin = CollectionRequestMixin()
        collection_mixin.remove_collected_input("solar-elements", home_status=self.home_status)

        collection_mixin.add_bulk_answers(
            {
                "solar-elements": SolarElements2022.NET_ZERO.value,
                "electric-vehicle-type": ElectricCarElements2022.EV_INSTALLED.value,
                "storage-type": StorageElements2022.STORAGE_INSTALLED.value,
                "storage-capacity": "123",
                "ets-annual-etsa-kwh": 1200,
            },
            home_status=self.home_status,
        )

        url = reverse_lazy("api_v3:eps_report-report", kwargs={"pk": self.home_status.pk})
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)

        document = PdfReader(BytesIO(response.content))
        self.assertEqual(document.metadata["/Author"], self.user.get_full_name())
        self.assertEqual(len(document.pages), 1)
        self.assertIsNone(document.get_fields())

        # management.call_command(
        #     "generate_eto_report",
        #     "--home-status",
        #     self.home_status.id,
        #     "--user",
        #     self.provider_user.id,
        #     stdout=DevNull(),
        # )
