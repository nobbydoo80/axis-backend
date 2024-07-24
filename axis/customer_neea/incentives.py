"""incentives.py: Django customer_neea"""


import logging
import datetime

from django.apps import apps

from axis.incentive_payment.models import IncentivePaymentStatus

__author__ = "Steven Klass"
__date__ = "12/28/17 1:46 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)
customer_neea_app = apps.get_app_config("customer_neea")


def create_neea_incentive(home_status):
    """Creates the NEEA Incentive if there is something to be paid"""

    if not home_status.certification_date:
        log.info("Skipping un-certified home")
        return

    if home_status.state != "complete":
        log.info("Skipping incomplete home")
        return

    company = home_status.get_electric_company()
    if not company:
        log.info("No utility found")
        return

    incentive_cost = home_status.get_builder_incentive()

    if incentive_cost < 0.01:
        log.info("Skipping IPP no money..")
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
    from axis.customer_neea.models import StandardProtocolCalculator

    company = home_status.get_electric_company()
    if not company:
        log.info("No utility found")
        return 0.0

    if company.slug not in customer_neea_app.NEEA_SP_INCENTIVE_UTILITY_SLUGS:
        log.info("%s is not currently paying incentives", company)
        return 0.0

    data = StandardProtocolCalculator.objects.get(home_status=home_status).as_dict()
    return data["builder_incentive"]


def get_rater_incentive(home_status):
    """Get the rater incentive"""
    return 0.0


def get_total_incentive(home_status):
    """Get the total incentive"""
    from axis.customer_neea.models import StandardProtocolCalculator

    company = home_status.get_electric_company()
    if not company:
        log.info("No utility found")
        return 0.0

    if company.slug not in customer_neea_app.NEEA_SP_INCENTIVE_UTILITY_SLUGS:
        log.info("%s is not currently paying incentives", company)
        return 0.0

    data = StandardProtocolCalculator.objects.get(home_status=home_status).as_dict()
    return data["total_incentive"]
