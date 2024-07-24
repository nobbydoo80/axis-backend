"""validators.py: core validators"""


import logging

from django.core.exceptions import ValidationError
import re

__author__ = "Steven Klass"
__date__ = "2011/06/22 09:56:26"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = ["Steven Klass"]

log = logging.getLogger(__name__)

represents_integer_regex = re.compile(r"[-+]?\d+(\.0*)?$")


def represents_integer(s):
    try:
        return represents_integer_regex.match("{}".format(s)) is not None
    except TypeError:
        log.exception("We were passed %(obj)r and failed", {"obj": s})
        return False


def validate_rater_id(value):
    # Matches any 4-digit number:
    rater = re.compile(r"^\d{4,7}$")

    # If year does not match our regex:
    if not rater.match(str(value)):
        raise ValidationError(
            "%s should be between 4 and 7 digits Rater ID in the form of XXXXXXX." % value
        )
