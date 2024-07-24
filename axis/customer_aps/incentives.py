"""incentives.py: Django customer_aps"""


import datetime
import logging

from axis.incentive_payment.models import IncentivePaymentStatus

__author__ = "Steven Klass"
__date__ = "4/14/14 2:47 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


def create_aps_incentive(home_status):
    """Creates the APS Incentive if there is something to be paid"""

    from axis.home.models import EEPProgramHomeStatus

    company = home_status.eep_program.owner

    incentive_cost = home_status.get_total_incentive()

    if not home_status.certification_date:
        log.info("Skipping un-certified home")
        return
    if incentive_cost < 0.01:
        log.info("Skipping IPP no money..")
        return

    if home_status not in EEPProgramHomeStatus.objects.filter_ready_for_incentivepaymentstatus():
        log.info("We should definately be there by this point..")
        return

    if hasattr(home_status.home, "apshome") and home_status.home.apshome is not None:
        from axis.customer_aps.models import LegacyAPSHome

        if LegacyAPSHome.objects.filter(aps_id=home_status.home.apshome.aps_id).all().count():
            log.info("Skipping legacy Payment %s", home_status.home.apshome.aps_id)
            return

    # Finally add the IPP Status
    created_datetime = datetime.datetime.combine(
        home_status.certification_date, datetime.time()
    ).replace(tzinfo=datetime.timezone.utc)

    ipp_stat, create = IncentivePaymentStatus.objects.get_or_create(
        home_status=home_status, defaults=dict(owner=company, created_on=created_datetime)
    )
    msg = "{} IPP Status item".format("Created" if create else "Using existing")
    log.info(msg)
    return msg


def get_builder_incentive(home_status):
    """Get the real builder incentive"""
    from axis.customer_aps.aps_calculator.calculator import APSCalculator
    from axis.customer_aps.aps_calculator.base import APSInputException

    try:
        calc = APSCalculator(home_status_id=home_status.id)
        return calc.incentives.builder_incentive
    except APSInputException:
        return home_status.eep_program.builder_incentive_dollar_value


def get_rater_incentive(home_status):
    """Get the rater incentive"""
    from axis.customer_aps.aps_calculator.calculator import APSCalculator
    from axis.customer_aps.aps_calculator.base import APSInputException

    try:
        calc = APSCalculator(home_status_id=home_status.id)
        return calc.incentives.rater_incentive
    except APSInputException:
        return home_status.eep_program.rater_incentive_dollar_value


def get_total_incentive(home_status):
    """Get the total incentive"""
    from axis.customer_aps.aps_calculator.calculator import APSCalculator
    from axis.customer_aps.aps_calculator.base import APSInputException

    try:
        calc = APSCalculator(home_status_id=home_status.id)
        return calc.incentives.total_incentive
    except APSInputException:
        return (
            home_status.eep_program.builder_incentive_dollar_value
            + home_status.eep_program.rater_incentive_dollar_value
        )
