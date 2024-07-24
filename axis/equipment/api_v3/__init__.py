"""__init__.py: """


__author__ = "Artem Hruzd"
__date__ = "04/03/2020 18:40"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

# common set of search_fields for Equipment Viewsets
EQUIPMENT_SEARCH_FIELDS = [
    "brand",
    "equipment_model",
    "serial",
    "calibration_company",
    "description",
    "owner_company__name",
]

# common set of ordering_fields for Equipment Viewsets
EQUIPMENT_ORDERING_FIELDS = [
    "id",
    "equipment_type",
    "brand",
    "equipment_model",
    "serial",
    "description",
    "calibration_date",
    "calibration_cycle",
]

# common set of FilterSet fields for Equipment Viewsets
EQUIPMENT_FILTER_FIELDS = [
    "owner_company",
]
