"""base.py - Axis"""

import logging
import re

log = logging.getLogger(__name__)

__author__ = "Steven K"
__date__ = "1/26/21 12:45"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]


class APSInputException(Exception):
    """APS Exception"""

    def __init__(self, *args, **kwargs):
        Exception.__init__(self, "APS Program Calculator Input Error:", *args, **kwargs)


class APSBase(object):
    """Base APS Objects"""

    def __getattr__(self, attr):
        """Allow you to pass round__<VARIABLE> and it will go ahead and do the right thing"""
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
        """Round a value"""
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
            _dval = "{:" + "{}".format(".{}".format(ndigits) if ndigits is not None else "") + "}"
            return _dval.format(value)
        if as_dollar:
            return "${:.2f}".format(value)
        return value

    def kwh_to_mbtu(self, value):
        """Convert kWh to mBtu"""
        return (value * 3.412) / 1000.00

    def therms_to_mbtu(self, value):
        """Convert therms to mBtu"""
        return value / 10.0
