__author__ = "Artem Hruzd"
__date__ = "06/03/2023 20:06"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from axis.annotation.api_v3.filters import AnnotationTypeFilter
from axis.annotation.api_v3.serializers import AnnotationTypeSerializer
from axis.annotation.models import Type as AnnotationType
from axis.core.api_v3.filters import AxisSearchFilter, AxisOrderingFilter, AxisFilterBackend


ANNOTATION_TYPE_SEARCH_FIELDS = ["id", "name", "slug", "description"]
ANNOTATION_TYPE_ORDERING_FIELDS = ["id", "name"]


class AnnotationTypeViewSet(
    viewsets.mixins.RetrieveModelMixin,
    viewsets.mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    model = AnnotationType
    permission_classes = (IsAuthenticated,)
    queryset = model.objects.all()
    filterset_class = AnnotationTypeFilter
    serializer_class = AnnotationTypeSerializer
    filter_backends = [AxisFilterBackend, AxisSearchFilter, AxisOrderingFilter]
    search_fields = ANNOTATION_TYPE_SEARCH_FIELDS
    ordering_fields = ANNOTATION_TYPE_ORDERING_FIELDS
