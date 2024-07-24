"""router.py: """

from axis.geographic.api_v3.viewsets import (
    CityViewSet,
    NestedCityViewSet,
    CountyViewSet,
    USStateViewSet,
)

__author__ = "Artem Hruzd"
__date__ = "09/30/2020 18:07"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from axis.geographic.api_v3.viewsets.country import CountryViewSet


class GeographicRouter:
    @staticmethod
    def register(router):
        router.register(r"cities", CityViewSet, "cities")
        county_router = router.register(r"counties", CountyViewSet, "counties")
        county_router.register(
            r"cities", NestedCityViewSet, "county-cities", parents_query_lookups=["county_id"]
        )
        router.register(r"us_states", USStateViewSet, "us_states")
        router.register(r"countries", CountryViewSet, "countries")
