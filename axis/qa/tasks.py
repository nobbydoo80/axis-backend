"""tasks.py: Django qa"""


import datetime
from collections import namedtuple, defaultdict

from celery import shared_task
from celery.utils.log import get_task_logger
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.utils.timezone import now

from . import messages
from .messages import QACorrectionRequiredDailyEmail, QAFailingHomesDailyEmail
from .models import QAStatus, QARequirement

__author__ = "Steven Klass"
__date__ = "12/26/13 9:20 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

User = get_user_model()
logger = get_task_logger(__name__)


@shared_task
def update_notify_opportunities(home_status_id, **kwargs):
    """Given a newly created homestatus determine if a messages should be sent to the QA company
    and act on it"""
    from axis.home.models import EEPProgramHomeStatus

    log = kwargs.get("log", logger)

    try:
        home_status = EEPProgramHomeStatus.objects.get(id=home_status_id)
    except ObjectDoesNotExist:
        return

    qa_requirements = QARequirement.objects.filter_for_home_status(home_status)

    MessageContext = namedtuple(
        "MessageContext", "qa_company, percent, program, home_detail, action_url, home"
    )
    contexts = set()

    url = home_status.home.get_absolute_url()
    action_url = url + "#/tabs/qa"

    for requirement in qa_requirements:
        # Only send the message if the requirement is < 100%  It's too much otherwise.
        # Only send the message if the requirement is > 0%  It's not enough otherwise.
        if 0 < requirement.coverage_pct < 1:
            if requirement.get_active_coverage_pct() <= requirement.coverage_pct:
                qa_company = "{}".format(requirement.qa_company)
                program = "{}".format(home_status.eep_program)
                home = home_status.home.get_addr()

                context = MessageContext(
                    qa_company, requirement.coverage_pct, program, url, action_url, home
                )
                contexts.add((context, requirement.qa_company))

    for context, company in contexts:
        messages.QaRecommendedMessage(url=action_url).send(
            context=context._asdict(), company=company
        )

    log.info("QA Messages have been sent.")


@shared_task
def update_qa_states(qa_status_id, user_id=None, **kwargs):
    """Automagically move us through the qa states if applicable"""

    log = kwargs.get("log", logger)

    try:
        qa_status = QAStatus.objects.get(id=qa_status_id)
    except QAStatus.DoesNotExist:
        return

    log.debug("Called - update_qa_states")
    try:
        user = User.objects.get(id=user_id)
    except ObjectDoesNotExist:
        try:
            user = (
                qa_status.history.filter(id=qa_status.id, history_user__isnull=False)
                .last()
                .history_user
            )
        except AttributeError:
            user = qa_status.requirement.qa_company.users.first()

    if qa_status.state == "received":
        next_transition = next((x.get_name() for x in qa_status.possible_transitions))
        if qa_status.get_home_status().state != "pending_inspection":
            qa_status.make_transition(next_transition, user=user)
            msg = "Successfully completed {} transition for user {}".format(next_transition, user)
            log.info(msg)
            return msg

    return "Nothing done for {}".format(qa_status_id)


@shared_task
def correction_required_daily_email(**kwargs):
    from axis.core.utils import get_previous_day_start_end_times
    from axis.home.models import EEPProgramHomeStatus

    start, end = get_previous_day_start_end_times()
    if kwargs.get("ignore_dates"):
        start, end = datetime.datetime(2010, 1, 1, tzinfo=datetime.timezone.utc), now()
    full_date = start.strftime("%A, %B %d %Y")

    qafilter = {
        "qastatus__state": "correction_required",
        "qastatus__last_update__gte": start,
        "qastatus__last_update__lte": end,
    }

    companies = EEPProgramHomeStatus.objects.filter(**qafilter).values_list("company", flat=True)
    companies = list(set(companies))

    for company_id in companies:
        stats = EEPProgramHomeStatus.objects.filter(company_id=company_id, **qafilter)
        company = stats.first().company
        context = {
            "base_url": "https://pivotalenergy.net",
            "company": company,
            "full_date": full_date,
            "home_statuses": stats,
            "total": stats.count(),
        }
        QACorrectionRequiredDailyEmail().send(company=company, context=context)

    return "{} companies were sent email(s) on QA correction requests".format(len(companies))


@shared_task
def qa_review_fail_daily_email(queryset=None, triggered_from_admin_interface=False, **kwargs):
    from axis.core.utils import get_previous_day_start_end_times
    from axis.qa.models import QAStatus

    start, end = get_previous_day_start_end_times()
    if kwargs.get("ignore_dates"):
        start, end = datetime.datetime(2010, 1, 1, tzinfo=datetime.timezone.utc), now()
    full_date = start.strftime("%A, %B %d %Y")

    if queryset and triggered_from_admin_interface:
        stats = queryset
    else:
        stats = QAStatus.objects.filter(
            state="complete",
            result="fail",
            state_history__start_time__range=[start, end],
            state_history__to_state="complete",
        )

    rater_header = """
    Upon QA review and attempted corrections, the following homes participating in
    {program_counts} program(s) for {rater_names} have failed QA. These homes do not meet the
    requirements associated with this program.
    """

    utility_header = """
    Upon QA review and follow-up with the Rater, the following homes participating in
    {program_counts} program(s) for {rater_names} have failed QA. Per the QA guidelines of this
    program, QA determined these homes do not meet the requirements associated with this program.
    """

    footer = """
    QA results may be reviewed by navigating to the home and clicking on the QA tab.
    """

    grouped_stats = defaultdict(set)
    for stat in stats:
        grouped_stats[stat.home_status.company].add(stat)
        grouped_stats[stat.home_status.get_gas_company()].add(stat)
        grouped_stats[stat.home_status.get_electric_company()].add(stat)
    grouped_stats = dict(grouped_stats)

    # Status may not have a gas or electric company
    if None in grouped_stats:
        del grouped_stats[None]

    for company, company_stats in grouped_stats.items():
        header = rater_header if company.company_type == "rater" else utility_header
        rater_names = ", ".join({"{}".format(stat.home_status.company) for stat in company_stats})
        program_counts = len(set([x.home_status.eep_program for x in company_stats]))

        context = {
            "num_homes": len(company_stats),
            "full_date": full_date,
            "base_url": "https://pivotalenergy.net",
            "stats": [x.home_status for x in company_stats],
            "header": header.format(program_counts=program_counts, rater_names=rater_names),
            "footer": footer,
        }
        QAFailingHomesDailyEmail().send(company=company, context=context)
