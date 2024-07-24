"""neea_calculator_v2.py - Axis"""

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
from axis.customer_neea.models import PNWZone
from axis.customer_neea.rtf_calculator.base import RTFInputException
from axis.customer_neea.rtf_calculator.calculator import NEEAV2Calculator
from axis.customer_neea.rtf_calculator.constants.default import (
    NEEA_WATER_HEATER_TIER_MAP,
)
from axis.geographic.models import County

log = logging.getLogger(__name__)


class NEEACalculatorBase:
    def __init__(self, *args, **kwargs):
        super(NEEACalculatorBase, self).__init__(*args, **kwargs)
        neea = Company.objects.filter(slug="neea").first()
        if neea and getattr(self, "fields"):
            gas_qs = Company.objects.filter(
                company_type=Company.UTILITY_COMPANY_TYPE
            ).filter_by_company(neea, gas_provider=True)
            ele_qs = Company.objects.filter(
                company_type=Company.UTILITY_COMPANY_TYPE
            ).filter_by_company(neea, electricity_provider=True)
            county_qs = County.objects.filter_by_company(neea)
            self.fields["county"].queryset = County.objects.filter_by_company(neea)
            self.fields["gas_utility"].queryset = gas_qs
            self.fields["electric_utility"].queryset = ele_qs
            self.fields["county"].queryset = county_qs

    def calculator(self, *args, **kwargs):
        """The calculator used"""
        return NEEAV2Calculator(*args, **kwargs)

    def validate(self, attrs):  # noqa: MC0001  pylint: disable=too-many-statements
        """Validate no other obvious errors"""
        if attrs.get("primary_heating_type"):
            # Allow Heatpumps to have both.
            if "heat pump" not in attrs["primary_heating_type"].lower():
                if "gas" in attrs["primary_heating_type"].lower():
                    if attrs["heating_fuel"].lower() != "gas":
                        error = "Heating Fuel of %s does not align with heating type of %s"
                        raise serializers.ValidationError(
                            error % (attrs["heating_fuel"], attrs["primary_heating_type"])
                        )
                    if attrs["gas_utility"] in [None, ""]:
                        error = "Missing Gas Utility when specifying heating type of %s"
                        raise serializers.ValidationError(error % (attrs["primary_heating_type"]))

                if "electric" in attrs["primary_heating_type"].lower():
                    if attrs["heating_fuel"].lower() != "electric":
                        error = "Heating Fuel of %s does not align with heating type of %s"
                        raise serializers.ValidationError(
                            error % (attrs["heating_fuel"], attrs["primary_heating_type"])
                        )
                    if attrs["electric_utility"] in [None, ""]:
                        error = "Missing Electric Utility when specifying heating type of %s"
                        raise serializers.ValidationError(error % (attrs["primary_heating_type"]))
                    code = attrs.get("code_data_heating_therms", 0.0)
                    improved = attrs.get("improved_data_heating_therms", 0.0)
                    if code > 0 or improved > 0:
                        error = "%s primary heat does not allow %s %s input values"
                        raise serializers.ValidationError(
                            error % (attrs["primary_heating_type"], "heating", "Therm")
                        )
            else:
                if attrs["electric_utility"] in [None, ""]:
                    error = "Missing Electric Utility when specifying heating type of %s"
                    raise serializers.ValidationError(error % (attrs["primary_heating_type"]))
                if attrs["heating_fuel"].lower() != "electric":
                    error = "Heating Fuel of %s does not align with heating type of %s"
                    raise serializers.ValidationError(
                        error % (attrs["heating_fuel"], attrs["primary_heating_type"])
                    )
                if "gas" in attrs["primary_heating_type"].lower():
                    if attrs["gas_utility"] in [None, ""]:
                        error = "Missing Gas Utility when specifying heating type of %s"
                        raise serializers.ValidationError(error % (attrs["primary_heating_type"]))

            code = attrs.get("code_data_heating_therms", 0.0)
            improved = attrs.get("improved_data_heating_therms", 0.0)
            if code > 0 or improved > 0:
                if attrs["gas_utility"] in [None, ""]:
                    error = "Missing Gas Utility when specifying hot water therms"
                    raise serializers.ValidationError(error)

            code = attrs.get("code_data_heating_kwh", 0.0)
            improved = attrs.get("improved_data_heating_kwh", 0.0)
            if code > 0 or improved > 0:
                if attrs["electric_utility"] in [None, ""]:
                    error = "Missing Gas Utility when specifying hot water kWh"
                    raise serializers.ValidationError(error)

        if attrs.get("code_data_heating_therms", 0.0) > attrs.get(
            "code_data_total_consumption_therms", 0.0
        ):
            msg = "Total Code Therms must be greater than Code Heating Therms (%s)"
            raise serializers.ValidationError(msg % attrs.get("code_data_heating_therms", 0.0))

        if attrs.get("improved_data_heating_therms", 0.0) > attrs.get(
            "improved_data_total_consumption_therms", 0.0
        ):
            msg = "Total Improved Therms must be greater than Improved Heating Therms (%s)"
            raise serializers.ValidationError(msg % attrs.get("improved_data_heating_therms", 0.0))

        vals = sum(
            [
                attrs.get("code_data_heating_kwh", 0.0),
                attrs.get("code_data_cooling_kwh", 0.0),
            ]
        )
        if vals > attrs.get("code_data_total_consumption_kwh", 0.0):
            msg = "Total Code kWh must be greater than Code Heating/Cooling kWh (%s)"
            raise serializers.ValidationError(msg % vals)

        vals = sum(
            [
                attrs.get("improved_data_heating_kwh", 0.0),
                attrs.get("improved_data_cooling_kwh", 0.0),
            ]
        )
        if vals > attrs.get("improved_data_total_consumption_kwh", 0.0):
            msg = "Total Improved kWh must be greater than Improved Heating/Cooling kWh (%s)"
            raise serializers.ValidationError(msg % vals)

        county = attrs.get("county")
        attrs["us_state"] = county.state
        attrs["improved_data_conditioned_area"] = attrs.get("conditioned_area")
        attrs["improved_data_primary_heating_type"] = attrs.get("primary_heating_type")
        try:
            attrs["heating_zone"] = PNWZone.objects.get(county=county).get_heating_zone_display()
        except PNWZone.DoesNotExist:
            pass

        try:
            self.calculator(**attrs)
        except RTFInputException as e:
            raise serializers.ValidationError("{}".format(e))
        return attrs

    def create(self, validated_data):
        """Run the calculator"""
        return self.calculator(**validated_data)


class NEEACalculatorV2Serializer(NEEACalculatorBase, Serializer):
    """THe NEEA Standard Protocol Serializer"""

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
        choices=[("electric", "Electric"), ("gas", "Gas")],
        required=True,
        allow_null=True,
    )
    heating_system_config = serializers.ChoiceField(
        choices=[("central", "Central"), ("zonal", "Zonal")],
        label="Heating System Configuration",
        required=True,
        allow_null=True,
    )
    primary_heating_type = serializers.ChoiceField(
        choices=[
            (x, x)
            for x in [
                "Heat Pump",
                "Heat Pump - Geothermal/Ground Source",
                "Heat Pump - w/ Gas Backup",
                "Heat Pump - Mini Split",
                "Gas with AC",
                "Gas No AC",
                "Zonal Electric",
                "Propane Oil or Wood",
                "Hydronic Radiant Electric Boiler",
                "Hydronic Radiant Gas Boiler",
                "Hydronic Radiant Heat Pump",
            ]
        ],
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
    qty_shower_head_1p5 = serializers.IntegerField(
        min_value=0, max_value=10, default=0, label="Qty 1.5 gpm Showerheads"
    )
    qty_shower_head_1p75 = serializers.IntegerField(
        min_value=0, max_value=10, default=0, label="Qty 1.75 gpm Showerheads"
    )

    cfl_installed = serializers.IntegerField(
        min_value=0, max_value=500, label="Qty CFL lamps", default=0
    )
    led_installed = serializers.IntegerField(
        min_value=0, max_value=500, label="Qty LED lamps", default=0
    )
    total_installed_lamps = serializers.IntegerField(
        min_value=0,
        max_value=1000,
        label="Qty Total Lamps",
        default=0,
    )

    estar_std_refrigerators_installed = serializers.BooleanField(
        label="ENERGY STAR® Refrigerator Installed"
    )
    estar_dishwasher_installed = serializers.BooleanField(label="ENERGY STAR® Dishwasher Installed")
    estar_front_load_clothes_washer_installed = serializers.BooleanField(
        label="ENERGY STAR® Front Load Clothes Washer Installed"
    )
    clothes_dryer_tier = serializers.ChoiceField(
        choices=[
            ("", "None"),
            ("tier2", "Tier 2"),
            ("tier3", "Tier 3"),
            ("estar", "ENERGY STAR®"),
        ],
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
