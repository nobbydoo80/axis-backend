"""test_management.py - Axis"""
import json
import logging
import os

from django.core import management
from django.core.management import CommandError
from django.forms import model_to_dict
from django.test import TestCase

from axis.geographic.models import Metro, ClimateZone, County, City
from axis.geographic.tests.factories import real_city_factory

log = logging.getLogger(__name__)

__author__ = "Steven K"
__date__ = "6/1/21 16:17"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]


class GeographicManagementUpdateTigerDataTestCase(TestCase):
    """This will test out the update_tiger_data scripts"""

    output = "/tmp/output.json"

    def load_data(
        self,
        save_output=True,
        update=True,
        state_search=None,
        county_search=None,
        city_search=None,
        country_search=None,
        exclude_cities=False,
    ):
        args = [
            "update_base_geographic_data",
        ]
        if not update:
            args.append("--no_update")
        if state_search:
            args += ["--state", state_search]
        if county_search:
            args += ["--county", county_search]
        if city_search:
            args += ["--city", city_search]
        if country_search:
            args += ["--country", country_search]
        if exclude_cities:
            args.append("--exclude_cities")
        if save_output:
            args.append("--json")
            args.append(self.output)

        with open(os.devnull, "w") as stdout:
            management.call_command(
                *args,
                stdout=stdout,
                stderr=stdout,
            )

        if save_output:
            with open(self.output) as f:
                data = json.load(f)
            os.unlink(self.output)
            return data

    def build_assertions(self, data, label="data"):
        if isinstance(data, dict):
            for k, v in data.items():
                keyname = f'{label}["{k}"]'
                if isinstance(v, list):
                    keyname = f'set({label}["{k}"])'
                    v = set(v)
                print(f"self.assertEqual({keyname}, {v!r})")
        else:
            data = model_to_dict(data)
            for k, v in data.items():
                if v is None:
                    print(f"self.assertIsNone({label}.{k})")
                    continue
                if k.endswith("id") and isinstance(v, int):
                    print(f"self.assertIsNotNone({label}.{k})")
                    continue
                keyname = f"{label}.{k}"
                if isinstance(v, list):
                    keyname = f"set({label}.{k})"
                    v = set(v)
                print(f"self.assertEqual({keyname}, {v!r})")

    def test_read_climate_zone(self):
        """Test out our climate zones"""
        data = self.load_data(update=False, state_search="OR")
        climate = next((x for x in data["climate_data"] if x["county_fips"] == "41069"))
        self.assertEqual(climate["state_code"], "OR")
        self.assertEqual(climate["state_fips"], "41")
        self.assertEqual(climate["county_fips"], "41069")
        self.assertEqual(climate["zone"], 5)
        self.assertEqual(climate["moisture_regime"], "B")
        self.assertEqual(climate["doe_zone"], "5_dry")
        self.assertEqual(climate["building_america_climate_zone"], "Cold")
        self.assertEqual(climate["county_name"], "Wheeler")

    def test_read_climate_zone_na(self):
        """Test out our climate zones"""
        data = self.load_data(update=False, state_search="WI")
        climate = next((x for x in data["climate_data"] if x["county_fips"] == "55003"))
        self.assertEqual(climate["state_code"], "WI")
        self.assertEqual(climate["state_fips"], "55")
        self.assertEqual(climate["county_fips"], "55003")
        self.assertEqual(climate["zone"], 7)
        self.assertEqual(climate["moisture_regime"], None)
        self.assertEqual(climate["doe_zone"], "7")
        self.assertEqual(climate["building_america_climate_zone"], "Very Cold")
        self.assertEqual(climate["county_name"], "Ashland")

    def test_metro_read(self):
        """Test out our Metros - Minneapolis Metro contains two states"""
        data = self.load_data(update=False, state_search="MN")
        metro = next((x for x in data["metro_data"] if x["cbsa_code"] == "33460"))
        self.assertEqual(metro["name"], "Minneapolis-St. Paul-Bloomington, MN-WI")
        self.assertEqual(metro["cbsa_code"], "33460")
        self.assertEqual(
            set(metro["county_fips"]),
            {
                "27025",
                "27123",
                "27171",
                "27037",
                "27139",
                "55093",
                "27019",
                "27163",
                "55109",
                "27059",
                "27053",
                "27003",
                "27141",
            },
        )
        self.assertEqual(set(metro["state_fips"]), {"27", "55"})

    def test_county_read(self):
        """Test out our Counties - Special encoding"""
        data = self.load_data(update=False, state_search="PR")
        county = next((x for x in data["county_data"] if x["county_fips"] == "72033"))

        self.assertEqual(county["county_name"], "Cataño")
        self.assertEqual(county["county_fips"], "72033")
        self.assertEqual(county["ansi_code"], "01804496")
        self.assertEqual(county["state_code"], "PR")
        self.assertEqual(county["state_fips"], "72")
        self.assertEqual(county["legal_statistical_area_description"], "Cataño Municipio")
        self.assertEqual(county["land_area_meters"], "12515561")
        self.assertEqual(county["water_area_meters"], "5615090")
        self.assertEqual(county["county_type"], "6")
        self.assertEqual(county["latitude"], "18.444614")
        self.assertEqual(county["longitude"], "-66.148819")

    def test_city_read(self):
        """Test out our City - Spans two counties"""
        data = self.load_data(update=False, state_search="WI", city_search="Watertown")
        city = next((x for x in data["city_data"] if x["city_name"] == "Watertown"))

        self.assertEqual(set(city["county_fips"]), {"55055", "55027"})
        self.assertEqual(city["state_fips"], "55")
        self.assertEqual(city["city_name"], "Watertown")
        self.assertEqual(city["legal_statistical_area_description"], "Watertown city")
        self.assertEqual(city["ansi_code"], "01584365")
        self.assertEqual(city["state_code"], "WI")
        self.assertEqual(city["land_area_meters"], "31245697")
        self.assertEqual(city["water_area_meters"], "1035660")
        self.assertEqual(city["latitude"], "43.189405")
        self.assertEqual(city["longitude"], "-88.72891")

    def test_city_read_encoding(self):
        """Test out our City - Encoding"""
        data = self.load_data(update=False, state_search="PR", city_search="búfaLO")
        city = next((x for x in data["city_data"] if x["ansi_code"] == "02415314"))

        self.assertEqual(set(city["county_fips"]), {"72017"})
        self.assertEqual(city["state_fips"], "72")
        self.assertEqual(city["city_name"], "Búfalo")
        self.assertEqual(city["legal_statistical_area_description"], "Búfalo comunidad")
        self.assertEqual(city["ansi_code"], "02415314")
        self.assertEqual(city["state_code"], "PR")
        self.assertEqual(city["land_area_meters"], "618072")
        self.assertEqual(city["water_area_meters"], "0")
        self.assertEqual(city["latitude"], "18.416531")
        self.assertEqual(city["longitude"], "-66.57501")

    def test_create_encoding(self):
        """Test our create process - This is unique in that all names have encoding"""
        data = self.load_data(update=True, state_search="PR", city_search="Mayagüez")
        self.assertEqual(len(data["metro_data"]), 1)
        self.assertEqual(len(data["county_data"]), 1)
        self.assertEqual(len(data["city_data"]), 1)
        self.assertEqual(len(data["climate_data"]), 1)

        self.assertEqual(Metro.objects.count(), 1)

        metro = Metro.objects.get()
        self.assertIsNotNone(metro.id)
        self.assertEqual(metro.name, "Mayagüez, PR")
        self.assertEqual(metro.cbsa_code, "32420")
        self.assertEqual(metro.is_active, True)

        self.assertEqual(ClimateZone.objects.count(), 1)
        climate_zone = ClimateZone.objects.get()
        self.assertIsNotNone(climate_zone.id)
        self.assertEqual(climate_zone.zone, 1)
        self.assertEqual(climate_zone.moisture_regime, "A")
        self.assertEqual(climate_zone.doe_zone, "1_moist")
        self.assertEqual(climate_zone.is_active, True)

        self.assertEqual(County.objects.count(), 1)
        county = County.objects.get()
        self.assertIsNotNone(county.id)
        self.assertEqual(county.name, "Mayagüez")
        self.assertEqual(county.state, "PR")
        self.assertEqual(county.county_fips, "72097")
        self.assertEqual(county.county_type, "6")
        self.assertEqual(county.legal_statistical_area_description, "Mayagüez Municipio")
        self.assertEqual(county.ansi_code, "01804529")
        self.assertEqual(county.land_area_meters, 201174435)
        self.assertEqual(county.water_area_meters, 508705765)
        self.assertEqual(county.latitude, 18.08385)
        self.assertEqual(county.longitude, -67.886337)
        self.assertIsNotNone(county.metro)
        self.assertIsNotNone(county.climate_zone)

        self.assertEqual(City.objects.count(), 1)
        city = City.objects.get()
        self.assertIsNotNone(city.id)
        self.assertEqual(city.name, "Mayagüez")
        self.assertIsNotNone(city.county)
        self.assertEqual(city.place_fips, "7252431")
        self.assertEqual(city.legal_statistical_area_description, "Mayagüez zona urbana")
        self.assertEqual(city.ansi_code, "02414879")
        self.assertEqual(city.land_area_meters, 54344580)
        self.assertEqual(city.water_area_meters, 5621232)
        self.assertEqual(city.latitude, 18.201221)
        self.assertEqual(city.longitude, -67.14178)

    def test_create_no_metro(self):
        """Test our create process No Metro cz moisture is None"""
        data = self.load_data(update=True, state_search="WI", city_search="Lac du Flambeau")
        self.assertEqual(len(data["metro_data"]), 0)
        self.assertEqual(len(data["county_data"]), 1)
        self.assertEqual(len(data["city_data"]), 1)
        self.assertEqual(len(data["climate_data"]), 1)

        self.assertEqual(ClimateZone.objects.count(), 1)
        climate_zone = ClimateZone.objects.get()
        self.assertIsNotNone(climate_zone.id)
        self.assertEqual(climate_zone.zone, 7)
        self.assertIsNone(climate_zone.moisture_regime)
        self.assertEqual(climate_zone.doe_zone, "7")
        self.assertEqual(climate_zone.is_active, True)

        self.assertEqual(Metro.objects.count(), 0)

        self.assertEqual(County.objects.count(), 1)
        county = County.objects.get()
        self.assertIsNotNone(county.id)
        self.assertEqual(county.name, "Vilas")
        self.assertEqual(county.state, "WI")
        self.assertEqual(county.county_fips, "55125")
        self.assertEqual(county.county_type, "1")
        self.assertEqual(county.legal_statistical_area_description, "Vilas County")
        self.assertEqual(county.ansi_code, "01581122")
        self.assertEqual(county.land_area_meters, 2221455734)
        self.assertEqual(county.water_area_meters, 414418148)
        self.assertEqual(county.latitude, 46.049848)
        self.assertEqual(county.longitude, -89.501254)
        self.assertIsNone(county.metro)
        self.assertIsNotNone(county.climate_zone)

        self.assertEqual(City.objects.count(), 1)
        city = City.objects.get()
        self.assertIsNotNone(city.id)
        self.assertEqual(city.name, "Lac du Flambeau")
        self.assertIsNotNone(city.county)
        self.assertEqual(city.place_fips, "5540675")
        self.assertEqual(city.legal_statistical_area_description, "Lac du Flambeau CDP")
        self.assertEqual(city.ansi_code, "02393075")
        self.assertEqual(city.land_area_meters, 12814147)
        self.assertEqual(city.water_area_meters, 7312201)
        self.assertEqual(city.latitude, 45.962279)
        self.assertEqual(city.longitude, -89.896865)

    def test_territories(self):
        """We should be able to add in the counties and cliamte zones"""
        data = self.load_data(update=True, state_search="VI")
        self.assertEqual(len(data["climate_data"]), 3)
        self.assertEqual(ClimateZone.objects.count(), 1)
        self.assertEqual(len(data["metro_data"]), 0)
        self.assertEqual(Metro.objects.count(), 0)
        self.assertEqual(len(data["county_data"]), 3)
        self.assertEqual(County.objects.count(), 3)
        self.assertEqual(len(data["city_data"]), 0)
        self.assertEqual(City.objects.count(), 0)

    def test_metro_update(self):
        """Test out the metro data"""
        self.load_data(update=True, state_search="PR", city_search="San Germán")

        metro = Metro.objects.get()
        self.assertEqual(metro.name, "San Germán-Cabo Rojo, PR")
        metro.name = "foobar"
        metro.save()

        self.load_data(update=True, state_search="PR", city_search="San Germán")
        metro = Metro.objects.get()
        self.assertEqual(metro.name, "San Germán-Cabo Rojo, PR")

    def test_county_level_1_update(self):
        """ "This will update counties"""
        self.load_data(update=True, state_search="WI", city_search="Watertown")

        self.assertEqual(ClimateZone.objects.count(), 1)
        self.assertEqual(Metro.objects.count(), 0)

        self.assertEqual(County.objects.count(), 2)
        county = County.objects.first()
        self.assertEqual(county.name, "Dodge")
        self.assertEqual(county.state, "WI")
        self.assertEqual(county.county_fips, "55027")
        self.assertEqual(county.county_type, "1")

        # Keep Fips / Change ANSI
        county.name = "Dunder Miflin"
        county.state = "AK"
        county.legal_statistical_area_description = "FOO"
        county.ansi_code = "BAR"
        county.save()

        self.assertEqual(City.objects.count(), 2)

        self.load_data(update=True, state_search="WI", city_search="Watertown")
        self.assertEqual(ClimateZone.objects.count(), 1)
        self.assertEqual(Metro.objects.count(), 0)
        self.assertEqual(County.objects.count(), 2)
        county = County.objects.first()
        self.assertIsNotNone(county.id)
        self.assertEqual(county.name, "Dodge")
        self.assertEqual(county.state, "WI")
        self.assertEqual(county.county_fips, "55027")
        self.assertEqual(county.county_type, "1")
        self.assertEqual(county.legal_statistical_area_description, "Dodge County")
        self.assertEqual(county.ansi_code, "01581073")
        self.assertEqual(county.land_area_meters, 2268049732)
        self.assertEqual(county.water_area_meters, 81331401)
        self.assertEqual(county.latitude, 43.429628)
        self.assertEqual(county.longitude, -88.701939)
        self.assertIsNone(county.metro)
        self.assertIsNotNone(county.climate_zone)

        self.assertEqual(City.objects.count(), 2)

    def test_county_level_2_update(self):
        """ "This will update counties"""
        self.load_data(update=True, state_search="WI", city_search="Watertown")

        self.assertEqual(ClimateZone.objects.count(), 1)
        self.assertEqual(Metro.objects.count(), 0)

        self.assertEqual(County.objects.count(), 2)
        county = County.objects.first()
        self.assertEqual(county.name, "Dodge")
        self.assertEqual(county.state, "WI")
        self.assertEqual(county.county_fips, "55027")
        self.assertEqual(county.county_type, "1")

        # Keep ANSI / Change FIPS
        county.name = "Dunder Miflin"
        county.county_fips = "1232"
        county.state = "AK"
        county.legal_statistical_area_description = "FOO"
        county.save()

        self.assertEqual(City.objects.count(), 2)

        self.load_data(update=True, state_search="WI", city_search="Watertown")
        self.assertEqual(ClimateZone.objects.count(), 1)
        self.assertEqual(Metro.objects.count(), 0)
        self.assertEqual(County.objects.count(), 2)
        county = County.objects.first()
        self.assertIsNotNone(county.id)
        self.assertEqual(county.name, "Dodge")
        self.assertEqual(county.state, "WI")
        self.assertEqual(county.county_fips, "55027")
        self.assertEqual(county.county_type, "1")
        self.assertEqual(county.legal_statistical_area_description, "Dodge County")
        self.assertEqual(county.ansi_code, "01581073")
        self.assertEqual(county.land_area_meters, 2268049732)
        self.assertEqual(county.water_area_meters, 81331401)
        self.assertEqual(county.latitude, 43.429628)
        self.assertEqual(county.longitude, -88.701939)
        self.assertIsNone(county.metro)
        self.assertIsNotNone(county.climate_zone)

        self.assertEqual(City.objects.count(), 2)

    def test_city_level1_update(self):
        """ "This will update city level one means that the place fips hasn't changed we are
        allowed to change everything else"""
        self.load_data(update=True, state_search="FL", city_search="Panama City")

        self.assertEqual(ClimateZone.objects.count(), 1)
        self.assertEqual(Metro.objects.count(), 1)
        self.assertEqual(County.objects.count(), 1)
        self.assertEqual(City.objects.count(), 1)
        city = City.objects.get()

        self.assertIsNotNone(city.id)
        self.assertEqual(city.name, "Panama City")
        city.name = "FOOBAR"
        self.assertEqual(city.place_fips, "1254700")
        self.assertEqual(city.legal_statistical_area_description, "Panama City city")
        city.legal_statistical_area_description = "FOOBAR"
        self.assertEqual(city.ansi_code, "02404468")
        city.ansi_code = "xxx"
        self.assertEqual(city.land_area_meters, 90911120)
        city.land_area_meters = 12
        self.assertEqual(city.water_area_meters, 15928864)
        city.water_area_meters = 32
        self.assertEqual(city.latitude, 30.166271)
        city.latitude = 32.2
        self.assertEqual(city.longitude, -85.670191)
        city.longitude = -32.2
        city.save()

        self.load_data(update=True, state_search="FL", city_search="Panama City")
        self.assertEqual(ClimateZone.objects.count(), 1)
        self.assertEqual(Metro.objects.count(), 1)
        self.assertEqual(County.objects.count(), 1)
        self.assertEqual(City.objects.count(), 1)
        city = City.objects.get()

        self.assertIsNotNone(city.id)
        self.assertEqual(city.name, "Panama City")
        self.assertIsNotNone(city.county)
        self.assertEqual(city.place_fips, "1254700")
        self.assertEqual(city.legal_statistical_area_description, "Panama City city")
        self.assertEqual(city.ansi_code, "02404468")
        self.assertEqual(city.land_area_meters, 90911120)
        self.assertEqual(city.water_area_meters, 15928864)
        self.assertEqual(city.latitude, 30.166271)
        self.assertEqual(city.longitude, -85.670191)

    def test_city_level2_update(self):
        """ "This will update city level two implies we came along before this ran and manually
        created a city"""

        self.load_data(update=True, state_search="AZ", city_search="Peoria")

        self.assertEqual(ClimateZone.objects.count(), 2)
        self.assertEqual(Metro.objects.count(), 2)
        self.assertEqual(County.objects.count(), 2)
        self.assertEqual(City.objects.count(), 2)

        # Roll back the one to what is is like on prod
        self.assertTrue(City.objects.filter(name="Peoria", county__name="Maricopa").exists())
        City.objects.filter(name="Peoria", county__name="Maricopa").update(
            place_fips="9900000",
            legal_statistical_area_description="Unregistered Peoria (9900000)",
            ansi_code="9900000",
            land_area_meters=0,
            water_area_meters=0,
            latitude=0.0,
            longitude=0.0,
        )

        self.assertTrue(City.objects.filter(place_fips="9900000").exists())
        self.load_data(update=True, state_search="AZ", city_search="Peoria")

        self.assertEqual(ClimateZone.objects.count(), 2)
        self.assertEqual(Metro.objects.count(), 2)
        self.assertEqual(County.objects.count(), 2)
        self.assertEqual(City.objects.count(), 2)

        city = City.objects.get(name="Peoria", county__name="Maricopa")
        self.assertIsNotNone(city.id)
        self.assertEqual(city.name, "Peoria")
        self.assertEqual(city.county.name, "Maricopa")
        self.assertEqual(city.place_fips, "0454050")
        self.assertEqual(city.legal_statistical_area_description, "Peoria city")
        self.assertEqual(city.ansi_code, "02411401")
        self.assertEqual(city.land_area_meters, 456049509)
        self.assertEqual(city.water_area_meters, 8199012)
        self.assertEqual(city.latitude, 33.786186)
        self.assertEqual(city.longitude, -112.308042)

    def test_full(self):
        """Just test out everything"""
        self.load_data(update=True)

        self.assertEqual(ClimateZone.objects.count(), 15)
        self.assertEqual(Metro.objects.count(), 374)
        self.assertEqual(County.objects.count(), 3224)
        self.assertEqual(City.objects.count(), 33334)

    def test_county_only(self):
        self.load_data(
            update=True, county_search="maricopa", state_search="AZ", exclude_cities=True
        )
        self.assertEqual(ClimateZone.objects.count(), 1)
        self.assertEqual(Metro.objects.count(), 1)
        self.assertEqual(County.objects.count(), 1)
        self.assertEqual(City.objects.count(), 0)

    def test_bad_country(self):
        self.assertRaises(CommandError, self.load_data, country_search="XXX")
        self.assertRaises(CommandError, self.load_data, country_search="DO", state_search="AZ")

    def test_load_country(self):
        self.load_data(update=True, country_search="VI")
        self.assertEqual(ClimateZone.objects.count(), 0)
        self.assertEqual(Metro.objects.count(), 0)
        self.assertEqual(County.objects.count(), 0)
        self.assertEqual(City.objects.count(), 2)

    def test_add_unlisted_city(self):
        self.load_data(update=True, country_search="DO", city_search="Basima")
        self.assertEqual(ClimateZone.objects.count(), 0)
        self.assertEqual(Metro.objects.count(), 0)
        self.assertEqual(County.objects.count(), 0)
        self.assertEqual(City.objects.count(), 1)

    def test_intl_factory(self):
        obj = real_city_factory("Charlotte Amalie", country="VI")
        self.assertEqual(obj.name, "Charlotte Amalie")
        self.assertEqual(obj.county, None)
        self.assertEqual(obj.country.abbr, "VI")
        self.assertEqual(obj.place_fips, "9900000")
        self.assertEqual(obj.legal_statistical_area_description, "Charlotte Amalie")
        self.assertEqual(obj.ansi_code, "9900000")
        self.assertEqual(obj.land_area_meters, 0)
        self.assertEqual(obj.water_area_meters, 0)
        self.assertEqual(obj.latitude, 18.3419004)
        self.assertEqual(obj.longitude, -64.9307007)
        self.assertIsNotNone(obj.geocode_response)
