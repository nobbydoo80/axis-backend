__author__ = "Artem Hruzd"
__date__ = "05/24/2023 11:17"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.contrib.contenttypes.models import ContentType
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_extensions.mixins import NestedViewSetMixin

from axis.annotation.api_v3.filters import AnnotationFilter
from axis.annotation.api_v3.serializers import AnnotationSerializer
from axis.annotation.models import Annotation
from axis.core.api_v3.filters import AxisFilterBackend, AxisSearchFilter, AxisOrderingFilter
from axis.core.api_v3.viewsets import NestedHistoryViewSet

ANNOTATION_SEARCH_FIELDS = [
    "id",
]
ANNOTATION_ORDERING_FIELDS = [
    "id",
]


class AnnotationViewSet(
    viewsets.mixins.RetrieveModelMixin,
    viewsets.mixins.ListModelMixin,
    viewsets.mixins.UpdateModelMixin,
    viewsets.mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    model = Annotation
    permission_classes = (IsAuthenticated,)
    queryset = model.objects.all()
    filterset_class = AnnotationFilter
    serializer_class = AnnotationSerializer
    filter_backends = [AxisFilterBackend, AxisSearchFilter, AxisOrderingFilter]
    search_fields = ANNOTATION_SEARCH_FIELDS
    ordering_fields = ANNOTATION_ORDERING_FIELDS


class AnnotationNestedHistoryViewSet(NestedHistoryViewSet):
    model = Annotation.history.model
    queryset = model.objects.all()
    permission_classes = (IsAuthenticated,)
    filter_backends = [AxisFilterBackend, AxisSearchFilter, AxisOrderingFilter]
    search_fields = ANNOTATION_SEARCH_FIELDS
    ordering_fields = ANNOTATION_ORDERING_FIELDS


class NestedAnnotationViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    model = Annotation
    queryset = model.objects.all()
    filterset_class = AnnotationFilter
    serializer_class = AnnotationSerializer
    filter_backends = [AxisFilterBackend, AxisSearchFilter, AxisOrderingFilter]
    search_fields = ANNOTATION_SEARCH_FIELDS
    ordering_fields = ANNOTATION_ORDERING_FIELDS

    @property
    def permission_classes(self):
        return (IsAuthenticated,)

    @property
    def parent_model(self):
        raise NotImplementedError

    @property
    def content_type(self):
        return ContentType.objects.get_for_model(self.parent_model)

    def get_queryset(self):
        qs = super(NestedAnnotationViewSet, self).get_queryset()
        qs = qs.filter(content_type=self.content_type).filter_by_user(user=self.request.user)
        return qs

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save(
            content_type=self.content_type,
            object_id=self.get_parents_query_dict().get("object_id"),
            user=self.request.user,
        )
        headers = self.get_success_headers(serializer.data)
        serializer = AnnotationSerializer(instance=instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
