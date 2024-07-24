import json
from unittest import mock

from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models.signals import post_save
from django.core.exceptions import ValidationError

from axis.core.tests.client import AxisClient
from axis.core.tests.factories import rater_admin_factory
from axis.core.tests.testcases import AxisTestCase
from axis.ekotrope.tests.factories import (
    house_plan_factory,
    ekotrope_auth_details_factory,
    project_factory,
    analysis_factory,
)
from axis.ekotrope.tests.mock_responses import (
    mocked_request_project,
    mocked_request_houseplan,
    mocked_request_analysis,
)
from axis.floorplan.models import Floorplan

__author__ = "Artem Hruzd"
__date__ = "5/31/19 11:00 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
]

from axis.floorplan.tests.api_v3.viewsets.test_simulation import SimulationViewSetTests

from axis.remrate_data.models import Simulation as RemSimulation
from axis.floorplan.tests.mixins import FloorplanTestMixin
from simulation.models import Simulation


class FloorplanTest(FloorplanTestMixin, AxisTestCase):
    client_class = AxisClient

    def test_floorplan_save(self):
        with mock.patch(
            "axis.ekotrope.signals.fetch_full_object", autospec=True
        ) as mocked_fetch_full_object:
            post_save.connect(
                mocked_fetch_full_object, sender=Floorplan, dispatch_uid="test_fetch_full_object"
            )

        floorplan = Floorplan.objects.filter(remrate_target__isnull=False).first()
        floorplan.name = None
        floorplan.simulation = None
        floorplan.number = None
        floorplan.square_footage = None
        floorplan.save()

        self.assertTrue(mocked_fetch_full_object.called)
        self.assertEqual(mocked_fetch_full_object.call_count, 1)

    @mock.patch("axis.ekotrope.utils.import_project_tree")
    def test_floorplan_input_data_type(self, import_project_tree):
        floorplan = Floorplan.objects.filter(remrate_target__isnull=False).first()
        self.assertEqual(floorplan.input_data_type, "remrate")

        # prepare data for handling signals when we have ekotrope
        user = self.get_admin_user(company_type="rater")
        project = project_factory(company=user.company)
        ekotrope_auth_details_factory(user=user)
        # mock post_save import_project_tree to skip connecting to API
        import_project_tree.return_value = project
        house_plan = house_plan_factory(project=project)

        floorplan.remrate_target = None

        floorplan.ekotrope_houseplan = house_plan
        floorplan.save()
        self.assertEqual(floorplan.input_data_type, "ekotrope")

        floorplan.remrate_target = None
        floorplan.ekotrope_houseplan = None
        remrate_data_file = SimpleUploadedFile(name="file.txt", content=b"file content")
        floorplan.remrate_data_file = remrate_data_file
        floorplan.save()

        self.assertEqual(floorplan.input_data_type, "blg_data")

        floorplan.ekotrope_houseplan = None
        floorplan.remrate_target = None
        floorplan.remrate_data_file = None
        floorplan.save()

        self.assertIsNone(floorplan.input_data_type)

    def test_floorplan_printable_representation(self):
        floorplan = Floorplan.objects.first()

        self.assertEqual("{}".format(floorplan), floorplan.name)
        floorplan.type = "preliminary"
        floorplan.save()
        self.assertEqual(
            "{}".format(floorplan),
            "{name} ({type})".format(name=floorplan.name, type=floorplan.get_type_display()),
        )

    def test_floorplan_absolute_url(self):
        user = self.get_admin_user(company_type="rater")
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )
        floorplan = Floorplan.objects.first()
        url = floorplan.get_absolute_url()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_is_restricted(self):
        from axis.incentive_payment.tests.factories import basic_incentive_payment_status_factory

        floorplan = Floorplan.objects.first()
        self.assertEqual(floorplan.is_restricted, 0)

        incentive_payment = basic_incentive_payment_status_factory(home_status__floorplan=floorplan)
        self.assertEqual(floorplan.is_restricted, 0)

        incentive_payment.state = "ipp_payment_failed_requirements"
        incentive_payment.save()
        self.assertEqual(floorplan.is_restricted, 0)

        incentive_payment.state = "complete"
        incentive_payment.save()
        self.assertEqual(floorplan.is_restricted, 1)

    @mock.patch("axis.ekotrope.utils.import_project_tree")
    def test_simulation_passes_energy_star_v3(self, import_project_tree):
        floorplan = Floorplan.objects.filter(remrate_target__isnull=False).first()
        self.assertEqual(
            floorplan.simulation_passes_energy_star_v3,
            floorplan.remrate_target.energystar.passes_energy_star_v3,
        )

        # prepare data for handling signals when we have ekotrope
        user = self.get_admin_user(company_type="rater")
        project = project_factory(company=user.company)
        ekotrope_auth_details_factory(user=user)
        # mock post_save import_project_tree to skip connecting to API
        import_project_tree.return_value = project
        house_plan = house_plan_factory(project=project)
        analysis_factory(houseplan=house_plan)

        floorplan.remrate_target = None

        floorplan.ekotrope_houseplan = house_plan
        floorplan.save()

        self.assertTrue(floorplan.simulation_passes_energy_star_v3)

    @mock.patch("axis.ekotrope.utils.request_project", side_effect=mocked_request_project)
    @mock.patch("axis.ekotrope.utils.request_houseplan", side_effect=mocked_request_houseplan)
    @mock.patch("axis.ekotrope.utils.request_analysis", side_effect=mocked_request_analysis)
    def test_simulation_object_create_from_ekotrope(
        self, _mock_request_analysis, _mock_request_houseplan, _mock_request_project
    ):
        """Verify that we can walk through this flow"""
        user = self.get_admin_user(company_type="rater")
        ekotrope_auth_details_factory(user=user)

        # This will create a full project with data and a stubbed house_plan (no .data)
        houseplan_stub = house_plan_factory(stub_only=True, company=user.company)
        self.assertIsNotNone(houseplan_stub.project)
        self.assertNotEqual(houseplan_stub.project.data, {})  # You need a full project
        self.assertEqual(houseplan_stub.data, {})

        # The process of binding the stub to the floorplan will fully bring in the house_plan data
        # It will also add the simulation to this model.
        self.assertFalse(_mock_request_project.called)
        self.assertFalse(_mock_request_houseplan.called)
        self.assertFalse(_mock_request_analysis.called)
        fp = Floorplan.objects.create(owner=user.company, ekotrope_houseplan=houseplan_stub)
        self.assertTrue(_mock_request_project.called)
        self.assertTrue(_mock_request_houseplan.called)
        self.assertTrue(_mock_request_analysis.called)
        self.assertEqual(_mock_request_project.call_count, 1)
        self.assertEqual(_mock_request_houseplan.call_count, 1)
        self.assertEqual(_mock_request_analysis.call_count, 32)
        floorplan = Floorplan.objects.get(id=fp.id)

        self.assertIsNotNone(floorplan.simulation)
        self.assertTrue(floorplan.simulation.analyses.count())
        self.assertTrue(floorplan.simulation.mechanical_equipment.count())
        self.assertTrue(floorplan.simulation.above_grade_walls.count())

    def test_unique_constraint(self):
        """Unique constraint"""
        user = self.get_admin_user(company_type="rater")
        Floorplan.objects.create(
            owner=user.company, name="test floorplan", number=1, square_footage=1200
        )
        self.assertRaises(
            ValidationError,
            Floorplan.objects.create,
            owner=user.company,
            name="test floorplan",
            number=1,
            square_footage=1200,
        )
        rater_admin = rater_admin_factory()
        Floorplan.objects.create(
            owner=rater_admin.company, name="test floorplan", number=1, square_footage=1200
        )

    def test_get_normalized_input_data(self):
        Floorplan.objects.all().delete()
        Simulation.objects.all().delete()
        RemSimulation.objects.all().delete()

        floorplan = SimulationViewSetTests.floorplan_factory()
        floorplan.simulation = None
        floorplan.remrate_target = None
        floorplan.save()

        f = Floorplan.objects.get(id=floorplan.id)
        self.assertEqual(f.input_data_type, Floorplan.INPUT_DATA_TYPE_BLG_DATA)
        data = floorplan.get_normalized_blg_input_data()
        self.assertEqual(data["source_type"], "blg_data")
