"""set_versions: Django core"""

import logging

from django.core.management.base import BaseCommand

__author__ = "Steven Klass"
__date__ = "11/17/14 8:53 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = (
        "Sets the versions file (._versions) - used to non-evasively store "
        "the last change to our axis"
    )

    def handle(self, *app_labels, **options):
        from ...git_utils import set_version_numbers

        set_version_numbers()
