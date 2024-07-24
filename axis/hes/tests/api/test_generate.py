import datetime
import logging
from unittest import mock

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from simulation.enumerations import Orientation

from axis.company.models import Company
from axis.core.tests.testcases import AxisTestCase
from axis.hes.enumerations import COMPLETE
from axis.hes.models import HESSimulationStatus, HESSimulation
from axis.hes.tests.mocked_responses import doe_mocked_soap_responses, validation_mock
from axis.home.models import EEPProgramHomeStatus
from axis.remrate_data.tests.factories import (
    simulation_factory as rem_simulation_factory,
)
from axis.floorplan.tests.factories import floorplan_with_simulation_factory
from axis.home.tests.factories import (
    home_factory,
    eep_program_custom_home_status_factory,
)
from ..mixins import HESTestMixin

__author__ = "Steven K"
__date__ = "11/22/2019 12:27"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

from ....gbr.tests.mocked_responses import gbr_mocked_response

log = logging.getLogger(__name__)


class HESAPITest(HESTestMixin, AxisTestCase):
    """Tests of the generate method of the Home Energy Score API"""

    client_class = APIClient

    def setUp(self):
        super(HESAPITest, self).setUp()
        self.base_url = reverse("apiv2:hes-generate")
        self.home_status = EEPProgramHomeStatus.objects.get()
        self.bad_company = Company.objects.get(name="unrelated__rater")
        self.good_rater = self.home_status.company
        self.available_rem_simulation = rem_simulation_factory(company=self.good_rater)
        self.user = self.good_rater.users.filter(is_company_admin=True).get()
        self.credential_id = self.user.hes_credentials.pk
        msg = "User %s [pk=%s] is not allowed to login"
        self.assertTrue(
            self.client.login(username=self.user.username, password="password"),
            msg=msg % (self.user.username, self.user.pk),
        )

    def generate_eep_program_home_status(self) -> EEPProgramHomeStatus:
        floorplan = floorplan_with_simulation_factory(**self.floorplan_factory_kwargs)

        assert str(floorplan.simulation.location.climate_zone) == "4C"
        assert str(floorplan.simulation.climate_zone) == "4C"
        home = home_factory(
            subdivision=floorplan.subdivision_set.first(), city=self.city, zipcode=97229
        )
        return eep_program_custom_home_status_factory(
            home=home,
            floorplan=floorplan,
            eep_program=self.eep_program,
            company=self.rater_company,
        )

    @mock.patch("axis.hes.hes.DOEInterface.get", side_effect=doe_mocked_soap_responses)
    @mock.patch("axis.hes.hes.DOEInterface.post", side_effect=doe_mocked_soap_responses)
    @mock.patch("simulation.serializers.hpxml.NrelHpxmlValidator", side_effect=validation_mock)
    def test_generate_hpxml_existing(self, *args):
        """Test that we can generate using an existing hpxml"""
        HESSimulationStatus.objects.all().delete()

        data = {"home_status_id": self.home_status.pk}
        response = self.client.post(self.base_url, data)
        self.assertEqual(status.HTTP_201_CREATED, response.status_code, response.json())
        self.assertIn("pk", response.json())
        simulation_status = HESSimulationStatus.objects.get(pk=response.json().get("pk"))
        self.assertIn("state", response.json())
        self.assertEqual(simulation_status.status, COMPLETE)
        self.assertIn("status", response.json())
        self.assertIn("Running", response.json().get("status"))
        self.assertEqual(simulation_status.simulation, self.sim)

    @mock.patch("axis.hes.hes.DOEInterface.get", side_effect=doe_mocked_soap_responses)
    @mock.patch("axis.hes.hes.DOEInterface.post", side_effect=doe_mocked_soap_responses)
    @mock.patch("simulation.serializers.hpxml.NrelHpxmlValidator", side_effect=validation_mock)
    def test_generate_home_status_only(self, *args):
        """Test that we can generate full set from a simulation"""
        data = {"home_status_id": self.home_status.pk}
        response = self.client.post(self.base_url, data)
        self.assertEqual(status.HTTP_201_CREATED, response.status_code, response.json())

        response = response.json()
        self.assertIn("pk", response)

        self.assertIn("state", response)
        self.assertEqual(COMPLETE, response.get("state"))
        self.assertIn("status", response)
        self.assertIn("Running", response.get("status"))

        simulation_status = HESSimulationStatus.objects.get(pk=response.get("pk"))
        self.assertEqual(simulation_status.company, self.home_status.company)
        self.assertEqual(
            simulation_status.rem_simulation, self.home_status.floorplan.remrate_target
        )
        self.assertEqual(simulation_status.home_status, self.home_status)

    @mock.patch("axis.hes.hes.DOEInterface.get", side_effect=doe_mocked_soap_responses)
    @mock.patch("axis.hes.hes.DOEInterface.post", side_effect=doe_mocked_soap_responses)
    @mock.patch("simulation.serializers.hpxml.NrelHpxmlValidator", side_effect=validation_mock)
    def test_generate_optionals(self, *args):
        """Test that we can push through some optionals"""
        orientation = Orientation.SOUTH
        external_id = "SOMETHING"
        data = {
            "home_status_id": self.home_status.pk,
            "orientation": orientation,
            "external_id": external_id,
        }
        response = self.client.post(self.base_url, data)
        response_json = response.json()
        self.assertEqual(status.HTTP_201_CREATED, response.status_code, response_json)
        self.assertIn("pk", response_json)
        simulation_status = HESSimulationStatus.objects.get(pk=response_json["pk"])
        hes_simulations = simulation_status.hes_simulations.all()
        self.assertEqual(
            1,
            len(hes_simulations),
            "We expect only one HES simulation to exist on the HESSimulationStatus because we passed an "
            "orientation, so only that orientation should have been simulated.",
        )
        self.assertEqual(
            orientation,
            hes_simulations[0].orientation,
            "We expect the simulation created to have the orientation that we passed to the API.",
        )

    @mock.patch("axis.hes.hes.DOEInterface.get", side_effect=doe_mocked_soap_responses)
    @mock.patch("axis.hes.hes.DOEInterface.post", side_effect=doe_mocked_soap_responses)
    @mock.patch("simulation.serializers.hpxml.NrelHpxmlValidator", side_effect=validation_mock)
    def test_generate_update(self, *args):
        """Test that we can push through some optionals"""

        HESSimulationStatus.objects.all().delete()

        data = {"home_status_id": self.home_status.pk}
        response = self.client.post(self.base_url, data)
        self.assertEqual(status.HTTP_201_CREATED, response.status_code, response.json())

        response = self.client.post(self.base_url, data)
        self.assertEqual(status.HTTP_200_OK, response.status_code, response.json())

        self.assertEqual(HESSimulationStatus.objects.count(), 1)

    @mock.patch("axis.hes.hes.DOEInterface.get", side_effect=doe_mocked_soap_responses)
    @mock.patch("axis.hes.hes.DOEInterface.post", side_effect=doe_mocked_soap_responses)
    @mock.patch("simulation.serializers.hpxml.NrelHpxmlValidator", side_effect=validation_mock)
    def test_full_motion_without_orientation(self, _mock_post, _mock_get, _mock_val):
        """Allow this to through and process everything."""
        data = {"home_status_id": self.home_status.pk}
        self.home_status.annotations.all().delete()
        response = self.client.post(self.base_url, data)
        self.assertEqual(status.HTTP_201_CREATED, response.status_code, response.json())

        response = self.client.post(self.base_url, data)
        self.assertEqual(status.HTTP_200_OK, response.status_code, response.json())
        self.assertEqual(HESSimulationStatus.objects.count(), 1)
        self.assertEqual(HESSimulation.objects.count(), 4)

        simulation_status = HESSimulationStatus.objects.get()
        for orientation in Orientation.cardinal_directions():
            self.assertIsNotNone(simulation_status.get_hes_simulation(orientation))
        self.assertIsNotNone(simulation_status.worst_case_simulation)
        self.assertIsNotNone(simulation_status.worst_case_orientation)

    @mock.patch("axis.hes.hes.DOEInterface.get", side_effect=doe_mocked_soap_responses)
    @mock.patch("axis.hes.hes.DOEInterface.post", side_effect=doe_mocked_soap_responses)
    @mock.patch("simulation.serializers.hpxml.NrelHpxmlValidator", side_effect=validation_mock)
    def test_full_motion_with_orientation(self, _mock_post, _mock_get, _mock_valid):
        """Allow this to through and process everything."""
        orientation = Orientation.SOUTHEAST
        data = {
            "home_status_id": self.home_status.pk,
            "simulation_id": self.home_status.floorplan.simulation.pk,
            "orientation": orientation,
        }

        # Post the first time to create a simulation status object
        response = self.client.post(self.base_url, data)
        self.assertEqual(status.HTTP_201_CREATED, response.status_code, response.json())

        # Post a second time with the same data and confirm that we get "200 OK" instead of "201 CREATED", because
        # now the object should be found to already exist instead of being re-created
        response = self.client.post(self.base_url, data)
        self.assertEqual(status.HTTP_200_OK, response.status_code, response.json())

        self.assertEqual(HESSimulationStatus.objects.count(), 1)
        self.assertEqual(HESSimulation.objects.count(), 1)

        simulation_status = HESSimulationStatus.objects.get()
        for _o in Orientation:
            value = simulation_status.get_hes_simulation(_o)
            if _o == orientation:
                self.assertIsNotNone(value)
            else:
                self.assertIsNone(value)
        self.assertIsNotNone(simulation_status.worst_case_simulation)
        self.assertIsNotNone(simulation_status.worst_case_orientation)

    @mock.patch("axis.hes.hes.DOEInterface.get", side_effect=doe_mocked_soap_responses)
    @mock.patch("axis.hes.hes.DOEInterface.post", side_effect=doe_mocked_soap_responses)
    @mock.patch(
        "axis.gbr.gbr.GreenBuildingRegistryAPIConnect.post", side_effect=gbr_mocked_response
    )
    def test_home_certification(self, _mock_gbr, _mock_post, _mock_get):
        """This will test that on certification everything advances and we get a final cert."""

        data = {
            "home_status_id": self.home_status.pk,
            "simulation_id": self.home_status.floorplan.simulation.pk,
            "orientation": Orientation.SOUTH,
        }

        # Post the first time to create a simulation status object
        response = self.client.post(self.base_url, data)
        self.assertEqual(status.HTTP_201_CREATED, response.status_code, response.json())

        sim_status = HESSimulationStatus.objects.get()
        self.assertEqual(sim_status.status, COMPLETE)
        self.assertEqual(sim_status.home_status.home.customer_documents.count(), 1)
        pre_cert = sim_status.home_status.home.customer_documents.get()

        # Get this thing to 100%
        self.home_status.cont = 100
        self.home_status.pct_complete = 100
        self.home_status.save()

        try:
            self.assertTrue(self.home_status.is_eligible_for_certification())
        except AssertionError:
            import pprint

            for k, v in self.home_status.get_progress_analysis()["requirements"].items():
                if v["status"] is False:
                    print(k)
                    pprint.pprint(v)
            raise

        from axis.home.tasks import certify_single_home

        peci_user = Company.objects.get(slug="peci").users.get(is_company_admin=True)
        certify_single_home(
            peci_user, self.home_status, datetime.datetime.today(), throw_errors=True
        )

        response = self.client.post(self.base_url, data)
        self.assertEqual(status.HTTP_200_OK, response.status_code, response.json())

        sim_status = HESSimulationStatus.objects.get()
        self.assertEqual(
            sim_status.home_status.home.customer_documents.count(), 2
        )  # EPS Report / HES
        post = sim_status.home_status.home.customer_documents.get(document__icontains="hes_label")

        self.assertNotEqual(pre_cert.pk, post.pk)
        self.assertTrue(sim_status.is_certified)

        self.assertEqual(HESSimulationStatus.objects.count(), 1)
        self.assertEqual(HESSimulation.objects.count(), 1)
