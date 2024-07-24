"""permissions.py: Django geocoder"""


import logging

from axis.core.management.commands.set_permissions import AppPermission
from axis.geocoder.models import GeocodeResponse, Geocode

__author__ = "Steven Klass"
__date__ = "4/7/16 09:17"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class GeocoderPermissions(AppPermission):
    models = [Geocode, GeocodeResponse]
