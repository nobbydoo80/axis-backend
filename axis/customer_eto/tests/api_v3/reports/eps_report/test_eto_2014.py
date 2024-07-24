"""test_eto_2014.py - Axis"""

__author__ = "Steven K"
__date__ = "10/14/21 15:35"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
import datetime
from functools import cached_property
from io import BytesIO

from PyPDF2 import PdfReader
from django.urls import reverse_lazy
from rest_framework import status
from rest_framework.test import APITestCase

from axis.checklist.collection.excel import ExcelChecklistCollector
from axis.checklist.collection.test_mixins import CollectionRequestMixin
from axis.customer_eto.api_v3.serializers.reports.eps_report.eto_2014 import EPSReport2014Serializer
from axis.customer_eto.reports.legacy_utils import get_legacy_calculation_data
from axis.customer_eto.models import FastTrackSubmission, ETOAccount
from axis.customer_eto.tests.program_checks.test_eto_2019 import ETO2019ProgramTestMixin

log = logging.getLogger(__name__)


class TestEPSReport2014(ETO2019ProgramTestMixin, APITestCase, CollectionRequestMixin):
    @classmethod
    def setUpTestData(cls):
        super(TestEPSReport2014, cls).setUpTestData()

        from axis.core.tests.factories import rater_user_factory

        cls.user = rater_user_factory(company=cls.rater_company)

        # Hack in required stuff form old calculator.
        cls.eep_program.slug = "eto"
        cls.eep_program.save()
        cls.home_status.refresh_from_db()

        collection_request = CollectionRequestMixin()
        cls.checklist_responses = {
            "eto-ceiling_r_value": 29,
            "eto-wall_r_value": 30,
            "eto-floor_r_value": 12,
            "eto-lighting_pct": 87,
            "eto-water_heater_heat_type": "Storage",
            "eto-water_heater_ef": 22,
            "eto-primary_heat_afue": 97,
            "eto-primary_heat_type": "Gas Unit Heater",
            "eto-duct_leakage_ach50": 36,
            "eto-eto_pathway": "Pathway 1",
        }

        collection_request.add_bulk_answers(
            cls.checklist_responses, home_status=cls.home_status, auto_create_instrument=True
        )

        _errors = get_legacy_calculation_data(cls.home_status, return_errors=True)
        # print(_errors)
        cls.project_tracker = FastTrackSubmission.objects.get()

    def test_calculator_data(self):
        """Verify the calculator data was saved and somve values are there"""
        self.assertGreater(self.project_tracker.electric_cost_per_month, 0.0)
        self.assertGreater(self.project_tracker.improved_total_kwh, 0.0)
        self.assertGreater(self.project_tracker.projected_carbon_consumption_electric, 0.0)
        self.assertGreater(self.project_tracker.projected_carbon_consumption_natural_gas, 0.0)

    def test_calculator_core_data(self):
        """Verify the Core serializer info is present"""
        serializer = EPSReport2014Serializer(instance=self.project_tracker)
        data = serializer.data
        self.assertIsNotNone(data)

        with self.subTest("Home / Home Status Elements"):
            self.assertIn(self.home_status.home.street_line1, data["street_line"])
            self.assertEqual(self.home_status.home.city.name, data["city"])
            self.assertEqual(self.home_status.home.state, data["state"])
            self.assertEqual(self.home_status.home.zipcode, data["zipcode"])

        with self.subTest("Rater"):
            self.assertEqual(str(self.home_status.company), data["rater"])

        with self.subTest("Electric"):
            self.assertEqual(str(self.home_status.get_electric_company()), data["electric_utility"])

        with self.subTest("Gas"):
            self.assertEqual(str(self.home_status.get_gas_company()), data["gas_utility"])

    def test_serializer_floorplan_type(self):
        serializer = EPSReport2014Serializer(instance=FastTrackSubmission.objects.get())
        self.assertIn("PRELIMINARY", serializer.data["floorplan_type"])
        self.assertEqual(None, serializer.data["eps_issue_date"])

        self.home_status.certification_date = datetime.date.today()
        self.home_status.save()
        serializer = EPSReport2014Serializer(instance=FastTrackSubmission.objects.get())
        self.assertIn("OFFICIAL", serializer.data["floorplan_type"])
        self.assertEqual(
            str(self.home_status.certification_date), serializer.data["eps_issue_date"]
        )

    def test_serializer_rater_ccb(self):
        serializer = EPSReport2014Serializer(instance=FastTrackSubmission.objects.get())
        self.assertEqual(self.home_status.home.state, "OR")
        self.assertIsNotNone(self.rater_eto_account.ccb_number)
        self.assertIn(self.rater_eto_account.ccb_number, serializer.data["rater_ccb"])

        from axis.home.models import Home

        Home.objects.all().update(state="WA")
        serializer = EPSReport2014Serializer(instance=FastTrackSubmission.objects.get())
        self.assertEqual("", serializer.data["rater_ccb"])

        Home.objects.all().update(state="OR")
        ETOAccount.objects.all().update(ccb_number=None)
        serializer = EPSReport2014Serializer(instance=FastTrackSubmission.objects.get())
        self.assertIn("--", serializer.data["rater_ccb"])

    def test_solar(self):
        defaults = {"solar_hot_water_kwh": 0.0, "pv_kwh": 0.0, "solar_hot_water_therms": 0.0}
        with self.subTest("No PV / Solar"):
            FastTrackSubmission.objects.update(**defaults)
            self.project_tracker.refresh_from_db()
            self.assertEqual(self.project_tracker.solar_hot_water_kwh, 0.0)
            self.assertEqual(self.project_tracker.pv_kwh, 0.0)
            self.assertEqual(self.project_tracker.solar_hot_water_therms, 0.0)
            serializer = EPSReport2014Serializer(instance=self.project_tracker)
            self.assertEqual("No system", serializer.data["solar"])
        with self.subTest("Solar Therms"):
            _defaults = defaults.copy()
            _defaults["solar_hot_water_therms"] = 10.0
            FastTrackSubmission.objects.update(**_defaults)
            self.project_tracker = FastTrackSubmission.objects.get()
            self.assertEqual(self.project_tracker.solar_hot_water_kwh, 0.0)
            self.assertEqual(self.project_tracker.pv_kwh, 0.0)
            self.assertEqual(self.project_tracker.solar_hot_water_therms, 10.0)
            serializer = EPSReport2014Serializer(instance=self.project_tracker)
            self.assertEqual("Natural gas (therms): 10", serializer.data["solar"])
        with self.subTest("Solar kwh"):
            _defaults = defaults.copy()
            _defaults["solar_hot_water_kwh"] = 10.0
            FastTrackSubmission.objects.update(**_defaults)
            self.project_tracker = FastTrackSubmission.objects.get()
            self.assertEqual(self.project_tracker.solar_hot_water_kwh, 10.0)
            self.assertEqual(self.project_tracker.pv_kwh, 0.0)
            self.assertEqual(self.project_tracker.solar_hot_water_therms, 0.0)
            serializer = EPSReport2014Serializer(instance=self.project_tracker)
            self.assertEqual("Electric (kWh): 10", serializer.data["solar"])
        with self.subTest("PV"):
            _defaults = defaults.copy()
            _defaults["pv_kwh"] = 10.0
            FastTrackSubmission.objects.update(**_defaults)
            self.project_tracker = FastTrackSubmission.objects.get()
            self.assertEqual(self.project_tracker.solar_hot_water_kwh, 0.0)
            self.assertEqual(self.project_tracker.pv_kwh, 10.0)
            self.assertEqual(self.project_tracker.solar_hot_water_therms, 0.0)
            serializer = EPSReport2014Serializer(instance=self.project_tracker)
            self.assertEqual("Electric (kWh): 10", serializer.data["solar"])
        with self.subTest("All"):
            _defaults = {"solar_hot_water_kwh": 1.0, "pv_kwh": 2.0, "solar_hot_water_therms": 4.0}
            FastTrackSubmission.objects.update(**_defaults)
            self.project_tracker = FastTrackSubmission.objects.get()
            self.assertEqual(self.project_tracker.solar_hot_water_kwh, 1.0)
            self.assertEqual(self.project_tracker.pv_kwh, 2.0)
            self.assertEqual(self.project_tracker.solar_hot_water_therms, 4.0)
            serializer = EPSReport2014Serializer(instance=self.project_tracker)
            self.assertEqual("Electric (kWh): 3, Natural gas (therms): 4", serializer.data["solar"])

    def test_fastrack_model_backed_data(self):
        defaults = {
            "solar_hot_water_kwh": 1,
            "pv_kwh": 1,
            "solar_hot_water_therms": 1,
            "improved_total_kwh": 10,
            "improved_total_therms": 5,
            "projected_carbon_consumption_electric": 17,
            "projected_carbon_consumption_natural_gas": 13,
            "electric_cost_per_month": 10.0,
            "natural_gas_cost_per_month": 25.0,
        }
        FastTrackSubmission.objects.update(**defaults)
        serializer = EPSReport2014Serializer(instance=FastTrackSubmission.objects.get())

        self.assertEqual(serializer.data["electric_kwhs"], str(defaults["improved_total_kwh"]))
        self.assertEqual(serializer.data["net_electric_kwhs"], "8")
        self.assertEqual(serializer.data["total_electric_kwhs"], "12")
        self.assertEqual(
            serializer.data["natural_gas_therms"], str(defaults["improved_total_therms"])
        )
        self.assertEqual(serializer.data["total_natural_gas_therms"], "6")
        self.assertEqual(
            serializer.data["electric_tons_per_year"],
            float(defaults["projected_carbon_consumption_electric"]),
        )
        self.assertEqual(
            serializer.data["natural_gas_tons_per_year"],
            float(defaults["projected_carbon_consumption_natural_gas"]),
        )
        self.assertEqual(
            serializer.data["electric_per_month"],
            str(round(defaults["electric_cost_per_month"])),
        )
        self.assertEqual(
            serializer.data["natural_gas_per_month"],
            str(round(defaults["natural_gas_cost_per_month"])),
        )

    @cached_property
    def _answers(self):
        context = {"user__company": self.home_status.company}
        collector = ExcelChecklistCollector(self.home_status.collection_request, **context)
        instrument_lookup = collector.get_instruments()
        return {i.measure_id: collector.get_data_display(i) for i in instrument_lookup}

    def test_checklist_responses(self):
        serializer = EPSReport2014Serializer(instance=self.project_tracker)
        serializer_dict = {
            "eto-ceiling_r_value": "insulated_ceiling",
            "eto-wall_r_value": "insulated_walls",
            "eto-floor_r_value": "insulated_floors",
        }

        for measure, value in self.checklist_responses.items():
            with self.subTest(f"{measure} -> {value}"):
                self.assertIn(measure, self._answers)
                if measure not in serializer_dict:
                    continue
                self.assertEqual(
                    serializer.data[serializer_dict.get(measure)], f"R-{float(value):.0f}"
                )

        with self.subTest("lighting_pct"):
            self.assertIn("eto-lighting_pct", self._answers)
            value = self._answers["eto-lighting_pct"]
            self.assertEqual(
                serializer.data["efficient_lighting"], "{} %".format(round(float(value), 1))
            )

        with self.subTest("Water Heater"):
            self.assertIn("eto-water_heater_heat_type", self._answers)
            self.assertIn("eto-water_heater_ef", self._answers)
            wht = self._answers["eto-water_heater_heat_type"]
            whv = round(float(self._answers["eto-water_heater_ef"]), 1)
            self.assertEqual(serializer.data["water_heater"], f"{wht} {whv} EF")

        with self.subTest("Space Heating"):
            self.assertIn("eto-primary_heat_afue", self._answers)
            self.assertIn("eto-primary_heat_type", self._answers)
            ht = self._answers["eto-primary_heat_type"]
            hv = round(float(self._answers["eto-primary_heat_afue"]))
            self.assertEqual(serializer.data["space_heating"], f"{hv} {ht}")

        with self.subTest("lighting_pct"):
            self.assertIn("eto-duct_leakage_ach50", self._answers)
            value = self._answers["eto-duct_leakage_ach50"]
            self.assertEqual(
                serializer.data["envelope_tightness"],
                "{} ACH @ 50Pa".format(round(float(value), 1)),
            )

    def test_eto_report_generation(self):
        """verify we can get the report"""
        url = reverse_lazy("api_v3:eps_report-report", kwargs={"pk": self.home_status.pk})
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)

        document = PdfReader(BytesIO(response.content))

        address = self.home_status.home.get_home_address_display(
            include_city_state_zip=True, include_lot_number=False
        )

        self.assertEqual(document.metadata["/Title"], address)
        self.assertEqual(document.metadata["/Author"], self.user.get_full_name())
        self.assertEqual(len(document.pages), 2)
        self.assertIsNone(document.get_fields())
