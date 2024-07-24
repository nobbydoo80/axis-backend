"""reso.py: Django RESO.data_models"""


import logging

import re

from django.conf import settings
from django.utils.text import slugify
from lxml import etree

from axis.remrate_data.strings import COOLING_TYPES, HEATER_TYPES

try:
    from . import DataModel, ResoJsonMixin, ResoXmlMixin
except ValueError:
    from axis.reso.RESO.data_models import DataModel, ResoJsonMixin, ResoXmlMixin

__author__ = "Steven Klass"
__date__ = "06/16/17 09:42"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)

CAP_CITIES_COUNTY = 5
# if settings.DEBUG:
#     CAP_CITIES_COUNTY = 5


class RESOEDMXBase(ResoXmlMixin):
    @property
    def schema(self):
        if not hasattr(self, "_schema"):
            EDM_MAP = {None: "http://docs.oasis-open.org/odata/ns/edm"}
            self._schema = etree.Element("Schema", Namespace="ODataService", nsmap=EDM_MAP)
        return self._schema

    @property
    def property(self):
        root = etree.Element("Entitytype", Name="Property")

        key = etree.Element("Key")
        key.append(etree.Element("PropertyRef", name="ListingKeyNumeric"))
        root.append(key)

        # HERE IS WHERE WE ADD OUR STUFF FROM THE DATA DICTIONARY - TRY TO KEEP THE ORDER IN ALPHA
        root.append(
            self.element_with_text(
                "property", None, Name="ListingKeyNumeric", Type="Edm.Int64", Nullable="false"
            )
        )
        root.append(
            self.element_with_text(
                "property",
                None,
                Name="AboveGradeFinishedArea",
                Type="Edm.Decimal",
                Precision="13",
                Scale="2",
            )
        )
        root.append(
            self.element_with_text(
                "property", None, Name="AboveGradeFinishedAreaSource", Type="Edm.String"
            )
        )
        root.append(
            self.element_with_text(
                "property",
                None,
                Name="AboveGradeFinishedAreaUnits",
                Type="OData.Models.AreaUnitType",
            )
        )
        # root.append(self.element_with_text("property", None, Name="BedroomsTotal", Type="Edm.Int32"))
        # root.append(self.element_with_text("property", None, Name="BelowGradeFinishedArea", Type="Edm.Decimal"))
        # root.append(self.element_with_text("property", None, Name="BelowGradeFinishedAreaSource", Type="Edm.String"))
        # root.append(self.element_with_text("property", None, Name="BelowGradeFinishedAreaUnits", Type="OData.Models.AreaUnitType"))
        # root.append(self.element_with_text("property", None, Name="BuilderModel", Type="Edm.String"))
        # root.append(self.element_with_text("property", None, Name="BuilderModelCode", Type="Edm.String"))
        # root.append(self.element_with_text("property", None, Name="BuilderName", Type="Edm.String"))
        # root.append(self.element_with_text("property", None, Name="BuildingAreaTotal", Type="Edm.Decimal"))
        # root.append(self.element_with_text("property", None, Name="BuildingAreaUnits", Type="OData.Models.AreaUnitType"))
        # root.append(self.element_with_text("property", None, Name="City", Type="OData.Models.City"))
        # root.append(self.element_with_text("property", None, Name="Cooling", Type="OData.Models.Cooling_Flags"))
        # root.append(self.element_with_text("property", None, Name="CoolingYN", Type="Edm.Boolean"))
        # root.append(self.element_with_text("property", None, Name="CountyOrParish", Type="OData.Models.County"))
        # root.append(self.element_with_text("property", None, Name="Electric", Type="OData.Models.Electric_Flags"))
        # root.append(self.element_with_text("property", None, Name="ElectricExpense", Type="Edm.Decimal"))
        # root.append(self.element_with_text("property", None, Name="Elevation", Type="Edm.Decimal"))
        # root.append(self.element_with_text("property", None, Name="ElevationUnits", Type="Edm.Decimal"))
        # root.append(self.element_with_text("property", None, Name="FoundationArea", Type="Edm.Decimal"))
        # root.append(self.element_with_text("property", None, Name="FoundationAreaUnits", Type="Edm.Decimal"))  #Note this isn't in the standard??
        # # root.append(self.element_with_text("property", None, Name="Gas", Type="OData.Models.Gas_Flags"))
        # root.append(self.element_with_text("property", None, Name="GasExpense", Type="Edm.Decimal"))  # Note this isn't in the standard but is in CRMLS Example?
        # root.append(self.element_with_text("property", None, Name="GreenBuildingVerificationType", Type="OData.Models.GreenBuildingVerificationType_Flags"))
        # root.append(self.element_with_text("property", None, Name="GreenEnergyEfficient", Type="OData.Models.GreenEnergyEfficient_Flags"))
        # root.append(self.element_with_text("property", None, Name="GreenEnergyGeneration", Type="OData.Models.GreenEnergyGeneration_Flags"))
        # root.append(self.element_with_text("property", None, Name="GreenIndoorAirQuality", Type="OData.Models.GreenIndoorAirQuality_Flags"))
        # root.append(self.element_with_text("property", None, Name="GreenWaterConservation", Type="OData.Models.GreenWaterConservation_Flags"))
        # root.append(self.element_with_text("property", None, Name="Heating", Type="OData.Models.Heating_Flags"))
        # root.append(self.element_with_text("property", None, Name="HeatingYN", Type="Edm.Boolean"))
        # root.append(self.element_with_text("property", None, Name="Latitude", Type="Edm.Decimal"))
        # root.append(self.element_with_text("property", None, Name="Longitude", Type="Edm.Decimal"))
        # root.append(self.element_with_text("property", None, Name="NewConstructionYN", Type="Edm.Boolean"))
        # root.append(self.element_with_text("property", None, Name="PostalCode", Type="Edm.String"))
        # root.append(self.element_with_text("property", None, Name="PropertyType", Type="Edm.String"))
        # root.append(self.element_with_text("property", None, Name="StateOrProvince", Type="OData.Models.StateOrProvince_Flags"))
        # root.append(self.element_with_text("property", None, Name="Stories", Type="Edm.Int32"))
        # root.append(self.element_with_text("property", None, Name="SubdivisionName", Type="Edm.String"))
        # root.append(self.element_with_text("property", None, Name="Utilities", Type="OData.Models.Utilities_Flags"))
        # root.append(self.element_with_text("property", None, Name="YearBuilt", Type="Edm.Int32"))
        # root.append(self.element_with_text("property", None, Name="YearBuiltSource", Type="OData.Models.YearBuiltSource_Flags"))

        # root.append(self.element_with_text("navigationproperty", None, Name="PropertyGreen", Type="Collection(OData.Models.PropertyGreen)", containstarget="true"))
        # root.append(self.element_with_text("navigationproperty", None, Name="PowerProduction", Type="Collection(OData.Models.PowerProduction)", containstarget="true"))

        return root

    def property_green(self):
        root = etree.Element("entitytype", name="Property")

        key = etree.Element("key")
        key.append(etree.Element("propertyref", name="GreenKey"))
        root.append(key)

        for item in [
            self.element_with_text(
                "property", None, name="GreenKey", type="Edm.Int64", nullable="false"
            ),
            self.element_with_text(
                "property",
                None,
                name="GreenBuildingVerificationType",
                type="OData.Models.GreenBuildingCertification",
            ),
            self.element_with_text(
                "property",
                None,
                name="GreenVerificationSource",
                type="OData.Models.GreenVerificationSource_Flags",
            ),
            self.element_with_text(
                "property", None, name="GreenVerificationBody", type="Edm.String"
            ),
            self.element_with_text(
                "property", None, name="GreenVerificationMetric", type="Edm.String"
            ),
            self.element_with_text(
                "property", None, name="GreenVerificationRating", type="Edm.String"
            ),
            self.element_with_text(
                "property", None, name="GreenVerificationStatus", type="Edm.String"
            ),
            self.element_with_text(
                "property", None, name="GreenVerificationURL", type="Edm.String"
            ),
            self.element_with_text(
                "property", None, name="GreenVerificationVersion", type="Edm.String"
            ),
            self.element_with_text(
                "property", None, name="GreenVerificationYear", type="Edm.String"
            ),
        ]:
            root.append(item)

        return root

    def power_production(self):
        root = etree.Element("entitytype", name="Property")

        key = etree.Element("key")
        key.append(etree.Element("propertyref", name="PowerProduction"))
        root.append(key)

        for item in [
            self.element_with_text(
                "property", None, name="PowerProductionKey", type="Edm.Int64", nullable="false"
            ),
            self.element_with_text(
                "property",
                None,
                name="PowerProductionType",
                type="OData.Models.PowerProductionType_Flags",
            ),
            self.element_with_text(
                "property", None, name="PowerProductionAnnualStatus", type="Edm.String"
            ),
            self.element_with_text("property", None, name="PowerProductionSize", type="Edm.String"),
            self.element_with_text(
                "property", None, name="PowerProductionYearInstall", type="Edm.String"
            ),
        ]:
            root.append(item)

        return root

    # @property
    def build_generic_enum(self, root_label, data):
        root = etree.Element("enumtype", name=root_label, isflags="true")

        def get_contorted_name(text):
            if re.search(r"^\d", text):
                text = "_" + text
            text = re.sub(r"-", "_", text)
            text = re.sub(r"\/", "_", text)
            text = re.sub(r"\+", "_", text)
            text = re.sub(r" ", "_", text)
            text = re.sub(r"_+", "_", text)
            return text

        for idx, item in enumerate(data, start=1):
            member_label = get_contorted_name(item)
            member = etree.Element("member", name="{}".format(member_label), value="{}".format(idx))
            if member_label != item:
                annotation = etree.Element(
                    "annotation", term="RESO.OData.Metadata.StandardName", string="{}".format(item)
                )
                member.append(annotation)
            root.append(member)
        return root

    def area_unit_type(self):
        data = """Square Feet
        Square Meters
        """
        return self.build_generic_enum("AreaUnitType", [x.strip() for x in data.split("\n")])

    def city_data(self):
        root = etree.Element("enumtype", name="City")
        from axis.geographic.models import City

        cities = City.objects.filter(county__state__in=["AZ", "NC", "GA", "WA", "OR", "ID", "MT"])
        if CAP_CITIES_COUNTY:
            cities = cities[:CAP_CITIES_COUNTY]

        for city in cities:
            city_name = f"{slugify(str(city))}"
            member = etree.Element("member", name=city_name, value="{}".format(city.id))
            annotation = etree.Element(
                "annotation", term="RESO.OData.Metadata.StandardName", string="{}".format(city.name)
            )
            member.append(annotation)
            root.append(member)
        return root

    def cooling_flags(self):
        return self.build_generic_enum("Cooling_Flags", [x[1] for x in COOLING_TYPES[:-1]])

    def county_data(self):
        root = etree.Element("enumtype", name="CountyOrParish")
        from axis.geographic.models import County

        counties = County.objects.filter(state__in=["AZ", "NC", "GA", "WA", "OR", "ID", "MT"])
        if CAP_CITIES_COUNTY:
            counties = counties[:CAP_CITIES_COUNTY]

        for county in counties:
            city_name = "{}_{}".format(slugify(county.name), county.state)
            member = etree.Element("member", name=city_name, value="{}".format(county.id))
            annotation = etree.Element(
                "annotation",
                term="RESO.OData.Metadata.StandardName",
                string="{}".format(county.name),
            )
            member.append(annotation)
            root.append(member)
        return root

    def electric_flags(self):
        data = """Energy Storage Device
            Generator
            Net Meter
            Photovoltaics Seller Owned
            Pre-Wired for Renewables"""
        return self.build_generic_enum("Electric_Flags", [x.strip() for x in data.split("\n")])

    def green_building_verification_flags(self):
        data = """Certified Passive House
        ENERGY STAR Certified Homes
        EnerPHit
        HERS Index Score
        Home Energy Score
        Home Energy Upgrade Certificate of Energy Efficiency Improvements
        Home Energy Upgrade Certificate of Energy Efficiency Performance
        Home Performance with ENERGY STAR
        Indoor airPLUS
        LEED For Homes
        Living Building Challenge
        NGBS New Construction
        NGBS Small Projects Remodel
        NGBS Whole-Home Remodel
        PHIUS+
        WaterSense
        Zero Energy Ready Home""".split(
            "\n"
        )

        return self.build_generic_enum("GreenBuildingCertification", [x.strip() for x in data])

    def green_verification_source(self):
        data = """Administrator
          Assessor
          Builder
          Contractor or Installer
          Other
          Owner
          Program Sponsor
          Program Verifier
          Public Records
          See Remarks"""
        return self.build_generic_enum(
            "GreenVerificationSource_Flags", [x.strip() for x in data.split("\n")]
        )

    def green_efficient_flags(self):
        data = """Appliances
         Construction
         Doors
         Exposure/Shade
         HVAC
         Incentives
         Insulation
         Lighting
         Roof
         Thermostat
         Water Heater
         Windows"""

        return self.build_generic_enum(
            "GreenEnergyEfficient_Flags", [x.strip() for x in data.split("\n")]
        )

    def green_energy_generation_flags(self):
        data = """Solar"""
        return self.build_generic_enum("GreenEnergyGeneration_Flags", [data])

    def green_indoor_air_quality_flags(self):
        data = """Contaminant Control
            Moisture Control
            Ventilation"""
        return self.build_generic_enum(
            "GreenIndoorAirQuality_Flags", [x.strip() for x in data.split("\n")]
        )

    def green_water_conservation(self):
        data = """Efficient Hot Water Distribution
         Low-Flow Fixtures"""
        return self.build_generic_enum(
            "GreenWaterConservation_Flags", [x.strip() for x in data.split("\n")]
        )

    def heating_flags(self):
        return self.build_generic_enum("Heating_Flags", [x[1] for x in HEATER_TYPES[:-1]])

    def power_production_flags(self):
        data = """Estimated"""
        return self.build_generic_enum(
            "PowerProductionAnnualStatus_Flags", [x.strip() for x in data.split("\n")]
        )

    def power_production_type_flags(self):
        data = """Photovoltaics"""
        return self.build_generic_enum(
            "PowerProductionType_Flags", [x.strip() for x in data.split("\n")]
        )

    def us_states(self):
        from localflavor.us.us_states import US_STATES

        return self.build_generic_enum("StateOrProvince_Flags", [x[0] for x in US_STATES])

    def utilites(self):
        data = """Electricity Connected
         Natural Gas Available
         Propane"""
        return self.build_generic_enum("Utilities_Flags", [x.strip() for x in data.split("\n")])

    def year_built_source(self):
        data = """Appraiser
            Assessor
            Builder
            Estimated
            Other
            Owner
            Public Records
            See Remarks"""
        return self.build_generic_enum(
            "YearBuiltSource_Flags", [x.strip() for x in data.split("\n")]
        )


class RESO1p4EDMX(RESOEDMXBase):
    """This sets up the RESO format and structure.  How is it structured for version 1.4 edmx"""

    version = "1.4"

    @property
    def data(self):
        NS_MAP = {"edmx": "http://docs.oasis-open.org/odata/ns/edmx"}
        root = etree.Element("{%s}Edmx" % NS_MAP["edmx"], Version="4.0", nsmap=NS_MAP)
        dataservices = etree.Element("{%s}Dataservices" % NS_MAP["edmx"])

        self.schema.append(self.property)

        self.schema.append(self.property_green())
        self.schema.append(self.power_production())

        self.schema.append(self.area_unit_type())
        self.schema.append(self.city_data())
        self.schema.append(self.cooling_flags())
        self.schema.append(self.county_data())
        self.schema.append(self.electric_flags())
        self.schema.append(self.green_building_verification_flags())
        self.schema.append(self.green_efficient_flags())
        self.schema.append(self.green_energy_generation_flags())
        self.schema.append(self.green_indoor_air_quality_flags())
        self.schema.append(self.green_verification_source())
        self.schema.append(self.green_water_conservation())
        self.schema.append(self.power_production_flags())
        self.schema.append(self.power_production_type_flags())
        self.schema.append(self.us_states())
        self.schema.append(self.utilites())
        self.schema.append(self.year_built_source())

        dataservices.append(self.schema)
        root.append(dataservices)
        return root


def main(args):
    """Main - $<description>$"""
    import sys, os

    logging.basicConfig(
        level=logging.INFO,
        datefmt="%H:%M:%S",
        stream=sys.stdout,
        format="%(asctime)s %(levelname)s [%(filename)s] (%(name)s) %(message)s",
    )

    args.verbose = 4 if args.verbose > 4 else args.verbose
    loglevel = 50 - args.verbose * 10
    log.setLevel(loglevel)

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", args.settings)
    from django.apps import apps as django_app

    if not django_app.apps_ready:
        import django

        django.setup()

    class FakeHomeStatus(object):
        class home:
            latitude = 1.123
            longitude = 2.321

    _hs = FakeHomeStatus()
    DefaultDataDict = {
        "latitude": _hs.home.latitude,
        "longitude": _hs.home.longitude,
    }

    reso = RESO1p4EDMX()
    reso.pprint(output="Pivotal_EDMX.xml")


if __name__ == "__main__":
    import argparse, sys

    parser = argparse.ArgumentParser(description="$<description>$")
    parser.add_argument(
        "-v",
        dest="verbose",
        help="How verbose of the output",
        action="append_const",
        const=1,
        default=[1, 2, 3],
    )
    parser.add_argument("-y", dest="settings", help="Django Settings", action="store")
    parser.add_argument("-n", dest="dry_run", help="Dry Run", action="store_true")
    sys.exit(main(parser.parse_args()))
