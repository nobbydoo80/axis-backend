"""tasks.py: Django incentive_payment"""


import re

from celery import shared_task
from celery.utils.log import get_task_logger

from django.core.exceptions import ObjectDoesNotExist

__author__ = "Steven Klass"
__date__ = "4/19/13 5:39 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

from axis.customer_neea.utils import NEEA_BPA_SLUGS

logger = get_task_logger(__name__)


@shared_task(ignore_result=True, store_errors_even_if_ignored=True)
def incentive_payment_status_create(home_stat_id):
    """
    Sets the status item for IPP
    """
    from axis.home.models import EEPProgramHomeStatus

    home_stat = EEPProgramHomeStatus.objects.get(id=home_stat_id)
    assert isinstance(home_stat, EEPProgramHomeStatus), "Umm Home Stat?.."

    if home_stat.eep_program.owner.slug == "aps":
        from axis.customer_aps.incentives import create_aps_incentive

        return create_aps_incentive(home_stat)

    if home_stat.eep_program.slug in NEEA_BPA_SLUGS:
        from axis.customer_neea.incentives import create_neea_incentive

        return create_neea_incentive(home_stat)


@shared_task
def catch_missing_incentive_payments():
    """This will catch any (typically sampled homes) that didn't get to IPP"""
    from axis.home.models import EEPProgramHomeStatus

    for stat in EEPProgramHomeStatus.objects.filter_ready_for_incentivepaymentstatus():
        incentive_payment_status_create(stat.id)


@shared_task(default_retry_delay=15, max_retries=3, ignore_result=True)
def incentive_payment_status_update(ipp_stat_id, ipp_state, home_status_id):
    """This will auto advance our state has all requirements"""
    from axis.incentive_payment.models import IncentivePaymentStatus, IPPItem
    from axis.home.models import EEPProgramHomeStatus

    log = logger

    if ipp_state == "complete":
        return

    # log.info('Executing task id {0.id}, args: {0.args!r} kwargs: {0.kwargs!r}'.format(
    #     incentive_payment_status_update.request))

    home_status = EEPProgramHomeStatus.objects.get(id=home_status_id)
    try:
        ipp_stat = IncentivePaymentStatus.objects.get(id=ipp_stat_id)
    except ObjectDoesNotExist as exc:
        try:
            if incentive_payment_status_update.request.retries > 2:
                msg = "IncentivePaymentStatus %s does not yet exist - with count %d > 2"
                log.error(msg, ipp_stat_id, incentive_payment_status_update.request.retries)
        except AttributeError:
            log.warn("IncentivePaymentStatus %s does not yet exist - retrying" % ipp_stat_id)
        incentive_payment_status_update.retry(exc=exc)

    assert isinstance(ipp_stat, IncentivePaymentStatus), "Hmm not a IncentivePaymentStatus"

    ipp_items = IPPItem.objects.filter(home_status=home_status)

    fast_transition_path = [
        ("start", "pending_requirements"),
        ("ipp_payment_requirements", "pending_automatic_requirements"),
        ("ipp_payment_automatic_requirements", "pending_payment_requirements"),
        ("payment_pending", "pending_complete"),
    ]

    # The first two handle the cases where we have existing data..
    try:
        # This is IMPORTANT.  We are tracking the lowest IPP Items State!
        status = min(ipp_items.values_list("incentive_distribution__status", flat=True))
        true_state = "complete" if status > 1 else "payment_pending"
        while ipp_state != true_state:
            stat, transition = next(
                (x for x in fast_transition_path if x[0] == ipp_state), (None, None)
            )
            if transition:
                log.info("Starting next transition %s for %s", transition, ipp_stat)
                ipp_stat.make_transition(transition, user=None)
                ipp_state = ipp_stat.state
    except ValueError:
        pass

    # After this the only transition we need to worry about it is the automatics
    if ipp_state == "ipp_payment_requirements":
        eep_program = home_status.eep_program
        check_method = "ipp_{}_auto_checks".format(re.sub(r"-", "_", eep_program.slug))
        if hasattr(eep_program, check_method):
            check = getattr(eep_program, check_method)
            if check():
                ipp_stat.make_transition("pending_automatic_requirements", user=None)
        else:
            log.info("Starting next transition pending_automatic_requirements for %s", ipp_stat)
            ipp_stat.make_transition("pending_automatic_requirements", user=None)
    return
