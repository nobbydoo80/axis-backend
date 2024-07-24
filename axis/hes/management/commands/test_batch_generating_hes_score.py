from django.core.management import BaseCommand

from axis.hes.enumerations import COMPLETE
from axis.hes.models import HESCredentials
from axis.home.models import EEPProgramHomeStatus
from simulation.enumerations import Orientation
from simulation.models import Simulation
from ...functions.trigger_generation_task_for_home_status import _get_hes_sim_status
from ...tasks import submit_hpxml_inputs, generate_label, get_results

__author__ = "Benjamin Stürmer"
__date__ = "11/23/2022 17:41"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Benjamin Stürmer",
]


class Command(BaseCommand):
    help = """A method developed to support testing Home Energy Score generation. It will generate a large number of
    HES scores and report out how many were successful and what errors occurred.

    WARNING: This is NOT meant to be run in a production environment!!!"""
    requires_system_checks = []

    def add_arguments(self, parser):
        parser.add_argument(
            "--num-scores-to-generate",
            dest="num_scores_to_generate",
            type=int,
            help="How many scores to run",
            required=True,
        )
        parser.add_argument(
            "--hes_api_username", action="store", dest="hes_api_username", type=str, required=True
        )
        parser.add_argument(
            "--num-scores-to-skip",
            dest="num_scores_to_skip",
            nargs="?",
            default=0,
            type=int,
            help="An offset so that we can, say, run it for batches of 100 scores at a time",
            required=False,
        )

    def handle(
        self, num_scores_to_generate: int, hes_api_username: str, num_scores_to_skip: int, **kwargs
    ):
        home_statuses = EEPProgramHomeStatus.objects.filter(floorplan__simulation__isnull=False)[
            num_scores_to_skip : num_scores_to_skip + num_scores_to_generate
        ]

        hes_credential_id = HESCredentials.objects.values_list("id", flat=True).get(
            username=hes_api_username
        )
        if hes_credential_id is None:
            raise Exception(f"No HES credential found with username {hes_api_username}")
        self._write_out(
            f"Processing {home_statuses.count()} EEPProgramHomeStatuses with credential {hes_api_username}"
        )

        count_total = 0
        count_success = 0
        count_error = 0
        for home_status in home_statuses:
            count_total += 1
            self._write_out(
                f"Working on EEPProgramHomeStatus ({home_status.id}) (simulation {home_status.floorplan.simulation_id}) - {home_status} ({count_total})"
            )
            try:
                statuses = home_status.hes_score_statuses
                if statuses.count() and statuses.first().status == COMPLETE:
                    self._write_out("Skipping generation - already has status COMPLETE")
                else:
                    self._generate_home_status(home_status, hes_credential_id)
                count_success += 1
                self._write_out("Success!")
            except Exception as e:
                count_error += 1
                self._write_out(f"Failed! {e}")
            self._write_out(
                f"Done ({home_status.id}) - {home_status} Successes: {count_success}, Errors: {count_error} \n"
            )
            self._write_out("")

    def _generate_home_status(self, home_status: EEPProgramHomeStatus, hes_api_credential_id: int):
        """This function is derived from trigger_generation_task_for_home_status(), which I rewrote here as
        a synchronous function because of errors I was getting trying to get RabbitMQ to work in a command
        """
        sim_id = home_status.floorplan.simulation_id

        hes_sim_status, is_sim_status_new = _get_hes_sim_status(home_status, sim_id)
        self._write_out(
            f"{'Creating' if is_sim_status_new else 'Updating'} Simulation Status {hes_sim_status.id}"
        )

        self._submit_hpxml(
            hes_sim_status_id=hes_sim_status.pk,
            hes_api_credential_id=hes_api_credential_id,
            orientation=self.get_orientation(home_status.floorplan.simulation),
        )

        return hes_sim_status, is_sim_status_new

    @staticmethod
    def get_orientation(sim: Simulation):
        """Use the windows (the walls don't provide us any orientation information) to figure out what orientations
        are possible for the home. We need this because otherwise we get into trouble with townhomes - we have to
        point the front of the house in a direction such that the windows aren't on an inside wall.
        """
        windows = {w.orientation: w for w in sim.windows.all()}
        first_side = sim.windows.first().orientation
        related_orientations = Orientation(first_side).get_related()
        for i, side in enumerate(related_orientations):
            if not windows.get(side):
                try:
                    return related_orientations[i - 1]
                except KeyError:
                    return related_orientations[i + 1]
        return first_side

    def _submit_hpxml(
        self, hes_sim_status_id: int, hes_api_credential_id: int, orientation: Orientation
    ):
        submit_hpxml_inputs(hes_sim_status_id, hes_api_credential_id, orientation)
        generate_label(hes_sim_status_id, hes_api_credential_id, orientation)
        get_results(hes_sim_status_id, hes_api_credential_id, orientation)

    def _write_out(self, msg):
        self.stdout.write(msg, ending="\n")
