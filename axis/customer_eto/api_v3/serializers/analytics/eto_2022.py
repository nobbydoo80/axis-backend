"""eto_2022.py - Axis"""

__author__ = "Steven K"
__date__ = "3/16/22 13:18"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from analytics.models import AnalyticRollup
from rest_framework import serializers

from .analytics import ETOAnalyticsSerializer
from .home_analysis import ETOHomeAnalysisSerializer

log = logging.getLogger(__name__)


class ETO2022AnalyticRollupSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    program_name = serializers.SerializerMethodField()
    home_analysis = ETOHomeAnalysisSerializer(source="*")
    analytics = ETOAnalyticsSerializer(source="*")

    class Meta:
        """Meta Options"""

        model = AnalyticRollup
        fields = ("id", "date_modified", "program_name", "status", "home_analysis", "analytics")

    def get_status(self, obj) -> str:
        """Status"""
        return "%s" % obj.get_status_display() if obj.status != "READY" else ""

    def get_program_name(self, obj) -> str:
        return "%s" % obj.content_object.eep_program
