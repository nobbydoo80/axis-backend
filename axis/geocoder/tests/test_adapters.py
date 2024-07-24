"""test_adapters.py - axis"""

__author__ = "Steven K"
__date__ = "7/13/22 08:14"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
import os.path
import sqlite3
import tempfile
import uuid

from django.conf import settings
from django.test import TestCase, override_settings

from axis.geocoder.engines import PESGoogleV3

log = logging.getLogger(__name__)


class CachedDataAdapterTests(TestCase):
    address = "175 5th Avenue NYC"

    def get_rows(self, database):
        conn = sqlite3.connect(settings.GEOCODER_CACHED_STORAGE_FILENAME)
        c = conn.cursor()
        c.execute("""SELECT netloc, address, result FROM geo_data""")
        rows = c.fetchall()
        conn.close()
        return rows

    @override_settings(
        GEOCODER_CACHED_STORAGE_FILENAME=os.path.join(
            tempfile.gettempdir(), f"test_{uuid.uuid1()}.db"
        )
    )
    def test_actual_create(self):
        geolocator = PESGoogleV3()
        location = geolocator.geocode(self.address)
        with self.subTest("DB Exists"):
            self.assertTrue(os.path.exists(settings.GEOCODER_CACHED_STORAGE_FILENAME))

        with self.subTest("Record Exists"):
            rows = self.get_rows(settings.GEOCODER_CACHED_STORAGE_FILENAME)
            self.assertEqual(len(rows), 1)
            netloc, address, result = rows[0]
            self.assertIn("maps.googleapis.com", netloc)
            self.assertEqual(self.address.lower(), address)
            self.assertIn(
                """{"results": [{"address_components": [{"long_name": "Flatiron Building",""",
                result,
            )
        with self.subTest("No doubles"):
            location = geolocator.geocode(self.address.upper())
            rows = self.get_rows(settings.GEOCODER_CACHED_STORAGE_FILENAME)
            self.assertEqual(len(rows), 1)
