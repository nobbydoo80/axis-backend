"""permissions.py: Django geographic"""


import logging

from axis.core.management.commands.set_permissions import AppPermission
from axis.geographic.models import City, County, Metro, ClimateZone

__author__ = "Steven Klass"
__date__ = "2/1/13 6:20 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class CityPermissions(AppPermission):
    models = [
        City,
    ]


class CountyMetroClimateZonePermissions(AppPermission):
    models = [County, Metro, ClimateZone]
