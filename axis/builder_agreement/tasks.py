"""tasks.py: Django home"""


import os
import tempfile

from celery import shared_task
from celery.utils.log import get_task_logger
from django.apps import apps
from django.contrib.auth import get_user_model
from django.core.files import File

from axis.builder_agreement import messages
from .utils import increase_builder_agreement_gauge_for_incentive_distribution

app = apps.get_app_config("builder_agreement")


__author__ = "Steven Klass"
__date__ = "5/27/13 10:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

logger = get_task_logger(__name__)

User = get_user_model()


@shared_task(ignore_result=True, store_errors_even_if_ignored=True)
def update_lots_paid_count(incentive_distribution_id, **kwargs):
    from .models import BuilderAgreement
    from axis.incentive_payment.models import IncentiveDistribution
    from axis.home.models import EEPProgramHomeStatus

    log = kwargs.get("log", logger)

    # Resolve the instance id to an object
    try:
        incentive_distribution = IncentiveDistribution.objects.get(id=incentive_distribution_id)
    except IncentiveDistribution.DoesNotExist:
        return

    # Update the gauges if we've paid
    if incentive_distribution.status == IncentiveDistribution.PAID_STATUS:
        increase_builder_agreement_gauge_for_incentive_distribution(incentive_distribution)

    if incentive_distribution.customer.company_type != "builder":
        return

    # Update the lot totals if we are a builder.
    # Builders are an organization choice that semantically will only trigger this once.
    company = incentive_distribution.company
    customer = incentive_distribution.customer
    ipp_items = incentive_distribution.ippitem_set.select_related("home_status__home__subdivision")
    processed = set()
    for item in ipp_items:
        subdivision = item.home_status.home.subdivision
        try:
            builder_agreement = BuilderAgreement.objects.get(
                company=company, builder_org=customer, subdivision=subdivision
            )
        except BuilderAgreement.DoesNotExist:
            continue

        if builder_agreement.id in processed:
            continue
        if builder_agreement.is_legacy:
            continue

        lots_paid = EEPProgramHomeStatus.objects.filter_homes_for_builder_agreement_paid(
            builder_agreement
        ).count()

        # https://pivotalenergysolutions.zendesk.com/agent/tickets/25606
        # An incentives anomaly in APS's accounting has left homes without record of payment.
        if (
            builder_agreement.subdivision
            and builder_agreement.subdivision.slug == app.APS_LOTS_PAID_HACK_SLUG
        ):
            lots_paid += app.APS_LOTS_PAID_HACK_OFFSET

        if lots_paid == builder_agreement.lots_paid:
            continue

        msg = "Updating lots paid from {} to {} for builder agreement {}"
        log.info(msg.format(builder_agreement.lots_paid, lots_paid, builder_agreement))
        builder_agreement.lots_paid = lots_paid
        builder_agreement.save()
        processed.add(builder_agreement.id)
    log.info("Updated {} builder agreements".format(len(list(processed))))
    if len(list(processed)):
        return "Updated {} builder agreements".format(len(list(processed)))
    return "No builder agreement updates!"


@shared_task(time_limit=60 * 60)
def audit_builder_agreements(*args, **kwargs):
    """Perform a daily audit to make sure everything is good to go."""
    from .models import BuilderAgreement
    from .utils import setup_builder_agreement_payment_guages
    from axis.incentive_payment.models import IncentiveDistribution

    log = kwargs.get("log", logger)

    distributions = IncentiveDistribution.objects.filter(status=2, customer__company_type="builder")
    subdivision_tally = {}
    reset_guages = False
    agreements = BuilderAgreement.objects.all()
    if kwargs.get("agreement_id"):
        agreements = agreements.filter(id=kwargs.get("agreement_id"))
    for distribution in distributions.all():
        for item in distribution.ippitem_set.all():
            builder = item.home_status.home.get_builder()
            subdivision = item.home_status.home.subdivision
            if (builder, subdivision) not in subdivision_tally.keys():
                subdivision_tally[(builder, subdivision)] = []
            subdivision_tally[(builder, subdivision)].append(item)

    for agreement in agreements:
        log.info("Reviewing {}".format(agreement))
        key = (agreement.builder_org, agreement.subdivision)
        values = next((v for k, v in subdivision_tally.items() if k == key), [])
        # Take into account the Program
        eep_ids = list(agreement.eep_programs.all().values_list("id", flat=True))
        values = [i for i in values if i.home_status.eep_program.id in eep_ids]
        if agreement.lots_paid != len(values):
            log.info(
                "Discrepancy Found - {} {} != {}".format(
                    agreement, agreement.lots_paid, len(values)
                )
            )
            agreement.lots_paid = len(values)
            agreement.save()
            reset_guages = True
    if reset_guages:
        setup_builder_agreement_payment_guages(purge=True)


@shared_task(time_limit=60 * 60 * 2, bind=True)
def export_status_report(self, result_object_id, **kwargs):
    """Validates and then imports a checklist ``document``."""
    from axis.filehandling.models import AsynchronousProcessedDocument

    kwargs["task"] = self

    from axis.filehandling.log_storage import LogStorage

    app_log = LogStorage(model_id=result_object_id)

    result_object = AsynchronousProcessedDocument.objects.get(id=result_object_id)

    user_id = kwargs.get("user_id", None)
    user = User.objects.get(id=user_id) if user_id else None

    msg = "{user} requested builder agreement export task [{task_id}]"
    app_log.info(msg.format(user=user.get_full_name(), task_id=result_object.task_id))

    from .export_data import BuilderAgreementXLSExport

    export = BuilderAgreementXLSExport(log=app_log, **kwargs)
    new_filename = tempfile.NamedTemporaryFile(
        delete=True, suffix=".xlsx", prefix="Builder_Information_Report_"
    )
    export.write(output=new_filename)

    app_log.info("New file saved %s", os.path.basename(new_filename.name))
    new_filename.seek(0)

    result_object.document = File(new_filename, name=os.path.basename(new_filename.name))
    result_object.save()

    messages.BuilderAgreementExportCompletedMessage(url=result_object.get_absolute_url()).send(
        user=user
    )

    app_log.update_model(throttle_seconds=None)
    return
