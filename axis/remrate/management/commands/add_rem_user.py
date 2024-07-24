"""Adds a mysql user with password to the `remrate` db with all GRANT privileges."""


from django.core.management import BaseCommand

from ..models import RemRateUser

__author__ = "Steven Klass"
__date__ = "01/28/2019 11:26"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class Command(BaseCommand):
    """Run a BLG Parsing and optionally dump out the test data."""

    help = "Adds a mysql user with password to the `remrate` db with all GRANT privileges."
    requires_system_checks = []

    def add_arguments(self, parser):
        """Add our own arguments"""
        parser.add_argument("username", type=str, nargs=1, help="remrate db usernamer")
        parser.add_argument("password", type=str, nargs=1, help="remrate db password")

    def handle(self, username, password):
        try:
            list(
                RemRateUser.objects.raw(
                    "GRANT ALL PRIVILEGES on remrate.* to %s@'%' IDENTIFIED BY %s",
                    [username, password],
                )
            )
        except TypeError:
            # None will not unpack to a list, but casting forces the query to evaluate properly
            pass
