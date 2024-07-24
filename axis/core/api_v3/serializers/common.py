"""common.py: """


from rest_framework import serializers

__author__ = "Artem Hruzd"
__date__ = "03/17/2020 00:00"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class IdSerializer(serializers.Serializer):
    """
    Common serializer with only one id field
    """

    id = serializers.IntegerField()

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError


class BulkSelectByIdSerializer(serializers.Serializer):
    """
    Common serializer using for bulk update objects by id
    """

    ids = serializers.ListSerializer(child=serializers.IntegerField(), allow_empty=True)

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError
