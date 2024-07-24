"""api.py: Community serializers"""


from rest_framework import serializers

from axis.core.utils import make_safe_field
from axis.geographic.models import City
from axis.geographic.serializers import RawAddressPreferenceSerializerMixin
from .models import Community

__author__ = "Michael Jeffrey"
__date__ = "5/27/13 10:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


class CommunitySerializer(RawAddressPreferenceSerializerMixin, serializers.ModelSerializer):
    city = serializers.PrimaryKeyRelatedField(queryset=City.objects.all())
    slug = serializers.CharField(read_only=True)

    city_name = make_safe_field(serializers.CharField)(source="city.name", read_only=True)
    county_name = make_safe_field(serializers.CharField)(source="county.name", read_only=True)
    metro_name = make_safe_field(serializers.CharField)(source="metro.name", read_only=True)
    country_name = make_safe_field(serializers.CharField)(
        source="city.country.name", read_only=True
    )

    raw_address = serializers.CharField(
        source="geocode_response.geocode.raw_address", read_only=True
    )
    geocoded_address = serializers.SerializerMethodField()
    company_display_raw_addresses = serializers.SerializerMethodField()

    axis_id = serializers.SerializerMethodField()

    class Meta:
        model = Community
        fields = (
            "address_override",
            "city",
            "confirmed_address",
            "county",
            "created_date",
            "cross_roads",
            "is_active",
            "metro",
            "modified_date",
            "name",
            "slug",
            "state",
            "website",
            "is_multi_family",
            # Hidden
            "id",
            "geocode_response",
            "confirmed_address",
            "latitude",
            "longitude",
            # Virtual-readonly
            "city_name",
            "metro_name",
            "county_name",
            "country_name",
            "raw_address",
            "geocoded_address",
            "axis_id",
            "company_display_raw_addresses",
        )
        read_only_fields = (
            "id",
            "county",
            "state",
            "confirmed_address",
            "latitude",
            "longitude",
            "created_date",
            "modified_date",
        )

    def get_geocoded_address(self, obj):
        if obj.pk:
            return f"{obj.cross_roads} {obj.city}"

    def get_axis_id(self, obj):
        if obj.pk:
            return obj.get_id()
        return None
