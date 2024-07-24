"""tasks.py: Django home"""

__author__ = "Steven Klass"
__date__ = "6/22/12 10:33 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

import datetime
import logging
import os
import tempfile
import time
from collections import defaultdict, OrderedDict, namedtuple
from decimal import Decimal

from celery import shared_task
from celery.utils.log import get_task_logger
from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core.files import File
from django.db.models import Q, DecimalField, Sum, Value as V, F
from django.db.models.functions import Coalesce
from django.utils.timezone import now

from axis.gbr.models import GreenBuildingRegistry
from django_states.exceptions import TransitionCannotStart
from infrastructure.utils import elapsed_time

from axis.customer_neea.utils import NEEA_BPA_SLUGS
from axis.filehandling.log_storage import LogStorage
from axis.home import messages
from axis.home import strings
from axis.home.messages import (
    PendingCertificationsDailyEmail,
    CertificationsDailyEmail,
    BPACertificationsDailyEmail,
    PivotalAdminDailyEmail,
)
from axis.home.models import EEPProgramHomeStatus
from axis.home.utils import write_home_program_reports, HomeCertification

customer_hirl_app = apps.get_app_config("customer_hirl")
logger = get_task_logger(__name__)
User = get_user_model()


# TODO: move this to utils
def certify_single_home(
    user,
    home_status: EEPProgramHomeStatus,
    certification_date: datetime.datetime | datetime.date,
    **kwargs,
):
    kwargs["log"] = kwargs.get("log", logger)
    start = time.time()
    certification = HomeCertification(user, home_status, certification_date, **kwargs)
    if certification.already_certified:
        # FIXME: placeholder messages, do we want anything here?
        return []

    if not kwargs.get("bypass_check", False):
        if not certification.verify():
            if kwargs.get("throw_errors", False):
                raise Exception(certification.errors)
            return certification.errors

    certification.certify()
    stop = time.time()
    logger.info(
        "Program certification on status %(home_status_id)s by %(user_id)s "
        "for %(eep_program_slug)s took %(submit_time)s",
        {
            "home_status_id": home_status.pk,
            "user_id": user.pk,
            "eep_program_slug": home_status.eep_program.slug,
            "submit_time": elapsed_time(stop - start).long_fmt,
        },
    )
    return []


# TODO: move this to utils
def certify_sampleset(user, sampleset, certification_date, **kwargs):
    from axis.home.utils import HomeCertification

    kwargs["log"] = kwargs.get("log", logger)
    start = time.time()
    stats = sampleset.home_statuses.all().order_by("samplesethomestatus__is_test_home")

    report = {"debug": [], "info": [], "warning": [], "error": []}

    verified = True
    for stat in stats:
        certify = HomeCertification(user, stat, certification_date, **kwargs)
        if certify.already_certified:
            continue
        elif certify.verify():
            verified = verified and True
        else:
            verified = False
            report["error"] += certify.errors

    if verified:
        ss_report = sampleset.certify(user, certification_date, return_report=True)
        for level, msgs in ss_report.items():
            map(report[level].append, msgs)

    stop = time.time()
    logger.info(
        "Program certification on sampleset %(sampleset_id)s by %(user_id)s "
        "took %(submit_time).3f s",
        {"sampleset_id": sampleset.pk, "user_id": user.pk, "submit_time": stop - start},
    )

    return report


# TODO: move this to utils
def certify_multiple_homes(user, stats, certification_date, **kwargs):
    start = time.time()
    errors = []

    sampleset_stats = stats.filter(samplesethomestatus__sampleset__isnull=False)
    standalone = stats.filter(samplesethomestatus__isnull=True)

    ss_ids = set(sampleset_stats.values_list("samplesethomestatus__sampleset", flat=True))

    if len(ss_ids):
        from axis.sampleset.models import SampleSet

        for ss in SampleSet.objects.filter(id__in=ss_ids):
            errors = certify_sampleset(user, ss, certification_date, **kwargs)["error"]

    for stat in standalone:
        errors += certify_single_home(user, stat, certification_date, **kwargs)

    stop = time.time()
    logger.info(
        "Program certification on %(total_homes)s by %(user_id)s took %(submit_time).3f s",
        {"total_homes": stats.count(), "user_id": user.pk, "submit_time": stop - start},
    )

    return errors


@shared_task
def set_abandoned_homes_task():
    """
    This will update set all homes which haven't been touched in
    settings.HOME_ABANDON_EXPIRE_DAYS days to abandoned.
    """
    from axis.home.models import EEPProgramHomeStatus

    now_ = now()
    home_statuses = EEPProgramHomeStatus.objects.exclude(
        Q(state__in=["complete", "abandoned"])
        | Q(
            eep_program__slug__in=customer_hirl_app.HIRL_PROJECT_EEP_PROGRAM_SLUGS
            + customer_hirl_app.HIRL_PROJECT_LEGACY_EEP_PROGRAM_SLUGS
        ),
    ).distinct()
    for stat in home_statuses:
        delta = now_ - stat.modified_date
        if delta.days > settings.HOME_ABANDON_EXPIRE_DAYS:
            stat.make_transition("to_abandoned_transition", user=None)


@shared_task(time_limit=20000, bind=True)
def export_home_data(self, result_object_id, **kwargs):
    """Validates and then imports a checklist ``document``."""
    from axis.filehandling.models import AsynchronousProcessedDocument
    from axis.home.export_data import HomeDataXLSExport

    kwargs["task"] = self

    app_log = LogStorage(model_id=result_object_id)

    result_object = AsynchronousProcessedDocument.objects.get(id=result_object_id)

    user_id = kwargs.get("user_id", None)
    user = User.objects.get(id=user_id) if user_id else None

    msg = "{user} requested home data export task [{task_id}]"
    app_log.info(msg.format(user=user.get_full_name(), task_id=result_object.task_id))

    export = HomeDataXLSExport(log=app_log, **kwargs)
    new_filename = tempfile.NamedTemporaryFile(
        delete=True, suffix=".xlsx", prefix="Home-Status-Export_"
    )
    export.write(output=new_filename)

    app_log.info("New file saved %s", os.path.basename(new_filename.name))
    new_filename.seek(0)

    result_object.document = File(new_filename, name=os.path.basename(new_filename.name))
    result_object.save()

    exp_filters = "-"
    if export.filters:
        exp_filters = (
            "<ul><li>"
            + "</li><li>".join(["{k}: {v}".format(k=k, v=v) for k, v in export.filters])
            + "</li></ul>"
        )
    messages.HomeStatusExportCompletedMessage(url=result_object.get_absolute_url()).send(
        user=user,
        context={"filters": exp_filters},
    )

    app_log.update_model(throttle_seconds=None)


@shared_task(bind=True, time_limit=60 * 60 * 3)
def export_home_program_report_task(
    self, user_id, result_object_id, homestatus_ids, filter_info, **kwargs
):
    start_time = time.time()
    from axis.filehandling.models import AsynchronousProcessedDocument
    from axis.home.models import EEPProgramHomeStatus

    task = self

    user = User.objects.get(id=user_id)
    result_object = AsynchronousProcessedDocument.objects.get(id=result_object_id)
    queryset = EEPProgramHomeStatus.objects.filter_by_user(user).filter(id__in=homestatus_ids)

    app_log = LogStorage(model_id=result_object_id)
    msg = "{user} requested home data export task [{task_id}]"
    app_log.info(msg.format(user=user.get_full_name(), task_id=result_object.task_id))

    filename, response_stream = write_home_program_reports(
        user,
        queryset,
        **{
            "filter_info": filter_info,
            "task": task,
            "log": app_log,
        },
    )
    result_object.document = File(response_stream, name=filename)
    result_object.save()

    exp_filters = "-"
    if filter_info:
        exp_filters = (
            "<ul><li>"
            + "</li><li>".join(["{k}: {v}".format(k=k, v=v) for k, v in filter_info])
            + "</li></ul>"
        )
    messages.HomeStatusProgramReportsCompletedMessage(url=result_object.get_absolute_url()).send(
        user=user,
        context={"filters": exp_filters},
    )
    app_log.update_model(throttle_seconds=None)
    msg = "Completed %(task)s in %(elapsed_time)s"
    kw = {
        "task": "export_home_program_report_task",
        "elapsed_time": elapsed_time(time.time() - start_time).long_fmt,
    }
    logger.info(msg, kw)


@shared_task
def update_home_states(
    eepprogramhomestatus_ids=None, eepprogramhomestatus_id=None, user_id=None, log=None
):
    """This is looking to move a program forward if outside factors (company relationships) have
    been influenced and the program is now ready for movement - this will fire the post save
    trigger"""
    from axis.home.models import EEPProgramHomeStatus

    if not log:
        log = logger

    log.debug("Called - update_home_states")

    home_status_ids = []
    if eepprogramhomestatus_ids:
        home_status_ids = eepprogramhomestatus_ids
    elif eepprogramhomestatus_id:
        home_status_ids = [
            eepprogramhomestatus_id,
        ]
    else:
        raise ValueError("Provide eepprogramhomestatus_ids or eepprogramhomestatus_id")

    home_statuses = EEPProgramHomeStatus.objects.filter(id__in=home_status_ids)

    sample_set_home_status_ids = []
    for home_status in home_statuses:
        ss_statuses = home_status.get_current_sampleset_home_statuses()
        if len(ss_statuses):
            sample_set_home_status_ids += list(ss_statuses.values_list("id", flat=True))

    user = None
    if user_id:
        user = User.objects.get(id=user_id)

    home_statuses = EEPProgramHomeStatus.objects.filter(
        id__in=set(home_status_ids + sample_set_home_status_ids)
    ).select_related("eep_program", "customer_hirl_project")

    updated = {}
    for stat in home_statuses:
        while True:
            if stat.eep_program.slug in customer_hirl_app.HIRL_PROJECT_EEP_PROGRAM_SLUGS:
                next_state_transition = _get_customer_hirl_next_state_transition(
                    home_status=stat, user=user, log=log
                )
            else:
                next_state_transition = _get_next_state_transition(
                    home_status=stat, user=user, log=log
                )

            if next_state_transition:
                if settings.DEBUG:
                    log.debug("  Moving to next state - %s", next_state_transition)
                try:
                    stat.make_transition(next_state_transition, user=user)
                except Exception as err:
                    company = user.company if user else ""
                    log.error(
                        "Failed Transition to %s by %r (%r) for %r - %r",
                        next_state_transition,
                        user,
                        company,
                        stat,
                        err,
                    )
                    raise
                else:
                    try:
                        _hstat = EEPProgramHomeStatus.objects.get(id=stat.id).history.most_recent()
                        if user and _hstat.history_user is None:
                            _hstat.history_user = user
                            _hstat.save()
                    except AttributeError:
                        pass
                    updated["%s" % stat.id] = next_state_transition
            else:
                # log.debug("Ending")
                break

    if updated:
        if len(updated.keys()) > 1:
            results = "Updated %s Home states %s" % (
                len(list(updated.keys())),
                ",".join(list(updated.keys())),
            )
            log.debug(results)
        else:
            results = "Updated Home states %s %s" % (
                list(updated.keys())[0],
                list(updated.values())[0],
            )
            log.debug(results)
        return results
    return


def _get_customer_hirl_next_state_transition(home_status, user, log):
    from axis.home.models import EEPProgramHomeStatus
    from axis.customer_hirl.models import HIRLProjectRegistration
    from axis.qa.models import QARequirement, QAStatus

    next_state_transition = None
    customer_hirl_project = getattr(home_status, "customer_hirl_project", None)

    if home_status.state == EEPProgramHomeStatus.PENDING_INSPECTION_STATE:
        next_state_transition = "customer_hirl_pending_project_data_transition"

    elif home_status.state == EEPProgramHomeStatus.CUSTOMER_HIRL_PENDING_PROJECT_DATA:
        if (
            customer_hirl_project
            and customer_hirl_project.registration.state == HIRLProjectRegistration.ACTIVE_STATE
        ):
            next_state_transition = "customer_hirl_pending_rough_qa_transition"

    elif home_status.state == EEPProgramHomeStatus.CUSTOMER_HIRL_PENDING_ROUGH_QA_STATE:
        qa_status_exists = home_status.qastatus_set.filter(
            requirement__type=QARequirement.ROUGH_INSPECTION_QA_REQUIREMENT_TYPE,
            result=QAStatus.PASS_STATUS,
        ).exists()
        if customer_hirl_project:
            if qa_status_exists or not customer_hirl_project.is_require_rough_inspection:
                next_state_transition = "customer_hirl_pending_final_qa_transition"

    elif home_status.state == EEPProgramHomeStatus.CUSTOMER_HIRL_PENDING_FINAL_QA_STATE:
        qa_status_exists = home_status.qastatus_set.filter(
            requirement__type=QARequirement.FINAL_INSPECTION_QA_REQUIREMENT_TYPE,
            result=QAStatus.PASS_STATUS,
        ).exists()

        if customer_hirl_project:
            if qa_status_exists or not customer_hirl_project.is_require_final_inspection:
                next_state_transition = "customer_hirl_certification_pending_transition"
    elif home_status.state == "certification_pending" and home_status.certification_date:
        next_state_transition = "completion_transition"
    return next_state_transition


def _get_next_state_transition(home_status, user, log):
    next_state_transition, gating_qa_complete = None, True
    if home_status.state == "pending_inspection":
        if not home_status.get_missing_annotation_types().count():
            next_state_transition = "inspection_transition"
    if home_status.state == "inspection":
        eligible = home_status.is_eligible_for_certification(skip_certification_check=True)
        if eligible and home_status.pct_complete < 100:
            home_status.update_stats()
        if eligible or home_status.certification_date:
            if (
                not home_status.eep_program.manual_transition_on_certify
                or home_status.certification_date
            ):
                next_state_transition = "qa_transition"
                log.debug("Auto moving to QA Pending..")
            else:
                log.debug("Manual transition enforced for %s", home_status)
    if home_status.state == "qa_pending":
        if home_status.certification_date:
            next_state_transition = "certification_transition"
        else:
            gating_qa_complete = home_status.is_gating_qa_complete()
            if gating_qa_complete:
                log.debug("Auto moving to Inspected..")
                next_state_transition = "certification_transition"

    if home_status.state == "certification_pending" and home_status.certification_date:
        log.debug("Auto moving to Certifed..")
        next_state_transition = "completion_transition"

    if (
        home_status.state == "certification_pending"
        and home_status.eep_program.slug == "neea-efficient-homes"
    ):
        if gating_qa_complete:
            log.debug("Auto moving to Certifed")
            next_state_transition = "completion_transition"

    if home_status.state == "complete" and home_status.eep_program.slug == "neea-efficient-homes":
        log.debug("Auto Completing this sucker..")
        certify_single_home(home_status=home_status, user=user, certification_date=now())

    return next_state_transition


@shared_task
def update_home_stats(**kwargs):
    from axis.home.models import EEPProgramHomeStatus

    log = kwargs.get("log", logger)

    kwgs = {
        "state__in": ["pending_inspection", "inspection", "qa_pending", "certification_pending"]
    }

    if kwargs.get("eepprogramhomestatus_id"):
        kwgs["id"] = kwargs.get("eepprogramhomestatus_id")
        status = EEPProgramHomeStatus.objects.get(id=kwgs["id"])
        ss_statuses = status.get_current_sampleset_home_statuses()
        if len(ss_statuses):
            kwgs["id__in"] = [kwgs["id"]] + list(ss_statuses.values_list("id", flat=True))
            kwgs.pop("id")

    elif kwargs.get("eepprogramhomestatus_ids") and len(kwargs.get("eepprogramhomestatus_ids")):
        kwgs["id__in"] = kwargs.get("eepprogramhomestatus_ids")
        statuses = EEPProgramHomeStatus.objects.filter(id__in=kwgs["id__in"])
        for status in statuses:
            ss_statuses = status.get_current_sampleset_home_statuses()
            if len(ss_statuses):
                kwgs["id__in"] += list(ss_statuses.values_list("id", flat=True))
    else:
        log.warning("Not updating eep program home status must be bound")
        return "Unsuccessful Stat Update.  This needs to be bound by and id or a group of ids."

    stats = EEPProgramHomeStatus.objects.filter(**kwgs)
    for stat in stats:
        stat.update_stats()

    if stats.count() > 1:
        msg = "Successfully updated {} stats".format(stats.count())
    elif stats.count() == 1:
        msg = "Successfully updated stat {}".format(stats[0].id)
    else:
        return
    return msg


@shared_task(time_limit=60 * 60)
def associate_nightly_companies_to_homestatuses():
    from axis.home.utils import associate_nightly_companies_to_homestatuses

    start = time.time()
    associate_nightly_companies_to_homestatuses()
    msg = "Completed %(task)s in %(elapsed_time)s"
    logger.info(
        msg,
        {
            "task": "associate_nightly_companies_to_homestatuses",
            "elapsed_time": elapsed_time(time.time() - start).long_fmt,
        },
    )


@shared_task
def pending_certification_daily_email_task(stats_list=None, superusers_only=False):
    """
    Notify company admins about pending certifications
    :param stats_list: list of custom EEPProgramHomeStatus ids that must be triggered
    :param superusers_only: send notifications only for superusers
    """
    from axis.core.utils import get_previous_day_start_end_times
    from axis.home.models import EEPProgramHomeStatus

    start_date, end_date = get_previous_day_start_end_times()

    if not stats_list:
        stats = EEPProgramHomeStatus.objects.filter(
            state="certification_pending",
            state_history__start_time__range=[start_date, end_date],
            state_history__to_state="certification_pending",
        )
    else:
        stats = EEPProgramHomeStatus.objects.filter(pk__in=stats_list)

    # {agent: {program: {rater: [homestatus, homestatus, ...]}}
    homes_by_certification_agent = dict()

    # {agent: 1}}
    quantities = defaultdict(int)

    # {program: True / False}
    requires_qa = defaultdict(bool)

    for stat in stats:
        agent = stat.get_certification_agent()
        if agent not in homes_by_certification_agent:
            homes_by_certification_agent[agent] = dict()
        if stat.eep_program not in homes_by_certification_agent[agent]:
            homes_by_certification_agent[agent][stat.eep_program] = dict()
        if stat.company not in homes_by_certification_agent[agent][stat.eep_program]:
            homes_by_certification_agent[agent][stat.eep_program][stat.company] = []
        if stat not in homes_by_certification_agent[agent][stat.eep_program][stat.company]:
            homes_by_certification_agent[agent][stat.eep_program][stat.company].append(stat)
            quantities[agent] += 1
            if requires_qa[stat.eep_program] is True:
                continue
            if stat.is_gating_qa_complete() is False:
                requires_qa[stat.eep_program] = True

    for certification_agent, grouped_stats in homes_by_certification_agent.items():
        context = {
            "base_url": "https://%s" % Site.objects.get(id=settings.SITE_ID).domain,
            "grouped_stats": grouped_stats,
            "requires_qa": requires_qa,
            "num_homes": quantities[certification_agent],
        }
        PendingCertificationsDailyEmail().send(company=certification_agent, context=context)
        logger.debug("Sending certification pending email for %s", certification_agent)


@shared_task
def new_certification_daily_email_task(stats_list=None, superusers_only=False):
    """
    Notify company admins about new home certifications
    :param stats_list: list of custom EEPProgramHomeStatus ids that must be triggered
    :param superusers_only: send notifications only for superusers
    """
    from django.conf import settings
    from axis.home.models import EEPProgramHomeStatus
    from axis.core.utils import get_previous_day_start_end_times

    start_date, end_date = get_previous_day_start_end_times()

    if not stats_list:
        stats = EEPProgramHomeStatus.objects.filter(
            # Avoid full range query, since certification_date doesn't have a time component.
            # The midnight end_date will be today's date.
            certification_date=end_date.date(),
            company__company_type__in=["rater", "provider"],
        ).exclude(eep_program__slug__in=NEEA_BPA_SLUGS)
    else:
        stats = EEPProgramHomeStatus.objects.filter(pk__in=stats_list)

    result_dict = defaultdict(list)
    for stat in stats:
        result_dict[(stat.company, stat.eep_program.owner)].append(stat)

    def get_program_text(program, sponsor):
        """
        Check for a program specific piece of text to accompany the list of homes.
        If one doesn't exist, check if there's a generic one for the sponsor.
        """
        lookup = program.slug.replace("-", "_").upper()
        try:
            return getattr(strings, lookup + "_PROGRAM_TEXT")
        except AttributeError:
            pass

        try:
            return getattr(strings, sponsor.slug.upper() + "_DEFAULT_PROGRAM_TEXT")
        except AttributeError:
            return ""

    for (company, sponsor), homes in result_dict.items():
        users = User.objects.filter(company=company, is_company_admin=True)
        if superusers_only:
            users = User.objects.filter(is_superuser=True)

        if not users.exists():
            continue

        programs = defaultdict(lambda: {"program_text": "", "homes": []})
        for stat in homes:
            programs[stat.eep_program]["program_text"] = get_program_text(stat.eep_program, sponsor)
            programs[stat.eep_program]["homes"].append(stat)

        base_url = Site.objects.get(id=settings.SITE_ID).domain

        context = {
            "base_url": "https://%s" % base_url,
            "start_date": start_date,
            "company": company,
            "programs": dict(programs),
            "num_homes": len(homes),
        }

        CertificationsDailyEmail().send(users=users, context=context)
        logger.debug(f"Sending certification email for {company} to {users.count()} users")


@shared_task
def new_bpa_certification_daily_email_task(stats_list=None, superusers_only=False):
    """
    Notify company admins about new bpa certifications
    :param stats_list: list of custom EEPProgramHomeStatus ids that must be triggered
    :param superusers_only: send notifications only for superusers
    """

    from axis.core.utils import get_previous_day_start_end_times
    from axis.home.models import EEPProgramHomeStatus
    from axis.eep_program.models import EEPProgram

    start_date, end_date = get_previous_day_start_end_times()
    program = EEPProgram.objects.get(slug="neea-bpa")

    if not stats_list:
        stats = EEPProgramHomeStatus.objects.filter(
            # Avoid full range query, since certification_date doesn't have a time component.
            # The midnight end_date will be today's date.
            certification_date=end_date.date(),
            eep_program__slug__in=NEEA_BPA_SLUGS,
        )
    else:
        stats = EEPProgramHomeStatus.objects.filter(pk__in=stats_list)

    grouped_stats = defaultdict(set)
    for stat in stats:
        grouped_stats[stat.company].add(stat)
        grouped_stats[stat.get_gas_company()].add(stat)
        grouped_stats[stat.get_electric_company()].add(stat)
    grouped_stats = dict(grouped_stats)
    # Status may not have a gas or electric company
    if None in grouped_stats:
        del grouped_stats[None]

    base_url = Site.objects.get(id=settings.SITE_ID).domain

    for company, company_stats in iter(grouped_stats.items()):
        users = User.objects.filter(company=company, is_company_admin=True)
        if superusers_only:
            users = User.objects.filter(is_superuser=True)

        if not users.exists():
            continue

        rater_names = ", ".join({"%s" % stat.company for stat in company_stats})
        context = {
            "base_url": "https://%s" % base_url,
            "stats": company_stats,
            "program": program,
            "rater_names": rater_names,
            "date": start_date,
            "company": company,
            "num_homes": len(company_stats),
        }
        BPACertificationsDailyEmail().send(users=users, context=context)
        logger.debug(f"Sending NEEA BPA certification email for {company} to {users.count()} users")


@shared_task
def admin_daily_email_task():
    from django.conf import settings
    from simulation.models import Simulation
    from axis.core.models import User
    from axis.company.models import Company
    from axis.core.utils import get_previous_day_start_end_times
    from axis.community.models import Community
    from axis.ekotrope.models import Project as EkotropeProject
    from axis.subdivision.models import Subdivision
    from axis.remrate_data.models import DataTracker
    from axis.remrate_data.models import Simulation as RemSimulation
    from axis.floorplan.models import Floorplan
    from axis.customer_hirl.models import HIRLProject, HIRLProjectRegistration
    from axis.home.models import EEPProgramHomeStatus, Home
    from axis.qa.models import QAStatus
    from axis.customer_eto.models import FastTrackSubmission
    from axis.customer_neea.models import StandardProtocolCalculator
    from axis.invoicing.models import Invoice

    from axis.incentive_payment.models import IncentiveDistribution

    start_date, end_date = get_previous_day_start_end_times()

    stat_filters = Q(certification_date__gte=start_date, certification_date__lte=end_date) | Q(
        created_date__gte=start_date,
        created_date__lte=end_date,  # noqa: E127
        home__bulk_uploaded=True,
        certification_date__isnull=False,
    )
    stats = EEPProgramHomeStatus.objects.filter(stat_filters)

    cert_dict, cert_total = dict(), 0
    for stat in stats:
        if not cert_dict.get(stat.company):
            cert_dict[stat.company] = dict()
        if not cert_dict[stat.company].get(stat.eep_program):
            cert_dict[stat.company][stat.eep_program] = 0
        cert_dict[stat.company][stat.eep_program] += 1
        cert_total += 1

    IncentiveHistory = IncentiveDistribution.history.model
    payment_stats = IncentiveHistory.objects.filter(
        history_date__gte=start_date, history_date__lte=end_date, paid_date__isnull=False
    )

    _paid_dict, pay_total, gross_total = dict(), 0, 0
    for incentive in payment_stats:
        company = incentive.company
        customer = incentive.customer
        ipps = list(
            IncentiveHistory.objects.filter(id=incentive.id).exclude(paid_date__isnull=True)
        )
        if ipps[-1].history_date >= start_date and ipps[-1].history_date <= end_date:
            if not _paid_dict.get(company):
                _paid_dict[company] = dict()
            if not _paid_dict[company].get(customer):
                _paid_dict[company][customer] = 0
            _paid_dict[company][customer] += incentive.total
            gross_total += incentive.total
            pay_total += 1

    FastTrackSubmissionHistory = FastTrackSubmission.history.model
    total_count = list(
        set(
            FastTrackSubmissionHistory.objects.filter(
                project_id__isnull=False,
                eps_score__isnull=False,
                home_status__certification_date__isnull=False,
                history_date__gte=start_date,
                history_date__lte=end_date,
            ).values_list("id", flat=True)
        )
    )
    company = Company.objects.get(slug="eto")
    for item in FastTrackSubmission.objects.filter(id__in=total_count):
        rater = item.home_status.company
        builder = item.home_status.home.get_builder()
        if not _paid_dict.get(company):
            _paid_dict[company] = dict()
        if not _paid_dict[company].get(rater):
            _paid_dict[company][rater] = 0
        _paid_dict[company][rater] += item.rater_incentive
        gross_total += item.rater_incentive
        if item.rater_incentive:
            pay_total += 1
        if not _paid_dict[company].get(builder):
            _paid_dict[company][builder] = 0
        _paid_dict[company][builder] += item.builder_incentive
        gross_total += item.builder_incentive
        if item.builder_incentive:
            pay_total += 1

    # Those that transitioned last night.
    to_state = "ipp_payment_automatic_requirements"
    total_count = list(
        set(
            StandardProtocolCalculator.objects.filter(
                home_status__incentivepaymentstatus__state_history__to_state=to_state,
                home_status__incentivepaymentstatus__state_history__start_time__gte=start_date,
                home_status__incentivepaymentstatus__state_history__start_time__lte=end_date,
                home_status__certification_date__isnull=False,
                builder_incentive__gt=0,
            ).values_list("id", flat=True)
        )
    )
    for item in StandardProtocolCalculator.objects.filter(id__in=total_count):
        company = item.home_status.incentivepaymentstatus.owner
        builder = item.home_status.home.get_builder()
        if not _paid_dict.get(company):
            _paid_dict[company] = dict()
        if not _paid_dict[company].get(builder):
            _paid_dict[company][builder] = 0
        _paid_dict[company][builder] += Decimal(round(item.builder_incentive, 2))
        gross_total += Decimal(round(item.builder_incentive, 2))
        pay_total += 1

    payers = sorted(_paid_dict.keys(), key=lambda x: x.name)
    paid_data = OrderedDict([(x, OrderedDict()) for x in payers])

    for payer in payers:
        payees = sorted(_paid_dict[payer].keys(), key=lambda x: x.name)
        for payee in payees:
            paid_data[payer][payee] = "{:,.2f}".format(_paid_dict[payer][payee])

    subject = ""
    if cert_total:
        if cert_total > 1:
            subject += "{cert_total} homes were certified".format(cert_total=cert_total)
        else:
            subject += "{cert_total} home was certified".format(cert_total=cert_total)
    if pay_total:
        subject += " and " if len(subject) else ""
        if pay_total > 1:
            subject += "{pay_total} homes were paid".format(pay_total=pay_total)
        else:
            subject += "{pay_total} home was paid".format(pay_total=pay_total)
    if not cert_total and not pay_total:
        subject += "Light day"
    subject += " in Axis."

    stats = OrderedDict()
    Stat = namedtuple("Stat", ("total", "created"))

    created = User.objects.filter(
        date_joined__gte=start_date,
        date_joined__lte=end_date,
        is_active=True,
        last_login__isnull=False,
    ).count()
    total = User.objects.filter(is_active=True, last_login__isnull=False).count()
    stats["Users added"] = Stat(total, created)

    total = Community.objects.all().count()
    stats["Communities added"] = Stat(total, created)

    created = Community.objects.filter(
        created_date__gte=start_date, created_date__lte=end_date
    ).count()
    total = Community.objects.all().count()
    stats["Communities added"] = Stat(total, created)

    created = Subdivision.objects.filter(
        created_date__gte=start_date, created_date__lte=end_date
    ).count()
    total = Subdivision.objects.all().count()
    stats["Subdivisions/MF Developments added"] = Stat(total, created)

    created = DataTracker.objects.filter(
        created_on__gte=start_date, created_on__lte=end_date
    ).count()
    total = RemSimulation.objects.all().count()
    stats["REM/Rate data sets uploaded"] = Stat(total, created)

    created = (
        EkotropeProject.objects.filter(created_date__gte=start_date, created_date__lte=end_date)
        .exclude(data={})
        .count()
    )
    total = EkotropeProject.objects.exclude(data={}).count()
    stats["Ekotrope simulations imported"] = Stat(total, created)

    created = Simulation.objects.filter(
        created_date__gte=start_date, created_date__lte=end_date
    ).count()
    total = Simulation.objects.all().count()
    stats["Axis Simulations added"] = Stat(total, created)

    created = Floorplan.objects.filter(
        created_date__gte=start_date, created_date__lte=end_date
    ).count()
    total = Floorplan.objects.all().count()
    stats["Floorplans added"] = Stat(total, created)

    created = Home.objects.filter(created_date__gte=start_date, created_date__lte=end_date).count()
    total = Home.objects.all().count()
    stats["Projects created"] = Stat(total, created)

    GreenBuildingHistory = GreenBuildingRegistry.history.model
    created = GreenBuildingHistory.objects.filter(
        history_date__gte=start_date,
        history_date__lte=end_date,
        history_type="+",
        gbr_id__isnull=False,
    ).count()
    total = GreenBuildingHistory.objects.filter(gbr_id__isnull=False).count()
    stats["Green Building Registry ID's created"] = Stat(total, created)

    created = HIRLProjectRegistration.objects.filter(
        created_at__gte=start_date, created_at__lte=end_date
    ).count()
    total = HIRLProject.objects.all().count()
    stats["NGBS Project Registrations created"] = Stat(total, created)

    created = HIRLProject.objects.filter(
        created_at__gte=start_date, created_at__lte=end_date
    ).count()
    total = HIRLProject.objects.all().count()
    stats["NGBS Projects created"] = Stat(total, created)

    # created = SampleSet.objects.filter(creation_date__gte=start, creation_date__lte=end).count()
    # total = SampleSet.objects.all().count()
    # stats['Sample Sets'] = Stat(total, created)

    created = EEPProgramHomeStatus.objects.filter(
        created_date__gte=start_date, created_date__lte=end_date
    ).count()
    total = EEPProgramHomeStatus.objects.all().count()
    stats["Programs added to homes"] = Stat(total, created)

    created = QAStatus.objects.filter(created_on__gte=start_date, created_on__lte=end_date).count()
    total = QAStatus.objects.all().count()
    stats["QA added to programs"] = Stat(total, created)

    created = IncentiveDistribution.objects.filter(
        check_requested_date__gte=start_date, check_requested_date__lte=end_date
    ).count()
    total = IncentiveDistribution.objects.all().count()
    stats["Incentive Distributions created"] = Stat(total, created)

    # Gross Totals
    total = IncentiveDistribution.objects.filter(paid_date__lte=end_date).aggregate(
        gross_total=Coalesce(Sum("total"), V(0), output_field=DecimalField())
    )["gross_total"]

    total_count = FastTrackSubmissionHistory.objects.filter(
        project_id__isnull=False,
        eps_score__isnull=False,
        home_status__certification_date__isnull=False,
        history_date__lte=end_date,
    ).distinct()

    total += FastTrackSubmission.objects.filter(id__in=total_count).aggregate(
        aps_eto_total=Coalesce(
            Sum(F("builder_incentive") + F("rater_incentive")), V(0), output_field=DecimalField()
        ),
    )["aps_eto_total"]

    to_state = "ipp_payment_automatic_requirements"
    total_count = StandardProtocolCalculator.objects.filter(
        home_status__incentivepaymentstatus__state_history__to_state=to_state,
        home_status__incentivepaymentstatus__state_history__start_time__lte=end_date,
        home_status__certification_date__isnull=False,
        builder_incentive__gt=0,
    ).distinct()

    aps_eto_neea_total = StandardProtocolCalculator.objects.filter(id__in=total_count).aggregate(
        aps_eto_neea_total=Coalesce(
            Sum(F("builder_incentive") * V(2)), V(0), output_field=DecimalField()
        )
    )["aps_eto_neea_total"]
    total += Decimal(aps_eto_neea_total)

    total = "${:20,.2f}".format(total)
    gross_total = gross_total if gross_total == 0 else "${:20,.2f}".format(gross_total)
    stats["Incentives Generated"] = Stat(total, gross_total)

    created = Invoice.objects.filter(created_at__gte=start_date, created_at__lte=end_date).count()
    total = Invoice.objects.all().count()
    stats["Invoices created"] = Stat(total, created)

    created = sum(
        Invoice.objects.filter(created_at__gte=start_date, created_at__lte=end_date).values_list(
            "total", flat=True
        )
    )
    invoice_total = sum(Invoice.objects.all().values_list("total", flat=True))
    stats["Invoiced Amount"] = Stat(f"${invoice_total:,.2f}", f"${created:,.2f}")

    base_url = Site.objects.get(id=settings.SITE_ID).domain
    context = {
        "base_url": "https://%s" % base_url,
        "title": subject,
        "start_date": start_date,
        "certification_total": cert_total,
        "certifications": cert_dict,
        "payment_total": pay_total,
        "payments": paid_data,
        "invoice_total": invoice_total,
        "statistics": stats,
    }

    users = User.objects.filter(company__slug="pivotal-energy-solutions", is_superuser=True)
    if not users.count():
        return
    PivotalAdminDailyEmail().send(users=users, context=context)
    logger.debug(f"Sending dail admin email to {users.count()} users")


@shared_task(time_limit=60 * 10)
def home_upload_process(company_id, user_id, result_object_id, **kwargs):
    """Validates and then imports a Single Home Checklist"""
    from axis.filehandling.models import AsynchronousProcessedDocument
    from axis.home.single_home_checklist import SingleHomeChecklist
    from axis.filehandling.utils import get_physical_file

    log = kwargs.get("log", logger)
    app_log = LogStorage(model_id=result_object_id)

    start = time.time()

    result_object = AsynchronousProcessedDocument.objects.get(id=result_object_id)

    if None in [company_id, user_id, result_object_id]:
        items = [("Company", company_id), ("User", user_id), ("Result Object", result_object_id)]
        missing = [x[0] for x in items if not x[1]]
        log.critical("Missing input items {missing}".format(missing=", ".join(missing)))
        return

    result = "--"
    user = User.objects.get(id=user_id)
    company = result_object.company
    document = result_object.document
    overwrite_old_answers = kwargs.get("update_existing_answers", False)

    try:
        filename = get_physical_file(document.name, log=log)
    except AttributeError:
        app_log.info("Using document string %s", document)
        filename = "MISSING"

    msg = "{user} submitted {document} for processing with task {task} [{task_id}]"
    app_log.info(
        msg.format(
            user=user,
            document=os.path.basename(filename),
            task=result_object.task_name,
            task_id=result_object.task_id,
        )
    )

    single_file_upload = SingleHomeChecklist(
        filename=filename,
        result_id=result_object_id,
        user=user,
        company=company,
        log=app_log,
        overwrite_old_answers=overwrite_old_answers,
    )

    for method in ["read", "validate_data", "process_data"]:
        app_log.info("Starting '%s' on %s", method, os.path.basename(filename))
        #
        # if method == "process_data":
        #     CustomerDocument.objects.create(
        #         company = company
        #         document = document
        #         type = "document"
        #         filesize =
        #         description = "Home via Single Home Upload",
        #     )

        try:
            result = getattr(single_file_upload, method)()
        except Exception as err:
            log.debug("Single Family Exception - %s" % err)
            extra = {"company_id": company_id, "user_id": user_id, "result_id": result_object_id}
            log.error(
                "Single Family Error Processing on %(method)s",
                {"method": method},
                exc_info=1,
                extra=extra,
            )
            raise
        else:
            app_log.update_model(throttle_seconds=None)
            if app_log.has_errors:
                app_log.info("Issues found with '%s' on %s", method, os.path.basename(filename))
                app_log.update_model(throttle_seconds=None)
                return
            app_log.info("Completed '%s' on %s", method, os.path.basename(filename))

    app_log.info(
        "Successfully uploaded the Single File Home '%s' in %s",
        os.path.basename(filename),
        elapsed_time(time.time() - start).long_fmt,
    )

    app_log.update_model(throttle_seconds=None)
    return result
