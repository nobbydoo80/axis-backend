"""county.py - axis"""

__author__ = "Steven K"
__date__ = "7/28/22 11:12"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
import re

from django.db.models import Q

from .state import resolve_state
from ..models import County, USState
from ..tests.factories import real_county_factory

log = logging.getLogger(__name__)


def resolve_county(
    name: str | int | County,
    state_abbreviation: USState | str | None = None,
) -> County | None:
    if isinstance(name, County):
        return name

    if isinstance(name, int):
        return County.objects.get(id=name)

    if name is None:
        raise County.DoesNotExist("You need to provide a name to resolve")

    state_abbreviation = resolve_state(state_abbreviation)

    # Perform a quick query this will work for > 90% of counties
    query = Q(name__iexact=name)
    query |= Q(legal_statistical_area_description__iexact=name)

    if state_abbreviation:
        query = query & Q(state=state_abbreviation.abbr)

    counties = County.objects.filter(query)
    if counties.exists():
        return counties.first()

    # Now a complete cleaning of this data.

    query = Q(name__iexact=name)
    query |= Q(legal_statistical_area_description__iexact=name)

    cleaned_name = name
    cleaned_name = re.sub(r"^St\s", "St. ", cleaned_name, flags=re.I)
    cleaned_name = re.sub(r"^Ste\s", "Ste. ", cleaned_name, flags=re.I)
    if cleaned_name != name:
        query |= Q(legal_statistical_area_description__iexact=cleaned_name)

    match = re.search(
        r"(.*)(County|Parish|City|Borough|Municipality|Municipio|Census Area)",
        cleaned_name,
        flags=re.I,
    )
    if match:
        cleaned_name = match.group(1).strip()

    if state_abbreviation and state_abbreviation.abbr == "DC":
        cleaned_name = name = "District of Columbia"
    if name.startswith("City of Fairfax"):
        # City of fairfax county bug..
        name = "Fairfax"
    if state_abbreviation.abbr == "IN" and "laporte" in name.lower():
        cleaned_name = "La Porte"

    query = Q(name__iexact=name)
    query |= Q(legal_statistical_area_description__iexact=name)

    if cleaned_name != name:
        query |= Q(name__iexact=cleaned_name)
        query |= Q(legal_statistical_area_description__iexact=cleaned_name)

    if state_abbreviation:
        query = query & Q(state=state_abbreviation.abbr)

    try:
        return County.objects.get(query)
    except County.MultipleObjectsReturned:
        # Fairfax VA, St Louis MO
        if state_abbreviation and state_abbreviation.abbr in ["VA", "MO"]:
            return County.objects.filter(query).first()
        raise
    except County.DoesNotExist:
        pass

    real_county_factory(
        name=name,
        state=state_abbreviation.abbr if state_abbreviation else None,
        include_cities=False,
    )

    if name in ["Fairfax", "St. Louis"]:
        return County.objects.filter(query).first()
    return County.objects.get(query)
