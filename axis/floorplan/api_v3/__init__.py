"""__init__.py: """

__author__ = "Artem Hruzd"
__date__ = "08/27/2020 22:34"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


FLOORPLAN_SEARCH_FIELDS = [
    "name",
    "remrate_target__id",
    "comment",
]
FLOORPLAN_ORDERING_FIELDS = [
    "name",
    "remrate_target",
    "owner",
    "comment",
    "homes_count",
    "created_date",
]
FLOORPLAN_FILTER_FIELDS = []


SIMULATION_SEARCH_FIELDS = [
    "id",
    "name",
    "company__name",
    "location__street_line1",
    "location__street_line2",
    "location__city__name",
    "location__county__name",
    "location__zipcode",
]
SIMULATION_ORDERING_FIELDS = ["id", "name", "modified_date", "bedroom_count"]
SIMULATION_FILTER_FIELDS = ["company", "source_type", "status"]

SEED_SEARCH_FIELDS = [
    "id",
    "label",
    "company__name",
    "source_remrate_sql_data__model_name",
    "source_remrate_sql_data__property_address",
    "source_remrate_sql_data__subdivision_name",
    "source_remrate_sql_data__builder_name",
    "source_ekotrope_data__model_name",
    "source_ekotrope_data__property_address",
    "source_ekotrope_data__subdivision_name",
    "source_ekotrope_data__builder_name",
    "simulation__model_name",
    "simulation__property_address",
    "simulation__subdivision_name",
    "simulation__builder_name",
]
SEED_ORDERING_FIELDS = ["id", "label", "source_date"]
SEED_FILTER_FIELDS = ["label", "company", "company__name"]
