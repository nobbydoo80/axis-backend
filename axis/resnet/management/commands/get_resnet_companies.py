"""update_resnet_companies.py: Get RESENT Provider Lists"""


import logging
import pprint

from django.core.management import BaseCommand

from axis.resnet.data_scraper import (
    RESENTProvider,
    RESNETSamplingProvider,
    RESNETTrainingProvider,
    RESNETWaterSenseProvider,
)

__author__ = "Steven Klass"
__date__ = "07/05/2019 09:30"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class Command(BaseCommand):
    """Gets RESNET Provider Directory Data"""

    help = "Gets RESNET Provider Directory Data"
    requires_system_checks = []

    def add_arguments(self, parser):
        """Add our own arguments"""
        parser.add_argument("-A", "--all", help="Update All", action="store_true", dest="get_all")
        parser.add_argument(
            "-p",
            "--provider",
            help="Update Providers",
            action="store_true",
            dest="update_providers",
        )
        parser.add_argument(
            "-s",
            "--sampling",
            help="Update Sampling Providers",
            action="store_true",
            dest="update_sampling_providers",
        )
        parser.add_argument(
            "-t",
            "--training",
            help="Update Training Providers",
            action="store_true",
            dest="update_training_providers",
        )
        parser.add_argument(
            "-w",
            "--water",
            help="Update Water Sense Providers",
            action="store_true",
            dest="update_water_sense_providers",
        )
        parser.add_argument("-P", "--print", help="Print output", action="store_true", dest="print")

    def handle(self, *args, **options):
        """Handle it."""

        if options.get("update_providers") or options.get("get_all"):
            parser = RESENTProvider()
            providers = parser.parse()
            if options.get("print"):
                pprint.pprint(providers)
            print("Found %d Providers" % len(providers))

        if options.get("update_sampling_providers") or options.get("get_all"):
            parser = RESNETSamplingProvider()
            sampling_providers = parser.parse()
            if options.get("print"):
                pprint.pprint(sampling_providers)
            print("Found %d Sampling Providers" % len(sampling_providers))

        if options.get("update_training_providers") or options.get("get_all"):
            parser = RESNETTrainingProvider()
            training_providers = parser.parse()
            if options.get("print"):
                pprint.pprint(training_providers)
            print("Found %d Training Providers" % len(training_providers))

        if options.get("update_water_sense_providers") or options.get("get_all"):
            parser = RESNETWaterSenseProvider()
            water_sense_providers = parser.parse()
            if options.get("print"):
                pprint.pprint(water_sense_providers)
            print("Found %d Water Sense Providers" % len(water_sense_providers))
