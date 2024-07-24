"""hes.py: Django """


import base64
import datetime
import logging
import os
import re
from io import BytesIO

from django.apps import apps

import requests
from lxml import etree
from lxml.etree import XMLSyntaxError
from requests import HTTPError

from .models import HESCredentials

__author__ = "Steven K"
__date__ = "11/14/2019 09:12"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

log = logging.getLogger(__name__)
app = apps.get_app_config("hes")


class SoapError(Exception):
    """General Soap Error"""

    def __init__(self, *_args, **kwargs):
        self.error_string = kwargs.pop("faultstring", None)
        for k, v in kwargs.items():
            setattr(self, k, v)


class DOEAuthenticationError(Exception):
    """General Auth Error"""

    pass


class DOEAPIError(Exception):
    """General Auth Error"""

    pass


class NRELValidationError(Exception):
    """NREL HPXML Validation Error"""

    pass


class DOEValidationError(Exception):
    """DOE Validation Error"""

    pass


class DOEInterface:
    """This provides an interface to the DOE HES Calculator.


    This was developed using zeep

    API Documentation: https://hes-documentation.labworks.org/home/api-definitions/api-methods

    Using Zeep to get the data can be done by inspecting the XSD files at
    https://sandbox.hesapi.labworks.org/st_api/wsdl

    The main wsdl gives you the data you need to find out
    client = Client(base_url, plugins=[history])

    result = client.service.retrieve_label_results(
        building_info={'user_key': api_key, 'session_token': session_token, 'building_id': 225883})

    try:
        for hist in [history.last_sent, history.last_received]:
            print(etree.tostring(hist['envelope'], encoding='unicode', pretty_print=True))
    except (IndexError, TypeError):
        # catch cases where it fails before being put on the wire
        pass

    The trick is figuring out how to put this into the right holder (building_info).  That is
    found in the XSD.
    """

    def __init__(self, **kwargs):
        self.session_token = None
        self.base_url = app.URL
        self.api_key = app.API_KEY

        self.credential_id = kwargs.get("credential_id")
        if self.credential_id:
            credentials = HESCredentials.objects.get(pk=self.credential_id)
            self.username = credentials.username
            self.password = credentials.password
            log.debug(
                "Using %(url)s with credential id %(credential_id)s and key %(api_key)s",
                {
                    "url": self.base_url,
                    "credential_id": self.credential_id,
                    "api_key": "".join(["*" for _x in self.api_key]),
                },
            )
        else:
            self.username = kwargs.get("username")
            self.password = kwargs.get("password")
            log.debug(
                "Using %(url)s with %(username)s:%(password)s and key %(api_key)s",
                {
                    "url": self.base_url,
                    "username": self.username,
                    "password": "".join(["*" for _x in self.password]),
                    "api_key": "".join(["*" for _x in self.api_key]),
                },
            )

        self.headers = {"Content-Type": "text/xml; charset=utf-8"}

        self.namespaces = {
            "soap-env": "http://schemas.xmlsoap.org/soap/envelope/",
            "ns1": "http://hesapi.labworks.org/st_api/serve",
        }

        self.dump_file = False
        self.session_token = None
        self.building_id = None
        self.dump_requests = kwargs.get("dump_requests")
        self.dump_responses = kwargs.get("dump_responses")
        if None in [self.username, self.password, self.api_key]:
            raise KeyError("We need a USERNAME, PASSWORD and API_KEY key defined")

    def post(self, url, *args, **kwargs):
        """This provides a way to mock out all hes posts"""
        return requests.post(url, *args, **kwargs)

    def get(self, url, *args, **kwargs):
        """This provides a way to mock out all hes get"""
        return requests.get(url, *args, **kwargs)

    def dump_request(self, data, method):
        print(etree.tostring(etree.fromstring(data), encoding="unicode", pretty_print=True))
        if self.dump_file:
            with open("%s.xml" % method, "w+") as output:
                output.write("%s\n" % data)
            print("Output saved to %s" % "%s.xml" % method)

    def get_soap_wrapper(self, method, data_holder=None, **data):
        """Gets a soap wrapper for holding the data send in the request"""
        if data_holder is None:
            data_holder = method + "Request"
        wrapper = """
                <soap-env:Envelope xmlns:soap-env="http://schemas.xmlsoap.org/soap/envelope/">
                  <soap-env:Body>
                    <ns0:{data_holder} xmlns:ns0="http://hesapi.labworks.org/st_api/serve">
                      <ns0:{method}>""".format(
            method=method, data_holder=data_holder
        )
        for k, v in data.items():
            wrapper += "<ns0:{key}>{value}</ns0:{key}>".format(key=k, value=v)
        wrapper += """
                      </ns0:{method}>
                    </ns0:{data_holder}>
                  </soap-env:Body>
                </soap-env:Envelope>""".format(
            method=method, data_holder=data_holder
        )
        if self.dump_requests:
            self.dump_request(
                etree.tostring(etree.fromstring(wrapper), encoding="unicode", pretty_print=True),
                method,
            )
        return wrapper

    def verify_response_and_translate_to_xml(self, response, response_key=None, as_list=False):
        """Simply a wrapper method to verify the response and and translate to xml"""
        response.raise_for_status()
        try:
            root = etree.fromstring(response.content)
        except XMLSyntaxError:
            log.exception("Invalid XML returned from %s", response.content)
            raise
        if self.dump_responses:
            print(etree.tostring(root, encoding="unicode", pretty_print=True))
        errors = {}
        for element in root.xpath("soap-env:Body/soap-env:Fault", namespaces=self.namespaces):
            for error in element:
                errors[error.tag] = error.text

        if errors:
            raise SoapError("Soap response %r" % errors, **errors)

        if response_key is None:
            return root

        data = []
        paths = root.xpath(response_key, namespaces=self.namespaces)
        for path in paths:
            for ele in path:
                data.append({ele.tag.split("}")[-1]: ele.text})
            else:
                data.append({path.tag.split("}")[-1]: path.text})

        if not data:
            print(
                "%s not found in %r"
                % (response_key, etree.tostring(root, encoding="unicode", pretty_print=True))
            )
            log.error(
                "%s not found in %r",
                response_key,
                etree.tostring(root, encoding="unicode", pretty_print=True),
            )
            return None
        if len(data) == 1:
            return data[0]
        if len(data) > 1:
            # Support lists of data
            keys = [key for item in data for key in item.keys()]
            if len(keys) % len(set(keys)) == 0:
                _results = []
                _res = {}
                for item in data:
                    if list(item.keys())[0] in _res:
                        _results.append(_res)
                        _res = {}
                    _res[list(item.keys())[0]] = list(item.values())[0]
                _results.append(_res)
                return _results if len(_results) > 1 or as_list else _results[0]
        return data

    def request_token(self, request):
        """Broke out so we can test this"""
        return self.post(self.base_url, headers=self.headers, data=request.encode("utf-8"))

    def get_session_token(self):
        """Authenticate and get a session token
        https://hes-documentation.labworks.org/home/api-definitions/api-methods/get_session_token
        """
        if self.session_token:
            return
        info = {"user_key": self.api_key, "user_name": self.username, "password": self.password}
        data = self.get_soap_wrapper("get_session_token", **info)
        response = self.post(self.base_url, headers=self.headers, data=data.encode("utf-8"))
        response_key = "//ns1:get_session_token_result/*"
        try:
            data = self.verify_response_and_translate_to_xml(response, response_key)
        except SoapError as err:
            raise DOEAuthenticationError(
                err.error_string + " Username: %s Password: %s" % (self.username, self.password)
            )
        self.session_token = data["session_token"]
        return self.session_token

    def destroy_session_token(self):
        """Destroy our session token
        https://hes-documentation.labworks.org/home/api-definitions/api-methods/destroy_session_token
        """
        info = {"user_key": self.api_key, "session_token": self.session_token}
        data = self.get_soap_wrapper("destroy_session_token", **info)
        response_key = "//ns1:destroy_session_token_result/*"
        response = self.post(self.base_url, headers=self.headers, data=data.encode("utf-8"))
        try:
            data = self.verify_response_and_translate_to_xml(response, response_key)
        except SoapError as err:
            raise DOEAPIError(err.error_string)
        if data.get("result") != "OK":
            raise DOEAPIError(data.get("result"))
        self.session_token = None

    # TODO: Type-hint `hpxml` - do we need to support all three types currently supported? Are they actually
    #  all being used? What type is being assumed when we try to call read()?
    def submit_hpxml_inputs(self, hpxml) -> int:
        """Submit HPXML to DOE
        https://hes-documentation.labworks.org/home/api-definitions/api-methods/submit_hpxml_inputs

        :returns: The Home Energy Score ID of the building created by this request
        """
        if not self.session_token:
            self.get_session_token()

        if isinstance(hpxml, str):
            if os.path.exists(hpxml):
                with open(hpxml, "rb") as _hpxml:
                    hpxml = _hpxml.read()
            else:
                hpxml = hpxml.encode("utf-8")
        elif isinstance(hpxml, etree._Element):
            hpxml = etree.tostring(hpxml, encoding="unicode").encode("utf-8")
        else:
            try:
                hpxml = hpxml.read().encode("utf-8")
            except AttributeError:
                pass

        info = {
            "user_key": self.api_key,
            "session_token": self.session_token,
            "hpxml": base64.b64encode(hpxml).decode("ascii"),
        }

        data = self.get_soap_wrapper("submit_hpxml_inputs", **info)
        response_key = "//ns1:submit_hpxml_inputs_result/*"
        response = self.post(self.base_url, headers=self.headers, data=data.encode("utf-8"))

        try:
            data = self.verify_response_and_translate_to_xml(response, response_key)
        except SoapError as err:
            raise DOEAPIError(err.error_string)
        except HTTPError as error:
            raise DOEAPIError(str(error))

        if data.get("result") != "OK" or data.get("building_id") == 0:
            error = data.get("result") or "Missing Building ID"
            if data.get("message"):
                error = data.get("message")
                # DOE's API sometimes returns a stack trace, reformat it for readability
                if error.startswith("Traceback"):
                    error = re.sub("&#13;", "\n", error)
            raise DOEAPIError(error)

        return data["building_id"]

    def retrieve_file(self, url, extension=None):
        """Retrieves the file from a url"""

        request = self.get(url)
        if request.status_code != requests.codes.ok:
            raise DOEAPIError(
                "Download Error %s - Unable to get a filename from %s", request.status_code, url
            )

        file_name = url.split("/")[-1].split("%2F")[-1].split("&")

        if len(file_name) == 1:  # This is the pdf
            file_name = file_name[0]
            page = None
        elif len(file_name) == 2:  # This is the png
            file_name, page = file_name
            page = int(page.split("=")[-1])
        else:
            raise DOEAPIError("Page Parse Error - Unable to get a filename from %s", url)

        split_name, ext = os.path.splitext(file_name)
        if extension and extension != ext:
            file_name = ".".join([split_name, extension])

        if not file_name.startswith("hes_label_"):
            file_name = "hes_label_" + file_name

        return {"name": file_name, "page": page, "document": BytesIO(request.content)}

    def validate_inputs(self, building_id):
        """Validate
        https://hes-documentation.labworks.org/home/api-definitions/api-methods/validate_inputs
        """
        if not self.session_token:
            self.get_session_token()

        info = {
            "user_key": self.api_key,
            "session_token": self.session_token,
            "building_id": building_id,
        }

        data = self.get_soap_wrapper("building_info", "validate_inputsRequest", **info)

        response_key = "//ns1:validation_message/*"
        response = self.post(self.base_url, headers=self.headers, data=data.encode("utf-8"))
        try:
            issues = self.verify_response_and_translate_to_xml(response, response_key, as_list=True)
        except SoapError as err:
            raise DOEAPIError(err.error_string)

        if issues:
            msg = "Validation Error %(count)s issue(s) found:\n" % {"count": len(issues)}
            for issue in issues:
                msg += " - %(field)s: [%(type)s] %(message)s\n" % issue
            raise DOEValidationError(msg)

    def generate_label(
        self,
        building_id: int,
        force_regenerate: bool = False,
        is_final: bool = False,
        retrieve: bool = True,
    ) -> dict:
        """
        https://hes-documentation.labworks.org/home/api-definitions/api-methods/generate_label

        :param building_id: The Home Energy Score building ID of the building for which to generate a label.
          This is the ID returned by submit_hpxml_inputs.
        :param force_regenerate: Pass True to force the label to be regenerated. Otherwise the HES API will
          simply return the already-generated label from a previous call.
        :param is_final: Pass True to generate a "final" label, which includes no upgrade recommendations.
        :param retrieve: Pass False to skip loading the actual files in the return dict
        """
        if not self.session_token:
            self.get_session_token()

        info = {
            "user_key": self.api_key,
            "session_token": self.session_token,
            "building_id": building_id,
            # The HES API is inconsistent: the force_regenerate field is an integer field, and
            # is_final is a boolean field.
            "force_regenerate": 1 if force_regenerate else 0,
            "is_final": is_final,
        }
        data = self.get_soap_wrapper("building_label", "generate_labelRequest", **info)
        response = self.post(self.base_url, headers=self.headers, data=data.encode("utf-8"))

        try:
            root = self.verify_response_and_translate_to_xml(response)
        except SoapError as err:
            if "Call validate_inputs for more information" in err.error_string:
                self.validate_inputs(building_id=building_id)
            raise DOEAPIError(err.error_string)
        except HTTPError as error:
            if "Too Many Requests" in "%s" % error:
                from .tasks import generate_label

                log.warning("We are being throttled - on `generate_label`")

                # task.retry() raises an exception, so execution will terminate here
                # TODO: Rewrite this so that we pass a handler into the function call instead
                #  of this. The current construct makes testing difficult because a throttle
                #  error will always result in the task being triggered, even if we weren't
                #  calling this function from a task in the first place.
                generate_label.retry(exc=error)
            raise DOEAPIError("%s" % error)

        # TODO: Can we retrieve these values more cleanly? Realistically PNNL isn't likely
        #  to change the aliases they assign their namespaces, but it's really not a great
        #  idea to have the aliases hard-coded on the client side because there's nothing
        #  guaranteeing that they won't change
        data = {
            "result": root.xpath("//ns1:result", namespaces=self.namespaces)[0].text,
            "message": root.xpath("//ns1:message", namespaces=self.namespaces)[0].text,
            "files": [],
        }
        for file in root.xpath("//ns1:file", namespaces=self.namespaces):
            data["files"].append(
                {"".join(ele.tag.split("}")[-1]): ele.text for ele in file.getchildren()}
            )

        if data.get("result") != "OK":
            raise DOEAPIError("No Result provided", data)

        if retrieve and data["files"]:
            files = data.pop("files")
            data["files"] = []
            for file_data in files:
                item = file_data.copy()
                item.update(self.retrieve_file(file_data["url"], extension=file_data.get("type")))
                data["files"].append(item)
        return data

    def _present_data(self, data):
        """Normalize out some of these fields."""
        date_keys = ["assessment_date", "create_label_date"]
        string_keys = [
            "address",
            "city",
            "state",
            "zip_code",
            "assessment_type",
            "qualified_assessor_id",
            "hescore_version",
            "weather_station_location",
        ]
        float_keys = ["average_state_cost", "average_state_eui"]
        boolean_keys = ["cooling_present"]

        for key, value in data.items():
            if key in date_keys:
                try:
                    data[key] = datetime.datetime.strptime(value, "%Y-%m-%d").date()
                except (ValueError, TypeError, KeyError):
                    pass
            elif key in float_keys:
                try:
                    data[key] = float(value)
                except TypeError:
                    pass
            elif key in boolean_keys:
                try:
                    data[key] = bool(value)
                except TypeError:
                    pass
            elif key not in string_keys:
                try:
                    data[key] = int(value)
                except TypeError:
                    pass
        return data

    def retrieve_label_results(self, building_id):
        """https://hes-documentation.labworks.org/home/api-definitions/
        api-methods/retrieve_label_results"""

        if not self.session_token:
            self.get_session_token()

        info = {
            "user_key": self.api_key,
            "session_token": self.session_token,
            "building_id": building_id,
        }

        data = self.get_soap_wrapper("building_info", "retrieve_label_resultsRequest", **info)
        response_key = "//ns1:label_result/*"
        response = self.post(self.base_url, headers=self.headers, data=data.encode("utf-8"))
        try:
            data = self.verify_response_and_translate_to_xml(response, response_key)
        except SoapError as err:
            raise DOEAPIError(err.error_string)
        except HTTPError as error:
            if "Too Many Requests" in "%s" % error:
                from .tasks import get_results

                log.warning("We are being throttled - on `retrieve_label_results`")
                get_results.retry(exc=error)
                return
            raise DOEAPIError("%s" % error)
        return self._present_data(data)

    def retrieve_extended_results(self, building_id):
        """https://hes-documentation.labworks.org/home/api-definitions/
        api-methods/retrieve_extended_results"""
        if not self.session_token:
            self.get_session_token()

        info = {
            "user_key": self.api_key,
            "session_token": self.session_token,
            "building_id": building_id,
        }

        data = self.get_soap_wrapper("building_info", "retrieve_extended_resultsRequest", **info)
        response_key = "//ns1:extended_result/*"
        response = self.post(self.base_url, headers=self.headers, data=data.encode("utf-8"))
        try:
            data = self.verify_response_and_translate_to_xml(response, response_key)
        except SoapError as err:
            raise DOEAPIError(err.error_string)
        except HTTPError as error:
            if "Too Many Requests" in "%s" % error:
                from .tasks import get_results

                log.warning("We are being throttled - on `retrieve_extended_results`")
                get_results.retry(exc=error)
                return
            raise DOEAPIError("%s" % error)
        return self._present_data(data)
