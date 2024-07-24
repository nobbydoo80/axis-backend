"""test_floorplan_nested_viewsets.py: """


__author__ = "Steven K"
__date__ = "3/19/21 12:36"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]


import io

from django.urls import reverse_lazy

from axis.core.tests.testcases import ApiV3Tests
from axis.floorplan.tests.factories import floorplan_with_simulation_factory
from axis.core.tests.factories import rater_admin_factory
from simulation.tests.factories import simulation_factory
from axis.home.tests.factories import eep_program_custom_home_status_factory


class TestFloorplanNestedViewSets(ApiV3Tests):
    def setUp(self):
        self.rater_admin = rater_admin_factory()
        self.simulation = simulation_factory(company=self.rater_admin.company)
        floorplan_with_simulation_factory(owner=self.simulation.company, simulation=self.simulation)

    def test_create_and_list(self):
        user = self.rater_admin
        create_url = reverse_lazy(
            "api_v3:floorplan-documents-list", args=(self.simulation.floorplan.id,)
        )
        with io.open(__file__, "rb") as file:
            obj = self.create(
                user=self.rater_admin,
                url=create_url,
                data=dict(
                    document=file,
                    description="test floorplan doc",
                    is_public=False,
                ),
                data_format="multipart",
            )
        self.assertTrue(bool(obj["document"]))
        self.assertEqual(obj["description"], "test floorplan doc")
        self.assertFalse(obj["is_public"])

        list_url = reverse_lazy(
            "api_v3:floorplan-documents-list", args=(self.simulation.floorplan.id,)
        )
        data = self.list(user=user, url=list_url)
        self.assertEqual(len(data), self.simulation.floorplan.customer_documents.count())

    def test_floorplan_homes(self):
        eep_program_custom_home_status_factory(
            company=self.simulation.company,
            skip_floorplan=False,
            floorplan=self.simulation.floorplan,
        )
        user = self.rater_admin
        list_url = reverse_lazy(
            "api_v3:floorplan-home_statuses-list", args=(self.simulation.floorplan.id,)
        )
        data = self.list(url=list_url, user=user)
        self.assertEqual(len(data), 1)
        self.assertIsNotNone(data[0]["home"])
        self.assertIsNotNone(data[0]["home_info"]["id"])
        self.assertIsNotNone(data[0]["home_info"]["slug"])
        self.assertIsNone(data[0]["home_info"]["subdivision"])
        self.assertIsNone(data[0]["home_info"]["subdivision_info"])
        self.assertEqual(data[0]["home_info"]["is_custom_home"], True)
        self.assertEqual(data[0]["home_info"]["is_active"], True)
        self.assertEqual(data[0]["home_info"]["bulk_uploaded"], False)
        self.assertIsNotNone(data[0]["home_info"]["street_line1_profile"])
        self.assertIsNotNone(data[0]["home_info"]["modified_date"])
        self.assertIsNotNone(data[0]["home_info"]["created_date"])
        self.assertIsNotNone(data[0]["home_info"]["home_address"])
        self.assertEqual(len(data[0]["home_info"]["eep_programs"]), 1)
