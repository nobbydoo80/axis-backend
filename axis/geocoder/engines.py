"""engines.py: Django geocoder"""


import logging

from django.apps import apps
from django.conf import settings

import geopy
from geopy.exc import (
    GeocoderAuthenticationFailure,
    GeocoderInsufficientPrivileges,
    GeocoderQuotaExceeded,
    GeocoderServiceError,
    GeocoderUnavailable,
)
from geopy.geocoders import Bing, GoogleV3


__author__ = "Peter Landry"
__date__ = "12/4/13 5:47 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Peter Landry",
]

from geopy.geocoders.base import DEFAULT_SENTINEL

log = logging.getLogger(__name__)
app = apps.get_app_config("geocoder")


class PESGoogleV3(GoogleV3):
    """Adapted Google geocoder for Django usage"""

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        api_key=None,
        domain="maps.googleapis.com",
        scheme=None,
        client_id=None,
        secret_key=None,
        timeout=None,
        proxies=geopy.geocoders.base.DEFAULT_SENTINEL,
        user_agent=None,
        ssl_context=geopy.geocoders.base.DEFAULT_SENTINEL,
        adapter_factory=None,
        channel="",
    ):
        client_id = client_id or settings.GOOGLE_MAPS_CLIENT_ID
        secret_key = secret_key or settings.GOOGLE_MAPS_API_KEY
        timeout = timeout if timeout else app.GEOCODER_DEFAULT_TIMEOUT
        if timeout is not None and not isinstance(timeout, int):
            # This will raise a nasty Warning that is all but impossible to track down
            raise TypeError("ERROR We need an int we got %s %s" % (type(timeout), timeout))
        super(PESGoogleV3, self).__init__(
            api_key=api_key,
            domain=domain,
            scheme=scheme,
            client_id=client_id,
            secret_key=secret_key,
            timeout=timeout,
            proxies=proxies,
            user_agent=user_agent,
            ssl_context=ssl_context,
            adapter_factory=adapter_factory,
            channel=channel,
        )

    def geocode(
        self,
        query=None,
        exactly_one=True,
        timeout=geopy.geocoders.base.DEFAULT_SENTINEL,
        bounds=None,
        region=None,
        components=None,
        place_id=None,
        language=None,
        sensor=False,
    ):
        """Overriding method to set own defaults"""
        # Note to restrict by country API is an AND not OR so we need to do this upstream
        # See: https://developers.google.com/maps/documentation/javascript/geocoding#ComponentFiltering
        return super(PESGoogleV3, self).geocode(
            query=query,
            exactly_one=exactly_one,
            timeout=timeout,
            bounds=bounds,
            region=region,
            components=components,
            place_id=place_id,
            language=language,
            sensor=sensor,
        )

    def _parse_json(self, page, exactly_one=True):
        """Return list of dictionaries with place information"""

        places = page.get("results", [])
        if not places:
            self._check_status(page)
            return []
        return places


class PESBing(Bing):
    """Adapted Bing geocoder for Django usage"""

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        api_key=None,
        scheme=None,
        timeout=None,
        proxies=geopy.geocoders.base.DEFAULT_SENTINEL,
        user_agent=None,
        ssl_context=geopy.geocoders.base.DEFAULT_SENTINEL,
        adapter_factory=None,
    ):
        timeout = timeout if timeout else app.GEOCODER_DEFAULT_TIMEOUT
        if timeout is not None and not isinstance(timeout, int):
            # This will raise a nasty Warning that is all but impossible to track down
            raise TypeError("ERROR We need an int we got %s %s" % (type(timeout), timeout))
        api_key = api_key or settings.BING_MAPS_API_KEY
        super(PESBing, self).__init__(
            api_key=api_key,
            scheme=scheme,
            timeout=timeout,
            proxies=proxies,
            user_agent=user_agent,
            ssl_context=ssl_context,
            adapter_factory=adapter_factory,
        )

    def geocode(
        self,
        query,
        *args,
        exactly_one=True,
        user_location=None,
        timeout=DEFAULT_SENTINEL,
        culture=None,
        include_neighborhood=None,
        include_country_code=True,
    ):
        # Note to filter by country we would use countrySet parameter.  We do this upstream.
        # See: https://docs.microsoft.com/en-us/rest/api/maps/search/get-search-address?tabs=HTTP
        return super(PESBing, self).geocode(
            query=query,
            exactly_one=exactly_one,
            user_location=user_location,
            include_neighborhood=include_neighborhood,
            include_country_code=include_country_code,
        )

    def _parse_json(self, doc, exactly_one=True):
        """Return list of dictionaries with place information"""

        status_code = doc.get("statusCode", 200)
        if status_code != 200:
            err = doc.get("errorDetails", "")
            if status_code == 401:
                raise GeocoderAuthenticationFailure(err)
            elif status_code == 403:
                raise GeocoderInsufficientPrivileges(err)
            elif status_code == 429:
                raise GeocoderQuotaExceeded(err)
            elif status_code == 503:
                raise GeocoderUnavailable(err)
            else:
                raise GeocoderServiceError(err)

        resources = doc["resourceSets"][0]["resources"]
        if not resources:
            return []
        return [
            resources[0],
        ]


GEOCODER_ENGINES = {"Google": PESGoogleV3, "Bing": PESBing}

GEOCODER_ENGINE_CHOICES = [(engine_name, engine_name) for engine_name in GEOCODER_ENGINES]
