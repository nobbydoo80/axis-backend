"""rater_role.py: """

__author__ = "Artem Hruzd"
__date__ = "05/11/2022 16:51"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from rest_framework import serializers

from axis.core.models import RaterRole


class RaterRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = RaterRole
        fields = ("id", "title", "slug", "is_hidden")
