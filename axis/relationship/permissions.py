"""permissions.py: Django relationship"""

from axis.core.management.commands.set_permissions import AppPermission
from axis.relationship.models import Relationship

__author__ = "Steven Klass"
__date__ = "2/1/13 6:29 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


class RelationshipPermissions(AppPermission):
    models = [Relationship]
