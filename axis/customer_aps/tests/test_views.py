"""aps.py: Django aps.tests"""


import datetime
import logging
import os

from django.conf import settings

from axis.company.models import Company
from axis.core.tests.testcases import AxisTestCase
from axis.eep_program.models import EEPProgram
from axis.filehandling.tests.test_views import AsynchronousProcessedDocumentBaseTestHandler
from axis.floorplan.models import Floorplan
from axis.home.models import Home, EEPProgramHomeStatus
from .mixins import CustomerAPSBulkHomeTests
from ..forms import APSHomeStringForm
from ..models import APSHome
from ..utils import geolocate_apshome

__author__ = "Steven Klass"
__date__ = "1/10/12 3:27 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class APSViewTests(
    CustomerAPSBulkHomeTests, AxisTestCase, AsynchronousProcessedDocumentBaseTestHandler
):
    def test_meterset_import(self):
        """Test the ability to upload a meterset"""

        self.assertEqual(APSHome.objects.all().count(), 0)
        filename = "new-meter-set-sample.csv"
        file_path = os.path.join(settings.SITE_ROOT, "axis", "customer_aps", "sources", filename)

        user = self.user_model.objects.get(company__slug="aps")

        self.assertEqual(self.client.login(username=user.username, password="password"), True)
        self.assertEqual(user.has_perm("customer_aps.add_apshome"), True)

        document = self._handle_uploading(
            user_id=user.id, file_obj=file_path, url="aps_bulk_homes_add", password="password"
        )

        try:
            self.assertEqual(document.final_status, "SUCCESS")
        except AssertionError:
            print(document.result)
            raise

        self.assertEqual(document.download, False)

        results = document.result
        keys = ["info", "errors", "warnings", "traceback", "result", "debug", "latest"]
        self.assertEqual(sorted(list(results.keys())), sorted(keys))
        self.assertIn("Completed processing {} for APS in".format(filename), results["result"])
        self.assertEqual(results["latest"], "3/3 Processing Part 2 of Meterset")

        self.assertEqual(APSHome.objects.all().count(), 3)
        for home in APSHome.objects.all():
            self.assertIsNotNone(home.place)
            self.assertEqual(home.lot_number, home.place.lot_number)
            self.assertEqual(home.street_line1, home.place.street_line1)
            self.assertEqual(home.street_line2, home.place.street_line2)
            self.assertEqual(home.city, home.place.city)
            self.assertEqual(home.county, home.place.county)
            self.assertEqual(home.state, home.place.state)
            self.assertEqual(home.zipcode, home.place.zipcode)
            self.assertEqual(home.metro, home.place.metro)
            self.assertEqual(home.climate_zone, home.place.climate_zone)
            self.assertEqual(home.latitude, home.place.latitude)
            self.assertEqual(home.longitude, home.place.longitude)
            self.assertEqual(home.confirmed_address, home.place.confirmed_address)
            self.assertEqual(home.address_override, home.place.address_override)

    def test_bad_meterset_import(self):
        """Test the ability to upload a bad meterset"""

        self.assertEqual(APSHome.objects.all().count(), 0)
        file_path = os.path.join(
            settings.SITE_ROOT, "axis", "customer_aps", "sources", "meter-set-sample-bad.txt"
        )

        user = self.user_model.objects.get(company__slug="aps")

        self.assertEqual(self.client.login(username=user.username, password="password"), True)
        self.assertEqual(user.has_perm("customer_aps.add_apshome"), True)

        document = self._handle_uploading(
            user_id=user.id, file_obj=file_path, url="aps_bulk_homes_add", password="password"
        )

        self.assertEqual(document.final_status, "FAILURE")
        self.assertEqual(APSHome.objects.all().count(), 0)

        results = document.result
        keys = ["info", "errors", "warnings", "traceback", "result", "debug", "latest"]
        self.assertEqual(sorted(list(results.keys())), sorted(keys))
        self.assertEqual(len(results.get("errors", [])), 2)
        self.assertIn("Did not find Premise ID", results["errors"][-1])

    def _create_aps_home(self):
        data = {
            "premise_id": "214611288",
            "meterset_date": datetime.date.today(),
            "raw_street_line_1": "350 W HORSESHOE AVE",
            "raw_lot_number": None,
            "raw_street_line_2": None,
            "raw_city": "GILBERT",
            "raw_state": "AZ",
            "raw_zip": "85233",
        }

        geolocation_matches = geolocate_apshome(**data)
        self.assertEqual(len(geolocation_matches), 1)
        match = geolocation_matches[0]
        geocoded_data = match.get_normalized_fields()
        values = [
            "street_line1",
            "street_line2",
            "state",
            "zipcode",
            "confirmed_address",
            "latitude",
            "longitude",
        ]
        data.update({k: geocoded_data.get(k, None) for k in values})
        data["geocode_response"] = match.id
        data["city"] = geocoded_data.get("city").id if geocoded_data.get("city") else None
        data["county"] = geocoded_data.get("county").id if geocoded_data.get("county") else None
        form = APSHomeStringForm(data=data, instance=None)
        self.assertEqual(form.is_valid(), True)
        data = form.save()
        return data

    def test_aps_meterset_match(self):
        """This will verify that after a confirmed address matches that it will auto match"""

        # First create the APS Side Home
        aps_home = self._create_aps_home()
        self.assertIsNone(aps_home.home)

        status = EEPProgramHomeStatus.objects.create(
            home=Home.objects.get(street_line1__icontains="horseshoe"),
            eep_program=EEPProgram.objects.get(slug="aps-energy-star-v3-2018"),
            floorplan=Floorplan.objects.get(name="floorplan75"),
            company=Company.objects.get(slug="efl"),
        )

        # Trigger the PostSaveTrigger
        status.home.save()

        # The big finale..
        aps_home = APSHome.objects.get(id=aps_home.id)
        self.assertEqual(status.home, aps_home.home)

    def test_aps_meterset_reverse_match(self):
        """This will verify that after a confirmed address matches that it will auto match"""

        from axis.customer_aps.utils import update_apshomes

        status = EEPProgramHomeStatus.objects.create(
            home=Home.objects.get(street_line1__icontains="horseshoe"),
            eep_program=EEPProgram.objects.get(slug="aps-energy-star-v3-2018"),
            floorplan=Floorplan.objects.get(name="floorplan75"),
            company=Company.objects.get(slug="efl"),
        )

        aps_home = self._create_aps_home()

        confirmations = update_apshomes()

        aps_home = APSHome.objects.get(id=aps_home.id)
        self.assertEqual(len(confirmations), 1)
        self.assertEqual(status.home, aps_home.home)
