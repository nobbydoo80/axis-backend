__author__ = "Artem Hruzd"
__date__ = "06/03/2023 20:08"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django_filters import rest_framework as filters
from axis.annotation.models import Type as AnnotationType


class AnnotationTypeFilter(filters.FilterSet):
    class Meta:
        model = AnnotationType
        fields = ["id", "slug", "data_type"]
