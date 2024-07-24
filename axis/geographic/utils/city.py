"""city.py - axis"""

__author__ = "Steven K"
__date__ = "7/8/22 13:01"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from django.db.models import Count

from axis.geographic.models import County, City, Country, USState

log = logging.getLogger(__name__)


def resolve_city(
    name: str | int | City | None,
    county: County | str | None = None,
    state_abbreviation: USState | str = None,
    country: Country | str = None,
) -> City:
    """Find or create a city in axis using our serializers.
    This is a convenience function for use in single or bulk uploads.
    """
    if isinstance(name, City):
        return name
    elif isinstance(name, int):
        return City.objects.get(id=name)

    from axis.geocoder.api_v3.serializers import GeocodeCityMatchesSerializer

    data = {
        "name": name,
        "county": county,
        "state": state_abbreviation,
        "country": country,
    }
    data.update(GeocodeCityMatchesSerializer().parse_one_liner(**data))

    # Look to see if it exists.
    query = GeocodeCityMatchesSerializer().get_existing_city_query(**data)

    try:
        return City.objects.get(query)
    except City.MultipleObjectsReturned:
        return City.objects.filter(query).annotate(n=Count("home")).order_by("-n").first()
    except City.DoesNotExist:
        pass

    from axis.geographic.api_v3.serializers import BaseCitySerializer
    from axis.geocoder.api_v3.serializers import GeocodeCityMatchesSerializer, GeocodeCitySerializer

    data = {
        "name": data["name"],
        "county": data["county"].pk if data["county"] else None,
        "state": data["state"].pk if data["state"] else None,
        "country": data["country"].abbr if data["country"] else None,
    }

    serializer = GeocodeCityMatchesSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    obj, create = serializer.save()

    # Now we request for responses
    serializer = GeocodeCitySerializer(instance=obj)
    try:
        data = serializer.data["valid_responses"][0]
        data["geocode_response"] = data.pop("id")
    except IndexError:
        # Use what we have...
        pass

    # Now create the actual item
    serializer = BaseCitySerializer(data=data)
    serializer.is_valid(raise_exception=True)
    return serializer.save()
