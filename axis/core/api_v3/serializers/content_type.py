"""content_type.py: """

from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers


__author__ = "Artem Hruzd"
__date__ = "08/28/2020 13:41"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class ContentTypeInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentType
        fields = ("id", "model", "name")


class ContentTypeRelatedField(serializers.Field):
    """
    Info representation of any object on AXIS
    """

    def to_representation(self, value):
        """
        Serialize tagged objects to a simple textual representation.
        """
        from axis.community.api_v3.serializers import CommunityInfoSerializer
        from axis.community.models import Community
        from axis.company.api_v3.serializers import CompanyInfoSerializer
        from axis.company.models import Company
        from axis.home.api_v3.serializers import HomeInfoSerializer
        from axis.home.models import Home
        from axis.subdivision.api_v3.serializers import SubdivisionInfoSerializer
        from axis.subdivision.models import Subdivision
        from axis.floorplan.models import Floorplan
        from axis.floorplan.api_v3.serializers import FloorplanInfoSerializer
        from axis.qa.models import QAStatus
        from axis.qa.api_v3.serializers import QAStatusInfoSerializer

        if isinstance(value, Company):
            serializer = CompanyInfoSerializer(value)
        elif isinstance(value, Subdivision):
            serializer = SubdivisionInfoSerializer(value)
        elif isinstance(value, Community):
            serializer = CommunityInfoSerializer(value)
        elif isinstance(value, Home):
            serializer = HomeInfoSerializer(value)
        elif isinstance(value, Floorplan):
            serializer = FloorplanInfoSerializer(value)
        elif isinstance(value, QAStatus):
            serializer = QAStatusInfoSerializer(value)
        else:
            raise Exception("Unexpected type of relationship object")
        return serializer.data
