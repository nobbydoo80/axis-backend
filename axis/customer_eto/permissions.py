"""permissions.py: Django customer_eto"""

from django.apps import apps

from axis.core.management.commands.set_permissions import AppPermission
from .models import FastTrackSubmission, ETOAccount, PermitAndOccupancySettings

__author__ = "Steven Klass"
__date__ = "4/7/16 08:24"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

app = apps.get_app_config("customer_eto")


class ETOAccountPermissions(AppPermission):
    models = [
        ETOAccount,
    ]
    default_abilities = []
    default_admin_abilities = []

    def get_eto_permissions(self):
        return ["view", "add", "change", "delete"], [
            "view",
        ]

    def get_peci_permissions(self):
        return ["view", "add", "change", "delete"], [
            "view",
        ]

    def get_csg_qa_permissions(self):
        return ["view", "add", "change", "delete"], [
            "view",
        ]


class FastTrackSubmissionPermissions(AppPermission):
    models = [
        FastTrackSubmission,
    ]
    default_abilities = []
    default_admin_abilities = []

    def get_eto_permissions(self):
        return ["view", "add", "change"], [
            "view",
        ]

    def get_peci_permissions(self):
        return ["view", "add", "change"], [
            "view",
        ]


# pylint: disable=abstract-method
class PermitAndOccupancySettingsPermissions(AppPermission):
    """Permission controls for Hillsboro participants."""

    # NOTE: The companies obtaining these permissions are based on the appconfig's
    # `CITY_OF_HILLSBORO_PARTICIPANT_SLUGS` static setting, meaning that this class should not be
    # modified except to change how the

    def __init__(self, *args, **kwargs):
        super(PermitAndOccupancySettingsPermissions, self).__init__(*args, **kwargs)

        # Assign dynamic hooks
        for slug in app.CITY_OF_HILLSBORO_PARTICIPANT_SLUGS:
            setattr(
                self,
                "get_{flat_slug}_permissions".format(flat_slug=slug.replace("-", "_")),
                self._get_hillsboro_verifiers_permissions,
            )

    models = [
        PermitAndOccupancySettings,
    ]
    default_abilities = []
    default_admin_abilities = []

    def _get_hillsboro_verifiers_permissions(self):
        """Return default calculated admin/default permissions."""

        return ["view", "add", "change"], ["view", "add", "change"]
