"""__init__.py: """

__author__ = "Artem Hruzd"
__date__ = "07/16/2020 20:48"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


QA_STATUS_SEARCH_FIELDS = [
    "id",
    "home_status__home__street_line1",
    "home_status__home__city__name",
    "home_status__home__city__county__name",
    "home_status__eep_program__name",
    "home_status__customer_hirl_project__id",
    "home_status__customer_hirl_project__h_number",
    "home_status__customer_hirl_project__registration__id",
    "home_status__customer_hirl_rough_verifier__first_name",
    "home_status__customer_hirl_rough_verifier__last_name",
    "home_status__customer_hirl_final_verifier__first_name",
    "home_status__customer_hirl_final_verifier__last_name",
    "home_status__customer_hirl_project__registration__registration_user__first_name",
    "home_status__customer_hirl_project__registration__registration_user__last_name",
]
QA_STATUS_ORDERING_FIELDS = [
    "id",
    "home_status__home__street_line1",
    "home_status__eep_program__name",
    "home_status__state",
    "requirement__type",
    "state",
]
QA_STATUS_FILTER_FIELDS = [
    "state",
    "requirement__type",
    "home_status__state",
    "home_status__customer_hirl_project__registration",
    "home_status__customer_hirl_project",
    "home_status__customer_hirl_project__registration__builder_organization",
    "home_status__customer_hirl_project__registration__architect_organization",
    "home_status__customer_hirl_project__registration__developer_organization",
    "home_status__customer_hirl_project__registration__community_owner_organization",
    "home_status__customer_hirl_project__registration__registration_user__company",
]

OBSERVATION_SEARCH_FIELDS = [
    "id",
]
OBSERVATION_ORDERING_FIELDS = [
    "id",
]
OBSERVATION_FILTER_FIELDS = []

QA_NOTE_SEARCH_FIELDS = [
    "id",
    "user__first_name",
    "user__last_name",
    "observation__observation_type__name",
]
QA_NOTE_ORDERING_FIELDS = [
    "id",
]

QA_NOTE_FILTER_FIELDS = []
