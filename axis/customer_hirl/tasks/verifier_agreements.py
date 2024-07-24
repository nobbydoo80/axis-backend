"""verifier_agreements.py: """

__author__ = "Artem Hruzd"
__date__ = "10/08/2020 20:37"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from celery import shared_task
from celery.utils.log import get_task_logger
from django.contrib.auth import get_user_model
from axis.customer_hirl.verifier_agreements.docusign import (
    UnsignedVerifierAgreement,
    UnsignedVerifierAgreementV2,
    UnsignedOfficerAgreement,
    UnsignedOfficerAgreementV2,
    CountersigningVerifierAgreement,
    CountersigningVerifierAgreementV2,
)
from axis.customer_hirl.verifier_agreements.messages.verifier import (
    VerifierLegalAgreementReadyForSigningMessage,
    OfficerLegalAgreementReadyForSigningMessage,
)
from axis.customer_hirl.verifier_agreements.messages.owner import (
    VerifierLegalAgreementReadyForCountersigningMessage,
)
from axis.customer_hirl.models import VerifierAgreement
from axis.customer_hirl.verifier_agreements.states import VerifierAgreementStates
from django.utils import timezone

log = get_task_logger(__name__)
User = get_user_model()


@shared_task
def post_agreement_for_verifier_signing_task(agreement_id, customer_document_id):
    """Send target `customer_document` to the DocuSign backend for enrollee `user` to sign.
    The DocuSign api response and related JSON info is kept in `agreement.data`.
    """

    agreement = VerifierAgreement.objects.get(id=agreement_id)
    version = agreement.get_va_version_to_sign()

    # Start DocuSign workflow
    customer_document = agreement.customer_documents.get(id=customer_document_id)

    document = UnsignedVerifierAgreement()
    if version == 2:
        document = UnsignedVerifierAgreementV2()

    result = document.create_envelope(
        customer_document=customer_document,
        return_filename="Verifier Signed Agreement",
        verifier=agreement.verifier,
    )

    agreement.verifier_agreement_docusign_data.update(
        {
            "envelope_id": result["envelopeId"],
            "unsigned_upload_result": result,
            "signed_upload_result": None,
            "latest_result": None,
        }
    )
    agreement.save(update_fields=["verifier_agreement_docusign_data"])  # Due to async behavior

    VerifierLegalAgreementReadyForSigningMessage(url=agreement.get_absolute_url()).send(
        user=agreement.verifier,
        context={
            "owner": agreement.owner,
            "email": agreement.verifier.email,
        },
    )
    return "Customer document %d has been posted to DocuSign with envelope Id %s" % (
        agreement_id,
        result["envelopeId"],
    )


@shared_task
def update_verifier_signed_status_from_docusign_task(agreement_id=None):
    """Poll DocuSign for status updates for recorded envelope ids."""

    agreements = VerifierAgreement.objects.filter(
        verifier_signed_agreement__isnull=True,
        verifier_agreement_docusign_data__envelope_id__isnull=False,
    )
    if agreement_id:
        agreements = agreements.filter(pk=agreement_id)

    envelope_ids = {}
    for agreement in agreements:
        try:
            envelope_ids[agreement.verifier_agreement_docusign_data["envelope_id"]] = agreement
        except KeyError:
            log.error("envelopeId not found on Verifier Agreement %(pk)s", {"pk": agreement.pk})

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

    document = UnsignedVerifierAgreement()

    results = document.get_envelope_statuses(list(envelope_ids.keys()))
    for result in results.get("envelopes", []):
        agreement = envelope_ids[result["envelopeId"]]
        latest_result = document.get_envelope_signing_status(result["envelopeId"])
        agreement.verifier_agreement_docusign_data.update({"latest_result": latest_result})
        update_fields = ["verifier_agreement_docusign_data", "state"]
        if result["status"] == "completed":
            # Ok lets' get the documents
            docs = document.get_completed_documents(result["envelopeId"])
            sign_doc = next((_x["document"] for _x in docs if _x["type"] == "content"), None)
            sign_url = next((_x["uri"] for _x in docs if _x["type"] == "content"), None)
            agreement.verifier_agreement_docusign_data.update({"signed_upload_result": sign_url})
            if sign_doc:
                update_fields.append("verifier_signed_agreement")

            cert_doc = next((_x["document"] for _x in docs if _x["type"] == "summary"), None)
            if cert_doc:
                update_fields.append("verifier_certifying_document")

            agreement.receive_verifier_signed_document(sign_doc, cert_doc)

        agreement.save(update_fields=update_fields)

    if len(results.get("envelopes", [])) != len(envelope_ids.keys()):
        have = [x["envelopeId"] for x in results.get("envelopes")]
        _missing = list(set(have) - set(envelope_ids.keys()))
        missing = {envelope_ids[env].id: env for env in _missing}
        if missing:
            msg = "Unable to find a response for envelopes: %r (agreement_id: envelop)r"
            log.warning(msg, missing)

    return latest_result if agreement_id else results


@shared_task
def post_agreement_for_officer_signing_task(agreement_id, customer_document_id):
    """Send target `customer_document` to the DocuSign backend for enrollee `officer` to sign.
    The DocuSign api response and related JSON info is kept in
    `agreement.verifier_agreement_docusign_data`.
    """

    agreement = VerifierAgreement.objects.get(id=agreement_id)
    version = agreement.get_va_version_to_sign()

    # Start DocuSign workflow
    customer_document = agreement.customer_documents.get(id=customer_document_id)

    document = UnsignedOfficerAgreement()
    if version == 2:
        document = UnsignedOfficerAgreementV2()

    # create a User object from officer data, because `create_envelope` function requires it
    officer = User(
        first_name=agreement.company_officer_first_name,
        last_name=agreement.company_officer_last_name,
        title=agreement.company_officer_title,
        email=agreement.company_officer_email,
        work_phone=agreement.company_officer_phone_number,
    )
    result = document.create_envelope(
        customer_document=customer_document,
        officer=officer,
        return_filename="Officer Signed Agreement",
    )

    agreement.officer_agreement_docusign_data.update(
        {
            "envelope_id": result["envelopeId"],
            "unsigned_upload_result": result,
            "signed_upload_result": None,
            "latest_result": None,
        }
    )
    agreement.save(update_fields=["officer_agreement_docusign_data"])  # Due to async behavior

    OfficerLegalAgreementReadyForSigningMessage(url=agreement.get_absolute_url()).send(
        user=agreement.verifier,
        context={
            "owner": agreement.owner,
            "email": agreement.company_officer_email,
        },
    )
    return "Customer document %d has been posted to DocuSign with envelope Id %s" % (
        agreement_id,
        result["envelopeId"],
    )


@shared_task
def update_officer_signed_status_from_docusign_task(agreement_id=None):
    """Poll DocuSign for status updates for recorded envelope ids."""

    agreements = VerifierAgreement.objects.filter(
        officer_signed_agreement__isnull=True,
        officer_agreement_docusign_data__envelope_id__isnull=False,
    )
    if agreement_id:
        agreements = agreements.filter(pk=agreement_id)

    envelope_ids = {}
    for agreement in agreements:
        try:
            envelope_ids[agreement.officer_agreement_docusign_data["envelope_id"]] = agreement
        except KeyError:
            log.error("envelopeId not found on Verifier Agreement %(pk)s", {"pk": agreement.pk})

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

    document = UnsignedOfficerAgreement()

    results = document.get_envelope_statuses(list(envelope_ids.keys()))
    for result in results.get("envelopes", []):
        agreement = envelope_ids[result["envelopeId"]]
        latest_result = document.get_envelope_signing_status(result["envelopeId"])
        agreement.verifier_agreement_docusign_data.update({"latest_result": latest_result})
        update_fields = ["officer_agreement_docusign_data", "state"]
        if result["status"] == "completed":
            # Ok lets' get the documents
            docs = document.get_completed_documents(result["envelopeId"])
            sign_doc = next((_x["document"] for _x in docs if _x["type"] == "content"), None)
            sign_url = next((_x["uri"] for _x in docs if _x["type"] == "content"), None)
            agreement.verifier_agreement_docusign_data.update({"signed_upload_result": sign_url})
            if sign_doc:
                update_fields.append("officer_signed_agreement")

            cert_doc = next((_x["document"] for _x in docs if _x["type"] == "summary"), None)
            if cert_doc:
                update_fields.append("officer_certifying_document")

            agreement.receive_officer_signed_document(sign_doc, cert_doc)

        agreement.save(update_fields=update_fields)

    if len(results.get("envelopes", [])) != len(envelope_ids.keys()):
        have = [x["envelopeId"] for x in results.get("envelopes")]
        _missing = list(set(have) - set(envelope_ids.keys()))
        missing = {envelope_ids[env].id: env for env in _missing}
        if missing:
            msg = "Unable to find a response for envelopes: %r (agreement_id: envelop)r"
            log.warning(msg, missing)

    return latest_result if agreement_id else results


@shared_task
def post_verifier_agreement_for_owner_countersigning_task(agreement_id, customer_document_id):
    """Send target `customer_document` to the DocuSign backend for enrollee `user` to sign.
    The DocuSign api response and related JSON info is kept in
    `agreement.hirl_agreement_docusign_data`.
    """
    agreement = VerifierAgreement.objects.get(id=agreement_id)
    version = agreement.get_va_version_to_sign()

    # Start DocuSign workflow
    countersigning_user = agreement.get_countersigning_user()
    customer_document = agreement.customer_documents.get(id=customer_document_id)

    document = CountersigningVerifierAgreement()
    if version == 2:
        document = CountersigningVerifierAgreementV2()

    result = document.create_envelope(
        customer_document=customer_document,
        countersigning_user=countersigning_user,
        return_filename="Countersigned Agreement",
    )

    agreement.hirl_agreement_docusign_data.update(
        {
            "envelope_id": result["envelopeId"],
            "countersigning_upload_result": result,
            "countersigned_upload_result": None,
            "latest_result": None,
        }
    )
    agreement.save(update_fields=["hirl_agreement_docusign_data"])  # Due to async behavior

    VerifierLegalAgreementReadyForCountersigningMessage(url=agreement.get_absolute_url()).send(
        user=agreement.get_countersigning_user(),
        context={
            "verifier": agreement.verifier,
            "email": countersigning_user.email,
        },
    )
    return "Customer document %d has been posted to DocuSign with envelope Id %s" % (
        agreement_id,
        result["envelopeId"],
    )


@shared_task
def update_verifier_countersigned_status_from_docusign_task(agreement_id=None):
    """Poll DocuSign for status updates for recorded envelope ids."""

    agreements = VerifierAgreement.objects.filter(state=VerifierAgreementStates.VERIFIED)
    if agreement_id:
        agreements = agreements.filter(pk=agreement_id)

    envelope_ids = {}
    for agreement in agreements:
        try:
            envelope_ids[agreement.hirl_agreement_docusign_data["envelope_id"]] = agreement
        except KeyError:
            log.error("envelopeId not found on Verifier Agreement %(pk)s", {"pk": agreement.pk})

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

    document = CountersigningVerifierAgreement()

    results = document.get_envelope_statuses(list(envelope_ids.keys()))
    for result in results.get("envelopes", []):
        agreement = envelope_ids[result["envelopeId"]]
        latest_result = document.get_envelope_signing_status(result["envelopeId"])
        agreement.hirl_agreement_docusign_data.update({"latest_result": latest_result})
        update_fields = ["hirl_agreement_docusign_data", "state"]
        if result["status"] == "completed":
            # Ok lets' get the documents
            docs = document.get_completed_documents(result["envelopeId"])
            sign_doc = next((_x["document"] for _x in docs if _x["type"] == "content"), None)
            sign_url = next((_x["uri"] for _x in docs if _x["type"] == "content"), None)
            agreement.hirl_agreement_docusign_data.update({"countersigned_upload_result": sign_url})
            if sign_doc:
                update_fields.append("hirl_signed_agreement")

            cert_doc = next((_x["document"] for _x in docs if _x["type"] == "summary"), None)
            if cert_doc:
                update_fields.append("hirl_certifying_document")

            agreement.countersign(sign_doc, cert_doc)

        agreement.save(update_fields=update_fields)

    if len(results.get("envelopes", [])) != len(envelope_ids.keys()):
        have = [x["envelopeId"] for x in results.get("envelopes")]
        _missing = list(set(have) - set(envelope_ids.keys()))
        missing = {envelope_ids[env].id: env for env in _missing}
        if missing:
            msg = "Unable to find a response for envelopes: %r (agreement_id: envelop)r"
            log.warning(msg, missing)

    return latest_result if agreement_id else results


@shared_task
def verifier_agreement_expire_notification_warning_task(days_before_expire=60):
    """Issue timed notifications. This should be called daily."""
    from axis.customer_hirl.models import VerifierAgreement
    from axis.customer_hirl.verifier_agreements.messages.owner import (
        VerifierAgreementExpirationWarningMessage,
    )

    # sending agreement expiration warning
    verifier_agreements = VerifierAgreement.objects.filter(
        agreement_expiration_date=timezone.now().date()
        + timezone.timedelta(days=days_before_expire)
    ).exclude(state=VerifierAgreementStates.EXPIRED)

    for verifier_agreement in verifier_agreements:
        msg_context = {
            "verifier": verifier_agreement.verifier,
            "days": days_before_expire,
            "url": verifier_agreement.get_absolute_url(),
        }
        admins = verifier_agreement.owner.users.filter(is_company_admin=True)
        if admins:
            VerifierAgreementExpirationWarningMessage().send(
                users=admins,
                context=msg_context,
            )

        verifier_message = VerifierAgreementExpirationWarningMessage()
        verifier_message.content = (
            'Agreement is expiring in {days} days. <a href="{url}">Manage the agreement.</a>'
        )
        verifier_message.send(
            user=verifier_agreement.verifier,
            context=msg_context,
        )


@shared_task
def verifier_agreement_expire_task():
    """Issue timed notifications. This should be called daily."""
    from axis.customer_hirl.models import VerifierAgreement

    verifier_agreements = VerifierAgreement.objects.filter(
        agreement_expiration_date__lte=timezone.now().date()
    ).exclude(state=VerifierAgreementStates.EXPIRED)

    for verifier_agreement in verifier_agreements:
        verifier_agreement.expire()
        verifier_agreement.save()
