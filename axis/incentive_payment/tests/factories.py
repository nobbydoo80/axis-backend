"""factories.py: Django incentive_payment"""


import logging
import re

from django.utils.timezone import now

from axis.core.utils import random_sequence
from axis.company.tests.factories import builder_organization_factory, eep_organization_factory
from axis.home.tests.factories import certified_custom_home_with_basic_eep_factory
from axis.incentive_payment.tasks import incentive_payment_status_update
from ..models import IncentiveDistribution, IPPItem, IncentivePaymentStatus

__author__ = "Steven Klass"
__date__ = "4/19/13 6:22 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


def basic_incentive_payment_status_factory(**kwargs):
    """A incentive payment status factory.  get_or_create based on the field 'username'."""
    home_status = kwargs.pop("home_status", None)
    owner = kwargs.pop("owner", None)

    kwrgs = {}
    if not home_status:
        c_kwrgs = {
            "eep_program__builder_incentive_dollar_value": 100,
        }
        for k, v in list(kwargs.items()):
            if k.startswith("home_status__"):
                c_kwrgs[re.sub(r"home_status__", "", k)] = kwargs.pop(k)
        kwrgs["home_status"] = certified_custom_home_with_basic_eep_factory(**c_kwrgs)
    else:
        kwrgs["home_status"] = home_status

    if not owner:
        if home_status:
            kwrgs["owner"] = home_status.company
        else:
            kwrgs["owner"] = kwrgs["home_status"].company
    else:
        kwrgs["owner"] = owner
    kwrgs.update(kwargs)

    return IncentivePaymentStatus.objects.get_or_create(
        home_status=kwrgs.pop("home_status"), defaults=kwrgs
    )[0]


def basic_incentive_payment_item(**kwargs):
    """A IPP Items factory.  get_or_create based on the field 'lot_number'."""
    home_status = kwargs.pop("home_status", None)
    incentive_distribution = kwargs.pop("incentive_distribution", None)

    kwrgs = {"cost": 1.00}
    if not home_status:
        c_kwrgs = {}
        for k, v in list(kwargs.items()):
            if k.startswith("home_status__"):
                c_kwrgs[k] = kwargs.pop(k)
        ipp_stat = basic_incentive_payment_status_factory(**c_kwrgs)
        kwrgs["home_status"] = ipp_stat.home_status
    else:
        kwrgs["home_status"] = home_status

    if not incentive_distribution:
        raise NotImplemented("Start with the incentive distribution")
    else:
        kwrgs["incentive_distribution"] = incentive_distribution

    kwrgs.update(kwargs)
    return IPPItem.objects.get_or_create(**kwrgs)[0]


def basic_pending_builder_incentive_distribution_factory(**kwargs):
    """An incentive distribution factory.  get_or_create based on the field 'lot_number'."""
    company = kwargs.pop("company", None)
    customer = kwargs.pop("customer", None)
    rater = kwargs.pop("rater", None)

    ipp_items = kwargs.pop("ipp_items", None)
    ipp_count = kwargs.pop("ipp_count", 1)
    ipp_item_cost = kwargs.pop("ipp_item_cost", 1000.00)

    kwrgs = {
        "check_to_name": random_sequence(4),
        "check_requested": True,
        "check_requested_date": now(),
        "status": 1,
        "comment": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
    }

    if customer is None:
        c_kwrgs = {}
        for k, v in list(kwargs.items()):
            if k.startswith("customer__"):
                c_kwrgs[re.sub(r"customer__", "", k)] = kwargs.pop(k)
        kwrgs["customer"] = builder_organization_factory(**c_kwrgs)
    else:
        kwrgs["customer"] = customer

    if company is None:
        c_kwrgs = {}
        for k, v in list(kwargs.items()):
            if k.startswith("company__"):
                c_kwrgs[re.sub(r"company__", "", k)] = kwargs.pop(k)
        kwrgs["company"] = eep_organization_factory(**c_kwrgs)
    else:
        kwrgs["company"] = company

    kwrgs.update(kwargs)

    incentive_distribution, create = IncentiveDistribution.objects.get_or_create(**kwrgs)

    if create:
        if ipp_items is None and kwrgs["customer"]:
            ipp_items = []
            while len(ipp_items) < ipp_count:
                _ipp_kwrgs = {
                    "cost": ipp_item_cost,
                    "incentive_distribution": incentive_distribution,
                    "home_status__home__builder_org": kwrgs["customer"],
                    "home_status__eep_program__builder_incentive_dollar_value": ipp_item_cost,
                    "home_status__eep_program__owner": kwrgs["company"],
                    "home_status__eep_program__no_close_dates": True,
                }
                if rater is not None:
                    _ipp_kwrgs["home_status__company"] = rater
                ipp_items.append(basic_incentive_payment_item(**_ipp_kwrgs))
            for ipp in ipp_items:
                incentive_payment_status_update(
                    ipp.home_status.incentivepaymentstatus.id,
                    ipp.home_status.incentivepaymentstatus.state,
                    ipp.home_status.id,
                )

        incentive_distribution.total = incentive_distribution.total_cost()
    return incentive_distribution
