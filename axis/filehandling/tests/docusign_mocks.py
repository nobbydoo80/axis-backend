"""docusign_mocks.py: Django """


import io
import json
import logging
import os
from urllib.parse import urlparse

from requests import Response

from axis.filehandling.docusign import DocuSignObject

__author__ = "Steven Klass"
__date__ = "06/17/2019 14:44"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

from axis.filehandling.docusign.backend import BaseDocuSignObject

log = logging.getLogger(__name__)


class DocusignMock:
    oath_token_response = {
        "access_token": "SOMEBIGTHING",
        "token_type": "Bearer",
        "expires_in": 3600,
    }

    oath_invalid_grant = {"error": "invalid_grant", "error_description": "issuer_not_found"}
    oath_consent_required = {"error": "consent_required", "error_description": "issuer_not_found"}
    oath_failure = {"error": "No IDEA", "error_description": "something"}

    account_info = {
        "sub": "35ba1bab-9820-4674-bbb9-918a20237d2f",
        "name": "Steven Klass",
        "given_name": "Steven",
        "family_name": "Klass",
        "created": "2019-05-12T04:31:06.093",
        "email": "steven@pivotal.energy",
        "accounts": [
            {
                "account_id": "8119ce76-e875-42eb-af24-b358bcb955f1",
                "is_default": False,
                "account_name": "Home Innovations",
                "base_uri": "https://na3.docusign.net",
                "organization": {
                    "organization_id": "26912d5c-0103-4c3e-a105-f2c0400e647f",
                    "links": [
                        {
                            "rel": "self",
                            "href": "https://account.docusign.com/organizations/26912d5c-0103-4c3e-a105-f2c0400e647f",
                        }
                    ],
                },
            },
            {
                "account_id": "283e03ce-4b46-4a91-8a32-fcb84915b58f",
                "is_default": True,
                "account_name": "Pivotal Energy Solutions",
                "base_uri": "https://na3.docusign.net",
                "organization": {
                    "organization_id": "26912d5c-0103-4c3e-a105-f2c0400e647f",
                    "links": [
                        {
                            "rel": "self",
                            "href": "https://account.docusign.com/organizations/26912d5c-0103-4c3e-a105-f2c0400e647f",
                        }
                    ],
                },
            },
            {
                "account_id": "6203629b-387c-46d2-8556-bd44c38dba0f",
                "is_default": False,
                "account_name": "Energy Trust of Oregon",
                "base_uri": "https://na3.docusign.net",
                "organization": {
                    "organization_id": "26912d5c-0103-4c3e-a105-f2c0400e647f",
                    "links": [
                        {
                            "rel": "self",
                            "href": "https://account.docusign.com/organizations/26912d5c-0103-4c3e-a105-f2c0400e647f",
                        }
                    ],
                },
            },
        ],
    }

    create_envelope = {
        "envelopeId": "44040055-4fa6-4aed-a1a4-9ed69fab8cc3",
        "uri": "/envelopes/44040055-4fa6-4aed-a1a4-9ed69fab8cc3",
        "statusDateTime": "2019-06-17T23:57:06.1030000Z",
        "status": "sent",
    }
    _envelope_statuses = {
        "resultSetSize": "1",
        "totalSetSize": "1",
        "startPosition": "0",
        "endPosition": "0",
        "nextUri": "",
        "previousUri": "",
        "envelopes": [
            {
                "status": "sent",
                "documentsUri": "/envelopes/44040055-4fa6-4aed-a1a4-9ed69fab8cc3/documents",
                "recipientsUri": "/envelopes/44040055-4fa6-4aed-a1a4-9ed69fab8cc3/recipients",
                "attachmentsUri": "/envelopes/44040055-4fa6-4aed-a1a4-9ed69fab8cc3/attachments",
                "envelopeUri": "/envelopes/44040055-4fa6-4aed-a1a4-9ed69fab8cc3",
                "envelopeId": "44040055-4fa6-4aed-a1a4-9ed69fab8cc3",
                "customFieldsUri": "/envelopes/44040055-4fa6-4aed-a1a4-9ed69fab8cc3/custom_fields",
                "notificationUri": "/envelopes/44040055-4fa6-4aed-a1a4-9ed69fab8cc3/notification",
                "statusChangedDateTime": "2019-06-17T23:57:06.1030000Z",
                "documentsCombinedUri": "/envelopes/44040055-49fab8cc3/documents/combined",
                "certificateUri": "/envelopes/44040055-4fa6-d69fab8cc3/documents/certificate",
                "templatesUri": "/envelopes/44040055-4fa6-4aed-a1a4-9ed69fab8cc3/templates",
            }
        ],
    }
    envelope_statuses = _envelope_statuses.copy()

    envelope_form_data = {
        "formData": [],
        "envelopeId": "44040055-4fa6-4aed-a1a4-9ed69fab8cc3",
        "status": "sent",
        "sentDateTime": "2019-06-18T06:57:06.0000000Z",
        "recipientFormData": [
            {
                "name": "Mike Mansfield",
                "formData": [],
                "recipientId": "4e89d4e1-bd15-498d-9438-69f59afc0101",
                "signedTime": "2019-06-18T08:29:21.6800000Z",
                "deliveredTime": "2019-06-18T08:29:07.4470000Z",
                "email": "steven.klass@pointcircle.com",
            },
            {
                "formData": [],
                "recipientId": "a849f329-d2a2-428f-a3d0-f8a3a41bdfb3",
                "name": "NGBS Admin",
                "email": "steven@pointcircle.com",
            },
        ],
    }

    envelope_documents = {
        "envelopeId": "44040055-4fa6-4aed-a1a4-9ed69fab8cc3",
        "envelopeDocuments": [
            {
                "documentId": "55588",
                "name": "NGBS Builder Agreement",
                "type": "content",
                "uri": "/envelopes/44040055-4fa6-4aed-a1a4-9ed69fab8cc3/documents/55588",
                "order": "1",
                "pages": "5",
                "availableDocumentTypes": [{"type": "electronic", "isDefault": "true"}],
                "display": "inline",
                "includeInDownload": "true",
                "signerMustAcknowledge": "no_interaction",
                "authoritativeCopy": "false",
            },
            {
                "documentId": "certificate",
                "name": "Summary",
                "type": "summary",
                "uri": "/envelopes/44040055-4fa6-4aed-a1a4-9ed69fab8cc3/documents/certificate",
                "order": "999",
                "pages": "5",
                "availableDocumentTypes": [{"type": "electronic", "isDefault": "true"}],
                "display": "inline",
                "includeInDownload": "true",
                "signerMustAcknowledge": "no_interaction",
                "authoritativeCopy": "false",
            },
        ],
    }

    build_response = BaseDocuSignObject().build_response

    @property
    def envelope_statuses_complete(self):
        data = self.envelope_statuses.copy()
        for item in data["envelopes"]:
            item["status"] = "completed"
        return data

    @property
    def envelope_form_data_complete(self):
        data = self.envelope_form_data.copy()
        data["status"] = "completed"
        data["recipientFormData"] = [
            {
                "name": "Mike Mansfield",
                "formData": [],
                "recipientId": "4e89d4e1-bd15-498d-9438-69f59afc0101",
                "signedTime": "2019-06-18T08:29:21.6800000Z",
                "deliveredTime": "2019-06-18T08:29:07.4470000Z",
                "email": "steven.klass@pointcircle.com",
            },
            {
                "name": "NGBS Admin",
                "formData": [],
                "recipientId": "a849f329-d2a2-428f-a3d0-f8a3a41bdfb3",
                "signedTime": "2019-06-18T08:30:30.5070000Z",
                "deliveredTime": "2019-06-18T08:29:41.6170000Z",
                "email": "steven@pointcircle.com",
            },
        ]
        return data

    def get_account_info(self, netloc):
        data = self.account_info.copy()
        data["accounts"] = []
        for item in self.account_info["accounts"]:
            # Make sure that we pull the right dev stuff out.
            if "account-d" in netloc:
                item["base_uri"] = f"https://{netloc}"
            data["accounts"].append(item)
        return data

    @classmethod
    def get_document_object(cls, url):
        filename = "/docusign_test.pdf"
        if url.endswith("certificate"):
            filename = "/docusign_test_certificate.pdf"
        with io.open(os.path.abspath(os.path.dirname(__file__) + filename), encoding="latin1") as f:
            data = f.read()
        output_stream = io.BytesIO(data.encode())
        output_stream.seek(0)
        return output_stream.read()

    def get_completed_documents(self):
        """FAKE DATA"""
        documents = []
        for item in self.envelope_documents["envelopeDocuments"]:
            item["document"] = self.get_document_object(item["uri"])
            documents.append(item)
        return documents

    @classmethod
    def post(cls, url, **kwargs):
        parsed_url = urlparse(url)

        match parsed_url.path.split("/")[-1]:
            case "token":
                return cls.build_response(200, content=cls.oath_token_response)
            case "envelopes":
                return cls.build_response(200, content=cls.create_envelope)
            case _:
                return cls.build_response(400, content={"error": "Not Found"})

    @classmethod
    def post_fail_auth_token(cls, url, **kwargs):
        parsed_url = urlparse(url)
        match parsed_url.path:
            case "/oauth/token":
                return cls.build_response(400, content=cls.oath_invalid_grant)
        return cls.post(url, **kwargs)

    @classmethod
    def post_fail_auth_consent(cls, url, **kwargs):
        parsed_url = urlparse(url)
        match parsed_url.path:
            case "/oauth/token":
                return cls.build_response(400, content=cls.oath_consent_required)
        return cls.post(url, **kwargs)

    @classmethod
    def post_fail_auth(cls, url, **kwargs):
        parsed_url = urlparse(url)
        match parsed_url.path:
            case "/oauth/token":
                return cls.build_response(400, content=cls.oath_consent_required)
        return cls.post(url, **kwargs)

    @classmethod
    def post_fail_token(cls, url, **kwargs):
        parsed_url = urlparse(url)
        match parsed_url.path:
            case "/oauth/token":
                return cls.build_response(400, content=cls.oath_invalid_grant)
        return cls.post(url, **kwargs)

    @classmethod
    def get(cls, url, **kwargs):
        parsed_url = urlparse(url)
        match parsed_url.path.split("/")[-1]:
            case "userinfo":
                return cls.build_response(200, content=cls.get_account_info(cls, parsed_url.netloc))
            case "form_data":
                return cls.build_response(200, content=cls.envelope_form_data)
            case "documents":
                return cls.build_response(200, content=cls.envelope_documents)
            case "certificate":
                return cls.build_response(200, content=cls.get_document_object(url))
            case "55588":
                return cls.build_response(200, content=cls.get_document_object(url))
            case _:
                return cls.build_response(400, content={"error": "Not Found"})

    @classmethod
    def put(cls, url, **kwargs):
        parsed_url = urlparse(url)
        match parsed_url.path.split("/")[-2]:
            case "path":
                return cls.build_response(200, {"put": True})
            case "envelopes":
                return cls.build_response(200, content=cls.envelope_statuses)
            case _:
                return cls.build_response(400, content={"error": f"Not Found!"})

    @classmethod
    def delete(cls, url, **kwargs):
        """Note this is here but we really don't use this"""
        parsed_url = urlparse(url)
        match parsed_url.path.split("/")[-2]:
            case "path":
                return cls.build_response(200, content={"delete": True})
            case _:
                return cls.build_response(400, content={"error": "Not Found"})
