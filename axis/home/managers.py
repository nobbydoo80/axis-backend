"""managers.py: Django home"""

__author__ = "Steven Klass"
__date__ = "3/5/12 1:35 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

import datetime
import logging
import typing
from collections import defaultdict, namedtuple

from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db import models, IntegrityError
from django.db.models import F, Value, CharField, Exists
from django.db.models import IntegerField
from django.db.models import OuterRef, Subquery
from django.db.models import Q, Sum, Case, When
from django.db.models.functions import Cast
from django.db.models.functions import Coalesce
from django.db.models.query import QuerySet
from django.urls import reverse, NoReverseMatch
from django.utils import timezone
from django.utils.timezone import now
from simple_history.models import HistoricalRecords

from axis.company.models import Company
from axis.geocoder.models import Geocode, GeocodeResponse
from axis.geographic.models import City, Country, County
from axis.relationship.models import Relationship
from axis.relationship.utils import create_or_update_spanning_relationships
from axis.scheduling.models import ConstructionStage, ConstructionStatus
from axis.subdivision.models import Subdivision
from . import strings
from .utils import validate_compatible_program
from ..geographic.utils.country import resolve_country

customer_hirl_app = apps.get_app_config("customer_hirl")

log = logging.getLogger(__name__)
User = get_user_model()


class HomeDocumentManager(models.Manager):
    def filter_by_company_and_home(self, home, company):
        docs = self.filter(home=home, is_public=True)
        return docs.exclude(company__company_type=company.company_type)


class HomeManager(models.Manager):
    """A generic manager with metros"""

    def filter_by_multiple_companies(self, companies, **kwargs):
        """Get a queryset of homes for multiple companies"""
        assert isinstance(companies, (QuerySet, list))
        results = self.none()
        for comp in companies:
            results = results | self.filter_by_company(comp, **kwargs)

        return results

    def filter_by_company(self, company, **kwargs):
        """A way to trim down the list of objects by company"""
        show_attached = kwargs.pop("show_attached", False)
        relationship_homes = company.relationships.get_homes(show_attached=show_attached).filter(
            **kwargs
        )
        home_ids = list(relationship_homes.values_list("id", flat=True))

        from .models import EEPProgramHomeStatus

        Associations = EEPProgramHomeStatus.associations.rel.related_model
        associations = Associations.objects.filter(company=company, is_active=True, is_hidden=False)
        home_ids.extend(associations.values_list("eepprogramhomestatus__home_id", flat=True))

        return self.filter(id__in=home_ids)

    def filter_by_user(self, user, **kwargs):
        """A way to trim down the list of objects by user"""
        show_attached = kwargs.pop("show_attached", False)
        if user.is_superuser:
            return self.filter(**kwargs)
        if user.company is None:
            return self.none()
        kwargs["company"] = user.company
        kwargs["show_attached"] = show_attached
        return self.filter_by_company(**kwargs)

    def filter_by_eep_program(self, eep_program):
        """Get homes for a company"""
        return self.filter(homestatuses__eep_program=eep_program)
        # from axis.home.models import EEPProgramHomeStatus
        # homes = EEPProgramHomeStatus.objects.filter(eep_program=eep_program)
        # homes = [x.home.id for x in homes]
        # return self.filter(id__in=homes)

    def filter_by_floorplan(self, floorplan):
        """Get homes for a company"""
        return self.filter(homestatuses__floorplan=floorplan)
        # from axis.home.models import EEPProgramHomeStatus
        # floorplans = EEPProgramHomeStatus.objects.filter(floorplan=floorplan)
        # floorplans = [x.floorplan.id for x in floorplans]
        # return self.filter(id__in=floorplans)

    def filter_confirmed_by_eep_program_unpaid(self, eep_program=None, eep_programs=None):
        """Get me a list of homes by Program which have been confirmed"""

        from axis.home.models import EEPProgramHomeStatus

        kwargs = dict(confirm_date__isnull=False)
        if eep_program:
            kwargs["eep_program"] = eep_program
        elif eep_programs:
            kwargs["eep_program__in"] = eep_programs

        home_ids = EEPProgramHomeStatus.objects.filter(**kwargs).values_list("home_id")

        kwargs = dict(ippitem__isnull=True, id__in=home_ids)
        log.debug("Filter Kwargs: %s", kwargs)
        return self.filter(**kwargs)

    def filter_by_builder(self, builder):
        """Get homes by builder"""
        return builder.relationships.get_homes()

    def get_aps_ms_for_user_qs(self, user, **kwargs):
        """Return a list of eep_programs ids for a given queryset"""
        _sqs = self.filter_by_user(user=user, **kwargs)
        _sqsv = list(set(_sqs.values_list("id", "apshome", "apshome__meterset_date")))
        obj = namedtuple("APSMS_by_Home", ["id", "date", "url"])
        results = []
        href = '<a href="{}">{}</a>'
        for home_id, apshome_id, ms_date in _sqsv:
            url = None
            if apshome_id is not None:
                _url = reverse("aps_homes_detail_view", kwargs={"pk": apshome_id})
                url = href.format(_url, ms_date.strftime("%m/%d/%Y"))
            results.append(obj(home_id, ms_date, url))
        return results

    def get_homes_for_scheduling(self, company, id_list):
        return self.filter_by_company(company=company).exclude(id__in=id_list)

    def verify_and_create_for_user(
        self,
        user: User,
        create: bool = True,
        lot_number: str | None = None,
        street_line1: str | None = None,
        street_line2: str | None = None,
        zipcode: str | None = None,
        state: str | None = None,
        city: City | None = None,
        county: County | None = None,
        country: Country | None = None,
        subdivision: Subdivision | None = None,
        builder: Company | None = None,
        bulk_uploaded: bool = False,
        alt_name: str | None = None,
        is_multi_family: bool | str = False,
        geocode_address: bool = True,
        show_warning_messages: bool = True,
        log: logging.Logger | None = None,
    ):
        """Verify all the things surrounding a home and optionally create it"""

        log = log if log is not None else logging.getLogger(__name__)
        history_start = now()

        if isinstance(lot_number, str):
            lot_number = lot_number.strip()
            if len(str(lot_number)) > 16:
                log.error(strings.INVALID_LOT_NUMBER.format(lot_number=lot_number))
                return None, False
            if not len(lot_number):
                lot_number = None

        if street_line1 is None:
            log.error(strings.MISSING_STREET_LINE1)
            return None, False
        if isinstance(street_line1, str):
            street_line1 = street_line1.strip()

        if geocode_address and zipcode is None:
            log.error(strings.MISSING_ZIP_CODE)
            return None, False

        if isinstance(zipcode, str):
            zipcode = zipcode.strip()

        if isinstance(street_line2, str):
            street_line2 = street_line2.strip()
        if street_line2 in ["", None]:
            street_line2 = None

        if isinstance(is_multi_family, str):
            if is_multi_family.lower() in ["yes", "x"]:
                is_multi_family = True
            else:
                is_multi_family = False
        is_multi_family = is_multi_family if is_multi_family is not None else False

        company = user.company

        if city:
            if state is None and city.state:
                state = city.state
            if county is None and city.county:
                county = city.county
            if country is None and city.country:
                country = city.country
        else:
            try:
                city = subdivision.city
                if state is None and city.state:
                    state = city.state
                if county is None and city.county:
                    county = city.county
                if country is None and city.country:
                    country = city.country
            except AttributeError:
                log.error(strings.MISSING_CITY)
                return None, False

        if county is None and country in [None, resolve_country("US")]:
            try:
                county = subdivision.county
            except AttributeError:
                log.error(strings.MISSING_COUNTY)
                return None, False

        if state is None and country in [None, resolve_country("US")]:
            try:
                state = subdivision.state
            except AttributeError:
                log.error(strings.MISSING_STATE)
                return None, False

        if city and subdivision:
            if "{}".format(city) != "{}".format(subdivision.city) and show_warning_messages:
                log.warning(
                    strings.CITY_SUBDIVISON_MISMATCH.format(
                        city=city, subdivision_city=subdivision.city
                    )
                )

        if county and subdivision:
            if county != subdivision.county and show_warning_messages:
                log.warning(
                    strings.COUNTY_SUBDIVISON_MISMATCH.format(
                        county=county, subdivision_county=subdivision.county
                    )
                )

        if state and subdivision:
            if state != subdivision.state and show_warning_messages:
                log.warning(
                    strings.STATE_SUBDIVISON_MISMATCH.format(
                        state=state, subdivision_state=subdivision.state
                    )
                )

        if subdivision and subdivision.is_multi_family and not is_multi_family:
            _url = subdivision.get_absolute_url()
            log.error(strings.HOME_MULTIFAMLY_MISMATCH.format(subdivision=subdivision, url=_url))

        object_defaults = dict(
            confirmed_address=False,
            is_custom_home=False,
            bulk_uploaded=bulk_uploaded,
        )
        if alt_name:
            object_defaults["alt_name"] = alt_name

        # Perform geocoding to get updated values where possible.
        # These will be used to create the home.

        lookup = dict(street_line1=street_line1, city=city, state=state, zipcode=zipcode)

        if not is_multi_family and street_line2:
            lookup["street_line2"] = street_line2
        if country:
            lookup["country"] = country.abbr

        # Now if we look this address up and we find a match what should we be doing?
        # Example we upload an address was previously unconfirmed..
        # Then we re-upload and it's confirmed we will get two homes..
        objects = self.filter_similar(
            street_line1=street_line1,
            street_line2=street_line2,
            city=city,
            country=country,
            state=state,
            zipcode=zipcode,
            lot_number=lot_number,
        )

        home = None

        if objects.count() > 1:
            log.error(strings.MULTIPLE_HOMES_FOUND)
        elif objects.count() == 1:
            home = objects.get()

        if geocode_address:
            if home is None or (home.confirmed_address is False and home.address_override is False):
                geolocation_matches = Geocode.objects.get_matches(**lookup)

                if len(geolocation_matches) == 1:
                    match = geolocation_matches.get()

                    geocoded_data = match.get_normalized_fields()
                    street_line1 = geocoded_data.get("street_line1", street_line1)
                    street_line2 = (
                        geocoded_data.get("street_line2", street_line2) if street_line2 else None
                    )
                    zipcode = geocoded_data.get("zipcode", zipcode)
                    object_defaults.update(
                        {
                            k: geocoded_data[k]
                            for k in ["confirmed_address", "latitude", "longitude"]
                        }
                    )
                    object_defaults.update(
                        {
                            "geocode_response": match,
                            "confirmed_address": True,
                            "address_override": False,
                        }
                    )
                    if (
                        geocoded_data.get("county")
                        and geocoded_data["county"] != county
                        and show_warning_messages
                    ):
                        log.warning(
                            "Override county provided '%s' to '%s' based on " "geocoder",
                            county,
                            geocoded_data["county"],
                        )
                        county = geocoded_data["county"]
                    if (
                        geocoded_data.get("city")
                        and geocoded_data["city"].name != city.name
                        and show_warning_messages
                    ):
                        log.warning(
                            "Override city provided '%s' to '%s' based on " "geocoder",
                            city,
                            geocoded_data["city"],
                        )
                        city = geocoded_data["city"]
                else:
                    # Can't make a positive match on a single geocoded result
                    object_defaults["confirmed_address"] = False
                    if geolocation_matches and (show_warning_messages or settings.DEBUG):
                        addr = "{street_line1} {city}, {state} {zipcode}".format(**lookup)
                        log.info(
                            "%s - Address provided was not confirmed - %s matches - %s",
                            "Home.verify_and_create_for_user",
                            len(geolocation_matches),
                            addr,
                        )

        if subdivision is None and builder is None:
            log.error(strings.MISSING_SUBDIVISION_OR_BUILDER)
            return None, False

        # Build new dictionary of data.  These values are final and will be sent to the Home
        # constructor.

        object_dict = dict(
            lot_number=lot_number,
            street_line1=street_line1,
            zipcode=zipcode,
            street_line2=street_line2,
            city=city,
            county=county,
            state=state,
        )

        # Try to locate existing objects based on the address information.  Multi-Family is not
        # considered as part of the street_address uniqueness.  It's solely used for geocoding.
        if home is None:
            objects = self.filter_similar(
                street_line1=street_line1,
                street_line2=street_line2,
                city=city,
                state=state,
                zipcode=zipcode,
                lot_number=lot_number,
                geocode_response=object_defaults.get("geocode_response"),
            )

        created = create
        if objects.count() == 1:
            home = objects[0]
            created = False
            try:
                _url = reverse("home:view", kwargs={"pk": home.id})
                log.debug(strings.EXISTING_HOME.format(home=home, url=_url))
            except NoReverseMatch:
                log.debug(strings.EXISTING_HOME_ID.format(home_id=home.id))
            try:
                alt_cities_names = [city.name, home.place.geocode_response.geocode.raw_city.name]
            except AttributeError:
                alt_cities_names = [home.city.name]

            if not builder and home.is_custom_home:
                log.error("Existing address used is a custom home but builder was not specified")
                return None, False
            elif city.name not in alt_cities_names:
                log.error(
                    strings.EXISTING_HOME_CITY_ERROR.format(
                        home=home, url=_url, city=home.city.name, file_city=city.name
                    )
                )
            if create and object_defaults.get("confirmed_address"):
                log.info("Updating existing home with a confirmed address")
                for k, v in object_dict.items():
                    if getattr(home, k) != v:
                        setattr(home, k, v)
                for k, v in object_defaults.items():
                    if getattr(home, k) != v:
                        setattr(home, k, v)
                home.save()
                if home.history.all()[0].history_user is None:
                    home.history.filter(
                        history_date__gte=history_start, history_user__isnull=True
                    ).update(history_user=user)

        elif objects.count() > 1:
            log.error(strings.MULTIPLE_HOMES_FOUND)
            created = False
        elif create:
            object_dict["subdivision"] = None
            if county:
                object_defaults["metro"] = county.metro
                object_defaults["climate_zone"] = county.climate_zone
            object_dict["is_multi_family"] = is_multi_family
            sub_url = ""
            if subdivision:
                object_dict["subdivision"] = subdivision
                _url = reverse("subdivision:view", kwargs={"pk": subdivision.id})
                sub_url = '<a href="{}">{}</a>'.format(_url, subdivision)
            else:
                object_dict["is_custom_home"] = True
            home, created = self.get_or_create(defaults=object_defaults, **object_dict)

            _url = reverse("home:view", kwargs={"pk": home.id})

            if created and home.history.all()[0].history_user is None:
                hist = home.history.all()[0]
                hist.history_user = user
                hist.save()

            const_stage = ConstructionStage.objects.filter_by_company(company=company).first()
            if const_stage:
                cstats = ConstructionStatus.objects.filter(
                    stage=const_stage, home=home, company=company
                )
                if not cstats.count():
                    ConstructionStatus.objects.create(
                        stage=const_stage, home=home, company=company, start_date=now()
                    )

            Relationship.objects.validate_or_create_relations_to_entity(
                entity=home, direct_relation=company, implied_relations=builder, log=log
            )
            create_or_update_spanning_relationships(company, home)
            home._generate_utility_type_hints(None, None, discover=True)

            log.info(
                strings.HOME_USED_CREATE.format(
                    create="Created" if created else "Used existing",
                    custom="custom " if home.is_custom_home else "",
                    multifamily="multi-family " if home.is_multi_family else "",
                    url=_url,
                    home=home,
                    subdivision="in {} ".format(sub_url) if subdivision else "",
                    confirmed=" confirmed"
                    if object_defaults.get("confirmed_address")
                    else "n unconfirmed",
                )
            )

        if home and not home.place:
            home.create_place()
            home.save()

        return home, created

    def verify_for_user(
        self,
        user: User,
        lot_number: str | None = None,
        street_line1: str | None = None,
        street_line2: str | None = None,
        zipcode: str | None = None,
        state: str | None = None,
        city: City | None = None,
        county: County | None = None,
        country: Country | None = None,
        subdivision: Subdivision | None = None,
        builder: Company | None = None,
        bulk_uploaded: bool = False,
        alt_name: str | None = None,
        is_multi_family: bool | str = False,
        geocode_address: bool = True,
        show_warning_messages: bool = True,
        log: logging.Logger | None = None,
    ):
        return self.verify_and_create_for_user(
            create=False,
            user=user,
            lot_number=lot_number,
            street_line1=street_line1,
            street_line2=street_line2,
            zipcode=zipcode,
            state=state,
            city=city,
            county=county,
            country=country,
            subdivision=subdivision,
            builder=builder,
            bulk_uploaded=bulk_uploaded,
            alt_name=alt_name,
            is_multi_family=is_multi_family,
            geocode_address=geocode_address,
            show_warning_messages=show_warning_messages,
            log=log,
        )[0]

    def filter_similar(
        self,
        street_line1: str,
        city: City | int | str,
        zipcode: str | None,
        street_line2: str | None = None,
        state: str | None = None,
        lot_number: str | None = None,
        geocode_response: GeocodeResponse | int | None = None,
        country: Country | int | str | None = None,
    ):
        if isinstance(country, int):
            country = Country.objects.get(id=country)
        elif isinstance(country, str) and len(country):
            country = resolve_country(country)

        if isinstance(city, int):
            city = City.objects.get(id=city)

        if isinstance(geocode_response, int):
            geocode_response = GeocodeResponse.objects.get(id=geocode_response)

        if isinstance(city, City):
            if country is None:
                country = city.country
            if state is None and city.state:
                state = city.state
            city = city.name

        if street_line1 is None or city is None or zipcode is None:
            log.error(
                f"Refusing to filter without all components; {street_line1=} {city=} {zipcode=}"
            )
            return self.none()

        args = []
        geo_args = []
        kwargs = {"street_line1__iexact": street_line1, "zipcode": zipcode}

        # We only care about a lot number if it was passed otherwise dont care
        if lot_number is not None:
            args.append(~Q(lot_number=""))
            geo_args.append(~Q(geocode_response__home__lot_number=""))
            kwargs["lot_number"] = lot_number

        if street_line2 not in ["", None]:
            args.append(~Q(street_line2=""))
            geo_args.append(~Q(geocode_response__geocode__raw_street_line2=""))
            kwargs["street_line2__iexact"] = street_line2
        else:
            args.append(Q(street_line2__isnull=True) | Q(street_line2=""))
            geo_args.append(
                Q(geocode_response__geocode__raw_street_line2__isnull=True)
                | Q(geocode_response__geocode__raw_street_line2="")
            )

        if city:
            kwargs["city__name__iexact"] = city

        if state:
            kwargs["state"] = state
        else:
            kwargs["state__isnull"] = True

        if country:
            kwargs["city__country"] = country

        geo_kwargs = {
            f"geocode_response__geocode__raw_{k}": v
            for k, v in kwargs.items()
            if k not in ["lot_number", "state", "state__isnull"]
        }
        geo_kwargs["geocode_response__home__lot_number"] = lot_number

        query = Q(*args, **kwargs) | Q(*geo_args, **geo_kwargs)

        # If a geocoder finds the result you need to work through that as well.
        if geocode_response:
            place = geocode_response.get_normalized_fields(return_city_as_string=True)
            gr_args = []
            gr_kwargs = {
                "street_line1__iexact": place.get("street_line1"),
                "zipcode": place.get("zipcode"),
            }

            if lot_number is not None:
                gr_args.append(~Q(lot_number=""))
                gr_kwargs["lot_number"] = lot_number

            if street_line2 not in ["", None]:
                gr_args.append(~Q(street_line2=""))
                gr_kwargs["street_line2__iexact"] = place.get("street_line2")
            else:
                gr_args.append(Q(street_line2__isnull=True) | Q(street_line2=""))

            if place.get("city"):
                gr_kwargs["city__name__iexact"] = place.get("city")

            if place.get("state"):
                gr_kwargs["state"] = place.get("state")

            if place.get("country"):
                gr_kwargs["city__country"] = place.get("country")

            query |= Q(*gr_args, **gr_kwargs)

        # print(query)
        similar = self.filter(query).distinct()
        if log.isEnabledFor(logging.DEBUG) and similar.count() >= 1:
            address = (
                f"{lot_number=} {street_line1=} {street_line2=} {city=} {state=}"
                f" {country=} {zipcode=} {geocode_response=}"
            )
            log.debug(f"Identified {similar.count()} similar homes to {address}")
        return similar


class EEPProgramHomeStatusManager(models.Manager):
    """This manages the Program Statuses for the homes"""

    def get_queryset(self):
        return EEPProgramHomeStatusQuerySet(self.model, using=self._db)

    def in_sampleset(self, sampleset=None):
        return self.get_queryset().in_sampleset(sampleset=sampleset)

    def filter_confirmed_ratings(self):
        return self.get_queryset().filter_confirmed_ratings()

    def filter_by_multiple_companies(self, companies, **kwargs):
        """Filter stats by multiple companies"""
        assert isinstance(companies, (QuerySet, list))
        results = self.none()
        for comp in companies:
            results = results | self.filter_by_company(comp, **kwargs)

    def filter_by_company(self, company, **kwargs):
        return self.get_queryset().filter_by_company(company=company, **kwargs)

    def filter_by_user(self, user, **kwargs):
        """A way to trim down the list of objects by user"""
        return self.get_queryset().filter_by_user(user=user, **kwargs)

    def filter_for_company_and_subdivision(self, company, subdivision):
        """A way to trim down the list of floorplans to a company and subdivison"""
        return self.filter_by_company(company=company).filter(home__subdivision=subdivision)

    def filter_by_company_for_company_type(self, company, company_type):
        """Return a list of companies bound to homes that are of company type"""
        from axis.company.models import COMPANY_MODELS

        content_types = ContentType.objects.get_for_models(*COMPANY_MODELS).values()
        home_ids = self.filter_by_company(company).values_list("id", flat=True)
        rels = (
            Relationship.objects.filter(
                object_id__in=list(home_ids), content_type__in=content_types
            )
            .values_list("company", flat=True)
            .distinct()
        )
        companies = Company.objects.filter_by_company(company)
        return companies.filter(id__in=rels, company_type=company_type)

    def filter_by_user_for_company_type(self, user, company_type):
        """Return a list of builders for a company"""
        from .models import Home

        if user.is_superuser:
            home_ids = self.filter_by_user(user).values_list("home_id", flat=True)
            homes = Home.objects.filter(id__in=home_ids)
            return Company.objects.filter(
                id__in=homes.values_list("relationships__company", flat=True),
                company_type=company_type,
            )
        else:
            return self.filter_by_company_for_company_type(user.company, company_type)

    def filter_by_user_for_list_of_companies_by_types(self, user, ids_only=False, **kwargs):
        """Return a defaultdict(list) of companies keyed by type filtered by user."""
        from .models import Home

        content_type = ContentType.objects.get_for_model(Home)
        home_ids = self.filter_by_user(user).values_list("home_id", flat=True).distinct()
        rels = (
            Relationship.objects.filter(object_id__in=list(home_ids), content_type=content_type)
            .values_list("company", flat=True)
            .distinct()
        )
        companies = (
            Company.objects.filter_by_user(user).filter(id__in=rels, **kwargs).order_by("name")
        )
        breakdown = defaultdict(list)
        for c in companies:
            breakdown[c.company_type].append(c.id if ids_only else (c.id, c))
        return breakdown

    def filter_for_company_ready_for_invoice(self, company, builder_id=None):
        data = self.filter_by_company(company=company).filter(
            certification_date__isnull=False, ippitem__isnull=True
        )
        if company.name == "APS":
            from axis.home.models import Home
            from axis.customer_aps.models import LegacyAPSHome

            meterset_ids = data.filter(home__apshome__premise_id__isnull=False).values_list(
                "home__apshome__premise_id", flat=True
            )
            legacy_ids = LegacyAPSHome.objects.filter(aps_id__in=list(meterset_ids)).values_list(
                "aps_id", flat=True
            )
            legacy_home_ids = Home.objects.filter(
                apshome__premise_id__in=list(legacy_ids)
            ).values_list("id", flat=True)
            if len(legacy_ids):
                log.warning("Excluding Legacy Payment to APS ID's %s", legacy_ids)
                data = data.exclude(home__id__in=list(legacy_home_ids))
        if builder_id:
            builder = Company.objects.get(id=builder_id)
            home_ids = builder.relationships.get_homes(show_attached=True).values_list(
                "id", flat=True
            )
            data = data.filter(home_id__in=home_ids)
        return data

    def filter_homes_for_builder_agreement_paid(self, builder_agreement):
        """Return the number of lots paid for a builder agreement"""
        from axis.home.models import Home

        paid = self.filter(
            home__subdivision=builder_agreement.subdivision,
            ippitem__incentive_distribution__customer=builder_agreement.builder_org,
            eep_program__in=builder_agreement.eep_programs.all(),
            ippitem__incentive_distribution__status=2,
        )
        return Home.objects.filter(id__in=[x.home.id for x in paid.all()])

    def filter_homes_for_builder_agreement_pending(
        self, builder_agreement, incentive_distribution=None
    ):
        """Return the number of lots pending payment for a builder agreement"""
        from axis.home.models import Home

        pending = self.filter(
            home__subdivision=builder_agreement.subdivision,
            ippitem__incentive_distribution__customer=builder_agreement.builder_org,
            eep_program__in=builder_agreement.eep_programs.all(),
            ippitem__incentive_distribution__status=1,
        )
        if incentive_distribution:
            pending = pending.exclude(ippitem__incentive_distribution=incentive_distribution)
        return Home.objects.filter(id__in=[x.home.id for x in pending.all()])

    def get_recent_state_changes(self, company, days=30, limit=None):
        """Get a list of homes which have recently changed states"""
        today = now()
        activity_date = today - datetime.timedelta(days=days)
        queryset = self.filter_by_company(company)
        queryset = queryset.filter(
            Q(state_history__start_time__gte=activity_date)
            | Q(home__answer__modified_date__gte=activity_date)
        )
        stats = list[queryset.all().order_by("state_history__start_time").distinct()]
        if limit:
            return stats[:limit]
        return stats

    def get_ytd_certified_count(self, company):
        """Return the year to date certified homes"""
        home_stats = self.filter_by_company(company)
        today = now()
        year = datetime.datetime(today.year, 1, 1)
        return home_stats.filter(certification_date__gte=year).count()

    def get_prior_year_certified_count(self, company):
        """Return the prior year certified homes"""
        home_stats = self.filter_by_company(company)
        today = now()
        prior_year = datetime.datetime(today.year - 1, 1, 1)
        year = datetime.datetime(today.year, 1, 1)
        return home_stats.filter(
            certification_date__gte=prior_year, certification_date__lt=year
        ).count()

    def get_mtd_certified_count(self, company):
        """Return the current months certified homes"""
        home_stats = self.filter_by_company(company)
        today = now()
        month = datetime.datetime(today.year, today.month, 1)
        return home_stats.filter(certification_date__gte=month).count()

    def get_prior_month_certified_count(self, company):
        """Return the prior months certified homes"""
        home_stats = self.filter_by_company(company)
        today = now()
        if today.month == 1:
            prior_month = datetime.datetime(today.year - 1, 12, 1)
        else:
            prior_month = datetime.datetime(today.year, today.month - 1, 1)
        month = datetime.datetime(today.year, today.month, 1)
        return home_stats.filter(
            certification_date__gte=prior_month, certification_date__lt=month
        ).count()

    def get_status_counts(self, company):
        """Return the active state counts"""
        states, show = [], False
        today = now()
        year = datetime.datetime(today.year, 1, 1)
        home_stats = self.filter_by_company(company)
        for state, state_name in self.model.get_state_choices():
            sstats = home_stats.filter(state=state)
            if state == "complete":
                sstats = sstats.filter(certification_date__gte=year)
            sstats_count = sstats.count()
            if not sstats_count and state in ["pending_inspection", "abandoned", "failed"]:
                continue
            if sstats_count > 0:
                show = True
            states.append((state_name, sstats_count))
        if show:
            return states
        return []

    def get_subdiv_homes_for_scheduling(self, company, subdiv, id_list):
        kwargs = {"company": company, "home__subdivision": subdiv}
        if id_list:
            kwargs["home__id__in"] = id_list
        return self.filter(**kwargs)

    def get_builder_homes_for_scheduling(self, company, id_list):
        return self.filter(company=company, home__id__in=id_list)

    def filter_ready_for_incentivepaymentstatus(self):
        """This is how we filter for getting stuff over to IPP"""
        return self.filter(
            Q(eep_program__builder_incentive_dollar_value__gte=0.01)
            | Q(eep_program__rater_incentive_dollar_value__gte=0.01)
            | Q(standardprotocolcalculator__builder_incentive__gte=0.01),
            certification_date__isnull=False,
            eep_program__owner__is_customer=True,
            state="complete",
            incentivepaymentstatus__isnull=True,
        )

    @staticmethod
    def coerce_boolean(item):
        if isinstance(item, bool):
            return item
        if isinstance(item, type(None)):
            return bool(0)
        if isinstance(item, int):
            return bool(item)
        if isinstance(item, str):
            if item in ["1", "0"]:
                return bool(int(item))
            if item.lower() == "true":
                return bool(1)
            if item.lower() == "false":
                return bool(0)
        raise ValueError("Invalid item must be |True|False|")

    def verify_and_create_for_user(
        self,
        user: models.Model,
        create: bool = True,
        company: models.Model | None = None,
        eep_program: models.Model | None = None,
        floorplan: models.Model | None = None,
        home: models.Model | None = None,
        remrate: models.Model | None = None,
        is_billable: typing.Union[bool, None] = None,
        ignore_missing: bool = False,
        ignore_missing_floorplan: bool = False,
        overwrite_old_answers: bool = False,
        rater_of_record: models.Model | None = None,
        log: typing.Union[logging.Logger, None] = None,
    ):
        log = log if log is not None else logging.getLogger(__name__)
        history_start = now()

        floorplan_or_remrate = floorplan or remrate
        issue, missing = None, []
        if eep_program:
            issue = []
            if eep_program.requires_floorplan() and floorplan_or_remrate is None:
                issue.append("Floorplan")
                missing.append("floorplan")
            if len(issue):
                prm = "'{program}' requires ".format(program=eep_program)
                issue = prm + " and ".join(issue) + " to be specified, none provided."
        else:
            issue = []
            if floorplan_or_remrate:
                issue.append("Floorplan or REMRate Data")
                missing.append("floorplan")
            if len(issue):
                issue = " and ".join(issue) + " cannot be specified without a Program."
            else:
                issue = "Missing Program, Rating Type and Floorplan or REMRate Data."

        if issue:
            if ignore_missing or ignore_missing_floorplan:
                if len(missing) == 1 and missing[0] == "floorplan" and ignore_missing_floorplan:
                    log.warning("Skipping missing floorplan")
                else:
                    log.warning(issue)
                    return None
            else:
                log.error(issue)
                return None
        try:
            is_billable = self.coerce_boolean(is_billable)
        except ValueError:
            log.error(strings.INVALID_IS_BILLABLE.format(is_billable=is_billable))

        if home:
            try:
                home_url = reverse("home:view", kwargs={"pk": home.id})
            except NoReverseMatch:
                home_url = "/home/%d" % home.id

            home_stats = self.filter(eep_program=eep_program, home=home, company=company)
            if home_stats.count() > 1:
                log.error(
                    strings.MULTIPLE_HOME_STATS_FOUND.format(
                        home=home, url=home_url, program=eep_program
                    )
                )
                return None
            elif home_stats.count() == 1:
                home_stat = home_stats.get()

                errors = validate_compatible_program(
                    home,
                    eep_program,
                    created_date=home_stat.created_date,
                    state=home_stat.state,
                    raise_exception=False,
                    pretty=True,
                )
                for error in errors:
                    log.error(error)

                if home_stat.company.id != company.id:
                    log.error(
                        strings.PROGRAM_ON_HOME_IN_USE.format(
                            home=home,
                            url=home_url,
                            company=home_stat,
                            program=home_stat.eep_program,
                        )
                    )
                if home_stat.floorplan and home_stat.floorplan != floorplan:
                    if floorplan is not None:
                        log.error(
                            strings.PREVIOUSLY_DEFINED_FLOORPLAN.format(
                                home=home,
                                url=home_url,
                                floorplan=floorplan,
                                prior_floorplan=home_stat.floorplan,
                            )
                        )
                    else:
                        log.info(
                            strings.USING_PREVIOUSLY_DEFINED_FLOORPLAN.format(
                                home=home, url=home_url, prior_floorplan=home_stat.floorplan
                            )
                        )
                if home_stat.certification_date:
                    if overwrite_old_answers:
                        log.warning(
                            strings.EXISTING_PROGRAM_ALREADY_CERTIFIED.format(
                                home=home_stat.home, program=home_stat.eep_program, url=home_url
                            )
                        )
                    else:
                        log.info(
                            strings.EXISTING_PROGRAM_ALREADY_CERTIFIED.format(
                                home=home_stat.home, program=home_stat.eep_program, url=home_url
                            )
                        )
                return home_stat
            else:
                if eep_program:
                    log.info(
                        "Verifying that %s isn't already closed (date=%r)...",
                        eep_program,
                        eep_program.program_close_date,
                    )
                    if (
                        eep_program.program_close_date
                        and eep_program.program_close_date < datetime.date.today()
                    ):
                        error_message = "Program %s has closed and cannot be added to home"
                        log.error(error_message, eep_program)
                        return None

                if create:
                    errors = validate_compatible_program(
                        home,
                        eep_program,
                        raise_exception=False,
                        pretty=True,
                    )
                    for error in errors:
                        log.error(error)
                    if errors:
                        return None

                    company = Company.objects.get(id=company.id)
                    try:
                        home_stat, created = self.get_or_create(
                            eep_program=eep_program,
                            home=home,
                            company=company,
                            floorplan=floorplan,
                            rater_of_record=rater_of_record,
                            defaults=dict(is_billable=is_billable),
                        )
                    except IntegrityError:
                        _home_stat = self.get(eep_program=eep_program, home=home)
                        log.error(
                            "The program %s is already assigned to home %s by %s",
                            eep_program,
                            home,
                            _home_stat.company,
                        )
                        return

                    # Initialize input-collection for qa
                    uses_input_collection = home_stat.eep_program.collection_request_id
                    needs_initialization = not home_stat.collection_request_id
                    if uses_input_collection and needs_initialization:
                        home_stat.set_collection_from_program()

                    log.info(
                        strings.STAT_USED_CREATE.format(
                            create="Created" if create else "Used existing",
                            url=home_url,
                            home=home,
                            program=home_stat.eep_program,
                        )
                    )

                    if created:
                        create_or_update_spanning_relationships(company, home_stat)

                    if created and home_stat.history.all()[0].history_user is None:
                        home_stat.history.filter(
                            history_date__gte=history_start, history_user__isnull=True
                        ).update(history_user=user)

                    return home_stat
        return None

    def verify_for_company(
        self,
        user: models.Model,
        company: models.Model | None = None,
        eep_program: models.Model | None = None,
        floorplan: models.Model | None = None,
        home: models.Model | None = None,
        remrate: models.Model | None = None,
        is_billable: typing.Union[bool, None] = None,
        ignore_missing: bool = False,
        ignore_missing_floorplan: bool = False,
        overwrite_old_answers: bool = False,
        rater_of_record: models.Model | None = None,
        log: typing.Union[logging.Logger, None] = None,
    ):
        return self.verify_and_create_for_user(
            create=False,
            user=user,
            company=company,
            eep_program=eep_program,
            floorplan=floorplan,
            home=home,
            remrate=remrate,
            is_billable=is_billable,
            ignore_missing=ignore_missing,
            ignore_missing_floorplan=ignore_missing_floorplan,
            overwrite_old_answers=overwrite_old_answers,
            rater_of_record=rater_of_record,
            log=log,
        )


class EEPProgramHomeStatusQuerySet(QuerySet):
    def order_by_customer_status(self):
        """Mirrors behavior from EEPProgram queryset.order_by_customer_status()"""
        return self.order_by(
            "-eep_program__owner__is_customer",  # Is a paying customer
            "eep_program__program_start_date",  # Oldest opened programs first
        )

    def in_sampleset(self, sampleset=None):
        kwargs = {"samplesethomestatus__is_active": True}
        if sampleset:
            kwargs["samplesethomestatus__sampleset"] = sampleset
        return self.filter(**kwargs)

    def filter_confirmed_ratings(self):
        return self.filter(samplesethomestatus__isnull=True)

    # FIXME: This method is a monster.
    def filter_by_company(self, company, **kwargs):
        from axis.home.models import Home

        # This already includes items related via Association on homestatuses
        home_ids = list(
            Home.objects.filter_by_company(company=company).values_list("id", flat=True)
        )

        reversed_companies = Relationship.objects.get_reversed_companies(company, ids_only=True)
        outwards_relationships = company.relationships.get_companies(
            show_attached=True, is_viewable=True, ids_only=True
        )

        mutual_relationships = list(
            set(reversed_companies).intersection(set(outwards_relationships))
        )

        # Include Items that:
        include_query = Q(
            # Company owns the EEPProgram
            Q(company=company)
            # OR company has mutual relationship with stat owner AND program owner
            | Q(company__in=mutual_relationships, eep_program__owner__in=mutual_relationships)
            # OR company is the owner of the program and is a sponsor
            | Q(eep_program__owner=company, eep_program__owner__is_eep_sponsor=True)
            # OR company has been shared with via Association
            | Q(
                associations__company=company,
                associations__is_active=True,
                associations__is_hidden=False,
            )
        )

        # Remove items that:
        exclude_query = Q(
            # The company isn't the owner of
            ~Q(company=company)
            # AND isn't the owner of the eep_program
            & ~Q(eep_program__owner=company)
            # AND has restrictions
            & Q(eep_program__viewable_by_company_type__isnull=False)
            # AND the company type isn't allowed
            & ~Q(eep_program__viewable_by_company_type__contains=company.company_type)
        )

        value_ids = (
            self.filter(home_id__in=home_ids, **kwargs).filter(include_query).exclude(exclude_query)
        )
        return self.filter(id__in=list(value_ids.values_list("pk", flat=True)))

    def filter_by_user(self, user: User | None, **kwargs) -> QuerySet:
        """A way to trim down the list of objects by user"""
        if user is None:
            return self.none()
        if user.is_superuser:
            return self.filter(**kwargs)
        try:
            kwargs["company"] = user.company
        except AttributeError:
            return self.none()
        return self.filter_by_company(**kwargs)

    def annotate_customer_hirl_legacy_project_id(self):
        """
        Annotate legacy projects project-id annotation
        :return: project-id annotation or None
        """
        from axis.annotation.models import Annotation

        annotations_subquery = Annotation.objects.filter(
            type__slug="project-id",
            object_id=OuterRef("pk"),
        ).annotate(
            hirl_legacy_project_id=Case(
                When(content="", then=None), default=Cast("content", output_field=CharField())
            )
        )
        return self.annotate(
            hirl_legacy_project_id=Subquery(
                annotations_subquery.values("hirl_legacy_project_id")[:1]
            )
        )

    def annotate_customer_hirl_unit_count(self):
        """
        Example queryset:
        EEPProgramHomeStatus.objects.filter(
            eep_program__owner__slug=customer_hirl_app.CUSTOMER_SLUG,
            eep_program__is_multi_family=True
        ).annotate_customer_hirl_unit_count()

        :return: queryset with unit_count annotated field
        """

        return self.annotate(
            unit_count=Coalesce(
                F("customer_hirl_project__number_of_units"), 0, output_field=IntegerField()
            )
        )

    def annotate_customer_hirl_hers_score(self):
        """
        Annotate HERS score for legacy and new projects from Annotations
        :return: hers_score annotation with Integer value or None
        """
        from axis.annotation.models import Annotation

        annotations_subquery = Annotation.objects.filter(
            type__slug__in=[
                "hers-score",  # legacy hers-score annotation
                # 2020 programs
                "eri-as-designed-ngbs-sf-new-construction-2020-new-final",
                "eri-as-designed-ngbs-mf-new-construction-2020-new-final",
                "eri-as-designed-ngbs-sf-certified-2020-new-final",
                # 2015 programs
                "as-designed-home-hers-ngbs-sf-new-construction-2015-new-final",
                "as-designed-home-hers-ngbs-mf-new-construction-2015-new-final",
            ],
            object_id=OuterRef("pk"),
        ).annotate(
            hers_score=Case(
                When(content="", then=None), default=Cast("content", output_field=IntegerField())
            )
        )
        return self.annotate(hers_score=Subquery(annotations_subquery.values("hers_score")[:1]))

    def annotate_customer_hirl_certification_level(self):
        """
        Annotate NGBS Certification Level score for legacy from Annotations and new projects from Final QA
        :return: certification_level annotation with String value or None
        """
        from axis.qa.models import QAStatus, QARequirement

        final_qa_status_subquery = QAStatus.objects.filter(
            home_status=OuterRef("pk"),
            requirement__type=QARequirement.FINAL_INSPECTION_QA_REQUIREMENT_TYPE,
        )
        return self.annotate(
            certification_level=Subquery(
                final_qa_status_subquery.values("hirl_certification_level_awarded")[:1]
            ),
        )

    def annotate_customer_hirl_certification_number(self):
        """
        Annotate Certification Number for legacy and new projects from Annotations
        :return: certification_number annotation with Integer value or None
        """
        return self.annotate(
            certification_number=Case(
                When(
                    customer_hirl_project__certification_counter=None,
                    then=F("customer_hirl_project__wri_certification_counter"),
                ),
                default=F("customer_hirl_project__certification_counter"),
            ),
        )

    def annotate_customer_hirl_client_ca_status(self):
        """
        Customer HIRL specific: Annotate current Project Client Agreement status.
        By default, use Builder Organization CA state
        :return: QuerySet with client_ca_status annotation
        """
        from axis.customer_hirl.models import HIRLProjectRegistration, BuilderAgreement

        return self.annotate(
            client_ca_status=Case(
                When(
                    customer_hirl_project__registration__project_client=HIRLProjectRegistration.PROJECT_CLIENT_BUILDER,
                    then=Subquery(
                        BuilderAgreement.objects.filter(
                            company=OuterRef(
                                "customer_hirl_project__registration__builder_organization__pk"
                            ),
                        )
                        .order_by("-date_created")
                        .values("state")[:1]
                    ),
                ),
                When(
                    customer_hirl_project__registration__project_client=HIRLProjectRegistration.PROJECT_CLIENT_ARCHITECT,
                    then=Subquery(
                        BuilderAgreement.objects.filter(
                            company=OuterRef(
                                "customer_hirl_project__registration__architect_organization__pk"
                            ),
                        )
                        .order_by("-date_created")
                        .values("state")[:1]
                    ),
                ),
                When(
                    customer_hirl_project__registration__project_client=HIRLProjectRegistration.PROJECT_CLIENT_DEVELOPER,
                    then=Subquery(
                        BuilderAgreement.objects.filter(
                            company=OuterRef(
                                "customer_hirl_project__registration__developer_organization__pk"
                            ),
                        )
                        .order_by("-date_created")
                        .values("state")[:1]
                    ),
                ),
                When(
                    customer_hirl_project__registration__project_client=HIRLProjectRegistration.PROJECT_CLIENT_OWNER,
                    then=Subquery(
                        BuilderAgreement.objects.filter(
                            company=OuterRef(
                                "customer_hirl_project__registration__community_owner_organization__pk"
                            ),
                        )
                        .order_by("-date_created")
                        .values("state")[:1]
                    ),
                ),
                default=Subquery(
                    BuilderAgreement.objects.filter(
                        company=OuterRef(
                            "customer_hirl_project__registration__builder_organization__pk"
                        ),
                    )
                    .order_by("-date_created")
                    .values("state")[:1]
                ),
            )
        )

    def annotate_customer_hirl_client_coi_expiration_status(self):
        """
        Customer HIRL specific: Annotate client_coi_status field that returns "active" or "expired"
        string based on whether Client company have non-expired COIDocument.
        :return: client_coi_status and _client_coi_active_count annotation fields
        """
        from axis.customer_hirl.models import HIRLProjectRegistration, COIDocument

        expiration_date = timezone.now()

        return self.annotate(
            _coi_document_exists=Case(
                When(
                    customer_hirl_project__registration__project_client=HIRLProjectRegistration.PROJECT_CLIENT_BUILDER,
                    then=Exists(
                        COIDocument.objects.filter(
                            company=OuterRef(
                                "customer_hirl_project__registration__builder_organization"
                            )
                        ),
                        expiration_date__gt=expiration_date,
                    ),
                ),
                When(
                    customer_hirl_project__registration__project_client=HIRLProjectRegistration.PROJECT_CLIENT_ARCHITECT,
                    then=Exists(
                        COIDocument.objects.filter(
                            company=OuterRef(
                                "customer_hirl_project__registration__architect_organization"
                            )
                        ),
                        expiration_date__gt=expiration_date,
                    ),
                ),
                When(
                    customer_hirl_project__registration__project_client=HIRLProjectRegistration.PROJECT_CLIENT_DEVELOPER,
                    then=Exists(
                        COIDocument.objects.filter(
                            company=OuterRef(
                                "customer_hirl_project__registration__developer_organization"
                            )
                        ),
                        expiration_date__gt=expiration_date,
                    ),
                ),
                When(
                    customer_hirl_project__registration__project_client=HIRLProjectRegistration.PROJECT_CLIENT_OWNER,
                    then=Exists(
                        COIDocument.objects.filter(
                            company=OuterRef(
                                "customer_hirl_project__registration__community_owner_organization"
                            )
                        ),
                        expiration_date__gt=expiration_date,
                    ),
                ),
                default=Exists(
                    COIDocument.objects.filter(
                        company=OuterRef(
                            "customer_hirl_project__registration__builder_organization"
                        )
                    ),
                    expiration_date__gt=expiration_date,
                ),
            ),
            client_coi_status=Case(
                When(_coi_document_exists=True, then=Value("active")),
                default=Value("expired"),
                output_field=CharField(),
            ),
        )


class EEPProgramHomeStatusHistoricalRecords(HistoricalRecords):
    def get_meta_options(self, model):
        """
        Returns a dictionary of fields that will be added to
        the Meta inner class of the historical record model.
        :param model: Model Object
        """
        # use a less verbose name so we keep auto-generated permissions
        # under 50 chars
        return {
            "ordering": ("-history_date",),
            "verbose_name": "Historical Project",
        }


class StandardDisclosureSettingsQuerySet(QuerySet):
    """This manages the Program Statuses for the homes"""

    def filter_by_company(self, company, source=None):
        from axis.company.models import Company
        from axis.subdivision.models import Subdivision
        from .models import EEPProgramHomeStatus

        kwargs = {}
        if isinstance(source, EEPProgramHomeStatus):
            kwargs["home_status"] = source
        elif isinstance(source, Subdivision):
            kwargs["subdivision"] = source
        elif isinstance(source, Company):
            kwargs["company"] = source
        return self.filter(owner=company, **kwargs)

    def filter_by_user(self, user, source=None):
        return self.filter_by_company(user.company, source=source)

    def get_for_company(self, company):
        return self.filter_by_company(company).first()

    def get_for_user(self, user):
        return self.filter_by_user(user).first()

    def get_for_object(self, source, user):
        return self.filter_by_user(user, source=source).first()
