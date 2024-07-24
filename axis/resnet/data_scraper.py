"""data_scraper.py: Django resnet"""
import datetime
import logging
import re
from collections import OrderedDict

import dateutil.parser
import requests
from bs4 import BeautifulSoup, NavigableString
from django.utils.timezone import now

__author__ = "Steven Klass"
__date__ = "7/25/14 9:26 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class RESETHTTPParser(object):
    """Base resnet parser interface class"""

    def __init__(self, *args, **kwargs):
        self.base_url = "https://www.resnet.us"

        self.start_page = self.get_start_page()

        self.soup = BeautifulSoup(self.start_page, "lxml")

    @property
    def page(self):
        """Relative path to page that will be parsed"""
        raise NotImplementedError

    def get_start_page(self):
        """Make HTTP request to page and read output"""
        headers = {"content-type": "application/json", "User-Agent": "curl/7.47.1"}
        request = requests.get(self.base_url + self.page, headers=headers)
        assert request.status_code == 200
        return request.content

    @staticmethod
    def decode_obscured_data(data, offset=0):
        """What we find with RESNET is they like to obscure the data using javascript,
        in a little function which has the following signature

        Email: <script type="text/javascript">function HYugmFoB(e) {
         for (i = 0; i <= e.length; i+=2) {
         document.write(String.fromCharCode((parseInt((('0x') + e.substring(i,i+2)),16)) - (2)));}}
         HYugmFoB('3e63226a7467683f246f636b6e76713c6d63766a7b42636a67747
          16b70653065716f24406d63766a7b42636a6774716b70653065716f3e316340');</script>

        Looking at this there are two components to reversing this the long ass string, and the
        offset which appears to be changing

        Feeding the long string with the offset into it will result in:
        decode_obscured_data(x, 2)
        u'<a href="mailto:kathy@aheroinc.com">kathy@aheroinc.com</a>'
        """
        split_data = ["{}{}".format(data[i], data[i + 1]) for i in range(0, len(data), 2)]
        # pylint: disable=eval-used
        return "".join([chr(int(eval("0x{}".format(x))) - offset) for x in split_data])

    def extract_email(self, text):  # pylint: disable=inconsistent-return-statements
        """Extract Email -- Note!  This does not appear to be used any more"""
        off = r"e.substring\(i,\s*i\s*\+\s*2\s*\)\s*\)\s*,\s*16\s*\)\s*\)\s*\-\s*\(\s*(\-?\d+)\s*\)"
        match = re.search(off, text)
        if not match:
            log.error("Unable to find offset in %s", text)
            return
        offset = match.group(1)
        match = re.search(r"function\s+([a-zA-Z0-9]+)\(", text)
        if not match:
            log.error("Unable to find function name in %s", text)
            return
        function = match.group(1)
        data_reg = function + r"\(('|\")([a-zA-Z0-9]+)('|\")\)"
        match = re.search(data_reg, text)
        if not match:
            log.error("Unable to find data in %s", text)
            return
        data = match.group(2)
        parsed = self.decode_obscured_data(data, int(offset))
        return BeautifulSoup(parsed, "lxml").text


class RESENTProvider(RESETHTTPParser):
    """Providers parser class"""

    page = "/providers/accredited-providers/accredited-rating-providers/"

    def parse_member(self, entry):  # noqa: MC0001
        """Parse member html to dict"""
        data = {}
        # Get the name and remove it.
        data["name"] = entry.find("b").text
        entry.find("b").clear()

        email = None
        for item in entry.find_all("a"):
            href = item.get("href")
            if "mailto:" in href:
                email = re.sub(r"mailto:", "", href)
            else:
                if data.get("home_page"):
                    log.warning("Already found home page -- %r >> %r", data["home_page"], href)
                data["home_page"] = href

        elements = []
        for item in entry.childGenerator():
            if isinstance(item, NavigableString):
                x = re.sub(r"\n", "", item.extract()).strip()
                if x:
                    elements.append(x)

        if elements and elements[0].strip():
            data["street_line1"] = elements[0]
            if len(elements[0].split(",")) > 1:
                data["street_line1"] = elements[0].split(",")[0].strip()
                data["street_line2"] = elements[0].split(",")[1].strip()

        for element in elements[1:]:
            if re.search(r"Email:", element):
                continue

            match = re.search(r"Accreditation Identification Number:\s*(\d\d\d\d\-\d+)", element)
            if match:
                data["provider_id"] = match.group(1)

            match = re.search(r"Date of Expiration:\s(.*)", element)
            if match and match.group(1):
                try:
                    expire = dateutil.parser.parse(match.group(1).strip())
                    data["resnet_expiration"] = expire.replace(tzinfo=datetime.timezone.utc)
                except TypeError:
                    pass

            match = re.search(r"(.*),\s+([A-Z][A-Z])\s+(\d\d\d\d\d)", element)
            if match:
                data["city"] = match.group(1).strip()
                data["state"] = match.group(2).strip()
                data["zipcode"] = match.group(3).strip()
                continue

            match = re.search(r"Phone:\s*\(?(\d\d\d).*(\d\d\d).*(\d\d\d\d)", element)
            if match:
                data["office_phone"] = "({}) {}-{}".format(
                    match.group(1), match.group(2), match.group(3)
                )
                continue

            match = re.search(r"Fax:\s*\(?(\d\d\d).*(\d\d\d).*(\d\d\d\d)", element)
            if match:
                data["office_fax"] = "({}) {}-{}".format(
                    match.group(1), match.group(2), match.group(3)
                )
                continue

            match = re.search(r"Contact:\s*(.*)", element)
            if match:
                data["users"] = []
                user = {}
                user["name"] = match.group(1)
                if email:
                    user["email"] = email
                if len(match.group(1).split(",")) == 2:
                    user["name"] = match.group(1).split(",")[0].strip()
                    user["title"] = match.group(1).split(",")[1].strip()
                data["users"].append(user)
                continue

        if None in [data.get("name"), data.get("state")]:
            log.warning("Unable to parse valid components from %s", entry)
            return {}
        return data

    @staticmethod
    def _parse_accreditation(entry):
        match = re.search(r"(\d\d\d\d\-\d+)", entry.text)
        if match:
            return {"provider_id": match.group(1)}
        return {}

    @staticmethod
    def _parse_expiration(entry):
        match = re.search(r"Date of Expiration:\s(.*)", entry.text)
        if match:
            expire = dateutil.parser.parse(match.group(1).strip())
            expire = expire.replace(tzinfo=datetime.timezone.utc)
            return {"resnet_expiration": expire}
        return {}

    def _get_entries(self):
        return self.soup.find_all("span", id=re.compile(r"ctl"))

    def parse(self, max_count=None):
        """
        Parsing providers output
        :param max_count: max entries to parse
        :return: list of parsed entries
        """
        entries = self._get_entries()
        log.debug("Parsing %s from %s", len(entries) / 3, self.soup.title.text)
        data = OrderedDict()

        for entry in entries:
            if max_count and entries.index(entry) > max_count:
                break
            full_id = entry.attrs.get("id")
            match = re.search(r"_ctl(\d+)_(Member|Accreditation|Expiration)$", full_id)
            if not match:
                log.warning("Skipping: %s", full_id)
                continue
            _id, _type = match.groups()
            if _id not in data.keys():
                data[_id] = {}

            if _type == "Member":
                data[_id].update(self.parse_member(entry))
            elif _type == "Accreditation":
                data[_id].update(self._parse_accreditation(entry))
            elif _type == "Expiration":
                data[_id].update(self._parse_expiration(entry))
            else:
                log.warning("Cannot handle %s", _type)

            data[_id]["is_provider"] = False
            if data[_id].get("resnet_expiration"):
                data[_id]["is_provider"] = data[_id]["resnet_expiration"] > now()

        return list(data.values())


class RESNETSamplingProvider(RESENTProvider):
    """Sample providers parser class"""

    page = "/providers/accredited-providers/accredited-rating-sampling-providers/"

    def parse(self, max_count=None):
        """
        Parsing sampling providers output
        :param max_count: max entries to parse
        :return: list of parsed entries
        """
        data = super(RESNETSamplingProvider, self).parse(max_count=max_count)
        for company in data:
            del company["is_provider"]
            company["is_sampling_provider"] = False
            if company.get("resnet_expiration"):
                company["is_sampling_provider"] = company["resnet_expiration"] > now()
        return data


class RESNETTrainingProvider(RESENTProvider):
    """Training providers parser class"""

    page = "/providers/accredited-providers/accredited-rater-training-providers/"

    def _get_entries(self):
        return self.soup.find_all("p", class_=re.compile(r"trainingProviderInfo"))

    def parse_member(self, entry):  # noqa: MC0001
        """Parse member html to dict"""
        data = {}
        # Get the name and remove it.
        data["name"] = entry.find("b").text
        entry.find("b").clear()

        email = None
        for item in entry.find_all("a"):
            href = item.get("href")
            if "mailto:" in href:
                email = re.sub(r"mailto:", "", href)
            else:
                if data.get("home_page"):
                    log.warning("Already found home page -- %r >> %r", data["home_page"], href)
                data["home_page"] = href

        elements = []
        for item in entry.children:
            if item.text.strip():
                elements.append(item.text)

        if elements and elements[0].strip():
            first_part = None
            match = re.search(r"(.*)\s([A-Z][A-Z])\s(\d\d\d\d\d)", elements[0])
            if match:
                first_part = match.group(1).strip()
                data["state"] = match.group(2).strip()
                data["zipcode"] = match.group(3).strip()

            if first_part and len(first_part.split(",")) > 1:
                data["street_line1"] = first_part.split(",")[0].strip()

        for element in elements[1:]:
            if re.search(r"Email:", element):
                continue

            match = re.search(r"Accreditation Identification Number:\s*(\d\d\d\d\-\d+)", element)
            if match:
                data["provider_id"] = match.group(1)

            match = re.search(r"Date of Expiration:\s(.*)", element)
            if match and match.group(1):
                try:
                    expire = dateutil.parser.parse(match.group(1).strip())
                    data["resnet_expiration"] = expire.replace(tzinfo=datetime.timezone.utc)
                except TypeError:
                    pass

            match = re.search(r"Phone:\s*\(?(\d\d\d).*(\d\d\d).*(\d\d\d\d)", element)
            if match:
                data["office_phone"] = "({}) {}-{}".format(
                    match.group(1), match.group(2), match.group(3)
                )
                continue

            match = re.search(r"Fax:\s*\(?(\d\d\d).*(\d\d\d).*(\d\d\d\d)", element)
            if match:
                data["office_fax"] = "({}) {}-{}".format(
                    match.group(1), match.group(2), match.group(3)
                )
                continue

            match = re.search(r"Contact:\s*(.*)", element)
            if match:
                data["users"] = []
                user = {}
                user["name"] = match.group(1)
                if email:
                    user["email"] = email
                if len(match.group(1).split(",")) == 2:
                    user["name"] = match.group(1).split(",")[0].strip()
                    user["title"] = match.group(1).split(",")[1].strip()
                data["users"].append(user)
                continue

        if None in [data.get("name"), data.get("state")]:
            log.warning("Unable to parse valid components from %s", entry)
            return {}
        return data

    def parse(self, max_count=None):
        """
        Parsing training providers output
        :param max_count: max entries to parse
        :return: list of parsed entries
        """
        entries = self._get_entries()
        log.debug("Parsing %s from %s", len(entries), self.soup.title.text)
        data = []
        for entry in entries:
            if max_count and entries.index(entry) > max_count:
                break
            result = self.parse_member(entry.parent)
            result["is_training_provider"] = False
            if result.get("resnet_expiration"):
                result["is_training_provider"] = result["resnet_expiration"] > now()
            data.append(result)
        return data


class RESNETWaterSenseProvider(RESENTProvider):
    """Water sense providers parser class"""

    page = "/providers/accredited-providers/approved-watersense-providers/"

    def parse(self, max_count=None):
        """
        Parsing water sense providers output
        :param max_count: max entries to parse
        :return: list of parsed entries
        """
        data = super(RESNETWaterSenseProvider, self).parse(max_count=max_count)
        for company in data:
            del company["is_provider"]
            company["is_watersense_provider"] = False
            if company.get("resnet_expiration"):
                company["is_watersense_provider"] = company["resnet_expiration"] > now()
        return data
