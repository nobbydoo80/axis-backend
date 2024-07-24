"""router.py: """

from axis.geocoder.api_v3.viewsets import GeocodeViewSet

__author__ = "Artem Hruzd"
__date__ = "09/30/2020 18:20"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class GeocoderRouter:
    @staticmethod
    def register(router):
        # geocoder app
        geocoder_router = router.register(r"geocoder", GeocodeViewSet, "geocoder")
