"""api.py: Django annotation"""


from django.contrib.contenttypes.models import ContentType
from rest_framework import viewsets
from rest_framework.decorators import action

from axis.examine.api.restframework import ExamineViewSetAPIMixin
from .models import Type, Annotation
from .serializers import (
    AnnotationTypeSerializer,
    AnnotationSerializer,
    BaseAnnotationsSerializer,
    BaseFieldAnnotationsSerializer,
)


__author__ = "Autumn Valenta"
__date__ = "5/27/13 10:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]


class AnnotationTypeViewSet(viewsets.ReadOnlyModelViewSet):
    model = Type
    queryset = model.objects.all()
    serializer_class = AnnotationTypeSerializer


class AnnotationViewSet(ExamineViewSetAPIMixin, viewsets.ModelViewSet):
    model = Annotation
    queryset = model.objects.all()
    serializer_class = AnnotationSerializer

    object_model = None  # content_object's Model, filled in by factory
    content_type = None

    annotation_type = None

    top_level = True

    # FIXME: This is a perfect example of why we need better url routes, to do this dynamically
    @action(detail=True)
    def note(self, request, *args, **kwargs):
        self.annotation_type = "note"
        return self.list(request, *args, **kwargs)

    def get_examine_machinery_classes(self):
        from axis.certification.api.examine import get_workflowstatus_annotations_machinery_class
        from axis.floorplan.views.examine import get_floorplan_annotations_machinery_class
        from axis.customer_hirl.verifier_agreements.examine import (
            get_verifieragreement_notes_machinery,
        )
        from axis.home.models import EEPProgramHomeStatus
        from .machinery import annotations_machinery_factory

        homestatus_home_note_machinery = annotations_machinery_factory(
            EEPProgramHomeStatus, type_slug="note"
        )
        workflowstatus_note_machinery = get_workflowstatus_annotations_machinery_class()
        floorplan_note_machinery = get_floorplan_annotations_machinery_class()
        hirl_verifieragreement_note_machinery = get_verifieragreement_notes_machinery()

        return {
            "WorkflowStatusAnnotationsMachinery_note": workflowstatus_note_machinery,
            "EEPProgramHomeStatusAnnotationsMachinery_note": homestatus_home_note_machinery,
            "FloorplanAnnotationsMachinery_note": floorplan_note_machinery,
            "VerifierAgreementAnnotationsMachinery_note": hirl_verifieragreement_note_machinery,
        }

    def get_queryset(self):
        queryset = Annotation.objects.filter_by_user(self.request.user)
        if self.object_model:
            # If used as a model-scoped viewset instead of raw
            ct = ContentType.objects.get_for_model(self.object_model)
            queryset = queryset.filter(content_type=ct)
        if self.annotation_type:
            queryset = queryset.filter(type__slug=self.annotation_type)
        return queryset

    def perform_create(self, serializer):
        self._save(serializer)

    def perform_update(self, serializer):
        self._save(serializer)

    def _save(self, serializer):
        extra_data = {
            "user": self.request.user,
        }
        if "type" in self.request.query_params:
            extra_data["type"] = Type.objects.get(slug=self.request.query_params["type"])
        if self.object_model:
            extra_data["content_type"] = ContentType.objects.get_for_model(self.object_model)
        obj = serializer.save(**extra_data)

        # When we have a working POST/PATCH system on BaseFieldAnnotationsViewSet and creation
        # queries are routed there instead of here, this code will be able to unconditionally issue
        # messages corresponding to fieldannotations, instead of guardedly checking like this.
        if obj.type.slug == "field-annotation":
            from axis.builder_agreement.utils import generate_field_annotation_messages

            generate_field_annotation_messages(obj.user, obj)


class BaseContentTypeAnnotationViewSet(viewsets.ModelViewSet):
    # 'model' attribute dynamically set in core/api.py loop.
    # model will be the model for which field annotations are retrieved.

    def get_serializer_class(self):
        class Meta(BaseAnnotationsSerializer.Meta):
            model = self.model

        serializer_name = "%sAnnotationsSerializer" % (self.model.__name__,)
        return type(
            str(serializer_name),
            (BaseAnnotationsSerializer,),
            {
                "Meta": Meta,
            },
        )

    def get_queryset(self):
        return self.model.objects.all()


class BaseFieldAnnotationsViewSet(viewsets.ModelViewSet):
    # 'model' attribute dynamically set in core/api.py loop.
    # model will be the model for which field annotations are retrieved.

    def get_serializer_class(self):
        class Meta(BaseFieldAnnotationsSerializer.Meta):
            model = self.model

        serializer_name = "%sFieldAnnotationsSerializer" % (self.model.__name__,)
        return type(
            str(serializer_name),
            (BaseFieldAnnotationsSerializer,),
            {
                "Meta": Meta,
            },
        )

    def get_queryset(self):
        return self.model.objects.all()
