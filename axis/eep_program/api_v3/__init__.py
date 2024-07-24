"""__init__.py: """


__author__ = "Artem Hruzd"
__date__ = "07/07/2020 13:10"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


EEP_PROGRAM_SEARCH_FIELDS = [
    "id",
    "name",
    "owner__name",
]
EEP_PROGRAM_ORDERING_FIELDS = [
    "id",
    "name",
    "is_legacy",
    "is_public",
    "is_qa_program",
    "is_multi_family",
]
EEP_PROGRAM_FILTER_FIELDS = [
    "owner",
    "owner__slug",
    "is_legacy",
    "is_active",
    "is_public",
    "opt_in",
    "is_qa_program",
    "is_multi_family",
    # custom
    "set",
]
