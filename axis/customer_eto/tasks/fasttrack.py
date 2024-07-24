"""fasttrack.py - Axis"""

__author__ = "Steven K"
__date__ = "8/19/21 12:01"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import datetime
import time
from urllib.error import HTTPError

import requests
import xmltodict
from celery import shared_task
from celery.utils.log import get_task_logger
from django.apps import apps
from django.conf import settings
from rest_framework.exceptions import ValidationError

from axis.company.models import Company
from axis.customer_eto.api_v3.serializers import ProjectTrackerXMLSerializer
from axis.customer_eto.api_v3.viewsets import ProjectTrackerXMLViewSet
from axis.customer_eto.models import ETOAccount
from axis.incentive_payment.models import IncentivePaymentStatus
from axis.customer_eto.enumerations import (
    ProjectTrackerSubmissionStatus,
)
from axis.customer_eto.messages import (
    ProjectTrackerFailedSubmissionMessage,
    ProjectTrackerSuccessSubmissionMessage,
)
from axis.incentive_payment.models import IncentivePaymentStatus

from ..models import FastTrackSubmission

logger = get_task_logger(__name__)
customer_eto_app = apps.get_app_config("customer_eto")


class FastTrackResultException(Exception):
    pass


class FastTrackPostException(Exception):
    pass


fasttrack_headers = {
    "Content-type": "text/xml",
    "SOAPAction": '"http://tempuri.org/FTImportXML"',
}


def handle_failure(
    submission: FastTrackSubmission,
    project_type: str,
    exception: str,
    result: str | None = None,
    source: str | None = None,
    response: str | None = None,
):
    """Generic way to handle submission errors"""
    submit_status_field = "submit_status" if project_type == "ENH" else "solar_submit_status"
    setattr(submission, submit_status_field, ProjectTrackerSubmissionStatus.FAILURE)
    submission.save(update_fields=[submit_status_field, "modified_date"])
    submission.refresh_from_db()

    url = submission.home_status.home.get_absolute_url()

    for slug in [customer_eto_app.CUSTOMER_SLUG, "peci"]:
        ProjectTrackerFailedSubmissionMessage(url=url).send(
            context={
                "home": str(submission.home_status.home),
                "home_url": url,
                "project_type": project_type,
                "attempt": submission.submission_count - 1,
                "exc": exception,
            },
            company=Company.objects.get(slug=slug),
        )
    return {
        "status": ProjectTrackerSubmissionStatus.FAILURE,
        "result": result if result else exception,
        "source": source,
        "count": submission.submission_count,
        "response": response,
    }


@shared_task(
    default_retry_delay=15 * 60, max_retries=3, time_limit=60 * 6, store_errors_even_if_ignored=True
)
def submit_fasttrack_xml(
    home_status_id: int,
    user_id: int = None,
    project_type: str = "ENH",
    only_return_xml: bool = False,
    skip_fasttrack_submit: bool = False,
) -> dict:
    """Submits a home status to FastTrack / ProjectTracker (oldname vs newname)"""
    from axis.home.models import EEPProgramHomeStatus
    from ..models import FastTrackSubmission

    log = logger
    try:
        called_directly = (
            submit_fasttrack_xml.request.is_eager or submit_fasttrack_xml.request.called_directly
        )
    except AttributeError:
        called_directly = True

    # Make sure to ignore eto-qa programs
    home_statuses = EEPProgramHomeStatus.objects.filter(eep_program__owner__slug="eto").exclude(
        eep_program__is_qa_program=True,
    )
    home_status = home_statuses.get(pk=home_status_id)
    submission, _ = FastTrackSubmission.objects.get_or_create(home_status=home_status)

    submit_status_field = "submit_status" if project_type == "ENH" else "solar_submit_status"
    setattr(submission, submit_status_field, ProjectTrackerSubmissionStatus.STARTED)
    submission.submission_count = (
        1 if submission.submission_count is None else submission.submission_count + 1
    )
    update_fields = ["modified_date", "submission_count", submit_status_field]
    if submission.submit_user_id is None and user_id:
        submission.submit_user_id = user_id
        update_fields.append("submit_user_id")

    submission.save(update_fields=update_fields)
    submission.refresh_from_db()

    vs = ProjectTrackerXMLViewSet()
    try:
        context = vs.get_context_data(submission)
    except ValidationError as exc:
        return handle_failure(submission, project_type, exception=str(exc))

    context["project_type"] = project_type
    serializer = ProjectTrackerXMLSerializer(instance=submission, context=context)

    data, project_id, result, response = "No FT Data", "N/A", "N/A", None
    if not skip_fasttrack_submit:
        # We need trap any errors here.
        try:
            data = serializer.data
        except Exception as exc:
            return handle_failure(submission, project_type, exception=str(exc))

        # Do not set pretty here - It may give you \n right after a tag which ETO will barf on.
        data = xmltodict.unparse(data)

        if only_return_xml:
            return data

        start = time.time()
        response = requests.post(
            settings.FASTTRACK_API_ENDPOINT,
            data=data,
            headers=fasttrack_headers,
        )

        # Stop abruptly here if anything is wrong with the status_code
        try:
            response.raise_for_status()
        except HTTPError as exc:
            setattr(submission, submit_status_field, ProjectTrackerSubmissionStatus.RETRY)
            submission.save(update_fields=[submit_status_field, "modified_date"])
            return submit_fasttrack_xml.retry(exc=exc)
        else:
            try:
                _resp = xmltodict.parse(response.content.decode())["soap:Envelope"]["soap:Body"]
                _resp = _resp["FTImportXMLResponse"]["FTImportXMLResult"]
                import_response = _resp["ImportResponse"]
                code = import_response["result"]["code"]
                description = import_response["result"]["desc"]
            except KeyError:
                import_response = {}
                code = "FAILURE"
                description = f"Unable to parse result - {response.content.decode()}"

        stop = time.time()

        if code != "SUCCESS":
            result = f"Fastrack submission {code!r}: {description!r}"
            print(result) if called_directly else log.error(result)
            return handle_failure(
                submission,
                project_type,
                str({"code": code, "description": description}),
                result,
                data,
                response.content.decode(),
            )

        fields = [submit_status_field, "modified_date"]
        project_id = import_response["internalid"]["projects"]["project"]["#text"]
        setattr(submission, submit_status_field, ProjectTrackerSubmissionStatus.SUCCESS)
        if project_type == "ENH":
            submission.project_id = project_id
            fields.append("project_id")
        elif project_type == "SLE":
            submission.solar_project_id = project_id
            fields.append("solar_project_id")
        submission.save(update_fields=fields)

        result = (
            f"{project_type} Project {project_id} ETO submission to {settings.FASTTRACK_API_ENDPOINT} "
            f"took {stop - start:.3f} s"
        )
        log.info(result)

    # Finally add the IPP Status
    created_datetime = datetime.datetime.combine(
        home_status.certification_date, datetime.time()
    ).replace(tzinfo=datetime.timezone.utc)
    ipp_stat, create = IncentivePaymentStatus.objects.get_or_create(
        home_status=home_status,
        defaults=dict(owner=home_status.eep_program.owner, created_on=created_datetime),
    )

    # We need to advance this to lock the edit as it's now in ETO's hands and we don't want users
    # To be able to edit it.
    if ipp_stat.state == "start":
        ipp_stat.make_transition("pending_requirements")

    # Issue messaging for completed item
    url = submission.home_status.home.get_absolute_url()
    for slug in [
        customer_eto_app.CUSTOMER_SLUG,
        "peci",
        submission.home_status.company.slug,
    ]:
        ProjectTrackerSuccessSubmissionMessage(
            url=url,
        ).send(
            context={
                "project_id": project_id,
                "home": str(submission.home_status.home),
                "home_url": url,
                "project_type": project_type,
            },
            company=Company.objects.get(slug=slug),
        )
    return {
        "status": ProjectTrackerSubmissionStatus.SUCCESS,
        "result": result,
        "source": data,
        "count": submission.submission_count,
        "response": response.content.decode() if response else "N/A",
    }
