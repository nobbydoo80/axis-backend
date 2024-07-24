"""input.py: Django """


import logging

import re

__author__ = "Steven Klass"
__date__ = "06/16/17 10:29"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class InputModel(object):
    """This is used primarily for testing or overriding items"""

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
            log.info("Setting %s: %s", "_%s" % k, v)

    def round_value(self, value, ndigits, as_string=False, as_percent=False, as_dollar=False):
        if value is None:
            value = "-"
        if as_percent:
            _dval = "{:" + "{}".format(".{}".format(ndigits) if ndigits else "") + "%}"
            return _dval.format(value)
        elif ndigits == 0:
            value = int(round(value, 0))
        else:
            value = round(value, ndigits)
        if as_string:
            return "{}".format(value)
        if as_dollar:
            return "${:.2f}".format(value)
        return value

    def __getattr__(self, attr):
        """This allows us to do a number of things.
        First our standard rounding is in place
        Secondly if you pass "longitude" into the constructor that will override the default property
        """
        match = re.match(r"round(\d*)([s|p|d]?)__(.*)", attr)
        if match:
            ndigits = int(match.group(1)) if match.group(1) != "" else 0
            as_string = match.group(2) == "s"
            as_pct = match.group(2) == "p"
            as_dollar = match.group(2) == "d"
            attr = match.group(3)
            try:
                return self.round_value(getattr(self, attr), ndigits, as_string, as_pct, as_dollar)
            except TypeError:
                pass

        if hasattr(self, "_%s" % attr):
            return self.__getattribute__("_%s" % attr)

        return self.__getattribute__(attr)


class HomeStatusModel(InputModel):
    """This allows us to abstract out the fields needed by RESO"""

    def __init__(self, home_status, **kwargs):
        self.home_status = home_status
        self.home = self.home_status.home
        super(HomeStatusModel, self).__init__(**kwargs)

    @property
    def latitude(self):
        return self.home.latitude

    @property
    def longitude(self):
        return self.home.longitude

    @property
    def square_footage(self):
        return self.home_status.floo
