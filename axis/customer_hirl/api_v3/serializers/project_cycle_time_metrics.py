# -*- coding: utf-8 -*-
"""project_cycle_time_metrics.py: """

__author__ = "Artem Hruzd"
__date__ = "09/29/2022 16:51"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


from rest_framework import serializers


class ProjectCycleTimeMetricsSerializer(serializers.Serializer):
    cycle_days = serializers.IntegerField()
    projects_count = serializers.IntegerField(default=0)

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError
