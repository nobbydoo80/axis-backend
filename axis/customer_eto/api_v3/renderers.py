"""renderers.py - Axis"""

__author__ = "Steven K"
__date__ = "8/22/21 12:47"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

import xmltodict

from rest_framework.renderers import BaseRenderer

log = logging.getLogger(__name__)


class XMLRenderer(BaseRenderer):
    """
    Renderer which serializes to XML.
    """

    media_type = "application/xml"
    format = "xml"
    charset = "utf-8"
    item_tag_name = "list-item"
    root_tag_name = "root"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        Renders `data` into serialized XML.
        """
        if data is None:
            return ""
        try:
            if not isinstance(data, list):
                data = [data]

            # Do not set pretty here - It may give you \n right after a tag which ETO will barf on.
            if len(data) == 1:
                return xmltodict.unparse(
                    data[0], pretty=False, full_document=False, short_empty_elements=True
                )
            else:
                return xmltodict.unparse(
                    {"data": {"soap:Envelope": [x["soap:Envelope"] for x in data]}},
                    pretty=False,
                    full_document=False,
                    short_empty_elements=True,
                )
        except AttributeError:
            return data
