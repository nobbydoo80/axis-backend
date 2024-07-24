"""simulation_data.py - Axis"""

__author__ = "Steven K"
__date__ = "10/5/21 08:56"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from django.db.models import Q
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from simulation.enumerations import (
    WaterHeaterStyle,
    FuelType,
    HotWaterEfficiencyUnit,
    HeatingEfficiencyUnit,
    CostUnit,
    SourceType,
    AnalysisEngine,
)
from simulation.models import Simulation, Analysis

from axis.customer_eto.enumerations import ClimateLocation

log = logging.getLogger(__name__)


class EPSSimulationBaseSerializer(serializers.ModelSerializer):
    climate_location = serializers.SerializerMethodField()
    conditioned_area = serializers.IntegerField()
    percent_improvement = serializers.SerializerMethodField()
    code_heating_therms = serializers.SerializerMethodField()
    code_heating_kwh = serializers.SerializerMethodField()
    code_cooling_kwh = serializers.SerializerMethodField()
    code_hot_water_therms = serializers.SerializerMethodField()
    code_hot_water_kwh = serializers.SerializerMethodField()
    code_lights_and_appliance_therms = serializers.SerializerMethodField()
    code_lights_and_appliance_kwh = serializers.SerializerMethodField()
    code_pv_kwh = serializers.SerializerMethodField()
    code_electric_cost = serializers.SerializerMethodField()
    code_gas_cost = serializers.SerializerMethodField()
    improved_heating_therms = serializers.SerializerMethodField()
    improved_heating_kwh = serializers.SerializerMethodField()
    improved_cooling_kwh = serializers.SerializerMethodField()
    improved_hot_water_therms = serializers.SerializerMethodField()
    improved_hot_water_kwh = serializers.SerializerMethodField()
    improved_lights_and_appliance_therms = serializers.SerializerMethodField()
    improved_lights_and_appliance_kwh = serializers.SerializerMethodField()
    improved_pv_kwh = serializers.SerializerMethodField()
    improved_electric_cost = serializers.SerializerMethodField()
    improved_gas_cost = serializers.SerializerMethodField()
    electric_rate = serializers.SerializerMethodField()
    gas_rate = serializers.SerializerMethodField()
    has_tankless_water_heater = serializers.SerializerMethodField()
    has_gas_hot_water = serializers.SerializerMethodField()
    has_heat_pump_water_heater = serializers.SerializerMethodField()
    hot_water_ef = serializers.SerializerMethodField()
    has_gas_heater = serializers.SerializerMethodField()
    gas_furnace_afue = serializers.SerializerMethodField()
    has_ashp = serializers.SerializerMethodField()

    base_error_message = "Unable to identify {type} analysis on simulation ({id})for {detail}"
    analysis_type_hints = {"type__contains": None}

    class Meta:
        """Meta Options"""

        model = Simulation
        fields = (
            "climate_location",
            "conditioned_area",
            "percent_improvement",
            "code_heating_therms",
            "code_heating_kwh",
            "code_cooling_kwh",
            "code_hot_water_therms",
            "code_hot_water_kwh",
            "code_lights_and_appliance_therms",
            "code_lights_and_appliance_kwh",
            "code_pv_kwh",
            "code_electric_cost",
            "code_gas_cost",
            "improved_heating_therms",
            "improved_heating_kwh",
            "improved_cooling_kwh",
            "improved_hot_water_therms",
            "improved_hot_water_kwh",
            "improved_lights_and_appliance_therms",
            "improved_lights_and_appliance_kwh",
            "improved_pv_kwh",
            "improved_electric_cost",
            "improved_gas_cost",
            "electric_rate",
            "gas_rate",
            "has_tankless_water_heater",
            "has_gas_hot_water",
            "has_heat_pump_water_heater",
            "hot_water_ef",
            "has_gas_heater",
            "gas_furnace_afue",
            "has_ashp",
        )

    def to_internal_value(self, data):
        raise NotImplementedError("Un-supported Read-Only")

    @classmethod
    def get_climate_location(cls, instance):
        data = {
            "astoria, or": ClimateLocation.ASTORIA,
            "burns, or": ClimateLocation.BURNS,
            "eugene, or": ClimateLocation.EUGENE,
            "medford, or": ClimateLocation.MEDFORD,
            "north bend, or": ClimateLocation.NORTH_BEND,
            "pendleton, or": ClimateLocation.PENDLETON,
            "portland, or": ClimateLocation.PORTLAND,
            "redmond, or": ClimateLocation.REDMOND,
            "salem, or": ClimateLocation.SALEM,
            "astoria regional airport, or": ClimateLocation.ASTORIA,
            "aurora state, or": ClimateLocation.PORTLAND,
            "baker municipal ap, or": ClimateLocation.PENDLETON,
            "burns municipal arpt [uo], or": ClimateLocation.BURNS,
            "corvallis muni, or": ClimateLocation.EUGENE,
            "eugene mahlon sweet arpt [uo], or": ClimateLocation.EUGENE,
            "klamath falls intl ap [uo], or": ClimateLocation.MEDFORD,
            "la grande muni ap, or": ClimateLocation.PENDLETON,
            "lakeview (awos), or": ClimateLocation.BURNS,
            "medford rogue valley intl ap [ashland - uo], or": ClimateLocation.MEDFORD,
            "north bend muni airport, or": ClimateLocation.NORTH_BEND,
            "pendleton e or regional ap, or": ClimateLocation.PENDLETON,
            "portland international ap, or": ClimateLocation.PORTLAND,
            "portland/hillsboro, or": ClimateLocation.PORTLAND,
            "portland/troutdale, or": ClimateLocation.PORTLAND,
            "redmond roberts field, or": ClimateLocation.REDMOND,
            "roseburg regional ap, or": ClimateLocation.NORTH_BEND,
            "salem mcnary field, or": ClimateLocation.SALEM,
            "sexton summit, or": ClimateLocation.MEDFORD,
        }
        return data.get(instance.location.weather_station.lower())

    def reference_analysis(self, instance) -> Analysis:
        if hasattr(self, "_reference_analysis"):
            return self._reference_analysis

        try:
            analysis = instance.logical_reference_analyses(
                type_hints=self.analysis_type_hints
            ).get()
            self._reference_analysis = analysis
            return self._reference_analysis
        except Analysis.MultipleObjectsReturned:
            detail = "multiple analyses exist."
            raise ValidationError(
                {
                    "simulation": [
                        self.base_error_message.format(
                            type="reference", id=self.instance.id, detail=detail
                        )
                    ]
                }
            )
        except Analysis.DoesNotExist:
            detail = "no analysis exist."
            raise ValidationError(
                {
                    "simulation": self.base_error_message.format(
                        type="reference", id=self.instance.id, detail=detail
                    )
                }
            )

    def as_designed_analysis(self, instance) -> Analysis:
        if hasattr(self, "_as_designed_analysis"):
            return self._as_designed_analysis

        try:
            analysis = instance.logical_as_designed_analyses(
                type_hints=self.analysis_type_hints
            ).get()
            self._as_designed_analysis = analysis
            return self._as_designed_analysis
        except Analysis.MultipleObjectsReturned:
            detail = "multiple analyses exist."
            raise ValidationError(
                {
                    "simulation": self.base_error_message.format(
                        type="design", id=self.instance.id, detail=detail
                    )
                }
            )
        except Analysis.DoesNotExist:
            detail = "no analysis exist."
            raise ValidationError(
                {
                    "simulation": self.base_error_message.format(
                        type="design", id=self.instance.id, detail=detail
                    )
                }
            )

    def get_percent_improvement(self, instance) -> float:
        analysis = self.as_designed_analysis(instance)
        reference = self.reference_analysis(instance)
        return analysis.get_percent_improvement_over(reference)

    def get_code_heating_therms(self, instance) -> float:
        analysis = self.reference_analysis(instance)
        return analysis.fuel_usages.all().gas_heating_consumption_therms

    def get_code_heating_kwh(self, instance) -> float:
        analysis = self.reference_analysis(instance)
        return analysis.fuel_usages.all().electric_heating_consumption_kwh

    def get_code_cooling_kwh(self, instance) -> float:
        analysis = self.reference_analysis(instance)
        return analysis.fuel_usages.all().electric_cooling_consumption_kwh

    def get_code_hot_water_therms(self, instance) -> float:
        analysis = self.reference_analysis(instance)
        return analysis.fuel_usages.all().gas_water_heating_consumption_therms

    def get_code_hot_water_kwh(self, instance) -> float:
        analysis = self.reference_analysis(instance)
        return analysis.fuel_usages.all().electric_water_heating_consumption_kwh

    def get_code_lights_and_appliance_therms(self, instance) -> float:
        analysis = self.reference_analysis(instance)
        return analysis.fuel_usages.all().gas_lighting_and_appliances_consumption_therms

    def get_code_lights_and_appliance_kwh(self, instance) -> float:
        analysis = self.reference_analysis(instance)
        return analysis.fuel_usages.all().electric_lighting_and_appliances_consumption_kwh

    def get_code_pv_kwh(self, instance) -> float:
        analysis = self.reference_analysis(instance)
        return analysis.summary.solar_generation_kwh

    def get_code_electric_cost(self, instance) -> float:
        analysis = self.reference_analysis(instance)
        return analysis.fuel_usages.all().electric_cost

    def get_code_gas_cost(self, instance) -> float:
        analysis = self.reference_analysis(instance)
        return analysis.fuel_usages.all().gas_cost

    def get_improved_heating_therms(self, instance) -> float:
        analysis = self.as_designed_analysis(instance)
        return analysis.fuel_usages.all().gas_heating_consumption_therms

    def get_improved_heating_kwh(self, instance) -> float:
        analysis = self.as_designed_analysis(instance)
        return analysis.fuel_usages.all().electric_heating_consumption_kwh

    def get_improved_cooling_kwh(self, instance) -> float:
        analysis = self.as_designed_analysis(instance)
        return analysis.fuel_usages.all().electric_cooling_consumption_kwh

    def get_improved_hot_water_therms(self, instance) -> float:
        analysis = self.as_designed_analysis(instance)
        return analysis.fuel_usages.all().gas_water_heating_consumption_therms

    def get_improved_hot_water_kwh(self, instance) -> float:
        analysis = self.as_designed_analysis(instance)
        return analysis.fuel_usages.all().electric_water_heating_consumption_kwh

    def get_improved_lights_and_appliance_therms(self, instance) -> float:
        analysis = self.as_designed_analysis(instance)
        return analysis.fuel_usages.all().gas_lighting_and_appliances_consumption_therms

    def get_improved_lights_and_appliance_kwh(self, instance) -> float:
        analysis = self.as_designed_analysis(instance)
        return analysis.fuel_usages.all().electric_lighting_and_appliances_consumption_kwh

    def get_improved_pv_kwh(self, instance) -> float:
        analysis = self.as_designed_analysis(instance)
        return analysis.summary.solar_generation_kwh

    def get_improved_electric_cost(self, instance) -> float:
        analysis = self.as_designed_analysis(instance)
        return analysis.fuel_usages.all().electric_cost

    def get_improved_gas_cost(self, instance) -> float:
        analysis = self.as_designed_analysis(instance)
        return analysis.fuel_usages.all().gas_cost

    def get_electric_rate(self, instance) -> float:
        _values = instance.utility_rates.filter(fuel=FuelType.ELECTRIC).values_list(
            "seasonal_rates__block_rates__cost", "cost_units"
        ) or [(0.0, CostUnit.USD.value)]
        values = [0.0]
        for cost, rate in _values:
            if rate == CostUnit.USD.value:
                values.append(cost)
            elif rate == CostUnit.USC.value:
                values.append(cost / 100.0)
        return max(values)

    def get_gas_rate(self, instance) -> float:
        _values = instance.utility_rates.filter(fuel=FuelType.NATURAL_GAS).values_list(
            "seasonal_rates__block_rates__cost", "cost_units"
        ) or [(0.0, CostUnit.USD.value)]
        values = [0.0]
        for cost, rate in _values:
            if rate == CostUnit.USD.value:
                values.append(cost)
            elif rate == CostUnit.USC.value:
                values.append(cost / 100.0)
        return max(values)

    def get_has_tankless_water_heater(self, instance) -> bool:
        return instance.water_heaters.filter(style=WaterHeaterStyle.TANKLESS).exists()

    def get_has_gas_hot_water(self, instance) -> bool:
        return instance.water_heaters.filter(fuel=FuelType.NATURAL_GAS).exists()

    def get_has_heat_pump_water_heater(self, instance) -> bool:
        return instance.water_heaters.heat_pumps().exists()

    def get_hot_water_ef(self, instance) -> float:
        vals = list(
            set(
                instance.water_heaters.filter(
                    efficiency_unit=HotWaterEfficiencyUnit.ENERGY_FACTOR
                ).values_list("efficiency", flat=True)
            )
        )
        if len(vals) == 1:
            return vals[0]
        if not vals:
            return 0.0

    def get_has_gas_heater(self, instance) -> bool:
        return instance.heaters.filter(fuel=FuelType.NATURAL_GAS).exists()

    def get_gas_furnace_afue(self, instance) -> float:
        value = instance.heaters.filter(
            fuel=FuelType.NATURAL_GAS, efficiency_unit=HeatingEfficiencyUnit.AFUE, efficiency__lt=94
        ).first()
        return value.efficiency if value else None

    def get_has_ashp(self, instance) -> bool:
        return instance.air_source_heat_pumps.exists()


class EPSSimulation2020Serializer(EPSSimulationBaseSerializer):
    """This is the Simulation Serializer for 2020"""

    base_error_message = "Unable to identify {type} analysis on simulation ({id}) for 2020 {detail}"
    analysis_type_hints = {
        "type__contains": 2020,
        "engine__in": [AnalysisEngine.REMRATE, AnalysisEngine.EKOTROPE],
    }


class EPSSimulation2021Serializer(EPSSimulationBaseSerializer):
    """This is the Simulation Serializer for 2021"""

    base_error_message = "Unable to identify {type} analysis on simulation ({id}) for 2021 {detail}"
    analysis_type_hints = {
        "type__contains": 2021,
        "engine__in": [AnalysisEngine.REMRATE, AnalysisEngine.EKOTROPE],
    }


class EPSSimulation2022Serializer(EPSSimulationBaseSerializer):
    """This is the Simulation Serializer for 2022"""

    base_error_message = "Unable to identify {type} analysis on simulation ({id}) for 2022 {detail}"
    analysis_type_hints = {
        "type__contains": 2023,
        "engine__in": [AnalysisEngine.REMRATE, AnalysisEngine.EKOTROPE],
    }


class EPSSimulation2023Serializer(EPSSimulationBaseSerializer):
    """This is the Simulation Serializer for 2023"""

    base_error_message = "Unable to identify {type} analysis on simulation ({id}) for 2023 {detail}"
    analysis_type_hints = Q(
        type__contains=2022, engine__in=[AnalysisEngine.REMRATE, AnalysisEngine.EKOTROPE]
    ) | Q(type__contains=2023, engine=AnalysisEngine.REMRATE)
