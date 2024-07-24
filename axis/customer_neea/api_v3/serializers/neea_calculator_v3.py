"""neea_calculator_v3.py - Axis"""

__author__ = "Steven K"
__date__ = "7/9/21 08:08"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from rest_framework import serializers
from rest_framework.serializers import Serializer

from axis.company.models import Company
from axis.customer_neea.rtf_calculator.calculator import NEEAV3Calculator
from axis.customer_neea.rtf_calculator.constants.neea_v3 import (
    NEEA_V3_HEATING_TYPES,
    NEEA_WATER_HEATER_TIER_MAP,
    NEEA_CLOTHES_DRYER_FUELS_CHOICE_MAP,
    NEEA_REFRIGERATOR_CHOICE_MAP,
    NEEA_CLOTHES_WASHER_CHOICE_MAP,
)
from axis.geographic.models import County
from .neea_calculator_v2 import NEEACalculatorBase

log = logging.getLogger(__name__)


class NEEACalculatorV3Serializer(NEEACalculatorBase, Serializer):
    """THe NEEA Standard Protocol V3 Serializer"""

    home_status_id = serializers.IntegerField(required=False, label="Home Status ID")

    county = serializers.PrimaryKeyRelatedField(required=True, queryset=County.objects.none())
    conditioned_area = serializers.IntegerField(
        min_value=500, max_value=6000, label="Conditioned Area (sq. ft.)"
    )

    gas_utility = serializers.PrimaryKeyRelatedField(
        many=False,
        default=None,
        allow_null=True,
        required=False,
        queryset=Company.objects.none(),
    )
    electric_utility = serializers.PrimaryKeyRelatedField(
        many=False,
        default=None,
        allow_null=True,
        required=False,
        queryset=Company.objects.none(),
    )

    heating_fuel = serializers.ChoiceField(
        choices=[("electric", "Electric"), ("gas", "Gas")], required=True, allow_null=True
    )
    heating_system_config = serializers.ChoiceField(
        choices=[("central", "Central"), ("zonal", "Zonal")],
        label="Heating System Configuration",
        required=True,
        allow_null=True,
    )
    primary_heating_type = serializers.ChoiceField(
        choices=[(x, x) for x in NEEA_V3_HEATING_TYPES],
        label="Primary Heat Source",
        required=True,
        allow_null=True,
    )
    smart_thermostat_installed = serializers.BooleanField()

    code_data_heating_therms = serializers.FloatField(min_value=0.0, default=0, label="")
    code_data_heating_kwh = serializers.FloatField(min_value=0, default=0, label="")
    code_data_cooling_kwh = serializers.FloatField(min_value=0, default=0, label="")
    code_data_total_consumption_kwh = serializers.FloatField(min_value=0, default=0, label="")
    code_data_total_consumption_therms = serializers.FloatField(min_value=0, default=0, label="")

    improved_data_heating_therms = serializers.FloatField(min_value=0.0, default=0, label="")
    improved_data_heating_kwh = serializers.FloatField(min_value=0.0, default=0, label="")
    improved_data_cooling_kwh = serializers.FloatField(min_value=0.0, default=0, label="")
    improved_data_total_consumption_kwh = serializers.FloatField(min_value=0, default=0, label="")
    improved_data_total_consumption_therms = serializers.FloatField(
        min_value=0, default=0, label=""
    )

    water_heater_tier = serializers.ChoiceField(
        choices=NEEA_WATER_HEATER_TIER_MAP,
        label="Water Heater Type",
        required=True,
        allow_null=True,
    )

    clothes_dryer_fuel = serializers.ChoiceField(
        choices=NEEA_CLOTHES_DRYER_FUELS_CHOICE_MAP,
        label="Clothes Dryer Fuel",
        required=True,
        allow_null=True,
    )

    estar_std_refrigerators_installed = serializers.ChoiceField(
        choices=NEEA_REFRIGERATOR_CHOICE_MAP,
        label="ENERGY STAR® Refrigerator Installed",
        required=True,
        allow_null=True,
    )
    estar_dishwasher_installed = serializers.BooleanField(label="ENERGY STAR® Dishwasher Installed")
    estar_front_load_clothes_washer_installed = serializers.ChoiceField(
        choices=NEEA_CLOTHES_WASHER_CHOICE_MAP,
        label="ENERGY STAR® Clothes Washer Installed",
    )
    clothes_dryer_tier = serializers.ChoiceField(
        choices=[("", "None"), ("tier2", "Tier 2"), ("tier3", "Tier 3"), ("estar", "ENERGY STAR®")],
        label="Clothes Dryer Tier",
    )

    certified_earth_advantage = serializers.ChoiceField(
        choices=[
            ("", "None"),
            ("Silver", "Silver"),
            ("Gold", "Gold"),
            ("Platinum", "Platinum"),
            ("Net Zero Ready", "Net Zero Ready"),
            ("Net Zero", "Net Zero"),
        ],
        label="Certified Earth Advantage",
    )

    def calculator(self, *args, **kwargs):
        """The calculator used"""
        return NEEAV3Calculator(*args, **kwargs)
