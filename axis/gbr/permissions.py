"""permissions.py - axis"""

__author__ = "Steven K"
__date__ = "1/27/23 11:23"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from axis.core.management.commands.set_permissions import AppPermission
from .models import GreenBuildingRegistry

log = logging.getLogger(__name__)


class GBRPermissions(AppPermission):
    """Base Permissions Class for GBR"""

    models = [
        GreenBuildingRegistry,
    ]

    def get_qa_permissions(self):
        return [], []
