"""permissions.py: Django filehandling"""


import logging

from axis.core.management.commands.set_permissions import AppPermission
from .models import AsynchronousProcessedDocument, CustomerDocument

__author__ = "Steven Klass"
__date__ = "2/1/13 6:11 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class FileHandlingTypePermissions(AppPermission):
    models = [CustomerDocument]


class AsynchronousProcessedDocumentPermissions(AppPermission):
    models = [AsynchronousProcessedDocument]
    default_abilities = ["view", "add"]
    default_admin_abilities = ["view", "add"]
