"""utils.py: customer aps"""


import copy
import datetime
import logging
import math
import re
import time

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db.models import Q
from localflavor.us.us_states import STATES_NORMALIZED

from axis.geocoder.models import Geocode
from axis.geographic.utils.legacy import do_blind_geocode

__author__ = "Steven Klass"
__date__ = "3/5/12 11:25 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


def update_apshomes(lots=None):
    """
    This will correlate homes to metersets.
    https://github.com/pivotal-energy-solutions/axis/wiki/APS_Overview#apsautomatcher-class
    :param lots: Home queryset.
    :return: list of new confirmations [(Home, APSHome), (Home, APSHome), ...]
    """
    from axis.home.models import EEPProgramHomeStatus, Home
    from axis.customer_aps.models import APSHome
    from axis.company.models import Company

    if not lots:
        aps = Company.objects.get(name="APS")
        home_stats = EEPProgramHomeStatus.objects.filter(eep_program__owner=aps)
        lots = Home.objects.filter(
            id__in=home_stats.values_list("home_id", flat=True), apshome__isnull=True
        )

    confirmations = []
    for home in lots:
        try:
            if home.street_line2 in ["", None]:
                # Changed b/c APS has a tendency to use bogus street line 2 only consider it if
                # the parent has it..
                aps_home = APSHome.objects.get(
                    Q(street_line2__isnull=True)
                    | Q(street_line2="")
                    | Q(street_line2__icontains="JSP"),
                    home__isnull=True,
                    street_line1=home.street_line1,
                    city=home.city,
                    state=home.state,
                    zipcode=home.zipcode,
                )
            else:
                aps_home = APSHome.objects.get(
                    home__isnull=True,
                    street_line1=home.street_line1,
                    street_line2=home.street_line2,
                    city=home.city,
                    state=home.state,
                    zipcode=home.zipcode,
                )
            aps_home.home = home
            aps_home.save()
            confirmations.append((aps_home, home))
        except (ObjectDoesNotExist, MultipleObjectsReturned):
            continue
    return confirmations


class APSAutoMatcher(object):
    def __init__(self, *args, **kwargs):
        self.axis_home = kwargs.get("axis_home", None)
        self.aps_home = kwargs.get("axis_home", None)

        self.corrected = False
        self.aligned = False
        self.matched = False
        self.match_reason = None
        self.issues = list(range(10000))
        self.show_detail = kwargs.get("show_detail", False)

        self.reserved_words = [
            "north",
            "south",
            "east",
            "west",
            "blvd",
            "place",
            "street",
            "road",
            "place",
            "avenue",
            "circle",
            "drive",
            "trail",
            "glen",
            "gln",
            "manor",
        ]

    def queryset(self, exclude_ids):
        from axis.customer_aps.models import APSHome

        if self.axis_home.geocode_response and self.axis_home.geocode_response.geocode:
            homes = APSHome.objects.filter(
                Q(raw_street_line_1__icontains=self.axis_home.street_line1)
                | Q(
                    raw_street_line_1__iexact=self.axis_home.geocode_response.geocode.raw_street_line1
                ),
                home__isnull=True,
            )
            log.debug("Using raw address as well.")
        else:
            homes = APSHome.objects.filter(
                home__isnull=True, raw_street_line_1__icontains=self.axis_home.street_line1
            )
            log.debug("No Geocode response -- %d APS Homes found", homes.count())

        if exclude_ids:
            homes = homes.exclude(id__in=exclude_ids)

        if homes.count() == 0:
            log.info(" No APS homes Found")

        elif homes.count() > 1:
            log.info("%s APS homes found", homes.count())
            for home in homes:
                if not home.confirmed_address:
                    update = self.geolocate_aps_home(home=home)
                    if update.confirmed_address:
                        self._update(home, update)

        elif homes.count() == 1:
            log.debug("Perfect!! 1 APS Home found.")

        return homes

    def get_fuzzy_aps_match(self, exclude_ids=None):
        homes = self.queryset(exclude_ids)
        self.aps_home = homes.get()
        if self.aps_home:
            log.debug("Fuzzy Matched to APS Home (%d) %s", self.aps_home.id, self.aps_home)
        return self.aps_home

    def geolocate_aps_home(self, home=None):
        obj = copy.deepcopy(self.aps_home)
        log.info(
            "Geolocating APS Home (%d)%s - %s", obj.id, " with home entered" if home else "", obj
        )
        geolocate_apshome(object=obj, **obj.__dict__)

        if home is None:
            self.updated_aps_home = obj
        return obj

    def geolocate_axis_home(self):
        obj = copy.deepcopy(self.axis_home)
        log.info(
            "Geolocating Axis Home (%d)%s - %s",
            obj.id,
            " with home entered" if self.axis_home else "",
            obj,
        )
        lookup = dict(
            street_line1=obj.street_line1,
            street_line2=obj.street_line2,
            city=obj.city,
            state=obj.state,
            zipcode=obj.zipcode,
        )
        if obj.confirmed_address is False and obj.address_override is False:
            do_blind_geocode(obj, **lookup)
        self.updated_axis_home = obj
        return obj

    def is_address_equal(self, addr1, addr2):
        errors = []
        if not addr1.confirmed_address and not addr2.confirmed_address:
            for key in ["street_line1", "street_line2", "state", "zipcode"]:
                if (
                    "{}".format(getattr(addr1, key)).lower()
                    != "{}".format(getattr(addr2, key)).lower()
                ):
                    log.debug(" Bad %s %s != %s", key, getattr(addr1, key), getattr(addr2, key))
                    errors.append(key)
            if len(errors):
                log.debug(" Unconfirmed on both APS and Axis")
                return False, ["Unconfirmed"]

        elif not addr1.confirmed_address or not addr2.confirmed_address:
            log.debug(" Unconfirmed on either APS and Axis")
            return False, ["Unconfirmed"]

        if addr1.confirmed_address and addr2.confirmed_address:
            if not (addr1.latitude and addr1.longitude) or not (addr2.latitude and addr2.longitude):
                log.debug(" Missing Lat / Long")
                return False, ["Missing Lat / Long"]

            for key in ["street_line1", "state", "zipcode"]:
                if getattr(addr1, key) != getattr(addr2, key):
                    log.debug(" Bad %s %s != %s", key, getattr(addr1, key), getattr(addr2, key))
                    errors.append(key)

            if addr1.street_line2 not in ["", None] and addr2.street_line2 not in ["", None]:
                key = "street_line2"
                if getattr(addr1, key) != getattr(addr2, key):
                    log.debug(" Bad %s %s != %s", key, getattr(addr1, key), getattr(addr2, key))
                    errors.append(key)

        addr1_city, addr2_city = None, None
        if addr1.city:
            addr1_city = addr1.city if isinstance(addr1.city, str) else addr1.city.name
        if addr2.city:
            addr2_city = addr2.city if isinstance(addr2.city, str) else addr2.city.name

        if addr1_city and addr1_city != addr2_city:
            key = "city"
            log.debug("Bad %s %s != %s", key, getattr(addr1, key), getattr(addr2, key))
            errors.append(key)
        if len(errors):
            return False, errors

        if not addr1.confirmed_address and not addr2.confirmed_address:
            log.info("Both address are unconfirmed - but otherwise equal")

        return True, None

    def automatch(self, exclude_ids=None):
        self.get_fuzzy_aps_match(exclude_ids=exclude_ids)

        self.geolocate_aps_home()
        self.geolocate_axis_home()

        priority = [
            (self.axis_home, self.aps_home, "No Changes"),
            (self.axis_home, self.updated_aps_home, "Updated APS"),
            (self.updated_axis_home, self.aps_home, "Updated Axis"),
            (self.updated_axis_home, self.updated_aps_home, "Updated Axis and APS"),
        ]

        for axis, aps, notes in priority:
            match, errors = self.is_address_equal(axis, aps)
            if match:
                self.matched = True
                self.match_reason = notes
                self.issues = []
                break
            if len(errors) < len(self.issues):
                self.issues = errors
                self.match_reason = notes
        if self.matched:
            log.info(
                "We have a match (%s) - Axis (%d) %s  == APS (%d) %s !",
                notes,
                axis.id,
                axis,
                aps.id,
                aps,
            )
            return True
        return False

    def _update(self, object, geolocation_object):
        include = [
            "street_line1",
            "street_line2",
            "city",
            "county",
            "state",
            "zipcode",
            "latitude",
            "longitude",
        ]
        updated_items = dict([(item, getattr(geolocation_object, item)) for item in include])
        for key, value in updated_items.items():
            if value and getattr(object, key) != value:
                log.debug("Updating %s : %s > %s", key, getattr(object, key), value)
                setattr(object, key, value)
        object.save()
        model = ContentType.objects.get_for_model(object).model_class()
        return model.objects.get(id=object.id)

    def update(self):
        if not self.matched:
            return
        if self.updated_aps_home and self.match_reason.lower() == "Updated APS".lower():
            self._update(self.aps_home, self.updated_aps_home)
        update_apshomes(lots=[self.axis_home])
        from axis.customer_aps.models import APSHome

        aps = APSHome.objects.get(id=self.aps_home.id)
        if aps.home:
            self.corrected = True

    def align(self):
        data = {"axis_home": self.axis_home, "aps_home": self.aps_home, "aligned": False}

        if not self.aps_home.confirmed_address or not self.axis_home.confirmed_address:
            log.info("Skipping alignment - addresses are not confirmed")
            data["aligned"] = True
            return data
        if self.aps_home.home and self.aps_home.home.id:
            log.info("Skipping alignment - already aligned")
            data["aligned"] = True
            return data

        log.info("We should be matching.. %s != %s", self.aps_home, self.axis_home)

        include = [
            "street_line1",
            "street_line2",
            "city",
            "county",
            "state",
            "zipcode",
            "latitude",
            "longitude",
        ]

        start, counter = datetime.datetime.now(datetime.timezone.utc), 0
        while True:
            self.geolocate_axis_home()
            try:
                aware_modified_date = self.updated_axis_home.place.modified_date
            except (AttributeError, ValueError):
                log.info("No place modified date on Axis Home")
                aware_modified_date = start - datetime.timedelta(minutes=5)

            if aware_modified_date >= start or counter > 10:
                log.info(
                    "Axis Geolocation [%s] - %s", self.updated_axis_home.id, self.updated_axis_home
                )
                break
            self.updated_axis_home.correlations = 0
            self.updated_axis_home.save()
            counter += 1
            time.sleep(1)

        def get_obj_or_none(obj, attr):
            value = getattr(obj, attr)
            if value or value is None:
                return value
            if not len(value):
                return None
            return value

        updated_axis_items = dict(
            [(item, get_obj_or_none(self.updated_axis_home, item)) for item in include]
        )

        while True:
            self.geolocate_aps_home()
            try:
                aware_modified_date = self.updated_aps_home.place.modified_date
            except (AttributeError, ValueError):
                log.info("No place modified date on APS Home")
                aware_modified_date = start - datetime.timedelta(minutes=5)

            if aware_modified_date >= start or counter > 10:
                log.info(
                    "APS Geolocation [%s] - %s", self.updated_aps_home.id, self.updated_aps_home
                )
                break
            self.updated_aps_home.correlations = 0
            self.updated_aps_home.save()
            counter += 1
            time.sleep(1)
        updated_aps_items = dict(
            [(item, get_obj_or_none(self.updated_aps_home, item)) for item in include]
        )

        matched = True
        if not self.updated_axis_home.confirmed_address:
            log.info("Axis home is not confirmed - %s", self.updated_axis_home)
            matched = False
        if not self.updated_aps_home.confirmed_address:
            log.info("APS home is not confirmed - %s", self.updated_axis_home)
            matched = False
        for key, value in updated_axis_items.items():
            aps_value = updated_aps_items[key]
            # for latitude and longitude we allow almost-equality
            if key == "latitude" or key == "longitude":
                matched = math.isclose(aps_value, value, abs_tol=0.01)
            elif aps_value != value:
                matched = False

            if not matched:
                log.debug("%s: %s != %s", key, value, updated_aps_items[key])

        if matched:
            log.info("Was able to match %s to %s", self.axis_home, self.aps_home)
            self._update(self.axis_home, self.updated_axis_home)
            self._update(self.aps_home, self.updated_aps_home)
            self.aps_home.home = self.axis_home
            self.aps_home.save()
            self.aligned = True
            data["aligned"] = True
        else:
            log.info("Was UNABLE to match %s to %s", self.axis_home, self.aps_home)
        return data


def geolocate_apshome(**data):
    """This is the generic tool to translate a meterset to a lookup"""

    return_lookup = data.get("return_lookup", False)
    object = data.get("object")

    try:
        street_line1 = data["raw_street_line_1"]
    except KeyError:
        try:
            street_line1 = [
                data["raw_street_number"],
                data["raw_prefix"],
                data["raw_street_name"],
                data["raw_suffix"],
            ]
            street_line1 = " ".join([x for x in street_line1 if x])
        except KeyError:
            street_line1 = data["street_line1"]

    if data.get("raw_state"):
        state = STATES_NORMALIZED[data.get("raw_state").lower()]
    else:
        if "state" in data:
            state = data["state"]
        else:
            state = None
            log.info("No STATE found for %s", data)

    is_multi_family = False
    street_line2 = data.get("raw_street_line_2")
    street_line2 = street_line2.strip() if street_line2 else street_line2
    if street_line2 in ["", None]:
        street_line2 = None
    else:
        if re.search(r"\b(STE|APT|UNIT)\b", street_line2):
            is_multi_family = True

    from axis.geographic.models import City

    city, _ = City.objects.get_or_create_by_string(
        data.get("raw_city"), state=data.get("raw_state")
    )

    if city is None:
        if "city_id" in data:
            city = City.objects.get(id=data["city_id"])
        else:
            log.info("No city provided for %r data", data)
            return Geocode.objects.none()

    lookup = dict(
        street_line1=street_line1,
        lot_number=data.get("raw_lot_number"),
        street_line2=street_line2,
        is_multi_family=is_multi_family,
        city=city,
        county=city.county,
        metro=city.county.metro,
        climate_zone=city.county.climate_zone,
        state=state,
        zipcode=data.get("raw_zip"),
    )

    if return_lookup:
        return lookup
    if object:
        if object.address_override is False:
            log.debug("Doing blind geocode")
            try:
                do_blind_geocode(object, **lookup)
            except UnicodeDecodeError:
                log.exception("Unable to lookup %r [%d] %r", object, object.id, lookup)
                raise
            if not object.confirmed_address:
                for k, v in lookup.items():
                    if getattr(object, k) != v:
                        setattr(object, k, v)
            object.lot_number = lookup.get("lot_number")
            if street_line2:
                object.street_line2 = street_line2
            object.save()
        return
    return Geocode.objects.get_matches(**lookup)
