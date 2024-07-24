import logging

from axis.core.management.commands.set_permissions import AppPermission
from . import models

__author__ = "Autumn Valenta"
__date__ = "11/15/17 2:11 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class CertificationAppPermissions(AppPermission):
    models = [models.Workflow, models.CertifiableObject, models.WorkflowStatus]
    default_abilities = []
    default_admin_abilities = ["add", "change", "delete"]

    def get_trc_permissions(self):
        return ["view", "add", "change", "delete"], [
            "view",
        ]
