"""city.py - axis"""

__author__ = "Steven K"
__date__ = "7/25/22 15:26"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import re
from collections import Counter

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db import models
from django.db.models import Q
from django.db.models.query import QuerySet
from django.urls import reverse
from localflavor.us.us_states import STATES_NORMALIZED

from axis.core.validators import represents_integer
from ..strings import (
    MISSING_CITY,
    UNKNOWN_CITY_IN_STATE,
    UNKNOWN_CITY,
    MULTIPLE_CITIES_FOUND,
    MULTIPLE_CITIES_FOUND_IN_STATE,
    FOUND_CITY,
)

import logging

log = logging.getLogger(__name__)


class CityManager(models.Manager):
    def get_queryset(self):
        return CityQuerySet(self.model, using=self._db)

    def get_by_natural_key(self, legal_statistical_area_description, place_fips):
        return self.get(
            legal_statistical_area_description=legal_statistical_area_description,
            place_fips=place_fips,
        )

    def filter_by_company(self, *args, **kwargs):
        return self.get_queryset().filter_by_company(*args, **kwargs)

    def filter_by_user(self, *args, **kwargs):
        return self.get_queryset().filter_by_user(*args, **kwargs)

    def find(self, *args, **kwargs):
        return self.get_queryset().find(*args, **kwargs)

    def choice_items_from_instances(self, *args, **kwargs):
        return self.get_queryset().choice_items_from_instances(*args, **kwargs)

    def get_or_create_unregistered_city(self, **kwargs):
        """This will create an unregistered city"""

        assert kwargs.get("name") is not None, "You must provide a city"

        defaults = kwargs.pop("defaults", dict())

        if not kwargs.get("place_fips", defaults.get("place_fips")):
            cid = self.filter(place_fips__startswith="990").order_by("-id").first()
            if cid:
                defaults["place_fips"] = int(cid.place_fips) + 1
            else:
                defaults["place_fips"] = 9900000

        if not kwargs.get("ansi_code", defaults.get("ansi_code")):
            defaults["ansi_code"] = kwargs.get("place_fips", defaults.get("place_fips"))

        if not kwargs.get(
            "legal_statistical_area_description", defaults.get("legal_statistical_area_description")
        ):
            desc = "Unregistered {} ({})".format(kwargs.get("name"), defaults["place_fips"])
            defaults["legal_statistical_area_description"] = desc

        if not kwargs.get("land_area_meters", defaults.get("land_area_meters")):
            defaults["land_area_meters"] = 0
        if not kwargs.get("water_area_meters", defaults.get("water_area_meters")):
            defaults["water_area_meters"] = 0
        if not kwargs.get("latitude", defaults.get("latitude")):
            defaults["latitude"] = 0
        if not kwargs.get("longitude", defaults.get("longitude")):
            defaults["longitude"] = 0

        kwargs["defaults"] = defaults

        from ..utils import get_usa_default

        if kwargs.get("name") and kwargs.get("county"):
            # We need to prevent duplicates - A city and county is pretty specific.
            obj, created = super(CityManager, self).get_or_create(
                name=kwargs.pop("name"),
                county=kwargs.pop("county"),
                country=kwargs.pop("country", get_usa_default()),
                defaults=kwargs.pop("defaults"),
            )
            self.model.objects.filter(id=obj.id).update(**kwargs)
            return self.model.objects.get(id=obj.id), created

        return super(CityManager, self).get_or_create(**kwargs)

    def get_or_create_by_string(
        self,
        name,
        county=None,
        state=None,
        country="US",
        confirmed=False,
        zipcode=None,
    ):
        if isinstance(name, self.model):
            return name, False
        if name is None:
            return None, False
        name = name.strip()

        if state:
            state = STATES_NORMALIZED[state.lower()]

        from ..utils import resolve_country

        country = resolve_country(country)

        city = self.filter(name__iexact=name, country=country)
        if county:
            from ..models import County

            county = County.objects.get_by_string(name=county, state=state)
            city = city.filter(county=county)
        elif state:
            city = city.filter(county__state=state)
        try:
            city = city.get()
            return city, False
        except MultipleObjectsReturned:
            counties = city.values_list("county_id", flat=True)
            if len(set(counties)) != len(counties):
                from ..models import County

                duplicates = [item for item, count in Counter(counties).items() if count > 1]
                counties = ["{}".format(x) for x in County.objects.filter(id__in=duplicates)]
                msg = (
                    "Duplicate city / county combination for %(city)r, "
                    "%(state)r in counties %(counties)r "
                )
                try:
                    log.error(msg, dict(city=name, state=state, counties=", ".join(counties)))
                except TypeError:
                    log.error(msg % dict(city=name, state=state, counties=", ".join(counties)))
            else:
                if confirmed:
                    log.error(
                        "Confirmed -- Multiple Cities found for %(name)r, %(county)r, " "%(state)r",
                        {"name": name, "county": county, "state": state},
                    )

            return city.first(), False
        except (ObjectDoesNotExist, Exception):
            if county is None:
                from ..models import County

                county = County.objects.filter(state=state).first()
                log.warning("No County found for new city %s %s using %s" % (name, state, county))
            lookups = {
                "city": name,
                "county": county,
                "state": state,
                "zipcode": zipcode,
            }
            log.debug(f"Creating city {name}, {county}, {state} → {lookups}")
            city, created = self.get_or_create_unregistered_city(name=name, county=county)
            lookups["city"] = city
            city, _created = self.get_or_create_from_geocode_lookups(**lookups)
            return city, created

    def get_or_create_from_geocode_lookups(self, **lookups):
        from axis.geocoder.models import Geocode
        from axis.geographic.models import County

        matches = Geocode.objects.get_matches(only_confirmed=False, **lookups)
        if matches.count() == 0:
            msg = (
                "Can't successfully geocode a city. No candidate matches"
                " from geocoder. Lookups: %r"
            )
            log.error(msg, lookups)
            if not lookups.get("county"):
                log.warning("No county was identified for %r - using first" % (lookups,))
                lookups["county"] = County.objects.filter(state=lookups.get("state"))[0]
            match_norm = lookups
        else:
            _match_norms = [
                match.get_normalized_fields(return_city_as_string=True) for match in matches
            ]
            match_norms = [x for x in _match_norms if x.get("county")]
            match_norms = match_norms if match_norms else _match_norms

            match_norm = match_norms[0]

            if len(match_norms) > 1:
                log.warning("Found more than one geocoding match for city. Lookups: %r", lookups)
            if not match_norm.get("county"):
                match_norm["county"] = County.objects.filter(state=match_norm.get("state"))[0]
                log.warning(
                    "No county was identified from geocoder - using first %r", match_norm["county"]
                )

        match_norm["name"] = match_norm.pop("city", lookups.get("city"))
        if not isinstance(match_norm["name"], str) and hasattr(match_norm["name"], "name"):
            match_norm["name"] = match_norm["name"].name

        for field in list(match_norm.keys()):
            if field not in [x.name for x in self.model._meta.fields]:
                match_norm.pop(field)

        # Build name and county from geocoded information
        city, created = self.get_or_create_unregistered_city(**match_norm)

        log.info(f"Created new city {city}")

        return city, created

    def verify(
        self, name=None, county=None, state=None, info_only=False, ignore_missing=False, log=None
    ):
        log = log if log else logging.getLogger(__name__)

        city = None

        from ..models import County

        assert isinstance(county, (type(None), County)), "County must be County Type if specified"

        if isinstance(name, str):
            name = name.strip()

        if name is None:
            if ignore_missing:
                log.info(MISSING_CITY)
                return None
            log.error(MISSING_CITY)
            return None
        elif represents_integer(name):
            city = self.get(id=int(name))
        else:
            county_name = county.name if county else None
            try:
                city, create = self.get_or_create_by_string(
                    name=name, county=county_name, state=state
                )
            except (TypeError, ValueError, ObjectDoesNotExist):
                err = UNKNOWN_CITY.format(city=name)
                if state:
                    err = UNKNOWN_CITY_IN_STATE.format(city=name, state=state)
                if info_only:
                    log.info(err)
                else:
                    log.error(err)
            except MultipleObjectsReturned:
                err = MULTIPLE_CITIES_FOUND.format(city=name)
                if state:
                    err += MULTIPLE_CITIES_FOUND_IN_STATE.format(city=name, state=state)
                if info_only:
                    log.info(err)
                else:
                    log.error(err)
        if city:
            _url = reverse("city:view", kwargs={"pk": city.id})
            log.debug(FOUND_CITY.format(url=_url, city=city))
        return city


class CityQuerySet(QuerySet):
    # Geocoding may return certain abbreviated versions of names that we prefer to have expanded.
    # The find() method on this manager will use this map of known translations to proxy the queried
    # city name.
    NAME_TRANSLATIONS = {
        # "Our city's version" -> "geocoder version"
        "Mount": "Mt",
    }
    NAME_TRANSLATIONS = {k: re.compile(r"\b{}\b".format(v)) for k, v in NAME_TRANSLATIONS.items()}

    def filter_by_company(self, company, **kwargs):
        """A way to trim down the list of objects by company"""
        counties = company.counties.all()
        countries = company.countries.exclude(abbr="US")
        return self.filter(Q(county__in=counties) | Q(country__in=countries), **kwargs)

    def filter_by_user(self, user, **kwargs):
        """A way to trim down the list of objects by user"""
        kwargs.pop("include_self", None)
        if user.is_superuser:
            return self.filter(**kwargs)
        try:
            kwargs["company"] = user.company
        except AttributeError:
            return self.none()
        return self.filter_by_company(**kwargs)

    # def find(self, name, **kwargs):
    #     """Like ``get()``, but adds fuzzy matches for hard geocoding mismatches."""
    #     for expanded, pattern in self.NAME_TRANSLATIONS.items():
    #         name = pattern.replace(expanded, name)
    #     return self.get(name=name, **kwargs)

    def choice_items_from_instances(self, user=None, *args, **kwargs):
        #        """This is simply a more effient way to get lots of labels"""
        """An efficient way to get labels for use in select widget.  This will
        return a list of tuples [(id, label), (id, label)]

        :param user: django.contrib.auth.models.User
        :param args: list
        :param kwargs: dict
        :return: list
        """
        cities = self.filter(*args, **kwargs)
        if user:
            cities = self.filter_by_user(user).filter(*args, **kwargs)

        results = []
        for _id, name, state, country in cities.values_list(
            "id", "name", "county__state", "country__abbr"
        ):
            value = f"{name} {state}"
            if country != "US":
                value = f"{name} {country}"
            results.append((_id, value))
        return sorted(list(set(results)), key=lambda item: (item[1]))
