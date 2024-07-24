"""permissions.py: Django eep_program"""


import logging

from axis.core.management.commands.set_permissions import AppPermission
from .models import EEPProgram

__author__ = "Steven Klass"
__date__ = "2/1/13 5:40 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class EEPProgramPermissions(AppPermission):
    models = [
        EEPProgram,
    ]

    def get_eep_permissions(self):
        return ["view", "add", "change", "delete"], ["view"]

    def get_customer_permissions(self):
        return ["view", "add", "change", "delete"], ["view"]

    def get_trc_permissions(self):
        return [], []
