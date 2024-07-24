"""data.py: Django """


import argparse
import datetime
import importlib
import json
import logging
import os
import sys
from collections import OrderedDict

from lxml import etree
from lxml.etree import CDATA
import xmltodict

from simulation.serializers.rem.xml import SimulationSerializer as RemXMLSimulationSerializer

__author__ = "Steven Klass"
__date__ = "2/17/16 08:07"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


def json_serial(obj):
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()


class RESNETDataBase(object):
    def __init__(self, home_status, provider_id, rater_id, **kwargs):
        self.home_status = home_status

        if not home_status.certification_date:
            raise Exception("%r must be certified" % home_status)

        self.provider_id = provider_id
        self.rater_id = rater_id

        self.registry_id = kwargs.get("registry_id")
        self.registry_reason = kwargs.get("registry_reason")

        self.xsd = kwargs.get("xsd", None)
        self.xsd_version = 2.0
        if self.xsd:
            assert os.path.exists(self.xsd), "XSD Provided does not exist -- %s" % self.xsd
            if "2.03" in self.xsd:
                self.xsd_version = 2.03

        self.root = None

        self.strings_module_path = kwargs.get("strings_module_path", "axis.remrate_data.strings")
        if self.strings_module_path is None:
            self.strings_module_path = "axis.remrate_data.strings"
        try:
            self.strings_module = importlib.import_module(self.strings_module_path, "*")
        except ImportError:
            log.info("Unable to open axis.remrate_data.strings")

    def strings(self, variable):
        return getattr(self.strings_module, variable)

    def dict_value(self, dictname, variable):
        return dict(self.strings(dictname)).get(variable)

    def get_date(self, date_obj):
        return date_obj

    def pprint(self, data):
        print(json.dumps(data, indent=4, default=json_serial))

    def add_sub_element_with_value(self, root, element, value=None):
        element = etree.SubElement(root, element)
        if value is not None:
            element.text = "{}".format(value)
            if isinstance(value, str):
                if value not in ["true", "false"]:
                    element.text = CDATA(value)
        elif value is None:
            element.text = ""
        return element

    def add_element_list(self, parent, data_list, element_name=None):
        for item in data_list:
            # print("Working on {}: {}".format(parent, item))
            # print("Working type {}: {}".format(type(data_list), type(item)))
            element = etree.Element(element_name) if element_name else parent
            for key, _v in item.items():
                if key == "id" and _v:
                    element.attrib.update(_v)
                    continue
                value = item.get(key)
                if isinstance(_v, (dict, type(OrderedDict))):
                    # print("Calling on {}: {}".format(parent, item))
                    sub = etree.SubElement(element, key)
                    self.add_element_list(sub, [value], None)
                else:
                    # print("{}: {}".format(key, value))
                    element.append(self.add_sub_element_with_value(element, key, value))
            if element != parent:
                parent.append(element)
        return parent

    def set_registry_id(self, registry_id):
        raise NotImplementedError("You need to implement this")

    def get_rating_type(self):
        base = self.home_status.get_rating_type()
        if "confirmed" in base.lower():
            return "Confirmed Rating"
        elif "test" in base.lower():
            return "Confirmed"
        elif "sampled" in base.lower():
            return "Sampled"
        else:
            log.warning("Unable to figure out Rating type {}".format(base))
            return "ProjectedWorstCase"

    @property
    def verifiers(self):
        _verifier = self.home_status.company
        if self.home_status.rater_of_record:
            _verifier = self.home_status.rater_of_record

        return OrderedDict(
            [
                (
                    "Verifier",
                    OrderedDict([("Name", _verifier), ("ID", "5031548")]),  # TODO FIX ME!!
                ),
            ]
        )

    @property
    def building(self):
        subdivision = self.home_status.home.subdivision
        try:
            subdivision_name = subdivision.name
        except AttributeError:
            subdivision_name, community_name = " ", " "
        else:
            try:
                community_name = subdivision.community.name
            except AttributeError:
                community_name = " "

        addr2 = "" if not self.home_status.home.street_line2 else self.home_status.home.street_line2

        return OrderedDict(
            [
                ("Address", self.home_status.home.street_line1),
                ("Address2", addr2),
                ("City", self.home_status.home.city.name),
                ("State", self.home_status.home.state),
                ("Zip", self.home_status.home.zipcode),
                ("Builder", self.home_status.home.get_builder().name),
                ("Community", community_name),  # TODO VERIFY FIELD
                ("PlanName", self.home_status.floorplan.name),  # TODO VERIFY FIELD
                ("Model", self.home_status.floorplan.number),  # TODO VERIFY FIELD
                ("Development", subdivision_name),  # TODO VERIFY FIELD
                ("ConstructionYear", self.home_status.home.created_date.strftime("%Y")),
            ]
        )

    @property
    def registry(self):
        try:
            sampleset = self.home_status.get_sampleset().uuid[:8].upper()
        except AttributeError:
            sampleset = "00000000"

        return OrderedDict(
            [
                ("ProviderID", self.provider_id),
                ("RaterID", self.rater_id),
                ("RatingCompany", self.home_status.company),
                ("ProviderSampleSetID", sampleset),
                ("DateRated", self.get_date(self.home_status.certification_date)),
                ("ClimateZoneNo", self.home_status.home.county.climate_zone),
                ("Status", "New"),
                ("HomeTypeID", "1"),
                ("ConditionedArea", -1.0),
                ("ConditionedVolume", -1.0),
                ("NumberBedrooms", 0),
                ("ConditionedBasementArea", 0),
                ("UnconditionedBasementArea", 0),
                ("Software", ""),
                ("SoftwareVersion", ""),
                # ('SoftwareUploadID', '6'), # List of possible elements expected: 'EPAAppID, Standard301Version, InputFile'
                ("InputFile", ""),
                (
                    "Notes",
                    "Axis Home ID:  {} Home Status ID: {}".format(
                        self.home_status.home.get_id(), self.home_status.id
                    ),
                ),
            ]
        )

    @property
    def rating(self):
        return OrderedDict(
            [
                ("HERSIndex", 123),
                ("AnnualElectricity", 0.0),
                ("AnnualGas", 0.0),
                ("AnnualOil", 0.0),
                ("AnnualPropane", 0.0),
                ("AnnualOPP", 0.0),
                ("AnnualOther", 0.0),
                ("PriceElectricity", None),
                ("PriceGas", None),
                ("PriceOil", None),
                ("PricePropane", None),
                ("CostHeating", 0.0),
                ("CostCooling", 0.0),
                ("CostHotWater", 0.0),
                ("CostLighting", 0.0),
                ("CostAppliances", 0.0),
                ("CostOPP", 0.0),
                ("CostTotal", 0.0),
                ("RateECHeating", -1.0),
                ("RateECCooling", -1.0),
                ("RateECHotWater", -1.0),
                ("RateECLgtApl", -1.0),
                ("nMEULHeating", -1.0),
                ("nMEULCooling", -1.0),
                ("nMEULHotWater", -1.0),
                ("nMEULLgtApl", -1.0),
                ("nECHeating", -1.0),
                ("nECCooling", -1.0),
                ("nECHotWater", -1.0),
                ("nECLgtApl", -1.0),
                ("CO2", -1.0),
                ("SOx", -1.0),
                ("NOx", -1.0),
                ("RefCostHeating", -1.0),
                ("RefCostCooling", -1.0),
                ("RefCostHotWater", -1.0),
                ("RefCostLighting", -1.0),
                ("RefCostAppliances", -1.0),
                ("RefCostTotal", -1.0),
                ("RefEULHeating", -1.0),
                ("RefEULCooling", -1.0),
                ("RefEULHotWater", -1.0),
                ("RefEULLgtApl", -1.0),
                ("RefECHeating", -1.0),
                ("RefECCooling", -1.0),
                ("RefECHotWater", -1.0),
                ("RefECLgtApl", -1.0),
                ("RefCO2", -1.0),
                ("RefSOx", -1.0),
                ("RefNOx", -1.0),
                ("OPPNet", -1.0),
                ("PEfrac", -1.0),
            ]
        )

    @property
    def eep(self):
        return OrderedDict([("EEPQualified", "false")])

    @property
    def enclosure(self):
        return OrderedDict(
            [
                ("ABGradeFloorA", -1.0),
                ("ABGradeFloorUo", -1.0),
                ("GroundContactFloorA", -1.0),
                ("GroundContactFloorUo", -1.0),
                ("CeilingA", -1.0),
                ("CeilingUo", -1.0),
                ("ABGradeWallA", -1.0),
                ("ABGradeWallUo", -1.0),
                ("GroundContactWallA", -1.0),
                ("GroundContactWallUo", -1.0),
                ("WindowA", -1.0),
                ("WindowUo", -1.0),
                ("WindowSHGC", -1.0),
                ("DoorA", -1.0),
                ("DoorUo", -1.0),
                ("OverallEnclosureUA", -1.0),
            ]
        )

    @property
    def heating_systems(self):
        def get_system(system):
            return OrderedDict(
                [
                    ("Fuel", "electric"),
                    ("Type", "standard"),
                    ("RatingMetric", "HSPF"),
                    ("RatingValue", -1.0),
                    ("RatedOutputCapacity", -1.0),
                ]
            )

        return [get_system(x) for x in [1]]

    @property
    def cooling_systems(self):
        def get_system(system):
            return OrderedDict(
                [
                    ("Type", "electric"),
                    ("RatingMetric", "SEER"),
                    ("RatingValue", -1.0),
                    ("RatedOutputCapacity", -1.0),
                ]
            )

        return [get_system(x) for x in [1]]

    @property
    def mechanical_vent_systems(self):
        def get_system(system):
            return OrderedDict(
                [
                    ("Type", "none"),
                    ("VentFanFlowRate", -1.0),
                    ("VentFanPower", -1.0),
                    ("VentFanRunTime", -1.0),
                ]
            )

        return [get_system(x) for x in [1]]

    @property
    def dehumidification_systems(self):
        def get_system(system):
            return OrderedDict(
                [
                    ("Type", "none"),
                    ("Capacity", -1.0),
                    ("Efficiency", -1.0),
                ]
            )

        return [get_system(x) for x in [1]]

    @property
    def lighting_systems(self):
        return OrderedDict(
            [
                ("QualifyingLightingLtX", -1.0),
                ("QualifyingLightingGeX", -1.0),
                ("Refrigerator", "standard"),
                ("DishWasher", "standard"),
                ("ClothesWasher", "standard"),
                ("ClothesDryer", "standard"),
                ("CeilingFans", None),
            ]
        )

    @property
    def hot_water_systems(self):
        def get_system(system):
            return OrderedDict(
                [
                    ("Type", "electric"),
                    ("EfficiencyUnits", "EF"),
                    ("EfficiencyValue", -1.0),
                    ("StorageCapacity", -1.0),
                ]
            )

        return [get_system(x) for x in [1]]

    @property
    def measured_enclosure_tightness(self):
        return OrderedDict(
            [
                ("MeasurementType", "SinglePoint"),
                ("SinglePoint", OrderedDict([("cfm50", -1.0), ("ELA", -1.0)])),
            ]
        )

    @property
    def duct_systems(self):
        def get_system(system):
            return OrderedDict(
                [
                    ("Type", "ductless"),
                    (
                        "TestedLeakage",
                        OrderedDict(
                            [
                                ("cfm25out", -1.0),
                                ("cfm25total", -1.0),
                                ("Qn", -1.0),
                            ]
                        ),
                    ),
                    ("SupplyDuctsCondSpace", -1.0),
                    ("ReturnDuctsCondSpace", -1.0),
                ]
            )

        return [get_system(x) for x in [1]]

    @property
    def energy_features(self):
        return OrderedDict(
            [
                ("OPP", OrderedDict([("CheckOPP", "false")])),
                ("SolarHotWaterSystems", OrderedDict([("SHWS", "false")])),
                ("DWHR", OrderedDict([("CheckDWHR", "false")])),
                ("ACHotWaterHeatRecovery", OrderedDict([("ACHWHRecovery", "false")])),
            ]
        )

    @property
    def whole_house_designators(self):
        return OrderedDict(
            [
                ("EPAEStarNewHome", "false"),
                ("DOEZHRH", "false"),
            ]
        )

    @property
    def warnings(self):
        return OrderedDict(
            [
                (
                    "BuildingAttributeFlags",
                    OrderedDict(
                        [
                            ("StoriesAboveGradeValue", -1),
                            ("AverageCeilingHeightValue", -1.0),
                            ("BelowGradeSlabFloorsValue", -1),
                            ("BelowGradeWallsValue", -1),
                            ("CrawlSpacePerimeterValue", -1.0),
                            ("BasementPerimeterValue", -1.0),
                            ("SlabGradePerimeterValue", -1.0),
                            ("FoundationWallHeightValue", -1.0),
                            ("BasementWallDepthValue", -1.0),
                            ("EnclosureFloorAreaValue", -1.0),
                            ("EnclosureGrossWallAreaValue", -1.0),
                        ]
                    ),
                ),
                (
                    "ApplianceVerificationFlags",
                    OrderedDict(
                        [
                            ("ClothesWashersValue", -1),
                            ("ElectricDryersValue", -1.0),
                            ("GasDryersThermsValue", -1),
                            ("GasDryersKWHValue", -1),
                            ("CWHotWaterSavingsValue", -1.0),
                        ]
                    ),
                ),
            ]
        )

    def get_data(self):
        if self.root is not None:
            return self.root
        NSMAP = {
            "xsi": "http://www.w3.org/2001/XMLSchema-instance",
        }

        self.root = etree.Element("Ratings", nsmap=NSMAP)
        location_attribute = "{" + NSMAP["xsi"] + "}noNamespaceSchemaLocation"
        self.root.attrib[location_attribute] = "http://brapiv2.resnet.us/ResXSDv2.0.xsd"

        if self.registry_id:
            self.revision = etree.SubElement(self.root, "Revision")
            self.add_sub_element_with_value(self.revision, "RegistryID", self.registry_id)
            self.add_sub_element_with_value(self.revision, "RevisionReason", self.registry_reason)

        self.add_sub_element_with_value(self.root, "RatingType", self.get_rating_type())
        self.add_element_list(self.root, [self.verifiers], "Verifiers")
        self.add_element_list(self.root, [self.building], "Building")
        self.add_element_list(self.root, [self.registry], "Registry")
        self.add_element_list(self.root, [self.rating], "Rating")
        self.add_element_list(self.root, [self.eep], "EEP")
        self.perf = etree.SubElement(self.root, "HomeEnergyPerformance")
        self.add_element_list(self.perf, [self.enclosure], "Enclosure")

        self.heating = etree.SubElement(self.perf, "HVACHeatingSystems")
        self.add_element_list(self.heating, self.heating_systems, "System")
        self.heating.attrib["NumHVACHeatingSystems"] = "{}".format(len(self.heating_systems))

        self.cooling = etree.SubElement(self.perf, "HVACCoolingSystems")
        self.add_element_list(self.cooling, self.cooling_systems, "System")
        self.cooling.attrib["NumHVACCoolingSystems"] = "{}".format(len(self.cooling_systems))

        self.mech = etree.SubElement(self.perf, "HVACMechVentSystems")
        self.add_element_list(self.mech, self.mechanical_vent_systems, "System")
        self.mech.attrib["NumHVACMechVentSystems"] = "{}".format(len(self.mechanical_vent_systems))

        self.dehumidification = etree.SubElement(self.perf, "HVACDehumidificationSystems")
        self.add_element_list(self.dehumidification, self.dehumidification_systems, "System")
        self.dehumidification.attrib["NumHVACDehumidificationSystems"] = "{}".format(
            len(self.dehumidification_systems)
        )

        self.add_element_list(self.perf, [self.lighting_systems], "LightingAppliances")

        self.hot_water = etree.SubElement(self.perf, "HotWaterSystems")
        self.add_element_list(self.hot_water, self.hot_water_systems, "System")
        self.hot_water.attrib["NumHotWaterSystems"] = "{}".format(len(self.hot_water_systems))

        self.add_element_list(
            self.perf, [self.measured_enclosure_tightness], "MeasuredEnclosureTightness"
        )

        self.ducts = etree.SubElement(self.perf, "DuctSystems")
        self.add_element_list(self.ducts, self.duct_systems, "System")
        self.ducts.attrib["NumDuctSystems"] = "{}".format(len(self.duct_systems))

        self.add_element_list(self.perf, [self.energy_features], "AddedEnergyFeatures")

        self.add_element_list(self.perf, [self.whole_house_designators], "WholeHEEffDesignations")
        self.add_element_list(self.root, [self.warnings], "WarningFlags")

        data = etree.tostring(self.root, pretty_print=True, xml_declaration=True, encoding="utf-8")

        if self.xsd:
            try:
                etree.fromstring(data, self.get_xsd_parser())
            except etree.XMLSyntaxError as err:
                log.warning(err)
            except Exception as err:
                print(data)
                raise err
            else:
                log.info(
                    "We have validated the xml to version {} -- {}".format(
                        self.xsd_version, self.xsd
                    )
                )

        return self.root

    def get_xsd_parser(self):
        with open(self.xsd, "rb") as f:
            schema_root = etree.XML(f.read())
        schema = etree.XMLSchema(schema_root)
        return etree.XMLParser(schema=schema)

    @property
    def xml(self):
        self.get_data()
        return etree.tostring(self.root, pretty_print=True, xml_declaration=True, encoding="utf-8")


class RESNETRem(RESNETDataBase):
    def __init__(self, *args, **kwargs):
        super(RESNETRem, self).__init__(*args, **kwargs)
        self.simulation = self.home_status.floorplan.remrate_target
        self.registry_id = self.simulation.building.project.resnet_registry_id

    def get_registry_input_file(self):
        serializer = RemXMLSimulationSerializer(self.home_status.floorplan.simulation)
        return xmltodict.unparse(serializer.data, pretty=True)

    def set_registry_id(self, registry_id):
        project = self.simulation.building.project
        project.resnet_registry_id = registry_id
        project.save()

    @property
    def registry(self):
        data = super(RESNETRem, self).registry
        data.update(
            dict(
                [
                    ("HomeTypeID", self.simulation.buildinginfo.type),
                    ("ConditionedArea", self.simulation.buildinginfo.conditioned_area),
                    ("ConditionedVolume", self.simulation.buildinginfo.volume),
                    ("NumberBedrooms", self.simulation.buildinginfo.number_bedrooms),
                    ("Software", 1),
                    ("SoftwareVersion", self.simulation.version.strip()),
                    ("InputFile", self.get_registry_input_file()),
                    (
                        "Notes",
                        "Axis Home ID:  {} Home Status ID: {} Simulation ID: {}".format(
                            self.home_status.home.get_id(), self.home_status.id, self.simulation.id
                        ),
                    ),
                ]
            )
        )
        return data

    @property
    def rating(self):
        data = super(RESNETRem, self).rating
        data["HERSIndex"] = int(round(self.simulation.hers.score))
        data["AnnualElectricity"] = 0.0
        data["AnnualGas"] = 0.0
        data["AnnualOil"] = 0.0
        data["AnnualPropane"] = 0.0
        data["AnnualOPP"] = 0.0
        data["AnnualOther"] = 0.0
        data["PriceElectricity"] = 0.0
        data["PriceGas"] = 0.0
        data["PriceOil"] = 0.0
        data["PricePropane"] = 0.0
        data["CostHeating"] = self.simulation.results.heating_cost
        data["CostCooling"] = self.simulation.results.cooling_cost
        data["CostHotWater"] = self.simulation.results.hot_water_cost
        data["CostLighting"] = self.simulation.results.lighting_cost
        data["CostAppliances"] = (
            self.simulation.results.lights_and_appliances_cost
            - self.simulation.results.lighting_cost
        )
        data["CostOPP"] = 0.0
        data["CostTotal"] = 0.0
        data["RateECHeating"] = -1.0
        data["RateECCooling"] = -1.0
        data["RateECHotWater"] = -1.0
        data["RateECLgtApl"] = -1.0
        data["nMEULHeating"] = -1.0
        data["nMEULCooling"] = -1.0
        data["nMEULHotWater"] = -1.0
        data["nMEULLgtApl"] = -1.0
        data["nECHeating"] = self.simulation.hers.designed_heating_consumption
        data["nECCooling"] = self.simulation.hers.designed_cooling_consumption
        data["nECHotWater"] = self.simulation.hers.designed_hot_water_consumption
        data["nECLgtApl"] = self.simulation.hers.designed_lights_appliance_consumption
        data["CO2"] = -1.0
        data["SOx"] = -1.0
        data["NOx"] = -1.0
        data["RefCostHeating"] = -1.0
        data["RefCostCooling"] = -1.0
        data["RefCostHotWater"] = -1.0
        data["RefCostLighting"] = -1.0
        data["RefCostAppliances"] = -1.0
        data["RefCostTotal"] = -1.0
        data["RefEULHeating"] = -1.0
        data["RefEULCooling"] = -1.0
        data["RefEULHotWater"] = -1.0
        data["RefEULLgtApl"] = -1.0
        data["RefECHeating"] = self.simulation.hers.reference_heating_consumption
        data["RefECCooling"] = self.simulation.hers.reference_cooling_consumption
        data["RefECHotWater"] = self.simulation.hers.reference_hot_water_consumption
        data["RefECLgtApl"] = self.simulation.hers.reference_lights_appliance_consumption
        data["RefCO2"] = -1.0
        data["RefSOx"] = -1.0
        data["RefNOx"] = -1.0
        data["OPPNet"] = -1.0
        data["PEfrac"] = -1.0
        return data

    @property
    def enclosure(self):
        data = OrderedDict()
        data["ABGradeFloorA"] = self.simulation.framefloor_set.get_total_area()
        if data["ABGradeFloorA"] > 0:
            data["ABGradeFloorUo"] = self.simulation.framefloor_set.get_total_u_value()
        data["GroundContactFloorA"] = self.simulation.slab_set.get_total_area()
        if data["GroundContactFloorA"] > 0:
            data["GroundContactFloorUo"] = self.simulation.slab_set.get_total_u_value()
        data["CeilingA"] = self.simulation.roof_set.get_total_area()
        if data["CeilingA"] > 0:
            data["CeilingUo"] = self.simulation.roof_set.get_total_u_value()
        data["ABGradeWallA"] = self.simulation.abovegradewall_set.get_total_area()
        if data["ABGradeWallA"] > 0:
            data["ABGradeWallUo"] = self.simulation.abovegradewall_set.get_total_u_value()
        data["GroundContactWallA"] = self.simulation.foundationwall_set.get_total_area()
        if data["GroundContactWallA"] > 0:
            data["GroundContactWallUo"] = self.simulation.foundationwall_set.get_total_u_value()
        data["WindowA"] = self.simulation.window_set.get_total_area()
        if data["WindowA"]:
            data["WindowUo"] = self.simulation.window_set.get_total_u_value()
            data["WindowSHGC"] = self.simulation.window_set.get_total_shgc()
        data["DoorA"] = self.simulation.door_set.get_total_area()
        if data["DoorA"]:
            data["DoorUo"] = self.simulation.door_set.get_total_u_value()
        data["OverallEnclosureUA"] = self.simulation.overall_enclosure_UA()
        return data

    def get_fuel_type(self, id):
        return {
            1: "gas",
            2: "propane",
            3: "oil",
            4: "electric",
            5: "oil",
            6: "biomass",
        }.get(id)

    def get_heater_type(self, id):
        return dict(
            [
                (1, "standard"),
                (2, "standard"),
                (3, "standard"),
                (4, "standard"),
                (5, "standard"),
                (6, "standard"),
                (7, "standard"),
                (8, "HeatPump"),
                (9, "HeatPump"),
            ]
        ).get(id, "standard")

    @property
    def heating_systems(self):
        heating_units = dict([(1, "AFUE"), (3, "HSPF"), (4, "COP")])

        def get_system(system):
            return OrderedDict(
                [
                    ("Fuel", self.get_fuel_type(system.fuel_type)),
                    ("Type", self.get_heater_type(system.type)),
                    ("RatingMetric", heating_units.get(system.efficiency_unit)),
                    ("RatingValue", system.efficiency),
                    ("RatedOutputCapacity", system.output_capacity),
                ]
            )

        data = [get_system(x) for x in self.simulation.heater_set.all()]
        return data if len(data) else super(RESNETRem, self).heating_systems

    @property
    def cooling_systems(self):
        cooling_units = dict([(1, "SEER"), (2, "EER")])

        def get_system(system):
            return OrderedDict(
                [
                    ("Type", self.get_fuel_type(system.fuel_type)),
                    ("RatingMetric", cooling_units.get(system.efficiency_unit)),
                    ("RatingValue", system.efficiency),
                    ("RatedOutputCapacity", system.output_capacity),
                ]
            )

        data = [get_system(x) for x in self.simulation.airconditioner_set.all()]
        return data if len(data) else super(RESNETRem, self).cooling_systems

    @property
    def mechanical_vent_systems(self):
        infiltration_types = dict(
            [(0, "none"), (1, "HRV"), (2, "Exhaust"), (3, "Supply"), (4, "CFIS")]
        )

        def get_system():
            return OrderedDict(
                [
                    (
                        "Type",
                        infiltration_types.get(self.simulation.infiltration.mechanical_vent_type),
                    ),
                    ("VentFanFlowRate", self.simulation.infiltration.mechanical_vent_cfm),
                    ("VentFanPower", self.simulation.infiltration.mechanical_vent_power),
                    ("VentFanRunTime", self.simulation.infiltration.hours_per_day),
                ]
            )

        return (
            [get_system()]
            if self.simulation.infiltration.mechanical_vent_type
            else super(RESNETRem, self).mechanical_vent_systems
        )

    @property
    def lighting_systems(self):
        ceiling_fans = "none"
        if self.simulation.mandatoryrequirements.energy_star_v3_ceiling_fans:
            ceiling_fans = (
                "eStar"
                if self.simulation.mandatoryrequirements.verified_energy_star_v3_ceiling_fans
                else "standard"
            )

        return OrderedDict(
            [
                ("QualifyingLightingLtX", self.simulation.lightsandappliance.pct_florescent),
                ("QualifyingLightingGeX", self.simulation.lightsandappliance.pct_interior_cfl),
                (
                    "Refrigerator",
                    "eStar"
                    if self.simulation.mandatoryrequirements.verified_energy_star_v3_refrigerators
                    else "standard",
                ),
                (
                    "DishWasher",
                    "eStar"
                    if self.simulation.mandatoryrequirements.verified_energy_star_v3_dishwashers
                    else "standard",
                ),
                ("ClothesWasher", "standard"),
                ("ClothesDryer", "standard"),
                ("CeilingFans", ceiling_fans),
            ]
        )

    @property
    def hot_water_systems(self):
        def get_system(system):
            return OrderedDict(
                [
                    ("Type", self.get_fuel_type(system.fuel_type)),
                    ("EfficiencyUnits", "EF"),
                    ("EfficiencyValue", system.energy_factor),
                    ("StorageCapacity", system.tank_size),
                ]
            )

        data = [get_system(x) for x in self.simulation.hotwaterheater_set.all()]
        return data if len(data) else super(RESNETRem, self).heating_systems

    @property
    def measured_enclosure_tightness(self):
        if self.simulation.infiltration.testing_type not in [3, 4]:
            return super(RESNETRem, self).measured_enclosure_tightness
        if self.simulation.infiltration.units not in [1, 6]:
            return super(RESNETRem, self).measured_enclosure_tightness
        if (
            not self.simulation.infiltration.heating_value
            != self.simulation.infiltration.cooling_value
        ):
            return super(RESNETRem, self).measured_enclosure_tightness

        cfm50 = ela = -1.0
        if self.simulation.infiltration.units == 1:
            cfm50 = self.simulation.infiltration.heating_value
        else:
            ela = self.simulation.infiltration.heating_value

        return OrderedDict(
            [
                ("MeasurementType", "SinglePoint"),
                ("SinglePoint", OrderedDict([("cfm50", cfm50), ("ELA", ela)])),
            ]
        )

    @property
    def duct_systems(self):
        def get_system(system):
            return OrderedDict(
                [
                    ("Type", "ducted"),
                    (
                        "TestedLeakage",
                        OrderedDict(
                            [
                                ("cfm25out", system.return_leakage),
                                ("cfm25total", system.total_leakage),
                                ("Qn", -1.0),
                            ]
                        ),
                    ),
                    ("SupplyDuctsCondSpace", system.supply_area),
                    ("ReturnDuctsCondSpace", system.return_area),
                ]
            )

        data = [
            get_system(x)
            for x in self.simulation.ductsystem_set.filter(leakage_unit__in=[2, 11, 12])
        ]
        return data if len(data) else super(RESNETRem, self).duct_systems

    @property
    def energy_features(self):
        opp = OrderedDict([("CheckOPP", "false")])
        if self.simulation.photovoltaics():
            opp = OrderedDict(
                [
                    ("CheckOPP", "true"),
                    ("Type", "PV"),
                    (
                        "NetPowerProduction",
                        sum(self.simulation.photovoltaics().values_list("peak_power", flat=True)),
                    ),
                ]
            )

        return OrderedDict(
            [
                ("OPP", opp),
                ("SolarHotWaterSystems", OrderedDict([("SHWS", "false")])),
                ("DWHR", OrderedDict([("CheckDWHR", "false")])),
                ("ACHotWaterHeatRecovery", OrderedDict([("ACHWHRecovery", "false")])),
            ]
        )

    @property
    def warnings(self):
        return OrderedDict(
            [
                (
                    "BuildingAttributeFlags",
                    OrderedDict(
                        [
                            (
                                "StoriesAboveGradeValue",
                                self.simulation.building.building_info.number_stories,
                            ),
                            ("AverageCeilingHeightValue", -1.0),
                            ("BelowGradeSlabFloorsValue", -1),
                            ("BelowGradeWallsValue", -1),
                            ("CrawlSpacePerimeterValue", -1.0),
                            ("BasementPerimeterValue", -1.0),
                            ("SlabGradePerimeterValue", -1.0),
                            ("FoundationWallHeightValue", -1.0),
                            ("BasementWallDepthValue", -1.0),
                            ("EnclosureFloorAreaValue", -1.0),
                            ("EnclosureGrossWallAreaValue", -1.0),
                        ]
                    ),
                ),
                (
                    "ApplianceVerificationFlags",
                    OrderedDict(
                        [
                            ("ClothesWashersValue", -1),
                            ("ElectricDryersValue", -1.0),
                            ("GasDryersThermsValue", -1),
                            ("GasDryersKWHValue", -1),
                            ("CWHotWaterSavingsValue", -1.0),
                        ]
                    ),
                ),
            ]
        )


class RESNETEko(RESNETDataBase):
    def get_data(self):
        raise NotImplementedError("Not in place yet")


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

    import os
    from django.apps import apps as django_app

    if not django_app.apps_ready:
        import django

        django.setup()

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", args.settings)

    XSD_DOC = "axis/resnet/sources/ResXSDv2.0.xsd"
    assert os.path.exists(XSD_DOC), "File does not exist {}".format(XSD_DOC)

    from axis.home.models import EEPProgramHomeStatus

    status = EEPProgramHomeStatus.objects.get(id=54239)
    from axis.company.models import Company

    remdata = RESNETRem(
        home_status=status,
        provider_id="1234-123",
        rater_id="1234567",
        provider=Company.objects.get(id=10),
        rater=Company.objects.get(id=10),
        xsd=XSD_DOC,
    )

    etree.fromstring(remdata.xml)

    print(remdata.xml)


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
