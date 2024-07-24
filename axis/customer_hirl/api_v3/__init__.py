__author__ = "Artem Hruzd"
__date__ = "07/23/2020 20:04"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


HIRL_PROJECT_SEARCH_FIELDS = [
    "id",
    "h_number",
    "home_address_geocode__raw_street_line1",
    "home_address_geocode__raw_street_line2",
    "home_address_geocode__raw_zipcode",
    "home_address_geocode__raw_city__name",
    "home_status__home__street_line1",
    "home_status__home__city__name",
    "home_status__home__city__county__name",
    "registration__registration_user__first_name",
    "registration__registration_user__last_name",
    "registration__eep_program__name",
    "registration__project_name",
    "registration__id",
    "hirllegacycertification__hirl_id",
    "hirllegacycertification__hirl_project_id",
    "registration__subdivision__name",
]

HIRL_PROJECT_ORDERING_FIELDS = [
    "id",
    "h_number",
    "is_include_commercial_space",
    "registration__project_type",
    "registration__state",
    "registration__project_name",
    "home_address_geocode__raw_street_line1",
]

HIRL_PROJECT_FILTER_FIELDS = [
    "is_accessory_dwelling_unit",
    "is_accessory_structure",
    "registration__state",
    "registration__project_type",
    "commercial_space_type",
    "commercial_space_parent",
    "registration__is_build_to_rent",
    "registration__registration_user",
]

HIRL_PROJECT_REGISTRATION_SEARCH_FIELDS = [
    "id",
    "registration_user__first_name",
    "registration_user__last_name",
    "eep_program__name",
    "project_name",
    "projects__h_number",
    "projects__home_address_geocode__raw_street_line1",
    "projects__home_address_geocode__raw_street_line2",
    "projects__home_address_geocode__raw_zipcode",
    "projects__home_address_geocode__raw_city__name",
    "projects__home_status__home__street_line1",
    "projects__home_status__home__city__name",
    "projects__home_status__home__city__county__name",
    "projects__hirllegacycertification__hirl_id",
    "projects__hirllegacycertification__hirl_project_id",
    "subdivision__name",
]

HIRL_PROJECT_REGISTRATION_ORDERING_FIELDS = [
    "id",
    "projects__id",
    "project_name",
    "state",
    "eep_program__name",
]

HIRL_PROJECT_REGISTRATION_FILTER_FIELDS = ["state", "eep_program", "project_type"]


HIRL_GREEN_EENERGY_BADGE_SEARCH_FIELDS = [
    "id",
    "name",
]
HIRL_GREEN_EENERGY_BADGE_ORDERING_FIELDS = [
    "id",
    "name",
]
HIRL_GREEN_EENERGY_BADGE_FILTER_FIELDS = []

COI_DOCUMENT_SEARCH_FIELDS = [
    "id",
]
COI_DOCUMENT_FILTER_FIELDS = []
COI_DOCUMENT_ORDERING_FIELDS = [
    "id",
]

CLIENT_AGREEMENT_SEARCH_FIELDS = [
    "id",
]
CLIENT_AGREEMENT_ORDERING_FIELDS = [
    "id",
]

CLIENT_AGREEMENT_FILTER_FIELDS = ["owner", "company"]


VERIFIER_AGREEMENT_SEARCH_FIELDS = [
    "id",
]
VERIFIER_AGREEMENT_ORDERING_FIELDS = [
    "id",
]
VERIFIER_AGREEMENT_FILTER_FIELDS = ["id"]

PROVIDED_SERVICE_SEARCH_FIELDS = ["id", "name"]
PROVIDED_SERVICE_ORDERING_FIELDS = ["id", "name", "order", "created_at"]
PROVIDED_SERVICE_FILTER_FIELDS = [
    "id",
]
