"""permissions.py: """


from rest_framework.permissions import BasePermission

__author__ = "Artem Hruzd"
__date__ = "01/06/2020 22:24"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class IsMessageOwnerPermission(BasePermission):
    """Allows access only to message owner or sender"""

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user or obj.sender == request.user or request.user.is_superuser
