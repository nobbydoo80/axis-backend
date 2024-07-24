"""builder_organization.py: """


from django_filters import rest_framework as filters

from ..models import Relationship

__author__ = "Autumn Valenta"
__date__ = "01/03/2020 22:53"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
    "Steven Klass",
]


class RelationshipFilter(filters.FilterSet):
    class Meta:
        model = Relationship
        fields = [
            "is_attached",
            "is_owned",
            "is_viewable",
            "is_reportable",
            "company__company_type",
        ]
