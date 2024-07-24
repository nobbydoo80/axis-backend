__author__ = "Steven Klass"
__date__ = "06/14/2019 07:51"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

# common set of search_fields for CustomerDocument Viewsets
CUSTOMER_DOCUMENT_SEARCH_FIELDS = [
    "document",
    "description",
]
# common set of ordering_fields for CustomerDocument Viewsets
CUSTOMER_DOCUMENT_ORDERING_FIELDS = ["id", "document", "description"]

# common set of FilterSet fields for CustomerDocument
CUSTOMER_DOCUMENT_FILTER_FIELDS = ["is_public", "is_active"]

DOCUMENT_ACCESS_LEVEL_GLOBAL = "public_global"
DOCUMENT_ACCESS_LEVEL_PUBLIC = "public_logged_in"
DOCUMENT_ACCESS_LEVEL_PRIVATE = "private"
