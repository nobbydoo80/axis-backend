"""signals.py: Django customer_eto"""


import logging

from django.urls import reverse
from django.db.models.signals import post_save

from axis.company.models import Company
from axis.customer_eto import strings
from axis.customer_eto.messages import (
    NewETOAccountMessage,
    HomeInspectedMessage,
    ETOAccountNumberAddedSingleMessage,
    ETOAccountNumberAddedMultipleMessage,
)
from axis.messaging.models import Message

__author__ = "Steven Klass"
__date__ = "1/16/17 16:36"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


def register_signals():
    """Nested to avoid tangling import during initial load."""

    # log.debug("Registering late signals.")

    from axis.customer_eto.models import ETOAccount

    post_save.connect(PostSaveETOAccountUpdateStats, sender=ETOAccount)

    from axis.home.models import EEPProgramHomeStatus

    post_save.connect(PostSaveAssignETOAccountAlert, sender=EEPProgramHomeStatus)
    post_save.connect(PostSaveAssignInspectedAlert, sender=EEPProgramHomeStatus)


def PostSaveAssignETOAccountAlert(sender, **kwargs):
    """This will fire off a notification to create an ETO Account number"""

    home_status = kwargs.get("instance")
    if kwargs.get("raw", False):
        return

    if "eto" not in home_status.eep_program.slug:
        return
    try:
        peci = Company.objects.get(slug="peci")
    except Company.DoesNotExist:
        log.warning(
            "Unable to find Company CLEAResult Provider - Skipping PostSaveAssignETOAccountAlert"
        )
        return

    company = home_status.home.get_builder()

    if company is None:
        return

    if hasattr(company, "eto_account") and company.eto_account.account_number is not None:
        return

    edit_url = reverse("company:view", kwargs={"type": company.company_type, "pk": company.pk})
    add_relationship = reverse(
        "relationship:add_id",
        kwargs={
            "model": "company",
            "app_label": "company",
            "object_id": company.id,
        },
    )
    context = {
        "company": "{}".format(company),
        "home_url": home_status.home.get_absolute_url(),
        "home": "{}".format(home_status.home),
        "add_relationship": add_relationship,
        "edit_url": edit_url,
    }
    NewETOAccountMessage(url=context["home_url"]).send(context=context, company=peci)
    log.debug("Called PostSaveAssignETOAccountAlert for %s", home_status)


def PostSaveAssignInspectedAlert(sender, **kwargs):
    """This will fire off a notification to create an ETO Account number"""

    home_status = kwargs.get("instance")
    if kwargs.get("raw", False):
        return

    if "eto" not in home_status.eep_program.slug:
        return

    if home_status.state != "certification_pending":
        return

    context = {
        "home_url": home_status.home.get_absolute_url(),
        "home": "{}".format(home_status.home),
    }
    try:
        csg = Company.objects.get(slug="csg-qa")
    except Company.DoesNotExist:
        log.warning('Comapny "csg-qa" does not exist')
        return

    HomeInspectedMessage(url=context["home_url"]).send(
        context=context,
        company=csg,
    )


def PostSaveETOAccountUpdateStats(sender, **kwargs):
    eto_account = kwargs.get("instance")
    if kwargs.get("raw", False):
        return
    if not kwargs.get("created"):
        return

    from axis.home.models import Home, EEPProgramHomeStatus
    from axis.home.tasks import update_home_stats

    home_ids = Home.objects.filter_by_company(eto_account.company, show_attached=True).values_list(
        "id", flat=True
    )

    stat_ids = EEPProgramHomeStatus.objects.filter(
        home__id__in=home_ids, certification_date__isnull=True, eep_program__owner__slug="eto"
    ).values_list("id", flat=True)

    if len(list(stat_ids)):
        update_home_stats.delay(eepprogramhomestatus_ids=list(stat_ids))

        stats = EEPProgramHomeStatus.objects.filter(id__in=stat_ids)
        company_ids = list(set(list(stats.values_list("company", flat=True))))

        msg = strings.ETO_ACCOUNT_NUMBER_ADDED_BASE.format(company=eto_account.company)
        if Message.objects.filter(content__istartswith=msg).count():
            return

        for company in Company.objects.filter(id__in=company_ids):
            home_statuses = stats.filter(company=company).distinct()

            context = {"company": "{}".format(eto_account.company)}
            if home_statuses.count() == 1:
                msg_cls = ETOAccountNumberAddedSingleMessage
                context["home"] = "{}".format(home_statuses[0].home)
                context["home_url"] = home_statuses[0].home.get_absolute_url()
            else:
                msg_cls = ETOAccountNumberAddedMultipleMessage
                context["count"] = home_statuses.count()
            log.debug("Sending persistant message for %s", company)

            msg_cls(url=context.get("home_url")).send(
                context=context,
                company=company,
            )

        log.debug("Dispatched %s update stats for ETO Account Add", stats.count())
