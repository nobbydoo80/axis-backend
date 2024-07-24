__author__ = "Artem Hruzd"
__date__ = "10/08/2020 20:21"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from celery import shared_task
from celery.utils.log import get_task_logger
from django.db.models import Q

from axis.customer_hirl.models import BuilderAgreement
from axis.customer_hirl.builder_agreements.messages.builder import (
    BuilderAgreementExpirationWarningMessage,
    LegalAgreementReadyForSigningMessage,
)
from axis.customer_hirl.builder_agreements.messages.owner import (
    AgreementExpirationWarningMessage,
)
from axis.customer_hirl.builder_agreements import docusign
from django.utils import timezone

log = get_task_logger(__name__)


def _check_missing_envelope_ids(
    docusign_response_result: dict, envelope_ids: dict, warning_message: str
):
    """
    Send a warning message to a production channel in tasks that periodically check Docusign document status
    :param docusign_response_result: Response result
    :param envelope_ids: Dictionary with envelope ID as a key, and envelope data as a value
    :param warning_message: Str message, can accept formatting
    """
    if len(docusign_response_result.get("envelopes", [])) != len(envelope_ids.keys()):
        have = [x["envelopeId"] for x in docusign_response_result.get("envelopes")]
        _missing = list(set(have) - set(envelope_ids.keys()))
        missing = {envelope_ids[env].id: env for env in _missing}
        if missing:
            log.warning(warning_message, missing)


@shared_task
def post_agreement_for_builder_signing_task(agreement_id, customer_document_id):
    """Send target `customer_document` to the DocuSign backend for enrollee `user` to sign.
    The DocuSign api response and related JSON info is kept in `agreement.data`.
    """

    agreement = BuilderAgreement.objects.get(id=agreement_id)
    version = agreement.get_ca_version_to_sign()

    # Start DocuSign workflow
    signing_user = agreement.get_signing_user()
    customer_document = agreement.customer_documents.get(id=customer_document_id)

    document = docusign.UnsignedBuilderAgreement()
    if version == 2:
        document = docusign.UnsignedBuilderAgreementV2()
    if version == 3:
        document = docusign.UnsignedBuilderAgreementV3()
    if version == 4:
        document = docusign.UnsignedBuilderAgreementV4()

    carbon_copies_users = []
    if agreement.initiator:
        carbon_copies_users.append(agreement.initiator)

    result = document.create_envelope(
        customer_document=customer_document,
        user=signing_user,
        return_filename="Signed Agreement",
        company=agreement.company,
        carbon_copies_users=carbon_copies_users,
    )

    agreement.data.update(
        {
            "envelope_id": result["envelopeId"],
            "unsigned_upload_result": result,
            "signed_upload_result": None,
            "latest_result": None,
        }
    )
    agreement.save(update_fields=["data"])  # Due to async behavior

    LegalAgreementReadyForSigningMessage(url=agreement.get_absolute_url()).send(
        company=agreement.company,
        context={
            "owner": agreement.owner,
            "email": signing_user.email,
        },
    )
    return "Customer document %d has been posted to DocuSign with envelope Id %s" % (
        agreement_id,
        result["envelopeId"],
    )


@shared_task
def post_agreement_for_owner_countersigning_task(agreement_id, customer_document_id):
    """Send target `customer_document` to the DocuSign backend for enrollee `user` to sign.
    The DocuSign api response and related JSON info is kept in `agreement.data`.
    """

    from axis.customer_hirl.models import BuilderAgreement
    from axis.customer_hirl.builder_agreements import messages

    agreement = BuilderAgreement.objects.get(id=agreement_id)
    version = agreement.get_ca_version_to_sign()

    # Start DocuSign workflow
    countersigning_user = agreement.get_countersigning_user()
    customer_document = agreement.customer_documents.get(id=customer_document_id)

    document = docusign.CountersigningBuilderAgreement()
    if version == 2:
        document = docusign.CountersigningBuilderAgreementV2()
    if version == 3:
        document = docusign.CountersigningBuilderAgreementV3()
    if version == 4:
        document = docusign.CountersigningBuilderAgreementV4()

    result = document.create_envelope(
        customer_document=customer_document,
        user=countersigning_user,
        return_filename="Countersigned Agreement",
        company=agreement.company,
    )

    agreement.data.update(
        {
            "envelope_id": result["envelopeId"],
            "countersigning_upload_result": result,
            "countersigned_upload_result": None,
            "latest_result": None,
        }
    )
    agreement.save(update_fields=["data"])  # Due to async behavior

    messages.owner.LegalAgreementReadyForCountersigningMessage(
        url=agreement.get_absolute_url()
    ).send(
        user=agreement.get_countersigning_user(),
        context={
            "company": agreement.company,
            "email": countersigning_user.email,
        },
    )
    return "Customer document %d has been posted to DocuSign with envelope Id %s" % (
        agreement_id,
        result["envelopeId"],
    )


@shared_task(time_limit=60 * 6)
def update_signed_status_from_docusign_task(agreement_id=None):
    """Poll DocuSign for status updates for recorded envelope ids."""

    agreements = BuilderAgreement.objects.filter(
        signed_agreement__isnull=True, data__envelope_id__isnull=False
    ).exclude(
        Q(
            data__latest_result__source__status__isnull=False,
            data__latest_result__source__status="voided",
        )
    )

    if agreement_id:
        agreements = agreements.filter(pk=agreement_id)

    envelope_ids = {}
    for agreement in agreements:
        try:
            envelope_ids[agreement.data["envelope_id"]] = agreement
        except KeyError:
            log.error("envelopeId not found on Builder Agreement %(pk)s", {"pk": agreement.pk})

    latest_result = {
        "status": "error",
        "status_message": "Unknown",
        "signed": "Unknown",
        "waiting_on": "Unknown",
        "remaining_signers": ["Unknown"],
    }

    if not envelope_ids:
        latest_result["status_message"] = "No envelope id found"
        return latest_result

    document = docusign.UnsignedBuilderAgreement()

    results = document.get_envelope_statuses(list(envelope_ids.keys()))
    for result in results.get("envelopes", []):
        agreement = envelope_ids[result["envelopeId"]]
        latest_result = document.get_envelope_signing_status(result["envelopeId"])
        agreement.data.update({"latest_result": latest_result})
        update_fields = ["data", "state"]
        if result["status"] == "completed":
            # Ok lets' get the documents
            docs = document.get_completed_documents(result["envelopeId"])
            sign_doc = next((_x["document"] for _x in docs if _x["type"] == "content"), None)
            sign_url = next((_x["uri"] for _x in docs if _x["type"] == "content"), None)
            agreement.data.update({"signed_upload_result": sign_url})
            if sign_doc:
                update_fields.append("signed_agreement")

            cert_doc = next((_x["document"] for _x in docs if _x["type"] == "summary"), None)
            if cert_doc:
                update_fields.append("certifying_document")

            agreement.receive_signed_document(sign_doc, cert_doc)

        agreement.save(update_fields=update_fields)

    _check_missing_envelope_ids(
        docusign_response_result=results,
        envelope_ids=envelope_ids,
        warning_message="Unable to find a response for envelopes: %r (agreement_id: envelop)r",
    )

    return latest_result if agreement_id else results


@shared_task
def update_countersigned_status_from_docusign_task(agreement_id=None):
    """Poll DocuSign for status updates for recorded envelope ids."""

    agreements = BuilderAgreement.objects.filter(state=BuilderAgreement.VERIFIED)
    if agreement_id:
        agreements = agreements.filter(pk=agreement_id)

    envelope_ids = {}
    for agreement in agreements:
        try:
            envelope_ids[agreement.data["envelope_id"]] = agreement
        except KeyError:
            log.error("envelopeId not found on Builder Agreement %(pk)s", {"pk": agreement.pk})

    latest_result = {
        "status": "error",
        "status_message": "Unknown",
        "signed": "Unknown",
        "waiting_on": "Unknown",
        "remaining_signers": ["Unknown"],
    }

    if not envelope_ids:
        latest_result["status_message"] = "No envelope id found"
        return latest_result

    document = docusign.CountersigningBuilderAgreement()

    results = document.get_envelope_statuses(list(envelope_ids.keys()))
    for result in results.get("envelopes", []):
        agreement = envelope_ids[result["envelopeId"]]
        latest_result = document.get_envelope_signing_status(result["envelopeId"])
        agreement.data.update({"latest_result": latest_result})
        update_fields = ["data", "state"]
        if result["status"] == "completed":
            # Ok lets' get the documents
            docs = document.get_completed_documents(result["envelopeId"])
            sign_doc = next((_x["document"] for _x in docs if _x["type"] == "content"), None)
            sign_url = next((_x["uri"] for _x in docs if _x["type"] == "content"), None)
            agreement.data.update({"countersigned_upload_result": sign_url})
            if sign_doc:
                update_fields.append("signed_agreement")

            cert_doc = next((_x["document"] for _x in docs if _x["type"] == "summary"), None)
            if cert_doc:
                update_fields.append("certifying_document")

            agreement.countersign(sign_doc, cert_doc)

        agreement.save(update_fields=update_fields)

    _check_missing_envelope_ids(
        docusign_response_result=results,
        envelope_ids=envelope_ids,
        warning_message="Unable to find a response for envelopes: %r (agreement_id: envelop)r",
    )
    return latest_result if agreement_id else results


@shared_task
def builder_agreement_expire_notification_warning_task(days_before_expire=60):
    """Issue timed notifications. This should be called daily."""

    builder_agreements = BuilderAgreement.objects.filter(
        agreement_expiration_date=timezone.now().date()
        + timezone.timedelta(days=days_before_expire)
    ).exclude(state=BuilderAgreement.EXPIRED)

    for builder_agreement in builder_agreements:
        AgreementExpirationWarningMessage().send(
            company=builder_agreement.owner,
            context={
                "company": builder_agreement.company,
                "url": builder_agreement.company.get_absolute_url(),
                "days": days_before_expire,
            },
        )
        BuilderAgreementExpirationWarningMessage().send(
            company=builder_agreement.company,
            context={
                "owner": builder_agreement.owner,
                "url": builder_agreement.company.get_absolute_url(),
                "days": days_before_expire,
            },
        )


@shared_task
def builder_agreement_expire_task():
    """Issue timed notifications. This should be called daily."""
    from axis.customer_hirl.models import BuilderAgreement

    builder_agreements = BuilderAgreement.objects.filter(
        agreement_expiration_date__lte=timezone.now().date()
    ).exclude(state=BuilderAgreement.EXPIRED)

    for builder_agreement in builder_agreements:
        builder_agreement.expire()
        builder_agreement.save()


@shared_task
def post_client_agreement_extension_request_signing_task(agreement_id, customer_document_id):
    """
    Send target `customer_document` to the DocuSign backend for enrollee `user` to sign extension request.
    The DocuSign api response and related JSON info is kept in `agreement.extension_request_data`.
    """

    from axis.customer_hirl.models import BuilderAgreement

    agreement = BuilderAgreement.objects.get(id=agreement_id)

    # Start DocuSign workflow
    signing_user = agreement.get_signing_user()
    customer_document = agreement.customer_documents.get(id=customer_document_id)

    document = docusign.UnsignedExtensionRequestAgreement()

    carbon_copies_users = []
    if agreement.initiator:
        carbon_copies_users.append(agreement.initiator)

    result = document.create_envelope(
        customer_document=customer_document,
        user=signing_user,
        return_filename="Signed Extension Request Agreement",
        company=agreement.company,
        carbon_copies_users=carbon_copies_users,
    )

    agreement.extension_request_data.update(
        {
            "envelope_id": result["envelopeId"],
            "unsigned_upload_result": result,
            "signed_upload_result": None,
            "latest_result": None,
        }
    )
    agreement.save(update_fields=["extension_request_data"])  # Due to async behavior


@shared_task(time_limit=60 * 6)
def update_extension_request_signed_status_from_docusign_task(agreement_id=None):
    """Poll DocuSign for status updates for extension request updates"""

    agreements = BuilderAgreement.objects.filter(
        extension_request_signed_agreement__isnull=True,
        extension_request_data__envelope_id__isnull=False,
    ).exclude(
        Q(
            extension_request_data__latest_result__source__status__isnull=False,
            extension_request_data__latest_result__source__status="voided",
        )
    )

    if agreement_id:
        agreements = agreements.filter(pk=agreement_id)

    envelope_ids = {}
    for agreement in agreements:
        try:
            envelope_ids[agreement.extension_request_data["envelope_id"]] = agreement
        except KeyError:
            log.error(
                "extension_request_data envelopeId not found on Builder Agreement %(pk)s",
                {"pk": agreement.pk},
            )

    latest_result = {
        "status": "error",
        "status_message": "Unknown",
        "signed": "Unknown",
        "waiting_on": "Unknown",
        "remaining_signers": ["Unknown"],
    }

    if not envelope_ids:
        latest_result["status_message"] = "No envelope id found"
        return latest_result

    document = docusign.UnsignedBuilderAgreement()

    results = document.get_envelope_statuses(list(envelope_ids.keys()))
    today = timezone.now().today()

    for result in results.get("envelopes", []):
        agreement = envelope_ids[result["envelopeId"]]
        latest_result = document.get_envelope_signing_status(result["envelopeId"])
        agreement.extension_request_data.update({"latest_result": latest_result})
        update_fields = ["extension_request_data", "extension_request_state"]
        if result["status"] == "completed":
            # Ok lets' get the documents
            docs = document.get_completed_documents(result["envelopeId"])
            sign_doc = next((_x["document"] for _x in docs if _x["type"] == "content"), None)
            sign_url = next((_x["uri"] for _x in docs if _x["type"] == "content"), None)
            agreement.extension_request_data.update({"signed_upload_result": sign_url})
            if sign_doc:
                update_fields.append("extension_request_signed_agreement")

            agreement.extension_request_signed_agreement = agreement.customer_documents.store(
                agreement,
                company=agreement.company,
                filename=f"Signed Extension Request ({today}).pdf",
                description=f"Signed Extension Request document ({today})",
                document=sign_doc,
            )

            cert_doc = next((_x["document"] for _x in docs if _x["type"] == "summary"), None)
            if cert_doc:
                update_fields.append("extension_request_certifying_document")

            agreement.extension_request_certifying_document = agreement.customer_documents.store(
                agreement,
                company=agreement.company,
                filename=f"Signed Extension Certifying Request ({today}).pdf",
                description=f"Signed Extension Request Certifying document ({today})",
                document=cert_doc,
            )

            agreement.save(update_fields=update_fields)

            # save new state
            agreement.send_for_countersign_extension_request()
            agreement.save(update_fields=["extension_request_state"])
        else:
            agreement.save(update_fields=update_fields)

    _check_missing_envelope_ids(
        docusign_response_result=results,
        envelope_ids=envelope_ids,
        warning_message="Unable to find a response for extension_request envelopes: %r (agreement_id: envelop)r",
    )
    return latest_result if agreement_id else results


@shared_task
def post_extension_request_agreement_for_owner_countersigning_task(
    agreement_id, customer_document_id
):
    """
    Send target `customer_document` to the DocuSign backend for NGBS user to countersign.
    The DocuSign api response and related JSON info are kept in `agreement.extension_request_data`.
    """

    from axis.customer_hirl.models import BuilderAgreement
    from axis.customer_hirl.builder_agreements import messages

    agreement = BuilderAgreement.objects.get(id=agreement_id)

    # Start DocuSign workflow
    countersigning_user = agreement.get_countersigning_user()
    customer_document = agreement.customer_documents.get(id=customer_document_id)

    document = docusign.CountersigningExtensionRequestAgreement()

    result = document.create_envelope(
        customer_document=customer_document,
        user=countersigning_user,
        return_filename="Countersigned Extension Request Agreement",
        company=agreement.company,
    )

    agreement.extension_request_data.update(
        {
            "envelope_id": result["envelopeId"],
            "countersigning_upload_result": result,
            "countersigned_upload_result": None,
            "latest_result": None,
        }
    )
    agreement.save(
        update_fields=[
            "extension_request_data",
        ]
    )  # Due to async behavior

    messages.owner.ExtensionRequestAgreementReadyForCountersigningMessage(
        url=agreement.get_absolute_url()
    ).send(
        user=agreement.get_countersigning_user(),
        context={
            "company": agreement.company,
            "email": countersigning_user.email,
        },
    )


@shared_task
def update_countersigned_extension_request_agreement_status_from_docusign_task(agreement_id=None):
    """Poll DocuSign for status updates for recorded envelope ids."""

    from axis.customer_hirl.models import BuilderAgreement

    agreements = BuilderAgreement.objects.filter(
        extension_request_state=BuilderAgreement.EXTENSION_REQUEST_SENT_FOR_COUNTERSIGN,
        extension_request_data__countersigning_upload_result__isnull=False,
    )
    if agreement_id:
        agreements = agreements.filter(pk=agreement_id)

    envelope_ids = {}
    for agreement in agreements:
        try:
            envelope_ids[agreement.extension_request_data["envelope_id"]] = agreement
        except KeyError:
            log.error("envelopeId not found on Builder Agreement %(pk)s", {"pk": agreement.pk})

    latest_result = {
        "status": "error",
        "status_message": "Unknown",
        "signed": "Unknown",
        "waiting_on": "Unknown",
        "remaining_signers": ["Unknown"],
    }

    if not envelope_ids:
        latest_result["status_message"] = "No envelope id found"
        return latest_result

    document = docusign.CountersigningBuilderAgreement()

    results = document.get_envelope_statuses(list(envelope_ids.keys()))
    for result in results.get("envelopes", []):
        agreement = envelope_ids[result["envelopeId"]]
        latest_result = document.get_envelope_signing_status(result["envelopeId"])
        agreement.extension_request_data.update({"latest_result": latest_result})
        update_fields = [
            "extension_request_data",
            "extension_request_state",
            "agreement_start_date",
            "agreement_expiration_date",
        ]
        if result["status"] == "completed":
            # Ok lets' get the documents
            docs = document.get_completed_documents(result["envelopeId"])
            sign_doc = next((_x["document"] for _x in docs if _x["type"] == "content"), None)
            sign_url = next((_x["uri"] for _x in docs if _x["type"] == "content"), None)
            agreement.extension_request_data.update({"countersigned_upload_result": sign_url})
            if sign_doc:
                update_fields.append("extension_request_signed_agreement")

            cert_doc = next((_x["document"] for _x in docs if _x["type"] == "summary"), None)
            if cert_doc:
                update_fields.append("extension_request_certifying_document")

            agreement.countersign_extension_request(
                countersigned_document=sign_doc, countersigned_certify_document=cert_doc
            )

        agreement.save(update_fields=update_fields)

    _check_missing_envelope_ids(
        docusign_response_result=results,
        envelope_ids=envelope_ids,
        warning_message="Unable to find a response for extension request envelopes: %r (agreement_id: envelop)r",
    )
