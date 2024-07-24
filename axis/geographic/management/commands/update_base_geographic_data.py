"""update_tiger_data.py - Axis"""
import csv
import glob
import json
import logging
import os
import re
import tempfile
import zipfile
from collections import defaultdict
from difflib import SequenceMatcher

from django.core.management import BaseCommand, CommandError
from localflavor.us.us_states import CONTIGUOUS_STATES, NON_CONTIGUOUS_STATES, US_TERRITORIES

from axis.geocoder.api_v3.serializers import GeocodeCityMatchesSerializer, GeocodeCitySerializer
from axis.geographic.api_v3.serializers import BaseCitySerializer
from axis.geographic.models import (
    ClimateZone,
    Metro,
    County,
    City,
    EXTENDED_COUNTRY_NAMES,
    COUNTRIES,
)
from axis.geographic.strings import COUNTY_TYPES, DOE_MOISTURE_REGIMES
from axis.geographic.utils.country import get_usa_default, resolve_country

log = logging.getLogger(__name__)

__author__ = "Steven K"
__date__ = "6/1/21 16:16"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

source_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "sources")

CLIMATE_ZONE_SOURCE = os.path.abspath(os.path.join(source_dir, "climate_zones.csv"))
METRO_SOURCE = os.path.abspath(os.path.join(source_dir, "Metro.txt"))
COUNTY_SOURCE = os.path.abspath(os.path.join(source_dir, "Gaz_counties_national.txt"))
CITY_SOURCE = os.path.abspath(os.path.join(source_dir, "Gaz_places_national.txt"))
CENSUS_SOURCE = os.path.abspath(os.path.join(source_dir, "USCensusPlaceData.zip"))
COUNTRY_CITY_SOURCE = os.path.abspath(os.path.join(source_dir, "world_cities.csv"))

US_STATES = [x[0] for x in CONTIGUOUS_STATES] + [x[0] for x in NON_CONTIGUOUS_STATES]
US_STATES += [x[0] for x in US_TERRITORIES]

TERRITORIES = [x[0] for x in US_TERRITORIES if x[0] != "PR"]


class Command(BaseCommand):
    help = "Updates the tiger data when it gets updated"
    requires_system_checks = []

    def add_arguments(self, parser):
        parser.add_argument(
            "--no_update", help="Do Not update", action="store_false", dest="update"
        )
        parser.add_argument(
            "--state",
            help="Only include state",
            action="store",
            dest="search_state",
            choices=US_STATES,
            required=False,
        )
        parser.add_argument(
            "--county",
            help="Only include county",
            action="store",
            dest="search_county",
            required=False,
        )
        parser.add_argument(
            "--city",
            help="Only include city",
            action="store",
            dest="search_city",
            required=False,
        )
        parser.add_argument(
            "--country",
            help="Only include country",
            action="store",
            dest="search_country",
            required=False,
            default="US",
        )
        parser.add_argument(
            "--exclude_cities",
            help="Exclude cities",
            action="store_true",
            dest="exclude_cities",
            required=False,
            default=False,
        )
        parser.add_argument(
            "--json",
            help="JSON File",
            action="store",
            dest="json_data",
            required=False,
        )

    def collect_climate_zone_data(self):
        """Collect the county data"""
        with open(CLIMATE_ZONE_SOURCE) as f:
            data = f.readlines()

        doe_zones = dict(DOE_MOISTURE_REGIMES)

        results = []
        for item in data[1:]:
            (
                state_code,
                state_fips,
                county_fips,
                iecc_climate_zone,
                moisture_regime,
                building_america_cz,
                county_name,
            ) = item.split(",")
            moisture_regime = moisture_regime if moisture_regime != "N/A" else None
            county_fips = state_fips + county_fips

            doe_zone = f"{iecc_climate_zone}"
            if moisture_regime:
                dz = doe_zones.get(moisture_regime).lower()
                doe_zone += f"_{dz}"
            results.append(
                dict(
                    state_code=state_code,
                    state_fips=state_fips,
                    county_fips=county_fips,
                    zone=int(iecc_climate_zone),
                    moisture_regime=moisture_regime,
                    doe_zone=doe_zone,
                    building_america_climate_zone=building_america_cz,
                    county_name=county_name.strip(),
                )
            )
        return results

    def update_climate_data(self, data):
        """Update climate zone info"""
        created = 0
        for item in data:
            kwargs = {"zone": item["zone"], "moisture_regime": item["moisture_regime"]}
            try:
                obj, create = ClimateZone.objects.update_or_create(
                    **kwargs,
                    defaults=dict(doe_zone=item["doe_zone"], is_active=True),
                )
                created += 1 if create else 0
            except ClimateZone.MultipleObjectsReturned:
                objs = ClimateZone.objects.filter(**kwargs)
                objs.exclude(id=objs.first().id).delete()
        msg = "No climate zones added"
        if created:
            msg = f"Added {created} new climate_zones"
        log.info(msg)

    def collect_metro_data(self):
        """Import in metros"""

        results = {}

        with open(METRO_SOURCE, encoding="ISO-8859-1") as f:
            data = f.readlines()

        name = None
        for line in data:
            line = line.strip()
            if line == "":
                name = None
                continue

            m = re.match(r"(\d{5})\s{19}(.*)\s(Metropolitan Statistical Area)", line)
            if m:
                name = m.group(2)
                cbsa_code = m.group(1)
                results[cbsa_code] = dict(
                    name=name, cbsa_code=cbsa_code, county_fips=[], state_fips=[]
                )
                continue
            else:
                if name is None:
                    continue
                _cbsa = line[:5]
                try:
                    _county_fips = int(line[16:21])  # noqa: F841
                    county_fips = line[16:21]
                    state_fips = county_fips[:2]
                except ValueError:
                    # This is the sub metros
                    continue
                if county_fips not in results[_cbsa]["county_fips"]:
                    results[_cbsa]["county_fips"].append(county_fips)
                if state_fips not in results[_cbsa]["state_fips"]:
                    results[_cbsa]["state_fips"].append(state_fips)

        return list(results.values())

    def update_metro_data(self, data):
        """Update metro info"""
        created = 0
        for item in data:
            obj, create = Metro.objects.update_or_create(
                cbsa_code=item["cbsa_code"],
                defaults=dict(
                    name=item["name"],
                    is_active=True,
                ),
            )
            created += 1 if create else 0
        msg = "No metros added"
        if created:
            msg = f"Added {created} new metros"
        self.stdout.write(msg)

    def collect_county_data(self, state=None):
        """Import in the county data"""

        with open(COUNTY_SOURCE, encoding="UTF-8") as f:
            data = f.readlines()

        results = []
        for line in data[1:]:
            (
                state_code,
                county_fips,
                ansi_code,
                full_name,
                land_area_meters,
                water_area_meters,
                land_area,
                water_area,
                latitude,
                longitude,
            ) = line.strip().split("\t")

            if state and state != state_code:
                continue

            state_fips = county_fips[:2]
            name = full_name
            county_type = None
            m = re.search(
                r"(.*)(County|Parish|City|Borough|Municipality|Municipio|Census Area)",
                full_name,
                re.IGNORECASE,
            )
            if m:
                name = m.group(1).strip()
                county_type = next(
                    value for value, name in COUNTY_TYPES if name.lower() == m.group(2).lower()
                )

            results.append(
                dict(
                    county_name=name,
                    county_fips=county_fips,
                    ansi_code=ansi_code,
                    state_code=state_code,
                    state_fips=state_fips,
                    legal_statistical_area_description=full_name,
                    land_area_meters=land_area_meters,
                    water_area_meters=water_area_meters,
                    county_type=county_type,
                    latitude=latitude,
                    longitude=longitude,
                )
            )
        return results

    def update_county_data(self, data, climate_data, metro_data):
        """Update metro info"""
        created = 0
        founds = defaultdict(int)
        for item in data:
            county_fips = item["county_fips"]
            # print(f"County {county_fips} -> {item}")
            _climate_zone = next((x for x in climate_data if x["county_fips"] == county_fips))
            climate_zone = ClimateZone.objects.get(
                zone=_climate_zone["zone"], moisture_regime=_climate_zone["moisture_regime"]
            )

            metro = None
            _metro = next((x for x in metro_data if county_fips in x["county_fips"]), None)
            if _metro:
                metro = Metro.objects.get(cbsa_code=_metro["cbsa_code"])

            county = None
            counties = County.objects.filter(county_fips=item["county_fips"])
            if counties.count() == 1:
                county = counties.get()
                founds["level_1"] += 1
            elif counties.count() > 1:
                raise CommandError(f"We found two counties with same fips {item['county_fips']}?")
            elif counties.count() == 0:
                counties = County.objects.filter(ansi_code=item["ansi_code"])
                if counties.count() == 1:
                    county = counties.get()
                    founds["level_2"] += 1
                elif counties.count() > 1:
                    raise CommandError(f"We found two counties with same ansi {item['ansi_code']}?")
                elif counties.count() == 0:
                    _county = County.objects.create(
                        county_fips=item["county_fips"],
                        name=item["county_name"],
                        state=item["state_code"],
                        county_type=item["county_type"],
                        legal_statistical_area_description=item[
                            "legal_statistical_area_description"
                        ],
                        ansi_code=item["ansi_code"],
                        land_area_meters=item["land_area_meters"],
                        water_area_meters=item["water_area_meters"],
                        latitude=item["latitude"],
                        longitude=item["longitude"],
                        climate_zone=climate_zone,
                        metro=metro,
                    )
                    created += 1
            if county:
                _county, _update = County.objects.update_or_create(
                    id=county.id,
                    defaults=dict(
                        county_fips=item["county_fips"],
                        name=item["county_name"],
                        state=item["state_code"],
                        county_type=item["county_type"],
                        legal_statistical_area_description=item[
                            "legal_statistical_area_description"
                        ],
                        ansi_code=item["ansi_code"],
                        land_area_meters=item["land_area_meters"],
                        water_area_meters=item["water_area_meters"],
                        latitude=item["latitude"],
                        longitude=item["longitude"],
                        climate_zone=climate_zone,
                        metro=metro,
                    ),
                )

        msg = "No counties added"
        if created:
            msg = f"Added {created} new counties"
        self.stdout.write(f"County Founds: {len(founds)}")
        self.stdout.write(msg)

    def collect_city_data(self, state=None):
        """Collect official city data"""

        results = defaultdict(dict)
        with tempfile.TemporaryDirectory() as tempdir:
            file = zipfile.ZipFile(CENSUS_SOURCE)
            file.extractall(path=tempdir)

            files = glob.glob(tempdir + "/BlockAssign_ST[0-9]*_CDP.txt")
            if state:
                files = glob.glob(tempdir + f"/BlockAssign_ST[0-9]*_{state}_*_CDP.txt")

            if state is None or state not in TERRITORIES:
                assert len(files), "Bad glob pattern"
            # This gets block assignments which is effectively a map of places to counties.
            # Note: A place can exist in multiple counties..
            for file in files:
                with open(file) as file_obj:
                    data = file_obj.readlines()
                for line in data[1:]:
                    line = line.strip().split("|")
                    if not len(line):
                        continue
                    block_id, _place_fips = line
                    if not _place_fips:
                        continue
                    state_fips = block_id[:2]
                    county_fips = block_id[:5]
                    place_fips = state_fips + _place_fips
                    if place_fips not in results:
                        results[place_fips] = dict(
                            county_fips=[county_fips],
                            state_fips=state_fips,
                        )
                    elif county_fips not in results[place_fips]["county_fips"]:
                        results[place_fips]["county_fips"].append(county_fips)

            files = glob.glob(tempdir + "/NAMES_ST[0-9]*.txt")
            if state:
                files = glob.glob(tempdir + f"/NAMES_ST[0-9]*_{state}_*.txt")

            if state is None or state not in TERRITORIES:
                assert len(files) >= 1, "Bad glob pattern"

            # This gets fills in the official city names.
            for file in files:
                with open(file) as file_obj:
                    data = file_obj.readlines()
                for line in data[1:]:
                    line = line.strip().split("|")
                    if not len(line):
                        continue
                    try:
                        state_fips, _place_fips, name, namelsad = line
                    except ValueError:
                        print(f"Unable to Read {file}")
                        continue
                    place_fips = state_fips + _place_fips
                    results[place_fips].update(
                        dict(
                            city_name=name,
                            legal_statistical_area_description=namelsad,
                        )
                    )

        # This gets fill in a lot of associated data
        with open(CITY_SOURCE, encoding="UTF-8") as f:
            data = f.readlines()

        for line in data[1:]:
            (
                state_code,
                place_fips,
                ansi_code,
                city_name,
                _lsad,
                _funcstat,
                land_area_meters,
                water_area_meters,
                _land_area,
                _water_area,
                latitude,
                longitude,
            ) = line.strip().split("\t")

            if state and state != state_code:
                continue

            results[place_fips].update(
                dict(
                    place_fips=place_fips,
                    ansi_code=ansi_code,
                    state_code=state_code,
                    land_area_meters=land_area_meters,
                    water_area_meters=water_area_meters,
                    latitude=latitude,
                    longitude=longitude,
                )
            )

        return list(results.values())

    def collect_world_city_data(self, country=None, search_city=None):
        reverse_countries = {v.lower(): k for k, v in COUNTRIES.items()}
        reverse_countries.update(EXTENDED_COUNTRY_NAMES)

        skipped = []
        results = []
        with open(COUNTRY_CITY_SOURCE) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    intl_country = reverse_countries[row["country"].lower()]
                except KeyError:
                    if row["country"] not in skipped:
                        # self.stderr.write(f"Skipping {row['country']}")
                        skipped.append(row["country"])
                    continue
                if intl_country == country:
                    if search_city is None or search_city.lower() == row["name"].lower():
                        results.append(
                            {
                                "city_name": search_city or row["name"],
                                "country": intl_country,
                                "legal_statistical_area_description": row["name"],
                            }
                        )
        if search_city and not len(results):
            results.append({"city_name": search_city, "country": country})

        # Lets get some geodata
        final = []
        for result in results:
            kw = {"name__iexact": result["city_name"], "country__abbr": result["country"]}
            if City.objects.filter(**kw).exists():
                continue
            input_data = {
                "name": result["city_name"],
                "country": resolve_country(result["country"]).abbr,
            }
            serializer = GeocodeCityMatchesSerializer(data=input_data)
            serializer.is_valid(raise_exception=True)
            geo_obj, created = serializer.save()  # Our geocode object

            serializer = GeocodeCitySerializer(instance=geo_obj)
            results = serializer.data
            if len(results["valid_responses"]) == 1:
                input_data = results["valid_responses"][0]
                input_data["legal_statistical_area_description"] = input_data["name"]
                input_data["geocode_response"] = input_data.pop("id")

            final.append(input_data)
        return final

    def update_city_data(self, data, skip_missing_counties=False):
        founds = defaultdict(int)
        created = 0
        for item in data:
            for cnty in item["county_fips"]:
                # print(" ->", cnty, item)
                city = None
                try:
                    county = County.objects.get(county_fips=cnty)
                except County.DoesNotExist:
                    if skip_missing_counties:
                        continue
                    raise

                # Only consider the county if we absolutely have to.  This may have changed?
                kw = {"place_fips": item["place_fips"]}
                if len(item["county_fips"]) > 1:
                    kw["county"] = county

                cities = City.objects.filter(**kw)
                if cities.count() == 1:
                    city = cities.get()
                    founds["level_1"] += 1
                elif cities.count() > 1:
                    raise CommandError(f"We found two cities with same fips {item['place_fips']}?")
                elif cities.count() == 0:
                    cities = City.objects.filter(county=county, name__iexact=item["city_name"])
                    if cities.count() == 1:
                        city = cities.get()
                        founds["level_2"] += 1
                    elif cities.count() > 1:
                        raise CommandError(f"We found two cities with same county {county}?")
                    elif cities.count() == 0:
                        # print(f"New city {item}")
                        founds["no"] += 1
                        _city = City.objects.create(
                            name=item["city_name"],
                            county=county,
                            place_fips=item["place_fips"],
                            legal_statistical_area_description=item[
                                "legal_statistical_area_description"
                            ],
                            ansi_code=item["ansi_code"],
                            land_area_meters=item["land_area_meters"],
                            water_area_meters=item["water_area_meters"],
                            latitude=item["latitude"],
                            longitude=item["longitude"],
                            country=get_usa_default(),
                        )
                        created += 1
                if city:
                    _city, _update = City.objects.update_or_create(
                        id=city.id,
                        defaults=dict(
                            name=item["city_name"],
                            county=county,
                            place_fips=item["place_fips"],
                            legal_statistical_area_description=item[
                                "legal_statistical_area_description"
                            ],
                            ansi_code=item["ansi_code"],
                            land_area_meters=item["land_area_meters"],
                            water_area_meters=item["water_area_meters"],
                            latitude=item["latitude"],
                            longitude=item["longitude"],
                            country=get_usa_default(),
                        ),
                    )
        msg = "No cities added"
        if created:
            msg = f"Added {created} new cities"
        self.stdout.write(f"City Founds: {len(founds)}")
        self.stdout.write(msg)

    def update_intl_city_data(self, city_data):
        result = []
        for data in city_data:
            serializer = BaseCitySerializer(data=data)
            serializer.is_valid(raise_exception=True)
            obj = serializer.save()
            result.append(obj)
        return result

    def get_top_matches(self, data, search_name, data_name):
        matches = {}
        for obj in data:
            matches[obj[data_name]] = SequenceMatcher(
                lambda x: x == " ", search_name, obj[data_name]
            ).ratio()
        top_matches = sorted(matches, key=matches.get, reverse=True)[:5]
        return " * " + "\n * ".join(top_matches)

    def handle(self, *args, **options):
        if options["search_country"] == "US":
            if options["search_county"] and options["search_city"]:
                raise CommandError(
                    "For US you need to provide either a city && state OR county && state"
                )

            if options["search_county"] and not options["search_state"]:
                raise CommandError(
                    "For US you must provide a state if you are looking for a county"
                )

            if options["search_city"] and not options["search_state"]:
                raise CommandError("For US you must provide a state if you are looking for a city")
        else:
            if options["search_country"] not in COUNTRIES:
                raise CommandError(f"Country {options['search_county']} not found")
            if options["search_county"] or options["search_state"]:
                raise CommandError("For international cities state / county are not supported")

        if options["search_city"] and options["exclude_cities"]:
            raise CommandError("Obviously this won't work. search_city combined exclude_cities")

        self.stdout.write("Collecting input data")
        self.stdout.write("• Collecting Climate Zone data")
        climate_data = self.collect_climate_zone_data()
        if options["search_country"] == "US":
            self.stdout.write("• Collecting Metro data")
            metro_data = self.collect_metro_data()
            self.stdout.write("• Collecting County data")
            county_data = self.collect_county_data(state=options["search_state"])
            self.stdout.write("• Collecting City data")
            city_data = self.collect_city_data(state=options["search_state"])
            intl_city_data = []
        else:
            self.stdout.write("• Collecting International City data")
            intl_city_data = self.collect_world_city_data(
                country=options["search_country"], search_city=options["search_city"]
            )
            city_data = county_data = metro_data = climate_data = []

        # Now trim this up.  Note - we already have narrowed the city stuff down to the state level.
        skip_missing_counties = False
        if city_data and options["search_city"]:
            self.stdout.write("• Trimming to city")
            top_matches_pretty = self.get_top_matches(
                city_data, options["search_city"], "city_name"
            )

            city_data = [
                x for x in city_data if x["city_name"].lower() == options["search_city"].lower()
            ]

            if len(city_data) == 0:
                raise CommandError(
                    f"Unable to find city in {options['search_city']!r} "
                    f"in {options['search_state']} Possible matches:\n{top_matches_pretty}"
                )

            if len(city_data) > 1:
                raise CommandError(
                    f"Found multiple cities in {options['search_state']!r} "
                    f"with name {options['search_city']} Possible matches:\n{top_matches_pretty}"
                )

            county_fips = list(set([fip for city in city_data for fip in city["county_fips"]]))
            county_data = [x for x in county_data if x["county_fips"] in county_fips]

        if options["search_county"]:
            skip_missing_counties = True
            self.stdout.write("• Trimming to county")

            if options["search_state"]:
                county_data = [
                    x
                    for x in county_data
                    if x["state_code"].lower() == options["search_state"].lower()
                ]

            top_matches_pretty = self.get_top_matches(
                county_data, options["search_county"], "county_name"
            )

            _results = []

            cleaned_name = options["search_county"].lower()
            cleaned_name = re.sub(r"^st\s", "st. ", cleaned_name, re.IGNORECASE)
            cleaned_name = re.sub(r"^ste\s", "ste. ", cleaned_name, re.IGNORECASE)

            county_data = [
                x
                for x in county_data
                if x["county_name"].lower() == cleaned_name
                or x["legal_statistical_area_description"].lower() == cleaned_name
            ]

            in_args = f"in {options['search_state']} " if options["search_state"] else ""
            if len(city_data) == 0:
                raise CommandError(
                    f"Unable to find county {options['search_county']!r} {in_args} no matches"
                    f"Possible matches:\n{top_matches_pretty}"
                )

            # Note more than one (Fairfax VA) is acceptable

        county_fips = [x["county_fips"] for x in county_data]

        # Now let's Trimmed out
        city_data = [
            x for x in city_data if any(set(x["county_fips"]).intersection(set(county_fips)))
        ]
        metro_data = [
            x for x in metro_data if any(set(x["county_fips"]).intersection(set(county_fips)))
        ]
        climate_data = [x for x in climate_data if x["county_fips"] in county_fips]

        if options["update"]:
            self.stdout.write("• Updating Climate Zone Data")
            self.update_climate_data(climate_data)
            self.stdout.write("• Updating Metro Data")
            self.update_metro_data(metro_data)
            self.stdout.write("• Updating County Data")
            self.update_county_data(county_data, climate_data, metro_data)
            if options["exclude_cities"] is False:
                self.stdout.write("• Updating City Data")
                self.update_city_data(city_data, skip_missing_counties=skip_missing_counties)
                self.stdout.write("• Updating International City Data")
                self.update_intl_city_data(intl_city_data)

        if options["json_data"]:
            self.stdout.write("• Writing output")
            parsed_data = {
                "city_data": city_data,
                "county_data": county_data,
                "metro_data": metro_data,
                "climate_data": climate_data,
            }

            with open(options["json_data"], "w") as f:
                f.write("{}\n".format(json.dumps(parsed_data, indent=4)))

        return "All Done"
