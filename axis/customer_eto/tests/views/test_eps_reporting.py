"""test_eps_reporting.py - Axis"""

__author__ = "Steven K"
__date__ = "11/4/21 11:09"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from django.contrib.auth.models import Permission
from django.urls import reverse

from axis.annotation.tests.test_mixins import AnnotationMixin
from axis.checklist.collection.test_mixins import CollectionRequestMixin
from axis.core.tests.client import AxisClient
from axis.core.tests.testcases import AxisTestCase
from axis.customer_eto.enumerations import (
    PrimaryHeatingEquipment2020,
    SmartThermostatBrands2020,
    Fireplace2020,
    GridHarmonization2020,
    AdditionalIncentives2020,
    SolarElements2020,
)
from axis.customer_eto.tests.program_checks.test_eto_2021 import ETO2021ProgramTestMixin
from axis.home.tests.factories import home_factory, eep_program_custom_home_status_factory
from axis.relationship.utils import create_or_update_spanning_relationships

log = logging.getLogger(__name__)


class EPSReportViewTests(ETO2021ProgramTestMixin, AxisTestCase):
    client_class = AxisClient

    @classmethod
    def setUpClass(cls):
        super(EPSReportViewTests, cls).setUpClass()

        collection_request = CollectionRequestMixin()
        answers = {
            "primary-heating-equipment-type": PrimaryHeatingEquipment2020.ELECTRIC_RESISTANCE,
            "smart-thermostat-brand": SmartThermostatBrands2020.BRYANT,
            "has-gas-fireplace": Fireplace2020.FE_60_69,
            "grid-harmonization-elements": GridHarmonization2020.ALL,
            "eto-additional-incentives": AdditionalIncentives2020.ENERGY_SMART,
            "solar-elements": SolarElements2020.SOLAR_PV,
            "ets-annual-etsa-kwh": 2000,
            "is-adu": "No",
            "builder-payment-redirected": "No",
            "has-battery-storage": "No",
            "ceiling-r-value": 32,
            "equipment-heating-other-type": PrimaryHeatingEquipment2020.ELECTRIC_RESISTANCE,
            "equipment-heating-other-brand": "Lame Brand",
            "equipment-heating-other-model-number": "XYZ",
            "equipment-water-heater": {"brand": "Brand", "model": "Model"},
            "equipment-dishwasher": {"brand": "Brand", "model": "Model"},
        }
        collection_request.add_bulk_answers(answers, home_status=cls.home_status)
        annotation = AnnotationMixin()
        annotation.add_annotation(
            content="foo", type_slug="hpxml_gbr_id", content_object=cls.home_status
        )
        missing_checks = cls.home_status.report_eligibility_for_certification()
        assert not len(missing_checks), missing_checks

        home = home_factory(
            subdivision=cls.home_status.floorplan.subdivision_set.first(),
            city=cls.city,
            zipcode=97229,
        )
        cls.home_status_2 = eep_program_custom_home_status_factory(
            home=home,
            floorplan=cls.home_status.floorplan,
            eep_program=cls.eep_program,
            company=cls.rater_company,
        )
        collection_request.add_bulk_answers(answers, home_status=cls.home_status_2)
        rel_ele = create_or_update_spanning_relationships(cls.pac_pwr, cls.home_status_2.home)[0][0]
        rel_gas = create_or_update_spanning_relationships(cls.nw_nat, cls.home_status_2.home)[0][0]
        create_or_update_spanning_relationships(cls.qa, cls.home_status_2.home)
        create_or_update_spanning_relationships(cls.peci, cls.home_status_2.home)

        home._generate_utility_type_hints(rel_gas, rel_ele)

        cls.user = cls.provider_user
        cls.url = reverse("eto:download", kwargs={"home_status": cls.home_status.id})
        cls.bulk_url = reverse("eto:download")

    def test_login_required(self):
        with self.subTest("Single Auth Required"):
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, 302)
            self.assertIn(self.url, response["Location"], msg=self.url)
            self.assertIn(reverse("auth:login"), response["Location"])
        with self.subTest("Bulk Auth Required"):
            response = self.client.get(self.bulk_url)
            self.assertEqual(response.status_code, 302)
            self.assertIn(self.bulk_url, response["Location"], msg=self.bulk_url)
            self.assertIn(reverse("auth:login"), response["Location"])

    def test_permissions(self):
        self.client.force_login(self.user)
        self.assertTrue(self.user.has_perm("home.view_home"))

        with self.subTest("Single Permissions"):
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, 200, response.content)

        with self.subTest("Bulk Permissions"):
            response = self.client.get(self.bulk_url)
            self.assertEqual(response.status_code, 200, response.content)

        view_home_perm = Permission.objects.get(codename="view_home")
        self.user.user_permissions.remove(view_home_perm)
        self.user.groups.clear()

        with self.subTest("Single No Permissions"):
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, 403, response.content)

        with self.subTest("Bulk No Permissions"):
            response = self.client.get(self.bulk_url)
            self.assertEqual(response.status_code, 403, response.content)

    def test_post_form(self):
        self.client.force_login(self.user)
        with self.subTest("Single Post"):
            response = self.client.get(self.bulk_url)
            self.assertEqual(response.status_code, 200, response.content)
            response = self.client.post(self.bulk_url, data={"homes": [self.home_status.id]})
            self.assertEqual(response.status_code, 200, response.content)
            self.assertEqual(response["content-type"], "application/pdf")

        with self.subTest("Bulk Post"):
            response = self.client.get(self.bulk_url)
            self.assertEqual(response.status_code, 200, response.content)
            response = self.client.post(
                self.bulk_url,
                data={"homes": [self.home_status.id, self.home_status_2.id]},
                follow=True,
            )
            self.assertEqual(len(response.redirect_chain), 1)
            self.assertIn("/file-operation/document/", response.redirect_chain[0][0])
            self.assertEqual(response.redirect_chain[0][1], 302)

            # Async Document Page
            document_page = response.redirect_chain[0][0]
            response = self.client.get(document_page)
            self.assertEqual(response.status_code, 200)

            # Live status URL
            status_url = document_page.replace("/document/", "/document/stat/")
            response = self.client.get(status_url)
            self.assertEqual(response.status_code, 200)

            # API URL
            api_url = document_page.replace(
                "/file-operation/document/", "/api/v2/asynchronous_document/"
            )
            response = self.client.get(api_url)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn("document", data)
            self.assertTrue(data["document"].endswith(".zip"))
