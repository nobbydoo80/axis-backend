"""docusign.py - Axis"""

__author__ = "Steven K"
__date__ = "8/19/21 12:02"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]


from celery import shared_task
from celery.utils.log import get_task_logger


logger = get_task_logger(__name__)


def _poll_permits_and_occupancy_docusign(
    envelope_set,
    doc_type,
    instance_doc_field,
    instance_callback=None,
    instance_cert_field=None,
    instance_id=None,
):
    """Poll DocuSign and if we have the document it will add this signed document
    (and optionally the certification document) to the instance by way of a method on the
    instance.

    This will accept an envelope_set list of tuples (envelope_id, <instance>).

    Example:
        class Foo(models.Model):
            signed_document = models.FileField(upload_to=content_name, max_length=512)
            envelope_id = models.CharField(max_length=512)

            def save_docusign_docs(signed_doc, certification_doc):
                self.signed_document=signed_doc

    poll_permits(
        [(Foo.envelope_id, Foo)], instance_doc_field='signed_document',
        instance_callback='save_docusign_docs')

    """

    log = logger
    from ..docusign import BuildingPermit

    latest_result = {
        "status": "error",
        "status_message": "Unknown",
        "signed": "Unknown",
        "waiting_on": "Unknown",
        "remaining_signers": ["Unknown"],
    }

    if not envelope_set:
        latest_result["status_message"] = "No envelope id found"
        return latest_result
    envelopes = dict(envelope_set)

    docusign = BuildingPermit()
    results = docusign.get_envelope_statuses(list(envelopes.keys()))
    for result in results.get("envelopes", []):
        instance_obj = envelopes[result["envelopeId"]]
        latest_result = docusign.get_envelope_signing_status(result["envelopeId"])
        instance_obj.data[doc_type].update({"latest_result": latest_result})
        update_fields = ["data"]
        if result["status"] == "completed":
            log.debug("Gathering docs for %(envelope_id)s", {"envelope_id": result["envelopeId"]})
            docs = docusign.get_completed_documents(result["envelopeId"])
            sign_doc = next((_x["document"] for _x in docs if _x["type"] == "content"), None)
            sign_url = next((_x["uri"] for _x in docs if _x["type"] == "content"), None)
            instance_obj.data[doc_type].update({"signed_upload_result": sign_url})
            if sign_doc:
                update_fields.append(instance_doc_field)

            cert_doc = next((_x["document"] for _x in docs if _x["type"] == "summary"), None)
            if cert_doc and instance_cert_field:
                update_fields.append(instance_cert_field)

            callback = getattr(instance_obj, instance_callback)
            callback(sign_doc, cert_doc)

        instance_obj.save(update_fields=update_fields)
    docusign.session.close()

    if len(results.get("envelopes", [])) != len(envelopes.keys()):
        have = [x["envelopeId"] for x in results.get("envelopes")]
        _missing = list(set(have) - set(envelopes.keys()))
        missing = {envelopes[env].id: env for env in _missing}
        if missing:
            msg = "Unable to find a response for envelopes: %r (agreement_id: envelop)r"
            log.warning(msg, missing)

    return latest_result if instance_id else results


@shared_task
def poll_building_permits_docusign(instance_id=None):
    """Identify completed documents on the DocuSign backend."""

    from ..models import PermitAndOccupancySettings

    queryset = PermitAndOccupancySettings.objects.filter(
        home__isnull=False, signed_building_permit__isnull=True
    )

    envelope_set = []
    for item in queryset:
        # We back this off according to a schedule
        if item.should_get_latest_docusign_status("building_permit"):
            try:
                envelope_set.append((item.data["building_permit"]["envelope_id"], item))
            except KeyError:
                pass

    return _poll_permits_and_occupancy_docusign(
        envelope_set=envelope_set,
        doc_type="building_permit",
        instance_doc_field="signed_building_permit",
        instance_callback="sign_building_permit",
        instance_id=instance_id,
    )


@shared_task
def poll_certificates_of_occupancy_docusign(instance_id=None):
    """Identify completed documents on the DocuSign backend."""

    from ..models import PermitAndOccupancySettings

    queryset = PermitAndOccupancySettings.objects.filter(
        home_id__isnull=False,
        signed_building_permit__isnull=False,
        signed_certificate_of_occupancy__isnull=True,
    )

    envelope_set = []
    for item in queryset:
        # We back this off according to a schedule
        if item.should_get_latest_docusign_status("certificate_of_occupancy"):
            try:
                envelope_set.append((item.data["certificate_of_occupancy"]["envelope_id"], item))
            except KeyError:
                pass

    return _poll_permits_and_occupancy_docusign(
        envelope_set=envelope_set,
        doc_type="certificate_of_occupancy",
        instance_doc_field="signed_certificate_of_occupancy",
        instance_callback="sign_certificate_of_occupancy",
        instance_id=instance_id,
    )
