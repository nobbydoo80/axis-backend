"""country.py - axis"""

__author__ = "Steven K"
__date__ = "7/15/22 11:35"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
from django.apps import apps

log = logging.getLogger(__name__)


def get_usa_default():
    """Default is the USA!"""
    Country = apps.get_model("geographic", "Country")
    return Country.objects.get_or_create(abbr="US", name="United States")[0]


def resolve_country(name: str | None):
    """This will get (and create) a country"""
    from axis.geographic.models import COUNTRIES, EXTENDED_COUNTRY_NAMES

    Country = apps.get_model("geographic", "Country")

    if name is None:
        return get_usa_default()
    if isinstance(name, Country):
        return name
    if name.upper() in COUNTRIES:
        return Country.objects.get_or_create(abbr=name.upper(), name=COUNTRIES[name.upper()])[0]
    else:
        reverse_countries = {v.lower(): k for k, v in COUNTRIES.items()}
        reverse_countries.update(EXTENDED_COUNTRY_NAMES)
        if name.lower() in reverse_countries:
            abbr = reverse_countries[name.lower()]
            return Country.objects.get_or_create(abbr=abbr, name=COUNTRIES[abbr])[0]
    raise KeyError(f"Country {name!r} not found!")
