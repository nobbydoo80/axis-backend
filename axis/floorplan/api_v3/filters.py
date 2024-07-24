"""filters.py: """

__author__ = "Artem Hruzd"
__date__ = "08/27/2020 22:34"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django_filters import rest_framework as filters
from django.db.models import QuerySet

from axis.company.models import Company
from simulation.models import Seed, Simulation

from axis.floorplan.api_v3 import (
    FLOORPLAN_FILTER_FIELDS,
    SEED_FILTER_FIELDS,
    SIMULATION_FILTER_FIELDS,
)
from axis.floorplan.models import Floorplan
from simulation.enumerations import FuelType, WaterHeaterStyle, SourceType, CrawlspaceType


class FloorplanFilter(filters.FilterSet):
    heater_fuel_type = filters.ChoiceFilter(
        field_name="simulation__mechanical_equipment__heater__fuel", choices=FuelType.choices
    )

    water_heater_fuel_type = filters.ChoiceFilter(
        field_name="simulation__mechanical_equipment__water_heater__fuel", choices=FuelType.choices
    )

    water_heater_style = filters.ChoiceFilter(
        field_name="simulation__mechanical_equipment__water_heater__style",
        choices=WaterHeaterStyle.choices,
    )

    air_conditioner = filters.BooleanFilter(
        field_name="simulation__mechanical_equipment__air_conditioner",
        lookup_expr="isnull",
    )
    ashp = filters.BooleanFilter(
        field_name="simulation__mechanical_equipment__air_source_heat_pump",
        lookup_expr="isnull",
    )
    gshp = filters.BooleanFilter(
        field_name="simulation__mechanical_equipment__ground_source_heat_pump",
        lookup_expr="isnull",
    )
    dehumidifier = filters.BooleanFilter(
        field_name="simulation__mechanical_equipment__dehumidifier",
        lookup_expr="isnull",
    )
    simulation_source = filters.ChoiceFilter(
        field_name="simulation__source_type", choices=SourceType.choices
    )
    simulation_version = filters.CharFilter(field_name="simulation__version")
    attached_to_home = filters.BooleanFilter(
        field_name="homes_count", method="filter_attached_to_home"
    )
    crawl_space = filters.CharFilter(method="filter_by_crawl_space")
    has_slabs = filters.BooleanFilter(field_name="simulation__slabs", lookup_expr="isnull")
    num_stories = filters.NumberFilter(method="filter_by_num_stories")
    has_basement = filters.BooleanFilter(method="filter_basement")
    attic_type = filters.CharFilter(method="filter_attic_type")
    vaulted_ceilings = filters.BooleanFilter(method="filter_vaulted_ceilings")
    has_photovoltaics = filters.BooleanFilter(
        field_name="simulation__photovoltaics", lookup_expr="isnull"
    )
    water_heater_type = filters.CharFilter(method="filter_by_water_heater_type")

    def filter_by_water_heater_type(self, qs: QuerySet, field: str, value: str):
        return qs.filter_by_water_heater_fuel_and_style(value)

    def filter_by_crawl_space(self, qs: QuerySet, field: str, value: str):
        return qs.filter_by_crawl_space(value)

    def filter_basement(self, qs: QuerySet, field: str, value: bool):
        return qs.filter_by_basement(value)

    def filter_attic_type(self, qs: QuerySet, field: str, value: str):
        return qs.filter_by_attic_type(value)

    def filter_vaulted_ceilings(self, qs: QuerySet, field: str, value: bool):
        return qs.filter_vaulted_ceilings(value)

    def filter_by_num_stories(self, qs: QuerySet, field: str, value: int):
        return qs.filter_by_num_stories(value)

    def filter_attached_to_home(self, qs: QuerySet, field: str, value: bool):
        if value:
            return qs.filter(**{f"{field}__gt": 0})
        return qs.filter(**{field: 0})

    class Meta:
        model = Floorplan
        fields = FLOORPLAN_FILTER_FIELDS


class SeedFilter(filters.FilterSet):
    class Meta:
        model = Seed
        fields = SEED_FILTER_FIELDS


class SimulationFilter(filters.FilterSet):
    company = filters.ModelMultipleChoiceFilter(queryset=Company.objects.all())

    class Meta:
        model = Simulation
        fields = SIMULATION_FILTER_FIELDS
