"""recently_viewed.py: """

from rest_framework import serializers
from axis.core.models import RecentlyViewed

from .content_type import ContentTypeInfoSerializer, ContentTypeRelatedField

__author__ = "Artem Hruzd"
__date__ = "10/29/2020 00:28"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class RecentlyViewedSerializer(serializers.ModelSerializer):
    content_object = ContentTypeRelatedField(read_only=True)
    content_type_info = ContentTypeInfoSerializer(source="content_type", read_only=True)

    class Meta:
        model = RecentlyViewed
        fields = ("id", "content_type", "content_type_info", "content_object", "updated_at")
        read_only_fields = ("content_type",)
