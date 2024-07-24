"""backend.py: Django """


from operator import attrgetter
import logging

__author__ = "Steven Klass"
__date__ = "06/14/2019 07:51"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


def poll_docusign(
    docusign_wrapper,
    envelopes,  # dict of {e_id: signable_model_instance}
    instance_data_getter=attrgetter("data"),
    instance_callback_getter=attrgetter("receive_signed_document"),
):
    """Poll DocuSign backend for the `envelopes` keys as ids, and update each mapped instance."""

    results = docusign_wrapper.get_envelope_statuses(envelopes.keys())

    for result in results.get("envelopes", []):
        instance = envelopes[result["envelopeId"]]
        data = instance_data_getter(instance)
        callback = instance_callback_getter(instance)

        latest_result = docusign_wrapper.get_envelope_signing_status(result["envelopeId"])
        data.update(latest_result=latest_result)

        if result["status"] == "completed":
            docs = docusign_wrapper.get_completed_documents(result["envelopeId"])

            certificate = next((_x["document"] for _x in docs if _x["type"] == "summary"), None)
            signed_doc = next((_x["document"] for _x in docs if _x["type"] == "content"), None)
            signed_url = next((_x["uri"] for _x in docs if _x["type"] == "content"), None)

            data.update(signed_upload_result=signed_url)

            callback(signed_doc, certificate)

        instance.save()

    return results
