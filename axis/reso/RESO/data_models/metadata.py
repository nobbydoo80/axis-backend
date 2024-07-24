"""metadata.py: Django RESO"""


import argparse
import json
import logging

import datetime

import sys

import os

from django.utils.text import slugify
from lxml import etree


__author__ = "Steven Klass"
__date__ = "9/7/17 08:54"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class ResoMetadataBase(object):
    def __init__(self):
        self.data = None
        self.initialize_data()

    def initialize_data(self):
        pass


class ResoJSON(ResoMetadataBase):
    def pprint(self):
        def json_serial(obj):
            if isinstance(obj, datetime.datetime):
                return obj.isoformat()

        print(json.dumps(self.data, indent=4, default=json_serial))


class ResoXml(ResoMetadataBase):
    def initialize_data(self):
        NS_MAP = {"edmx": "http://docs.oasis-open.org/odata/ns/edmx"}
        root = etree.Element("{%s}Edmx" % NS_MAP["edmx"], Version="4.0", nsmap=NS_MAP)
        dataservices = etree.Element("{%s}Dataservices" % NS_MAP["edmx"])

        EDM_MAP = {None: "http://docs.oasis-open.org/odata/ns/edm"}
        self.schema = etree.Element("Schema", Namespace="ODataService", nsmap=EDM_MAP)

        self.schema.append(self.property_root)
        self.schema.append(self.media_root)

        dataservices.append(self.schema)
        dataservices.append(self.greenverifications_root)
        dataservices.append(self.propertyenums_root)
        dataservices.append(self.mediaenums_root)
        dataservices.append(self.default_root)
        dataservices.append(self.odata_root)

        root.append(dataservices)
        self.data = root

    def element_with_text(self, attr, text, annotation=None, **kwargs):
        key = etree.Element(attr, **kwargs)
        key.text = text
        if annotation:
            key.append(
                self.element_with_text(
                    "Annotation",
                    None,
                    Term="RESO.OData.Metadata.StandardName",
                    String="%s" % annotation,
                )
            )
        return key

    @property
    def property_root(self):
        root = etree.Element("Entitytype", Name="Property")

        key = etree.Element("Key")
        key.append(etree.Element("PropertyRef", name="ListingKeyNumeric"))
        root.append(key)

        root.append(
            self.element_with_text(
                "Property",
                None,
                Name="ListingKeyNumeric",
                Type="Edm.Int64",
                Nullable="false",
                MaximumLength="16",
                Precision="0",
            )
        )

        root.append(
            self.element_with_text(
                "Property",
                None,
                Name="AboveGradeFinishedArea",
                Type="Edm.Decimal",
                Precision="13",
                Scale="2",
            )
        )
        root.append(
            self.element_with_text(
                "Property",
                None,
                Name="AboveGradeFinishedAreaSource",
                Type="PropertyEnums.StandardEnergyDataSources",
            )
        )
        root.append(
            self.element_with_text(
                "Property",
                None,
                Name="AboveGradeFinishedAreaUnits",
                Type="PropertyEnums.StandardAreaUnits",
            )
        )

        root.append(
            self.element_with_text(
                "Property", None, Name="Basement", Type="PropertyEnums.FoundationTypes"
            )
        )

        root.append(
            self.element_with_text(
                "Property", None, Name="BuilderModel", Type="Edm.String", MaxLength="64"
            )
        )
        root.append(
            self.element_with_text(
                "Property", None, Name="BuilderName", Type="Edm.String", MaxLength="64"
            )
        )

        root.append(
            self.element_with_text(
                "Property",
                None,
                Name="BuildingAreaSource",
                Type="PropertyEnums.StandardEnergyDataSources",
            )
        )
        root.append(
            self.element_with_text(
                "Property",
                None,
                Name="BuildingAreaTotal",
                Type="Edm.Decimal",
                Precision="13",
                Scale="2",
            )
        )
        root.append(
            self.element_with_text(
                "Property", None, Name="BuildingAreaUnits", Type="PropertyEnums.StandardAreaUnits"
            )
        )

        root.append(
            self.element_with_text("Property", None, Name="City", Type="PropertyEnums.Cities")
        )

        root.append(
            self.element_with_text("Property", None, Name="Cooling", Type="PropertyEnums.Cooling")
        )
        root.append(self.element_with_text("Property", None, Name="CoolingYN", Type="Edm.Boolean"))

        root.append(
            self.element_with_text("Property", None, Name="ElectricExpense", Type="Edm.Decimal")
        )
        root.append(
            self.element_with_text(
                "Property", None, Name="ElectricOnPropertyYN", Type="Edm.Boolean"
            )
        )

        root.append(
            self.element_with_text(
                "Property", None, Name="CountyOrParish", Type="PropertyEnums.Counties"
            )
        )

        root.append(
            self.element_with_text(
                "Property",
                None,
                Name="ElectricExpense",
                Type="Edm.Decimal",
                Precision="13",
                Scale="2",
            )
        )
        root.append(
            self.element_with_text(
                "Property", None, Name="ElectricOnPropertyYN", Type="Edm.Boolean"
            )
        )

        root.append(
            self.element_with_text(
                "Property", None, Name="GasExpense", Type="Edm.Decimal", Precision="13", Scale="2"
            )
        )
        root.append(
            self.element_with_text("Property", None, Name="GasOnPropertyYN", Type="Edm.Boolean")
        )

        root.append(
            self.element_with_text("Property", None, Name="Heating", Type="PropertyEnums.Heating")
        )
        root.append(self.element_with_text("Property", None, Name="HeatingYN", Type="Edm.Boolean"))

        root.append(
            self.element_with_text(
                "Property",
                None,
                Name="GreenBuildingVerificationType",
                Type="PropertyEnums.GreenBuildingVerificationTypes",
            )
        )

        root.append(
            self.element_with_text(
                "Property", None, Name="Latitude", Type="Edm.Decimal", Precision="20", Scale="8"
            )
        )
        root.append(
            self.element_with_text(
                "Property", None, Name="Longitude", Type="Edm.Decimal", Precision="20", Scale="8"
            )
        )

        root.append(
            self.element_with_text(
                "Property", None, Name="PostalCode", Type="Edm.String", MaxLength="10"
            )
        )

        root.append(
            self.element_with_text(
                "Property", None, Name="StateOrProvince", Type="PropertyEnums.States"
            )
        )

        root.append(
            self.element_with_text("Property", None, Name="Stories", Type="Edm.Byte", Precision="1")
        )
        root.append(
            self.element_with_text(
                "Property", None, Name="StoriesTotal", Type="Edm.Byte", Precision="1"
            )
        )

        root.append(
            self.element_with_text(
                "Property", None, Name="YearBuilt", type="Edm.Int16", Precision="1"
            )
        )
        root.append(
            self.element_with_text(
                "Property",
                None,
                Name="YearBuiltSource",
                Type="PropertyEnums.StandardEnergyDataSources",
            )
        )

        # TODO ADD MORE...

        # These are in-flux as I have no idea how to actually implement this on metadata side.

        root.append(
            self.element_with_text(
                "Property", None, Name="AddressLine1", Type="Edm.String", MaxLength="128"
            )
        )
        root.append(
            self.element_with_text(
                "Property", None, Name="AddressLine2", Type="Edm.String", MaxLength="128"
            )
        )

        root.append(
            self.element_with_text(
                "Property",
                None,
                Name="ElectricConsumption",
                Type="Edm.Decimal",
                Precision="13",
                Scale="2",
            )
        )

        root.append(
            self.element_with_text(
                "NavigationProperty",
                None,
                Name="GreenVerification",
                Type="Collection(GreenVerification)",
            )
        )

        return root

    # @property
    # def green_root(self):
    #     root = etree.Element("Entitytype", Name="PropertyGreen")
    #     root.append(self.element_with_text("Property", None, Name="GreenBuildingVerificationType", Type="PropertyEnums.GreenBuildingVerificationType"))
    #     return root

    def get_cities(self):
        from axis.home.models import Home
        from axis.geographic.models import City

        source = self.element_with_text("EnumType", None, Name="Cities", UnderlyingType="Edm.Int32")

        home_cities = list(set(Home.objects.all().values_list("city_id", flat=True)))
        cities = City.objects.filter(id__in=home_cities).values_list(
            "pk", "name", "county__name", "county__state"
        )
        for pk, name, county, state in cities:
            city_name = "{}_{}_{}".format(slugify(name), slugify(county), state)
            source.append(
                self.element_with_text(
                    "Member",
                    None,
                    Name=city_name,
                    Value="{}".format(pk),
                    annotation="%s (%s) %s" % (name, county, state),
                )
            )
        return source

    def get_counties(self):
        from axis.home.models import Home
        from axis.geographic.models import County

        source = self.element_with_text(
            "EnumType", None, Name="Counties", UnderlyingType="Edm.Int32"
        )

        home_counties = list(set(Home.objects.all().values_list("city__county_id", flat=True)))
        counties = County.objects.filter(id__in=home_counties).values_list("pk", "name", "state")
        for pk, name, state in counties:
            label = "{}_{}".format(slugify(name), state)
            source.append(
                self.element_with_text(
                    "Member",
                    None,
                    Name=label,
                    Value="{}".format(pk),
                    annotation="%s %s" % (name, state),
                )
            )
        return source

    def get_states(self):
        from localflavor.us.us_states import US_STATES

        STATES = [(idx, name, "{}".format(label)) for idx, (name, label) in enumerate(US_STATES)]
        source = self.element_with_text("EnumType", None, Name="States", UnderlyingType="Edm.Int32")
        for pk, name, label in list(STATES):
            source.append(self.element_with_text("Member", None, Name=name, Value="{}".format(pk)))
        return source

    def onlyascii(self, char):
        if ord(char) < 48 or ord(char) > 127:
            return ""
        else:
            if char in [" ", "-", "_"]:
                return ""
            return char

    def build_enuration_list_by_choices(
        self, name, choices, underlying_type="Edm.Int32", is_flags=None
    ):
        kwargs = {"Name": name, "UnderlyingType": underlying_type}
        if is_flags:
            kwargs["isFlags"] = "true"

        source = self.element_with_text("EnumType", None, **kwargs)
        for value, label in choices:
            name = filter(self.onlyascii, label)
            source.append(
                self.element_with_text(
                    "Member", None, Name=name, Value="{}".format(value), annotation=label
                )
            )
        return source

    @property
    def propertyenums_root(self):
        EDM_MAP = {None: "http://docs.oasis-open.org/odata/ns/edm"}
        root = etree.Element("Schema", Name="PropertyEnums", nsmap=EDM_MAP)

        from axis.reso.models import (
            STANDARD_ENERGY_DATA_SOURCES,
            STANDARD_UNITS,
            GREEN_BUILDING_VERIFICATION_TYPES,
        )
        from axis.reso.models import RESO_COOLING_CHOICES, RESO_HEATER_CHOICES

        from axis.remrate_data.strings import FOUNDATION_TYPES

        root.append(
            self.build_enuration_list_by_choices(
                "StandardEnergyDataSources", STANDARD_ENERGY_DATA_SOURCES
            )
        )
        root.append(self.build_enuration_list_by_choices("StandardAreaUnits", STANDARD_UNITS))
        root.append(
            self.build_enuration_list_by_choices("FoundationTypes", FOUNDATION_TYPES, is_flags=True)
        )

        root.append(
            self.build_enuration_list_by_choices("Cooling", RESO_COOLING_CHOICES, is_flags=True)
        )
        root.append(
            self.build_enuration_list_by_choices("Heating", RESO_HEATER_CHOICES, is_flags=True)
        )

        root.append(self.get_cities())
        root.append(self.get_counties())
        root.append(self.get_states())

        # In-Flux
        root.append(
            self.build_enuration_list_by_choices(
                "GreenBuildingVerificationTypes", GREEN_BUILDING_VERIFICATION_TYPES, is_flags=True
            )
        )
        root.append(
            self.build_enuration_list_by_choices(
                "GreenBuildingVerificationType", GREEN_BUILDING_VERIFICATION_TYPES
            )
        )

        return root

    @property
    def greenverifications_root(self):
        EDM_MAP = {None: "http://docs.oasis-open.org/odata/ns/edm"}
        root = etree.Element("Schema", Name="GreenVerification", nsmap=EDM_MAP)
        root.append(
            self.element_with_text(
                "Property",
                None,
                Name="GreenBuildingVerificationType",
                Type="PropertyEnums.GreenBuildingVerificationType",
            )
        )
        root.append(
            self.element_with_text(
                "Property", None, Name="GreenVerificationBody", Type="Edm.String", MaxLength="64"
            )
        )
        root.append(
            self.element_with_text(
                "Property", None, Name="GreenVerificationDate", Type="Edm.DateTimeOffset"
            )
        )
        root.append(
            self.element_with_text(
                "Property", None, Name="GreenVerificationMetric", Type="Edm.String", MaxLength="64"
            )
        )
        root.append(
            self.element_with_text(
                "Property", None, Name="GreenVerificationRating", Type="Edm.String", MaxLength="64"
            )
        )
        root.append(
            self.element_with_text(
                "Property", None, Name="GreenVerificationSource", Type="Edm.String", MaxLength="64"
            )
        )
        root.append(
            self.element_with_text(
                "Property", None, Name="GreenVerificationStatus", Type="Edm.String", MaxLength="64"
            )
        )
        root.append(
            self.element_with_text(
                "Property", None, Name="GreenVerificationURL", Type="Edm.String", MaxLength="64"
            )
        )
        return root

    @property
    def media_root(self):
        root = etree.Element("Entitytype", Name="Media")

        return root

    @property
    def mediaenums_root(self):
        EDM_MAP = {None: "http://docs.oasis-open.org/odata/ns/edm"}
        root = etree.Element("Schema", Name="MediaEnums", nsmap=EDM_MAP)

        return root

    @property
    def default_root(self):
        EDM_MAP = {None: "http://docs.oasis-open.org/odata/ns/edm"}
        root = etree.Element("Schema", Name="Default", nsmap=EDM_MAP)

        return root

    @property
    def odata_root(self):
        EDM_MAP = {None: "http://docs.oasis-open.org/odata/ns/edm"}
        root = etree.Element("Schema", Name="RESO.OData.Metadata", nsmap=EDM_MAP)

        return root

    def pprint(self, output=None, pretty=True, as_string=False):
        if output:
            with open(output, "wb") as outputfile:
                outputfile.write(
                    etree.tostring(
                        self.data, pretty_print=pretty, xml_declaration=True, encoding="utf-8"
                    )
                )
            return
        if as_string:
            return etree.tostring(
                self.data, pretty_print=pretty, xml_declaration=True, encoding="utf-8"
            )
        print(
            etree.tostring(self.data, pretty_print=pretty, xml_declaration=True, encoding="utf-8")
        )


def main(args):
    """Main - $<description>$"""
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

    reso = ResoXml()
    reso.pprint()
    reso.pprint(output="../../odata/metadata.xml")


if __name__ == "__main__":
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
