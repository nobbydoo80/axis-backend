"""test_eto_2016.py - Axis"""

__author__ = "Steven K"
__date__ = "10/14/21 15:36"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
from functools import cached_property
from io import BytesIO

from PyPDF2 import PdfReader
from django.urls import reverse_lazy
from rest_framework import status
from rest_framework.test import APITestCase

from axis.checklist.collection.excel import ExcelChecklistCollector
from axis.checklist.collection.test_mixins import CollectionRequestMixin
from axis.customer_eto.api_v3.serializers.reports.eps_report.eto_2016 import EPSReport2016Serializer
from axis.customer_eto.reports.legacy_utils import get_legacy_calculation_data
from axis.customer_eto.models import FastTrackSubmission
from axis.customer_eto.tests.program_checks.test_eto_2019 import ETO2019ProgramTestMixin
from axis.eep_program.models import EEPProgram

log = logging.getLogger(__name__)


class TestEPSReport2016(ETO2019ProgramTestMixin, APITestCase, CollectionRequestMixin):
    @classmethod
    def setUpTestData(cls):
        super(TestEPSReport2016, cls).setUpTestData()

        from axis.core.tests.factories import rater_user_factory

        cls.user = rater_user_factory(company=cls.rater_company)

        # Hack in required stuff form old calculator.
        cls.eep_program.slug = "eto-2016"
        cls.eep_program.save()
        cls.home_status.refresh_from_db()

        collection_request = CollectionRequestMixin()
        cls.checklist_responses = {
            "eto-ceiling_r_value": 29,
            "eto-wall_r_value": 30,
            "eto-floor_r_value": 12,
            "eto-lighting_pct-2016": 91,
            "eto-water_heater_heat_type": "Storage",
            "eto-water_heater_ef": 22,
            "eto-primary_heat_afue": 97,
            "eto-primary_heat_type-2016": "Gas Unit Heater",
            "eto-duct_leakage_ach50": 36,
            "eto-eto_pathway": "Pathway 1",
            "eto-primary_heat_hspf-2016": 56.2,
            "eto-primary_heat_seer-2016": 12.2,
            "eto-primary_heat_cop-2016": 23.1,
        }

        collection_request.add_bulk_answers(
            cls.checklist_responses, home_status=cls.home_status, auto_create_instrument=True
        )

        _errors = get_legacy_calculation_data(cls.home_status, return_errors=True)
        # print(_errors)
        cls.project_tracker = FastTrackSubmission.objects.get()

    @cached_property
    def _answers(self):
        context = {"user__company": self.home_status.company}
        collector = ExcelChecklistCollector(self.home_status.collection_request, **context)
        instrument_lookup = collector.get_instruments()
        return {i.measure_id: collector.get_data_display(i) for i in instrument_lookup}

    def test_efficient_lighting(self):
        serializer = EPSReport2016Serializer(instance=self.project_tracker)
        self.assertIn("eto-lighting_pct-2016", self._answers)
        value = self._answers["eto-lighting_pct-2016"]
        self.assertEqual(serializer.data["efficient_lighting"], "{} %".format(round(float(value))))

    def test_space_heating(self):
        with self.subTest("Gas AFUE"):
            serializer = EPSReport2016Serializer(instance=FastTrackSubmission.objects.get())
            self.assertIn("eto-primary_heat_type-2016", self._answers)
            ht = self._answers["eto-primary_heat_type-2016"]
            self.assertIn("eto-primary_heat_afue", self._answers)
            value = self._answers["eto-primary_heat_afue"]
            self.assertEqual(
                serializer.data["space_heating"], "{} {}".format(round(float(value)), ht)
            )
        with self.subTest("Heat Pump HSPF"):
            self.remove_collected_input("eto-primary_heat_type-2016")
            self.remove_collected_input("eto-primary_heat_afue")
            self.add_collected_input(measure_id="eto-primary_heat_type-2016", value="Heat XX Pump")

            serializer = EPSReport2016Serializer(instance=FastTrackSubmission.objects.get())
            self.assertIn("eto-primary_heat_type-2016", self._answers)
            self.assertIn("eto-primary_heat_hspf-2016", self._answers)
            value = self._answers["eto-primary_heat_hspf-2016"]
            self.assertEqual(
                serializer.data["space_heating"], "{} HSFP Heat Pump".format(round(float(value), 1))
            )
        with self.subTest("Radiant Seer"):
            self.remove_collected_input("eto-primary_heat_type-2016")
            self.remove_collected_input("eto-primary_heat_hspf-2016")
            self.add_collected_input(
                measure_id="eto-primary_heat_type-2016", value="Radiant heater thingy"
            )

            serializer = EPSReport2016Serializer(instance=FastTrackSubmission.objects.get())
            self.assertIn("eto-primary_heat_type-2016", self._answers)
            self.assertIn("eto-primary_heat_seer-2016", self._answers)
            value = self._answers["eto-primary_heat_seer-2016"]
            self.assertEqual(
                serializer.data["space_heating"], "{} SEER Radiant".format(round(float(value), 1))
            )
        with self.subTest("Furnace COP"):
            self.remove_collected_input("eto-primary_heat_type-2016")
            self.remove_collected_input("eto-primary_heat_seer-2016")
            self.add_collected_input(
                measure_id="eto-primary_heat_type-2016", value="Big as furnace"
            )

            serializer = EPSReport2016Serializer(instance=FastTrackSubmission.objects.get())
            self.assertIn("eto-primary_heat_type-2016", self._answers)
            self.assertIn("eto-primary_heat_cop-2016", self._answers)
            value = self._answers["eto-primary_heat_cop-2016"]
            self.assertEqual(
                serializer.data["space_heating"], "{} COP Furnace".format(round(float(value), 1))
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

    def test_eto_report_2019_generation(self):
        """verify we can get the report"""
        EEPProgram.objects.filter(slug="eto-2018").update(slug="eto-2019")
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
