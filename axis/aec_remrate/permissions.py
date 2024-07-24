"""permissions.py: Django aec_remrate"""

from axis.core.management.commands.set_permissions import AppPermission
from .models import Simulation

__author__ = "Steven Klass"
__date__ = "4/5/16 13:53"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


class AECPermissions(AppPermission):
    models = [
        Simulation,
    ]
