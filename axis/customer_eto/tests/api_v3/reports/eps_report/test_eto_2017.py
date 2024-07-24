"""test_eto_2017.py - Axis"""

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
from axis.customer_eto.api_v3.serializers.reports.eps_report.eto_2017 import EPSReport2017Serializer
from axis.customer_eto.api_v3.serializers.reports.eps_report.legacy_simulation import (
    EPSReportLegacySimulationSerializer,
)
from axis.customer_eto.reports.legacy_utils import get_legacy_calculation_data
from axis.customer_eto.models import FastTrackSubmission
from axis.customer_eto.tests.program_checks.test_eto_2019 import ETO2019ProgramTestMixin
from axis.remrate_data.tests.factories import simulation_factory

log = logging.getLogger(__name__)


class TestLegacySerializer(APITestCase):
    @classmethod
    def setUpTestData(cls):
        super(TestLegacySerializer, cls).setUpTestData()
        cls.simulation = simulation_factory(
            flavor="rate",
            frame_floors_count=1,
        )
        cls.serializer = EPSReportLegacySimulationSerializer(instance=cls.simulation)

    def test_conditioned_area(self):
        self.assertEqual(
            self.serializer.data["conditioned_area"],
            self.simulation.building.building_info.conditioned_area,
        )

    def test_construction_year(self):
        self.assertEqual(
            self.serializer.data["construction_year"],
            self.simulation.building.building_info.year_built,
        )

    def test_electric_unit_cost(self):
        self.assertEqual(
            self.serializer.data["electric_unit_cost"],
            round(self.simulation.block_set.get_first_fuel_rate_dict()["Electric"][0], 2),
        )

    def test_gas_unit_cost(self):
        try:
            value = self.simulation.block_set.get_first_fuel_rate_dict()["Natural gas"][0]
        except KeyError:
            value = 0.0
        self.assertEqual(
            self.serializer.data["gas_unit_cost"],
            round(value, 2),
        )

    def test_insulated_walls(self):
        value = self.simulation.abovegradewall_set.get_r_value_for_largest()
        self.assertEqual(
            self.serializer.data["insulated_walls"],
            f"R-{value:.0f}",
        )

    def test_insulated_floors(self):
        value = self.simulation.framefloor_set.get_r_value_for_largest()
        self.assertEqual(
            self.serializer.data["insulated_floors"],
            f"R-{value:.0f}",
        )

    def test_efficient_windows(self):
        value = self.simulation.window_set.get_dominant_values()["u_value"]
        self.assertEqual(self.serializer.data["efficient_windows"], f"U-{value:.2f}")

    def test_efficient_lighting(self):
        value = self.simulation.lightsandappliance.pct_interior_led
        value += self.simulation.lightsandappliance.pct_interior_cfl
        self.assertEqual(self.serializer.data["efficient_lighting"], f"{value:.1f} %")

    def test_water_heater_efficiency(self):
        equip = self.simulation.installedequipment_set.get_dominant_values(self.simulation.id)[
            self.simulation.id
        ]
        value = "{energy_factor} EF".format(**equip["dominant_hot_water"])
        self.assertEqual(self.serializer.data["water_heater_efficiency"], value)

    def test_heating_efficiency(self):
        equip = self.simulation.installedequipment_set.get_dominant_values(self.simulation.id)[
            self.simulation.id
        ]
        value = "{efficiency:.1f} {units_pretty}".format(**equip["dominant_heating"])
        self.assertEqual(self.serializer.data["heating_efficiency"], value)

    def test_envelope_tightness(self):
        value = "{} {}".format(
            self.simulation.infiltration.heating_value,
            self.simulation.infiltration.get_units_display(),
        )
        self.assertEqual(self.serializer.data["envelope_tightness"], value)


class TestEPSReport2017(ETO2019ProgramTestMixin, APITestCase, CollectionRequestMixin):
    @classmethod
    def setUpTestData(cls):
        super(TestEPSReport2017, cls).setUpTestData()

        from axis.core.tests.factories import rater_user_factory

        cls.user = rater_user_factory(company=cls.rater_company)

        # Hack in required stuff form old calculator.
        cls.eep_program.slug = "eto-2017"
        cls.eep_program.save()
        cls.home_status.refresh_from_db()

        collection_request = CollectionRequestMixin()
        cls.checklist_responses = {
            "eto-flat_ceiling_r_value-2017": 29,
            "eto-vaulted_ceiling_r_value-2017": 67,
            "eto-above_grade_walls_r_value-2017": 50,
            "eto-framed_floor_r_value": 13,
            "eto-slab_under_insulation_r_value": 30,
            "eto-slab_perimeter_r_value": 88,
            "eto-window_u_value": 0.21,
            "eto-lighting_pct-2016": 87,
            "eto-water_heater_heat_type-2017": "Storage",
            "eto-water_heater_ef": 22,
            "eto-primary_heat_type-2016": "Gas Unit Heater",
            "eto-primary_heat_afue": 97,
            "eto-primary_heat_hspf-2016": 56.2,
            "eto-primary_heat_seer-2016": 12.2,
            "eto-primary_heat_cop-2016": 23.1,
            "eto-duct_leakage_ach50": 36,
            "eto-eto_pathway": "Pathway 1",
        }

        collection_request.add_bulk_answers(
            cls.checklist_responses, home_status=cls.home_status, auto_create_instrument=True
        )

        _errors = get_legacy_calculation_data(cls.home_status, return_errors=True)
        # print(_errors)
        cls.project_tracker = FastTrackSubmission.objects.get()
        cls.simulation = cls.home_status.floorplan.remrate_target

    def test_simulation_data(self):
        serializer = EPSReport2017Serializer(instance=FastTrackSubmission.objects.get())
        with self.subTest("Year"):
            self.assertEqual(
                serializer.data["year"], self.simulation.building.building_info.year_built
            )
        with self.subTest("SQ Ft"):
            self.assertEqual(
                serializer.data["square_footage"],
                f"{self.simulation.building.building_info.conditioned_area:,.0f}",
            )
        with self.subTest("kWH Cost"):
            self.assertEqual(
                serializer.data["kwh_cost"],
                f"${self.simulation.block_set.get_first_fuel_rate_dict()['Electric'][0]:,.2f}",
            )
        with self.subTest("therm Cost"):
            try:
                value = self.simulation.block_set.get_first_fuel_rate_dict()["Natural gas"][0]
            except KeyError:
                value = 0.0
            self.assertEqual(serializer.data["therm_cost"], f"${value:,.2f}")

    @cached_property
    def _answers(self):
        context = {"user__company": self.home_status.company}
        collector = ExcelChecklistCollector(self.home_status.collection_request, **context)
        instrument_lookup = collector.get_instruments()
        return {i.measure_id: collector.get_data_display(i) for i in instrument_lookup}

    def test_insulated_ceiling(self):
        with self.subTest("Flat Roof"):
            self.assertIn("eto-flat_ceiling_r_value-2017", self._answers)
            value = self._answers["eto-flat_ceiling_r_value-2017"]
            serializer = EPSReport2017Serializer(instance=FastTrackSubmission.objects.get())
            self.assertEqual(serializer.data["insulated_ceiling"], f"R-{float(value):.0f}")
        with self.subTest("Vaulted Roof"):
            self.remove_collected_input("eto-flat_ceiling_r_value-2017")
            self.assertIn("eto-vaulted_ceiling_r_value-2017", self._answers)
            value = self._answers["eto-vaulted_ceiling_r_value-2017"]
            serializer = EPSReport2017Serializer(instance=FastTrackSubmission.objects.get())
            self.assertEqual(serializer.data["insulated_ceiling"], f"R-{float(value):.0f}")

    def test_insulated_walls(self):
        serializer = EPSReport2017Serializer(instance=self.project_tracker)
        self.assertIn("eto-above_grade_walls_r_value-2017", self._answers)
        value = self._answers["eto-above_grade_walls_r_value-2017"]
        self.assertEqual(serializer.data["insulated_walls"], "R-{}".format(round(float(value))))

    def test_insulated_floors(self):
        with self.subTest("Framed Floor"):
            self.assertIn("eto-framed_floor_r_value", self._answers)
            value = self._answers["eto-framed_floor_r_value"]
            serializer = EPSReport2017Serializer(instance=FastTrackSubmission.objects.get())
            self.assertEqual(serializer.data["insulated_floors"], f"R-{float(value):.0f}")
        with self.subTest("Slab Floor"):
            self.remove_collected_input("eto-framed_floor_r_value")
            self.assertIn("eto-slab_under_insulation_r_value", self._answers)
            value = self._answers["eto-slab_under_insulation_r_value"]
            serializer = EPSReport2017Serializer(instance=FastTrackSubmission.objects.get())
            self.assertEqual(serializer.data["insulated_floors"], f"R-{float(value):.0f}")
        with self.subTest("Slab perimeter Floor"):
            self.remove_collected_input("eto-slab_under_insulation_r_value")
            self.assertIn("eto-slab_perimeter_r_value", self._answers)
            value = self._answers["eto-slab_perimeter_r_value"]
            serializer = EPSReport2017Serializer(instance=FastTrackSubmission.objects.get())
            self.assertEqual(serializer.data["insulated_floors"], f"R-{float(value):.0f}")

    def test_efficient_windows(self):
        serializer = EPSReport2017Serializer(instance=self.project_tracker)
        self.assertIn("eto-window_u_value", self._answers)
        value = self._answers["eto-window_u_value"]
        self.assertEqual(
            serializer.data["efficient_windows"], "U-{}".format(round(float(value), 2))
        )

    def test_efficient_lighting(self):
        serializer = EPSReport2017Serializer(instance=self.project_tracker)
        self.assertIn("eto-lighting_pct-2016", self._answers)
        value = self._answers["eto-lighting_pct-2016"]
        self.assertEqual(serializer.data["efficient_lighting"], "{} %".format(round(float(value))))

    def test_water_heater(self):
        serializer = EPSReport2017Serializer(instance=FastTrackSubmission.objects.get())
        self.assertIn("eto-water_heater_heat_type-2017", self._answers)
        ht = self._answers["eto-water_heater_heat_type-2017"]
        self.assertIn("eto-water_heater_ef", self._answers)
        value = self._answers["eto-water_heater_ef"]
        self.assertEqual(
            serializer.data["water_heater"], "{} {} EF".format(ht, round(float(value), 1))
        )

    def test_space_heating(self):
        with self.subTest("Gas AFUE"):
            serializer = EPSReport2017Serializer(instance=FastTrackSubmission.objects.get())
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

            serializer = EPSReport2017Serializer(instance=FastTrackSubmission.objects.get())
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

            serializer = EPSReport2017Serializer(instance=FastTrackSubmission.objects.get())
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

            serializer = EPSReport2017Serializer(instance=FastTrackSubmission.objects.get())
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
