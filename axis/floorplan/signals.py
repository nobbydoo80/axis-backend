"""signals.py: Django floorplan"""


import logging

from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save
from simulation.models import get_or_import_rem_simulation, get_or_import_ekotrope_simulation

from axis.floorplan.models import Floorplan
from axis.relationship.utils import create_or_update_spanning_relationships

__author__ = "Steven Klass"
__date__ = "1/17/17 09:42"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


def register_signals():
    """Nested to avoid tangling import during initial load."""
    # log.debug("Registering late signals.")
    post_save.connect(floorplan_relationship_create, sender=Floorplan)
    post_save.connect(floorplan_simulation_sync, sender=Floorplan)


def floorplan_relationship_create(sender, instance, created, raw, **kwargs):
    """Add a relationship to the owner on create"""
    if raw:
        return

    if instance and instance.owner:
        create_or_update_spanning_relationships(instance.owner, instance)


def floorplan_simulation_sync(sender, instance, created, raw, **kwargs):
    if raw:
        return

    official = None
    msg = "%(type)s simulation %(legacy_id)s assigned %(sim_id)s on floorplan %(floorplan)s"
    kw = {"type": "N/A", "legacy_id": None, "floorplan": instance.id, "sim_id": None}
    if instance.remrate_target:
        try:
            official = instance.remrate_target.simulation_seeds.get().simulation
            kw.update(
                {
                    "legacy_id": instance.remrate_target.id,
                    "type": "Existing Rem",
                    "sim_id": official.id,
                }
            )
        except (ObjectDoesNotExist, AttributeError):
            pass
    elif instance.ekotrope_houseplan:
        try:
            official = instance.ekotrope_houseplan.project.simulation_seeds.get().simulation
            kw.update(
                {
                    "legacy_id": instance.ekotrope_houseplan.id,
                    "type": "Existing Ekotrope",
                    "sim_id": official.id,
                }
            )
        except (ObjectDoesNotExist, AttributeError):
            pass

    try:
        simulation = instance.simulation
    except AttributeError:
        simulation = None

    if simulation and official == simulation:
        return

    if instance.remrate_target:
        if official is None:
            official = get_or_import_rem_simulation(
                simulation_id=instance.remrate_target.id, use_tasks=False
            )
            kw.update(
                {
                    "legacy_id": instance.remrate_target.id,
                    "type": "Imported Rem",
                    "sim_id": official.id if official else "-",
                }
            )
    elif instance.ekotrope_houseplan:
        if official is None:
            official = get_or_import_ekotrope_simulation(
                houseplan_id=instance.ekotrope_houseplan.id, use_tasks=False
            )
            kw.update(
                {
                    "legacy_id": instance.ekotrope_houseplan.id,
                    "type": "Imported Ekotrope",
                    "sim_id": official.id if official else "-",
                }
            )
    if official is not None:
        # The act of convert_seed should update this for us
        instance = Floorplan.objects.get(id=instance.id)
        if not instance.simulation:
            msg = "Unable to get simulation converted on Floorplan ID: %d" % instance.id
            try:
                real = Floorplan.objects.get(simulation=official)
                msg += " conflicts with FP: %d - conflicting=%r" % (real.id, [instance.id, real.id])
                # NOTE:  When we find ourselves here it's best to reconvert both offenders
                # To do this we need to do the following:
                #   from simulation.models import Seed
                #   conflicting = [ instance.id, real.id ]
                #   fps = Floorplan.objects.filter(id__in=conflicting)
                #   source_ids = fps.values_list('simulation__source', flat=True)
                #   Seed.objects.filter(id__in=source_ids).delete()
                #   fps.update(simulation=None)
                #   for fp in fps: fp.save()
            except ObjectDoesNotExist:
                Floorplan.objects.filter(id=instance.id).update(simulation=official)
                return
            # Note this happens when you can't assign simulation b/c it's already assigned.
            log.error(msg)
            return
        log.info(msg, kw)
        instance.validate_references()
    # Note we don't care if simulation exists and no remrate / ekotrope.  That is the path forward.
