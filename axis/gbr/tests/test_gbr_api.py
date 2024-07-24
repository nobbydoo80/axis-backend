"""test_gbr_api.py - axis"""

__author__ = "Steven K"
__date__ = "1/9/23 13:42"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import datetime
import logging
from unittest import mock

from django.apps import apps
from django.core import management

from axis.annotation.models import Annotation
from axis.checklist.collection.test_mixins import CollectionRequestMixin
from axis.core.tests.test_views import DevNull
from axis.core.tests.testcases import AxisTestCase
from axis.customer_eto.tests.program_checks.test_eto_2022 import ETO2022ProgramCompleteTestMixin
from axis.gbr.gbr import GreenBuildingRegistryAPIConnect
from axis.gbr.gbr.serializers import GBRHomeSerializer, GBRHomeStatusEPSSerializer
from axis.gbr.models import GbrStatus, GreenBuildingRegistry
from axis.gbr.tests.mocked_responses import gbr_mocked_response
from axis.geocoder.models import Geocode
from axis.geographic.models import County
from axis.home.models import Home, EEPProgramHomeStatus
from simulation.enumerations import PvCapacity
from simulation.tests.factories import photovoltaic_factory

log = logging.getLogger(__name__)
gbr_app = apps.get_app_config("gbr")


class GBRSerializerTests(ETO2022ProgramCompleteTestMixin, AxisTestCase):
    def test_home_serializer(self):
        with self.subTest("Residential"):
            Home.objects.update(is_multi_family=False)
            serializer = GBRHomeSerializer(instance=Home.objects.get())
            # Verify that we are using the as entered address.
            self.assertEqual(
                self.home_kwargs["street_line1"],
                self.home.get_home_address_display_parts(raw=True).street_line1,
            )
            self.assertNotEqual(
                self.home.street_line1,
                self.home.get_home_address_display_parts(raw=True).street_line1,
            )
            data = serializer.data

            self.assertEqual(data["address_line_1"], self.home_kwargs["street_line1"])
            self.assertEqual(data["city"], self.home_kwargs["city"].name)
            self.assertEqual(data["state"], self.home_kwargs["city"].county.state)
            self.assertEqual(data["postal_code"], self.home_kwargs["zipcode"])

            self.assertEqual(data["address_line_1"], "854 West 27th Avenue")
            self.assertEqual(data["address_line_2"], "")
            self.assertEqual(data["city"], "Eugene")
            self.assertEqual(data["state"], "OR")
            self.assertEqual(data["postal_code"], "97405")
            self.assertEqual(data["building_type"], "residential")

        with self.subTest("Multi-Family"):
            Home.objects.update(is_multi_family=True)
            Geocode.objects.update(raw_street_line2="#2")
            serializer = GBRHomeSerializer(instance=Home.objects.get())
            self.assertEqual(serializer.data["building_type"], "multifamily")
            self.assertEqual(serializer.data["address_line_2"], "#2")


class GBRHomeStatusEPSSerializerTests(ETO2022ProgramCompleteTestMixin, AxisTestCase):
    def test_serializer(self):
        # Get a GBR
        gbr = GreenBuildingRegistry.objects.create(
            gbr_id="foobar", home=self.home_status.home, status=GbrStatus.PROPERTY_VALID
        )

        # Fake certify the home
        EEPProgramHomeStatus.objects.filter(pk=self.home_status.pk).update(
            certification_date=str(datetime.date.today()),
            state="complete",
        )

        # Get a report
        management.call_command(
            "generate_eto_report",
            "--home-status",
            self.home_status.id,
            "--store",
            stdout=DevNull(),
        )

        self.home_status.refresh_from_db()
        self.simulation.photovoltaics.all().delete()

        # Here we are simply testing o
        with self.subTest("Pretty Empty"):
            serializer = GBRHomeStatusEPSSerializer(instance=self.home_status)

            self.assertEqual(serializer.data["gbr_id"], "foobar")
            self.assertEqual(serializer.data["certification_number"], f"{self.home_status.pk:0>6}")
            self.assertEqual(serializer.data["date"], str(datetime.date.today()))
            self.assertIsNotNone(serializer.data["score"])
            self.assertEqual(serializer.data["source"], "AXIS")
            self.assertIn("public_document", serializer.data["report_url"])
            self.assertIsNotNone(serializer.data["expiration_date"])
            self.assertEqual(serializer.data["conditioned_floor_area"], 2150)
            self.assertEqual(serializer.data["annual_generated"], None)
            self.assertEqual(serializer.data["capacity"], None)
            self.assertEqual(serializer.data["year_installed"], None)

        with self.subTest("PV Adders"):
            photovoltaic_factory(
                simulation=self.simulation,
                company=self.simulation.company,
                capacity=9600.51,
                capacity_units=PvCapacity.WATT,
            )
            photovoltaic_factory(
                simulation=self.simulation,
                company=self.simulation.company,
                capacity=2.1,
                capacity_units=PvCapacity.KWDC,
            )
            collection_mixin = CollectionRequestMixin()
            collection_mixin.add_bulk_answers(
                {"ets-annual-etsa-kwh": 1200},
                home_status=self.home_status,
            )
            self.home_status.refresh_from_db()
            serializer = GBRHomeStatusEPSSerializer(instance=self.home_status)
            self.assertEqual(serializer.data["annual_generated"], 1200)
            self.assertEqual(serializer.data["capacity"], 12)
            self.assertEqual(serializer.data["year_installed"], datetime.date.today().year)


@mock.patch("axis.gbr.gbr.GreenBuildingRegistryAPIConnect.post", side_effect=gbr_mocked_response)
class GreenBuildingRegistryAPIConnectTests(ETO2022ProgramCompleteTestMixin, AxisTestCase):
    def test_sandbox_mode_swaps(self, _mock):
        with self.subTest("Sandbox"):
            gbr = GreenBuildingRegistryAPIConnect(use_sandbox=True)
            self.assertEqual(gbr.api_key, gbr_app.API_KEY)
            self.assertTrue(gbr.use_sandbox)
            self.assertIn("sandbox", gbr.base_url)

        with self.subTest("Non Sandbox"):
            gbr = GreenBuildingRegistryAPIConnect(use_sandbox=False)
            # self.assertNotEqual(gbr.api_key, gbp_app.API_KEY)
            self.assertFalse(gbr.use_sandbox)
            self.assertNotIn("sandbox", gbr.base_url)

    def test_create_valid_home(self, _mock):
        Annotation.objects.filter(type__slug=gbr_app.EXTERNAL_ID_ANNOTATION_SLUG).delete()
        gbr = GreenBuildingRegistryAPIConnect()
        gbr_object = gbr.create_property(Home.objects.get())
        self.assertEqual(str(gbr_object), "OR10174306 (Property Valid)", gbr_object.api_result)
        self.assertEqual(gbr_object.home, self.home)
        self.assertEqual(gbr_object.gbr_id, "OR10174306")
        self.assertEqual(gbr_object.status, GbrStatus.PROPERTY_VALID)
        self.assertEqual(gbr_object.api_result, None)
        self.assertEqual(gbr_object.external_url, "")

    def test_create_invalid_address(self, _mock):
        Annotation.objects.filter(type__slug=gbr_app.EXTERNAL_ID_ANNOTATION_SLUG).delete()
        gbr = GreenBuildingRegistryAPIConnect()
        Geocode.objects.update(raw_street_line1="12 Foo bar lane")
        gbr_object = gbr.create_property(Home.objects.get())
        self.assertEqual(str(gbr_object), "- (Property Invalid)", gbr_object.api_result)
        self.assertEqual(gbr_object.home, self.home)
        self.assertEqual(gbr_object.gbr_id, None)
        self.assertEqual(gbr_object.status, GbrStatus.PROPERTY_INVALID)
        self.assertIn("validation_errors", gbr_object.api_result)

    def test_create_invalid_address_avail(self, _mock):
        Annotation.objects.filter(type__slug=gbr_app.EXTERNAL_ID_ANNOTATION_SLUG).delete()
        gbr = GreenBuildingRegistryAPIConnect()
        Geocode.objects.update(raw_street_line1="12 service lane")
        gbr_object = gbr.create_property(Home.objects.get())
        self.assertEqual(str(gbr_object), "- (Service Unavailable)", gbr_object.api_result)
        self.assertEqual(gbr_object.home, self.home)
        self.assertEqual(gbr_object.gbr_id, None)
        self.assertEqual(gbr_object.status, GbrStatus.SERVICE_UNAVAILABLE)
        self.assertIn("error", gbr_object.api_result)

    def test_create_invalid_address_throttled(self, _mock):
        Annotation.objects.filter(type__slug=gbr_app.EXTERNAL_ID_ANNOTATION_SLUG).delete()
        gbr = GreenBuildingRegistryAPIConnect()
        Geocode.objects.update(raw_street_line1="12 throttled lane")
        gbr_object = gbr.create_property(Home.objects.get())
        self.assertEqual(str(gbr_object), "- (Service Throttled)", gbr_object.api_result)
        self.assertEqual(gbr_object.home, self.home)
        self.assertEqual(gbr_object.gbr_id, None)
        self.assertEqual(gbr_object.status, GbrStatus.SERVICE_THROTTLED)
        self.assertIn("description", gbr_object.api_result)

    def test_create_invalid_program(self, _mock):
        Annotation.objects.filter(type__slug=gbr_app.EXTERNAL_ID_ANNOTATION_SLUG).delete()
        gbr = GreenBuildingRegistryAPIConnect()
        County.objects.update(state="CA")
        gbr_object = gbr.create_property(Home.objects.get())
        self.assertEqual(str(gbr_object), "- (Property Invalid)", gbr_object.api_result)
        self.assertEqual(gbr_object.home, self.home)
        self.assertEqual(gbr_object.gbr_id, None)
        self.assertEqual(gbr_object.status, GbrStatus.PROPERTY_INVALID)
        self.assertIn("description", gbr_object.api_result)

    def test_reuse_existing_gbr_id(self, _mock):
        annotation = Annotation.objects.filter(type__slug=gbr_app.EXTERNAL_ID_ANNOTATION_SLUG)
        self.assertTrue(annotation.exists())
        annotation = annotation.get().content

        gbr = GreenBuildingRegistryAPIConnect()
        gbr_object = gbr.create_property(Home.objects.get())
        self.assertEqual(str(gbr_object), f"{annotation} (Legacy Import)", gbr_object.api_result)
        self.assertEqual(gbr_object.home, self.home)
        self.assertEqual(gbr_object.gbr_id, annotation)
        self.assertEqual(gbr_object.status, GbrStatus.LEGACY_IMPORT)
        self.assertEqual(gbr_object.api_result, None)

    def test_create_assessement_missing_data(self, _mock):
        Annotation.objects.filter(type__slug=gbr_app.EXTERNAL_ID_ANNOTATION_SLUG).delete()
        gbr = GreenBuildingRegistryAPIConnect()
        gbr_object = gbr.create_property(Home.objects.get())
        # This home is not yet certified
        gbr.create_assessment(gbr_object, assessment="eps")
        self.assertEqual(gbr_object.status, GbrStatus.ASSESSMENT_INVALID)
        self.assertIsNotNone(gbr_object.api_result)

    def test_create_assessment_with_pv(self, _mock):
        Annotation.objects.filter(type__slug=gbr_app.EXTERNAL_ID_ANNOTATION_SLUG).delete()

        photovoltaic_factory(
            simulation=self.simulation,
            company=self.simulation.company,
            capacity=9600.51,
            capacity_units=PvCapacity.WATT,
        )
        collection_mixin = CollectionRequestMixin()
        collection_mixin.add_bulk_answers(
            {"ets-annual-etsa-kwh": 1200},
            home_status=self.home_status,
        )

        # Fake certify the home
        EEPProgramHomeStatus.objects.filter(pk=self.home_status.pk).update(
            certification_date=str(datetime.date.today()),
            state="complete",
        )
        # Generate the ETO Report
        management.call_command(
            "generate_eto_report",
            "--home-status",
            self.home_status.id,
            "--store",
            stdout=DevNull(),
        )

        gbr = GreenBuildingRegistryAPIConnect()
        gbr_object = gbr.create_property(Home.objects.get())

        self.home_status.refresh_from_db()
        gbr.create_assessment(gbr_object, assessment="eps")
        self.assertEqual(gbr_object.status, GbrStatus.ASSESSMENT_CREATED, gbr_object.api_result)
        self.assertEqual(gbr_object.api_result["PowerProductionType"], "Photovoltaics")
        self.assertEqual(gbr_object.api_result["PowerProductionSize"], "9601.0 kW DC")
        self.assertEqual(gbr_object.api_result["PowerProductionAnnual"], "1200 kWh/year")
        self.assertEqual(
            gbr_object.api_result["PowerProductionYearInstall"], datetime.date.today().year
        )
        self.assertEqual(
            gbr_object.external_url,
            "https://us-sandbox.greenbuildingregistry.com/green-homes/OR10174306",
        )

    def test_create_assessment_no_pv(self, _mock):
        Annotation.objects.filter(type__slug=gbr_app.EXTERNAL_ID_ANNOTATION_SLUG).delete()
        gbr = GreenBuildingRegistryAPIConnect()
        gbr_object = gbr.create_property(Home.objects.get())

        # # Fake certify the home
        EEPProgramHomeStatus.objects.filter(pk=self.home_status.pk).update(
            certification_date=str(datetime.date.today()),
            state="complete",
        )

        # Get a report
        management.call_command(
            "generate_eto_report",
            "--home-status",
            self.home_status.id,
            "--store",
            stdout=DevNull(),
        )

        self.home_status.refresh_from_db()
        gbr.create_assessment(gbr_object, assessment="eps")
        self.assertEqual(gbr_object.status, GbrStatus.ASSESSMENT_CREATED)
        self.assertIsNotNone(gbr_object.api_result)

        self.assertEqual(gbr_object.api_result["status"], None)
        self.assertEqual(gbr_object.api_result["GreenBuildingVerificationType"], "EPS")
        self.assertEqual(gbr_object.api_result["GreenVerificationBody"], "Energy Trust of Oregon")
        self.assertEqual(gbr_object.api_result["GreenVerificationDate"], str(datetime.date.today()))
        self.assertIsNotNone(gbr_object.api_result["GreenVerificationMetric"])
        self.assertEqual(gbr_object.api_result["GreenVerificationSource"], "AXIS")
        self.assertEqual(gbr_object.api_result["GreenVerificationStatus"], "")
        self.assertEqual(
            gbr_object.api_result["GreenVerificationURL"],
            "https://None.pivotalenergy.net/api/v3/public_document/1Z/",
        )
        self.assertEqual(gbr_object.api_result["GreenBuildingVerificationKey"], "000001")
        self.assertEqual(gbr_object.api_result["GreenVerificationVersion"], "")
        self.assertEqual(gbr_object.api_result["GreenVerificationYear"], datetime.date.today().year)

    def test_bad_service(self, _mock):
        Annotation.objects.filter(type__slug=gbr_app.EXTERNAL_ID_ANNOTATION_SLUG).delete()
        gbr = GreenBuildingRegistryAPIConnect()
        gbr_object = gbr.create_property(Home.objects.get())

        # # Fake certify the home
        EEPProgramHomeStatus.objects.filter(pk=self.home_status.pk).update(
            certification_date=str(datetime.date.today()),
            state="complete",
        )

        # Get a report
        management.call_command(
            "generate_eto_report",
            "--home-status",
            self.home_status.id,
            "--store",
            stdout=DevNull(),
        )
        # Hook to override
        for hook, status in [
            ("SERVICE", GbrStatus.SERVICE_UNAVAILABLE),
            ("THROTTLE", GbrStatus.SERVICE_THROTTLED),
        ]:
            with self.subTest(f"Testing {hook}"):
                GreenBuildingRegistry.objects.all().update(gbr_id=hook)
                self.home_status.refresh_from_db()
                gbr.create_assessment(gbr_object, assessment="eps")
                self.assertEqual(gbr_object.status, status)
                self.assertIsNotNone(gbr_object.api_result)

    def test_create_multiple_assessment_no_pv(self, _mock):
        """GBR allows us to just resubmit the same thing over and over again.."""
        Annotation.objects.filter(type__slug=gbr_app.EXTERNAL_ID_ANNOTATION_SLUG).delete()
        gbr = GreenBuildingRegistryAPIConnect()
        gbr_object = gbr.create_property(Home.objects.get())

        # # Fake certify the home
        EEPProgramHomeStatus.objects.filter(pk=self.home_status.pk).update(
            certification_date=str(datetime.date.today()),
            state="complete",
        )

        # Get a report
        management.call_command(
            "generate_eto_report",
            "--home-status",
            self.home_status.id,
            "--store",
            stdout=DevNull(),
        )
        self.home_status.refresh_from_db()
        gbr.create_assessment(gbr_object, assessment="eps")
        self.assertEqual(gbr_object.status, GbrStatus.ASSESSMENT_CREATED)
        self.assertIsNotNone(gbr_object.api_result)

        from axis.customer_eto.models import FastTrackSubmission

        FastTrackSubmission.objects.update(eps_score=9999)
        gbr.create_assessment(gbr_object, assessment="eps")
        self.assertEqual(gbr_object.status, GbrStatus.ASSESSMENT_CREATED)
        self.assertIsNotNone(gbr_object.api_result)
        self.assertIsNotNone(gbr_object.api_result["GreenVerificationMetric"], 9999)
