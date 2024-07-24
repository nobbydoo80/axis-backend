"""serializer_fields.py: """

__author__ = "Artem Hruzd"
__date__ = "06/02/2022 01:10"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from rest_framework import serializers


class HIRLProjectAddressDisplayField(serializers.ReadOnlyField):
    """
    Lightweight field to display HIRLProject flatten address. Require following select_related fields:
    "hirl_project__home_address_geocode",
    "hirl_project__home_address_geocode__raw_city",
    "hirl_project__home_address_geocode__raw_city__county",
    "hirl_project__home_address_geocode_response",
    "hirl_project__home_address_geocode_response__geocode",

    Example usage:
    HIRLProjectAddressDisplayField(
        source="home_status.customer_hirl_project"
    )
    """

    def to_representation(self, instance):
        home_address_geocode = getattr(instance, "home_address_geocode", None)
        home_address_geocode_response = getattr(instance, "home_address_geocode_response", None)
        address = ""
        if home_address_geocode_response:
            address += f"{home_address_geocode_response.broker.place.street_line1}"

            if home_address_geocode_response.broker.place.street_line2:
                address += f" {home_address_geocode_response.broker.place.street_line2}"

            address += f", {home_address_geocode_response.broker.place.city}"
            address += f", {home_address_geocode_response.broker.place.county}"
            address += f", {home_address_geocode_response.broker.place.state}"
            address += f" {home_address_geocode_response.broker.place.zipcode}"
            return address

        if home_address_geocode:
            address += f"{home_address_geocode.raw_street_line1}"

            if home_address_geocode.raw_street_line2:
                address += f" {home_address_geocode.raw_street_line2}"

            address += f", {home_address_geocode.raw_city.name}"
            if home_address_geocode.raw_city.country.abbr != "US":
                address += f", {home_address_geocode.raw_city.country.name}"
            else:
                address += f", {home_address_geocode.raw_city.county.name}"
                address += f", {home_address_geocode.raw_city.county.state}"
            address += f" {home_address_geocode.raw_zipcode}"
            return address
        return address

    def to_internal_value(self, data):
        return data
