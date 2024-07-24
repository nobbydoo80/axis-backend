"""serializers.py: """

from rest_framework import serializers
from axis.community.models import Community
from axis.relationship.models import Relationship
from axis.geographic.api_v3.serializers import CitySerializer, MetroSerializer

__author__ = "Artem Hruzd"
__date__ = "06/23/2020 14:45"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
    "Naruhito Kaide",
]


class CommunitySerializerMixin(metaclass=serializers.SerializerMetaclass):
    total_subdivisions = serializers.IntegerField(read_only=True)
    city_info = CitySerializer(source="city", read_only=True)

    def create(self, validated_data):
        company = super(CommunitySerializerMixin, self).create(validated_data)
        Relationship.objects.validate_or_create_relations_to_entity(
            entity=company, direct_relation=self.context["request"].user.company
        )
        return company


class CommunityFlatListSerializer(serializers.ModelSerializer):
    """
    Flat optimized list of communities to display
    """

    city_metro = serializers.SerializerMethodField()

    class Meta:
        model = Community
        fields = (
            "id",
            "name",
            "city_metro",
            "cross_roads",
        )

    def get_city_metro(self, community):
        city = getattr(community, "city", None)
        metro = getattr(community, "metro", None)
        city_metro_line = ""
        if city and metro:
            city_metro_line = f"{community.city.name} ({community.metro.name})"
        elif city:
            city_metro_line = f"{community.city.name}"
        return city_metro_line


class CommunityMeta:
    """
    Base Meta model for Community with common fields
    """

    model = Community
    fields = (
        "id",
        "name",
        "website",
        # Misc
        "slug",
        "is_active",
        "city",
        "city_info",
        # GeneralPlacedModel
        "cross_roads",
        "is_multi_family",
        "geocode_response",
        "place",
        "climate_zone",
        "confirmed_address",
        "address_override",
        "state",
        "metro",
        "metro_info",
        "total_subdivisions",
    )
    read_only_fields = ("slug",)


class CommunityInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Community
        fields = (
            "id",
            "name",
            "website",
            # Misc
            "slug",
            "is_active",
            "city",
            # GeneralPlacedModel
            "cross_roads",
            "is_multi_family",
            "geocode_response",
            "place",
            "climate_zone",
            "confirmed_address",
            "address_override",
            "state",
            "metro",
        )


class BasicCommunitySerializer(CommunitySerializerMixin, serializers.ModelSerializer):
    """Basic control of Community instance."""

    city_info = CitySerializer(read_only=True, source="city")
    metro_info = MetroSerializer(read_only=True, source="metro")

    class Meta(CommunityMeta):
        read_only_fields = CommunityMeta.read_only_fields + ("is_active", "confirmed_address")


class CommunitySerializer(CommunitySerializerMixin, serializers.ModelSerializer):
    """Allows full control of Community instance."""

    city_info = CitySerializer(read_only=True, source="city")
    metro_info = MetroSerializer(read_only=True, source="metro")

    class Meta(CommunityMeta):
        pass
