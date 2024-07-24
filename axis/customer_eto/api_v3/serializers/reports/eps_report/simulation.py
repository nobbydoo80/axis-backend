"""simulation.py - Axis"""

__author__ = "Steven K"
__date__ = "9/30/21 08:36"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from rest_framework import serializers

from axis.customer_eto.api_v3.serializers.calculators.simulation import EPSSimulationBaseSerializer
from simulation.enumerations import FuelType, SourceType, AnalysisEngine, CostUnit
from simulation.models import Simulation

log = logging.getLogger(__name__)


class EPSReportSimulationSerializer(EPSSimulationBaseSerializer):
    electric_per_month = serializers.SerializerMethodField()
    natural_gas_per_month = serializers.SerializerMethodField()

    conditioned_area = serializers.IntegerField()
    construction_year = serializers.SerializerMethodField()
    electric_unit_cost = serializers.SerializerMethodField()
    gas_unit_cost = serializers.SerializerMethodField()
    insulated_walls = serializers.SerializerMethodField()
    insulated_floors = serializers.SerializerMethodField()
    efficient_windows = serializers.SerializerMethodField()
    efficient_lighting = serializers.SerializerMethodField()
    water_heater_efficiency = serializers.SerializerMethodField()
    heating_efficiency = serializers.SerializerMethodField()
    envelope_tightness = serializers.SerializerMethodField()
    pv_capacity_watts = serializers.SerializerMethodField()

    class Meta:
        """Meta Options"""

        model = Simulation
        fields = (
            "electric_per_month",
            "natural_gas_per_month",
            "conditioned_area",
            "construction_year",
            "electric_unit_cost",
            "gas_unit_cost",
            "insulated_walls",
            "insulated_floors",
            "efficient_windows",
            "efficient_lighting",
            "water_heater_efficiency",
            "heating_efficiency",
            "envelope_tightness",
            "pv_capacity_watts",
        )

    def to_internal_value(self, data):
        raise NotImplementedError("Un-supported Read-Only")

    def get_electric_per_month(self, instance: Simulation):
        return self.get_improved_electric_cost(instance) / 12.0

    def get_natural_gas_per_month(self, instance: Simulation):
        return self.get_improved_gas_cost(instance) / 12.0

    def get_construction_year(self, instance: Simulation):
        return instance.project.construction_year

    def get_electric_unit_cost(self, instance: Simulation) -> float:
        try:
            rate = instance.utility_rates.get(fuel=FuelType.ELECTRIC)
            value = rate.seasonal_rates.first().block_rates.first().cost
            if rate.cost_units == CostUnit.USC:
                value /= 100.0
            return value
        except (AttributeError, ObjectDoesNotExist):
            return 0.0

    def get_gas_unit_cost(self, instance: Simulation) -> float:
        try:
            rate = instance.utility_rates.get(fuel=FuelType.NATURAL_GAS)
            value = rate.seasonal_rates.first().block_rates.first().cost
            if rate.cost_units == CostUnit.USC:
                value /= 100.0
            return value
        except (AttributeError, ObjectDoesNotExist):
            return 0.0

    def get_insulated_walls(self, instance: Simulation) -> str:
        wall = instance.above_grade_walls.all().get_dominant_by_r_value()
        if wall:
            cavity = wall.type.cavity_insulation_r_value or 0.0
            continuous = wall.type.continuous_insulation_r_value or 0.0
            return f"R-{cavity + continuous:.0f}"
        return ""

    def get_insulated_floors(self, instance: Simulation) -> str:
        floor = instance.frame_floors.all().get_dominant_by_r_value()
        if floor:
            cavity = floor.type.cavity_insulation_r_value or 0.0
            continuous = floor.type.continuous_insulation_r_value or 0.0
            return f"R-{cavity + continuous:.0f}"
        else:
            r_value = instance.slabs.all().dominant_underslab_r_value
            if r_value is not None:
                return f"R-{r_value:.0f}"
        return ""

    def get_efficient_windows(self, instance: Simulation) -> str:
        u_value = instance.windows.all().dominant_u_value
        return f"U-{u_value:.2f}"

    def get_efficient_lighting(self, instance: Simulation) -> str:
        value = instance.lights.interior_led_percent or 0.0
        return f"{value:.1f} %"

    def get_water_heater_efficiency(self, instance: Simulation) -> str:
        dominant = instance.mechanical_equipment.dominant_water_heating_equipment.equipment
        return f"{dominant.efficiency:.2f} {dominant.get_efficiency_unit_display()}"

    def get_heating_efficiency(self, instance: Simulation) -> str:
        dominant = instance.mechanical_equipment.dominant_heating_equipment.equipment
        try:
            return f"{dominant.efficiency:.2f} {dominant.get_efficiency_unit_display()}"
        except AttributeError:
            return f"{dominant.heating_efficiency:.2f} {dominant.get_heating_efficiency_unit_display()}"

    def get_envelope_tightness(self, instance: Simulation) -> str:
        return (
            f"{instance.infiltration.infiltration_value:.2f}"
            f" {instance.infiltration.get_infiltration_unit_display()}"
        )

    def get_pv_capacity_watts(self, instance: Simulation) -> float:
        return sum(instance.photovoltaics.all().values_list("capacity", flat=True))


class EPSReport2020SimulationSerializer(EPSReportSimulationSerializer):
    """This is the Simulation Serializer for 2020"""

    base_error_message = "Unable to identify {type} analysis on simulation ({id}) for 2020 {detail}"
    analysis_type_hints = {
        "type__contains": 2020,
        "engine__in": [AnalysisEngine.REMRATE, AnalysisEngine.EKOTROPE],
    }


class EPSReport2021SimulationSerializer(EPSReportSimulationSerializer):
    """This is the Simulation Serializer for 2021"""

    base_error_message = "Unable to identify {type} analysis on simulation ({id}) for 2021 {detail}"
    analysis_type_hints = {
        "type__contains": 2021,
        "engine__in": [AnalysisEngine.REMRATE, AnalysisEngine.EKOTROPE],
    }


class EPSReport2022SimulationSerializer(EPSReportSimulationSerializer):
    """This is the Simulation Serializer for 2022"""

    base_error_message = "Unable to identify {type} analysis on simulation ({id}) for 2022 {detail}"
    analysis_type_hints = {
        "type__contains": 2022,
        "engine__in": [AnalysisEngine.REMRATE, AnalysisEngine.EKOTROPE],
    }


class EPSReport2023SimulationSerializer(EPSReportSimulationSerializer):
    """This is the Simulation Serializer for 2023"""

    base_error_message = "Unable to identify {type} analysis on simulation ({id}) for 2023 {detail}"
    analysis_type_hints = (
        Q(type__contains=2023, engine=AnalysisEngine.REMRATE)
        | Q(type__contains=2022, engine=AnalysisEngine.REMRATE)
        | Q(type__contains=2022, engine=AnalysisEngine.EKOTROPE)
    )
