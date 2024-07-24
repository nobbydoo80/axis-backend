"""adapters.py - Axis"""
import json
import logging
import os
import sqlite3
import warnings

from urllib.parse import urlparse, parse_qs

from django.apps import apps
from django.conf import settings
from django.utils.timezone import now

from geopy.adapters import URLLibAdapter

from infrastructure.utils import elapsed_time

log = logging.getLogger(__name__)

__author__ = "Steven K"
__date__ = "5/24/21 15:49"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]


class GeocodeCacheMissWarning(Warning):
    pass


class CachedDataAdapter(URLLibAdapter):
    """
    This is used to store addresses in a small sqlite db.  It will fetch the data the first time
    and store the results for future use.

    Note:
        This is handled now automatically in our test settings.
        geopy.geocoders.base.options.default_adapter_factory = CachedDataAdapter

    """

    @classmethod
    def create_database(cls, database: str) -> None:
        """Creates a database"""
        conn = sqlite3.connect(database)
        c = conn.cursor()
        c.execute(
            """
                CREATE TABLE geo_data(
                    netloc CHAR(128) NOT NULL,
                    address TEXT NOT NULL,
                    result TEXT NOT NULL
                )
            """
        )
        conn.commit()
        conn.close()

    @classmethod
    def get_cached_address(cls, netloc: str, address: str, database: str) -> dict:
        """Pulls a response from database"""
        conn = sqlite3.connect(database)
        c = conn.cursor()
        c.execute(
            """SELECT result FROM geo_data WHERE netloc=? AND address=?""",
            [netloc.lower(), address.lower()],
        )

        try:
            rows = c.fetchall()
        except Exception as err:
            print(f"Exception {err}")
            raise

        conn.close()
        if not rows:
            raise KeyError(f"{netloc} {address!r} not found!")
        return json.loads(rows[0][0])

    @classmethod
    def store_address(cls, netloc: str, address: str, result: dict, database: str) -> dict:
        conn = sqlite3.connect(database)
        c = conn.cursor()
        c.execute(
            """INSERT INTO geo_data VALUES (?, ?, ?);""",
            (netloc.lower(), address.lower(), json.dumps(result)),
        )
        conn.commit()
        conn.close()
        return result

    def get_json(self, url, *_args, **kwargs):
        """This will simply pull a cached address from a file."""
        geocoder_app = apps.get_app_config("geocoder")
        # We need to strip a few things off of the URL to look it up in our db.
        _url = urlparse(url)
        query = parse_qs(_url.query)
        address = ""
        if "google" in _url.netloc:
            address = query["address"][0]
        elif "virtualearth" in _url.netloc:
            address = query["query"][0]

        try:
            database = settings.GEOCODER_CACHED_STORAGE_FILENAME
            log.info(f"Using db {database}")
        except AttributeError:
            database = geocoder_app.CACHED_STORAGE_FILENAME

        if not os.path.exists(database):
            log.info(f"Creating database {database}")
            self.create_database(database)

        try:
            return self.get_cached_address(_url.netloc, address, database)
        except KeyError:
            kwargs["timeout"] = 30  # Bump this as we want to ensure we get it.
            start = now()
            data = super(CachedDataAdapter, self).get_json(url, *_args, **kwargs)
            if database == geocoder_app.CACHED_STORAGE_FILENAME:
                msg_args = [
                    f"Address look up against {_url.netloc} occurred for {address!r}.  "
                    f"Don't forget to commit updated db {os.path.basename(database)}. "
                    f"Result found in {elapsed_time((now() - start).total_seconds()).long_fmt}",
                    GeocodeCacheMissWarning,
                ]
                warnings.warn(*msg_args)
                print(*msg_args)
            return self.store_address(_url.netloc, address, data, database)
