"""us_state.py: """

__author__ = "Artem Hruzd"
__date__ = "07/16/2020 21:38"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from rest_framework import serializers
from ...models import USState


class USStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = USState
        fields = ["abbr", "name"]
