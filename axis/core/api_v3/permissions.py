"""Api V3 base permission classes."""


from django.contrib.auth import get_user_model
from rest_framework.permissions import BasePermission, DjangoModelPermissions

__author__ = "Artem Hruzd"
__date__ = "01/06/2020 12:22"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

User = get_user_model()


class AxisDjangoModelPermissions(DjangoModelPermissions):
    """Assign GET access to our 'view' perm."""

    def __init__(self):
        self.perms_map["GET"] = ["%(app_label)s.view_%(model_name)s"]


class IsCurrentUserPermission(BasePermission):
    """Object is the request user."""

    def has_object_permission(self, request, view, obj):
        return bool(
            request.user
            and (request.user.is_staff or request.user.is_superuser)
            or obj == request.user
        )


class NestedIsCurrentUserPermission(BasePermission):
    """Allow access for nested resource only for current user or superuser"""

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        parents_query_dict = view.get_parents_query_dict()
        try:
            user_id = int(parents_query_dict["user_id"])
        except (KeyError, ValueError):
            return True
        return user_id == request.user.id


class IsUserIsCompanyAdminPermission(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and request.user.is_company_admin
        )


class IsAdminUserOrSuperUserPermission(BasePermission):
    """
    Check if user.is_staff or user.is_superuser
    """

    def has_permission(self, request, view):
        return bool(request.user and (request.user.is_staff or request.user.is_superuser))


class IsUserImpersonatedPermission(BasePermission):
    def has_permission(self, request, view):
        impersonator_pk = None
        if hasattr(request, "jwt") and request.jwt.get("impersonator"):
            impersonator_pk = request.jwt.get("impersonator")
        else:
            if hasattr(request, "impersonator") and request.impersonator:
                impersonator_pk = request.impersonator.pk
        impersonator_exists = User.objects.filter(pk=impersonator_pk).exists()
        return impersonator_exists


class UserUpdatePermission(BasePermission):
    def has_permission(self, request, view):
        if not bool(request.user and request.user.is_authenticated and request.user.company):
            return False
        return True

    def has_object_permission(self, request, view, user):
        return user.can_be_edited(user=request.user)
