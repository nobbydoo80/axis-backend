import logging

from django.utils.timezone import now
from django.core.exceptions import ValidationError

__author__ = "Autumn Valenta"
__date__ = "9/20/17 4:38 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


def reasonable_date(value):
    """A date with a year between 1900 and 2050"""
    return reasonable_year(value.year)


def reasonable_year(value):
    """A year between 1900 and 2050"""
    min_reasonable_year = 1900
    max_reasonable_year = 2050
    if value > max_reasonable_year:
        raise ValidationError("Year should not be later than %d" % (max_reasonable_year,))
    if value < min_reasonable_year:
        raise ValidationError("Year should not be earlier than %d" % (min_reasonable_year,))


def currency(value):
    rich_decimal(value, positive_only=True)

    try:
        value = float(value.replace(",", ""))
    except:
        raise ValidationError("Invalid decimal value")
    decimal_places(value, n=2)


def rich_decimal(value, positive_only=False):
    try:
        value = float(value.replace(",", ""))
    except:
        raise ValidationError("Invalid decimal value")

    if positive_only:
        positive_value(value)


def percent(value):
    positive_value(value)

    if value > 100:
        raise ValidationError("Cannot be more than 100")


def positive_value(value):
    if value < 0:
        raise ValidationError("Value must be a positive number")


def decimal_places(value=None, n=None):
    assert n is not None, "Provide a precision value"

    def validate(value):
        _, remainder = str(value).split(".", 1)
        if len(remainder) > n:
            raise ValidationError("Must use only {} decimal places or fewer".format(n))

    if value is None:
        return validate
    return validate(value)
