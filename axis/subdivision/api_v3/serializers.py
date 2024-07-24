"""serializers.py: """

__author__ = "Artem Hruzd"
__date__ = "06/24/2020 10:36"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from rest_framework import serializers

from axis.company.api_v3.serializers import CompanyInfoSerializer
from axis.geographic.api_v3.serializers import CitySerializer
from axis.community.api_v3.serializers import CommunityInfoSerializer
from axis.subdivision.models import Subdivision


class SubdivisionSerializerMixin(metaclass=serializers.SerializerMetaclass):
    city_info = CitySerializer(read_only=True, source="city")
    builder_org_info = CompanyInfoSerializer(source="builder_org", read_only=True)
    community_info = CommunityInfoSerializer(read_only=True, source="community")

    def create(self, validated_data):
        subdivision = super(SubdivisionSerializerMixin, self).create(validated_data)
        subdivision.set_builder(subdivision.builder_org, user=self.context["request"].user)
        return subdivision

    def update(self, validated_data):
        subdivision = super(SubdivisionSerializerMixin, self).update(validated_data)
        subdivision.set_builder(subdivision.builder_org, user=self.context["request"].user)
        return subdivision


class SubdivisionMeta:
    """
    Base Meta model for Subdivision with common fields
    """

    model = Subdivision
    fields = (
        "id",
        "name",
        "builder_name",
        "builder_org",
        "builder_org_info",
        "community",
        "community_info",
        "city",
        "city_info",
        "eep_programs",
        "floorplans",
        "use_sampling",
        "use_metro_sampling",
        "cross_roads",
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
        # Misc
        "is_active",
        "slug",
        "modified_date",
        "created_date",
    )
    read_only_fields = ("slug", "modified_date", "created_date")


class SubdivisionInfoSerializer(serializers.ModelSerializer):
    city_info = CitySerializer(read_only=True, source="city")
    community_info = CommunityInfoSerializer(read_only=True, source="community")

    class Meta:
        model = Subdivision
        fields = (
            "id",
            "name",
            "builder_name",
            "builder_org",
            "community",
            "community_info",
            "city",
            "city_info",
            "eep_programs",
            "floorplans",
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
            # Misc
            "is_active",
            "slug",
            "modified_date",
            "created_date",
        )


class BasicSubdivisionSerializer(SubdivisionSerializerMixin, serializers.ModelSerializer):
    """Basic control of Subdivision instance."""

    class Meta(SubdivisionMeta):
        read_only_fields = SubdivisionMeta.read_only_fields + ("is_active",)


class SubdivisionSerializer(SubdivisionSerializerMixin, serializers.ModelSerializer):
    """Allows full control of Subdivision instance."""

    class Meta(SubdivisionMeta):
        pass
