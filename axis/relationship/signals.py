"""signals.py: Django relationship"""
__author__ = "Steven Klass"
__date__ = "1/17/17 10:55"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


import logging

from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.dispatch import receiver

from .messages import SponsorPreferencesDoesNotExistMessage
from .models import Relationship, log
from ..messaging.models import Message

log = logging.getLogger(__name__)
customer_hirl_app = apps.get_app_config("customer_hirl")


def register_signals():
    """Nested to avoid tangling import during initial load."""

    # log.debug("Registering late signals.")
    post_save.connect(
        update_stats_for_company_rels,
        sender=Relationship,
        dispatch_uid="axis.relationship.update_stats_for_company_rels",
    )
    post_save.connect(
        update_stats_for_home_rels,
        sender=Relationship,
        dispatch_uid="axis.relationship.update_stats_for_home_sub_rels",
    )


def update_stats_for_company_rels(sender, instance, created, **kwargs):
    """This will update the stats where a program owner is required to have a relationships with vendor"""

    from axis.company.models import COMPANY_MODELS, Company
    from axis.eep_program.models import EEPProgram
    from axis.home.models import EEPProgramHomeStatus
    from axis.home.tasks import update_home_stats, update_home_states

    valid_ctype = (
        instance.content_type in ContentType.objects.get_for_models(*COMPANY_MODELS).values()
    )
    accepted_relationship = instance.is_accepted
    program_owner = EEPProgram.objects.filter(owner=instance.company).count()

    if kwargs.get("raw") or not (valid_ctype and accepted_relationship and program_owner):
        return

    company = Company.objects.get(id=instance.object_id)
    if company.company_type in ["general", "eep", "developer", "architect", "communityowner"]:
        return

    stats = EEPProgramHomeStatus.objects.filter_by_company(company)
    kw = {
        "eep_program__owner": instance.company,
        "eep_program__require_{}_relationship".format(company.company_type): True,
    }
    stats = stats.filter(**kw)

    if stats.count():
        log.debug("Called update_stats_for_company_rels for %s", instance)
        [x.validate_references() for x in stats]
        return (
            update_home_stats.si(eepprogramhomestatus_ids=list(stats.values_list("id", flat=True)))
            | update_home_states.si(
                eepprogramhomestatus_ids=list(stats.values_list("id", flat=True))
            )
        ).delay()


def update_stats_for_home_rels(sender, instance, **kwargs):
    """This will update the stats where a program is required to have a company type"""

    from axis.home.models import Home, EEPProgramHomeStatus
    from axis.subdivision.models import Subdivision
    from axis.home.tasks import update_home_stats, update_home_states

    kwrgs = {"certification_date__isnull": True}
    stats, use_celery = None, False
    if isinstance(instance.content_object, Home):
        kwrgs["home"] = instance.content_object
        stats = instance.content_object.homestatuses
    elif isinstance(instance.content_object, Subdivision):
        kwrgs["home__subdivision"] = instance.content_object
        stats = EEPProgramHomeStatus.objects.filter(home__subdivision=instance.content_object)
        use_celery = True

    invalid_company_type = instance.company.company_type in ["general", "eep"]

    if kwargs.get("raw") or len(kwrgs.keys()) == 1 or invalid_company_type or stats is None:
        return

    kwrgs["eep_program__require_{}_assigned_to_home".format(instance.company.company_type)] = True
    stats = stats.filter(**kwrgs)

    if stats.count():
        log.debug("Called update_stats_for_home_rels for %s", instance)
        if use_celery:
            [x.validate_references(immediate=True) for x in stats]
            return (
                update_home_stats.si(
                    eepprogramhomestatus_ids=list(stats.values_list("id", flat=True))
                )
                | update_home_states.si(
                    eepprogramhomestatus_ids=list(stats.values_list("id", flat=True))
                )
            ).delay()

        update_home_stats(eepprogramhomestatus_ids=list(stats.values_list("id", flat=True)))
        update_home_states(eepprogramhomestatus_ids=list(stats.values_list("id", flat=True)))
        [x.validate_references(immediate=True) for x in stats]


@receiver(post_save, sender=Relationship)
def notify_sponsors_about_new_relationships_without_affiliation(
    sender, instance, created, **kwargs
):
    """
    Send notification for HIRL company when they create relationship with non Affiliated company
    """
    from axis.company.models import Company

    company_ct = ContentType.objects.get(app_label="company", model="company")
    if instance.content_type != company_ct:
        return

    hirl_company = Company.objects.filter(slug=customer_hirl_app.CUSTOMER_SLUG).first()
    if not hirl_company:
        return

    sponsor = instance.company
    sponsored_company = instance.content_object

    if sponsor != hirl_company:
        return

    if not sponsored_company.is_sponsored_by_customer_hirl():
        url = f"/app/sponsor_preferences/create?company_to={sponsored_company.id}"
        SponsorPreferencesDoesNotExistMessage(url=url).send(
            company=sponsor,
            context={
                "sponsored_company": sponsored_company.name,
                "sponsor": sponsor.name,
                "url": url,
            },
        )
