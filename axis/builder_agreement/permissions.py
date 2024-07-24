"""permissions.py: Django builder_agreement"""


import logging

from axis.core.management.commands.set_permissions import AppPermission
from .models import BuilderAgreement

__author__ = "Steven Klass"
__date__ = "2/1/13 12:28 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class BuilderAgreementInformationPermissions(AppPermission):
    models = [
        BuilderAgreement,
    ]
    default_abilities = []
    default_admin_abilities = []

    def get_aps_permissions(self):
        return ["view", "add", "change", "delete"]

    def get_sponsored_aps_builder_permissions(self):
        return [
            "view",
        ]
