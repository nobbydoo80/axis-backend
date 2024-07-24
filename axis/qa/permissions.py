"""permissions.py: Django qa"""

from axis.core.management.commands.set_permissions import AppPermission
from axis.qa.models import QAStatus, QARequirement, QANote

__author__ = "Steven Klass"
__date__ = "12/20/13 6:46 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


class QARequirementPermissions(AppPermission):
    models = [QARequirement]
    default_admin_abilities = [
        "view",
    ]


class QAPermissions(AppPermission):
    models = [QAStatus, QANote]
    default_abilities = ["add", "change", "view"]
