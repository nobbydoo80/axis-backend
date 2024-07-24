"""test_context.py - Axis"""

__author__ = "Steven K"
__date__ = "1/4/22 08:57"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from django.core import management
from rest_framework.test import APITestCase

from axis.checklist.collection.test_mixins import CollectionRequestMixin
from axis.checklist.models import CollectedInput
from axis.core.tests.test_views import DevNull
from axis.customer_eto.api_v3.viewsets import ProjectTrackerXMLViewSet
from axis.customer_eto.enumerations import SmartThermostatBrands2020
from axis.customer_eto.models import FastTrackSubmission
from axis.customer_eto.tests.program_checks.test_eto_2020 import ETO2020ProgramTestMixin
from axis.eep_program.models import EEPProgram
from axis.home.models import EEPProgramHomeStatus, Home

log = logging.getLogger(__name__)


class TestProjectTrackerMixed(ETO2020ProgramTestMixin, APITestCase):
    """This verifies that when we have multiple programs getting the context data
    still work out.  Right now we only ask a question if it needs to be asked."""

    @classmethod
    def setUpTestData(cls):
        super(TestProjectTrackerMixed, cls).setUpTestData()

        collection_mixin = CollectionRequestMixin()
        collection_mixin.add_collected_input(
            value="Gas Furnace",
            measure_id="primary-heating-equipment-type",
            home_status=cls.home_status,
        )
        collection_mixin.add_collected_input(
            value={
                "input": {
                    "capacity": "50",
                    "brand_name": "OLD BRAND",
                    "model_number": "OLD VERSION",
                    "energy_factor": "0.60",
                }
            },
            measure_id="equipment-water-heater",
            home_status=cls.home_status,
        )
        cls.home_status.state = "abandonded"
        cls.home_status.save()

        # Now update the program

        management.call_command(
            "build_program",
            "-p",
            "eto-2021",
            "--warn_only",
            "--no_close_dates",
            stdout=DevNull(),
        )
        cls.eep_program = EEPProgram.objects.get(slug="eto-2021")

        cls.home_status = EEPProgramHomeStatus.objects.create(
            home=cls.home_status.home,
            company=cls.home_status.company,
            floorplan=cls.home_status.floorplan,
            eep_program=cls.eep_program,
        )
        cls.home_status.set_collection_from_program()

        collection_mixin = CollectionRequestMixin()
        collection_mixin.add_collected_input(
            value=SmartThermostatBrands2020.BRYANT,
            measure_id="smart-thermostat-brand",
            home_status=cls.home_status,
        )
        collection_mixin.add_collected_input(
            value={
                "input": {
                    "capacity": "50",
                    "brand_name": "NEW BRAND",
                    "model_number": "GS6 50 BRT*",
                    "energy_factor": "0.60",
                }
            },
            measure_id="equipment-water-heater",
            home_status=cls.home_status,
        )

        cls.project_tracker = FastTrackSubmission.objects.create(
            home_status=cls.home_status,
            builder_incentive=125.69,
            rater_incentive=225.21,
        )

    def test_setup(self):
        self.assertEqual(Home.objects.count(), 1)
        self.assertEqual(EEPProgram.objects.count(), 4)
        self.assertEqual(CollectedInput.objects.count(), 4)
        self.assertEqual(EEPProgramHomeStatus.objects.count(), 2)

    def test_collected_input_data_gettr(self):
        """This will verify that we pull ALL answers including cooperative requests"""
        viewset = ProjectTrackerXMLViewSet()
        data = viewset.get_collected_input_context(self.project_tracker)

        # This one is from the prior program
        with self.subTest("Test grab prior program data on same home"):
            self.assertEqual(data["primary_heating_type"], "Gas Furnace")

        # This grabs the latest answer when m
        with self.subTest("Test grab latest_response on same home"):
            self.assertEqual(data["water_heater_brand"], "NEW BRAND")
