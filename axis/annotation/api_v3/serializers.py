__author__ = "Artem Hruzd"
__date__ = "08/24/2022 16:01"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.contrib.auth import get_user_model

from rest_framework import serializers

from axis.annotation.models import Annotation, Type as AnnotationType
from axis.core.api_v3.serializers import UserInfoSerializer

User = get_user_model()


class AnnotationTypeInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnnotationType
        fields = ("id", "slug", "name")


class AnnotationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnnotationType
        fields = ("id", "slug", "name")


class AnnotationInfoSerializer(serializers.ModelSerializer):
    user_info = UserInfoSerializer(source="user", read_only=True)
    type__info = AnnotationTypeInfoSerializer(source="type", read_only=True)

    class Meta:
        model = Annotation
        fields = (
            "id",
            "content",
            "type",
            "type__info",
            "user",
            "user_info",
            "field_name",
            "is_public",
            "last_update",
            "created_on",
        )


class AnnotationSerializer(serializers.ModelSerializer):
    user_info = UserInfoSerializer(source="user", read_only=True)
    type__info = AnnotationTypeInfoSerializer(source="type", read_only=True)

    class Meta:
        model = Annotation
        fields = (
            "id",
            "content",
            "type",
            "type__info",
            "user",
            "user_info",
            "field_name",
            "is_public",
            "last_update",
            "created_on",
        )
