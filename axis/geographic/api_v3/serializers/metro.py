"""metro.py - Axis"""

__author__ = "Steven K"
__date__ = "10/13/21 16:00"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from rest_framework import serializers
from axis.geographic.models import Metro

log = logging.getLogger(__name__)


class MetroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Metro
        fields = (
            "id",
            "name",
            "cbsa_code",
        )
