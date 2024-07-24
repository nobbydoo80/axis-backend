"""test_api.py: Django """
import json
import logging
from unittest import mock

from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse

from axis.core.tests.client import AxisClient
from axis.core.tests.testcases import AxisTestCase
from axis.ekotrope.models import Project
from axis.ekotrope.tests.factories import (
    house_plan_factory,
    ekotrope_auth_details_factory,
    project_factory,
)
from .factories import add_dummy_blg_data_file
from .mixins import FloorplanTestMixin
from ..models import Floorplan

__author__ = "Steven Klass"
__date__ = "11/16/18 1:38 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class SimulationEngineMock:
    def __init__(self, *args, **kwargs):
        self.success = False
        self.project = None
        self.project_id = None

    def check_project_name(self, project_name):
        return None

    def simulate(self, *args, **kwargs):
        self.success = True
        self.project = Project.objects.first()
        self.project_id = self.project.id
        return {"foo": "bar"}

    def import_project(self):
        return Project.objects.first()


class FloorplanViewSetTests(FloorplanTestMixin, AxisTestCase):
    client_class = AxisClient

    def test_rem_data_fields(self):
        user = self.get_admin_user(company_type="rater")
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        floorplan = Floorplan.objects.filter(
            remrate_target__isnull=False, remrate_target__airconditioner__isnull=False
        ).first()
        hvacs = floorplan.remrate_target.airconditioner_set.all()
        try:
            vents = [floorplan.remrate_target.infiltration.get_ventilation_system()]
        except ObjectDoesNotExist:
            vents = []

        unique_name = Floorplan.objects.find_unique_floorplan_name(
            name=floorplan.remrate_target.building_name, company=user.company
        )

        url = reverse("apiv2:floorplan-rem-data-fields")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {})

        response = self.client.get(url, {"id": floorplan.remrate_target.pk})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {
                "hvac_systems": hvacs.count(),
                "ventilation_systems": len(vents),
                "name": unique_name,
                "number": floorplan.remrate_target.id,
                "square_footage": floorplan.remrate_target.buildinginfo.conditioned_area,
            },
        )

    @mock.patch("axis.ekotrope.utils.import_project_tree")
    def test_ekotrope_fields(self, import_project_tree):
        user = self.get_admin_user(company_type="rater")
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        floorplan = Floorplan.objects.first()
        project = project_factory(company=user.company)
        ekotrope_auth_details_factory(user=user)
        # mock post_save import_project_tree to skip connecting to API
        import_project_tree.return_value = project
        house_plan = house_plan_factory(project=project)

        floorplan.remrate_target = None

        floorplan.ekotrope_houseplan = house_plan
        floorplan.save()

        unique_name = Floorplan.objects.find_unique_floorplan_name(
            name=project.data["community"], company=user.company
        )

        url = reverse("apiv2:floorplan-ekotrope-fields")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {})

        url = reverse("apiv2:floorplan-ekotrope-fields")
        response = self.client.get(url, {"id": floorplan.ekotrope_houseplan.id})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {
                "name": unique_name,
                "number": house_plan.id,
                "square_footage": house_plan.data["thermalEnvelope"]["summary"]["conditionedArea"],
            },
        )


class FloorplanRemrateViewSetTests(FloorplanTestMixin, AxisTestCase):
    client_class = AxisClient

    def test_diff(self):
        user = self.get_admin_user(company_type="rater")
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )
        floorplan = Floorplan.objects.filter(remrate_target__isnull=False).first()
        add_dummy_blg_data_file(floorplan, version=None, use_real_data=True)

        url = reverse("apiv2:floorplan_remrate-diff", kwargs={"pk": floorplan.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(response.json().keys()), {"errors", "warnings", "ignored", "summary"})
