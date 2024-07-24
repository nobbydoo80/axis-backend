"""signals.py: Django customer_neea"""


import logging

from django.db.models.signals import post_save
from django.urls import reverse

from . import messages
from .models import StandardProtocolCalculator
from .utils import NEEA_PROGRAM_SLUGS, send_neea_missing_relationship_message, NEEA_BPA_SLUGS

__author__ = "Steven Klass"
__date__ = "1/17/17 06:43"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


def register_signals():
    """Nested to avoid tangling import during initial load."""

    # log.debug("Registering late signals.")
    dispatch_uid = "axis.customer_neea.notify_raterprovider_of_missing_associations_to_neea"
    from axis.home.models import EEPProgramHomeStatus

    post_save.connect(notify_neea_of_missing_associations, sender=EEPProgramHomeStatus)
    post_save.connect(
        notify_raterprovider_of_missing_associations_to_neea_handler,
        sender=EEPProgramHomeStatus,
        dispatch_uid=dispatch_uid,
    )
    post_save.connect(add_incentive_based_qa, sender=StandardProtocolCalculator)


def notify_neea_of_missing_associations(sender, instance, **kwargs):
    """Notifies NEEA of missing utility companies"""

    if kwargs.get("raw", False):
        return

    if instance.eep_program.slug in NEEA_BPA_SLUGS:
        neea = instance.eep_program.owner
        neea_companies = neea.relationships.get_companies(ids_only=True)

        def _check_company_association(company, company_type_pretty):
            """Verify company associations"""
            if company and company.id not in neea_companies:
                message_context = {
                    "company_type_pretty": company_type_pretty,
                    "company_list_url": reverse(
                        "company:list", kwargs={"type": company.company_type}
                    ),
                    "company": "{}".format(company),
                    "home_url": instance.get_absolute_url(),
                    "home": instance.home.get_addr(),
                    "program": "{}".format(instance.eep_program),
                }
                messages.NEEAMissingAssociationWithCompanyType().send(
                    context=message_context,
                    company=neea,
                )

        home = instance.home
        _check_company_association(home.get_electric_company(), "Electric Utility")
        _check_company_association(home.get_gas_company(), "Gas Utility")


def notify_raterprovider_of_missing_associations_to_neea_handler(
    sender, instance, created, **kwargs
):
    """
    Signal handler is using for convenient mocking while testing
    """
    notify_raterprovider_of_missing_associations_to_neea(
        sender=sender, instance=instance, created=created, **kwargs
    )


def notify_raterprovider_of_missing_associations_to_neea(sender, instance, created, **kwargs):
    """Notifies Rater / Provider of missing utility companies"""

    from axis.company.models import Company

    if instance.eep_program.slug not in NEEA_PROGRAM_SLUGS or kwargs.get("raw", False):
        return

    relationships = instance.home.relationships.filter(
        company__company_type__in=["hvac", "builder", "utility"]
    )
    company_ids = relationships.values_list("company_id", flat=True)

    neea = Company.objects.get(slug="neea")
    neea_companies = Company.objects.filter_by_company(neea).values_list("id", flat=True)

    missing = list(set(company_ids) - set(neea_companies))

    if missing:
        log.debug("Called ensure_hvac_builder_rels for %s", instance)
        for company in Company.objects.filter(id__in=missing):  # pylint: disable=not-an-iterable
            send_neea_missing_relationship_message(instance, company, neea)


def add_incentive_based_qa(sender, instance, created, **kwargs):
    """After we save this update the home relationships with any QA Required Orgs"""

    if kwargs.get("raw", False):
        return

    from axis.relationship.utils import create_or_update_spanning_relationships

    create_or_update_spanning_relationships(None, instance.home_status)
