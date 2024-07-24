"""country.py - axis"""

__author__ = "Steven K"
__date__ = "7/25/22 14:08"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from rest_framework import serializers

from axis.geographic.models import Country

log = logging.getLogger(__name__)


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ["id", "abbr", "name"]
        read_only_fields = ["id", "abbr", "name"]
