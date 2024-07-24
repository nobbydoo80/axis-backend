"""base.py - Axis"""

__author__ = "Steven K"
__date__ = "8/21/21 13:35"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from django.utils.timezone import now

from rest_framework import serializers
from simulation.enumerations import FuelType, WaterHeaterStyle

from ....eep_programs.washington_code_credit import WACCFuelType as WACCFuelType
from ....models import FastTrackSubmission

from .base import BaseXMLSerializer

log = logging.getLogger(__name__)


class SitePropertySerializer(BaseXMLSerializer):
    def to_representation_default(self, instance):
        try:
            simulation = instance.home_status.floorplan.simulation
        except AttributeError:
            return {}

        return {
            "YRBLT": simulation.project.construction_year,
            "AREA": f"{simulation.conditioned_area:.0f}" if simulation.conditioned_area else "0",
            "NUMFLRS": simulation.floors_on_or_above_grade,
            "FOUNDATION": simulation.foundation_type.label,
        }

    def to_representation_washington_code_credit(self, instance):
        try:
            year_built = instance.home_status.certification_date.year
        except AttributeError:
            year_built = now().year
        return {
            "YRBLT": year_built,
            "AREA": self.context["conditioned_floor_area"],
        }

    def to_representation(self, instance):
        data = super(SitePropertySerializer, self).to_representation(instance)
        properties = [{"Name": name, "Value": value} for (name, value) in data.items()]
        return {"Properties": {"Property": properties}}


class SiteTechnologySerializer(BaseXMLSerializer):
    def get_air_conditioner_measures(self, simulation):
        objects = []
        air_conditioners = simulation.mechanical_equipment.air_conditioners()
        if air_conditioners.exists():
            objects.append("ACCENTRAL")
        return objects

    def get_water_heater_measures(self, simulation):
        objects = []
        water_heaters = simulation.mechanical_equipment.water_heaters()
        if water_heaters.exists():
            if water_heaters.conventional_gas().exists():
                objects.append("GASDHWSTR")
            if water_heaters.tankless_gas().exists():
                objects.append("GASDHWTNKLS")
            if water_heaters.conventional_electric().exists():
                objects.append("ELEDHWSTR")
            if water_heaters.tankless_electric().exists():
                objects.append("ELEDHWTNKLS")
            if water_heaters.heat_pumps().exists():
                if water_heaters.filter(style=WaterHeaterStyle.GROUND_SOURCE_HEAT_PUMP).exists():
                    objects.append("ELEDHW")
                else:
                    objects.append("DHWHP")
            if water_heaters.filter(fuel=FuelType.OIL).exists():
                objects.append("OILDHW")
            if water_heaters.filter(fuel=FuelType.PROPANE).exists():
                objects.append("PROPDHW")
        return objects

    def get_heater_measures(self, simulation):
        objects = []
        heaters = simulation.mechanical_equipment.heaters()
        if heaters.exists():
            if heaters.gas_forced_air().exists():
                objects.append("GASFURN")
            if heaters.gas_hydronic().exists():
                objects.append("GASCFRADHEAT")
            if heaters.gas_ductless().exists():
                objects.append("GASFIREPLC")
            if heaters.electric_forced_air().exists():
                objects.append("ELEFURN")
            if heaters.electric_baseboard().exists():
                objects.append("BASEBOARD")
            elif heaters.electric_hydronic().exists():
                objects.append("ELERADIANT")
            if heaters.filter(fuel=FuelType.OIL).exists():
                objects.append("OILHEAT")
            if heaters.filter(fuel=FuelType.PROPANE).exists():
                objects.append("PROPHEAT")
            if heaters.filter(fuel=FuelType.WOOD).exists():
                objects.append("WOODHEAT")
        return objects

    def get_ashp_measures(self, simulation):
        objects = []
        air_source_heat_pumps = simulation.mechanical_equipment.air_source_heat_pumps()
        if air_source_heat_pumps.exists():
            if air_source_heat_pumps.ducted().exists():
                objects.append("HPDUCTED")
            if air_source_heat_pumps.ductless().exists():
                objects.append("HPDUCTLESS")
        return objects

    def get_gshp_measures(self, simulation):
        objects = []
        gshps = simulation.mechanical_equipment.ground_source_heat_pumps()
        if gshps.exists():
            objects.append("HPGRNDSRC")
        return objects

    def to_representation_default(self, instance):
        try:
            simulation = instance.home_status.floorplan.simulation
        except AttributeError:
            return []
        return list(
            set(
                self.get_air_conditioner_measures(simulation)
                + self.get_water_heater_measures(simulation)
                + self.get_heater_measures(simulation)
                + self.get_ashp_measures(simulation)
                + self.get_gshp_measures(simulation)
            )
        )

    def to_representation_washington_code_credit(self, instance):
        values = ["GASFURN"]
        if self.context.get("water_heater_fuel") == WACCFuelType.ELECTRIC.value:
            values.append("DHWHP")
        elif self.context.get("water_heater_fuel") == WACCFuelType.GAS.value:
            values.append("GASDHWTNKLS")

        return values

    def to_representation(self, instance):
        data = super(SiteTechnologySerializer, self).to_representation(instance)
        properties = [{"@ID": str(idx), "Code": item} for idx, item in enumerate(data, start=1)]
        return {"Technology": properties}


class SiteProvidersSerializer(BaseXMLSerializer):
    def to_representation(self, instance):
        return {
            "ServiceProviders": {
                "ProviderInfo": [
                    {
                        "Service": "ELE",
                        "Provider": self.context.get("electric_utility_code", "N/A"),
                    },
                    {
                        "Service": "GAS",
                        "Provider": self.context.get("gas_utility_code", "N/A"),
                    },
                ]
            }
        }


class SiteSerializer(serializers.ModelSerializer):
    properties = SitePropertySerializer(source="*", read_only=False)
    technologies = SiteTechnologySerializer(source="*", read_only=False)
    providers = SiteProvidersSerializer(source="*", read_only=False)

    class Meta:
        """Meta Options"""

        model = FastTrackSubmission
        fields = ("id", "properties", "technologies", "providers")
        read_only_fields = ("id", "properties", "technologies", "providers")

    def to_internal_value(self, data):
        raise NotImplementedError("Only output supported")

    def to_representation(self, instance):
        data = super(SiteSerializer, self).to_representation(instance)

        address = instance.home_status.home.get_home_address_display_parts(
            include_city_state_zip=True, raw=True
        )

        _address = address.street_line1
        if address.street_line2:
            _address += " Unit {}".format(address.street_line2)

        return {
            "SiteType": "STRUCTURE",
            "SiteMarket": "SINGLEFAM",
            "SiteProperties": data["properties"],
            "SiteTechnologies": data["technologies"],
            "ServiceProviders": data["providers"]["ServiceProviders"],
            "Associations": {
                "Projects": {
                    "Project": {"@ID": instance.home_status.id, "Measures": {"Measure": []}}
                }
            },
            "AddressInfo": {
                "Type": "Site",
                "Address": _address,
                "City": address.city,
                "State": address.state,
                "Zip": address.zipcode,
                "Plus4": None,
            },
        }
