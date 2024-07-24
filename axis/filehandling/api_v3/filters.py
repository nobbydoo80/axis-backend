"""filters.py: """


__author__ = "Rajesh Pethe"
__date__ = "07/27/2022 16:15:19"
__copyright__ = "Copyright 2011-2022 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Rajesh Pethe",
    "Steven Klass",
]


from django_filters import rest_framework as filters
from axis.filehandling.models import CustomerDocument
from axis.filehandling.api_v3 import CUSTOMER_DOCUMENT_FILTER_FIELDS


class CustomerDocumentFilterSet(filters.FilterSet):
    class Meta:
        model = CustomerDocument
        fields = CUSTOMER_DOCUMENT_FILTER_FIELDS
