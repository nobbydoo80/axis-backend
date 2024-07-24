# -*- coding: utf-8 -*-
"""hirl_project_registration_activity_metrics_by_month.py: """

__author__ = "Artem Hruzd"
__date__ = "09/28/2022 15:46"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


from rest_framework import serializers


class HIRLProjectRegistrationActivityMetricsByMonthSerializer(serializers.Serializer):
    month = serializers.DateField()
    registrations_count = serializers.IntegerField(default=0)

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError


class HIRLProjectRegistrationActivityMetricsByUnitsMonthSerializer(serializers.Serializer):
    month = serializers.DateField()
    units_count = serializers.IntegerField(default=0)

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError
