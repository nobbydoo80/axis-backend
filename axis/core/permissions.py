"""permissions.py: Django core"""


import logging

from rest_framework.permissions import DjangoModelPermissions

from .management.commands.set_permissions import AppPermission
from django.contrib.auth import get_user_model

__author__ = "Steven Klass"
__date__ = "1/31/13 7:27 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)
User = get_user_model()


class AxisModelPermissions(DjangoModelPermissions):
    perms_map = dict(DjangoModelPermissions.perms_map, GET=["%(app_label)s.view_%(model_name)s"])


class UserPermission(AppPermission):
    """Permissions for a User"""

    models = [User]
    default_admin_abilities = ["view", "add", "change"]

    def get_sponsored_provider_home_innovation_research_labs_rater_permissions(self):
        return [
            "view",
        ]
