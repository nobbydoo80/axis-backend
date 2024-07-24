"""base.py: Django RESNET"""


import logging
import os

import requests
from django.conf import settings
from lxml import etree

try:
    from .data import RESNETEko, RESNETRem
except (ImportError, ValueError):
    from axis.resnet.RESNET.data import RESNETEko, RESNETRem

from axis.company.models import ProviderOrganization, Company
from axis.resnet.models import RESNETCompany
from axis.remrate_data.models import Simulation

XSD_DOC = os.path.join(settings.SITE_ROOT, "axis", "resnet", "sources", "ResXSDv2.0.xsd")


__author__ = "Steven Klass"
__date__ = "2/16/16 09:48"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True


class RESNETCertificationError(Exception):
    pass


class RESNETMissingID(Exception):
    pass


class RESNETAuthenticationError(Exception):
    pass


class RESNETGeneralError(Exception):
    pass


class RESNETDuplicateError(Exception):
    pass


class RESNET(object):
    def __init__(self, home_status, provider_user, rater_of_record, **kwargs):
        self.home_status = home_status
        self.provider_user = provider_user
        self.rater_of_record = rater_of_record

        self.provider_id = self.get_provider_id(self.provider_user.company, **kwargs)
        self.rater_id = self.get_rater_id(self.rater_of_record, **kwargs)

        self.debug = kwargs.get("debug", settings.RESNET_API_DEBUG)
        self.service = kwargs.get("service", "RegisterStringXMLResponse")

        endpoint = kwargs.get("endpoint", settings.RESNET_API_ENDPOINT)
        self.endpoint = self.get_endpoint(endpoint, self.service)

        self.username = self.provider_user.resnet_username
        self.password = self.provider_user.resnet_password

        if not self.home_status.state == "complete":
            error = "Home: {} must be completed prior to sending to RESNET"
            raise RESNETCertificationError(error.format(self.home_status))

        self.xsd = XSD_DOC
        self.logged_in = False

        self.engine = self.get_xml_engine()

    @staticmethod
    def get_rater_id(rater, **kwargs):
        # Do we were we given a rater_id
        if kwargs.get("rater_id"):
            return kwargs.get("rater_id")

        if not rater:
            error = "Rater of record has not been identified"
            raise RESNETMissingID(error)

        if not rater.rater_id:
            error = (
                "Rater {} does not have RESNET Rater ID Identified or RESNET Axis Link identified"
            )
            raise RESNETMissingID(error.format(rater))

        return rater.rater_id

    @staticmethod
    def get_provider_id(provider, **kwargs):
        # Do we were we given a rater_id
        if kwargs.get("provider_id"):
            return kwargs.get("provider_id")

        if not provider:
            error = "Provider has not been identified"
            raise RESNETMissingID(error)

        try:
            if provider.resnet.provider_id:
                return provider.resnet.provider_id
        except RESNETCompany.DoesNotExist:
            pass

        try:
            if provider.provider_id:
                # log.warning('Provider %s does not have RESNET Axis Link established', provider)
                return provider.provider_id
        except Company.DoesNotExist:
            pass

        error = "Provider {} does not have RESNET Provider ID Identified or RESNET Axis Link identified."
        raise RESNETMissingID(error.format(provider))

    def get_endpoint(self, api_endpoint, service):
        return "{}/{}".format(api_endpoint, service)

    def get_data_type(self):
        if self.service in ["RegisterStringXMLResponse", "RegisterStringStringResponse"]:
            return "XmlString"
        return "XmlDoc"

    def get_content(self):
        data_type = self.get_data_type()
        data = etree.tostring(self.engine.get_data(), pretty_print=self.debug)
        return {
            data_type: data,
            "Username": self.username,
            "Password": self.password,
            "Debug": "true" if self.debug else "false",
        }

    def _parse_response(self, response):
        log.debug(response.content)

        try:
            root = etree.XML(response.content)
            response_code = root.xpath("//ResponseCode")[0].text.strip()
            response_msg = root.xpath("//ResponseMessage")[0].text.strip()
        except Exception as err:
            log.error(
                "{} - Returned: {} -- Unable to parse {}".format(
                    err, response.status_code, response.content
                )
            )
            raise

        if "This appears to be a duplicate rating" in response_msg:
            raise RESNETDuplicateError(response_msg)
        else:
            try:
                registry_id = root.xpath("//RegistryID")[0].text.strip()
            except IndexError:
                msg = "Status Code returned was {} with system code: {} - Msg: {}"
                raise RESNETGeneralError(
                    msg.format(response.status_code, response_code, response_msg)
                )
            if self.debug:
                registry_id = registry_id.split(" ")[0]

        if not response.status_code == 200:
            msg = "Status Code returned was {} with system code: {} - Msg: {}"
            raise RESNETGeneralError(msg.format(response.status_code, response_code, response_msg))

        msg = "Registry responded back with code {} and message: {}"
        log.info(msg.format(response_code, response_msg))
        if "could not be authenticated" in response_msg:
            raise RESNETAuthenticationError(response_msg)
        return response_code, response_msg, registry_id

    def post(self, dry_run=False):
        # FYI - https://brapiv2.resnet.us/post.asmx?op=RegisterStringXMLResponse
        content = self.get_content()

        if not dry_run:
            response = requests.post(self.endpoint, data=content)
            response_code, response, registry_id = self._parse_response(response)
            if registry_id:
                self.engine.set_registry_id(registry_id)
            return response_code, response, registry_id

    def get_xml_engine(self):
        kwargs = {
            "home_status": self.home_status,
            "provider_id": self.provider_id,
            "rater_id": self.rater_id,
            "xsd": self.xsd,
        }
        try:
            if self.home_status.floorplan.remrate_target:
                return RESNETRem(**kwargs)
            else:
                return RESNETEko(**kwargs)
        except Simulation.DoesNotExist:
            return RESNETEko(**kwargs)
