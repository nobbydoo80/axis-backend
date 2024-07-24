"""test_eto_2018.py - Axis"""

__author__ = "Steven K"
__date__ = "10/14/21 15:37"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from io import BytesIO

from PyPDF2 import PdfReader
from django.urls import reverse_lazy
from rest_framework import status
from rest_framework.test import APITestCase

from axis.checklist.collection.test_mixins import CollectionRequestMixin
from axis.customer_eto.api_v3.serializers.reports.eps_report.eto_2018 import EPSReport2018Serializer
from axis.customer_eto.reports.legacy_utils import get_legacy_calculation_data
from axis.customer_eto.models import FastTrackSubmission
from axis.customer_eto.tests.program_checks.test_eto_2019 import ETO2019ProgramTestMixin

log = logging.getLogger(__name__)


class TestEPSReport2018(ETO2019ProgramTestMixin, APITestCase, CollectionRequestMixin):
    @classmethod
    def setUpTestData(cls):
        super(TestEPSReport2018, cls).setUpTestData()

        from axis.core.tests.factories import rater_user_factory

        cls.user = rater_user_factory(company=cls.rater_company)

        # Hack in required stuff form old calculator.
        cls.eep_program.slug = "eto-2018"
        cls.eep_program.save()
        cls.home_status.refresh_from_db()

        collection_request = CollectionRequestMixin()
        cls.checklist_responses = {
            "ceiling-r-value": 29,
            "primary-heating-equipment-type": "Gas Furnace",
        }

        collection_request.add_bulk_answers(
            cls.checklist_responses, home_status=cls.home_status, auto_create_instrument=True
        )

        _errors = get_legacy_calculation_data(cls.home_status, return_errors=True)
        # print(_errors)
        cls.project_tracker = FastTrackSubmission.objects.get()
        cls.simulation = cls.home_status.floorplan.remrate_target

    def test_year(self):
        serializer = EPSReport2018Serializer(instance=FastTrackSubmission.objects.get())
        self.assertEqual(serializer.data["year"], self.simulation.building.building_info.year_built)

    def test_square_footage(self):
        serializer = EPSReport2018Serializer(instance=FastTrackSubmission.objects.get())
        self.assertEqual(
            serializer.data["square_footage"],
            f"{self.simulation.building.building_info.conditioned_area:,.0f}",
        )

    def test_kwh_cost(self):
        serializer = EPSReport2018Serializer(instance=FastTrackSubmission.objects.get())
        self.assertEqual(
            serializer.data["kwh_cost"],
            f"${self.simulation.block_set.get_first_fuel_rate_dict()['Electric'][0]:,.2f}",
        )

    def test_therm_cost(self):
        serializer = EPSReport2018Serializer(instance=FastTrackSubmission.objects.get())
        try:
            value = self.simulation.block_set.get_first_fuel_rate_dict()["Natural gas"][0]
        except KeyError:
            value = 0.0
        self.assertEqual(serializer.data["therm_cost"], f"${value:,.2f}")

    def test_simulation_data_therm_cost(self):
        serializer = EPSReport2018Serializer(instance=FastTrackSubmission.objects.get())
        try:
            value = self.simulation.block_set.get_first_fuel_rate_dict()["Natural gas"][0]
        except KeyError:
            value = 0.0
        self.assertEqual(serializer.data["therm_cost"], f"${value:,.2f}")

    def test_insulated_walls(self):
        serializer = EPSReport2018Serializer(instance=FastTrackSubmission.objects.get())
        value = self.simulation.abovegradewall_set.get_r_value_for_largest()
        self.assertEqual(
            serializer.data["insulated_walls"],
            f"R-{value:.0f}",
        )

    def test_insulated_floors(self):
        serializer = EPSReport2018Serializer(instance=FastTrackSubmission.objects.get())
        value = self.simulation.framefloor_set.get_r_value_for_largest()
        self.assertEqual(
            serializer.data["insulated_floors"],
            f"R-{value:.0f}",
        )

    def test_efficient_windows(self):
        serializer = EPSReport2018Serializer(instance=FastTrackSubmission.objects.get())
        value = self.simulation.window_set.get_dominant_values()["u_value"]
        self.assertEqual(serializer.data["efficient_windows"], f"U-{value:.2f}")

    def test_efficient_lighting(self):
        serializer = EPSReport2018Serializer(instance=FastTrackSubmission.objects.get())
        value = self.simulation.lightsandappliance.pct_interior_led
        value += self.simulation.lightsandappliance.pct_interior_cfl
        self.assertEqual(serializer.data["efficient_lighting"], f"{value:.1f} %")

    def test_water_heater(self):
        serializer = EPSReport2018Serializer(instance=FastTrackSubmission.objects.get())
        equip = self.simulation.installedequipment_set.get_dominant_values(self.simulation.id)[
            self.simulation.id
        ]
        value = "{energy_factor} EF".format(**equip["dominant_hot_water"])
        self.assertEqual(serializer.data["water_heater"], value)

    def test_space_heating(self):
        serializer = EPSReport2018Serializer(instance=FastTrackSubmission.objects.get())
        equip = self.simulation.installedequipment_set.get_dominant_values(self.simulation.id)[
            self.simulation.id
        ]
        value = "{efficiency:.1f} {units_pretty}".format(**equip["dominant_heating"])
        self.assertEqual(serializer.data["space_heating"], value)

    def test_envelope_tightness(self):
        serializer = EPSReport2018Serializer(instance=FastTrackSubmission.objects.get())
        value = "{} {}".format(
            self.simulation.infiltration.heating_value,
            self.simulation.infiltration.get_units_display(),
        )
        self.assertEqual(serializer.data["envelope_tightness"], value)

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
