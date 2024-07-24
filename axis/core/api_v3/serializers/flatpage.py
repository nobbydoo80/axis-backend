"""flatpage.py: """

from rest_framework import serializers
from axis.core.models import AxisFlatPage

__author__ = "Artem Hruzd"
__date__ = "11/16/2020 11:29"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class AxisFlatPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AxisFlatPage
        fields = ("id", "url", "title", "content", "order", "created_at")
