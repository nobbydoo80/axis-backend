"""permissions.py: Django RESNET"""

from axis.core.management.commands.set_permissions import AppPermission
from .models import RESNETCompany, RESNETContact

__author__ = "Steven Klass"
__date__ = "4/7/16 09:19"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


class ResnetPermissions(AppPermission):
    models = [RESNETCompany, RESNETContact]
