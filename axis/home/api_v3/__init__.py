"""__init__.py: """

__author__ = "Artem Hruzd"
__date__ = "07/07/2020 13:10"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


EEP_PROGRAM_HOME_STATUS_SEARCH_FIELDS = ["id", "state", "home__id"]
EEP_PROGRAM_HOME_STATUS_ORDERING_FIELDS = [
    "id",
    "home_id",
    "home__subdivision",
    "home__homestatuses__eep_program",
    "home__homestatuses__state",
    "eep_program__name",
    "home__street_line1",
    "certification_date",
    "home__subdivision__name",
]

EEP_PROGRAM_HOME_STATUS_SEARCH_FIELDS = [
    "id",
    "state",
    "certification_date",
    "home__street_line1",
    "home__city__name",
    "home__city__county__name",
    "home__zipcode",
    "customer_hirl_project__id",
    "customer_hirl_project__h_number",
    "customer_hirl_project__home_address_geocode__raw_street_line1",
    "customer_hirl_project__home_address_geocode__raw_street_line2",
    "customer_hirl_project__home_address_geocode__raw_zipcode",
    "customer_hirl_project__home_address_geocode__raw_city__name",
    "customer_hirl_project__registration__registration_user__first_name",
    "customer_hirl_project__registration__registration_user__last_name",
    "customer_hirl_project__registration__eep_program__name",
    "customer_hirl_project__registration__project_name",
    "customer_hirl_project__registration__id",
    "customer_hirl_project__hirllegacycertification__hirl_id",
    "customer_hirl_project__hirllegacycertification__hirl_project_id",
    "customer_hirl_project__registration__subdivision__name",
    "eep_program__name",
    "home__subdivision__name",
]
EEP_PROGRAM_HOME_STATUS_FILTER_FIELDS = [
    "state",
    "home__city__county__state",
    "eep_program__owner__slug",
    "customer_hirl_project__registration",
]


HOME_SEARCH_FIELDS = [
    "id",
]
HOME_ORDERING_FIELDS = [
    "id",
]
HOME_FILTER_FIELDS = [
    "subdivision",
    "homestatuses__eep_program",
    "homestatuses__qastatus__requirement__type",
    "homestatuses__state",
    "homestatuses__rater_of_record",
    "homestatuses__qastatus__correction_types",
    "city",
    "metro",
    "state",
]
