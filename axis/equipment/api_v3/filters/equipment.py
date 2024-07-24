"""equipment.py: """


from django_filters import rest_framework as filters

from axis.equipment.api_v3 import EQUIPMENT_FILTER_FIELDS
from axis.equipment.models import Equipment

__author__ = "Artem Hruzd"
__date__ = "04/03/2020 19:43"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class EquipmentFilter(filters.FilterSet):
    class Meta:
        model = Equipment
        fields = EQUIPMENT_FILTER_FIELDS
