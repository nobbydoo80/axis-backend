"""city.py: """


__author__ = "Artem Hruzd"
__date__ = "01/03/2020 21:11"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from axis.geocoder.models import GeocodeResponse
from axis.geographic.models import City, County, COUNTRIES
from .country import CountrySerializer
from .county import CountySerializer, CountyDetailSerializer
from ...utils.country import get_usa_default, resolve_country


class BaseCitySerializer(serializers.ModelSerializer):
    county = serializers.PrimaryKeyRelatedField(
        queryset=County.objects.all(), required=False, allow_null=True, default=None
    )
    country = serializers.ChoiceField(choices=COUNTRIES, default="US")
    legal_statistical_area_description = serializers.CharField(
        required=False, allow_null=True, default=None
    )
    place_fips = serializers.CharField(required=False, allow_null=True, default=None)
    ansi_code = serializers.CharField(required=False, allow_null=True, default=None)
    land_area_meters = serializers.FloatField(required=False, allow_null=True, default=0.0)
    water_area_meters = serializers.FloatField(required=False, allow_null=True, default=0.0)
    latitude = serializers.FloatField(required=False, allow_null=True, default=0.0)
    longitude = serializers.FloatField(required=False, allow_null=True, default=0.0)
    geocode_response = serializers.PrimaryKeyRelatedField(
        queryset=GeocodeResponse.objects.all(), required=False, allow_null=True, default=None
    )

    class Meta:
        model = City
        fields = (
            "id",
            "name",
            "county",
            "country",
            "legal_statistical_area_description",
            "place_fips",
            "ansi_code",
            "land_area_meters",
            "water_area_meters",
            "latitude",
            "longitude",
            "geocode_response",
        )
        read_only_fields = ("id",)

    def validate_country(self, attr):
        return resolve_country(attr)

    def validate(self, attrs):
        if "country" not in attrs or attrs.get("country") is None:
            attrs["country"] = get_usa_default()

        if attrs["country"].abbr != "US" and attrs["county"]:
            raise ValidationError(f"You cannot combine country {attrs['country']} with a county")

        if attrs["country"].abbr == "US" and not attrs.get("county"):
            raise ValidationError("You must provide a county when using USA")

        if "place_fips" not in attrs or attrs.get("place_fips") is None:
            attrs["place_fips"] = 9900000
            cid = City.objects.filter(place_fips__startswith="990").order_by("-id").first()
            if cid:
                attrs["place_fips"] = int(cid.place_fips) + 1

        if "ansi_code" not in attrs or attrs.get("ansi_code") is None:
            attrs["ansi_code"] = attrs["place_fips"]

        if (
            "legal_statistical_area_description" not in attrs
            or attrs.get("legal_statistical_area_description") is None
        ):
            desc = f"Unregistered {attrs['name']} ({attrs['place_fips']})"
            attrs["legal_statistical_area_description"] = desc

        if "land_area_meters" not in attrs or attrs.get("land_area_meters") is None:
            attrs["land_area_meters"] = 0.0
        if "water_area_meters" not in attrs or attrs.get("water_area_meters") is None:
            attrs["water_area_meters"] = 0.0
        if "latitude" not in attrs or attrs.get("latitude") is None:
            attrs["latitude"] = 0.0
        if "longitude" not in attrs or attrs.get("longitude") is None:
            attrs["longitude"] = 0.0
        return attrs

    def create(self, validated_data):
        defaults = {
            "name": validated_data.pop("name"),
            "place_fips": validated_data.pop("place_fips"),
            "ansi_code": validated_data.pop("ansi_code"),
            "legal_statistical_area_description": validated_data.pop(
                "legal_statistical_area_description"
            ),
            "land_area_meters": validated_data.pop("land_area_meters"),
            "water_area_meters": validated_data.pop("water_area_meters"),
            "latitude": validated_data.pop("latitude"),
            "longitude": validated_data.pop("longitude"),
        }

        ModelClass = self.Meta.model
        validated_data["name__iexact"] = defaults["name"]
        return ModelClass._default_manager.get_or_create(**validated_data, defaults=defaults)[0]


class CitySerializer(BaseCitySerializer):
    county_info = CountySerializer(source="county", read_only=True)
    country_info = CountrySerializer(source="country", read_only=True)

    class Meta:
        model = City
        fields = (
            "id",
            "name",
            "county",
            "county_info",
            "country",
            "country_info",
            "place_fips",
            "legal_statistical_area_description",
            "ansi_code",
            "land_area_meters",
            "water_area_meters",
            "latitude",
            "longitude",
        )
        read_only_fields = ("id", "county_info")


class CityDetailSerializer(CitySerializer):
    county_info = CountyDetailSerializer(source="county")
    country_info = CountrySerializer(source="country")
