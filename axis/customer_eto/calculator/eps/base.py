"""base.py - Axis"""

__author__ = "Steven K"
__date__ = "8/10/21 17:10"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
import re

log = logging.getLogger(__name__)


class EPSInputException(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, "EPS Calculator Input Error:", *args, **kwargs)


class EPSBase(object):
    """Base class"""

    def __getattr__(self, attr):
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
                return getattr(self, attr)
        return self.__getattribute__(attr)

    def round_value(self, value, ndigits, as_string=False, as_percent=False, as_dollar=False):
        """A nice way to round a value"""
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

    def kwh_to_mbtu(self, value):
        """kWh to mBtu"""
        return (value * 3.412) / 1000.00

    def mbtu_to_kwh(self, value):
        """mBtu to kWh"""
        return (value * 1000.00) / 3.412

    def therms_to_mbtu(self, value):
        """therms to mBtu"""
        return value / 10.0

    def mbtu_to_therms(self, value):
        """mBtu to therms"""
        return value * 10.0
