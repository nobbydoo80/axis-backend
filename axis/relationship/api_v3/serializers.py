"""Relationship serializers."""


from rest_framework import serializers

from axis.company.api_v3.serializers import CompanyInfoSerializer
from axis.company.models import Company
from axis.core.api_v3.serializers import ContentTypeRelatedField, ContentTypeInfoSerializer
from axis.relationship.models import Relationship

__author__ = "Autumn Valenta"
__date__ = "01/03/2020 21:11"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
    "Steven Klass",
]


class RelationshipSerializer(serializers.ModelSerializer):
    """Basic Relationship serializer."""

    company_info = CompanyInfoSerializer(source="company", read_only=True)
    content_object = ContentTypeRelatedField(read_only=True)
    content_type_info = ContentTypeInfoSerializer(source="content_type", read_only=True)

    class Meta:
        model = Relationship
        fields = (
            "id",
            "is_attached",
            "is_viewable",
            "is_owned",
            "is_reportable",
            "company",
            "company_info",
            "content_type",
            "content_type_info",
            "content_object",
        )
        read_only_fields = ("content_type",)
