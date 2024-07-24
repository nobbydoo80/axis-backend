"""rets.py: Django RESO.data_models"""


import logging

from . import DataModel, ResoXmlMixin

__author__ = "Steven Klass"
__date__ = "06/16/17 09:41"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class RETS_Base(DataModel):
    pass


class RETSXMLBase(RETS_Base, ResoXmlMixin):
    pass


class RETS1p8XML(RETSXMLBase):
    """This sets up the output for 1.8 XML"""

    pass

    @property
    def data(self):
        return {}
