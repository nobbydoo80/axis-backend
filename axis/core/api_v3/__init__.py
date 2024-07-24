"""__init__.py: """


__author__ = "Artem Hruzd"
__date__ = "01/06/2020 12:21"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
    "Naruhito Kaide",
]

# common set of search_fields for User Viewsets
USER_SEARCH_FIELDS = [
    "first_name",
    "last_name",
    "email",
    "title",
    "alt_phone",
    "cell_phone",
    "work_phone",
    "rater_id",
    "company__name",
    "company__slug",
    "company__street_line1",
    "company__street_line2",
    "company__city__name",
    "company__city__county__name",
    "company__city__county__state",
    "company__zipcode",
    "username",
    "accreditations__name",
]
FIND_VERIFIER_LIST_SEARCH_FIELDS = [
    "first_name",
    "last_name",
    "company__name",
]
# common set of ordering_fields for User Viewsets
USER_ORDERING_FIELDS = ["id", "first_name", "last_name", "company__name"]

# common set of FilterSet fields for User Viewsets
USER_FILTER_FIELDS = [
    "company",
    "company__slug",
    "company__company_type",
    "is_active",
    "is_public",
    "is_company_admin",
    # customer HIRL profile
    "hirluserprofile__is_qa_designee",
]


CONTACT_CARD_FILTER_FIELDS = ["company", "user", "protected"]


RATER_ROLE_SEARCH_FIELDS = ["id", "title", "slug"]
RATER_ROLE_FILTER_FIELDS = ["id", "is_hidden"]
RATER_ROLE_ORDERING_FIELDS = ["id", "title", "slug"]
