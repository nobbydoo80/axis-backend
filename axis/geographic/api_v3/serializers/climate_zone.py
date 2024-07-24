"""climate_zone.py - Axis"""

__author__ = "Steven K"
__date__ = "10/13/21 16:03"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
from rest_framework import serializers
from axis.geographic.models import ClimateZone

log = logging.getLogger(__name__)


class ClimateZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClimateZone
        fields = ("id", "zone", "moisture_regime", "doe_zone")
