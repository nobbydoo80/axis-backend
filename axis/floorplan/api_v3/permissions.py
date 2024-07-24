"""permissions.py: """

__author__ = "Artem Hruzd"
__date__ = "08/27/2020 22:35"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.core.exceptions import ObjectDoesNotExist
from rest_framework.permissions import BasePermission


class SimBaseMixin:
    def has_permission(self, request, view):
        if any(
            [
                request.user is None,
                request.user.is_anonymous,
                not request.user.is_authenticated,
                not request.user.is_active,
            ]
        ):
            return False

        if request.user.company is None:
            return False

        return True

    def usage_check(self, obj):
        """Are there any certified homestatuses that exist?"""
        try:
            floorplan = obj.floorplan
        except ObjectDoesNotExist:
            return True
        return not floorplan.homestatuses.filter(
            certification_date__isnull=False, state="complete"
        ).exists()

    def update_delete_has_object_permission(self, request, view, obj):
        """Generic reusable method"""
        if request.user.is_staff or request.user.is_superuser:
            return self.usage_check(obj)
        if request.user.company and obj.company.id == request.user.company.id:
            return self.usage_check(obj)
        return False


class SimulationCreatePermission(SimBaseMixin, BasePermission):
    """
    1. Raters / Providers can create
    2. Supers can create
    """

    def has_permission(self, request, view):
        if not super(SimulationCreatePermission, self).has_permission(request, view):
            return False

        if request.user.company.company_type in ["rater", "provider"] or request.user.is_superuser:
            return True
        return False


class SimulationUpdatePermission(SimBaseMixin, BasePermission):
    """
    1. Owners can update
    2. Supers can update
    """

    def has_object_permission(self, request, view, obj):
        return self.update_delete_has_object_permission(request, view, obj)


class SimulationDeletePermission(SimBaseMixin, BasePermission):
    """
    1. Owners can delete
    2. Supers can delete
    """

    def has_object_permission(self, request, view, obj):
        return self.update_delete_has_object_permission(request, view, obj)
