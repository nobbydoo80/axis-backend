"""tasks.py: Django customer_neea"""


import os
import tempfile

from celery import shared_task
from celery.utils.log import get_task_logger
from django.contrib.auth import get_user_model
from django.core.files import File
from django.urls import reverse
from django.utils import timezone

from axis.company.models import Company
from axis.eep_program.models import EEPProgram
from axis.filehandling.log_storage import LogStorage
from axis.filehandling.models import AsynchronousProcessedDocument
from . import messages
from .reports import NEEAHomeDataRawExport, NEEAHomeDataCustomExport, NEEAHomeDataBPAExport

__author__ = "Steven Klass"
__date__ = "7/29/13 9:46 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

from .utils import NEEA_BPA_SLUGS

logger = get_task_logger(__name__)
User = get_user_model()


def _export_file(report_class, prefix, result_object_id, **kwargs):
    app_log = LogStorage(model_id=result_object_id)

    result_object = AsynchronousProcessedDocument.objects.get(id=result_object_id)

    user_id = kwargs.get("user_id", None)
    user = User.objects.get(id=user_id) if user_id else None

    msg = "{user} requested home data export task {task} [{task_id}]"
    app_log.info(msg.format(user=user, task=result_object.task_name, task_id=result_object.task_id))

    export = report_class(log=app_log, **kwargs)
    new_filename = tempfile.NamedTemporaryFile(delete=True, suffix=".xlsx", prefix=prefix)
    export.write(output=new_filename)

    app_log.info("New file saved %s", os.path.basename(new_filename.name))
    new_filename.seek(0)

    result_object.document = File(new_filename, name=os.path.basename(new_filename.name))
    result_object.save()

    app_log.update_model(throttle_seconds=None)

    return locals()


@shared_task(time_limit=20000, bind=True)
def export_home_data_raw_task(self, result_object_id, **kwargs):
    """Validates and then imports a checklist ``document``."""

    kwargs["task"] = self
    results = _export_file(
        NEEAHomeDataRawExport, "Home-Utility-Status-Export_", result_object_id, **kwargs
    )

    user = results["user"]
    result_object = results["result_object"]

    messages.NeeaHomeUtilityStatusRawExportCompletedMessage(
        url=result_object.get_absolute_url()
    ).send(user=user)


@shared_task(time_limit=20000, bind=True)
def export_home_data_custom_task(self, result_object_id, **kwargs):
    """Validates and then imports a checklist ``document``."""

    kwargs["task"] = self
    results = _export_file(
        NEEAHomeDataCustomExport, "Home-Utility-NEEA-Export_", result_object_id, **kwargs
    )

    user = results["user"]
    result_object = results["result_object"]

    messages.NeeaHomeUtilityStatusCustomExportCompletedMessage(
        url=result_object.get_absolute_url()
    ).send(user=user)


@shared_task(time_limit=20000, bind=True)
def export_home_data_bpa_task(self, result_object_id, **kwargs):
    """Validates and then imports a checklist ``document``."""

    kwargs["task"] = self
    prefix = "Performance-Path-Calculator-Summary-Report_%s_" % timezone.now().date().strftime(
        "%m-%d-%Y"
    )
    results = _export_file(NEEAHomeDataBPAExport, prefix, result_object_id, **kwargs)

    user = results["user"]
    result_object = results["result_object"]

    messages.NeeaHomeUtilityStatusBPAExportCompletedMessage(
        url=result_object.get_absolute_url()
    ).send(user=user)


@shared_task(bind=True)
def issue_monthly_bpa_utility_reports_to_bpa_utilities_task(self, **kwargs):
    kwargs["task"] = self

    bpa_utilities = Company.objects.filter(
        **{
            "sponsors__slug": "bpa",
            "company_type": "utility",
            "is_active": True,
            "users__is_company_admin": True,
            "users__is_active": True,
        }
    ).distinct()
    utility_names = list(bpa_utilities.values_list("name", flat=True))

    logger.info(
        "Generating monthly BPA utility reports for %d companies: %r"
        % (len(utility_names), utility_names)
    )

    for utility in bpa_utilities:
        issue_monthly_bpa_utility_report_to_company_task.delay(
            **{
                "utility_id": utility.id,
            }
        )


@shared_task(bind=True)
def issue_monthly_bpa_utility_report_to_company_task(self, utility_id, **kwargs):
    from .forms import HomeStatusUtilityBPAReportForm

    kwargs["task"] = self

    # 'qs' variables saved for convenience in form field initializations
    neea_bpa_program_qs = EEPProgram.objects.filter(slug__in=NEEA_BPA_SLUGS)
    utility_qs = Company.objects.filter(id=utility_id)
    utility = utility_qs.get()

    now = timezone.now()
    last_day_in_period = now.replace(day=1) - timezone.timedelta(days=1)
    year = last_day_in_period.year
    month = last_day_in_period.month
    last_day = last_day_in_period.day

    report_filters = {
        "utility": [utility.id],
        "eep_program": [program.id for program in neea_bpa_program_qs.all()],
        "state": "complete",
        "activity_start": "%d/01/%d" % (month, year),
        "activity_stop": "%d/%d/%d" % (month, last_day, year),
        "certification_only": True,
    }
    kwargs.update(report_filters)

    filename_prefix = "Monthly-Performance-Path-Calculator-Summary-Report_%s_%s_" % (
        report_filters["activity_start"].replace("/", "-"),
        report_filters["activity_stop"].replace("/", "-"),
    )

    form = HomeStatusUtilityBPAReportForm(data=report_filters)
    # Fix field querysets that are empty by default
    form.fields["utility"].queryset = utility_qs
    form.fields["eep_program"].queryset = neea_bpa_program_qs

    if not form.is_valid():
        logger.error("Filter form errors for %r: %r", utility.name, form.errors)
        return

    logger.info("Starting monthly report generation for %r: %r", utility.name, report_filters)

    report_user = utility.users.filter(is_company_admin=True).first()
    kwargs["user_id"] = report_user.id

    result_object = form.save(commit=False)
    result_object.company = utility
    result_object.task_name = self.name
    result_object.save()

    results = _export_file(NEEAHomeDataBPAExport, filename_prefix, result_object.id, **kwargs)
    result_object = results["result_object"]

    download_url = reverse("async_document_download", kwargs={"pk": result_object.id})
    messages.NeeaMonthlyHomeUtilityStatusBPAExportAvailableMessage(url=download_url).send(
        company=utility,
        context={
            "year": year,
            "month": last_day_in_period.strftime("%B"),
            "url": download_url,
        },
    )
