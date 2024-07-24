"""test_managment.py - Axis"""

import logging
import os
from unittest import mock

from django import test
from django.core import management
from django.core.management import CommandError
from django.forms import model_to_dict

from axis.core.tests.factories import rater_admin_factory
from axis.ekotrope.models import EkotropeAuthDetails, Project, HousePlan, Analysis
from simulation.models import Simulation
from .mock_responses import (
    mocked_request_project,
    mocked_request_houseplan,
    mocked_request_analysis,
    mocked_project_list,
    mocked_import_project_tree,
)
from ...floorplan.models import Floorplan

log = logging.getLogger(__name__)

__author__ = "Steven K"
__date__ = "8/7/20 11:23"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]


class TestEkotropeManagement(test.TestCase):
    """This will flex out the management routines"""

    def setUp(self):
        self.user = rater_admin_factory()
        self.eko_auth_details = EkotropeAuthDetails.objects.create(
            username="axis-api", password="password", user=self.user
        )

    @mock.patch("axis.ekotrope.utils.request_project_list", side_effect=mocked_project_list)
    @mock.patch("axis.ekotrope.utils.request_project", side_effect=mocked_request_project)
    @mock.patch("axis.ekotrope.utils.request_houseplan", side_effect=mocked_request_houseplan)
    @mock.patch("axis.ekotrope.utils.request_analysis", side_effect=mocked_request_analysis)
    def test_import_company(self, _side_affect, _side_affect_2, _side_affect_3, _side_affect_4):
        """Tests importing in analysis.  Note Analysis is directly linked to the houseplan"""
        with open(os.devnull, "w") as stdout:
            management.call_command(
                "import_ekotrope_project",
                "-c",
                self.user.company.pk,
                "-p",
                "q2R6WDq2",
                stdout=stdout,
                stderr=stdout,
            )
        self.assertEqual(Project.objects.count(), 1)
        self.assertEqual(HousePlan.objects.count(), 1)
        self.assertEqual(Analysis.objects.count(), 1)

    @mock.patch("axis.ekotrope.utils.request_project_list", side_effect=mocked_project_list)
    @mock.patch("axis.ekotrope.utils.request_project", side_effect=mocked_request_project)
    @mock.patch("axis.ekotrope.utils.request_houseplan", side_effect=mocked_request_houseplan)
    @mock.patch("axis.ekotrope.utils.request_analysis", side_effect=mocked_request_analysis)
    def test_import_company_pk(self, _side_affect, _side_affect_2, _side_affect_3, _side_affect_4):
        """Tests importing in analysis.  Note Analysis is directly linked to the houseplan"""
        with open(os.devnull, "w") as stdout:
            management.call_command(
                "import_ekotrope_project",
                "-c",
                self.user.company.pk,
                "-p",
                "q2R6WDq2",
                stdout=stdout,
                stderr=stdout,
            )
        self.assertEqual(Project.objects.count(), 1)
        self.assertEqual(HousePlan.objects.count(), 1)
        self.assertEqual(Analysis.objects.count(), 1)

    @mock.patch("axis.ekotrope.utils.import_project_tree")
    def test_import_project_tree(self, _mocked_import_project_tree):
        """This simply demonstrates how to mock the import project tree"""
        mocked_import_project_tree(self.eko_auth_details, "q2R6WDq2")
        self.assertEqual(Project.objects.count(), 1)
        self.assertEqual(HousePlan.objects.count(), 1)
        self.assertEqual(Analysis.objects.count(), 1)
        self.assertEqual(Simulation.objects.count(), 1)

    @mock.patch("axis.ekotrope.utils.request_project_list", side_effect=mocked_project_list)
    @mock.patch("axis.ekotrope.utils.request_project", side_effect=mocked_request_project)
    @mock.patch("axis.ekotrope.utils.request_houseplan", side_effect=mocked_request_houseplan)
    @mock.patch("axis.ekotrope.utils.request_analysis", side_effect=mocked_request_analysis)
    def test_reimport_company_pk(
        self, _side_affect, _side_affect_2, _side_affect_3, _side_affect_4
    ):
        """Tests importing in analysis.  Note Analysis is directly linked to the houseplan"""

        initial = mocked_import_project_tree(self.eko_auth_details, "q2R6WDq2")
        self.assertEqual(Project.objects.count(), 1)
        self.assertEqual(HousePlan.objects.count(), 1)
        self.assertEqual(Analysis.objects.count(), 1)
        self.assertEqual(Simulation.objects.count(), 1)

        Floorplan.objects.get_or_create(
            owner=self.user.company,
            name="q2R6WDq2",
            ekotrope_houseplan=HousePlan.objects.get(),
            simulation_id=initial.get("simulation"),
        )

        with self.assertRaisesRegex(
            CommandError, expected_regex="Project has already been imported"
        ):
            with open(os.devnull, "w") as stdout:
                management.call_command(
                    "import_ekotrope_project",
                    "-c",
                    self.user.company.pk,
                    "-p",
                    "q2R6WDq2",
                    stdout=stdout,
                    stderr=stdout,
                )

        with open(os.devnull, "w") as stdout:
            management.call_command(
                "import_ekotrope_project",
                "-c",
                self.user.company.pk,
                "-p",
                "q2R6WDq2",
                "--reimport",
                "--no-input",
                stdout=stdout,
                stderr=stdout,
            )

        self.assertEqual(Project.objects.count(), 1)
        self.assertEqual(HousePlan.objects.count(), 1)
        self.assertEqual(Analysis.objects.count(), 1)
        self.assertEqual(Floorplan.objects.get().ekotrope_houseplan, HousePlan.objects.get())
        self.assertNotEqual(Floorplan.objects.get().simulation_id, initial["simulation"])
        self.assertEqual(Simulation.objects.count(), 1)
