"""washington_code_credit.py - Axis"""

__author__ = "Steven K"
__date__ = "11/5/21 09:54"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
from functools import cached_property

from analytics.models import AnalyticRollup
from rest_framework import serializers

log = logging.getLogger(__name__)


class WashingtonCodeCreditAnalyticRollupSerializer(serializers.ModelSerializer):
    """This is the Analytics Serializer"""

    status = serializers.SerializerMethodField()
    program_name = serializers.SerializerMethodField()
    home_analysis = serializers.SerializerMethodField()
    spec_analysis = serializers.SerializerMethodField()

    _flat_results = None

    class Meta:
        """Meta Options"""

        model = AnalyticRollup
        fields = ("id", "date_modified", "program_name", "status", "home_analysis", "spec_analysis")

    def get_status(self, obj: AnalyticRollup) -> str:
        """Status"""
        return f"{obj.get_status_display()}" if obj.status != "READY" else ""

    def get_program_name(self, obj: AnalyticRollup) -> str:
        """Get the program name"""
        return f"{obj.content_object.eep_program}"

    @cached_property
    def results(self) -> dict:
        """Pull the the data"""
        if self._flat_results is not None:
            return self._flat_results
        self._flat_results = self.instance.get_flattened_results()
        return self._flat_results

    def get_home_analysis(self, obj: AnalyticRollup) -> dict:
        """Home analysis pieces"""
        keys = [
            ("Rating Company", "rater"),
            ("Rater", "rater_of_record"),
            ("Builder Company", "builder"),
            ("Address", "addresss_long"),
            ("Electric Utility", "electric_utility"),
            ("Gas Utility", "gas_utility"),
        ]
        return {key: {"label": label, "value": self.results.get(key)} for label, key in keys}

    def get_spec_analysis(self, obj: AnalyticRollup) -> dict:
        """Fetch all the data"""
        keys = [
            "building_envelope_specification",
            "air_leakage_specification",
            "hvac_specification",
            "hvac_distribution_specification",
            "water_specification",
        ]
        data = {k: self.results.get(k, {}) for k in keys}
        warnings = []
        for k, v in data.items():
            if not v.get("meets_requirements"):
                warnings.append(k)
        data["warnings"] = warnings
        return data
