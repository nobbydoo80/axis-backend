__author__ = "Artem Hruzd"
__date__ = "05/24/2023 11:25"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django_filters import rest_framework as filters
from axis.annotation.models import Annotation


class AnnotationFilter(filters.FilterSet):
    class Meta:
        model = Annotation
        fields = [
            "id",
            "type__slug",
        ]
