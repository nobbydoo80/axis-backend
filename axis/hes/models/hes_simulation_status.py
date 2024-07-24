import logging
from functools import cached_property

from django.db.models import (
    ForeignKey,
    OneToOneField,
    DateTimeField,
    Model,
    CASCADE,
    SET_NULL,
)
from simple_history.models import HistoricalRecords
from simulation.enumerations import Orientation
from axis.home.models import EEPProgramHomeStatus
from ..managers import HESQuerySet
from ..enumerations import FAILED, NEW, ACTIVE, REPORTED, COMPLETE, IN_PROGRESS
from .hes_simulation import HESSimulation

__author__ = "Steven K"
__date__ = "11/12/2019 09:05"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

log = logging.getLogger(__name__)


class HESSimulationStatus(Model):
    """An HESSimulationStatus links together the set of all HES simulations that have been
    run for a home. This is necessary because, in general, we simulate the same home with
    the orientation set to each of the four cardinal directions in order to determine the
    worst case, as we don't always have home orientations in our data."""

    home_status = ForeignKey(
        "home.EEPProgramHomeStatus",
        on_delete=CASCADE,
        related_name="hes_score_statuses",
        blank=True,
        null=True,
    )

    simulation = ForeignKey(
        "simulation.Simulation", on_delete=CASCADE, related_name="hes_score_statuses", null=True
    )

    # The HESSimulation that got the worst score among those that were submitted for each orientation
    worst_case_simulation = OneToOneField(
        "hes.HESSimulation",
        related_name="worst_case_status",
        blank=True,
        null=True,
        on_delete=SET_NULL,
    )

    updated_at = DateTimeField(auto_now=True, editable=False)
    created_at = DateTimeField(auto_now_add=True, editable=False)

    # @deprecated
    # The rem_simulation field is kept in this model only to support old instances from before we
    # transitioned to using simulation.Simulation
    rem_simulation = ForeignKey(
        "remrate_data.simulation",
        on_delete=CASCADE,
        related_name="hes_score_statuses",
        blank=True,
        null=True,
    )

    history = HistoricalRecords()
    objects = HESQuerySet.as_manager()

    class Meta:
        verbose_name = "HES Simulation"

    def __str__(self):
        return f"HES Simulation <{self.pk}> for company <{self.company}>"

    @property
    def status(self) -> str:
        statuses = [o.status for o in self.hes_simulations.all()]

        # If we haven't actually created any simulation statuses yet, then we are in state NEW because nothing
        # could possibly have been run yet.
        if len(statuses) == 0:
            return NEW

        # If any of the simulations has an error, the overall status is FAILED
        if FAILED in statuses:
            return FAILED

        # If all the simulations have status NEW, that's the overall status as well
        if all([s == NEW for s in statuses]):
            return NEW

        # If all the simulations have been run, then the status is complete
        if all([s in [REPORTED, ACTIVE] for s in statuses]):
            return COMPLETE

        # Otherwise, at least one of the simulations must still be running
        return IN_PROGRESS

    @property
    def is_certified(self) -> bool:
        return self.home_status.state == EEPProgramHomeStatus.COMPLETE_STATE

    @property
    def building_id(self) -> str | None:
        """Get the Home Energy Score API's building_id for the orientation that had the worst score"""
        if self.worst_case_simulation is None:
            return None
        return self.worst_case_simulation.building_id

    @cached_property
    def company(self) -> str:
        return self.home_status.company

    @cached_property
    def worst_case_orientation(self) -> Orientation | None:
        return self.worst_case_simulation.orientation if self.worst_case_simulation else None

    def get_hes_simulation(self, orientation: Orientation) -> HESSimulation | None:
        return self.hes_simulations.filter(orientation=orientation).first()
