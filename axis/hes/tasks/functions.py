"""functions.py - Functions used by multiple tasks that we define here to avoid repetition in code"""

from typing import Tuple
from simulation.enumerations import Orientation
from axis.hes.enumerations import FAILED
from ..models import HESSimulationStatus, HESSimulation
from .exceptions import TaskFailed

__author__ = "Benjamin Stürmer"
__date__ = "10/22/2022 12:07"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Benjamin Stürmer",
]


def get_hes_sim_and_status(
    status_id: int, orientation: Orientation
) -> Tuple[HESSimulation, HESSimulationStatus]:
    simulation_status = HESSimulationStatus.objects.filter(pk=status_id).first()
    if simulation_status is None:
        raise TaskFailed(f"HESSimulationStatus pk {status_id} does not exist")

    hes_simulation = simulation_status.get_hes_simulation(orientation)
    if hes_simulation is None:
        raise TaskFailed(
            f"HESSimulationStatus pk {status_id} does not have an HESSimulation with orientation {orientation}"
        )

    if hes_simulation.status == FAILED:
        raise TaskFailed(
            f"HESSimulation {hes_simulation.pk} has status FAILED. Error is '{hes_simulation.error}'"
        )

    return hes_simulation, simulation_status
