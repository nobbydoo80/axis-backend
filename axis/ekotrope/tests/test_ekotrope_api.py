"""test_ekotrope_api.py: Django """

import logging
from unittest import mock

from django import test
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from axis.core.tests.factories import rater_admin_factory
from axis.ekotrope.models import Project, EkotropeAuthDetails, HousePlan, Analysis
from axis.ekotrope.utils import (
    request_project_list,
    request_project,
    request_houseplan,
    request_analysis,
    stub_project_list,
    stub_houseplan_list,
    import_project,
    import_houseplan,
    import_analysis,
    import_project_tree,
)
from simulation.models import Seed, Simulation
from .mock_responses import (
    mocked_requests_get_project,
    mocked_requests_get_projects_eula,
    mocked_requests_get_projects,
    mocked_requests_get_houseplan,
    mocked_requests_get_analysis,
    mocked_requests_get_detail_bad,
    mocked_project_list,
    mocked_request_project,
    mocked_request_houseplan,
    mocked_request_analysis,
    mocked_request_fail,
)

log = logging.getLogger(__name__)

__author__ = "Steven Klass"
__date__ = "11/16/18 1:08 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

valid_upload = """%%%INI%%%@@^^^?xml version="1.0" encoding="UTF-8"?^^^@@
@@^^^response^^^@@@@^^^files^^^@@@@^^^file^^^@@@@^^^ctype^^^@@application/xhtml+xml@@^^^/ctype^^^@@
@@^^^size^^^@@0@@^^^/size^^^@@
@@^^^field^^^@@GWTMU-033856229458416454-0@@^^^/field^^^@@
@@^^^name^^^@@ALL_FIELDS_SET_15.0.xml@@^^^/name^^^@@
@@^^^/file^^^@@
@@^^^/files^^^@@
@@^^^finished^^^@@ok@@^^^/finished^^^@@
@@^^^message^^^@@@@^^^![CDATA[RjcFxauy]]^^^@@@@^^^/message^^^@@
@@^^^parameters^^^@@@@^^^/parameters^^^@@
@@^^^/response^^^@@
%%%END%%%"""

valid_upload_1 = """%%%INI%%%@@^^^?xml version="1.0" encoding="UTF-8"?^^^@@
@@^^^response^^^@@@@^^^files^^^@@@@^^^file^^^@@@@^^^ctype^^^@@application/xml@@^^^/ctype^^^@@
@@^^^size^^^@@92915@@^^^/size^^^@@
@@^^^field^^^@@GWTMU-149233805302356460-0@@^^^/field^^^@@
@@^^^name^^^@@ALL_FIELDS_SET_14.6.1.xml@@^^^/name^^^@@
@@^^^/file^^^@@
@@^^^/files^^^@@
@@^^^finished^^^@@ok@@^^^/finished^^^@@
@@^^^message^^^@@@@^^^![CDATA[G6weckk9]]^^^@@@@^^^/message^^^@@
@@^^^parameters^^^@@@@^^^/parameters^^^@@
@@^^^/response^^^@@
%%%END%%%
"""


def parse_response(data):
    if not data.startswith("%%%INI%%%"):
        log.error("Expected response does not start with INI")
    if not data.endswith("%%%END%%%"):
        log.error("Expected response does not end with END")
    result = {}
    for x in data[9:-10].split("\n"):
        split = [y.split("^^^@@") for y in x.split("@@^^^")]
        if split[1][0] == "message" and split[2]:
            result[split[1][0]] = split[2][0]
        elif len(split[1]) == 2 and not split[1][0].startswith("/"):
            result[split[1][0]] = split[1][1]
    return result


class TestEkotropeUtils(test.TestCase):
    """This will flex out the utils stub and import routines"""

    def setUp(self):
        self.user = rater_admin_factory()
        self.eko_auth_details = EkotropeAuthDetails.objects.create(
            username="axis-api", password="password", user=self.user
        )

    @mock.patch("requests.get", side_effect=mocked_requests_get_projects)
    def test_request_list(self, _side_affect):
        """Flexes the actual _request_list"""
        data = request_project_list(self.eko_auth_details)
        self.assertEqual(len(data), 2)

    @mock.patch("requests.get", side_effect=mocked_requests_get_projects_eula)
    def test_request_list_bad(self, _side_affect):
        """Flexes the actual _request_list when we get a Eula log it but ignore it."""
        data = request_project_list(self.eko_auth_details)
        self.assertEqual(data, [])

    @mock.patch("requests.get", side_effect=mocked_requests_get_project)
    def test_request_project(self, _side_affect):
        """Flexes the _request_detail"""
        data, url = request_project(self.eko_auth_details, "some_id")
        self.assertGreater(len(data), 20)
        valid = {
            "createdBy",
            "model",
            "community",
            "isLocked",
            "name",
            "lotNumber",
            "submittedProjectId",
            "plans",
            "thirdParty",
            "id",
            "location",
            "notes",
            "constructionYear",
            "masterPlanId",
            "lastSavedBy",
            "createdAt",
            "hersRatingDetails",
            "lastSavedAt",
            "resultsUnchangedSince",
            "algorithmVersion",
            "status",
            "utilityRates",
            "builder",
            "builderPermitDateOrNumber",
            "selfOrPlanLastSavedAt",
        }
        self.assertEqual(set(data), valid)

    @mock.patch("requests.get", side_effect=mocked_requests_get_detail_bad)
    def test_request_detail_bad(self, _side_affect):
        """Flexes the _request_detail"""
        self.assertRaises(Exception, request_project, self.eko_auth_details)

    @mock.patch("requests.get", side_effect=mocked_requests_get_houseplan)
    def test_request_houseplan(self, _side_affect):
        """Flexes the _request_detail"""
        data, url = request_houseplan(self.eko_auth_details, "some_id")
        self.assertGreater(len(data), 8)
        valid = {
            "appliances",
            "onsiteGenerations",
            "waterSystem",
            "details",
            "id",
            "lighting",
            "mechanicals",
            "thermalEnvelope",
            "name",
        }
        self.assertEqual(set(data), valid)

    @mock.patch("requests.get", side_effect=mocked_requests_get_analysis)
    def test_request_analysis(self, _side_affect):
        """Flexes the _request_detail"""
        data, url = request_analysis(self.eko_auth_details, "some_id")
        valid = {
            "energy",
            "compliance",
            "hersScore",
            "name",
            "hersScoreNoPv",
            "id",
            "thirdParty",
            "buildingType",
            "emissions",
        }
        self.assertEqual(set(data), valid)

    @mock.patch("requests.get", side_effect=mocked_requests_get_analysis)
    def test_request_analysis_building_type(self, _side_affect):
        """Flexes the _request_detail"""
        data, url = request_analysis(
            self.eko_auth_details, "some_id", building_type="EPSNewConstructionOregon2020Proposed"
        )
        valid = {
            "energy",
            "compliance",
            "hersScore",
            "name",
            "hersScoreNoPv",
            "id",
            "thirdParty",
            "buildingType",
            "emissions",
        }
        self.assertEqual(set(data), valid)
        self.assertEqual(data["buildingType"], "EPSNewConstructionOregon2020Proposed")

    @mock.patch("requests.get", side_effect=mocked_requests_get_analysis)
    def test_request_analysis_code_to_check(self, _side_affect):
        """Flexes the _request_detail"""
        data, url = request_analysis(
            self.eko_auth_details, "some_id", codes_to_check=["EnergyStarV3"]
        )
        self.assertEqual(data["compliance"][0]["code"], "EnergyStarV3")

    @mock.patch("axis.ekotrope.utils.request_project_list", side_effect=mocked_project_list)
    def test_stub_project_list(self, _side_affect):
        """Tests stubbing out the project lists"""
        stub_project_list(self.eko_auth_details)
        self.assertEqual(Project.objects.count(), 2)
        self.assertEqual(Project.objects.first().data, {})
        self.assertEqual(Project.objects.last().data, {})
        self.assertEqual(HousePlan.objects.count(), 0)

    @mock.patch("axis.ekotrope.utils.request_project", side_effect=mocked_request_project)
    def test_stub_houseplan(self, _side_affect):
        """Tests stubbing out the house plans for a given project"""
        stub_houseplan_list(self.eko_auth_details, "Test")
        self.assertEqual(Project.objects.count(), 1)
        self.assertEqual(HousePlan.objects.count(), 1)
        self.assertEqual(HousePlan.objects.get().data, {})

    @mock.patch("axis.ekotrope.utils.request_project", side_effect=mocked_request_project)
    def test_import_project(self, _side_affect):
        """Tests importing a project"""
        import_project(self.eko_auth_details, "Test")
        self.assertEqual(Project.objects.count(), 1)
        self.assertEqual(HousePlan.objects.count(), 0)

        project = Project.objects.get()
        self.assertNotEqual(project.data, {})
        self.assertIsNone(project.import_request)
        self.assertIsNone(project.import_error)
        self.assertIsNone(project.import_traceback)
        self.assertFalse(project.import_failed)

    @mock.patch("axis.ekotrope.utils.request_project", side_effect=mocked_request_fail)
    def test_import_project_fail(self, _side_affect):
        """Tests importing a project with failure"""
        import_project(self.eko_auth_details, "Test")
        self.assertEqual(Project.objects.count(), 1)
        project = Project.objects.get()
        self.assertEqual(project.data, "BAD DATA")
        self.assertIsNotNone(project.import_request)
        self.assertIsNotNone(project.import_error)
        self.assertIsNotNone(project.import_traceback)
        self.assertTrue(project.import_failed)

    @mock.patch("axis.ekotrope.utils.request_project", side_effect=mocked_request_project)
    @mock.patch("axis.ekotrope.utils.request_houseplan", side_effect=mocked_request_houseplan)
    def test_import_houseplan(self, _side_affect, _side_affect_2):
        """Tests importing a houseplan fully"""
        stub_houseplan_list(self.eko_auth_details, "Test")
        self.assertEqual(Project.objects.count(), 1)
        self.assertEqual(HousePlan.objects.count(), 1)
        self.assertEqual(HousePlan.objects.get().data, {})
        project = Project.objects.get()
        stubbed_house_plan = HousePlan.objects.get()
        import_houseplan(
            self.eko_auth_details, project, stubbed_house_plan.id, stubbed_house_plan.name
        )
        house_plan = HousePlan.objects.get()
        self.assertNotEqual(house_plan.data, {})
        self.assertIsNone(house_plan.import_request)
        self.assertIsNone(house_plan.import_error)
        self.assertIsNone(house_plan.import_traceback)
        self.assertFalse(house_plan.import_failed)

    @mock.patch("axis.ekotrope.utils.request_project", side_effect=mocked_request_project)
    @mock.patch("axis.ekotrope.utils.request_houseplan", side_effect=mocked_request_fail)
    def test_import_houseplan_fail(self, _side_affect, _side_affect_2):
        """Tests importing a houseplan with failure"""
        stub_houseplan_list(self.eko_auth_details, "Test")
        self.assertEqual(Project.objects.count(), 1)
        self.assertEqual(HousePlan.objects.count(), 1)
        self.assertEqual(HousePlan.objects.get().data, {})
        project = Project.objects.get()
        stubbed_house_plan = HousePlan.objects.get()
        import_houseplan(
            self.eko_auth_details, project, stubbed_house_plan.id, stubbed_house_plan.name
        )
        house_plan = HousePlan.objects.get()
        self.assertEqual(house_plan.data, "BAD DATA")
        self.assertIsNotNone(house_plan.import_request)
        self.assertIsNotNone(house_plan.import_error)
        self.assertIsNotNone(house_plan.import_traceback)
        self.assertTrue(house_plan.import_failed)

    @mock.patch("axis.ekotrope.utils.request_project", side_effect=mocked_request_project)
    @mock.patch("axis.ekotrope.utils.request_houseplan", side_effect=mocked_request_houseplan)
    @mock.patch("axis.ekotrope.utils.request_analysis", side_effect=mocked_request_analysis)
    def test_import_analysis(self, _side_affect, _side_affect_2, _side_affect_3):
        """Tests importing in analysis.  Note Analysis is directly linked to the houseplan"""
        stub_houseplan_list(self.eko_auth_details, "Test")
        self.assertEqual(Project.objects.count(), 1)
        self.assertEqual(HousePlan.objects.count(), 1)
        self.assertEqual(Analysis.objects.count(), 0)
        self.assertEqual(HousePlan.objects.get().data, {})
        stubbed_house_plan = HousePlan.objects.get()
        import_analysis(
            self.eko_auth_details,
            stubbed_house_plan,
            stubbed_house_plan.id,
            stubbed_house_plan.name,
        )
        self.assertEqual(Analysis.objects.count(), 1)

        analysis = Analysis.objects.get()
        self.assertNotEqual(analysis.data, {})
        self.assertIsNone(analysis.import_request)
        self.assertIsNone(analysis.import_error)
        self.assertIsNone(analysis.import_traceback)
        self.assertFalse(analysis.import_failed)

    @mock.patch("axis.ekotrope.utils.request_project", side_effect=mocked_request_project)
    @mock.patch("axis.ekotrope.utils.request_houseplan", side_effect=mocked_request_houseplan)
    @mock.patch("axis.ekotrope.utils.request_analysis", side_effect=mocked_request_fail)
    def test_import_analysis_fail(self, _side_affect, _side_affect_2, _side_affect_3):
        """Tests importing in analysis with failure."""
        stub_houseplan_list(self.eko_auth_details, "Test")
        self.assertEqual(Project.objects.count(), 1)
        self.assertEqual(HousePlan.objects.count(), 1)
        self.assertEqual(Analysis.objects.count(), 0)
        self.assertEqual(HousePlan.objects.get().data, {})
        stubbed_house_plan = HousePlan.objects.get()
        import_analysis(
            self.eko_auth_details,
            stubbed_house_plan,
            stubbed_house_plan.id,
            stubbed_house_plan.name,
        )
        self.assertEqual(Analysis.objects.count(), 1)

        analysis = Analysis.objects.get()
        self.assertEqual(analysis.data, "BAD DATA")
        self.assertIsNotNone(analysis.import_request)
        self.assertIsNotNone(analysis.import_error)
        self.assertIsNotNone(analysis.import_traceback)
        self.assertTrue(analysis.import_failed)

    @mock.patch("axis.ekotrope.utils.request_project", side_effect=mocked_request_project)
    @mock.patch("axis.ekotrope.utils.request_houseplan", side_effect=mocked_request_houseplan)
    @mock.patch("axis.ekotrope.utils.request_analysis", side_effect=mocked_request_analysis)
    def test_import_project_tree(self, _side_affect, _side_affect_2, _side_affect_3):
        """Tests importing in analysis.  Note Analysis is directly linked to the houseplan"""
        import_project_tree(self.eko_auth_details, "Test")
        self.assertEqual(Project.objects.count(), 1)
        self.assertEqual(HousePlan.objects.count(), 1)
        self.assertEqual(Analysis.objects.count(), 1)

        self.assertEqual(Seed.objects.count(), 1)
        self.assertEqual(Simulation.objects.count(), 1)
        self.assertEqual(Simulation.objects.get().analyses.count(), 32)


class TestEkotropeAPI(APITestCase):
    """This will flex out our API"""

    def setUp(self):
        self.user = rater_admin_factory()
        self.eko_auth_details = EkotropeAuthDetails.objects.create(
            username="axis-api", password="password", user=self.user
        )
        self.client.force_authenticate(user=self.user)

    @mock.patch("axis.ekotrope.utils.request_project_list", side_effect=mocked_project_list)
    @mock.patch("axis.ekotrope.utils.request_project", side_effect=mocked_request_project)
    @mock.patch("axis.ekotrope.utils.request_houseplan", side_effect=mocked_request_houseplan)
    @mock.patch("axis.ekotrope.utils.request_analysis", side_effect=mocked_request_analysis)
    def test_refresh_api(self, _side_affect, _side_affect_2, _side_affect_3, _side_affect_4):
        """This allows us to refresh projects"""
        url = reverse("apiv2:houseplan-refresh-projects")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 201)
        self.assertIn("msg", response.json())

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("msg", response.json())

    def test_refresh_api_missing_creds(self):
        """This allows us to refresh projects"""
        url = reverse("apiv2:houseplan-refresh-projects")
        user = rater_admin_factory()
        self.client.force_authenticate(user=user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)
        self.assertIn("error", response.json())
