"""permissions.py: Django messaging"""


from axis.core.management.commands.set_permissions import AppPermission
from .models import MessagingPreference, Message, DigestPreference

__author__ = "Steven Klass"
__date__ = "4/21/13 5:19 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


class MessagePermissions(AppPermission):
    models = [
        Message,
    ]
    default_abilities = ["view", "add", "change"]


class MessagePreferencesPermissions(AppPermission):
    models = [MessagingPreference, DigestPreference]
    default_admin_abilities = ["view", "add", "change"]
    default_abilities = ["view", "add", "change"]
