"""permissions.py: """


from rest_framework.permissions import BasePermission

__author__ = "Artem Hruzd"
__date__ = "06/23/2020 14:46"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class CommunityDeletePermission(BasePermission):
    """
    Allow delete Community:
    1. For superusers
    2. If community have no subdivisions
    3. If user have owned relationship with this community
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.company)

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        if obj.subdivision_set.count() == 0:
            return True

        relationships = obj.relationships.filter(is_owned=True)
        relationships = relationships.exclude(company__auto_add_direct_relationships=True)
        relationship = relationships.first()

        if request.user.company.id == relationship.company_id:
            return True
        return False
