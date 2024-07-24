"""certification_import.py - Axis"""
import logging

from django.core.management import BaseCommand, CommandError

from axis.customer_neea.neea_data_report import NEEADataReportConfig

log = logging.getLogger(__name__)

__author__ = "Steven K"
__date__ = "3/1/21 11:05"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]


class Command(BaseCommand):
    help = "Imports Certification dumps from RESNET.  Note:  Infile argument is a CSV File."
    requires_system_checks = []

    def add_arguments(self, parser):
        parser.add_argument("--infile", metavar="FILE", required=True)

    def handle(self, *args, **options):
        """Run this sucker"""

        if not options["infile"].lower().endswith(".csv"):
            raise CommandError("You need to use as .csv")

        config = NEEADataReportConfig()
        config.import_certifications(options["infile"])
