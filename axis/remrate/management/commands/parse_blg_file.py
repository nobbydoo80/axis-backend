"""blg_parser.py: Django """
import json
import logging.config
import os

from django.core.files import File
from django.core.management import BaseCommand, CommandError

__author__ = "Steven Klass"
__date__ = "01/28/2019 11:26"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

from axis.company.models import Company
from simulation.models import Simulation
from simulation.serializers.rem.blg import get_blg_simulation_from_floorplan
from simulation.serializers.simulation.base import SimulationSerializer

log = logging.getLogger(__name__)


class Command(BaseCommand):
    """Run a BLG Parsing and optionally dump out the test data."""

    help = "Generates JSON data for a provided BLG File"
    requires_system_checks = []

    def add_arguments(self, parser):
        """Add our own arguments"""

        parser.add_argument(
            "-f", "--file", help="BLG Input file", action="store", dest="blg_file", type=str
        )

        parser.add_argument(
            "-o",
            "--output",
            help="Output JSON to write to",
            action="store",
            dest="output",
            type=str,
            default="~/Downloads/blg_data.json",
        )

    def handle(self, blg_file: str, output: str, **_kw):
        """Handle it."""

        blg_file = os.path.expanduser(blg_file)
        if not os.path.exists(blg_file):
            raise CommandError("Input BLG File %s does not exist" % os.path.abspath(blg_file))

        output = os.path.expanduser(output)
        if not os.path.exists(os.path.dirname(output)):
            raise CommandError(f"Output Path does not exist {os.path.dirname(output)}")

        with open(blg_file) as fh:
            from analytics.tests.test_api import Floorplan

            floorplan, _cr = Floorplan.objects.get_or_create(
                owner=Company.objects.filter(slug="pivotal-energy-solutions").get(),
                name=os.path.basename(blg_file).split(".")[0],
                remrate_data_file=File(fh, name=os.path.basename(blg_file)),
            )
        with open(output, "w") as f:
            blg_instance = get_blg_simulation_from_floorplan(floorplan)
            simulation_serializer = SimulationSerializer(instance=blg_instance)
            f.write(json.dumps(simulation_serializer.data, indent=4))

        print(f"Output JSON from {blg_file} saved to {output}")

        Floorplan.objects.filter(id=floorplan.id).delete()
        Simulation.objects.filter(id=blg_instance.id).delete()
