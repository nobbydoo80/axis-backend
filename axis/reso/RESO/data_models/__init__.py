"""__init__.py: Django Reso package container"""


import json

import datetime
from lxml import etree

__author__ = "Steven Klass"
__date__ = "06/16/17 09:28"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


class RESODataModelException(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, "RESO DataModel:", *args, **kwargs)


class DataModel(object):
    def __init__(self, home_status, **kwargs):
        self.input_data = self._get_data_model(home_status, **kwargs)

    def _get_data_model(self, object, **kwargs):
        """Where are we getting our data from"""
        from input_model import InputModel, HomeStatusModel

        if isinstance(object, dict):
            return InputModel(home_status=object, **kwargs)
        return HomeStatusModel(home_status=object, **kwargs)

    @property
    def data(self):
        raise NotImplemented("You need to do this")


def json_serial(obj):
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()


class ResoJsonMixin(object):
    def pprint(self):
        print(json.dumps(self.data, indent=4, default=json_serial))


class ResoXmlMixin(object):
    def element_with_text(self, attr, text, **kwargs):
        key = etree.Element(attr, **kwargs)
        key.text = text
        return key

    def pprint(self, output=None, pretty=True, as_string=False):
        if output:
            with open(output, "wb") as outputfile:
                outputfile.write(
                    etree.tostring(
                        self.data, pretty_print=pretty, xml_declaration=True, encoding="utf-8"
                    )
                )
            return
        if as_string:
            return etree.tostring(
                self.data, pretty_print=pretty, xml_declaration=True, encoding="utf-8"
            )
        print(
            etree.tostring(self.data, pretty_print=pretty, xml_declaration=True, encoding="utf-8")
        )
