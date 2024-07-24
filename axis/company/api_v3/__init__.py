"""__init__.py: """

__author__ = "Artem Hruzd"
__date__ = "01/03/2020 21:06"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

# common set of search_fields for Company Viewsets
COMPANY_SEARCH_FIELDS = [
    "name",
    "slug",
    "office_phone",
    "street_line1",
    "street_line2",
    "zipcode",
    "state",
    "city__name",
    "city__county__name",
    "city__county__state",
    "default_email",
    "eto_account__account_number",
    "eto_account__ccb_number",
]
# common set of ordering_fields for Company Viewsets
COMPANY_ORDERING_FIELDS = [
    "name",
    "street_line1",
    "state",
    "city__county__name",
    "city__county__state",
    "office_phone",
    "eto_account",
]

# common set of FilterSet fields for Company Viewsets
COMPANY_FILTER_FIELDS = [
    "name",
    "company_type",
    "state",
    "city__county__state",
    "city__country",
]

COMPANY_COMMON_SERIALIZER_FIELDS = (
    "id",
    "name",
    "company_type",
    # Place fields
    "street_line1",
    "street_line2",
    "state",
    "metro",
    "latitude",
    "longitude",
    "zipcode",
    "city",
    "city_info",
    "confirmed_address",
    "address_override",
    "geocode_response",
    "shipping_geocode",
    "shipping_geocode_info",
    "shipping_geocode_response",
    "shipping_geocode_response_info",
    # misc
    "office_phone",
    "home_page",
    "description",
    "default_email",
    "inspection_grade_type",
    "logo",
    "countries",
    # Customer ETO
    "eto_account",
    "eto_account_info",
    # Overall
    "is_active",
    "is_public",
    # Customer Options
    "is_customer",
    "is_eep_sponsor",
    "hirlcompanyclient",
    # Auto add relationships
    "auto_add_direct_relationships",
    "display_raw_addresses",
    # Annotations
    "total_users",
    "total_company_admin_users",
    "active_customer_hirl_builder_agreements_count",
    "active_coi_document_count",
    # custom fields
    "sponsor_slugs",
)
