"""accreditation_status.py: """


from rest_framework import serializers

from axis.user_management.models import Accreditation

__author__ = "Artem Hruzd"
__date__ = "10/31/2019 20:35"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class AccreditationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Accreditation
        fields = "__all__"


class AccreditationChangeStateSerializer(serializers.Serializer):
    accreditation_ids = serializers.ListField(child=serializers.IntegerField())
    new_state = serializers.ChoiceField(choices=Accreditation.STATE_CHOICES)

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError
