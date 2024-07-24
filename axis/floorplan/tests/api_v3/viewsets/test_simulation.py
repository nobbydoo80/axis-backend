import logging
import os
import random
import shutil
import tempfile
import uuid
from io import BytesIO
from unittest import mock

from django.apps import apps
from django.contrib.auth import get_user_model
from django.core.files import File
from lxml import etree
from rest_framework import status
from rest_framework.reverse import reverse_lazy
from simulation.enumerations import (
    SourceType,
    AnalysisType,
    AnalysisStatus,
    OpenStudioAnalysisSourceName,
)
from simulation.models import (
    Simulation,
    Seed,
    Heater,
    AirConditioner,
    Dehumidifier,
    WaterHeater,
    AirSourceHeatPump,
    GroundSourceHeatPump,
)
from simulation.tasks import convert_seed
from simulation.tests.factories import (
    simulation_factory,
    random_name,
    seed_factory,
    floorplan_factory,
    rem_simulation_seed_factory,
    foundation_wall_factory,
    above_grade_wall_factory,
    roof_factory,
    frame_floor_factory,
    mechanical_equipment_factory,
)

from axis.company.tests.factories import rater_organization_factory
from axis.core.tests.testcases import ApiV3Tests
from axis.floorplan.models import Floorplan
from simulation.tests.factories.utils import dump_test_data

log = logging.getLogger(__name__)

__author__ = "Steven K"
__date__ = "3/19/21 12:35"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]


User = get_user_model()
XML_SOURCE_PATH = os.path.join(apps.get_app_config("remrate").path, "tests", "sources")


class MockTask:
    id = str(uuid.uuid4())

    def __init__(self, simulation_id, *args, **kwargs):
        pass


class SimulationViewSetTests(ApiV3Tests):
    def test_list_protected(self):
        """Can't get to this without auth"""
        url = reverse_lazy("api_v3:simulations-list")
        response = self.client.get(url, format="json")
        data = response.data

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            "{url}: Unexpected status code {response.status_code}: {data}".format(**locals()),
        )

    def test_detail_protected(self):
        """Can't see anything without auth"""
        sim = simulation_factory(company=rater_organization_factory(name=random_name()))

        url = reverse_lazy("api_v3:simulations-detail", args=[sim.pk])
        response = self.client.get(url, format="json")
        data = response.data

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            "{url}: Unexpected status code {response.status_code}: {data}".format(**locals()),
        )

        # I shouldn't be able to access others stuff
        user = User.objects.get_or_create(
            company=rater_organization_factory(name=random_name()),
            is_staff=False,
            is_superuser=False,
            username=random_name(),
            is_company_admin=True,
        )[0]
        simulation_factory(company=user.company)

        self.client.force_authenticate(user=user)
        response = self.client.get(url, format="json")
        data = response.data

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
            "{url}: Unexpected status code {response.status_code}: {data}".format(**locals()),
        )

    def test_list_valid_user(self):
        """Should be able to see mine"""
        user = User.objects.get_or_create(
            company=rater_organization_factory(), username=random_name(), is_company_admin=True
        )[0]
        simulation_factory(company=user.company)

        url = reverse_lazy("api_v3:simulations-list")

        data = self.list(url, user)

        self.assertEqual(len(data), 1)
        self.assertNotIn("project", data[0])
        self.assertNotIn("source_extra", data[0])

    def test_list_valid_competing_data_blind(self):
        """Ensure you only see that for which you are allowed to see"""
        user = User.objects.get_or_create(
            company=rater_organization_factory(name=random_name()),
            username=random_name(),
            is_company_admin=True,
        )[0]
        simulation_factory(company=user.company)

        url = reverse_lazy("api_v3:simulations-list")

        self.client.force_authenticate(user=user)

        response = self.client.get(url, format="json")
        data = response.data

        competing_user = User.objects.get_or_create(
            company=rater_organization_factory(name=random_name()),
            username=random_name(),
            is_company_admin=True,
        )[0]
        simulation_factory(company=competing_user.company)

        self.assertEqual(Simulation.objects.count(), 2)

        response = self.client.get(url, format="json")
        new_data = response.data
        self.assertEqual(len(new_data["results"]), 1)
        self.assertEqual(new_data["results"][0]["id"], data["results"][0]["id"])
        self.assertNotIn("project", new_data["results"][0])
        self.assertNotIn("source_extra", new_data["results"][0])

    def test_detail_data(self):
        """This should return the full detail of our stuff"""
        user = User.objects.get_or_create(
            company=rater_organization_factory(name=random_name()),
            username=random_name(),
            is_company_admin=True,
        )[0]
        sim = simulation_factory(company=user.company)

        url = reverse_lazy("api_v3:simulations-detail", args=[sim.pk])

        self.client.force_authenticate(user=user)
        response = self.client.get(url, format="json")
        data = response.data

        self.assertIn("project", data)

    def test_remxml_download(self):
        """This should download the Rem XML file."""
        user = User.objects.get_or_create(
            company=rater_organization_factory(name=random_name()),
            username=random_name(),
            is_company_admin=True,
        )[0]
        seed = rem_simulation_seed_factory(company=user.company)
        convert_seed(seed.id)
        seed = Seed.objects.get()
        sim = seed.simulation

        url = reverse_lazy("api_v3:simulations-remxml", args=[sim.pk])

        self.client.force_authenticate(user=user)

        with self.subTest("Passing RemXML"):
            response = self.client.get(url, format="json")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.get("content-type"), "application/xml")
            self.assertNotIn("&quot;", response.content.decode())

            root = etree.fromstring(response.content)
            self.assertIsNotNone(root)

            content = BytesIO(response.content)
            context = etree.iterparse(content, events=("start", "end"))
            count = 0
            for _action, _elem in context:
                count += 1
            self.assertGreater(count, 1000)
            content.close()
        with self.subTest("Failing RemXML"):
            Simulation.objects.all().update(source_type=SourceType.EKOTROPE)
            response = self.client.get(url, format="json")
            self.assertEqual(response.status_code, 400)

    @classmethod
    def floorplan_factory(cls, data_source="16.0", include_blg=True):
        """This probably will need to come out of here but it's fine for now"""
        seed = seed_factory(type=SourceType.REMRATE_SQL, data_source=data_source)
        rem_simulation = seed.source_remrate_sql_data
        company = seed.company

        if include_blg:
            document_path = None
            paths = [
                data_source,
                os.path.join(XML_SOURCE_PATH, data_source),
                os.path.join(XML_SOURCE_PATH, f"ALL_FIELDS_SET_{data_source}.blg"),
            ]
            for data_path in paths:
                if os.path.exists(data_path):
                    document_path = os.path.abspath(data_path)
                    break
            if not document_path:
                raise IOError(f"Data Source Specified {data_source} does not exist")
            temp_dir = tempfile.gettempdir()
            temp_document = os.path.join(temp_dir, os.path.basename(document_path))
            shutil.copy2(document_path, temp_document)

            with open(temp_document) as fh:
                floorplan, _cr = Floorplan.objects.get_or_create(
                    owner=company,
                    name=seed.simulation.name,
                    remrate_data_file=File(fh, name=os.path.basename(temp_document)),
                    remrate_target=rem_simulation,
                    simulation=seed.simulation,
                    square_footage=seed.simulation.conditioned_area,
                )
        else:
            floorplan, _cr = Floorplan.objects.get_or_create(
                owner=company,
                name=seed.simulation.name,
                remrate_target=rem_simulation,
                simulation=seed.simulation,
                square_footage=seed.simulation.conditioned_area,
            )
        return floorplan

    def test_blg_remxml_download(self):
        """Verify that we can pull a blg from a simulation via the floorplan"""
        # This will dump out a BLG File from a floorplan
        floorplan = self.floorplan_factory(data_source="16.0")
        sim = floorplan.simulation
        user = User.objects.get_or_create(
            company=floorplan.owner,
            username=random_name(),
            is_company_admin=True,
        )[0]

        url = reverse_lazy("api_v3:simulations-blg-remxml", args=[sim.pk])

        self.client.force_authenticate(user=user)
        response = self.client.get(url, format="application/xml")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get("content-type"), "application/xml")
        self.assertNotIn("&quot;", response.content.decode())

        root = etree.fromstring(response.content)
        self.assertIsNotNone(root)
        count = 0
        content = BytesIO(response.content)
        context = etree.iterparse(content, events=("start", "end"))
        for _action, _elem in context:
            count += 1

        self.assertGreater(count, 1000)
        content.close()

        self.assertEqual(Simulation.objects.count(), 2)

    def test_blg_remxml_fail_download(self):
        """Verify that if we don't have a floorplan we bail gracefully"""
        floorplan = self.floorplan_factory(data_source="16.0", include_blg=False)
        sim = floorplan.simulation
        user = User.objects.get_or_create(
            company=floorplan.owner,
            username=random_name(),
            is_company_admin=True,
        )[0]

        url = reverse_lazy("api_v3:simulations-blg-remxml", args=[sim.pk])
        self.client.force_authenticate(user=user)

        response = self.client.get(url, format="application/xml")
        self.assertEqual(response.status_code, 404)

        Floorplan.objects.update(simulation=None)

        response = self.client.get(url, format="application/xml")
        self.assertEqual(response.status_code, 404)

    def test_blg_sql_diff(self):
        floorplan = floorplan_factory(data_source="16.0")
        simulation = floorplan.simulation
        user = User.objects.get_or_create(
            company=floorplan.owner,
            username=random_name(),
            is_company_admin=True,
        )[0]

        url = reverse_lazy("api_v3:simulations-blg-compare", args=[simulation.pk])
        self.client.force_authenticate(user=user)

        response = self.client.get(url, format="application/xml")
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.data["errors"], [])
        self.assertEqual(response.data["warnings"], [])
        self.assertEqual(response.data["ignored"], [])
        self.assertIsNotNone(response.data["summary"])

    def test_diff_fails_missing_blg_file(self):
        floorplan = floorplan_factory(data_source="16.0")
        simulation = floorplan.simulation
        user = User.objects.get_or_create(
            company=floorplan.owner,
            username=random_name(),
            is_company_admin=True,
        )[0]

        url = reverse_lazy("api_v3:simulations-blg-compare", args=[simulation.pk])
        self.client.force_authenticate(user=user)

        # Test 400 response for missing BLG data file.
        floorplan.remrate_data_file = None
        floorplan.save()
        response = self.client.get(url, format="application/xml")
        self.assertContains(
            response, "Associated Floorplan or BLG File does not exist", status_code=404
        )

    def test_diff_fails_bad_simulation(self):
        floorplan = floorplan_factory(data_source="16.0")
        simulation = floorplan.simulation
        user = User.objects.get_or_create(
            company=floorplan.owner,
            username=random_name(),
            is_company_admin=True,
        )[0]

        url = reverse_lazy("api_v3:simulations-blg-compare", args=[simulation.pk])
        self.client.force_authenticate(user=user)

        # Fail when missing project data
        simulation.project.delete()

        response = self.client.get(url, format="application/xml")
        self.assertContains(response, "Unable to generate REM XML from simulation", status_code=400)

    def test_diff_fails_bad_blg(self):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".BLG") as tmp_blg:
            tmp_blg.write(b"REM/Rate Building File\n")
            tmp_blg.write(b"\n")
            tmp_blg.write(b"REM/Rate Bad Building File\n")

        floorplan = floorplan_factory(data_source="16.0", blg_path=tmp_blg.name)
        simulation = floorplan.simulation
        user = User.objects.get_or_create(
            company=floorplan.owner,
            username=random_name(),
            is_company_admin=True,
        )[0]

        url = reverse_lazy("api_v3:simulations-blg-compare", args=[simulation.pk])
        self.client.force_authenticate(user=user)
        response = self.client.get(url, format="application/xml")
        self.assertContains(response, "Bad BLG Data", status_code=400)
        os.unlink(tmp_blg.name)

    def test_diff_survives_empty_models(self):
        floorplan = floorplan_factory(data_source="16.0")
        simulation = floorplan.simulation
        user = User.objects.get_or_create(
            company=floorplan.owner,
            username=random_name(),
            is_company_admin=True,
        )[0]

        for photovoltaic in simulation.photovoltaics.all():
            photovoltaic.delete()

        url = reverse_lazy("api_v3:simulations-blg-compare", args=[simulation.pk])
        self.client.force_authenticate(user=user)

        response = self.client.get(url, format="application/xml")
        self.assertEqual(response.status_code, 200)

    def test_simulation_summary(self):
        floorplan = floorplan_factory(data_source="16.0")
        simulation = floorplan.simulation
        user = User.objects.get_or_create(
            company=floorplan.owner,
            username=random_name(),
            is_company_admin=True,
        )[0]

        url = reverse_lazy("api_v3:simulations-summary", args=[simulation.pk])
        self.client.force_authenticate(user=user)

        response = self.client.get(url, format="application/xml")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["version"], "16.0")
        self.assertIsNotNone(response.data["seed"])
        self.assertIsNotNone(response.data["available_analyses"])

    @mock.patch(
        "axis.floorplan.api_v3.viewsets.simulation.get_open_studio_eri_result.delay", MockTask
    )
    def test_generate_os_eri_score(self):
        floorplan = floorplan_factory(data_source="16.0")
        simulation = floorplan.simulation
        user = User.objects.get_or_create(
            company=floorplan.owner,
            username=random_name(),
            is_company_admin=True,
        )[0]
        with self.subTest("No data should kick off a default simulation"):
            self.assertEqual(simulation.analyses.count(), 1)
            url = reverse_lazy("api_v3:simulations-open-studio-eri", args=[simulation.pk])
            self.client.force_authenticate(user=user)
            response = self.client.post(url)
            self.assertEqual(response.status_code, 201)
            data = response.json()
            self.assertEqual(data["id"], simulation.id)
            self.assertEqual(len(data["analysis_ids"]), 2)
            self.assertEqual(data["status"], AnalysisStatus.PENDING)
            self.assertIsNotNone(data["task_id"])
            self.assertEqual(simulation.analyses.count(), 3)
            self.assertEqual(
                list(simulation.analyses.values_list("type", flat=True)),
                ["default", "eri_2019ab_design", "eri_2019ab_reference"],
            )
            analyses = simulation.analyses.filter(
                type__in=[AnalysisType.OS_ERI_2019AB_DESIGN, AnalysisType.OS_ERI_2019AB_REFERENCE],
                task__isnull=True,
            )
            self.assertEqual(analyses.count(), 0)
            analyses = simulation.analyses.filter(
                type__in=[AnalysisType.OS_ERI_2019AB_DESIGN, AnalysisType.OS_ERI_2019AB_REFERENCE],
                task__isnull=False,
                status=AnalysisStatus.PENDING,
            )
            self.assertEqual(analyses.count(), 2)
            simulation.analyses.all().delete()

        with self.subTest("Run a bunch of simulations"):
            self.assertEqual(simulation.analyses.count(), 0)
            url = reverse_lazy("api_v3:simulations-open-studio-eri", args=[simulation.pk])
            self.client.force_authenticate(user=user)
            data = {
                OpenStudioAnalysisSourceName.ERI_CALCULATION.value: "2014",
                OpenStudioAnalysisSourceName.IECC_CALCULATION.value: "2018",
                OpenStudioAnalysisSourceName.ESTAR_CALCULATION.value: "SF_OregonWashington_3.2",
                OpenStudioAnalysisSourceName.ZERH_CALCULATION.value: "SF_2.0",
            }
            response = self.client.post(url, data=data)
            self.assertEqual(response.status_code, 201, response.json())
            data = response.json()
            self.assertEqual(data["id"], simulation.id)
            self.assertEqual(len(data["analysis_ids"]), 8)
            self.assertEqual(data["status"], AnalysisStatus.PENDING)
            self.assertIsNotNone(data["task_id"])

    @mock.patch(
        "axis.floorplan.api_v3.viewsets.simulation.get_open_studio_eri_result.delay", MockTask
    )
    def test_get_os_eri_score(self):
        floorplan = floorplan_factory(data_source="16.0")
        simulation = floorplan.simulation
        user = User.objects.get_or_create(
            company=floorplan.owner,
            username=random_name(),
            is_company_admin=True,
        )[0]
        url = reverse_lazy("api_v3:simulations-open-studio-eri", args=[simulation.pk])
        self.client.force_authenticate(user=user)

        with self.subTest("No simulation yet"):
            response = self.client.get(url)
            self.assertEqual(response.status_code, 400)

        response = self.client.post(url)
        self.assertEqual(response.status_code, 201)

        with self.subTest("After we kick it off"):
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["id"], simulation.id)
            self.assertEqual(data["status"], "pending")
            self.assertEqual(len(data["analysis_ids"]), 2)
            self.assertIsNotNone(data["task_id"])

        simulation.analyses.filter(id=data["analysis_ids"][0]).update(status=AnalysisStatus.FAILED)
        with self.subTest("Failed"):
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["id"], simulation.id)
            self.assertEqual(data["status"], "failed")
            self.assertEqual(len(data["analysis_ids"]), 2)
            self.assertIsNotNone(data["task_id"])
            # This should completely fail
            response = self.client.post(url)
            self.assertEqual(response.status_code, 400)

        simulation.analyses.filter(id=data["analysis_ids"][0]).update(status=AnalysisStatus.STARTED)
        with self.subTest("started"):
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["id"], simulation.id)
            self.assertEqual(data["status"], "started")
            self.assertEqual(len(data["analysis_ids"]), 2)
            self.assertIsNotNone(data["task_id"])

        simulation.analyses.filter(id__in=data["analysis_ids"]).update(
            status=AnalysisStatus.COMPLETE
        )
        with self.subTest("complete"):
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["id"], simulation.id)
            self.assertEqual(data["status"], "complete")
            self.assertEqual(len(data["analysis_ids"]), 2)
            self.assertIsNotNone(data["task_id"])


class SimulationNestedViewSetTests(ApiV3Tests):
    def setUp(self) -> None:
        self.simulation = simulation_factory(company=rater_organization_factory(name=random_name()))
        self.user = User.objects.get_or_create(
            company=self.simulation.company,
            username=random_name(),
            is_company_admin=True,
        )[0]

        self.client.force_authenticate(user=self.user)
        return super(SimulationNestedViewSetTests, self).setUp()

    def test_project(self):
        url = reverse_lazy("api_v3:simulation-project-list", args=[self.simulation.id])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 200)

    def test_mechanicals(self):
        url = reverse_lazy("api_v3:simulation-mechanicals-list", args=[self.simulation.id])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 200)

    def test_foundation_walls(self):
        url = reverse_lazy("api_v3:simulation-foundation_walls-list", args=[self.simulation.id])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 200)

        foundation_wall = foundation_wall_factory(simulation=self.simulation)
        url = reverse_lazy(
            "api_v3:simulation-foundation_walls-detail",
            args=[self.simulation.id, foundation_wall.id],
        )
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 200)

    def test_abovegrade_walls(self):
        url = reverse_lazy("api_v3:simulation-abovegrade_walls-list", args=[self.simulation.id])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 200)

        above_grade_wall = above_grade_wall_factory(simulation=self.simulation)
        url = reverse_lazy(
            "api_v3:simulation-abovegrade_walls-detail",
            args=[self.simulation.id, above_grade_wall.id],
        )
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 200)

    def test_roofs(self):
        url = reverse_lazy("api_v3:simulation-roofs-list", args=[self.simulation.id])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 200)

        roof = roof_factory(simulation=self.simulation)
        url = reverse_lazy("api_v3:simulation-roofs-detail", args=[self.simulation.id, roof.id])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 200)

    def test_floors(self):
        url = reverse_lazy("api_v3:simulation-floors-list", args=[self.simulation.id])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 200)

        floor = frame_floor_factory(simulation=self.simulation)
        url = reverse_lazy("api_v3:simulation-floors-detail", args=[self.simulation.id, floor.id])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 200)

    def test_mechanicals_are_in_order(self):
        # Make sure that we don't have a statistical pattern in this
        def randomize_pks():
            for Model in [
                Heater,
                AirConditioner,
                GroundSourceHeatPump,
                AirSourceHeatPump,
                WaterHeater,
                Dehumidifier,
            ]:
                for obj in Model.objects.all():
                    obj.id = random.randint(9000, 9500)
                    obj.save()

        simulation = simulation_factory(
            company=self.simulation.company,
            ground_source_heat_pump_count=1,
            heater_count=2,
            water_heater_count=2,
            air_conditioner_count=2,
            dehumidifier_count=1,
            air_source_heat_pump_count=1,
        )
        randomize_pks()

        url = reverse_lazy("api_v3:simulation-mechanicals-list", args=[simulation.id])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 200)

        mechanicals = response.data["results"]
        self.assertIsNotNone(mechanicals[0]["heater"])
        self.assertIsNotNone(mechanicals[1]["heater"])
        self.assertIsNotNone(mechanicals[2]["air_conditioner"])
        self.assertIsNotNone(mechanicals[3]["air_conditioner"])
        self.assertIsNotNone(mechanicals[4]["air_source_heat_pump"])
        self.assertIsNotNone(mechanicals[5]["ground_source_heat_pump"])
        self.assertIsNotNone(mechanicals[6]["water_heater"])
        self.assertIsNotNone(mechanicals[7]["water_heater"])
        self.assertIsNotNone(mechanicals[8]["dehumidifier"])

        simulation = simulation_factory(
            company=self.simulation.company,
            ground_source_heat_pump_count=1,
            heater_count=0,
            water_heater_count=0,
            air_conditioner_count=2,
            dehumidifier_count=1,
            air_source_heat_pump_count=1,
        )
        randomize_pks()

        url = reverse_lazy("api_v3:simulation-mechanicals-list", args=[simulation.id])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 200)

        mechanicals = response.data["results"]
        self.assertIsNotNone(mechanicals[0]["air_conditioner"])
        self.assertIsNotNone(mechanicals[1]["air_conditioner"])
        self.assertIsNotNone(mechanicals[2]["air_source_heat_pump"])
        self.assertIsNotNone(mechanicals[3]["ground_source_heat_pump"])
        self.assertIsNotNone(mechanicals[4]["dehumidifier"])

        mechanical_equipment_factory(simulation, equipment_type="heater")
        randomize_pks()

        url = reverse_lazy("api_v3:simulation-mechanicals-list", args=[simulation.id])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 200)

        mechanicals = response.data["results"]
        self.assertIsNotNone(mechanicals[0]["heater"])
        self.assertIsNotNone(mechanicals[1]["air_conditioner"])
        self.assertIsNotNone(mechanicals[2]["air_conditioner"])
        self.assertIsNotNone(mechanicals[3]["air_source_heat_pump"])
        self.assertIsNotNone(mechanicals[4]["ground_source_heat_pump"])
        self.assertIsNotNone(mechanicals[5]["dehumidifier"])
