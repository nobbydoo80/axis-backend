"""test_serializers.py: """


__author__ = "Rajesh Pethe"
__date__ = "02/21/2023 19:07:28"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Rajesh Pethe",
    "Steven Klass",
]

import glob
import io
import json
import logging
import os
import random
import uuid

from django.apps import apps
from django.core.files import File
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from axis.core.tests.testcases import ApiV3Tests
from axis.filehandling.tests.factories import customer_document_factory
from axis.floorplan.api_v3.serializers.analysis import (
    SummaryResultCostSerializer,
    SummaryResultConsumptionSerializer,
    AnalysisUrlSerializer,
    AnalysisSummaryDataSerializer,
)
from axis.floorplan.api_v3.serializers.simulation import (
    SimulationHomeBuildingParameterSerializer,
    SimulationOSERIAnalysisTypeSerializer,
    SimulationTaskSerializer,
)
from axis.geographic.tests.factories import real_city_factory
from axis.home.tests.factories import home_factory, eep_program_custom_home_status_factory
from axis.floorplan.tests.factories import floorplan_with_simulation_factory
from simulation.tests.factories import simulation_factory, analysis_factory
from axis.core.tests.factories import rater_admin_factory
from axis.subdivision.tests.factories import subdivision_factory
from axis.floorplan.api_v3.serializers.eep_program_home_status import EEPProgramHomeStatusSerializer
from axis.floorplan.api_v3.serializers import (
    FloorplanFlatListSerializer,
    FloorplanSerializer,
    FloorplanFromBlgSerializer,
)
from simulation.enumerations import SourceType, AnalysisStatus

log = logging.getLogger(__name__)

BLG_SOURCE_PATH = os.path.join(apps.get_app_config("remrate").path, "tests", "sources")


class TestEEPProgramHomeStatusSerializer(ApiV3Tests):
    """Test HomeAddressIsUniqueRequestDataSerializer Serializer"""

    @classmethod
    def setUpTestData(cls):
        cls.city = real_city_factory("Providence", "RI")
        cls.rater_admin = rater_admin_factory()
        cls.simulation = simulation_factory(company=cls.rater_admin.company)
        floorplan_with_simulation_factory(owner=cls.simulation.company, simulation=cls.simulation)

    def test_home_subdivision_eep_program_data(self):
        home_data = {
            "street_line1": "479 Washington St",
            "city": self.city.id,
            "zipcode": 34342,
            "is_multi_family": False,
        }

        subdivision = subdivision_factory(city=real_city_factory("Kennewick", "WA"))

        source_home = home_factory(
            street_line1=home_data["street_line1"],
            street_line2=home_data.get("street_line2"),
            is_multi_family=home_data["is_multi_family"],
            zipcode=home_data["zipcode"],
            city=self.city,
            geocode=None,
            subdivision=subdivision,
        )

        eep_program_home_status = eep_program_custom_home_status_factory(
            company=self.simulation.company,
            skip_floorplan=False,
            floorplan=self.simulation.floorplan,
            home=source_home,
        )

        with self.subTest("Valid User"):
            serializer = EEPProgramHomeStatusSerializer(
                instance=eep_program_home_status, context={"user": self.rater_admin}
            )
            data = serializer.data
            self.assertIsNotNone(data)
            self.assertIn(home_data["street_line1"], data["home_info"]["home_address"])
            self.assertEqual(
                data["home_info"]["eep_programs"][0]["eep_program"]["name"],
                eep_program_home_status.eep_program.name,
            )

            subdivision_info = data["home_info"]["subdivision_info"]
            self.assertEqual(subdivision_info["city_info"]["name"], subdivision.city.name)
        with self.subTest("In-Valid User"):
            serializer = EEPProgramHomeStatusSerializer(
                instance=eep_program_home_status, context={}
            )
            data = serializer.data
            self.assertIsNotNone(data)
            self.assertEqual(len(data["home_info"]["eep_programs"]), 0)


class TestFloorplanFlatListSerializer(ApiV3Tests):
    @classmethod
    def setUpTestData(cls):
        cls.rater_admin = rater_admin_factory()
        cls.simulation = simulation_factory(
            company=cls.rater_admin.company,
            source_type=SourceType.REMRATE_SQL,
        )
        cls.floorplan = floorplan_with_simulation_factory(
            owner=cls.simulation.company, simulation=cls.simulation
        )

    def test_floorplan_flat_list_serializer(self):
        serializer = FloorplanFlatListSerializer(instance=self.floorplan)
        data = serializer.data
        self.assertIsNotNone(data)
        sim_info = serializer.data["simulation_info"]
        self.assertEqual(sim_info["source_type"], SourceType.REMRATE_SQL)
        self.assertEqual(sim_info["source_type_display"], SourceType.REMRATE_SQL.label)


class TestFloorplanSerializer(ApiV3Tests):
    @classmethod
    def setUpTestData(cls):
        cls.rater_admin = rater_admin_factory()
        cls.floorplan = floorplan_with_simulation_factory(
            owner=cls.rater_admin.company,
            simulation__source_type=SourceType.REMRATE_SQL,
        )

    def test_serializer(self):
        serializer = FloorplanSerializer(instance=self.floorplan)
        data = serializer.data
        # dump_test_data(serializer.data)

        self.assertIsNotNone(data["id"])
        self.assertEqual(data["name"], "Test Simulation")
        self.assertEqual(data["name"], self.floorplan.simulation.name)
        self.assertIsNotNone(data["number"])
        self.assertEqual(data["square_footage"], int(self.floorplan.simulation.conditioned_area))

        self.assertEqual(data["is_custom_home"], False)
        self.assertIsNone(data["remrate_data_file"])
        self.assertIsNotNone(data["simulation"])
        self.assertEqual(data["is_active"], True)

        serializer = FloorplanSerializer(instance=self.floorplan, data=data)
        self.assertTrue(serializer.is_valid(raise_exception=True))

    def test_serializer_identical_named(self):
        serializer = FloorplanSerializer(instance=self.floorplan)
        data = serializer.data
        self.assertEqual(data["name"], "Test Simulation")

        floorplan = floorplan_with_simulation_factory(
            owner=self.rater_admin.company,
            simulation__source_type=SourceType.REMRATE_SQL,
            simulation__name="FOO",
        )
        self.assertEqual(floorplan.name, "FOO")

        serializer = FloorplanSerializer(instance=floorplan)
        data = serializer.data
        self.assertEqual(data["name"], "FOO")
        data["name"] = "Test Simulation"

        serializer = FloorplanSerializer(instance=floorplan, data=data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        with self.assertRaises(serializers.ValidationError):
            serializer.save(owner=self.rater_admin.company)


class TestFloorplanFromBlgSerializer(ApiV3Tests):
    @classmethod
    def setUpTestData(cls):
        cls.rater_admin = rater_admin_factory(company__name="Rater Org")

        class MockRequest:
            user = cls.rater_admin

        cls.context = {"request": MockRequest}

    def test_serializer(self):
        files = glob.glob(BLG_SOURCE_PATH + "/*.blg")
        for file_name in random.sample(files, 3):
            with self.subTest(f"Floorplan from {file_name}"):
                with io.open(file_name, "rb") as f:
                    file_obj = File(f, name=os.path.basename(file_name))

                    serializer = FloorplanFromBlgSerializer(
                        data={"file": file_obj}, context=self.context
                    )
                    self.assertTrue(serializer.is_valid(raise_exception=True))
                    instance = serializer.save()
                    instance.delete()

    def test_validation_error_serializer(self):
        file_name = os.path.join(BLG_SOURCE_PATH, "ALL_FIELDS_SET_16.3.2.blg")
        with io.open(file_name, "rb") as f:
            file_obj = File(f, name=os.path.basename(file_name))

            serializer = FloorplanFromBlgSerializer(data={"file": file_obj}, context=self.context)
            self.assertTrue(serializer.is_valid(raise_exception=True))
            instance = serializer.save()

        with io.open(file_name, "rb") as f:
            file_obj = File(f, name=os.path.basename(file_name))

            serializer = FloorplanFromBlgSerializer(data={"file": file_obj}, context=self.context)
            self.assertRaises(ValidationError, serializer.is_valid, raise_exception=True)

    def test_simulation_home_building_parameter_serializer(self):
        """This is used in examine views create home from BLG."""
        file_name = os.path.join(BLG_SOURCE_PATH, "ALL_FIELDS_SET_16.3.2.blg")
        with io.open(file_name, "rb") as f:
            file_obj = File(f, name=os.path.basename(file_name))

            serializer = FloorplanFromBlgSerializer(data={"file": file_obj}, context=self.context)
            self.assertTrue(serializer.is_valid(raise_exception=True))
            instance = serializer.save()

        serializer = SimulationHomeBuildingParameterSerializer(instance=instance.simulation)
        data = serializer.data
        self.assertEqual(data["home"]["is_multi_family"], True)
        self.assertEqual(data["home"]["street_line1"], "2342 Maybee Ave.")
        self.assertEqual(data["home"]["state"], "CO")
        self.assertEqual(data["home"]["subdivision_name"], "Rocky View")
        self.assertEqual(data["home_relationships"]["rater_name"], "Rater Org")
        self.assertEqual(data["floorplan"]["name"], "the bldg name")
        self.assertEqual(data["floorplan"]["square_footage"], 2000.0)
        self.assertEqual(data["floorplan"]["number"], "XYZ-REM16p3p2")


class TestAnalysisSummaryDataSerializer(ApiV3Tests):
    def test_cost_serializer(self):
        analysis = analysis_factory(
            simulation=simulation_factory(only_basic=True), solar_generation_mbtu=12.2
        )
        serializer = SummaryResultCostSerializer(instance=analysis.summary)
        data = serializer.data
        # dump_test_data(data)
        self.assertIsNotNone(data["id"])
        self.assertAlmostEqual(data["annual_heating_cost"], analysis.summary.heating_cost, 2)
        self.assertAlmostEqual(data["annual_cooling_cost"], analysis.summary.cooling_cost, 2)
        self.assertAlmostEqual(
            data["annual_hot_water_cost"], analysis.summary.water_heating_cost, 2
        )
        self.assertAlmostEqual(
            data["annual_light_and_appliances_cost"],
            analysis.summary.lighting_and_appliances_cost,
            2,
        )
        self.assertAlmostEqual(
            data["annual_generation"], analysis.summary.solar_generation_savings, 4
        )
        self.assertAlmostEqual(data["total_annual_costs"], analysis.summary.total_cost, 2)
        self.assertAlmostEqual(
            data["total_annual_costs_with_generation"], analysis.summary.total_cost_no_pv, 2
        )

    def test_consumption_serializer(self):
        analysis = analysis_factory(simulation=simulation_factory(only_basic=True))

        serializer = SummaryResultConsumptionSerializer(instance=analysis.summary)
        data = serializer.data
        # dump_test_data(data)
        self.assertAlmostEqual(
            data["total_heating_consumption"], analysis.summary.heating_consumption, 2
        )

        self.assertAlmostEqual(
            data["total_cooling_consumption"], analysis.summary.cooling_consumption, 4
        )
        self.assertAlmostEqual(
            data["total_hot_water_consumption"], analysis.summary.water_heating_consumption, 2
        )
        self.assertAlmostEqual(
            data["total_light_and_appliances_consumption"],
            analysis.summary.lighting_and_appliances_consumption,
            2,
        )
        self.assertAlmostEqual(
            data["total_onsite_generation"], analysis.summary.solar_generation, 2
        )
        self.assertAlmostEqual(
            data["total_energy_consumption"], analysis.summary.total_consumption, 2
        )

    def test_url_serializer(self):
        analysis = analysis_factory(
            simulation=simulation_factory(only_basic=True), solar_generation_mbtu=12.2
        )
        customer_document_factory(
            company=analysis.company,
            content_object=analysis,
            document_name="open_studio_html_results_HG3chhS.html",
        )
        serializer = AnalysisUrlSerializer(instance=analysis)
        data = serializer.data
        self.assertIn("/api/v3/customer_document/", data["rated_html_document"])

    def test_summary_data_serializer(self):
        analysis = analysis_factory(
            simulation=simulation_factory(only_basic=True), solar_generation_mbtu=12.2
        )
        customer_document_factory(
            company=analysis.company,
            content_object=analysis,
            document_name="open_studio_html_results_HG3chhS.html",
        )
        serializer = AnalysisSummaryDataSerializer(instance=analysis)
        data = serializer.data
        # dump_test_data(data)

        self.assertIsNotNone(data["id"])
        self.assertEqual(data["engine"], analysis.get_engine_display())
        self.assertIsNotNone(data["type"])
        self.assertEqual(data["valid"], True)
        self.assertEqual(data["version"], analysis.version)
        self.assertIsNotNone(data["simulation_date"])
        self.assertAlmostEqual(data["energy_rating_index"], analysis.eri_score, 2)
        self.assertIsNotNone(data["costs"])
        self.assertIsNotNone(data["consumption"])
        self.assertIsNotNone(data["urls"])


class TestSimulationTaskSerializers(ApiV3Tests):
    def test_open_studio_eri_analysis_types_serializer(self):
        data = {
            "ERICalculation": "2014",
            "IECCERICalculation": "2018",
        }
        serializer = SimulationOSERIAnalysisTypeSerializer(data=data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        self.assertEqual(serializer.data, data)

    def test_open_studio_eri_analysis_task_serializer(self):
        data = {
            "id": 10,
            "analysis_ids": [1, 2, 3],
            "status": AnalysisStatus.PENDING,
            "task_id": str(uuid.uuid4()),
        }
        serializer = SimulationTaskSerializer(data=data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        self.assertEqual(serializer.data, data)
