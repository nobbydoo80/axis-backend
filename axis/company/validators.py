"""validators.py: Axis validators"""


import re

from django.core.exceptions import ValidationError

__author__ = "Steven Klass"
__date__ = "2011/06/22 09:56:26"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = ["Steven Klass"]


def validate_provider_id(value):
    """Validate a provider ID.  This is a number in the form XXXX-XXX."""
    provider = re.compile(r"^\d{4}-\d{3}$")

    if not provider.match(str(value)):
        msg = "{} is not a valid 7 digit Provider ID in the form XXXX-XXX.".format(value)
        raise ValidationError(msg)
