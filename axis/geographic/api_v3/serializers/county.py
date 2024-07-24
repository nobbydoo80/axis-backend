"""country.py: """


from rest_framework import serializers
from axis.geographic.models import County
from .metro import MetroSerializer
from .climate_zone import ClimateZoneSerializer

__author__ = "Artem Hruzd"
__date__ = "01/03/2020 22:05"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class CountySerializer(serializers.ModelSerializer):
    class Meta:
        model = County
        fields = (
            "id",
            "name",
            "state",
            "county_fips",
            "county_type",
            "legal_statistical_area_description",
            "ansi_code",
            "land_area_meters",
            "water_area_meters",
            "latitude",
            "longitude",
            "metro",
            "climate_zone",
        )
        read_only_fields = ("id",)


class CountyDetailSerializer(serializers.ModelSerializer):
    metro_info = MetroSerializer(source="metro")
    climate_zone_info = ClimateZoneSerializer(source="climate_zone")

    class Meta:
        model = County
        fields = (
            "id",
            "name",
            "state",
            "county_fips",
            "county_type",
            "legal_statistical_area_description",
            "ansi_code",
            "land_area_meters",
            "water_area_meters",
            "latitude",
            "longitude",
            "metro",
            "metro_info",
            "climate_zone",
            "climate_zone_info",
        )
        read_only_fields = ("id", "climate_zone_info", "metro_info")
