import logging

from django.urls import reverse
from django.contrib.contenttypes.models import ContentType

from rest_framework import serializers

from .models import Type, Annotation

__author__ = "Autumn Valenta"
__date__ = "11/18/14 3:00 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = []

log = logging.getLogger(__name__)


class AnnotationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Type
        fields = (
            "id",
            "data_type",
            "description",
            "is_required",
            "is_unique",
            "name",
            "slug",
            "valid_multiplechoice_values",
        )


class AnnotationSerializer(serializers.ModelSerializer):
    content_type = serializers.SlugRelatedField(
        allow_null=True, required=False, slug_field="model", queryset=ContentType.objects.all()
    )
    content_object = serializers.SerializerMethodField()
    type = serializers.SlugRelatedField(
        allow_null=True, required=False, slug_field="slug", queryset=Type.objects.all()
    )
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    user_display = serializers.SerializerMethodField(read_only=True)
    company = serializers.PrimaryKeyRelatedField(read_only=True, source="user.company")

    class Meta:
        model = Annotation
        fields = (
            "id",
            "content_object",
            "content_type",
            "type",
            "content",
            "field_name",
            "object_id",
            "user",
            "user_display",
            "created_on",
            "is_public",
            "company",
        )
        read_only_fields = ("created_on",)

    content_type_lookup_keys = {
        "home": "home",
        "eepprogramhomestatus": "home_status",
        "subdivision": "subdivision",
        "community": "community",
        "state": "incentive_payment_status",
        "floorplan": "floorplan",
    }

    def get_user_display(self, obj):
        if obj.user:
            return obj.user.get_full_name()

    def get_content_object(self, obj):
        if obj.pk:
            return self.content_type_lookup_keys.get(obj.content_type.model, obj.content_type.model)
        # object_type = self.content_type_lookup_keys.get(obj.content_type.model, obj.content_type.model)
        # try:
        #     url = reverse('apiv2:{}-detail'.format(object_type), kwargs={'pk': obj.id})
        # except:
        #     log.exception("yo")
        #     return "'{}' not identifiable ".format(str(obj.content_type.name))
        # request = self.context.get('request')
        # if request:
        #     url = ("http%s://" % ('s' if request.is_secure() else '')) + request.get_host() + url
        # return url


class ImpliedContentObjectAnnotationSerializer(AnnotationSerializer):
    class Meta:
        model = Annotation

        # Omitting content_type
        fields = (
            "id",
            "content_object",
            "type",
            "content",
            "field_name",
            "object_id",
            "user",
            "created_on",
        )

    def __init__(self, *args, **kwargs):
        super(ImpliedContentObjectAnnotationSerializer, self).__init__(*args, **kwargs)

        if self.context.get("type"):
            self.fields["type"].read_only = True
        # if self.context.get('include_unread_flags'):
        #     self.fields['unread'] = serializers.SerializerMethodField('get_unread_flag')

    def get_unread_flag(self, obj):
        """
        Discover a message read/urnead status (if any) that corresponds to the field annotation.
        """
        return False

    def perform_create(self, serializer):
        implied_content_type = ContentType.objects.get_for_model(self.parent.Meta.model)
        serializer.save(content_type=implied_content_type)

    def perform_update(self, serializer):
        self.perform_create(serializer)


class BaseAnnotationsSerializer(serializers.ModelSerializer):
    annotations = ImpliedContentObjectAnnotationSerializer(many=True)

    # Inner 'Meta' class dynamically subclassed to add 'model' in api.BaseAnnotationViewSet
    class Meta(object):
        fields = ["annotations"]


class BaseFieldAnnotationsSerializer(serializers.ModelSerializer):
    field_annotations = serializers.SerializerMethodField()

    # Inner 'Meta' class dynamically subclassed to add 'model' in api.BaseAnnotationViewSet
    class Meta(object):
        fields = ["field_annotations"]

    def get_field_annotations(self, obj):
        queryset = obj.annotations.filter(type__slug="field-annotation")
        serializer = ImpliedContentObjectAnnotationSerializer(
            queryset,
            many=True,
            context={
                "type": "field-annotation",
                # 'include_unread_flags': True,
            },
        )
        serializer.parent = self
        return serializer.data
