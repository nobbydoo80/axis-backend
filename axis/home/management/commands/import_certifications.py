"""single_home_checklist.py: Django """


import logging

from django.core.management.base import AppCommand, CommandError


__author__ = "Autumn Valenta"
__date__ = "12/27/2019 2:11 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class Command(AppCommand):
    help = "Intakes the given NEEA Data Report csv"
    requires_migrations_checks = True

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument(
            "--filename", action="store", dest="filename", help="e.g., NEEA_Data_Report_YYMMDD.csv"
        )

    def handle_app_config(self, app_config, filename, **options):
        app_config.import_certifications(filename)
