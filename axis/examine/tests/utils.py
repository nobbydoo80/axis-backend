"""community_tests.py: Django community.tests"""


import io
import json
import logging
from base64 import b64encode

from django.http import QueryDict

from ..utils import ExamineJSONEncoder

__author__ = "Autumn Valenta"
__date__ = "11/26/14 2:18 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class DummyRequest(object):
    user = None
    query_params = QueryDict("")

    def build_absolute_uri(self, url):
        return url


class MachineryDriver(dict):
    """
    A Python interface for simulating the task of filling out data for a machinery and submitting it
    to the correct endpoint.
    """

    submit_whole_object = True
    raise_response_errors = True

    def __init__(self, machinery_class, **kwargs):
        self.machinery_class = machinery_class
        if "request_user" in kwargs:
            request = DummyRequest()
            request.user = kwargs.pop("request_user")
            request.company = request.user.company
            kwargs.setdefault("context", {})["request"] = request

        self.machinery = self.machinery_class(**kwargs)
        regions = self.machinery.get_regions()
        self.region = regions[0]
        self.ignore_fields = []

    def bind(self, data):
        """Store data that should be tracked as 'dirty' and be sent to the API."""
        self.clear()
        self.update(data)

    def set_ignore_fields(self, *field_list):
        """
        Sets the list of fields to remove from client/response objects for the sake of easier
        testing assertions of equality.  Because the "response object" will return with calculated
        virtual fields based on real fields, "client_object" will not know of these calculated
        fields and will cause assertion errors in testing.
        """
        self.ignore_fields = field_list

    def get_client_object(self):
        """Reduces the object instance to its serialization format (before string encode)."""
        obj = self.machinery.serialize_object(self.machinery.instance)
        obj.update(self)
        data = convert_to_deserialized(obj)

        # Remove any fields that are ignored.
        # We allow the field not not exist in the client data because rest_framework seems to
        # completely exclude PrimaryKeyRelatedField fields from the object when it's in creation
        # mode.  We'll want to exclude certain virtual calculated fields on the response object that
        # may not presently be here on the client data.
        for field in self.ignore_fields:
            data.pop(field, None)

        return data

    def get_response_object(self):
        """Deserializes and extracts the 'object' key of the examine response payload."""
        data = json.loads(self.response.content)["object"]

        # Remove any fields that are ignored.
        for field in self.ignore_fields:
            data.pop(field, None)

        return data

    def encode_file(self, f=None, content_type="text/plain"):
        if f is None:
            f = __file__

        file_obj = f[:-1] if f.endswith("pyc") else f  # passing in compiled python is discouraged

        with io.open(file_obj, encoding="utf-8") as file_content:
            b64content = b64encode(file_content.read().encode("utf-8"))
            b64content = b64content.decode("utf-8")

            return "data:{};base64,{}".format(content_type, b64content)

    def submit(self, client, method, **kwargs):
        """
        Sends the bound data to the correct API endpoint for the given machinery mode.
        :param client: Client object
        :param method: method that using to send request e.g 'get', 'post', 'patch' etc.
        :raise AttributeError: if Client doesn't support method
        :raise AssertionError: when response error occurs and raise_response_errors = True
        :return: response object
        """
        url = self.region["object_endpoint"]

        submit = getattr(client, method)

        kwargs.setdefault("content_type", "application/json")
        if self.submit_whole_object:
            submission_data = self.get_client_object()
        else:
            submission_data = dict(self)
        data = json.dumps(submission_data)
        response = submit(url, data=data, **kwargs)
        if response.status_code >= 400:
            log.error(
                "Problem using %(method)s on %(url)s; data=%(data)r, message=%(message)r",
                {
                    "method": submit.__name__,
                    "url": url,
                    "data": data,
                    "message": response.content,
                },
            )
            if self.raise_response_errors:
                raise AssertionError(
                    "Examine response HTTP %d: %r" % (response.status_code, response.content)
                )

        self.response = response
        return response


def convert_to_deserialized(d):
    """
    Serializes then deserializes the target dict so that it looks as it would if submitted to the
    API from an external client.
    """
    return json.loads(json.dumps(d, cls=ExamineJSONEncoder))
