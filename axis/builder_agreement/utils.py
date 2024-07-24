"""utils.py: Django builder_agreement"""


import logging
from decimal import Decimal

import datetime
from django.utils.text import slugify


__author__ = "Steven Klass"
__date__ = "6/18/12 4:03 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


def increase_builder_agreement_gauge_for_incentive_distribution(incentive_distribution):
    """Given an incentive distribution update the builder agreement gauges."""

    from .models import BuilderAgreement
    from app_metrics.models import Gauge

    for item in incentive_distribution.ippitem_set.all():
        kwargs = {
            "company": incentive_distribution.company,
            "subdivision": item.home_status.home.subdivision,
        }
        if incentive_distribution.company.company_type == "builder":
            kwargs["builder_org"] = incentive_distribution.customer
        else:
            kwargs["builder_org"] = item.home_status.home.get_builder()

        try:
            builder_agreement = BuilderAgreement.objects.get(**kwargs)
        except BuilderAgreement.DoesNotExist:
            log.debug(
                "No Builder Agreement is in place for %s with %s at %s",
                incentive_distribution.customer,
                incentive_distribution.company,
                item.home_status.home.subdivision,
            )
            break

        created_date = datetime.datetime(
            incentive_distribution.paid_date.year,
            incentive_distribution.paid_date.month,
            incentive_distribution.paid_date.day,
        ).replace(tzinfo=datetime.timezone.utc)
        gauge, create = Gauge.objects.get_or_create(
            slug=slugify(
                "Builder Agreement {} {} Payment".format(
                    builder_agreement.id, incentive_distribution.customer.company_type
                )
            ),
            company=incentive_distribution.company,
            defaults={
                "name": "Builder Agreement {} {} Payment".format(
                    builder_agreement, incentive_distribution.customer.company_type.capitalize()
                ),
                "created": created_date,
            },
        )
        gauge.current_value = Decimal(gauge.current_value) + Decimal(item.cost)
        gauge.save()


def setup_builder_agreement_payment_guages(**kwargs):
    """
    Assign all metrics to this.

    Note: If needed this can be regenerated.  It should be about once per month.  Especially if an
    incentive payment was deleted.

    """

    from app_metrics.models import Gauge
    from axis.incentive_payment.models import IncentiveDistribution

    limit = kwargs.get("limit", None)
    current = {}
    if kwargs.get("purge", True):
        log.warning("Purge has been called!")
        guages = Gauge.objects.filter(slug__istartswith=slugify("Builder Agreement"))
        current = dict(list(guages.values_list("slug", "current_value")))
        guages.delete()

    for idx, incentive_distribution in enumerate(
        IncentiveDistribution.objects.filter(status=2).all()
    ):
        if limit and idx >= limit:
            break
        increase_builder_agreement_gauge_for_incentive_distribution(incentive_distribution)

    if kwargs.get("purge", True):
        guages = Gauge.objects.filter(slug__istartswith=slugify("Builder Agreement"))
        for slug, value in list(guages.values_list("slug", "current_value")):
            if current.get(slug) != value:
                log.debug("Updated {}->{} for {}".format(value, current.get(slug), slug))


# Signal relays for other axis to use from the outside.
def update_lots_paid_count(incentive_distribution):
    """Update paid lots count"""
    from . import tasks

    tasks.update_lots_paid_count.delay(incentive_distribution_id=incentive_distribution.id)


def generate_field_annotation_messages(from_user, annotation):
    """
    Sends a messaging notification to the appropriate company based on which area was being
    annotated.
    """
    obj = annotation.content_object

    from .views.examine import BuilderAgreementMachinery

    machineries = (BuilderAgreementMachinery,)

    for machinery in machineries:
        if isinstance(obj, machinery.model):
            machinery = machinery(instance=obj)
            machinery.generate_message(from_user, annotation)
