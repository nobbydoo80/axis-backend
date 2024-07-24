"""test.py: """


__author__ = "Rajesh Pethe"
__date__ = "02/03/2023 18:07:38"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Rajesh Pethe",
    "Steven Klass",
]


from rest_framework import serializers

from simulation.enumerations import EnergyUnit
from simulation.models import Analysis, Summary
from simulation.utils import convert_energy_value_to


class SummaryResultCostSerializer(serializers.ModelSerializer):
    annual_heating_cost = serializers.FloatField(source="heating_cost")
    annual_cooling_cost = serializers.FloatField(source="cooling_cost")
    annual_hot_water_cost = serializers.FloatField(source="water_heating_cost")
    annual_light_and_appliances_cost = serializers.FloatField(source="lighting_and_appliances_cost")
    annual_generation = serializers.FloatField(source="solar_generation_savings")
    total_annual_costs = serializers.FloatField(source="total_cost")
    total_annual_costs_with_generation = serializers.FloatField(source="total_cost_no_pv")

    class Meta:
        model = Summary
        fields = (
            "id",
            "annual_heating_cost",
            "annual_cooling_cost",
            "annual_hot_water_cost",
            "annual_light_and_appliances_cost",
            "annual_generation",
            "total_annual_costs",
            "total_annual_costs_with_generation",
        )


class SummaryResultConsumptionSerializer(serializers.ModelSerializer):
    total_heating_consumption = serializers.SerializerMethodField()
    total_cooling_consumption = serializers.SerializerMethodField()
    total_hot_water_consumption = serializers.SerializerMethodField()
    total_light_and_appliances_consumption = serializers.SerializerMethodField()
    total_onsite_generation = serializers.SerializerMethodField()
    total_energy_consumption = serializers.SerializerMethodField()

    class Meta:
        model = Summary
        fields = (
            "total_heating_consumption",
            "total_cooling_consumption",
            "total_hot_water_consumption",
            "total_light_and_appliances_consumption",
            "total_onsite_generation",
            "total_energy_consumption",
        )

    def get_mbtu_value(self, field: str, instance: Summary) -> float | None:
        value = getattr(instance, field)
        if value is None:
            return value

        return convert_energy_value_to(value, instance.consumption_units, EnergyUnit.MBTU)

    def get_total_heating_consumption(self, instance: Summary) -> float | None:
        return self.get_mbtu_value("heating_consumption", instance)

    def get_total_cooling_consumption(self, instance: Summary) -> float | None:
        return self.get_mbtu_value("cooling_consumption", instance)

    def get_total_hot_water_consumption(self, instance: Summary) -> float | None:
        return self.get_mbtu_value("water_heating_consumption", instance)

    def get_total_light_and_appliances_consumption(self, instance: Summary) -> float | None:
        return self.get_mbtu_value("lighting_and_appliances_consumption", instance)

    def get_total_onsite_generation(self, instance: Summary) -> float | None:
        return self.get_mbtu_value("solar_generation", instance)

    def get_total_energy_consumption(self, instance: Summary) -> float | None:
        return self.get_mbtu_value("total_consumption", instance)


class AnalysisUrlSerializer(serializers.ModelSerializer):
    rated_html_document = serializers.SerializerMethodField()

    class Meta:
        model = Analysis
        fields = ("rated_html_document",)

    def get_rated_html_document(self, instance: Analysis) -> str:
        docs = instance.customer_documents.filter(
            document__icontains="open_studio_html_results", document__endswith=".html"
        )
        if docs.exists():
            return docs.first().get_preview_link()
        return ""


class AnalysisSummaryDataSerializer(serializers.ModelSerializer):
    engine = serializers.ReadOnlyField(source="get_engine_display")
    type = serializers.ReadOnlyField(source="get_type_display")
    simulation_date = serializers.ReadOnlyField(source="simulation_datetime")
    valid = serializers.BooleanField(source="pk")

    energy_rating_index = serializers.ReadOnlyField(source="eri_score")
    costs = SummaryResultCostSerializer(source="summary")
    consumption = SummaryResultConsumptionSerializer(source="summary")
    urls = AnalysisUrlSerializer(source="*")

    class Meta:
        model = Analysis
        fields = (
            "id",
            "engine",
            "type",
            "valid",
            "version",
            "simulation_date",
            "energy_rating_index",
            "costs",
            "consumption",
            "urls",
        )
