"""api.py: customer aps"""


from rest_framework import serializers

from axis.subdivision.models import Subdivision
from .models import APSHome, APSSmartThermostatOption, SMART_TSTAT_ELIGIBILITY, SMART_TSTAT_MODELS

__author__ = "Autumn Valenta"
__date__ = "1/08/15 10:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]


class APSHomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = APSHome
        fields = "__all__"


class APSSmartThermostatSerializer(serializers.ModelSerializer):
    """APS Smart Thermostat Options Serializer"""

    eligibility = serializers.ChoiceField(
        choices=SMART_TSTAT_ELIGIBILITY, source="aps_thermostat_option.eligibility"
    )
    models = serializers.MultipleChoiceField(
        choices=SMART_TSTAT_MODELS, source="aps_thermostat_option.models"
    )

    eligibility_display = serializers.ReadOnlyField(
        source="aps_thermostat_option.get_eligibility_display"
    )
    models_display = serializers.ListField(
        child=serializers.CharField(),
        default=[],
        source="aps_thermostat_option.get_models_pretty",
        read_only=True,
    )

    class Meta:
        """Meta"""

        model = Subdivision
        fields = ("id", "eligibility", "models", "eligibility_display", "models_display")

    def update(self, instance, validated_data):
        """This only applies to updates"""
        request = self.context["request"]
        user = request.user
        if instance.is_aps_thermostat_incentive_applicable(user):
            option, create = APSSmartThermostatOption.objects.get_or_create(subdivision=instance)
            option.eligibility = validated_data["aps_thermostat_option"]["eligibility"]
            option.models = validated_data["aps_thermostat_option"]["models"]
            option.save()

        return instance
