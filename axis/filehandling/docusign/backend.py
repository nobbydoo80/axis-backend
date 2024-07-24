"""backend.py: Django """

__author__ = "Steven Klass"
__date__ = "06/14/2019 07:51"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

import base64
import json
import logging
import pprint
import re
import sys
import time
from collections import defaultdict
from io import BytesIO
from typing import Optional, List

import jwt
import requests
from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from docusign_esign import (
    Document,
    SignHere,
    Signer,
    Tabs,
    EnvelopeDefinition,
    Recipients,
    Text,
    CarbonCopy,
    Notification,
    Reminders,
    Expirations,
)
from requests import Response

User = get_user_model()

log = logging.getLogger(__name__)
app = apps.get_app_config("filehandling")

TOKEN_REPLACEMENT_SECONDS = 60 * 10
TOKEN_EXPIRATION_SECONDS = 60 * 60


class DocusignException(Exception):
    pass


class DocusignTokenException(Exception):
    def __init__(self, message: str, response: dict | None = None, *args, **kwargs):
        self.message = message
        self.response = response

    def __str__(self):
        return f"DocusignTokenException({self.message}, {self.response})"


# pylint disable=too-many-instance-attributes
class BaseDocuSignObject(object):
    """Wrapper for docusign processes.

    Notes:
        - We are using JWT Grant Auth. We are not allowing users to work on behalf of
          themselves we are working system to system

    https://developers.docusign.com/esign-rest-api

    The basic process for this is outlined above but there are some things to keep in
    mind.
    - This code negates the need to use _any_ of the docusign-esign SDK.  You may use it
      if you want to design your envelope definition flow (Documents, SignHere, Signer, etc)
    - This will talk directly to the docusign.com endpoints.  It doesn't do any *magic* stuff
      that seems to happen with the DocuSign SDK, and IMO is completely screwy.  (It's clear it's
      generated SDK output).
    - This process requires the USER ID (This is in admin under users) this is the 'account_id`
      of the user who will be facilitating this work.  I could not ind a way to make the JWT work
      without the use of `sub` field.  This is very contrary to the SDK flow (which also failed)
      Docusign recommends.
    - Getting an JWT does NOT mean you are good to go.  You MUST be able to hit
      `/oauth/userinfo`.  This is where I really stumbled.  You need this as this will update the
      actual host you can make non-auth calls to.  This implies that the auth system they are
      using is decoupled from the API endpoints.  Nice to know.

    Once you are in and can hit things like brands (this is they example the provide) it's
    a good sanity checkpoint to make sure you've gotten past the auth stuff.

    Now you can use the docusign_esign design components (Document, SignHere, Signer, etc) when
    defining envelopes.  I'll convert it to the camelCase for you.  I couldn't figure out where
    in the docusign_esign SDK they do it but it has to happen otherwise it won't work. (TODO)
    Note:  You don't need to use it at all.  Especially for simple docs where you know what you
    doing.  But it's cool to use it.

    Usage:
    - The only thing you need to do is to implement a subclass of DocuSignObject and define your
     `get_envelope_definition` method.  This will tell you who gets it etc.  Once that's done
     it should work through it.

     class DocuSignAgreement(DocuSignObject):

        def get_envelope_definition(*args, **kwargs):

                content_bytes = kwargs.get('document').read()
                base64_file_content = base64.b64encode(content_bytes).decode('ascii')

                document = Document(
                    document_base64=base64_file_content,
                    name='Agreement',
                    file_extension='pdf',
                    document_id=kwargs.get('document').id)

     ...

     docusign = DocuSignAgreement()
     result = docusign.create_envelope(document=document)

    """

    def __init__(
        self,
        integrator_key: str | None = None,
        user_id: str | None = None,
        account_id: str | None = None,
        **kwargs,
    ):
        self.integrator_key = integrator_key or settings.DOCUSIGN_INTEGRATOR_KEY
        self.user_id = user_id or settings.DOCUSIGN_ACCOUNT_ID

        self.sandbox_mode = kwargs.get("sandbox_mode", settings.DOCUSIGN_SANDBOX_MODE)

        self.base_url = "https://account.docusign.com"
        self.rsa_key = app.DOCUSIGN_SECURE_KEY
        if self.sandbox_mode:
            self.base_url = "https://account-d.docusign.com"
            self.rsa_key = app.DOCUSIGN_SANDBOX_KEY
            log.debug("Using Sandbox Mode - Base URL: %s", self.base_url)

        self.docusign_api_version = "v2"

        self.token = None
        self.auth_header = {}
        self.expiration_timestamp = 0

        self.account_info = None
        self._account_id = account_id
        self.account_id = None

        self.session = requests.session()

        self.session.headers.update(
            {
                "X-DocuSign-SDK": "Python - AXIS DocuSign API",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )

    @classmethod
    def build_response(
        cls,
        status_code: int,
        content: dict | bytes | None = None,
        code: str | None = None,
        error_type: str | None = None,
    ) -> Response:
        """Allows for a generic response - Primarily used in testing or when we get an error we want to handle"""
        response = Response()
        response.code = code or content
        response.error_type = error_type or content
        response.status_code = status_code
        if isinstance(content, dict):
            # This try / except is here because in testing we simply append the byte data of
            # the document we shouldn't normally hit this; that's why it's bound to envelopeDocuments
            try:
                content = json.dumps(content).encode("utf-8")
            except TypeError:
                if "envelopeDocuments" not in content:
                    raise
                [x.pop("document") for x in content["envelopeDocuments"]]
                content = json.dumps(content).encode("utf-8")

        if not isinstance(content, bytes):
            content = str(content).encode("utf-8")
        response._content = content
        return response

    def should_raise_token_exception(self) -> bool:
        """Determine whether or raise DocusignTokenException.  Used on non-production"""
        return False if self.sandbox_mode else True

    @property
    def get_authorization_url(self) -> str:
        """Provide the URL to present which will enable the app to sign and
        impersonate on behalf of the user.  This should only be needed once.
        """
        url = self.base_url + "/oauth/auth"
        params = {
            "response_type": "code",
            "scope": "signature impersonation",
            "client_id": self.integrator_key,
            "redirect_uri": "https://axis.pivotalenergy.net",
        }
        return requests.Request("GET", url, params=params).prepare().url

    def check_token(self) -> dict:
        """Verifies our token is not expired"""
        current_time = int(round(time.time()))
        token_replacement = current_time + TOKEN_REPLACEMENT_SECONDS
        if token_replacement > self.expiration_timestamp:
            self.update_token()
        return self.account_info

    def update_token(self) -> dict:
        """Gets a new OAUTH user token"""
        now = int(round(time.time()))
        expires = now + TOKEN_EXPIRATION_SECONDS

        claim = {
            "iss": self.integrator_key,
            "aud": re.sub(r"https://", "", self.base_url),
            "iat": now,
            "exp": expires,
            "sub": self.user_id,
            "scope": "signature impersonation",
        }

        token = jwt.encode(payload=claim, key=self.rsa_key, algorithm="RS256")

        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = self.session.post(
            self.base_url + "/oauth/token",
            headers=headers,
            params={
                "assertion": token,
                "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            },
        )
        if response.status_code != 200:
            self.session.close()
            if response.status_code == 400 and "invalid_grant" in str(response.json()):
                raise DocusignTokenException(
                    message=f"Unable to get JWT Token - using claim {claim!r}",
                    response=response.json(),
                )
            if "consent_required" in response.content.decode():
                # If you run into this log into docusign under the account
                # Then paste in this url - you consent to using our app.
                raise DocusignException("Consent required - Hit up %s" % self.get_authorization_url)
            raise DocusignException("Unable to get JWT Token - using claim %r" % claim)
        self.token = response.json().get("access_token")
        self.expiration_timestamp = expires
        self.auth_header = {"Authorization": "Bearer %s" % self.token}
        log.debug("Auth token has been granted %s...", self.token[:32])
        if self.account_info is None:
            return self.get_account_info()
        return self.account_info

    def get_account_info(self) -> dict:
        """Gathers the account info"""
        if self.token is None:
            self.update_token()

        if self.account_info:
            return self.account_info

        response = self.session.get(self.base_url + "/oauth/userinfo", headers=self.auth_header)

        self.account_info = response.json()

        account_name = ""
        if self._account_id is None:
            # Use the default one.
            _account = next((x for x in self.account_info["accounts"] if x["is_default"]))
            self.account_id = _account["account_id"]
            self._account_id = _account["account_id"]
            account_name = _account["account_name"]
            self.base_url = _account["base_uri"]
        else:
            for _account in self.account_info["accounts"]:
                if _account["account_id"] == self._account_id:
                    self.account_id = _account["account_id"]
                    account_name = _account["account_name"]
                    self.base_url = _account["base_uri"]
                    break
        if self._account_id and not self.account_id:
            raise DocusignException(f"Unable to find provided account id {self._account_id}")
        log.debug("Account info for %s (%s) has been updated", account_name, self.account_id)
        return self.account_info

    @property
    def base_rest_url(self) -> str:
        """Returns the nice base rest url"""

        if self.account_id is None:
            self.get_account_info()

        url = self.base_url + "/restapi/" + self.docusign_api_version
        url += "/accounts/" + "%s" % self.account_id
        return url

    def session_rest_get(
        self,
        rest_url: str,
        headers: dict | None = None,
        params: dict | None = None,
        stream: bool = False,
    ) -> Response:
        """A wrapper around session get calls to parse for errors"""

        params = params if params else {}

        try:
            url = self.base_rest_url + rest_url
        except DocusignTokenException as err:
            if self.should_raise_token_exception():
                raise
            return self.build_response(401, content=err.response, code="Invalid JWT for GET")

        headers = headers if headers else {}
        headers.update(self.auth_header)

        response = self.session.get(url, headers=headers, params=params, stream=stream)

        if response.status_code != 200:
            log.error(
                f"{response.status_code} Unable to GET rest url {rest_url} - "
                f"{response.url} - {response.content}"
            )
        return response

    def session_rest_put(
        self,
        rest_url: str,
        headers: dict | None = None,
        params: dict | None = None,
        data: dict | None = None,
    ) -> Response:
        """A wrapper around session get calls to parse for errors"""

        params = params if params else {}

        try:
            url = self.base_rest_url + rest_url
        except DocusignTokenException as err:
            if self.should_raise_token_exception():
                raise
            return self.build_response(401, content=err.response, code="Invalid JWT for PUT")

        headers = headers if headers else {}
        headers.update(self.auth_header)

        response = self.session.put(url, headers=headers, params=params, json=data)

        if response.status_code != 200:
            log.error(
                f"{response.status_code} Unable to PUT rest url {rest_url} - "
                f"{response.url} - {response.content}"
            )
        return response

    def session_rest_post(
        self,
        rest_url: str,
        headers: dict | None = None,
        params: dict | None = None,
        data: dict | None = None,
    ) -> Response:
        """A wrapper around session post calls to parse for errors"""

        params = params if params else {}

        try:
            url = self.base_rest_url + rest_url
        except DocusignTokenException as err:
            if self.should_raise_token_exception():
                raise
            return self.build_response(401, content=err.response, code="Invalid JWT for POST")

        headers = headers if headers else {}
        headers.update(self.auth_header)

        response = self.session.post(url, headers=headers, params=params, json=data)

        if response.status_code != 201:
            log.error(
                f"{response.status_code} Unable to POST rest url {rest_url} - "
                f"{response.url} - {response.content} {str(data)[:128]}..."
            )
        return response

    def session_rest_delete(
        self,
        rest_url: str,
        headers: dict | None = None,
        params: dict | None = None,
        data: dict | None = None,
    ) -> Response:
        """A wrapper around session delete calls to parse for errors"""

        params = params if params else {}

        try:
            url = self.base_rest_url + rest_url
        except DocusignTokenException as err:
            if self.should_raise_token_exception():
                raise
            return self.build_response(401, content=err.response, code="Invalid JWT for DELETE")

        headers = headers if headers else {}
        headers.update(self.auth_header)

        response = self.session.delete(url, headers=headers, params=params, json=data)

        if response.status_code != 200:
            log.error(
                {
                    f"{response.status_code} Unable to DELETE rest url {rest_url} - "
                    f"{response.url} - {response.content} {data}"
                },
            )
        return response

    def get_envelope_definition(self, *args, **kwargs):
        """Defines the Full definition for and Envelope"""
        raise NotImplementedError("You must define this")

    def dump_envelope(self, envelope_definition: dict, stdout=None) -> None:
        """Dumps the envelope definition"""
        definition = {}

        for k, v in envelope_definition.items():
            definition[k] = v

        for doc in definition.get("documents", []):
            doc["documentBase64"] = doc["documentBase64"][:15] + "..."
        import pprint

        stdout = sys.stdout if stdout is None else stdout
        stdout.write(pprint.pformat(definition))

    def get_clean_envelope_definition(self, *args, **kwargs):
        """Cleans out the envelope definition by removing unused fields.  It also
        swaps out the key name for a lowerCamelCase version of it.  It's not at all clear
        why docusign in their wisdom can't support both camel and non-camel with their own
        tools prefer snake case..
        """

        _envelope_definition = self.get_envelope_definition(*args, **kwargs).to_dict()
        # print(self.get_envelope_definition(*args, **kwargs))
        envelope_definition = {}

        def rename_key(key):
            """Convert snake to lower camel case"""
            components = key.split("_")
            return components[0] + "".join(_x.title() for _x in components[1:])

        def convert_iterable(_x):
            """Work through interables and do the right thing"""
            if isinstance(_x, (list, tuple)):
                return [convert_iterable(y) for y in _x if y is not None]
            if isinstance(_x, dict):
                return {
                    rename_key(_k): convert_iterable(_v) for _k, _v in _x.items() if _v is not None
                }
            return _x

        for k, v in _envelope_definition.items():
            if v is None:
                continue
            key = rename_key(k)
            if isinstance(v, (list, tuple)):
                envelope_definition[key] = [convert_iterable(x) for x in v]
            elif isinstance(v, dict):
                envelope_definition[key] = {
                    rename_key(_k): convert_iterable(_v) for _k, _v in v.items() if _v is not None
                }
            else:
                envelope_definition[key] = v
        return envelope_definition

    def create_envelope(self, *args, **kwargs) -> dict:
        """Send a document for signatures"""
        envelope_definition = kwargs.pop("envelope_definition", None)
        if envelope_definition is None:
            envelope_definition = self.get_clean_envelope_definition(*args, **kwargs)
        response = self.session_rest_post(rest_url="/envelopes", data=envelope_definition)
        if response.status_code != 201:
            log.error(
                f"Issue creating envelope {pprint.pformat(envelope_definition)} -> "
                f"{response.json()}"
            )
            if response.status_code == 401:
                return {"envelopeId": None}

        return response.json()

    def update_envelope(self, envelope_id: str, data: dict | None) -> dict:
        try:
            self.check_token()
        except DocusignTokenException:
            if self.should_raise_token_exception():
                raise
            return {}
        response = self.session_rest_put(rest_url=f"/envelopes/{envelope_id}", data=data)
        if response.status_code != 200:
            self.dump_envelope(response.json())
        return response.json()

    def get_envelope_statuses(self, envelope_ids: str | list) -> dict:
        """Get the status of a set of envelopes."""
        rest_url = "/envelopes/status"
        data = {"envelopeIds": envelope_ids if isinstance(envelope_ids, list) else [envelope_ids]}
        params = {"envelope_ids": "request_body", "count": len(envelope_ids)}
        response = self.session_rest_put(rest_url, data=data, params=params)
        if response.status_code == 401:
            return {"envelopes": []}
        return response.json()

    def get_envelope_form_data(self, envelope_id: str) -> dict:
        """Get an individual envelope status.  It will tell us who we are waiting on."""
        rest_url = "/envelopes/" + envelope_id + "/form_data"
        response = self.session_rest_get(rest_url)
        if response.status_code == 401:
            return {}
        return response.json()

    def get_documents_for_envelope(self, envelope_id: str) -> dict:
        """Gets the documents associated with an envelope"""
        rest_url = "/envelopes/" + envelope_id + "/documents"
        response = self.session_rest_get(rest_url)
        if response.status_code == 401:
            return {"envelopeDocuments": []}
        return response.json()

    def get_document_object(self, url: str) -> bytes:
        """Simply download the file"""
        response = self.session_rest_get(url, stream=True)
        if response.status_code == 401:
            return bytes("No data".encode())
        content = response.content
        if isinstance(content, str):
            content = content.encode("utf-8")
        output_stream = BytesIO(content)
        output_stream.seek(0)
        return output_stream.read()

    def get_completed_documents(self, envelope_id: str) -> list:
        """Gets the completed documents"""
        documents = []
        doc_list = self.get_documents_for_envelope(envelope_id)
        for item in doc_list.get("envelopeDocuments", []):
            item["document"] = self.get_document_object(item.get("uri"))
            documents.append(item)
        return documents


class DocuSignObject(BaseDocuSignObject):
    """The exportable version"""

    def get_envelope_signing_status(self, envelope_id):
        """Who the heck we are waiting on status."""
        _data = self.get_envelope_form_data(envelope_id)

        try:
            signed = [_x["name"] for _x in _data["recipientFormData"] if not _x.get("signedTime")]
            remaining = [
                _x["name"] for _x in _data["recipientFormData"] if not _x.get("signedTime")
            ]
        except KeyError as exc:
            raise KeyError(f"{envelope_id} response have missing keys. {exc}")

        if remaining:
            msg = "Waiting on %s signers specifically %s" % (len(remaining), remaining[0])
        else:
            msg = "Complete - All signers have signed"

        return {
            "status": _data["status"],
            "status_message": msg,
            "signed": signed,
            "waiting_on": remaining[0] if remaining else None,
            "remaining_signers": remaining,
            "source": _data,
        }


class DocuSignDeclarativeTemplate(DocuSignObject):
    """A declarative version of `DocuSignBuilderObject`."""

    email_subject = "Signing Required"
    email_message = ""
    signers = []  # List of {'kwarg': 'user1', 'page': n, 'coordinates': (x, y)}

    def get_format_kwargs(self, **kwargs):
        return kwargs

    # pylint: disable=too-many-locals, arguments-differ
    def get_envelope_definition(
        self, customer_document, carbon_copies_users: Optional[List[User]] = None, **kwargs
    ):
        """Build an envelope from static attributes.

        The each of the `signers` dictionaries should contain a `kwarg` entry that corresponds to
        a name sent to `**kwargs` at runtime that provides the signing user.
        """

        if not self.signers:
            raise ValueError(
                "Signers list must have at least one dict like {'kwarg', 'page', 'coordinates'}."
            )

        if not carbon_copies_users:
            carbon_copies_users = []

        format_kwargs = self.get_format_kwargs(customer_document=customer_document, **kwargs)

        signing_users = [
            (spec["kwarg"], kwargs[spec["kwarg"]])
            for spec in self.signers
            if spec["kwarg"] in kwargs
        ]

        # Docusign do not allow recipients with same email
        for _, user in signing_users:
            for carbon_copies_user in carbon_copies_users[:]:
                if user.email == carbon_copies_user.email:
                    carbon_copies_users.remove(carbon_copies_user)

        signer_tabs = []
        recipient_id_counter = 1
        routing_order_counter = 1
        for i, k_user in enumerate(signing_users):
            k, user = k_user
            page = self.signers[i]["page"]
            x, y = self.signers[i]["coordinates"]
            sign_here = SignHere(
                document_id=customer_document.id,
                page_number=page,
                recipient_id="{}".format(i + 1),
                tab_label="SignHereTab",
                x_position=x,
                y_position=y,
            )
            signer = Signer(
                email=user.email,
                name=user.get_full_name(),
                recipient_id=f"{recipient_id_counter}",
                routing_order=f"{routing_order_counter}",
            )
            recipient_id_counter += 1
            routing_order_counter += 1

            field_tabs = defaultdict(list)
            for field_name, field_info in self.signers[i].get("fields", {}).items():
                page = "{}".format(field_info["page"])
                x, y = field_info["coordinates"]
                width, height = field_info.get("dimensions", (None, None))
                required = field_info.get("required", True)
                field_type = field_info["type"]
                value = field_info.get("value")
                font_size = field_info.get("font_size", "size14")
                if isinstance(value, str):
                    value = value.format(**format_kwargs)
                field_tabs[field_type].append(
                    Text(
                        document_id=customer_document.id,
                        page_number=page,
                        x_position=x,
                        y_position=y,
                        font="helvetica",
                        font_size=font_size,
                        tab_label=field_name,
                        height=height,
                        width=width,
                        locked="true" if field_info.get("locked", False) else "false",
                        value=value,
                        required="true" if required else "false",
                    )
                )

            signer.tabs = Tabs(sign_here_tabs=[sign_here], **field_tabs)
            signer_tabs.append(signer)

        content_bytes = customer_document.document.read()
        base64_file_content = base64.b64encode(content_bytes).decode("ascii")
        name = self.name if hasattr(self, "name") else self.__class__.__name__
        document = Document(
            document_base64=base64_file_content,
            name=name,
            file_extension="pdf",
            document_id=customer_document.id,
        )

        subject = self.email_subject.format(**format_kwargs)
        paragraphs = [
            re.sub(r"\s+", " ", p) for p in self.email_message.format(**format_kwargs).split("\n\n")
        ]
        message = "\n\r\n\r".join(paragraphs)

        carbon_copies = []
        for i, user in enumerate(carbon_copies_users):
            carbon_copies.append(
                CarbonCopy(
                    name=user.get_full_name(),
                    email=user.email,
                    recipient_id=f"{recipient_id_counter}",
                    routing_order=1,
                )
            )
            recipient_id_counter += 1

        envelope_definition = EnvelopeDefinition(
            email_subject=subject,
            email_blurb=message,
            documents=[document],
            recipients=Recipients(signers=signer_tabs, carbon_copies=carbon_copies),
            status="sent",
            notification=self.get_envelope_notification(),
        )
        return envelope_definition

    def get_envelope_notification(self) -> Notification:
        """
        Get default notification and reminder settings for current template
        https://www.docusign.com/blog/dsdev-common-api-tasks-add-reminders-and-expiration-to-an-envelope
        :return:
        """
        notification = Notification()
        notification.use_account_defaults = "false"  # customize the notification for this envelope
        reminders = Reminders()
        reminders.reminder_enabled = "true"
        reminders.reminder_delay = "5"  # first reminder to be sent 5 days after envelope was sent
        reminders.reminder_frequency = "3"  # keep sending reminders every 3 days

        expirations = Expirations()
        expirations.expire_enabled = "true"
        expirations.expire_after = "30"  # envelope will expire after 30 days
        expirations.expire_warn = (
            "2"  # expiration reminder would be sent two days before expiration
        )

        notification.expirations = expirations
        notification.reminders = reminders
        return notification
