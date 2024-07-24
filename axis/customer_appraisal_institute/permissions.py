"""permissions.py: Django appraisal_institute"""


import logging

from axis.core.management.commands.set_permissions import AppPermission
from .models import GEEAData

__author__ = "Steven Klass"
__date__ = "4/6/16 13:01"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class NEEAPermissions(AppPermission):
    models = [
        GEEAData,
    ]
    default_admin_abilities = [
        "view",
    ]
