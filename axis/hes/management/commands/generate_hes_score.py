import logging

from django.core.management import BaseCommand

from axis.hes.models import HESCredentials
from axis.home.models import EEPProgramHomeStatus
from ...functions import trigger_generation_task_for_home_status

__author__ = "Steven K"
__date__ = "11/24/2019 09:11"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Generate a Home Energy Score"
    requires_system_checks = []

    def add_arguments(self, parser):
        """Add our Arguments"""
        parser.add_argument(
            "-HS",
            "--home-status",
            dest="home_status_ids",
            nargs="+",
            type=int,
            help="Project (Home Status) ID",
            required=True,
        )
        parser.add_argument(
            "--credential_id", action="store", dest="credential_id", type=int, required=False
        )

    def handle(self, *args, **options):
        home_status_ids = options["home_status_ids"]
        if not isinstance(home_status_ids, list):
            home_status_ids = [home_status_ids]

        for home_status_id in home_status_ids:
            home_status = EEPProgramHomeStatus.objects.get(id=home_status_id)
            self._write_out(f"Working on Project ({home_status.id}) - {home_status}")

            credential_id = options.get("credential_id")
            if credential_id:
                hes_api_credentials = HESCredentials.objects.get(id=credential_id)
            else:
                hes_api_credentials = HESCredentials.objects.filter(
                    company=home_status.company
                ).first()
            self._write_out(f" - Using HES API credentials {hes_api_credentials}")

            task, hes_sim_status, is_sim_status_new = trigger_generation_task_for_home_status(
                home_status=home_status,
                hes_api_credentials=hes_api_credentials,
            )

            self._write_out(
                f" - HESSimulationStatus {hes_sim_status.id}: Task has been created {task.id}"
            )

    def _write_out(self, msg):
        self.stdout.write(msg, ending="\n")
