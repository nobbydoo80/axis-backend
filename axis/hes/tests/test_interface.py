"""test_interface.py: Django Test HES DOE Interface"""


import datetime
import logging
import os
from unittest import mock

from django.test import TestCase
from lxml import etree

from axis.hes.tests.factories import HESCredentialFactory
from .mocked_responses import doe_mocked_soap_responses
from ..hes import DOEInterface, DOEAuthenticationError, DOEAPIError

__author__ = "Steven K"
__date__ = "11/14/2019 10:34"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

log = logging.getLogger(__name__)

SOURCES = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sources"))


class DOEHESInterfaceTest(TestCase):
    """This will test out the DOE HES Interface"""

    @mock.patch("axis.hes.hes.DOEInterface.post", side_effect=doe_mocked_soap_responses)
    def test_get_session_token(self, _mock_post):
        """Verify we can get a session"""
        doe = DOEInterface(username="bob", password="password")
        doe.get_session_token()
        self.assertEqual(doe.session_token, "3pajidhl5m9n1kh9v8r8n4282d")

    @mock.patch("axis.hes.hes.DOEInterface.post", side_effect=doe_mocked_soap_responses)
    def test_get_session_token_with_hes_credentials(self, _mock_post):
        """Verify we can get a session"""
        creds = HESCredentialFactory()
        doe = DOEInterface(credential_id=creds.pk)
        doe.get_session_token()
        self.assertEqual(doe.session_token, "3pajidhl5m9n1kh9v8r8n4282d")

    @mock.patch("axis.hes.hes.DOEInterface.post", side_effect=doe_mocked_soap_responses)
    def test_get_session_token_fail(self, _mock_post):
        """Verify a bad password fails session"""
        doe = DOEInterface(username="bob", password="password")
        doe.api_key = "BAD_API"
        self.assertRaises(DOEAuthenticationError, doe.get_session_token)

    @mock.patch("axis.hes.hes.DOEInterface.post", side_effect=doe_mocked_soap_responses)
    def test_destroy_session_token(self, _mock_post):
        """Verify we can destroy a session"""
        doe = DOEInterface(username="bob", password="password")
        doe.get_session_token()
        doe.destroy_session_token()
        self.assertEqual(doe.session_token, None)

    @mock.patch("axis.hes.hes.DOEInterface.post", side_effect=doe_mocked_soap_responses)
    def test_destroy_session_token_fail(self, _mock_post):
        """Verify when the session is already destroyed"""
        doe = DOEInterface(username="bob", password="password")
        doe.get_session_token()
        doe.api_key = "BAD_API"
        self.assertRaises(DOEAPIError, doe.destroy_session_token)

    @mock.patch("axis.hes.hes.DOEInterface.post", side_effect=doe_mocked_soap_responses)
    def test_submit_hpxml_inputs_file_path(self, _mock_post):
        """Verify that when we pass it a file path if knows what to do"""
        doe = DOEInterface(username="bob", password="password")
        building_id = doe.submit_hpxml_inputs(hpxml=os.path.join(SOURCES, "hescore_min.hpxml"))
        self.assertEqual(building_id, "225871")

    @mock.patch("axis.hes.hes.DOEInterface.post", side_effect=doe_mocked_soap_responses)
    def test_submit_hpxml_inputs_xml_file_object(self, _mock_post):
        """Verify that when we pass it a file object if knows what to do"""
        doe = DOEInterface(username="bob", password="password")
        with open(os.path.join(SOURCES, "house1.hpxml")) as hpxml:
            building_id = doe.submit_hpxml_inputs(hpxml=hpxml)
        self.assertEqual(building_id, "225871")

    @mock.patch("axis.hes.hes.DOEInterface.post", side_effect=doe_mocked_soap_responses)
    def test_submit_hpxml_inputs_etree_xml(self, _mock_post):
        """Verify that when we pass it a etree.xml if knows what to do"""
        doe = DOEInterface(username="bob", password="password")
        with open(os.path.join(SOURCES, "house1.hpxml")) as hpxml:
            hpxml = etree.fromstring(hpxml.read())
        building_id = doe.submit_hpxml_inputs(hpxml=hpxml)
        self.assertEqual(building_id, "225871")

    @mock.patch("axis.hes.hes.DOEInterface.post", side_effect=doe_mocked_soap_responses)
    def test_submit_hpxml_inputs_xml_string(self, _mock_post):
        """Verify that when we pass it a building id we can deal with that"""
        doe = DOEInterface(username="bob", password="password")
        with open(os.path.join(SOURCES, "house1.hpxml")) as hpxml:
            hpxml = etree.fromstring(hpxml.read())
        building_id = doe.submit_hpxml_inputs(hpxml=etree.tostring(hpxml))
        self.assertEqual(building_id, "225871")

    @mock.patch("axis.hes.hes.DOEInterface.post", side_effect=doe_mocked_soap_responses)
    def test_submit_hpxml_inputs_fail(self, _mock_post):
        doe = DOEInterface(username="bob", password="password")
        doe.get_session_token()
        doe.api_key = "BAD_API"
        self.assertRaises(DOEAPIError, doe.destroy_session_token)

    @mock.patch("axis.hes.hes.DOEInterface.get", side_effect=doe_mocked_soap_responses)
    def test_retrieve_file(self, _mock_get):
        doe = DOEInterface(username="bob", password="password")
        data = doe.retrieve_file("https://media.giphy.com/media/KmBd3r88LGrqE/giphy.gif")
        self.assertEqual(data["name"], "hes_label_giphy.gif")
        self.assertIsNone(data["page"])
        self.assertIsNotNone(data["document"])

    @mock.patch("axis.hes.hes.DOEInterface.get", side_effect=doe_mocked_soap_responses)
    @mock.patch("axis.hes.hes.DOEInterface.post", side_effect=doe_mocked_soap_responses)
    def test_generate_label(self, _mock_post, _mock_get):
        doe = DOEInterface(username="bob", password="password")
        data = doe.generate_label(building_id=225871)
        self.assertEqual(data["result"], "OK")
        self.assertEqual(data["message"], "Label for building #225875 successfully generated")
        self.assertEqual(len(data["files"]), 7)

        file_data = data["files"][0]
        name = "hes_label_5dcdc939cef998.89098513_225875_ef3cb1ec9b1cf583979d2cd277dec3ed.pdf"
        self.assertEqual(file_data["type"], "pdf")
        self.assertIsNone(file_data["page"])
        self.assertEqual(file_data["name"], name)
        self.assertIsNotNone(file_data["url"])
        self.assertIsNotNone(file_data["document"])

        file_data = data["files"][-1]
        name = "hes_label_5dcdc939cef998.89098513_225875_ef3cb1ec9b1cf583979d2cd277dec3ed.png"
        self.assertEqual(file_data["type"], "png")
        self.assertEqual(file_data["page"], 6)
        self.assertEqual(file_data["name"], name)
        self.assertIsNotNone(file_data["url"])
        self.assertIsNotNone(file_data["document"])

    @mock.patch("axis.hes.hes.DOEInterface.post", side_effect=doe_mocked_soap_responses)
    def test_generate_label_fail(self, _mock_post):
        doe = DOEInterface(username="bob", password="password")
        doe.get_session_token()
        doe.api_key = "BAD_API"
        self.assertRaises(DOEAPIError, doe.generate_label, building_id=225871)

    @mock.patch("axis.hes.hes.DOEInterface.post", side_effect=doe_mocked_soap_responses)
    def test_retrieve_label_results(self, _mock_post):
        doe = DOEInterface(username="bob", password="password")
        data = doe.retrieve_label_results(building_id=225883)
        self.assertEqual(data["address"], "123 Main Street")
        self.assertEqual(data["city"], "Golden")
        self.assertEqual(data["state"], "CO")
        self.assertEqual(data["zip_code"], "80401")
        self.assertEqual(data["conditioned_floor_area"], 2400)
        self.assertEqual(data["year_built"], 1961)
        self.assertEqual(data["cooling_present"], True)
        self.assertEqual(data["base_score"], 8)
        self.assertEqual(data["package_score"], 8)
        self.assertEqual(data["cost_savings"], 35)
        self.assertEqual(data["assessment_type"], "Official - Initial")
        self.assertEqual(data["assessment_date"], datetime.date(2014, 12, 2))
        self.assertEqual(data["label_number"], 225883)
        self.assertEqual(data["qualified_assessor_id"], "TST-Pivotal")
        self.assertEqual(data["hescore_version"], "2019.2.0")
        self.assertEqual(data["utility_electric"], 8302)
        self.assertEqual(data["utility_natural_gas"], 541)
        self.assertEqual(data["utility_fuel_oil"], 0)
        self.assertEqual(data["utility_lpg"], 0)
        self.assertEqual(data["utility_cord_wood"], 0)
        self.assertEqual(data["utility_pellet_wood"], 0)
        self.assertEqual(data["utility_generated"], 0)
        self.assertEqual(data["source_energy_total_base"], 135)
        self.assertEqual(data["source_energy_asset_base"], 63)
        self.assertEqual(data["average_state_cost"], 0.67)
        self.assertEqual(data["average_state_eui"], 51.8)

    @mock.patch("axis.hes.hes.DOEInterface.post", side_effect=doe_mocked_soap_responses)
    def test_retrieve_label_results_fail(self, _mock_post):
        doe = DOEInterface(username="bob", password="password")
        doe.get_session_token()
        doe.api_key = "BAD_API"
        self.assertRaises(DOEAPIError, doe.retrieve_label_results, building_id=225871)

    @mock.patch("axis.hes.hes.DOEInterface.post", side_effect=doe_mocked_soap_responses)
    def test_retrieve_extended_results(self, _mock_patch):
        doe = DOEInterface(username="bob", password="password")
        data = doe.retrieve_extended_results(building_id=225875)
        self.assertEqual(data["label_number"], 225875)
        self.assertEqual(data["building_id"], 225875)
        self.assertEqual(data["weather_station_location"], "Broomfield Jeffco")
        self.assertEqual(data["create_label_date"], datetime.date(2019, 11, 15))
        self.assertEqual(data["cooling_present"], True)
        self.assertEqual(data["source_energy_total_base"], 135)
        self.assertEqual(data["source_energy_total_package"], 130)
        self.assertEqual(data["source_energy_asset_base"], 63)
        self.assertEqual(data["source_energy_asset_package"], 57)
        self.assertEqual(data["base_cost"], 1239)
        self.assertEqual(data["package_cost"], 1204)
        self.assertEqual(data["source_eui_base"], 56)
        self.assertEqual(data["source_eui_package"], 54)
        self.assertEqual(data["base_score"], 8)
        self.assertEqual(data["package_score"], 8)
        self.assertEqual(data["site_energy_base"], 82)
        self.assertEqual(data["site_energy_package"], 77)
        self.assertEqual(data["site_eui_base"], 34)
        self.assertEqual(data["site_eui_package"], 32)
        self.assertEqual(data["carbon_base"], 17686)
        self.assertEqual(data["carbon_package"], 17090)
        self.assertEqual(data["utility_electric_base"], 8302)
        self.assertEqual(data["utility_natural_gas_base"], 541)
        self.assertEqual(data["utility_fuel_oil_base"], 0)
        self.assertEqual(data["utility_lpg_base"], 0)
        self.assertEqual(data["utility_cord_wood_base"], 0)
        self.assertEqual(data["utility_pellet_wood_base"], 0)
        self.assertEqual(data["utility_generated_base"], 0)
        self.assertEqual(data["utility_electric_package"], 8302)
        self.assertEqual(data["utility_natural_gas_package"], 490)
        self.assertEqual(data["utility_fuel_oil_package"], 0)
        self.assertEqual(data["utility_lpg_package"], 0)
        self.assertEqual(data["utility_cord_wood_package"], 0)
        self.assertEqual(data["utility_pellet_wood_package"], 0)
        self.assertEqual(data["utility_generated_package"], 0)

    @mock.patch("axis.hes.hes.DOEInterface.post", side_effect=doe_mocked_soap_responses)
    def test_retrieve_extended_results_fail(self, _mock_post):
        doe = DOEInterface(username="bob", password="password")
        doe.get_session_token()
        doe.api_key = "BAD_API"
        self.assertRaises(DOEAPIError, doe.retrieve_extended_results, building_id=225875)
