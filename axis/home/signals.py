"""signals.py: Django home"""


import logging

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, post_delete
from django.dispatch import Signal
from django.utils import formats

from axis.customer_neea.utils import NEEA_BPA_SLUGS
from axis.home.messages import (
    HomeCertifiedMessage,
    NEEABPAHomeCertifiedRaterMessage,
    NEEABPAHomeCertifiedUtilityMessage,
)
from axis.home.models import Home, EEPProgramHomeStatus
from axis.home.tasks import update_home_stats, update_home_states

User = get_user_model()

__author__ = "Steven Klass"
__date__ = "4/16/13 9:00 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


eep_program_certified = Signal()


def register_signals():
    """Nested to avoid tangling import during initial load."""

    # log.debug("Registering late signals.")
    post_save.connect(update_states_for_home, sender=Home)
    post_save.connect(eep_program_home_status_post_save, sender=EEPProgramHomeStatus)
    eep_program_certified.connect(
        incentive_payment_status_create_handler, sender=EEPProgramHomeStatus
    )

    from axis.checklist.models import CollectedInput, Answer, QAAnswer

    post_save.connect(update_stats_on_answer, sender=CollectedInput)
    post_delete.connect(update_stats_on_answer, sender=CollectedInput)
    post_save.connect(update_stats_on_answer, sender=Answer)
    post_delete.connect(update_stats_on_answer, sender=Answer)
    post_save.connect(update_stats_on_answer, sender=QAAnswer)
    post_delete.connect(update_stats_on_answer, sender=QAAnswer)


def update_stats_on_answer(sender, instance, **kwargs):
    if kwargs.get("raw"):
        return

    # Provide switching capability here so this method continues to be in play
    # in all the places it was added already.
    if not hasattr(instance, "collection_request"):
        legacy_update_stats_on_answer(sender, instance, **kwargs)
        return

    if not instance.home_status_id or instance.home_status.certification_date:
        return

    try:
        log.debug("Called update_stats_on_answer for %s [%s]", instance, instance.id)
        update_home_stats(eepprogramhomestatus_ids=[instance.home_status_id])
        update_home_states(
            eepprogramhomestatus_ids=[instance.home_status_id], user_id=instance.user_id
        )
        instance.home_status.validate_references()
    except Exception as _err:
        log.exception(f"Problem updating input-collection stats - {_err}")
    return


def legacy_update_stats_on_answer(sender, instance, **kwargs):
    if not all([instance.home_id, instance.question_id, instance.user_id]) or kwargs.get(
        "raw", False
    ):
        return

    kwgs = {
        "certification_date__isnull": True,
        "eep_program__required_checklists__questions": instance.question,
        "home_id": instance.home_id,
        "company_id": instance.user.company_id,
    }

    stats = EEPProgramHomeStatus.objects.filter(**kwgs)

    user_id = instance.user.id if instance.user else None
    if stats.count():
        log.debug("Called update_stats_on_answer for %s [%s]", instance, instance.id)
        update_home_stats(eepprogramhomestatus_ids=list(stats.values_list("id", flat=True)))
        update_home_states(
            eepprogramhomestatus_ids=list(stats.values_list("id", flat=True)), user_id=user_id
        )
    [stat.validate_references() for stat in stats]


def eep_program_home_status_post_save(sender, instance, created, **kwargs):
    pass


def update_states_for_home(sender, instance, created, **kwargs):
    stats = instance.homestatuses.filter(certification_date__isnull=True)
    stat_ids = stats.values_list("id", flat=True)

    if not stats.count() or kwargs.get("raw", False):
        return

    log.debug("Called update_states_for_home for %s [%s]", instance, instance.id)
    update_home_stats(eepprogramhomestatus_ids=list(stat_ids))
    update_home_states(eepprogramhomestatus_ids=list(stat_ids))

    [stat.validate_references() for stat in stats]


def incentive_payment_status_create_handler(instance, **kwargs):
    from axis.company.models import Company

    home = instance.home
    try:
        user = kwargs.get("user")
        certifying_company = user.company
    except AttributeError:
        certifying_company = None

    if certifying_company and certifying_company != instance.company:
        cert_type = (
            "Certified" if instance.eep_program.slug != "neea-efficient-homes" else "Completed"
        )
        try:
            subdivision_url = home.subdivision.get_absolute_url()
            project_name = f"<a href='{home.get_absolute_url()}'>{home}</a> of <a href='{subdivision_url}'>{home.subdivision}</a>"

        except AttributeError:
            project_name = f"<a href='{home.get_absolute_url()}'>{home}</a>"

        context = {
            "home_url": home.get_absolute_url(),
            "project_name": project_name,
            "certifying_company": "{}".format(certifying_company),
            "certification_type": cert_type,
            "certification_date": formats.date_format(
                instance.certification_date, "SHORT_DATE_FORMAT"
            ),
        }
        if instance.eep_program.slug in NEEA_BPA_SLUGS:
            receiving_companies = filter(
                None,
                [instance.company, instance.get_electric_company(), instance.get_gas_company()],
            )
            context["program"] = str(instance.eep_program)
            for company in receiving_companies:
                if company.company_type == "rater":
                    msg = NEEABPAHomeCertifiedRaterMessage
                else:
                    msg = NEEABPAHomeCertifiedUtilityMessage
                msg(url=context["home_url"]).send(
                    company=company,
                    context=context,
                )
        else:
            receiving_companies_ids = filter(
                None,
                instance.home.relationships.filter(
                    company__company_type__in=[
                        Company.BUILDER_COMPANY_TYPE,
                        Company.RATER_COMPANY_TYPE,
                        Company.PROVIDER_COMPANY_TYPE,
                        Company.ARCHITECT_COMPANY_TYPE,
                        Company.DEVELOPER_COMPANY_TYPE,
                        Company.COMMUNITY_OWNER_COMPANY_TYPE,
                    ]
                ).values_list("company", flat=True),
            )
            receiving_companies = Company.objects.filter(id__in=receiving_companies_ids)
            for company in receiving_companies:
                HomeCertifiedMessage(url=context["home_url"]).send(
                    company=company,
                    context=context,
                )
