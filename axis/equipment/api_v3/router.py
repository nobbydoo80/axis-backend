__author__ = "Artem Hruzd"
__date__ = "04/11/2023 18:09"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from axis.equipment.api_v3.viewsets import EquipmentViewSet


class EquipmentRouter:
    @staticmethod
    def register(router):
        equipment_router = router.register(r"equipment", EquipmentViewSet, "equipment")
