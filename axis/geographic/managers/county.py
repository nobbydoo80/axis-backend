"""county.py - axis"""

__author__ = "Steven K"
__date__ = "7/25/22 15:38"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]
import logging
import os
import re

from django.core import management
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db import models
from django.db.models import Q
from django.db.models.query import QuerySet
from ..strings import (
    UNKNOWN_COUNTY,
    UNKNOWN_COUNTY_IN_STATE,
    MULTIPLE_COUNTIES_FOUND,
    MULTIPLE_COUNTIES_FOUND_IN_STATE,
    FOUND_COUNTY,
    MISSING_COUNTY,
)

log = logging.getLogger(__name__)


class CountyManager(models.Manager):
    def get_queryset(self):
        return CountyQuerySet(self.model, using=self._db)

    def get_by_natural_key(self, legal_statistical_area_description, county_fips):
        return self.get(
            legal_statistical_area_description=legal_statistical_area_description,
            county_fips=county_fips,
        )

    def filter_by_company(self, company, **kwargs):
        return self.get_queryset().filter_by_company(company, **kwargs)

    def filter_by_user(self, user, **kwargs):
        return self.get_queryset().filter_by_user(user, **kwargs)

    def get_by_string(self, name, state=None, create=True):
        return self.get_queryset().get_by_string(name=name, state=state, create=create)

    def verify(self, name=None, state=None, ignore_missing=False, log=None):
        return self.get_queryset().verify(
            name=name, state=state, ignore_missing=ignore_missing, log=log
        )


class CountyQuerySet(QuerySet):
    def filter_by_company(self, company, **kwargs):
        """A way to trim down the list of objects by company"""
        kwargs.pop("include_self", None)
        if company is None:
            return self.none()
        return self.filter(id__in=company.counties.values_list("id"), **kwargs)

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

    def get_by_string(self, name, state=None, log=None, create=True):
        log = log if log else logging.getLogger(__name__)
        if name in ["", None]:
            return None
        if isinstance(name, self.model):
            return name

        initial_name = cleaned_name = name

        # Our DB stores as "St." Geocoders don't like th./ma    at period.
        if name.lower().startswith("st ") or name.lower().startswith("ste "):
            cleaned_name = re.sub(r"^[s|S]t\s", "St. ", cleaned_name)
            cleaned_name = re.sub(r"^[s|S]te\s", "Ste. ", cleaned_name)
            initial_name = cleaned_name
        # We strip out Parish and County.  Hindsight not a smart idea.
        if name.lower().endswith(" county") or name.lower().endswith(" parish"):
            cleaned_name = re.sub(r"\s[c|C]ounty$", "", cleaned_name)
            cleaned_name = re.sub(r"\s[p|P]arish$", "", cleaned_name)
        if state and state.lower() == "dc":
            cleaned_name = initial_name = "District of Columbia"
        if state and state.lower() == "in" and "laporte" in name.lower():
            cleaned_name = "La Porte"
        if name.startswith("City of "):
            # City of fairfax county bug..
            cleaned_name = name.replace("City of ", "")

        query = Q(name__iexact=cleaned_name) | Q(
            legal_statistical_area_description__iexact=initial_name
        )
        if state:
            query = query & Q(state=state)

        try:
            county = self.get(query)
        except ObjectDoesNotExist:
            if create:
                args = [
                    "update_base_geographic_data",
                    "--exclude_cities",
                    "--county",
                    cleaned_name,
                ]
                if state:
                    args += ["--state", state]
                with open(os.devnull, "w") as stdout:
                    management.call_command(
                        *args,
                        stdout=stdout,
                    )
                return self.get(query)
            if cleaned_name == initial_name:
                log.error("Unable to find county %r %r", initial_name, state)
            else:
                log.error(
                    "Unable to find County %r %r OR %r %r",
                    initial_name,
                    state,
                    cleaned_name,
                    state,
                )
            return None
        except MultipleObjectsReturned:
            # Fucking Fairfax county VA. or St. Louis MO.
            # Really. like they could come up with a more origianl name.
            query = Q(name__iexact=initial_name) | Q(
                legal_statistical_area_description__iexact=initial_name
            )
            if state:
                query = query & Q(state=state)
            county = self.get(query)
        return county

    def verify(self, name=None, state=None, ignore_missing=False, log=None):
        log = log if log else logging.getLogger(__name__)
        objects, county = [], None
        if name is None:
            if ignore_missing:
                return None
            log.info(MISSING_COUNTY)
            return None
        else:
            objects = self.filter(name__iexact=name)
            if state:
                objects = objects.filter(state__iexact=state)
            if not objects.count():
                err = UNKNOWN_COUNTY.format(county=name)
                if state:
                    err = UNKNOWN_COUNTY_IN_STATE.format(county=name, state=state)
                log.error(err)
            elif objects.count() > 1:
                err = MULTIPLE_COUNTIES_FOUND.format(county=name)
                if state:
                    err = MULTIPLE_COUNTIES_FOUND_IN_STATE.format(county=name, state=state)
                log.error(err)
            else:
                county = objects[0]
        if county:
            log.info(FOUND_COUNTY.format(county=objects[0]))
        return county
