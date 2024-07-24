"""green_energy_badge.py: """

__author__ = "Artem Hruzd"
__date__ = "04/16/2021 17:21"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from rest_framework import serializers

from axis.customer_hirl.models import HIRLGreenEnergyBadge


class HIRLGreenEnergyBadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = HIRLGreenEnergyBadge
        fields = ("id", "name", "slug")


class HIRLGreenEnergyBadgeInfoSerializer(serializers.ModelSerializer):
    """
    Info version for nested representations
    """

    class Meta:
        model = HIRLGreenEnergyBadge
        fields = ("id", "name", "slug")
