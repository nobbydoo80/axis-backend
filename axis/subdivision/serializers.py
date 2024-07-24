from rest_framework import serializers

from axis.core.utils import make_safe_field
from axis.geographic.serializers import RawAddressPreferenceSerializerMixin
from axis.customer_eto.serializers import PermitAndOccupancySettingsFieldsMixin
from .models import Subdivision, EEPProgramSubdivisionStatus

__author__ = "Autumn Valenta"
__date__ = "09-30-14  2:39 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


class SubdivisionSerializer(
    RawAddressPreferenceSerializerMixin,
    PermitAndOccupancySettingsFieldsMixin,
    serializers.ModelSerializer,
):
    """Read/write serializer for new and existing subdivisions."""

    city_name = serializers.CharField(source="city.name", read_only=True)
    community_name = make_safe_field(serializers.CharField)(source="community.name", read_only=True)
    community_url = make_safe_field(serializers.CharField)(
        source="community.get_absolute_url", read_only=True
    )
    community_is_multi_family = make_safe_field(serializers.BooleanField)(
        source="community.is_multi_family", read_only=True
    )
    builder_org_name = make_safe_field(serializers.CharField)(
        source="builder_org.name", read_only=True
    )
    builder_org_url = make_safe_field(serializers.CharField)(
        source="builder_org.get_absolute_url", read_only=True
    )

    sample_eligibility = serializers.SerializerMethodField()

    # Extended related fields
    county = serializers.CharField(source="city.county_id", read_only=True)
    county_name = make_safe_field(serializers.CharField)(source="city.county.name", read_only=True)
    metro = serializers.CharField(source="city.county.metro_id", read_only=True)
    metro_name = make_safe_field(serializers.CharField)(
        source="city.county.metro.name", read_only=True
    )
    country_name = serializers.CharField(source="city.country.name", read_only=True)

    homes_count = serializers.SerializerMethodField()
    samplesets_count = serializers.SerializerMethodField()

    raw_address = serializers.CharField(
        source="geocode_response.geocode.raw_address", read_only=True
    )
    geocoded_address = serializers.SerializerMethodField()
    company_display_raw_addresses = serializers.SerializerMethodField()

    axis_id = serializers.SerializerMethodField()

    # ETO Permit and Occupancy fields
    reeds_crossing_compliance_option = serializers.SerializerMethodField()
    rosedale_parks_compliance_option = serializers.SerializerMethodField()

    fuel_types = serializers.SerializerMethodField()
    # electric_only = serializers.SerializerMethodField()

    class Meta:
        model = Subdivision
        fields = (
            "address_override",
            "builder_org",
            "builder_name",
            "confirmed_address",
            "created_date",
            "cross_roads",
            "is_active",
            "latitude",
            "longitude",
            "modified_date",
            "name",
            "slug",
            "state",
            "use_metro_sampling",
            "use_sampling",
            "city",
            "community",
            "is_multi_family",
            # Hidden
            "id",
            "geocode_response",
            "confirmed_address",
            "latitude",
            "longitude",
            # Virtual-readonly
            "city_name",
            "county",
            "county_name",
            "metro",
            "metro_name",
            "country_name",
            "builder_org_name",
            "community_name",
            "sample_eligibility",
            "homes_count",
            "samplesets_count",
            "raw_address",
            "geocoded_address",
            "community_url",
            "builder_org_url",
            "axis_id",
            "community_is_multi_family",
            "company_display_raw_addresses",
            "fuel_types",
            # 'electric_only',
            # ETO Permit and Occupancy fields
            "reeds_crossing_compliance_option",
            "rosedale_parks_compliance_option",
        )
        read_only_fields = (
            "id",
            "slug",
            "created_date",
            "modified_date",
            "confirmed_address",
            "latitude",
            "longitude",
        )

    def validate(self, attrs):
        if not any([attrs["city"], attrs["community"]]):
            raise serializers.ValidationError("A city or community must be provided.")

        if attrs["community"] and attrs["community"].is_multi_family != attrs["is_multi_family"]:
            raise serializers.ValidationError(
                {
                    "is_multi_family": "Multi-family setting must match community.",
                }
            )

        return attrs

    def get_sample_eligibility(self, obj):
        return obj.get_sample_eligibility(self.context["request"].user.company)

    def get_homes_count(self, obj: Subdivision) -> int:
        try:
            return obj.home_set.filter_by_user(self.context["request"].user).count()
        except ValueError:
            return 0

    def get_samplesets_count(self, obj):
        from axis.sampleset.models import SampleSet

        return SampleSet.objects.filter(home_statuses__home__subdivision=obj).distinct().count()

    def get_geocoded_address(self, obj):
        if obj.pk:
            return f"{obj.city} {obj.cross_roads}"

    def get_axis_id(self, obj):
        if obj.pk:
            return obj.get_id()
        return None

    def get_fuel_types(self, obj):
        if not obj.id:
            return ""
        return obj.get_fuel_types(self.context["request"].user)

    def get_electric_only(self, obj):
        if not obj.id:
            return ""
        return "Yes" if self.get_fuel_types(obj) == "Electric" else "No"


class SubdivisionEEPProgramSerializer(serializers.ModelSerializer):
    eep_program_url = serializers.CharField(source="eep_program.get_absolute_url", read_only=True)

    class Meta:
        model = EEPProgramSubdivisionStatus
        fields = "__all__"
        read_only_fields = ("id", "company", "date_added")
