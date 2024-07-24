"""__init__.py: """

__author__ = "Artem Hruzd"
__date__ = "11/19/2021 7:29 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


ACCREDITATION_SEARCH_FIELDS = [
    "id",
]
ACCREDITATION_ORDERING_FIELDS = [
    "id",
]

INSPECTION_GRADE_SEARCH_FIELDS = [
    "id",
    "user__first_name",
    "user__last_name",
    "user__company__name",
    "approver__first_name",
    "approver__last_name",
    "approver__company__name",
    "notes",
    "qa_status__home_status__home__street_line1",
    "qa_status__home_status__home__city__name",
    "qa_status__home_status__home__city__county__name",
    "qa_status__home_status__eep_program__name",
    "qa_status__home_status__customer_hirl_project__id",
    "qa_status__home_status__customer_hirl_project__h_number",
    "qa_status__home_status__customer_hirl_project__registration__id",
]
INSPECTION_GRADE_ORDERING_FIELDS = [
    "id",
    "letter_grade",
    "numeric_grade",
    "graded_date",
    "updated_at",
    "created_at",
]
