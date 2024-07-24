__author__ = "Artem Hruzd"
__date__ = "04/03/2020 18:41"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from rest_framework.permissions import BasePermission
from django.apps import apps

from axis.equipment.models import Equipment

equipment_app = apps.get_app_config("equipment")


class CopyEquipmentPermissionPermission(BasePermission):
    def has_permission(self, request, view) -> bool:
        return bool(request.user and request.user.is_authenticated and request.user.company)

    def has_object_permission(self, request, view, equipment: Equipment) -> bool:
        if request.user.is_superuser:
            return True
        if request.user.company.slug in equipment_app.EQUIPMENT_APPLICABLE_COMPANIES_SLUGS:
            return True
        if equipment.owner_company == request.user.company:
            return True
        return False
