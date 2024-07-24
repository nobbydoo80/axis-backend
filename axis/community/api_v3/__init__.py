"""__init__.py: """


__author__ = "Artem Hruzd"
__date__ = "06/23/2020 14:45"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


COMMUNITY_SEARCH_FIELDS = ["name", "website"]
COMMUNITY_ORDERING_FIELDS = ["id", "name", "cross_roads", "city__name"]
COMMUNITY_FILTER_FIELDS = ["is_active", "is_multi_family", "confirmed_address", "address_override"]
