from rest_framework import serializers

from axis.geographic.models import Metro, City, County, ClimateZone, Place

__author__ = "Michael Jeffrey"
__date__ = "5/27/13 10:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


class MetroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Metro
        fields = "__all__"


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = "__all__"


class CountySerializer(serializers.ModelSerializer):
    class Meta:
        model = County
        fields = "__all__"


class ClimateZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClimateZone
        fields = "__all__"


class PlaceSerializer(serializers.ModelSerializer):
    """Allows ``model`` kwarg to whitelist which place fields appear."""

    class Meta:
        model = Place
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        model = kwargs.pop("model", None)
        super(PlaceSerializer, self).__init__(*args, **kwargs)

        if model:
            allowed = set(model.DENORMALIZED_PLACE_FIELDS())
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class RawAddressPreferenceSerializerMixin(object):
    """
    Replaces address fields with their ``geocode_response.geocode.raw_*`` counterparts when the
    requesting user's company has specified that this is desired.
    """

    def to_representation(self, instance):
        data = super(RawAddressPreferenceSerializerMixin, self).to_representation(instance)

        for field_name in instance.DENORMALIZED_PLACE_FIELDS():
            field_value = data.get(field_name)
            if field_value:
                data[field_name + "_display"] = field_value

        if instance and instance.geocode_response:
            # ignore display as entered for all NGBS Projects, because
            # for their registration we always use one address
            # and allow user to select even non geocoded address
            try:
                is_hirl_project = instance.homestatuses.filter(
                    customer_hirl_project__isnull=False
                ).exists()
            except AttributeError:
                is_hirl_project = False

            use_raw = (
                "request" in self.context
                and self.context["request"].user.company.display_raw_addresses
                and not is_hirl_project
            )
            has_raw_fields = instance.geocode_response and any(
                (
                    getattr(instance.geocode_response.geocode, k)
                    for k in [
                        "raw_street_line1",
                        "raw_city",
                        "raw_zipcode",
                        "raw_cross_roads",
                    ]
                )
            )
            if use_raw and has_raw_fields:
                geocode = instance.geocode_response.geocode
                for field_name in instance.DENORMALIZED_PLACE_FIELDS():
                    raw_field_name = "raw_%s" % field_name
                    name_field_name = "%s_name" % field_name
                    display_field_name = "%s_display" % field_name

                    if hasattr(geocode, raw_field_name):
                        # OOOOOH BOI!!!!
                        # When a region makes it's way to the page, we attempt to synchronize
                        # the regionObject.object and form, where the form's values takes precedence.
                        # Specifically with raw addresses, that's an issue.
                        # To combat that we're adding a `{field_name}_display`.
                        # We expect the `field_name` to potentially be overwritten,
                        # so the template an choose to use the display value when they're different.
                        data[field_name] = getattr(geocode, raw_field_name)
                        data[display_field_name] = str(getattr(geocode, raw_field_name))

                        # another hack when our raw_state is None when
                        # we have geocode response, so we get state from raw_city.state
                        if raw_field_name == "raw_state" and not getattr(
                            geocode, raw_field_name, None
                        ):
                            raw_city = getattr(geocode, "raw_city", None)
                            if raw_city:
                                data[field_name] = raw_city.state
                                data[display_field_name] = str(raw_city.state)

                        if name_field_name in data:
                            try:
                                accessor = self.fields[name_field_name].source.split(".").pop()
                                data[name_field_name] = getattr(
                                    getattr(geocode, raw_field_name), accessor
                                )
                            except AttributeError:
                                # Field may not have `.source`
                                # Field's source may be more than one level deep
                                pass

        return data

    def get_company_display_raw_addresses(self, obj):
        """Helper for adding a 'company_address_display_type' hint field for the frontend."""
        if (
            self.context.get("request")
            and self.context["request"].user.company.display_raw_addresses
        ):
            return "raw"
        return "geocoded"
