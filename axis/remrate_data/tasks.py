"""tasks.py: Django remrate_data"""

import datetime

from celery import shared_task
from celery.utils.log import get_task_logger
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.utils.timezone import now
from simple_history.utils import update_change_reason
from simulation.models import get_or_import_rem_simulation

from .models import Building, Simulation

__author__ = "Steven Klass"
__date__ = "2/15/13 3:29 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

logger = get_task_logger(__name__)


@shared_task(time_limit=60 * 3)
def assign_references_and_similar_simulation_models(**kwargs):
    """Simply assigns similar"""

    before_now = now() - datetime.timedelta(minutes=10)
    buildings = Building.objects.filter(sync_status=1, last_update__gte=before_now)

    results = []
    for building in buildings:
        result = building.simulation.assign_references_and_similar()
        if result:
            results.append(result)
        get_or_import_rem_simulation(simulation_id=building.simulation.id, countdown=60)
    return results if len(results) else "No assignments over."


@shared_task(time_limit=60 * 60)
def prune_failed_simulation_models(min_lookback_days=7, max_lookback_days=45, **kwargs):
    """This looks towards each simulation and if it failed and is unused get rid of it."""
    last_update_gte = now() - datetime.timedelta(days=max_lookback_days)
    last_update_lt = now() - datetime.timedelta(days=min_lookback_days)

    simulations = Simulation.objects.filter(
        Q(building__isnull=True)
        | Q(building__last_update__gte=last_update_gte, building__last_update__lt=last_update_lt),
        Q(floorplan__isnull=True)
        | Q(floorplan__active_for_homestatuses__isnull=True)
        | Q(floorplan__homestatuses__isnull=True),
    )

    logger.debug(f"Found {simulations.count()} simulations to review")
    to_be_deleted = []
    for simulation in simulations:
        errors = simulation.get_validation_errors()
        if errors:
            logger.debug(
                f"Simulation {simulation.pk} has {len(errors)} validation errors, will delete if unused"
            )
            deletion_ids = [simulation.id]
            try:
                # Did the user do more than simply accept defaults
                if (
                    simulation.floorplan.remrate_data_file
                    or simulation.floorplan.customer_documents
                    or simulation.floorplan.comment
                ):
                    logger.debug(
                        f"Will not delete Simulation {simulation.pk} - it has a floorplan with remrate_data_file, customer_documents or comment"
                    )
                    continue
            except ObjectDoesNotExist:
                pass

            try:
                if simulation.floorplan.active_for_homestatuses.count():
                    logger.debug(
                        f"Will not delete Simulation {simulation.pk} - it has simulation.floorplan.active_for_homestatuses"
                    )
                    continue
            except ObjectDoesNotExist:
                pass

            try:
                if simulation.floorplan.homestatuses.count():
                    logger.debug(
                        f"Will not delete Simulation {simulation.pk} - it has simulation.floorplan.homestatuses"
                    )
                    continue
            except ObjectDoesNotExist:
                pass

            used = False
            # Are there references and if so are any of them used.
            refs = list(simulation.references.all()) + list(simulation.base_building.all())
            if len(refs):
                ref_ids = [ref.id for ref in refs]
                logger.debug(
                    f"Simulation {simulation.pk} has references to ({', '.join(map(str, ref_ids))}), checking whether they are used as well"
                )
            for ref in refs:
                deletion_ids.append(ref.id)

                try:
                    if ref.floorplan.active_for_homestatuses.count():
                        logger.debug(
                            f"Simulation {simulation.pk} won't be deleted - ref {ref.id} has floorplan.active_for_homestatuses"
                        )
                        used = True
                        break
                except ObjectDoesNotExist:
                    pass

                try:
                    if ref.floorplan.homestatuses.count():
                        logger.debug(
                            f"Simulation {simulation.pk} won't be deleted - ref {ref.id} has floorplan.homestatuses"
                        )
                        used = True
                        break
                except ObjectDoesNotExist:
                    pass

            if not used:
                logger.debug(
                    f"Adding ({', '.join(map(str, deletion_ids))} to set of IDs to be deleted"
                )
                to_be_deleted += deletion_ids

    to_be_deleted = sorted(list(set(to_be_deleted)))

    if not to_be_deleted:
        logger.debug("Nothing to be done.")
        return "Nothing to be done."

    if kwargs.get("return_ids"):
        logger.debug("return_ids is set, so we will not actually delete any Simulations")
        return to_be_deleted

    for sim in Simulation.objects.filter(id__in=to_be_deleted).all():
        sim.delete()
        update_change_reason(sim, "axis.remrate_data.tasks.prune_failed_simulation_models")

    return f"Removed {len(to_be_deleted)}/{simulations.count()} simulations between {last_update_gte} - {last_update_lt}"
