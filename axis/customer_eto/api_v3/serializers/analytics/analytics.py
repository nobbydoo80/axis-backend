"""analytics.py - Axis"""

__author__ = "Steven K"
__date__ = "3/16/22 13:57"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from analytics.models import AnalyticRollup
from rest_framework import serializers

from .home_analysis import AnalyticsBaseMixin

log = logging.getLogger(__name__)


class OutputSerializer(AnalyticsBaseMixin, serializers.ModelSerializer):
    warnings = serializers.IntegerField(default=0)
    fields = serializers.SerializerMethodField(method_name="get_field_data")

    class Meta(AnalyticsBaseMixin.Meta):
        fields = ("warnings", "fields")

    def get_field_data(self, instance: AnalyticRollup) -> list:
        fields = []
        for item in [
            self.context.get("heating_consumption_kwh", {}),
            self.context.get("heating_consumption_therms", {}),
            self.context.get("cooling_consumption_kwh", {}),
            self.context.get("lights_and_appliances_consumption_kwh", {}),
            self.context.get("hot_water_consumption_kwh", {}),
            self.context.get("hot_water_consumption_therms", {}),
            self.context.get("design_load_heating", {}),
            self.context.get("design_load_cooling", {}),
            self.context.get("total_consumption", {}),
            self.context.get("total_consumption_no_pv", {}),
        ]:
            if item and item.get("value", -1) > 0:
                fields.append(item)
        return list(self.divide_chunks(fields, 2))


class InsulationSerializer(AnalyticsBaseMixin, serializers.ModelSerializer):
    warnings = serializers.IntegerField(default=0)
    fields = serializers.SerializerMethodField(method_name="get_field_data")

    class Meta(AnalyticsBaseMixin.Meta):
        fields = ("warnings", "fields")

    def get_field_data(self, instance: AnalyticRollup) -> list:
        fields = []
        for item in [
            self.context.get("total_frame_floor_area"),
            self.context.get("dominant_floor_insulation_r_value"),
            self.context.get("dominant_floor_insulation_u_value"),
            self.context.get("total_slab_floor_area"),
            self.context.get("dominant_slab_insulation_r_value"),
            self.context.get("dominant_slab_insulation_u_value"),
            self.context.get("total_above_grade_wall_area", {}),
            self.context.get("dominant_above_grade_wall_r_value", {}),
            self.context.get("dominant_above_grade_wall_u_value", {}),
            self.context.get("total_ceiling_area", {}),
            self.context.get("dominant_ceiling_r_value", {}),
            self.context.get("dominant_ceiling_u_value", {}),
            self.context.get("dominant_window_u_value", {}),
            self.context.get("dominant_window_shgc_value", {}),
            self.context.get("total_window_area", {}),
        ]:
            if item and item.get("value", -1) > 0:
                fields.append(item)
        return list(self.divide_chunks(fields, 2))


class MechanicalSerializer(AnalyticsBaseMixin, serializers.ModelSerializer):
    warnings = serializers.IntegerField(default=0)
    fields = serializers.SerializerMethodField(method_name="get_field_data")

    class Meta(AnalyticsBaseMixin.Meta):
        fields = ("warnings", "fields")

    def get_field_data(self, instance: AnalyticRollup) -> list:
        fields = []
        for item in [
            self.context.get("heater_heating_capacity"),
            # self.context.get("heater_heating_efficiency"),
            self.context.get("air_conditioner_cooling_capacity"),
            self.context.get("air_conditioner_cooling_efficiency"),
            self.context.get("ground_source_heat_pump_heating_capacity", {}),
            self.context.get("ground_source_heat_pump_heating_efficiency", {}),
            self.context.get("ground_source_heat_pump_cooling_capacity", {}),
            self.context.get("ground_source_heat_pump_cooling_efficiency", {}),
            self.context.get("air_source_heat_pump_heating_capacity", {}),
            # self.context.get("air_source_heat_pump_heating_efficiency", {}),
            self.context.get("air_source_heat_pump_cooling_capacity", {}),
            # self.context.get("air_source_heat_pump_cooling_efficiency", {}),
            # self.context.get("dual_fuel_heat_pump_heating_capacity", {}),
            # self.context.get("dual_fuel_heat_pump_heating_efficiency", {}),
            # self.context.get("dual_fuel_heat_pump_cooling_capacity", {}),
            # self.context.get("dual_fuel_heat_pump_cooling_efficiency", {}),
            self.context.get("water_heater_tank_size", {}),
            self.context.get("water_heater_energy_factor", {}),
        ]:
            if item and item.get("value", -1) > 0:
                fields.append(item)
        return list(self.divide_chunks(fields, 2))


class DuctSerializer(AnalyticsBaseMixin, serializers.ModelSerializer):
    warnings = serializers.IntegerField(default=0)
    fields = serializers.SerializerMethodField(method_name="get_field_data")

    class Meta(AnalyticsBaseMixin.Meta):
        fields = ("warnings", "fields")

    def get_field_data(self, instance: AnalyticRollup) -> list:
        fields = []
        for item in [
            self.context.get("duct_system_total_leakage"),
            self.context.get("duct_system_total_total_real_leakage"),
            self.context.get("annual_infiltration_value"),
            self.context.get("ventilation_rate"),
            self.context.get("ventilation_watts", {}),
        ]:
            if item and item.get("value", -1) > 0:
                fields.append(item)
        return list(self.divide_chunks(fields, 2))


class ETOAnalyticsSerializer(AnalyticsBaseMixin, serializers.ModelSerializer):
    output_analysis = OutputSerializer(source="*")
    insulation_analysis = InsulationSerializer(source="*")
    mechanical_analysis = MechanicalSerializer(source="*")
    ducts_infiltration_analysis = DuctSerializer(source="*")
    warnings = serializers.IntegerField(default=0)

    class Meta(AnalyticsBaseMixin.Meta):
        fields = (
            "output_analysis",
            "insulation_analysis",
            "mechanical_analysis",
            "ducts_infiltration_analysis",
            "warnings",
        )
