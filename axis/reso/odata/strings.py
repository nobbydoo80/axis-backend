"""strings.py: Django """


import logging

import datetime

import os
from django.conf import settings

__author__ = "Steven Klass"
__date__ = "8/1/17 16:31"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)

TZ_OFFSET = -7

DATA_DICTIONARY_VERSION = 1.4
TRANSPORT_VERSION = 1.0

SERVER_PROTOCOL = "https" if not settings.DEBUG else "http"
SERVER = "{}://{}.pivotalenergy.net".format(SERVER_PROTOCOL, settings.SERVER_TYPE)

ROOT_URL = "/api/v2/RESO/"

BASE_URL = SERVER + ROOT_URL
LAST_UPDATED = datetime.datetime(2017, 7, 31, tzinfo=datetime.timezone.utc).isoformat()
NOW = datetime.datetime.now(datetime.timezone.utc).isoformat()

raw_not_implemented = """
<error xmlns="http://schemas.microsoft.com/ado/2007/08/dataservices/metadata">
  <code>NOSKIP</code>
  <message xml:lang="en-US">Bad Request - Resource does not support this</message>
</error>
"""

metadata_xml = os.path.abspath(os.path.join(os.path.dirname(__file__), "metadata.xml"))
service_xml = os.path.abspath(os.path.join(os.path.dirname(__file__), "service.xml"))
data_systems_xml = os.path.abspath(os.path.join(os.path.dirname(__file__), "data_systems.xml"))
data_systems_json = os.path.abspath(os.path.join(os.path.dirname(__file__), "data_systems.json"))
