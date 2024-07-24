"""signals.py: Django customer_aps"""


import logging

from django.db.models.signals import post_save

from .utils import update_apshomes

__author__ = "Steven Klass"
__date__ = "1/17/17 11:02"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


def register_signals():
    """Nested to avoid tangling import during initial load."""

    # log.debug("Registering late signals.")

    from axis.home.models import Home

    post_save.connect(
        associate_metersets, sender=Home, dispatch_uid="axis.customer_aps.associate_metersets"
    )


def associate_metersets(sender, instance, created, **kwargs):
    """Update meterset data"""

    if kwargs.get("raw") or not instance.confirmed_address or hasattr(instance, "apshome"):
        return

    log.debug("Called associate_metersets for %s", instance)
    if instance.homestatuses.filter(eep_program__owner__slug="aps").count():
        update_apshomes(lots=[instance])
