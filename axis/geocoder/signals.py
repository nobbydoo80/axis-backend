"""signals.py: Django geocoder"""


import logging

from celery import group
from django.db.models.signals import post_save
from django.utils.timezone import now

from infrastructure.utils import elapsed_time
from .engines import GEOCODER_ENGINE_CHOICES
from .models import GeocodeResponse, Geocode

__author__ = "Steven Klass"
__date__ = "1/17/17 09:51"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


def register_signals():
    """Nested to avoid tangling import during initial load."""

    # log.debug("Registering late signals.")
    post_save.connect(
        initiate_geocodes, sender=Geocode, dispatch_uid="axis.geocoder.signals.initiate_geocodes"
    )


def initiate_geocodes(sender, instance, created, **kwargs):
    if kwargs.get("raw"):
        return

    from axis.geocoder.tasks import get_responses

    # If we want them immediately we need to get each engines answer and not wait on celery
    # This would naturally cause a block to occur
    start = now()
    if instance.immediate:
        results = []
        log.debug(f"Submitting IMMEDIATE geocode task: {start}")
        for engine in GEOCODER_ENGINE_CHOICES:
            get_responses(
                instance.id,
                engine[0],
                raw_address=instance.raw_address,
                entity_type=instance.entity_type,
            )
            result = GeocodeResponse.objects.filter(geocode_id=instance.id)
            results += list(result)

        log.info(
            f"Received {len(results)} geocode results in "
            f"{elapsed_time((now() - start).total_seconds()).long_fmt}"
        )
        return results

    else:
        geocode_task_group = []
        for engine in GEOCODER_ENGINE_CHOICES:
            geocode_task_group.append(
                get_responses.s(
                    instance.id,
                    engine[0],
                    raw_address=instance.raw_address,
                    entity_type=instance.entity_type,
                )
            )

        if not len(geocode_task_group):
            return

        log.debug(f"Submitting geocode task: {start}")

        result = group(geocode_task_group).apply_async()
        return result
