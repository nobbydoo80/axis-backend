"""tasks.py: Django company"""


from celery import shared_task
from celery.utils.log import get_task_logger

__author__ = "Steven Klass"
__date__ = "4/23/13 8:04 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

logger = get_task_logger(__name__)


@shared_task(
    default_retry_delay=15, max_retries=5, ignore_result=True, store_errors_even_if_ignored=True
)
def update_company_groups(company_id, force=False):
    """This updates a companies groups to.
    :param company_id: axis.company.models.Company id
    :param force: clears the perms before_hand
    """
    from .models import Company

    log = logger

    try:
        company = Company.objects.get(id=company_id)
    except Company.DoesNotExist as err:
        msg = "Unable to find company id %s - unable to run task update_company_groups"
        log.info(msg, company_id, exc_info=True)
        update_company_groups.retry(exc=err)

    default_group = company.group
    admin_group = company.get_admin_group()

    if not default_group or not admin_group:
        import sys

        if "test" in sys.argv:
            log.info("No groups assigned to this company %s" % company_id)
            return

        log.error("No groups assigned to this company %s" % company_id)
        return

    if force:
        default_group.permissions.clear()
        admin_group.permissions.clear()
    return company.update_permissions()


@shared_task(ignore_result=True, store_errors_even_if_ignored=True)
def send_hquito_notification_message(company_id, status):
    """This will send an in-system message for an hvac who does not have a HQUTIO Certification"""

    from axis.relationship.models import Relationship
    from axis.company.models import Company
    from axis.home.models import EEPProgramHomeStatus
    from axis.company import messages
    from django.urls import reverse

    log = logger

    hvac_company = Company.objects.get(id=company_id)

    if hvac_company.hquito_accredited in [False, True]:
        return

    relations = Relationship.objects.filter_homes_for_company(
        Company.objects.get(id=company_id), True
    )
    home_ids = list(relations.values_list("object_id", flat=True))
    stats = EEPProgramHomeStatus.objects.filter(
        eep_program__owner__slug="neea", home_id__in=home_ids
    )
    stats = stats.exclude(state__in=["complete", "abandoned"]).distinct()

    destination = stats[0].eep_program.owner
    if hvac_company.is_customer:
        destination = Company.objects.get(id=company_id)

    url = reverse("company:view", kwargs={"type": hvac_company.company_type, "pk": hvac_company.id})
    if stats.count() == 1:
        messages.HVACContractorHQUITOStatusSingleMessage(url=hvac_company.get_absolute_url()).send(
            context={"company": "{}".format(hvac_company), "url": url, "status": status},
            company=destination,
        )
        log.info("Send hquito_notification_message to %s - %s", destination, status)

    elif stats.count() > 1:
        messages.HVACContractorHQUITOStatusMultipleMessage(
            url=hvac_company.get_absolute_url()
        ).send(
            context={"company": "{}".format(hvac_company), "url": url, "status": status},
            company=destination,
        )
        log.info("Send hquito_notification_message (mult) to %s - %s", destination, status)


@shared_task()
def update_stats_based_on_company_change(company_id, **kwargs):
    """Update home stats for any Active EPA Company"""

    from axis.home.models import Home, EEPProgramHomeStatus
    from axis.home.tasks import update_home_states, update_home_stats
    from axis.company.models import Company

    log = kwargs.get("log", logger)

    try:
        company = Company.objects.get(id=company_id)
    except Company.DoesNotExist:
        log.debug("Company {} was deleted".format(company_id))
        return

    home_ids = Home.objects.filter_by_company(company, show_attached=True).values_list(
        "id", flat=True
    )

    stats = EEPProgramHomeStatus.objects.filter(
        home_id__in=home_ids, certification_date__isnull=True
    )
    stats = stats.exclude(state="complete")
    stat_ids = list(set(stats.values_list("id", flat=True).values_list("id", flat=True)))

    if len(list(stat_ids)):
        log.debug("Called update_stats_based_on_company_change for %s", company)
        update_home_stats(eepprogramhomestatus_ids=list(stat_ids))
        update_home_states(eepprogramhomestatus_ids=list(stat_ids))

    [stat.validate_references() for stat in stats]
