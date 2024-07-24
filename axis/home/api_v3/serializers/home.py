"""home.py - Axis"""

__author__ = "Steven K"
__date__ = "7/16/21 12:33"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from rest_framework import serializers

from axis.geocoder.api_v3.serializers import GeocodeMatchesSerializer
from axis.geocoder.models import GeocodeResponse
from axis.geographic.api_v3.serializers import CitySerializer
from axis.geographic.models import City
from axis.home.models import Home
from axis.subdivision.api_v3.serializers import SubdivisionInfoSerializer
from axis.home.models import EEPProgramHomeStatus
from axis.eep_program.api_v3.serializers import EEPProgramInfoSerializer

log = logging.getLogger(__name__)


class HomeSerializerMixin(metaclass=serializers.SerializerMetaclass):
    subdivision_info = SubdivisionInfoSerializer(source="subdivision")


class HomeMeta:
    """
    Base Meta model for Home with common fields
    """

    model = Home
    fields = (
        "id",
        "slug",
        "subdivision",
        "subdivision_info",
        "is_custom_home",
        "is_active",
        "bulk_uploaded",
        "street_line1_profile",
        "modified_date",
        "created_date",
    )


class HomeInfoSerializer(serializers.ModelSerializer):
    home_address = serializers.SerializerMethodField(
        help_text="String representation of home object address"
    )
    city_info = CitySerializer(source="city", read_only=True)

    class Meta:
        model = Home
        fields = (
            "id",
            "street_line1",
            "street_line2",
            "city",
            "city_info",
            "zipcode",
            "home_address",
        )

    def get_home_address(self, home):
        return home.get_home_address_display()


class HomeSerializer(HomeSerializerMixin, serializers.ModelSerializer):
    """Basic control of Home instance."""

    class Meta(HomeMeta):
        pass


class BasicHomeSerializer(HomeSerializerMixin, serializers.ModelSerializer):
    """Allows full control of Home instance."""

    class Meta(HomeMeta):
        pass


class HomeRecentlyUpdatedFileObservationSerializer(serializers.Serializer):
    home_id = serializers.IntegerField()
    home_street_line1 = serializers.CharField()
    home_street_line2 = serializers.CharField()
    observation_user = serializers.IntegerField()
    observation_user_first_name = serializers.CharField()
    observation_user_last_name = serializers.CharField()
    observations = serializers.ListSerializer(
        child=serializers.CharField(), help_text="List of observation type names"
    )
    observation_created_on = serializers.DateTimeField()

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError


class HomeAddressIsUniqueRequestDataSerializer(serializers.Serializer):
    home = serializers.PrimaryKeyRelatedField(
        queryset=Home.objects.all(),
        allow_null=True,
        required=False,
        default=None,
        help_text="If provided exclude this home instance from search",
    )
    lot_number = serializers.CharField(
        required=False, allow_null=True, allow_blank=True, default=None
    )
    street_line1 = serializers.CharField()
    street_line2 = serializers.CharField(
        allow_blank=True, allow_null=True, required=False, default=""
    )
    is_multi_family = serializers.BooleanField(default=False)
    city = serializers.PrimaryKeyRelatedField(queryset=City.objects.all())
    zipcode = serializers.CharField()
    geocode_response = serializers.IntegerField(allow_null=True, required=False)

    @classmethod
    def home_address_is_unique(
        cls,
        instance: Home,
        street_line1: str,
        city: City | int,
        zipcode: str,
        state: str | None = None,
        country: str | None = None,
        street_line2: str | None = None,
        lot_number: str | None = None,
        is_multi_family: bool = False,
        second_pass: bool = False,
        geocode_response: GeocodeResponse | None | int = None,
    ):
        if isinstance(city, int):
            city = City.objects.get(id=city)

        if state is None and city.state:
            state = city.state
        elif country is None and city.country.abbr != "US":
            country = city.country.abbr

        if isinstance(geocode_response, int):
            geocode_response = GeocodeResponse.objects.get(id=geocode_response)

        if instance and instance.pk and lot_number is None:
            lot_number = instance.lot_number

        similar_homes_kwargs = {
            "lot_number": lot_number,
            "street_line1": street_line1,
            "street_line2": street_line2,
            "city": city,
            "state": state,
            "country": country,
            "zipcode": zipcode,
            "geocode_response": geocode_response,
        }

        similar_homes = Home.objects.filter_similar(**similar_homes_kwargs)

        if instance and instance.pk:
            similar_homes = similar_homes.exclude(pk=instance.pk)

        try:
            home = similar_homes.get()
        except Home.DoesNotExist:
            if not second_pass and geocode_response is None:
                log.debug("Second Pass - Geocoding")
                geocode_kwargs = similar_homes_kwargs.copy()
                if is_multi_family or not street_line2:
                    geocode_kwargs.pop("street_line2")
                # We should have one but double check ourselves.
                geo_data = similar_homes_kwargs.copy()
                geo_data["city"] = geo_data["city"].id
                geo_data.pop("geocode_response")
                geo_serializer = GeocodeMatchesSerializer(data=geo_data)
                geo_serializer.is_valid(raise_exception=True)
                geo_address, create = geo_serializer.save()
                valid_responses = geo_address.get_valid_responses()
                geocode_response = valid_responses[0] if len(valid_responses) else None
                if not create:
                    return HomeAddressIsUniqueRequestDataSerializer().home_address_is_unique(
                        instance,
                        second_pass=True,
                        lot_number=lot_number,
                        street_line1=street_line1,
                        street_line2=street_line2,
                        city=city,
                        country=country,
                        state=state,
                        zipcode=zipcode,
                        geocode_response=geocode_response,
                    )
            return True, None
        except Home.MultipleObjectsReturned:
            return False, similar_homes.first()
        else:
            return False, home

    def get_home_is_unique(self, **kwargs):
        assert hasattr(
            self, "_errors"
        ), "You must call `.is_valid()` before calling `.get_home_is_unique()`."

        validated_data = {**self.validated_data, **kwargs}
        # Bake in the state
        _state = validated_data["city"].county.state if validated_data["city"].county else None
        validated_data["state"] = _state
        # Bake in the country
        validated_data["country"] = validated_data["city"].country
        validated_data["instance"] = validated_data.pop("home", None)
        return self.home_address_is_unique(**validated_data)

    def save(self, validated_data):
        raise NotImplementedError("You probably want to sue `get_home_is_unique` method")

    def create(self, validated_data):
        raise NotImplementedError("You probably want to sue `get_home_is_unique` method")

    def update(self, instance, validated_data):
        raise NotImplementedError("You probably want to sue `get_home_is_unique` method")


class HomeEEPProgramStatusMeta:
    """
    EEPProgramHomeStatus data for Home
    """

    model = EEPProgramHomeStatus
    fields = (
        "id",
        "state",
        "eep_program",
        "certification_date",
        "pct_complete",
        "is_billable",
        "modified_date",
        "created_date",
    )


class HomeEEPProgramStatusSerializer(serializers.ModelSerializer):
    eep_program = EEPProgramInfoSerializer()

    class Meta(HomeEEPProgramStatusMeta):
        pass


class HomeSubdivisionEEPSerializer(HomeSerializerMixin, serializers.ModelSerializer):
    """Home Statuses per Home with Subdivision data."""

    home_address = serializers.SerializerMethodField(
        help_text="String representation of home object address"
    )
    eep_programs = serializers.SerializerMethodField()

    class Meta(HomeMeta):
        fields = HomeMeta.fields + ("home_address", "eep_programs")

    def get_eep_programs(self, data: Home) -> list:
        user = self.context.get("user")
        items = data.homestatuses.filter_by_user(user=user)
        serializer = HomeEEPProgramStatusSerializer(instance=items, many=True)
        return serializer.data

    def get_home_address(self, data: Home) -> str:
        company = self.context.get("user").company if self.context.get("user") else None
        return data.get_home_address_display(company=company)
