"""permissions.py: Django """


import logging

from axis.core.management.commands.set_permissions import AppPermission
from .models import HESSimulationStatus

__author__ = "Steven K"
__date__ = "11/19/2019 14:46"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

log = logging.getLogger(__name__)


class HESPermissions(AppPermission):
    """Base Permissions Class for HPXML"""

    models = [
        HESSimulationStatus,
    ]

    def get_qa_permissions(self):
        return [], []
