"""tests_docusign.py: Django """


import logging
import time
from unittest.mock import patch

from axis.core.tests.testcases import AxisTestCase
from .docusign_mocks import DocusignMock
from ..docusign import DocuSignObject
from ..docusign.backend import (
    DocusignTokenException,
    DocusignException,
    TOKEN_REPLACEMENT_SECONDS,
)
from ...core.tests.test_views import DevNull

__author__ = "Steven Klass"
__date__ = "06/17/2019 15:07"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

from ...gbr.tests.mocked_responses import gbr_mocked_response

log = logging.getLogger(__name__)


class DocuSignBackendTestCases(AxisTestCase):
    """Test out the DocuSign stuff"""

    base_session = "axis.filehandling.docusign.backend.BaseDocuSignObject.session"

    def test_get_authorization_url(self):
        """Check to make sure we can generate a auth url for consent"""
        url = DocuSignObject().get_authorization_url
        self.assertIn("signature", url)

    @patch("requests.Session.post", side_effect=DocusignMock().post)
    @patch("requests.Session.get", side_effect=DocusignMock().get)
    def test_check_token(self, _get, _post):
        """Verify check token"""
        token_replacement = int(round(time.time())) + TOKEN_REPLACEMENT_SECONDS + 2
        account_info = DocusignMock().account_info

        with self.subTest("Valid Token"):
            doc = DocuSignObject()

            doc.expiration_timestamp = token_replacement
            doc.account_info = account_info

            result = doc.check_token()
            self.assertEqual(result, account_info)
            self.assertEqual(doc.expiration_timestamp, token_replacement)
            _post.assert_not_called()
            _get.assert_not_called()

        with self.subTest("Invalid Token"):
            doc = DocuSignObject()
            result = doc.check_token()
            self.assertEqual(result, account_info)
            self.assertNotEqual(doc.expiration_timestamp, token_replacement)
            _post.assert_called_once()
            _get.assert_called_once()

    @patch("requests.Session.post", side_effect=DocusignMock().post)
    @patch("requests.Session.get", side_effect=DocusignMock().get)
    def test_update_token(self, _get, _post):
        account_info = DocusignMock().account_info

        with self.subTest("Valid Token Response with account info"):
            account_info["family_name"] = "FRODO"
            doc = DocuSignObject()
            doc.account_info = account_info
            doc.update_token()
            _post.assert_called_once()
            _get.assert_not_called()
            self.assertEqual(doc.account_info, account_info)

        with self.subTest("Valid Token Response no account info"):
            doc = DocuSignObject()
            doc.update_token()
            _get.assert_called_once()
            # Post now called twice
            self.assertEqual(doc.account_info, account_info)

    @patch("requests.Session.post", side_effect=DocusignMock().post_fail_auth_token)
    @patch("requests.Session.get", side_effect=DocusignMock().get)
    def test_update_with_token_failure(self, _get, _post):
        doc = DocuSignObject()
        self.assertRaises(DocusignTokenException, doc.update_token)
        _post.assert_called_once()
        _get.assert_not_called()

    @patch("requests.Session.post", side_effect=DocusignMock().post_fail_auth_consent)
    @patch("requests.Session.get", side_effect=DocusignMock().get)
    def test_update_with_consent_failure(self, _get, _post):
        doc = DocuSignObject()
        self.assertRaises(DocusignException, doc.update_token)
        _post.assert_called_once()
        _get.assert_not_called()

    @patch("requests.Session.post", side_effect=DocusignMock().post_fail_auth)
    @patch("requests.Session.get", side_effect=DocusignMock().get)
    def test_update_general_failure(self, _get, _post):
        doc = DocuSignObject()
        self.assertRaises(DocusignException, doc.update_token)
        _post.assert_called_once()
        _get.assert_not_called()

    @patch("requests.Session.post", side_effect=DocusignMock().post)
    @patch("requests.Session.get", side_effect=DocusignMock().get)
    def test_get_account_info(self, _get, _post):
        with self.subTest("Default Account"):
            doc = DocuSignObject()
            doc.update_token()
            _post.assert_called_once()
            _get.assert_called_once()
            self.assertEqual(doc.account_id, "283e03ce-4b46-4a91-8a32-fcb84915b58f")
            self.assertEqual(doc._account_id, doc.account_id)
        with self.subTest("Hirl Account"):
            doc = DocuSignObject(account_id="6203629b-387c-46d2-8556-bd44c38dba0f")
            doc.update_token()
            self.assertEqual(doc.account_id, "6203629b-387c-46d2-8556-bd44c38dba0f")
            self.assertEqual(doc._account_id, doc.account_id)
        with self.subTest("BOGUS Account"):
            doc = DocuSignObject(account_id="XXX")
            self.assertRaises(DocusignException, doc.update_token)

    @patch("requests.Session.post", side_effect=DocusignMock().post)
    @patch("requests.Session.get", side_effect=DocusignMock().get)
    def test_base_rest_url(self, _get, _post):
        with self.subTest("Default Account"):
            doc = DocuSignObject(sandbox_mode=False)
            self.assertEqual(
                doc.base_rest_url,
                "https://na3.docusign.net/restapi/v2/accounts/283e03ce-4b46-4a91-8a32-fcb84915b58f",
            )
            _post.assert_called_once()
            _get.assert_called_once()

        with self.subTest("Hirl Account"):
            doc = DocuSignObject(
                sandbox_mode=False, account_id="6203629b-387c-46d2-8556-bd44c38dba0f"
            )
            self.assertEqual(
                doc.base_rest_url,
                "https://na3.docusign.net/restapi/v2/accounts/6203629b-387c-46d2-8556-bd44c38dba0f",
            )
        with self.subTest("Sandbox Account"):
            doc = DocuSignObject(sandbox_mode=True)
            self.assertEqual(
                doc.base_rest_url,
                "https://account-d.docusign.com/restapi/v2/accounts/283e03ce-4b46-4a91-8a32-fcb84915b58f",
            )

    @patch("requests.Session.post", side_effect=DocusignMock().post_fail_auth_token)
    @patch("requests.Session.get", side_effect=DocusignMock().get)
    def test_session_rest_get_auth_failure(self, _get, _post):
        with self.subTest("Raise JWT Token Exception"):
            doc = DocuSignObject(sandbox_mode=False)
            self.assertTrue(doc.should_raise_token_exception())
            self.assertRaises(DocusignTokenException, doc.session_rest_get, "/userinfo")

        with self.subTest("Do NOT raise JWT Token Exception"):
            doc = DocuSignObject(sandbox_mode=True)
            self.assertFalse(doc.should_raise_token_exception())
            response = doc.session_rest_get("/userinfo")
            self.assertEqual(response.status_code, 401)

    @patch("requests.Session.post", side_effect=DocusignMock().post)
    @patch("requests.Session.get", side_effect=DocusignMock().get)
    def test_session_rest_get(self, _get, _post):
        with self.subTest("Fake Path"):
            doc = DocuSignObject(sandbox_mode=False)
            response = doc.session_rest_get("/fake")
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), {"error": "Not Found"})

        with self.subTest("Valid Path"):
            doc = DocuSignObject(sandbox_mode=False)
            response = doc.session_rest_get("/userinfo")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), DocusignMock.account_info)

    @patch("requests.Session.post", side_effect=DocusignMock().post_fail_auth_token)
    @patch("requests.Session.get", side_effect=DocusignMock().get)
    def test_session_rest_post_auth_failure(self, _get, _post):
        with self.subTest("Raise JWT Token Exception"):
            doc = DocuSignObject(sandbox_mode=False)
            self.assertTrue(doc.should_raise_token_exception())
            self.assertRaises(DocusignTokenException, doc.session_rest_post, "/token")

        with self.subTest("Do NOT raise JWT Token Exception"):
            doc = DocuSignObject(sandbox_mode=True)
            self.assertFalse(doc.should_raise_token_exception())
            response = doc.session_rest_post("/token")
            self.assertEqual(response.status_code, 401)

    @patch("requests.Session.post", side_effect=DocusignMock().post)
    @patch("requests.Session.get", side_effect=DocusignMock().get)
    def test_session_rest_post(self, _get, _post):
        with self.subTest("Fake Path"):
            doc = DocuSignObject(sandbox_mode=False)
            response = doc.session_rest_post("/fake")
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), {"error": "Not Found"})

        with self.subTest("Valid Path"):
            doc = DocuSignObject(sandbox_mode=False)
            response = doc.session_rest_post("/token")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), DocusignMock.oath_token_response)

    @patch("requests.Session.post", side_effect=DocusignMock().post_fail_auth_token)
    @patch("requests.Session.get", side_effect=DocusignMock().get)
    @patch("requests.Session.put", side_effect=DocusignMock().put)
    def test_session_rest_put_auth_failure(self, _put, _get, _post):
        with self.subTest("Raise JWT Token Exception"):
            doc = DocuSignObject(sandbox_mode=False)
            self.assertTrue(doc.should_raise_token_exception())
            self.assertRaises(DocusignTokenException, doc.session_rest_put, "/path/222e6840-22xx")

        with self.subTest("Do NOT raise JWT Token Exception"):
            doc = DocuSignObject(sandbox_mode=True)
            self.assertFalse(doc.should_raise_token_exception())
            response = doc.session_rest_put("/path/222e6840-22xx")
            self.assertEqual(response.status_code, 401)

    @patch("requests.Session.post", side_effect=DocusignMock().post)
    @patch("requests.Session.get", side_effect=DocusignMock().get)
    @patch("requests.Session.put", side_effect=DocusignMock().put)
    def test_session_rest_put(self, _put, _get, _post):
        with self.subTest("Fake Path"):
            doc = DocuSignObject(sandbox_mode=False)
            response = doc.session_rest_put("/fake/222e6840-22xx")
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), {"error": "Not Found!"})

        with self.subTest("Valid Path"):
            doc = DocuSignObject(sandbox_mode=False)
            response = doc.session_rest_put("/path/222e6840-22xx")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {"put": True})

    @patch("requests.Session.post", side_effect=DocusignMock().post_fail_auth_token)
    @patch("requests.Session.get", side_effect=DocusignMock().get)
    @patch("requests.Session.delete", side_effect=DocusignMock().delete)
    def test_session_rest_delete_auth_failure(self, _delete, _get, _post):
        with self.subTest("Raise JWT Token Exception"):
            doc = DocuSignObject(sandbox_mode=False)
            self.assertTrue(doc.should_raise_token_exception())
            self.assertRaises(
                DocusignTokenException, doc.session_rest_delete, "/path/222e6840-22xx"
            )

        with self.subTest("Do NOT raise JWT Token Exception"):
            doc = DocuSignObject(sandbox_mode=True)
            self.assertFalse(doc.should_raise_token_exception())
            response = doc.session_rest_delete("/path/222e6840-22xx")
            self.assertEqual(response.status_code, 401)

    @patch("requests.Session.post", side_effect=DocusignMock().post)
    @patch("requests.Session.get", side_effect=DocusignMock().get)
    @patch("requests.Session.delete", side_effect=DocusignMock().delete)
    def test_session_rest_delete(self, _delete, _get, _post):
        with self.subTest("Fake Path"):
            doc = DocuSignObject(sandbox_mode=False)
            response = doc.session_rest_delete("/fake/222e6840-22xx")
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), {"error": "Not Found"})

        with self.subTest("Valid Path"):
            doc = DocuSignObject(sandbox_mode=False)
            response = doc.session_rest_delete("/path/222e6840-22xx")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {"delete": True})

    def test_get_envelope_definition(self):
        doc = DocuSignObject()
        self.assertRaises(NotImplementedError, doc.get_clean_envelope_definition)

    def test_get_clean_envelope_definition(self):
        """Check for ability to clean a document definition"""

        class MyDocuSign(DocuSignObject):
            """Fake Stuff"""

            def get_envelope_definition(self, *args, **kwargs):
                """Fake Data"""

                class Something(object):
                    """Fake Data"""

                    def to_dict(self):
                        """Fake Data"""
                        return {
                            "my_stuff": True,
                            "your_stuff": {
                                "something_a": 1,
                                "something_b": [{"class_a": 1}],
                            },
                            "documents": [{"documentBase64": "Something.."}],
                        }

                return Something()

        doc = MyDocuSign()
        value = doc.get_clean_envelope_definition()
        self.assertEqual(set(value.keys()), {"yourStuff", "myStuff", "documents"})
        self.assertEqual(set(value["yourStuff"].keys()), {"somethingA", "somethingB"})
        doc.dump_envelope(value, stdout=DevNull())

    @patch("requests.Session.post", side_effect=DocusignMock().post)
    @patch("requests.Session.get", side_effect=DocusignMock().get)
    def test_create_envelope(self, _get, _post):
        """Check for ability to create an envelope"""
        doc = DocuSignObject()
        data = doc.create_envelope(envelope_definition=True)
        self.assertEqual(set(data.keys()), {"status", "envelopeId", "statusDateTime", "uri"})

    @patch("requests.Session.post", side_effect=DocusignMock().post_fail_auth_token)
    @patch("requests.Session.get", side_effect=DocusignMock().get)
    def test_create_envelope_auth(self, _get, _post):
        """Check for ability to create an envelope"""
        doc = DocuSignObject()
        data = doc.create_envelope(envelope_definition=True)
        self.assertEqual(len(data.keys()), 1)
        self.assertEqual(data["envelopeId"], None)

    @patch("requests.Session.post", side_effect=DocusignMock().post)
    @patch("requests.Session.get", side_effect=DocusignMock().get)
    @patch("requests.Session.put", side_effect=DocusignMock().put)
    def test_get_envelope_statuses(self, _put, _get, _post):
        """Check for ability to create an envelope"""
        doc = DocuSignObject()
        data = doc.get_envelope_statuses(envelope_ids=["44040055-4fa6-4aed-a1a4-9ed69fab8cc3"])
        self.assertEqual(
            set(data.keys()),
            {
                "previousUri",
                "endPosition",
                "startPosition",
                "resultSetSize",
                "envelopes",
                "nextUri",
                "totalSetSize",
            },
        )

    @patch("requests.Session.post", side_effect=DocusignMock().post_fail_auth_token)
    @patch("requests.Session.get", side_effect=DocusignMock().get)
    @patch("requests.Session.put", side_effect=DocusignMock().put)
    def test_get_envelope_statuses_auth(self, _put, _get, _post):
        """Check for ability to create an envelope"""
        doc = DocuSignObject()
        data = doc.get_envelope_statuses(envelope_ids=["44040055-4fa6-4aed-a1a4-9ed69fab8cc3"])
        self.assertEqual(data.keys(), {"envelopes"})

    @patch("requests.Session.post", side_effect=DocusignMock().post)
    @patch("requests.Session.get", side_effect=DocusignMock().get)
    def test_get_envelope_form_data(self, _get, _post):
        """Check for ability to get an envelope form data - this tells us who needs to sign it"""
        doc = DocuSignObject()
        data = doc.get_envelope_form_data("44040055-4fa6-4aed-a1a4-9ed69fab8cc3")
        self.assertEqual(
            set(data.keys()),
            {"status", "envelopeId", "formData", "sentDateTime", "recipientFormData"},
        )

    @patch("requests.Session.post", side_effect=DocusignMock().post_fail_auth_token)
    @patch("requests.Session.get", side_effect=DocusignMock().get)
    def test_get_envelope_form_data_auth(self, _get, _post):
        """Check for ability to get an envelope form data - this tells us who needs to sign it"""
        doc = DocuSignObject()
        data = doc.get_envelope_form_data("44040055-4fa6-4aed-a1a4-9ed69fab8cc3")
        self.assertEqual(len(data.keys()), 0)

    @patch("requests.Session.post", side_effect=DocusignMock().post)
    @patch("requests.Session.get", side_effect=DocusignMock().get)
    @patch("axis.gbr.gbr.GreenBuildingRegistryAPIConnect.post", side_effect=gbr_mocked_response)
    def test_get_documents_for_envelope(self, _gbr, _get, _post):
        """Gets the documents associated with an envelope"""
        doc = DocuSignObject()
        data = doc.get_documents_for_envelope("44040055-4fa6-4aed-a1a4-9ed69fab8cc3")
        self.assertEqual(set(data.keys()), {"envelopeId", "envelopeDocuments"})

    @patch("requests.Session.post", side_effect=DocusignMock().post_fail_auth_token)
    @patch("requests.Session.get", side_effect=DocusignMock().get)
    def test_get_documents_for_envelope_auth(self, _get, _post):
        """Gets the documents associated with an envelope"""
        doc = DocuSignObject()
        data = doc.get_documents_for_envelope("44040055-4fa6-4aed-a1a4-9ed69fab8cc3")
        self.assertEqual(set(data.keys()), {"envelopeDocuments"})

    @patch("requests.Session.post", side_effect=DocusignMock().post)
    @patch("requests.Session.get", side_effect=DocusignMock().get)
    def test_get_document_object(self, _get, _post):
        """Gets the documents associated with an envelope"""
        doc = DocuSignObject()
        data = doc.get_document_object("/envelopes/44040055-xx/documents/certificate")
        self.assertEqual(type(data), bytes)
        self.assertNotEqual(data, bytes("No data".encode()))

    @patch("requests.Session.post", side_effect=DocusignMock().post_fail_auth_token)
    @patch("requests.Session.get", side_effect=DocusignMock().get)
    def test_get_get_document_object_auth(self, _get, _post):
        """Gets the documents associated with an envelope"""
        doc = DocuSignObject()
        data = doc.get_document_object("/envelopes/44040055-xx/documents/certificate")
        self.assertEqual(data, bytes("No data".encode()))

    @patch("requests.Session.post", side_effect=DocusignMock().post)
    @patch("requests.Session.get", side_effect=DocusignMock().get)
    @patch("axis.gbr.gbr.GreenBuildingRegistryAPIConnect.post", side_effect=gbr_mocked_response)
    def test_get_completed_documents(
        self,
        _gbr,
        _get,
        _post,
    ):
        """Gets the documents associated with an envelope"""
        doc = DocuSignObject()
        data = doc.get_completed_documents("44040055-4fa6-4aed-a1a4-9ed69fab8cc3")
        self.assertEqual(len(data), 2)

    @patch("requests.Session.post", side_effect=DocusignMock().post_fail_auth_token)
    @patch("requests.Session.get", side_effect=DocusignMock().get)
    def test_get_completed_documents_auth(self, _get, _post):
        """Gets the documents associated with an envelope"""
        doc = DocuSignObject()
        data = doc.get_completed_documents("44040055-4fa6-4aed-a1a4-9ed69fab8cc3")
        self.assertEqual(len(data), 0)
