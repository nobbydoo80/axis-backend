# -*- coding: utf-8 -*-
"""test_floorplan.py: """


__author__ = "Rajesh Pethe"
__date__ = "10/05/2022 08:56:37"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Rajesh Pethe",
    "Steven Klass",
]

import glob
import os
import random

from django.core.files import File
from django.urls import reverse_lazy

from axis.core.tests.testcases import ApiV3Tests
from axis.floorplan.models import Floorplan
from axis.floorplan.tests.factories import floorplan_with_simulation_factory
from axis.core.tests.factories import rater_admin_factory
from simulation.models import FoundationWall, FrameFloor
from simulation.tests.factories import simulation_factory, random_name
from django.contrib.auth import get_user_model
from django.utils.http import urlencode
from simulation.enumerations import Location, SourceType

User = get_user_model()


class TestFloorplantViewSet(ApiV3Tests):
    def setUp(self):
        self.rater_admin = rater_admin_factory()
        # self.simulation = simulation_factory(company=self.rater_admin.company)
        self.user = User.objects.get_or_create(
            company=self.rater_admin.company,
            username=random_name(),
            is_company_admin=True,
        )[0]

        self.client.force_authenticate(user=self.user)

    def test_floorplan(self):
        simulation = simulation_factory(company=self.rater_admin.company)
        floorplan_with_simulation_factory(owner=simulation.company, simulation=simulation)
        url = reverse_lazy("api_v3:floorplans-list")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 200)

    def test_floorplan_crawlspace_filter(self):
        simulation = simulation_factory(
            company=self.rater_admin.company,
            foundation_wall_count=1,
            foundation_wall__interior_location=Location.ENCLOSED_CRAWL,
            frame_floor_count=1,
            frame_floor__exterior_location=Location.ENCLOSED_CRAWL,
            slabs_count=0,
        )
        floorplan_with_simulation_factory(owner=simulation.company, simulation=simulation)
        list_url = reverse_lazy("api_v3:floorplans-list")

        query_params = {"crawl_space": "vented"}
        url = f"{list_url}?{urlencode(query_params)}"
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 0)

        fw: FoundationWall = simulation.foundation_walls.first()
        fw.interior_location = Location.OPEN_CRAWL_SPACE
        fw.save()
        ff: FrameFloor = simulation.frame_floors.first()
        ff.exterior_location = Location.OPEN_CRAWL_SPACE
        ff.save()

        query_params = {"crawl_space": "vented"}
        url = f"{list_url}?{urlencode(query_params)}"
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)

    def test_floorplan_slabs_filter(self):
        simulation = simulation_factory(company=self.rater_admin.company, slabs_count=3)
        floorplan_with_simulation_factory(owner=simulation.company, simulation=simulation)
        list_url = reverse_lazy("api_v3:floorplans-list")

        query_params = {"has_slabs": "false"}
        url = f"{list_url}?{urlencode(query_params)}"
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)

    def test_photovoltaics_filter(self):
        simulation = simulation_factory(company=self.rater_admin.company, photovoltaic_count=0)
        floorplan_with_simulation_factory(owner=simulation.company, simulation=simulation)

        list_url = reverse_lazy("api_v3:floorplans-list")

        query_params = {"has_photovoltaics": "false"}
        url = f"{list_url}?{urlencode(query_params)}"
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 0)

    def test_floorplan_attic_filter(self):
        simulation = simulation_factory(
            company=self.rater_admin.company,
            roof_count=3,
            roof__interior_location=Location.ATTIC_VENTED,
        )
        floorplan_with_simulation_factory(owner=simulation.company, simulation=simulation)
        list_url = reverse_lazy("api_v3:floorplans-list")

        query_params = {"attic_type": "vented"}
        url = f"{list_url}?{urlencode(query_params)}"
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)

        simulation.delete()

        simulation = simulation_factory(
            company=self.rater_admin.company,
            roof_count=3,
            roof__interior_location=Location.SEALED_ATTIC,
        )
        floorplan_with_simulation_factory(owner=simulation.company, simulation=simulation)
        list_url = reverse_lazy("api_v3:floorplans-list")

        query_params = {"attic_type": "unvented"}
        url = f"{list_url}?{urlencode(query_params)}"
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)

        simulation.delete()

        simulation = simulation_factory(
            company=self.rater_admin.company,
            roof_count=3,
            roof__interior_location=Location.VAULTED_ROOF,
        )
        floorplan_with_simulation_factory(owner=simulation.company, simulation=simulation)

        query_params = {"attic_type": "vented"}
        url = f"{list_url}?{urlencode(query_params)}"
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 0)

    def test_floorplan_ceilings_filter(self):
        simulation = simulation_factory(
            company=self.rater_admin.company,
            roof_count=3,
            roof__interior_location=Location.VAULTED_ROOF,
        )
        floorplan_with_simulation_factory(owner=simulation.company, simulation=simulation)
        list_url = reverse_lazy("api_v3:floorplans-list")

        query_params = {"vaulted_ceilings": True}
        url = f"{list_url}?{urlencode(query_params)}"
        response = self.client.get(url, format="json")
        self.assertEqual(response.data["count"], 1)

        query_params = {"vaulted_ceilings": False}
        url = f"{list_url}?{urlencode(query_params)}"
        response = self.client.get(url, format="json")
        self.assertEqual(response.data["count"], 0)

    def test_filter_by_num_stories(self):
        simulation = simulation_factory(
            company=self.rater_admin.company,
        )
        floorplan_with_simulation_factory(owner=simulation.company, simulation=simulation)
        list_url = reverse_lazy("api_v3:floorplans-list")

        query_params = {"num_stories": simulation.floors_on_or_above_grade}
        url = f"{list_url}?{urlencode(query_params)}"

        response = self.client.get(url, format="json")
        self.assertEqual(response.data["count"], 1)

    def test_floorplan_flat_list(self):
        simulation = simulation_factory(
            company=self.rater_admin.company, source_type=SourceType.REMRATE_SQL
        )
        floorplan_with_simulation_factory(owner=simulation.company, simulation=simulation)
        list_url = reverse_lazy("api_v3:floorplans-flat-list")
        response = self.client.get(list_url, format="json")
        self.assertEqual(response.status_code, 200)
        data = response.data["results"][0]
        self.assertIsNotNone(data["simulation_info"])
        self.assertEqual(data["simulation_info"]["source_type"], SourceType.REMRATE_SQL)
        self.assertEqual(
            data["simulation_info"]["source_type_display"], SourceType.REMRATE_SQL.label
        )

    def test_floorplan_create_from_blg(self):
        url = reverse_lazy("api_v3:floorplans-create-from-blg")
        BLG_FILE_PATH = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__), "..", "..", "..", "..", "remrate", "tests", "sources"
            )
        )
        paths = BLG_FILE_PATH + "/*.blg"
        file_path = random.choice(glob.glob(paths))

        self.assertEqual(Floorplan.objects.count(), 0)

        with self.subTest("Clean post"):
            with open(file_path) as f:
                response = self.client.post(
                    url,
                    data={"file": File(f, name=os.path.basename(file_path))},
                    format="multipart",
                )
            self.assertEqual(response.status_code, 201)
            self.assertEqual(Floorplan.objects.count(), 1)
            floorplan = Floorplan.objects.get()
            self.assertIsNotNone(floorplan.owner)
            self.assertIsNotNone(floorplan.name)
            self.assertIsNotNone(floorplan.number)
            self.assertIsNotNone(floorplan.remrate_data_file)
            self.assertIsNotNone(floorplan.simulation)
            self.assertIsNotNone(floorplan.square_footage)
            self.assertEqual(floorplan.type, Floorplan.INPUT_DATA_TYPE_BLG_DATA)
            self.assertIsNone(floorplan.ekotrope_houseplan)
            self.assertIsNone(floorplan.remrate_target)
            self.assertEqual(floorplan.customer_documents.count(), 1)

        with self.subTest("Duplicates not allowed"):
            with open(file_path) as f:
                response = self.client.post(
                    url,
                    data={"file": File(f, name=os.path.basename(file_path))},
                    format="multipart",
                )
            self.assertEqual(response.status_code, 400)
            self.assertEqual(Floorplan.objects.count(), 1)
