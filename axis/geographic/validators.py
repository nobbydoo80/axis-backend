"""validators.py: Django geographic"""


import logging
from django.core.exceptions import ValidationError
import re

__author__ = "Steven Klass"
__date__ = "3/2/12 3:02 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


def validate_zipcode(value):
    # Matches any 5-digit number:
    year_re = re.compile(r"^\d{5}$")

    # If year does not match our regex:
    if not year_re.match(str(value)):
        raise ValidationError("%s is not a valid zip." % value)
