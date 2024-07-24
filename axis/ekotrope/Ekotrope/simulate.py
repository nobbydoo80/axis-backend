"""simulate.py: Ekotrope"""


import json
import logging
import random
import re
import time

from lxml import etree

import requests
from requests.auth import HTTPBasicAuth

from axis.ekotrope.models import Project
from axis.ekotrope.tasks import import_project_tree

__author__ = "Steven Klass"
__date__ = "1/21/16 10:23"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class EkotropeAuthenticationError(Exception):
    pass


class EkotropeSimulationFailure(Exception):
    pass


pages = {
    "auth": "https://app.ekotrope.com/#login",
    "login": "https://app.ekotrope.com/ekotrope/v1/auth/login",
    "import_page": "https://app.ekotrope.com/#importProjectsFromRemRate",
    "xml_upload": "https://app.ekotrope.com/servlet.gupld",
    "xml_progress": "https://app.ekotrope.com/ekotrope/v1/remImportJob/{job}",
    "project_list": "http://api.ekotrope.com/api/v1/projects",
    "api_project_list": "http://api.ekotrope.com/api/v1/projects",
    "api_project": "http://api.ekotrope.com/api/v1/projects/{project_id}",
}


class SimulationEngine:
    def __init__(self, auth_details, remxml, *args, **kwargs):
        self.username = auth_details.username
        self.password = auth_details.password
        self.auth_details = auth_details
        self.remxml = remxml
        self.xml_file_name = kwargs.get("xml_file_name")
        self.anonymize = kwargs.get("anonymize", False)
        self.dry_run = kwargs.get("dry_run", False)

        self.success = None
        self.logged_in = False

        self.log = kwargs.get("log", log)
        self.session = requests.Session()
        self.project = None

    def login(self):
        self.session.headers.update(
            **{
                "Accept": "application/json",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",
            }
        )

        request = self.session.get(pages.get("auth"))
        if not request.status_code == 200:
            raise EkotropeAuthenticationError("HTTPBasicAuth Authorization not accepted")

        login_payload = json.dumps({"username": self.username, "password": self.password})
        response = self.session.post(
            pages.get("login"), data=login_payload, headers={"Content-Type": "application/json"}
        )
        if not request.status_code == 200:
            raise EkotropeAuthenticationError("Authorization not accepted on login")

        if not response.json().get("username") == self.username:
            raise EkotropeAuthenticationError("Authorization for username not accepted")

        self.user_id = response.json().get("id")

        self.log.info("%s [%s] has been logged into Ekotrope" % (self.username, self.user_id))

        self.logged_in = True

    def parse_exception(self, response):
        m = re.search(r"Remrate XML translation failed. Context:\n\t(.*)\n\t(.*)", response)

        if m:
            return {
                "message": response,
                "class": "TranslationError",
                "exception": m.group(1),
                "data": m.group(2),
            }
        m = re.search(
            r"Ekotrope converted, but could not analyze the REM/Rate XML. Please ensure "
            "the plan can be analyzed by REM/Rate before sending to Ekotrope.",
            response,
        )
        if m:
            return {
                "raw": response,
                "class": "CannotSimulation",
                "exception": "Simulation",
                "data": None,
            }

        try:
            root = etree.fromstring(str(response))
            return {
                "raw": root.xpath("//message")[0].text,
                "class": root.xpath("//internalErrorCode")[0].text,
                "non_field_errors": [root.xpath("//message")[0].text],
            }
        except:
            pass

        log.error("Unknown error: {}".format(response))
        return {"message": response, "class": None}

    def XXXget_name(self):
        if self.xml_file_name is not None:
            return self.xml_file_name
        return self.remxml.floorplan.name + ".xml"

    def check_project_name(self, project_name):
        auth = HTTPBasicAuth(self.username, self.password)
        request = requests.get(
            pages.get("api_project_list"), params={"name": project_name}, auth=auth
        )
        data = [x for x in request.json() if x["name"] == project_name]
        if len(data) > 1:
            self.log.warning("Multiple projects identified for %r", project_name)
            return
        if len(data) == 1:
            self.log.info("Found existing project %s on Ekotrope", data[0]["id"])
            return data[0]
        return None

    def parse_response(self, data):
        """%%%INI%%%@@^^^?xml version="1.0" encoding="UTF-8"?^^^@@
        @@^^^response^^^@@@@^^^files^^^@@@@^^^file^^^@@@@^^^ctype^^^@@application/xml@@^^^/ctype^^^@@
        @@^^^size^^^@@92915@@^^^/size^^^@@
        @@^^^field^^^@@GWTMU-149233805302356460-0@@^^^/field^^^@@
        @@^^^name^^^@@ALL_FIELDS_SET_14.6.1.xml@@^^^/name^^^@@
        @@^^^/file^^^@@
        @@^^^/files^^^@@
        @@^^^finished^^^@@ok@@^^^/finished^^^@@
        @@^^^message^^^@@@@^^^![CDATA[G6weckk9]]^^^@@@@^^^/message^^^@@
        @@^^^parameters^^^@@@@^^^/parameters^^^@@
        @@^^^/response^^^@@
        %%%END%%%
        """
        if not data.startswith("%%%INI%%%"):
            log.error("Expected response does not start with INI")
        if not data.endswith("%%%END%%%"):
            log.error("Expected response does not end with END")
        result = {}
        for x in data[9:-10].split("\n"):
            split = [y.split("^^^@@") for y in x.split("@@^^^")]
            if split[1][0] == "message" and split[2]:
                result[split[1][0]] = split[2][0]
                if "CDATA" in split[2][0]:
                    result[split[1][0]] = split[2][0].split("[")[-1].split("]")[0]
            elif len(split[1]) == 2 and not split[1][0].startswith("/"):
                result[split[1][0]] = split[1][1]
        return result

    def get_ekotrope_request(self, url, retries=3):
        count = 1
        while True:
            if count > retries:
                if issue:
                    raise issue
                break

            issue = None
            if not self.logged_in:
                self.login()

            request = self.session.get(url, headers={"Content-Type": "application/json"})

            try:
                status_info = request.json()

                if request.status_code == 403:
                    if "User must be logged in" in status_info["message"]:
                        self.logged_in = False
                        continue

            except ValueError as issue:
                time.sleep(1)
                count += 1
            else:
                return request

    def simulate(self, project_name, xml_overrides=None):
        if not self.logged_in:
            self.login()

        if not self.remxml.xml:
            raise IOError("Missing remxml")

        project_xml = "{}.xml".format(project_name)

        params = {"userId": self.user_id, "uploadedFor": "forProjectRemImport"}

        xml = self.remxml.xml
        import lxml

        root = lxml.etree.fromstring(bytes(xml))

        if xml_overrides:
            for tag, value in xml_overrides.items():
                for idx, item in enumerate(root.xpath("//{}".format(tag))):
                    self.log.info(
                        "Replacing outgoing xml field %s with value of %s => %s",
                        tag,
                        item.text,
                        value,
                    )
                    item.text = value

        xml = etree.tostring(
            root,
            pretty_print=True,
            xml_declaration=True,
            encoding="utf-8",
        )
        xml = xml.replace("\n", "\r\n")

        files = [("GWTMU-%s" % format(random.randrange(0, 1e18), "018"), (project_xml, xml))]

        response = self.session.post(pages.get("xml_upload"), params=params, files=files)
        data = self.parse_response(response.content)

        self.log.info(
            "%(xml)s with size %(size)s dispatched %(result)s with Job %(job)s",
            dict(xml=project_xml, size=data["size"], result=data["finished"], job=data["message"]),
        )
        log.info(
            "%(xml)s with size %(size)s dispatched %(result)s with Job %(job)s",
            dict(xml=project_xml, size=data["size"], result=data["finished"], job=data["message"]),
        )

        error_count, count = 0, 0
        status, status_info = None, {}
        start = time.time()
        while True:
            if error_count > 3 or count > 1000:
                break
            try:
                request = self.get_ekotrope_request(
                    pages.get("xml_progress").format(job=data["message"])
                )
            except ValueError as err:
                self.log.info(
                    "Job %(job)s received a ValueError Exception - %(err)s",
                    dict(job=data["message"], err=err),
                )
                error_count += 1
                time.sleep(error_count * 5)
                status_info = {}
            else:
                status_info = request.json()

            if status_info.get("status") != status:
                if status:
                    self.log.info(
                        "Updating status on Job %(job)s from %(prior_status)s to %(status)s",
                        dict(
                            job=data["message"],
                            prior_status=status,
                            status=status_info.get("status"),
                        ),
                    )
                status = status_info.get("status")

            if status_info.get("status") is None:
                log.warning(
                    "Requesting status on Job %(job)s received status %(status_code)s got %(info)s",
                    dict(job=data["message"], status_code=request.status_code, info=status_info),
                )

            if status == "Complete":
                break

            self.log.info(
                "Ekotrope Simulation Job %(job)s %(status)s %(count)s",
                dict(job=data["message"], status=status, count="." * count),
            )
            log.info(
                "Ekotrope Simulation Job %(job)s %(status)s %(count)s",
                dict(job=data["message"], status=status, count="." * count),
            )

            sleep_time = 1 if count < 100 else 2
            sleep_time = sleep_time if count < 300 else 3
            sleep_time = sleep_time if count < 400 else 4
            sleep_time = sleep_time if count < 500 else 5

            time.sleep(sleep_time)

            count += 1

        if status == "Complete":
            request = self.get_ekotrope_request(
                pages.get("xml_progress").format(job=data["message"]) + "/resulturl"
            )
            try:
                result_info = request.json()["results"][0]
            except KeyError as err:
                log.info(
                    "Job %(job)s received a KeyError Exception - %(result)s",
                    dict(job=data["message"], result=request.json()),
                )

            log.info(
                "Job %(job)s simulation is complete in %(simulation_time).2f secs - %(result)s",
                dict(simulation_time=time.time() - start, job=data["message"], result=result_info),
            )

            if result_info["status"] in ["ERROR", "FAILURE"]:
                log.error(
                    "Job %(job)s resulted in %(status)s with a message of %(message)s - %(info)s",
                    dict(
                        job=data["message"],
                        status=result_info["status"],
                        message=result_info["message"],
                        info=result_info,
                    ),
                )
                self.log.error(
                    "Job %(job)s resulted in %(status)s with a message of %(message)s - %(info)s",
                    dict(
                        job=data["message"],
                        status=result_info["status"],
                        message=result_info["message"],
                        info=result_info,
                    ),
                )
                raise EkotropeSimulationFailure(result_info["message"])
            elif result_info["status"] == "WARNING":
                self.log.warning(
                    "Job %(job)s resulted in %(status)s with a message of %(message)s",
                    dict(
                        job=data["message"],
                        status=result_info["status"],
                        message=result_info["message"],
                    ),
                )
            else:
                self.log.info(
                    "Job %(job)s resulted in %(status)s with a message of %(message)s",
                    dict(
                        job=data["message"],
                        status=result_info["status"],
                        message=result_info["message"],
                    ),
                )
        else:
            self.log.error(
                "Job %(job)s did ended in status %(status)s in %(simulation_time).2f secs and with "
                "latest info of %(info)s",
                dict(
                    job=data["message"],
                    status=status,
                    info=status_info,
                    simulation_time=time.time() - start,
                ),
            )

        if status == "Complete" and result_info["status"] not in ["ERROR", "FAILURE"]:
            self.success = True
            request = self.get_ekotrope_request(pages.get("project_list"))
            try:
                self.project = next((x for x in request.json() if x["name"] == project_name), None)
            except TypeError:
                self.log.error(
                    "Job %(job)s was unable to get project (%(project_name)s) - %(request)s",
                    dict(job=data["message"], project_name=project_name, request=request.json()),
                )
            else:
                self.log.info(
                    "Job %(job)s identified as project %(project)s",
                    dict(job=data["message"], project=self.project.get("id")),
                )
                if self.project:
                    self.project_id = self.project.get("id")

        return data

    def import_project(self):
        if self.success and self.project_id:
            import_project_tree(auth_details_id=self.auth_details.id, project_id=self.project_id)
            self.log.info("Project %(project)s has been imported", dict(project=self.project_id))
            return Project.objects.get(id=self.project_id)
        log.error("Unable to find project in Ekotrope - Not good.")
