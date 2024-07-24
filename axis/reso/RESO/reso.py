"""__init__.py: Django __init__.py package container"""


import re

from . import RESOUnsupportedException

__author__ = "Steven Klass"
__date__ = "06/7/17 16:55"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


class RESOBase(object):
    def __init__(self, home_status, **kwargs):
        self.reso_version = kwargs.pop("reso_version", "1.4")
        self.rets_version = kwargs.pop("rets_version", "1.8")

        self.data_flavor = kwargs.pop("data_flavor", "reso")  # reso || rets
        self.output_type = kwargs.pop("output_type", "edmx")  # json || xml || edmx

        # self.data_model = self.get_data_model()(home_status, **kwargs)
        # self.input_data = self.data_model.input_data
        # self.pprint = self.data_model.pprint

    def get_data_model(self):
        if self.data_flavor == "reso":
            if self.reso_version == "1.4":
                if self.output_type == "edmx":
                    from data_models.reso import RESO1p4EDMX as DataModel

                    return DataModel
                else:
                    raise RESOUnsupportedException("Unknown RESO Output Type %s" % self.output_type)
            else:
                raise RESOUnsupportedException("Unknown RESO Version %s" % self.reso_version)
        elif self.data_flavor == "rets":
            if self.rets_version == "1.8":
                if self.output_type == "xml":
                    from data_models.rets import RETS1p8XML as DataModel

                    return DataModel
                else:
                    raise RESOUnsupportedException("Unknown RETS Output Type %s" % self.output_type)
            else:
                raise RESOUnsupportedException("Unknown RETS Version %s" % self.rets_version)

        raise RESOUnsupportedException("Unknown data flavor %s" % self.data_flavor)


class RESO(RESOBase):
    pass
