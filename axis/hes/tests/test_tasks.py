"""test_tasks.py: Django Task Testing"""


import datetime
import logging
from unittest import mock

from django.apps import apps
from django.test import override_settings
from rest_framework.test import APIClient

from axis.company.models import Company
from axis.core.tests.testcases import AxisTestCase
from axis.filehandling.models import CustomerDocument
from axis.hes.enumerations import NEW, ACTIVE, EAST, COMPLETE, IN_PROGRESS
from axis.hes.models import HESSimulationStatus, HESSimulation
from axis.hes.tasks import (
    create_or_update_hes_score,
    submit_hpxml_inputs,
    generate_label,
    get_results,
)
from axis.hes.tests.mocked_responses import doe_mocked_soap_responses
from axis.home.models import EEPProgramHomeStatus
from axis.remrate_data.models import Simulation
from axis.remrate_data.tests.factories import simulation_factory
from simulation.enumerations import Orientation
from .mixins import HESTestMixin
from axis.hes.tasks.exceptions import TaskFailed

__author__ = "Steven K"
__date__ = "11/21/2019 10:56"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

log = logging.getLogger(__name__)
app = apps.get_app_config("hes")


class HESTaskTest(HESTestMixin, AxisTestCase):
    """This will test out HES Tasks"""

    client_class = APIClient

    def setUp(self):
        super(HESTaskTest, self).setUp()
        self.home_status = EEPProgramHomeStatus.objects.get()
        self.bad_company = Company.objects.get(name="unrelated__rater")
        self.good_rater = self.home_status.company
        self.unrelated_rem_simulation = Simulation.objects.get(company=self.bad_company)
        self.available_rem_simulation = simulation_factory(company=self.good_rater)

        self.user = self.good_rater.users.filter(is_company_admin=True).get()
        self.peci_user = Company.objects.get(slug="peci").users.get(is_company_admin=True)
        self.credential_id = self.peci_user.hes_credentials.pk

        msg = "User %s [pk=%s] is not allowed to login"
        self.assertTrue(
            self.client.login(username=self.user.username, password="password"),
            msg=msg % (self.user.username, self.user.pk),
        )

        self.hes_sim_status, _ = HESSimulationStatus.objects.get_or_create(
            home_status=self.home_status,
            simulation=self.home_status.floorplan.simulation,
        )

    def _create_or_update_hes_score(self, orientation: Orientation = None):
        """Just a user-friendly wrapper for the create_or_update_hes_score task
        since we always pass it the same arguments"""
        create_or_update_hes_score(
            hes_sim_status_id=self.hes_sim_status.pk,
            credential_id=self.credential_id,
            orientation=orientation,
        )

    def test_create_or_update_hes_score_create(self):
        """Test that we don't without something do anything"""

        eep_program = self.home_status.eep_program
        eep_program.slug = "foobar"
        eep_program.save()

        self.assertEqual(HESSimulationStatus.objects.count(), 1)
        simulation = HESSimulationStatus.objects.get()
        self.assertEqual(simulation.company, self.home_status.company)
        self.assertEqual(simulation.home_status, self.home_status)
        self.assertEqual(simulation.home_status.eep_program.slug, "foobar")
        self.assertEqual(simulation.home_status.state, "inspection")
        self.assertEqual(simulation.status, NEW)
        self.assertIsNone(simulation.building_id)
        self.assertFalse(simulation.is_certified)

    @mock.patch("axis.hes.hes.DOEInterface.get", side_effect=doe_mocked_soap_responses)
    @mock.patch("axis.hes.hes.DOEInterface.post", side_effect=doe_mocked_soap_responses)
    def test_create_or_update_hes_score_prior(self, *args):
        """Test that when we update this thing it gets reflected"""

        self._create_or_update_hes_score()
        self.assertEqual(HESSimulationStatus.objects.count(), 1)
        hes_simulation_status = HESSimulationStatus.objects.get()
        self.assertEqual(hes_simulation_status.status, COMPLETE)

        self._create_or_update_hes_score()
        hes_sim_status = HESSimulationStatus.objects.get()
        self.assertEqual(hes_sim_status.simulation, self.sim)
        self.assertEqual(hes_sim_status.status, COMPLETE)

    @mock.patch("axis.hes.hes.DOEInterface.get", side_effect=doe_mocked_soap_responses)
    @mock.patch("axis.hes.hes.DOEInterface.post", side_effect=doe_mocked_soap_responses)
    def test_create_or_update_hes_score_certification_gate(self, *args):
        """Test that when we update this thing it gets reflected"""

        self._create_or_update_hes_score()
        self.assertEqual(HESSimulationStatus.objects.count(), 1)
        simulation = HESSimulationStatus.objects.get()
        self.assertEqual(simulation.status, COMPLETE)

        self.home_status.state = "complete"
        self.home_status.save()
        self._create_or_update_hes_score()

        simulation = HESSimulationStatus.objects.get()
        self.assertTrue(simulation.is_certified)
        self.assertEqual(simulation.status, COMPLETE)

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    @mock.patch("axis.hes.hes.DOEInterface.get", side_effect=doe_mocked_soap_responses)
    @mock.patch("axis.hes.hes.DOEInterface.post", side_effect=doe_mocked_soap_responses)
    def test_full_shot(self, *args):
        """This will test the full enchilada"""
        self._create_or_update_hes_score()
        sim_status = HESSimulationStatus.objects.get()
        self.assertEqual(sim_status.status, COMPLETE)
        self.assertEqual(HESSimulation.objects.count(), 4)
        self.assertEqual(CustomerDocument.objects.count(), 29)
        self.assertEqual(sim_status.home_status.home.customer_documents.count(), 1)
        self.assertEqual(sim_status.building_id, "225875")
        self.assertIsNotNone(sim_status.worst_case_simulation.pk)
        # self.assertEqual(sim_status.worst_case_orientation, EAST)

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    @mock.patch("axis.hes.hes.DOEInterface.get", side_effect=doe_mocked_soap_responses)
    @mock.patch("axis.hes.hes.DOEInterface.post", side_effect=doe_mocked_soap_responses)
    def test_full_shot_final(self, _mock_post, _mock_get):
        """This will test the full enchillada with a final simulation taking care that we store
        the final PDF."""

        self.home_status.state = "complete"
        self.home_status.save()

        self._create_or_update_hes_score()
        sim_status = HESSimulationStatus.objects.get()
        self.assertEqual(sim_status.status, COMPLETE)
        self.assertEqual(HESSimulation.objects.count(), 4)
        self.assertEqual(CustomerDocument.objects.count(), 29)
        self.assertEqual(sim_status.building_id, "225875")
        self.assertIsNotNone(sim_status.worst_case_simulation)
        # self.assertEqual(sim_status.worst_case_orientation, EAST)

        self.assertEqual(sim_status.home_status.home.customer_documents.count(), 1)
        pdf = sim_status.home_status.home.customer_documents.get()
        self.assertIn("hes_label", pdf.document.name)
        self.assertIn(".pdf", pdf.document.name)
        self.assertEqual(pdf.type, "document")
        self.assertGreater(pdf.filesize, 500000)
        self.assertEqual(pdf.description, "")
        self.assertTrue(pdf.is_active)
        self.assertTrue(pdf.is_public)

    @mock.patch("axis.hes.hes.DOEInterface.get", side_effect=doe_mocked_soap_responses)
    @mock.patch("axis.hes.hes.DOEInterface.post", side_effect=doe_mocked_soap_responses)
    def test_submit_hpxml_inputs(self, *args):
        """Test the submit of a building to DOE"""
        orientation = Orientation.NORTH
        self._create_or_update_hes_score(orientation)

        self.assertEqual(HESSimulationStatus.objects.count(), 1)
        self.assertEqual(HESSimulationStatus.objects.get().status, COMPLETE)
        submit_hpxml_inputs(HESSimulationStatus.objects.get().id, self.credential_id, orientation)
        self.assertEqual(HESSimulationStatus.objects.get().status, IN_PROGRESS)

    def test_submit_hpxml_inputs_with_invalid_sim_status_id(self):
        with self.assertRaises(Exception):
            submit_hpxml_inputs(
                hes_sim_status_id=-1,
                credential_id=self.credential_id,
                orientation=Orientation.NORTH,
            )

    def test_sim_status_without_simulation(self):
        """There are a smallish number of old HESSimulationStatus objects still in our database
        that have old REM simulations. For those objects, there is no Simulation.Simulation
        instance, because they were created before that model existed. We need to make sure
        that our handling is correct if someone tries to run a HES Score for such a simulation"""

        self.hes_sim_status.simulation = None
        self.hes_sim_status.save()

        with self.assertRaises(Exception):
            self._create_or_update_hes_score(Orientation.NORTH)

    @mock.patch("axis.hes.hes.DOEInterface.get", side_effect=doe_mocked_soap_responses)
    @mock.patch("axis.hes.hes.DOEInterface.post", side_effect=doe_mocked_soap_responses)
    def test_generate_label(self, _mock_post, _mock_get):
        """Test the submit of a building to DOE"""
        orientation = Orientation.EAST
        self._create_or_update_hes_score(orientation)
        self.assertEqual(HESSimulationStatus.objects.count(), 1)

        submit_hpxml_inputs(HESSimulationStatus.objects.get().id, self.credential_id, orientation)
        generate_label(HESSimulationStatus.objects.get().id, self.credential_id, orientation)
        self.assertEqual(HESSimulationStatus.objects.get().status, COMPLETE)
        self.assertEqual(CustomerDocument.objects.count(), 7)
        self.assertEqual(CustomerDocument.objects.filter(type="document").count(), 1)
        self.assertEqual(CustomerDocument.objects.filter(type="image").count(), 6)

        simulation = HESSimulation.objects.get()
        self.assertEqual(simulation.customer_documents.count(), 7)
        self.assertEqual(simulation.home_status.home.customer_documents.count(), 0)
        self.assertEqual(HESSimulationStatus.objects.get().status, COMPLETE)

        self.assertEqual(simulation.customer_documents.filter(type="image").count(), 6)
        for document in simulation.customer_documents.filter(type="image"):
            self.assertIn("hes_label", document.document.name)
            self.assertIn(".png", document.document.name)
            self.assertEqual(document.type, "image")
            self.assertGreater(document.filesize, 55000)
            self.assertEqual(document.description, "")
            self.assertTrue(document.is_active)
            self.assertTrue(document.is_public)

        # Bad Input
        with self.assertRaises(TaskFailed):
            generate_label(1234567, self.credential_id, orientation)

    @mock.patch("axis.hes.hes.DOEInterface.get", side_effect=doe_mocked_soap_responses)
    @mock.patch("axis.hes.hes.DOEInterface.post", side_effect=doe_mocked_soap_responses)
    def test_get_results(self, _mock_post, _mock_get):
        """Test the submit of a building to DOE"""
        orientation = Orientation.WEST
        self._create_or_update_hes_score(orientation)
        self.assertEqual(HESSimulationStatus.objects.count(), 1)

        submit_hpxml_inputs(HESSimulationStatus.objects.get().id, self.credential_id, orientation)
        generate_label(HESSimulationStatus.objects.get().id, self.credential_id, orientation)

        get_results(HESSimulationStatus.objects.get().id, self.credential_id, orientation)

        hes_simulation = HESSimulation.objects.get()
        hes_sim_status = HESSimulationStatus.objects.get(simulation=self.sim)
        self.assertEqual(hes_simulation.status, ACTIVE)
        self.assertEqual(hes_simulation.home_status_id, hes_sim_status.home_status_id)
        self.assertEqual(self.sim, hes_sim_status.simulation)
        self.assertEqual(hes_simulation.building_id, "225875")
        self.assertEqual(hes_simulation.address, "123 Main Street")
        self.assertEqual(hes_simulation.city, "Golden")
        self.assertEqual(hes_simulation.state, "CO")
        self.assertEqual(hes_simulation.zip_code, "80401")
        self.assertEqual(hes_simulation.conditioned_floor_area, 2400)
        self.assertEqual(hes_simulation.year_built, "1961")
        self.assertEqual(hes_simulation.cooling_present, True)
        self.assertEqual(hes_simulation.base_score, 8)
        self.assertEqual(hes_simulation.package_score, 8)
        self.assertEqual(hes_simulation.cost_savings, 35.0)
        self.assertEqual(hes_simulation.assessment_type, "Official - Initial")
        self.assertEqual(hes_simulation.assessment_date, datetime.date(2014, 12, 2))
        self.assertEqual(hes_simulation.label_number, "225875")
        self.assertEqual(hes_simulation.qualified_assessor_id, "TST-Pivotal")
        self.assertEqual(hes_simulation.hescore_version, "2019.2.0")
        self.assertEqual(hes_simulation.utility_electric, 8302.0)
        self.assertEqual(hes_simulation.utility_natural_gas, 541.0)
        self.assertEqual(hes_simulation.utility_fuel_oil, 0.0)
        self.assertEqual(hes_simulation.utility_lpg, 0.0)
        self.assertEqual(hes_simulation.utility_cord_wood, 0.0)
        self.assertEqual(hes_simulation.utility_pellet_wood, 0.0)
        self.assertEqual(hes_simulation.utility_generated, 0.0)
        self.assertEqual(hes_simulation.source_energy_total_base, 135.0)
        self.assertEqual(hes_simulation.source_energy_asset_base, 63.0)
        self.assertEqual(hes_simulation.average_state_cost, 0.67)
        self.assertEqual(hes_simulation.average_state_eui, 51.8)
        self.assertEqual(hes_simulation.weather_station_location, "Broomfield Jeffco")
        self.assertEqual(hes_simulation.create_label_date, datetime.date(2019, 11, 15))
        self.assertEqual(hes_simulation.source_energy_total_package, 130.0)
        self.assertEqual(hes_simulation.source_energy_asset_package, 57.0)
        self.assertEqual(hes_simulation.base_cost, 1239.0)
        self.assertEqual(hes_simulation.package_cost, 1204.0)
        self.assertEqual(hes_simulation.site_energy_base, 82.0)
        self.assertEqual(hes_simulation.site_energy_package, 77.0)
        self.assertEqual(hes_simulation.site_eui_base, 34.0)
        self.assertEqual(hes_simulation.site_eui_package, 32.0)
        self.assertEqual(hes_simulation.source_eui_base, 56.0)
        self.assertEqual(hes_simulation.source_eui_package, 54.0)
        self.assertEqual(hes_simulation.carbon_base, 17686.0)
        self.assertEqual(hes_simulation.carbon_package, 17090.0)
        self.assertEqual(hes_simulation.utility_electric_base, 8302.0)
        self.assertEqual(hes_simulation.utility_electric_package, 8302.0)
        self.assertEqual(hes_simulation.utility_natural_gas_base, 541.0)
        self.assertEqual(hes_simulation.utility_natural_gas_package, 490.0)
        self.assertEqual(hes_simulation.utility_fuel_oil_base, 0.0)
        self.assertEqual(hes_simulation.utility_fuel_oil_package, 0.0)
        self.assertEqual(hes_simulation.utility_lpg_base, 0.0)
        self.assertEqual(hes_simulation.utility_lpg_package, 0.0)
        self.assertEqual(hes_simulation.utility_cord_wood_base, 0.0)
        self.assertEqual(hes_simulation.utility_cord_wood_package, 0.0)
        self.assertEqual(hes_simulation.utility_pellet_wood_base, 0.0)
        self.assertEqual(hes_simulation.utility_pellet_wood_package, 0.0)
        self.assertEqual(hes_simulation.utility_generated_base, 0.0)
        self.assertEqual(hes_simulation.utility_generated_package, 0.0)
        self.assertIsNotNone(hes_simulation.updated_at)
        self.assertIsNotNone(hes_simulation.created_at)

        with self.assertRaises(TaskFailed):
            get_results(1234567, self.credential_id, orientation)
