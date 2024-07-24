"""training.py: """


from rest_framework import serializers

from axis.user_management.models import Training

__author__ = "Artem Hruzd"
__date__ = "10/31/2019 20:35"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class TrainingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Training
        fields = "__all__"
