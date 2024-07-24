"""signals.py: Django incentive_payment"""


import logging

from django.conf import settings
from django.db.models.signals import post_save

from .models import IncentivePaymentStatus, IncentiveDistribution
from .tasks import incentive_payment_status_create, incentive_payment_status_update

__author__ = "Steven Klass"
__date__ = "1/17/17 10:26"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


def register_signals():
    """Nested to avoid tangling import during initial load."""

    # log.debug("Registering late signals.")

    post_save.connect(
        incentive_payment_status_update_handler,
        sender=IncentivePaymentStatus,
        dispatch_uid="axis.incentive_payment.incentive_payment_status",
    )
    post_save.connect(incentive_distribution_status_update_handler, sender=IncentiveDistribution)

    from axis.home.signals import eep_program_certified
    from axis.home.models import EEPProgramHomeStatus

    eep_program_certified.connect(
        incentive_payment_status_create_handler, sender=EEPProgramHomeStatus
    )

    post_save.connect(handler__update_lots_paid_count, sender=IncentiveDistribution)


def incentive_payment_status_create_handler(instance, **kwargs):
    if not kwargs.get("raw"):
        incentive_payment_status_create.delay(home_stat_id=instance.id)


def incentive_payment_status_update_handler(instance, **kwargs):
    if not kwargs.get("raw"):
        incentive_payment_status_update.delay(
            ipp_stat_id=instance.id,
            ipp_state=instance.state,
            home_status_id=instance.home_status.id,
        )


def incentive_distribution_status_update_handler(instance, **kwargs):
    if not kwargs.get("raw"):
        for ipp_item in instance.ippitem_set.all():
            instance = ipp_item.home_status.incentivepaymentstatus
            incentive_payment_status_update.delay(
                ipp_stat_id=instance.id,
                ipp_state=instance.state,
                home_status_id=instance.home_status.id,
            )


def handler__update_lots_paid_count(sender, instance, **kwargs):
    if not kwargs.get("raw"):
        from axis.builder_agreement.tasks import update_lots_paid_count

        update_lots_paid_count.delay(incentive_distribution_id=instance.id)
